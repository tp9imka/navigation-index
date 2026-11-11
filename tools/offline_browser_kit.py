#!/usr/bin/env python3
"""Offline browser kit for the browser tools (playground and Solver) when cdn.jsdelivr.net is blocked.

Stdlib only. Run from anywhere; paths are resolved from this file.

  python3 tools/offline_browser_kit.py prepare   # download Pyodide core + numpy + scipy (+ deps) into
                                       # site/playground/pyodide-local/, check sha256 vs pyodide-lock.json
  python3 tools/offline_browser_kit.py verify    # local server + headless Chrome with cdn.jsdelivr.net mapped to
                                       # 127.0.0.1: one playground run, one Solver Quick sweep
  python3 tools/offline_browser_kit.py bundle    # dist/offline-browser-kit.zip: site/ + manifest files + vendored folder + serve.py
  python3 tools/offline_browser_kit.py verify --kit /path/to/unzipped   # same checks, served by the kit's serve.py

verify uses a Chrome already on the machine (CHROME=..., the macOS default path, or a Playwright
cache); it never installs one. Reports go to site/playground/pyodide-local/venue-kit-*.json (gitignored).
"""
import argparse
import base64
import functools
import glob
import hashlib
import http.server
import json
import os
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PG_DIR = ROOT / "site" / "playground"
MANIFEST = PG_DIR / "manifest.json"
# Files pyodide.mjs needs next to it (Pyodide 314: pyodide.asm.mjs, not pyodide.asm.js)
CORE_FILES = ["pyodide-lock.json", "pyodide.mjs", "pyodide.asm.mjs", "pyodide.asm.wasm", "python_stdlib.zip"]
SUMS = "SHA256SUMS"
REPORT_PREFIX = "venue-kit-"
SKIP_NAMES = {"__pycache__", ".DS_Store", ".git", "node_modules", ".venv"}
SKIP_SUFFIXES = (".pyc", ".part")
CDN_HOST = "cdn.jsdelivr.net"
MB = 1024 * 1024


# ------------------------------------------------------------------ lock and manifest (pure, unit tested)

def load_manifest(path=MANIFEST):
    return json.loads(Path(path).read_text())


def local_dir(manifest, manifest_dir=PG_DIR):
    return (Path(manifest_dir) / manifest.get("pyodide_local", "pyodide-local/")).resolve()


def parse_lock(text):
    """pyodide-lock.json text => {normalized name: {file_name, sha256, depends, version}}."""
    data = json.loads(text)
    pk = data.get("packages")
    if not isinstance(pk, dict) or not pk:
        raise ValueError("pyodide-lock.json has no 'packages' table")
    out = {}
    for key, p in pk.items():
        for field in ("file_name", "sha256"):
            if not p.get(field):
                raise ValueError(f"lock entry {key!r} has no {field}")
        out[norm(key)] = {"name": p.get("name", key), "file_name": p["file_name"], "sha256": p["sha256"].lower(),
                          "depends": [norm(d) for d in p.get("depends", [])], "version": p.get("version")}
    return out


def norm(name):
    return name.lower().replace("_", "-")


def resolve(lock, names):
    """Package names plus their transitive depends, dependencies first, each once."""
    order, seen = [], set()

    def visit(n, path):
        n = norm(n)
        if n in seen:
            return
        if n in path:
            return  # cycle: already being visited
        if n not in lock:
            raise KeyError(f"package {n!r} is not in pyodide-lock.json" + (f" (needed by {path[-1]})" if path else ""))
        for d in lock[n]["depends"]:
            visit(d, path + [n])
        seen.add(n)
        order.append(n)

    for n in names:
        visit(n, [])
    return order


def wheel_entries(lock, names):
    """[(file name, sha256)] for the packages and their deps. A URL file_name keeps only its basename."""
    return [(lock[n]["file_name"].rsplit("/", 1)[-1], lock[n]["sha256"]) for n in resolve(lock, names)]


def manifest_files(manifest, manifest_dir=PG_DIR, root=ROOT):
    """Repo-relative POSIX paths of every manifest 'files' src (src is relative to manifest.json)."""
    root = Path(root).resolve()
    out = []
    for f in manifest.get("files", []):
        p = (Path(manifest_dir) / f["src"]).resolve()
        try:
            rel = p.relative_to(root)
        except ValueError:
            raise ValueError(f"manifest src {f['src']!r} points outside the repo") from None
        if rel.as_posix() not in out:
            out.append(rel.as_posix())
    return out


def skip(rel_parts, name):
    return bool(SKIP_NAMES.intersection(rel_parts)) or name in SKIP_NAMES or name.endswith(SKIP_SUFFIXES) or name.startswith(REPORT_PREFIX)


def bundle_entries(root=ROOT, manifest=None, manifest_dir=None):
    """Sorted unique repo-relative paths for the zip: site/** (minus caches and reports) + manifest files.
    Raises FileNotFoundError when a manifest file is missing."""
    root = Path(root).resolve()
    manifest_dir = Path(manifest_dir) if manifest_dir else root / "site" / "playground"
    manifest = manifest if manifest is not None else load_manifest(manifest_dir / "manifest.json")
    rels = set()
    for dirpath, dirnames, filenames in os.walk(root / "site"):
        dirnames[:] = [d for d in dirnames if d not in SKIP_NAMES]
        rel_dir = Path(dirpath).relative_to(root)
        for fn in filenames:
            if not skip(rel_dir.parts, fn):
                rels.add((rel_dir / fn).as_posix())
    for rel in manifest_files(manifest, manifest_dir, root):
        if not (root / rel).is_file():
            raise FileNotFoundError(f"manifest file missing: {rel}")
        rels.add(rel)
    return sorted(rels)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_wheels(folder, entries):
    """[(file, status)] with status ok / missing / mismatch."""
    res = []
    for fn, sha in entries:
        p = Path(folder) / fn
        res.append((fn, "missing" if not p.is_file() else ("ok" if sha256_file(p) == sha else "mismatch")))
    return res


# ------------------------------------------------------------------ prepare

def download(url, dst, attempts=3, timeout=60):
    part = Path(str(dst) + ".part")
    last = None
    for i in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as r, open(part, "wb") as fh:
                shutil.copyfileobj(r, fh, 1 << 20)
            os.replace(part, dst)
            return Path(dst).stat().st_size
        except Exception as err:  # network errors of every kind: retry, then raise
            last = err
            part.unlink(missing_ok=True)
            if i < attempts:
                time.sleep(2 * i)
    raise RuntimeError(f"download failed after {attempts} attempts: {url}: {last}")


def cmd_prepare(args):
    m = load_manifest()
    base, folder = m["pyodide_base"], local_dir(m)
    if args.version and args.version != m["pyodide"]:
        sys.exit(f"manifest pins Pyodide {m['pyodide']}, not {args.version}")
    folder.mkdir(parents=True, exist_ok=True)
    print(f"Pyodide {m['pyodide']} from {base}\n=> {folder.relative_to(ROOT)}/")
    t0 = time.monotonic()
    got, rows = 0, []

    def fetch(fn, why):
        nonlocal got
        t = time.monotonic()
        n = download(base + fn, folder / fn)
        got += n
        rows.append({"file": fn, "bytes": n, "s": round(time.monotonic() - t, 2), "how": why})

    for fn in CORE_FILES:
        if args.force or not (folder / fn).is_file():
            fetch(fn, "downloaded")
        else:
            rows.append({"file": fn, "bytes": (folder / fn).stat().st_size, "s": 0, "how": "cached"})
    lock = parse_lock((folder / "pyodide-lock.json").read_text())
    entries = wheel_entries(lock, m["packages"])
    for fn, sha in entries:
        p = folder / fn
        if not args.force and p.is_file() and sha256_file(p) == sha:
            rows.append({"file": fn, "bytes": p.stat().st_size, "s": 0, "how": "cached"})
            continue
        fetch(fn, "downloaded")
    checks = check_wheels(folder, entries)
    bad = [c for c in checks if c[1] != "ok"]
    for r in rows:
        r["sha256"] = sha256_file(folder / r["file"])
        r["sha256_vs_lock"] = dict(checks).get(r["file"], "not in lock (core file)")
    (folder / SUMS).write_text("".join(f"{r['sha256']}  {r['file']}\n" for r in rows))
    elapsed = time.monotonic() - t0
    total = sum(r["bytes"] for r in rows)
    for r in rows:
        print(f"  {r['file']:<58} {r['bytes'] / MB:7.2f} MB  {r['how']:<10} {r['s']:6.2f} s  sha256 {r['sha256_vs_lock']}")
    print(f"packages: {', '.join(resolve(lock, m['packages']))} (from {', '.join(m['packages'])} + depends)")
    print(f"total {total / MB:.1f} MB in {len(rows)} files; downloaded {got / MB:.1f} MB in {elapsed:.1f} s; "
          f"wheels sha256 vs pyodide-lock.json: {len(checks) - len(bad)}/{len(checks)} ok")
    report = {"date": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "input": "real downloads from " + base,
              "pyodide": m["pyodide"], "folder": str(folder.relative_to(ROOT)), "files": rows,
              "total_mb": round(total / MB, 2), "downloaded_mb": round(got / MB, 2), "elapsed_s": round(elapsed, 2),
              "wheels_ok": len(checks) - len(bad), "wheels": len(checks)}
    (folder / (REPORT_PREFIX + "prepare.json")).write_text(json.dumps(report, indent=1) + "\n")
    if bad:
        sys.exit(f"FAIL: {bad}")
    print("PASS")


# ------------------------------------------------------------------ minimal WebSocket + CDP client

class WebSocket:
    """Text-frame WebSocket client, enough for the Chrome DevTools protocol on localhost."""

    def __init__(self, url, timeout=10):
        u = urllib.parse.urlparse(url)
        self.sock = socket.create_connection((u.hostname, u.port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        self.sock.sendall((f"GET {u.path} HTTP/1.1\r\nHost: {u.hostname}:{u.port}\r\nUpgrade: websocket\r\n"
                           f"Connection: Upgrade\r\nSec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n").encode())
        self.rf = self.sock.makefile("rb")
        status = self.rf.readline()
        if b" 101 " not in status:
            raise ConnectionError(f"websocket upgrade refused: {status!r}")
        while self.rf.readline() not in (b"\r\n", b""):
            pass
        self.sock.settimeout(None)
        self.lock = threading.Lock()

    def _frame(self, opcode, payload):
        n = len(payload)
        head = bytes([0x80 | opcode])
        if n < 126:
            head += bytes([0x80 | n])
        elif n < 65536:
            head += bytes([0x80 | 126]) + struct.pack(">H", n)
        else:
            head += bytes([0x80 | 127]) + struct.pack(">Q", n)
        mask = os.urandom(4)
        body = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        with self.lock:
            self.sock.sendall(head + mask + body)

    def send(self, text):
        self._frame(0x1, text.encode())

    def _read(self, n):
        b = self.rf.read(n)
        if b is None or len(b) < n:
            raise ConnectionError("websocket closed")
        return b

    def recv(self):
        parts = []
        while True:
            b0, b1 = self._read(2)
            op, n = b0 & 0x0F, b1 & 0x7F
            if n == 126:
                n = struct.unpack(">H", self._read(2))[0]
            elif n == 127:
                n = struct.unpack(">Q", self._read(8))[0]
            mask = self._read(4) if b1 & 0x80 else None
            data = self._read(n)
            if mask:
                data = bytes(c ^ mask[i % 4] for i, c in enumerate(data))
            if op == 0x8:
                raise ConnectionError("websocket closed by peer")
            if op == 0x9:
                self._frame(0xA, data)
                continue
            if op in (0x0, 0x1, 0x2):
                parts.append(data)
                if b0 & 0x80:
                    return b"".join(parts).decode()

    def close(self):
        try:
            self.sock.close()
        except OSError:
            pass


class CDP:
    def __init__(self, ws_url):
        self.ws = WebSocket(ws_url)
        self.id = 0
        self.waiting = {}
        self.handlers = []
        self.log = []
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        try:
            while True:
                m = json.loads(self.ws.recv())
                if "id" in m and m["id"] in self.waiting:
                    slot = self.waiting.pop(m["id"])
                    slot[1] = m
                    slot[0].set()
                else:
                    for h in self.handlers:
                        h(m)
        except Exception:
            for slot in list(self.waiting.values()):
                slot[0].set()

    def send(self, method, params=None, session=None, wait=True, timeout=60):
        self.id += 1
        msg = {"id": self.id, "method": method, "params": params or {}}
        if session:
            msg["sessionId"] = session
        slot = [threading.Event(), None]
        if wait:
            self.waiting[self.id] = slot
        self.ws.send(json.dumps(msg))
        if not wait:
            return None
        if not slot[0].wait(timeout):
            raise TimeoutError(f"{method}: no answer in {timeout} s")
        if slot[1] is None:
            raise ConnectionError(f"{method}: connection lost")
        if "error" in slot[1]:
            raise RuntimeError(f"{method}: {slot[1]['error']}")
        return slot[1].get("result", {})

    def eval(self, expr, timeout=60):
        r = self.send("Runtime.evaluate", {"expression": expr, "returnByValue": True, "awaitPromise": True}, timeout=timeout)
        if r.get("exceptionDetails"):
            raise RuntimeError("eval failed: " + json.dumps(r["exceptionDetails"])[:600])
        return r["result"].get("value")


class NetLog:
    """Network events of the page and of every worker (auto-attached, paused until Network.enable)."""

    def __init__(self, cdp):
        self.cdp, self.req, self.status, self.failed, self.workers = cdp, {}, {}, {}, []
        cdp.handlers.append(self.on)

    def on(self, m):
        meth, p, sid = m.get("method"), m.get("params", {}), m.get("sessionId")
        key = lambda rid: (sid, rid)  # noqa: E731
        if meth == "Target.attachedToTarget":
            s = p["sessionId"]
            self.workers.append(p["targetInfo"].get("url"))
            self.cdp.send("Network.enable", session=s, wait=False)
            self.cdp.send("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": True, "flatten": True}, session=s, wait=False)
            self.cdp.send("Runtime.runIfWaitingForDebugger", session=s, wait=False)
        elif meth == "Network.requestWillBeSent":
            self.req[key(p["requestId"])] = p["request"]["url"]
        elif meth == "Network.responseReceived":
            self.status[key(p["requestId"])] = p["response"]["status"]
            self.req.setdefault(key(p["requestId"]), p["response"]["url"])
        elif meth == "Network.loadingFailed":
            self.failed[key(p["requestId"])] = p.get("errorText")
        elif meth == "Runtime.exceptionThrown":
            self.cdp.log.append("exception: " + json.dumps(p.get("exceptionDetails"))[:400])

    def summary(self):
        cdn = [k for k, u in self.req.items() if CDN_HOST in u]
        local = [k for k, u in self.req.items() if "/pyodide-local/" in u]
        bad = sorted({f"{self.failed.get(k) or self.status.get(k)} {u}" for k, u in self.req.items()
                      if CDN_HOST not in u and (self.status.get(k, 200) >= 400 or k in self.failed)})
        return {"requests": len(self.req), "cdn_requests": len(cdn),
                "cdn_ok": sum(1 for k in cdn if self.status.get(k) == 200),
                "pyodide_local_ok": sum(1 for k in local if self.status.get(k) == 200),
                "pyodide_local_wasm_ok": sum(1 for k in local if self.status.get(k) == 200 and self.req[k].split("?")[0].endswith("pyodide.asm.wasm")),
                "other_errors": bad[:20], "workers_attached": len(self.workers)}


# ------------------------------------------------------------------ verify

def find_chrome():
    cands = [os.environ.get("CHROME"),
             "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
             "/Applications/Chromium.app/Contents/MacOS/Chromium",
             shutil.which("google-chrome"), shutil.which("google-chrome-stable"), shutil.which("chromium"),
             shutil.which("chromium-browser")]
    for pat in ("~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-*/chrome-headless-shell",
                "~/.cache/ms-playwright/chromium_headless_shell-*/chrome-*/chrome-headless-shell"):
        cands += sorted(glob.glob(os.path.expanduser(pat)), reverse=True)
    for c in cands:
        if c and os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    sys.exit("No Chrome found (set CHROME=/path/to/chrome). offline_browser_kit never installs one.")


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".mjs": "text/javascript", ".js": "text/javascript", ".wasm": "application/wasm",
                      ".json": "application/json", ".whl": "application/zip", ".zip": "application/zip"}

    def log_message(self, *a):
        pass


class QuietServer(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        if not isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError)):
            super().handle_error(request, client_address)


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_http(url, timeout=20):
    t = time.monotonic()
    while time.monotonic() - t < timeout:
        try:
            with urllib.request.urlopen(url, timeout=2):
                return True
        except Exception:
            time.sleep(0.2)
    return False


class Browser:
    def __init__(self, chrome):
        self.profile = tempfile.mkdtemp(prefix="venue-kit-chrome-")
        self.proc = subprocess.Popen([chrome, "--headless=new", "--remote-debugging-port=0", f"--user-data-dir={self.profile}",
                                      f"--host-resolver-rules=MAP {CDN_HOST} 127.0.0.1",
                                      "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
                                      "--disable-renderer-backgrounding", "--window-size=1280,900", "about:blank"],
                                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        port_file = Path(self.profile) / "DevToolsActivePort"
        for _ in range(240):
            if port_file.is_file() and port_file.read_text().strip():
                break
            time.sleep(0.25)
        port = int(port_file.read_text().split()[0])
        self.version = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=10))["Browser"]
        page = next(t for t in json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json/list", timeout=10)) if t["type"] == "page")
        self.cdp = CDP(page["webSocketDebuggerUrl"])
        self.net = NetLog(self.cdp)
        for meth in ("Runtime.enable", "Page.enable", "Network.enable"):
            self.cdp.send(meth)
        self.cdp.send("Network.setCacheDisabled", {"cacheDisabled": True})
        self.cdp.send("Target.setAutoAttach", {"autoAttach": True, "waitForDebuggerOnStart": True, "flatten": True})
        # record every worker's ready message (URL, Pyodide source) without touching the site's code
        self.cdp.send("Page.addScriptToEvaluateOnNewDocument", {"source": """
          window.__vk = [];
          const W0 = window.Worker;
          window.Worker = class extends W0 { constructor(u, o) { super(u, o); const url = String(u);
            this.addEventListener('message', e => { const m = e.data;
              if (m && m.type === 'ready') window.__vk.push({ url, source: m.env.pyodide_source, base: m.env.pyodide_base,
                ready_ms: m.timings && m.timings.ready_ms, mb: m.mb }); }); } };"""})

    def goto(self, url, global_name, timeout=30):
        self.cdp.send("Page.navigate", {"url": url})
        t = time.monotonic()
        while time.monotonic() - t < timeout:
            time.sleep(0.2)
            try:
                if self.cdp.eval(f"typeof {global_name} === 'object'"):
                    return
            except Exception:
                pass
        raise TimeoutError(f"{global_name} did not appear on {url}")

    def close(self):
        try:
            self.cdp.ws.close()
        finally:
            self.proc.kill()
            self.proc.wait(10)
            shutil.rmtree(self.profile, ignore_errors=True)


def check_playground(chrome, base):
    out = {"page": base + "site/playground/index.html", "pass": False}
    b = Browser(chrome)
    out["chrome"] = b.version
    try:
        t0 = time.monotonic()
        b.goto(out["page"], "PG")
        try:
            b.cdp.eval("PG.ready.then(() => true)", timeout=300)
        except Exception as err:
            out["error"] = str(err)
            out["load_state"] = b.cdp.eval("PG.loadState()")
            return out
        out["ready_s"] = round(time.monotonic() - t0, 2)
        b.cdp.eval("PG.started.then(() => true)", timeout=60)
        out["env"] = b.cdp.eval("(e => ({ source: e.pyodide_source, base: e.pyodide_base, python: e.python, numpy: e.numpy, scipy: e.scipy, load_mb: PG_STATE.loadMb }))(PG_STATE.env)")
        out["status_line"] = b.cdp.eval("document.querySelector('#envMsg').textContent")
        b.cdp.eval("PG.loadPreset('random_0').then(() => true)", timeout=60)
        cfg = {"planner": "astar_known", "preset": "ideal", "fault": "truth", "filter": "none", "seed": 0}
        t1 = time.monotonic()
        r = b.cdp.eval(f"PG.run([{json.dumps(cfg)}]).then(x => x && x.map(y => ({{score: y.score, wall_s: y.wall_s, sim_s: y.sim_s, worker_ms: y.worker_ms}})))", timeout=300)
        out["run"] = {"world": "random_0", "config": cfg, "click_to_result_s": round(time.monotonic() - t1, 2), "result": (r or [None])[0]}
        out["cdn_probe"] = b.cdp.eval(f"fetch('https://{CDN_HOST}/pyodide/v314.0.7/full/pyodide.mjs', {{mode: 'no-cors', cache: 'no-store'}}).then(() => 'reachable', e => 'blocked: ' + e)", timeout=30)
        out["net"] = b.net.summary()
        out["console"] = b.cdp.log[:10]
        score = (out["run"]["result"] or {}).get("score")
        out["pass"] = bool(score) and out["env"]["source"] == "local" and out["net"]["cdn_ok"] == 0 and out["cdn_probe"].startswith("blocked")
    finally:
        b.close()
    return out


def check_solver(chrome, base):
    out = {"page": base + "site/solver/index.html?map=random_0", "pass": False}
    b = Browser(chrome)
    try:
        t0 = time.monotonic()
        b.goto(out["page"], "SOLVER")
        b.cdp.eval("SOLVER.ready.then(() => true)", timeout=300)
        out["python_ready_s"] = round(time.monotonic() - t0, 2)
        t1 = time.monotonic()
        out["sweep"] = b.cdp.eval("SOLVER.quick().then(sw => ({ done: sw.done, total: sw.total, elapsed_s: sw.elapsed_s, cancelled: sw.cancelled, workers_ready: SOLVER.S.readyCount, K: SOLVER.K }))", timeout=900)
        out["sweep"]["wall_s_from_click"] = round(time.monotonic() - t1, 2)
        out["headline"] = b.cdp.eval("JSON.parse(SOLVER.exportJSON()).headline.text")
        out["workers"] = b.cdp.eval("window.__vk")
        out["env_source"] = b.cdp.eval("SOLVER.S.env.pyodide_source")
        out["net"] = b.net.summary()
        out["console"] = b.cdp.log[:10]
        w, sw = out["workers"] or [], out["sweep"]
        pool_ok = (len(w) == sw["K"] and all(x["source"] == "local" for x in w)
                   and all(urllib.parse.urlparse(x["url"]).path.endswith("/site/playground/worker.js") for x in w))
        out["pool_uses_local_pyodide"] = pool_ok
        out["pass"] = pool_ok and sw["done"] == sw["total"] > 0 and not sw["cancelled"] and out["net"]["cdn_ok"] == 0
    finally:
        b.close()
    return out


def cmd_verify(args):
    chrome = find_chrome()
    server, proc = None, None
    if args.kit:
        kit = Path(args.kit).resolve()
        port = free_port()
        proc = subprocess.Popen([sys.executable, str(kit / "serve.py"), "--port", str(port)], cwd=tempfile.gettempdir(),
                                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        report_dir = local_dir(load_manifest(kit / "site/playground/manifest.json"), kit / "site/playground")
        served = f"{kit} via its serve.py"
    else:
        server = QuietServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(ROOT)))
        port = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
        report_dir = local_dir(load_manifest())
        served = f"{ROOT} via http.server"
    base = f"http://127.0.0.1:{port}/"
    if not (report_dir / "pyodide.mjs").is_file():
        print(f"note: {report_dir}/pyodide.mjs is missing; run prepare first (the pages will try the blocked CDN)")
    try:
        if not wait_http(base + "site/playground/manifest.json"):
            sys.exit(f"server at {base} did not answer")
        print(f"serving {served} at {base}; Chrome: {chrome}; {CDN_HOST} => 127.0.0.1 (blocked)")
        res = {"date": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "input": "synthetic arena worlds, real local load",
               "served": served, "chrome_path": chrome, "cdn": f"{CDN_HOST} mapped to 127.0.0.1"}
        res["playground"] = check_playground(chrome, base)
        p = res["playground"]
        print(f"playground: {'PASS' if p['pass'] else 'FAIL'}  ready {p.get('ready_s')} s, source {p.get('env', {}).get('source')}, "
              f"run {p.get('run', {}).get('click_to_result_s')} s, CDN probe {p.get('cdn_probe')}, cdn requests {p.get('net', {}).get('cdn_requests')} (ok {p.get('net', {}).get('cdn_ok')})")
        if not args.playground_only:
            res["solver"] = check_solver(chrome, base)
            s = res["solver"]
            sw = s.get("sweep", {})
            print(f"solver:     {'PASS' if s['pass'] else 'FAIL'}  ready {s.get('python_ready_s')} s, Quick sweep {sw.get('done')}/{sw.get('total')} "
                  f"in {sw.get('wall_s_from_click')} s, workers {len(s.get('workers') or [])}/{sw.get('K')} on local Pyodide: {s.get('pool_uses_local_pyodide')}, "
                  f"cdn requests {s.get('net', {}).get('cdn_requests')} (ok {s.get('net', {}).get('cdn_ok')})")
        res["pass"] = all(res[k]["pass"] for k in ("playground", "solver") if k in res)
        if report_dir.is_dir():
            dst = report_dir / (REPORT_PREFIX + ("verify-kit.json" if args.kit else "verify.json"))
            dst.write_text(json.dumps(res, indent=1) + "\n")
            print(f"report: {dst}")
        print("PASS" if res["pass"] else "FAIL")
        if not res["pass"]:
            print(json.dumps(res, indent=1)[:4000])
            sys.exit(1)
    finally:
        if server:
            server.shutdown()
        if proc:
            proc.kill()
            proc.wait(10)


# ------------------------------------------------------------------ bundle

SERVE_PY = '''#!/usr/bin/env python3
"""Offline browser kit server (stdlib only). Serves this folder so the playground and the Solver load Pyodide
from site/playground/pyodide-local/ instead of cdn.jsdelivr.net.
  python3 serve.py [--port 8000] [--bind 127.0.0.1]
"""
import argparse
import functools
import http.server
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                      ".mjs": "text/javascript", ".js": "text/javascript", ".wasm": "application/wasm",
                      ".json": "application/json", ".whl": "application/zip", ".zip": "application/zip"}

    def log_message(self, *a):
        pass


class Server(http.server.ThreadingHTTPServer):
    def handle_error(self, request, client_address):
        if not isinstance(sys.exc_info()[1], (BrokenPipeError, ConnectionResetError)):
            super().handle_error(request, client_address)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--bind", default="127.0.0.1")
    a = ap.parse_args()
    srv = Server((a.bind, a.port), functools.partial(Handler, directory=HERE))
    host = "localhost" if a.bind in ("127.0.0.1", "0.0.0.0") else a.bind
    print(f"Serving {HERE}")
    print(f"  playground: http://{host}:{a.port}/site/playground/")
    print(f"  solver:     http://{host}:{a.port}/site/solver/")
    print("Ctrl-C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
'''


def cmd_bundle(args):
    m = load_manifest()
    folder = local_dir(m)
    if not (folder / "pyodide-lock.json").is_file():
        sys.exit(f"{folder.relative_to(ROOT)}/ is empty: run `python3 tools/offline_browser_kit.py prepare` first")
    missing_core = [f for f in CORE_FILES if not (folder / f).is_file()]
    checks = check_wheels(folder, wheel_entries(parse_lock((folder / "pyodide-lock.json").read_text()), m["packages"]))
    bad = [c for c in checks if c[1] != "ok"] + [(f, "missing") for f in missing_core]
    if bad:
        sys.exit(f"vendored folder incomplete: {bad}; run prepare again")
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    rels = bundle_entries()
    tmp = Path(str(out) + ".part")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for rel in rels:
            z.write(ROOT / rel, rel)
        zi = zipfile.ZipInfo("serve.py", time.localtime()[:6])
        zi.external_attr = 0o755 << 16
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, SERVE_PY)
    os.replace(tmp, out)
    src_mb = sum((ROOT / r).stat().st_size for r in rels) / MB
    vend = sum(1 for r in rels if "/pyodide-local/" in r)
    outside = sum(1 for r in rels if not r.startswith("site/"))
    print(f"{out}: {out.stat().st_size / MB:.1f} MB zipped ({src_mb:.1f} MB unzipped), {len(rels) + 1} files "
          f"({vend} vendored Pyodide, {outside} manifest files outside site/, serve.py), {time.monotonic() - t0:.1f} s")
    print(f"use: unzip {out.name} -d offline-browser-kit && cd offline-browser-kit && python3 serve.py  => http://localhost:8000/site/playground/")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare", help="download and sha256-check Pyodide core + numpy + scipy")
    p.add_argument("--force", action="store_true", help="download again even when cached")
    p.add_argument("--version", default="314.0.7", help="expected Pyodide version (must match manifest.json)")
    v = sub.add_parser("verify", help="headless Chrome, CDN blocked: one playground run, one Solver Quick sweep")
    v.add_argument("--kit", help="unzipped offline browser kit folder: serve it with its own serve.py instead of the repo")
    v.add_argument("--playground-only", action="store_true")
    b = sub.add_parser("bundle", help="zip site/ + manifest files + vendored Pyodide + serve.py")
    b.add_argument("--out", default=str(ROOT / "dist" / "offline-browser-kit.zip"))
    a = ap.parse_args(argv)
    {"prepare": cmd_prepare, "verify": cmd_verify, "bundle": cmd_bundle}[a.cmd](a)


if __name__ == "__main__":
    main()
