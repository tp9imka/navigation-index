#!/usr/bin/env python3
"""Post-deploy smoke check for the live site (stdlib only, Python 3.12).

Why: Cloudflare Pages without a root 404.html answered every missing path with the home page
(200 text/html). site/playground/worker.js probed for a local Pyodide folder, got that 200 and
failed to load (fixed in a42d49f). Nothing checked the deployed site; this does.

Checks (one output line each, PASS or FAIL; exit code 1 on any FAIL):
  1 missing-404      a missing path answers 404, not 200 HTML
  2 pages            every page linked from the home page and site/nav.js answers 200 text/html
  2 assets           every local script, stylesheet and JS module those pages load (with ?v=), plus
                     site/playground/worker.js, manifest.json and every manifest "files" src, answers
                     200; .js/.mjs/.json/.py/.css must not come back as HTML
  3 worker-version   WORKER_URL ?v= in playground.js equals WORKER_V in solver.js (deployed copies)
  3 js-equals-local  every git-tracked site/**/*.js and *.mjs has the same sha256 deployed and local
  4 pyodide-base     HEAD <pyodide_base>pyodide.mjs answers 200 with a JavaScript content type
  4 local-probe      with pyodide_source auto, HEAD <pyodide_local>pyodide.mjs answers 404

Usage:
  python3 tools/check_deploy.py                       # https://navigation-index.pages.dev/
  python3 tools/check_deploy.py http://127.0.0.1:8000/ --json
  python3 tools/check_deploy.py URL --pyodide-base http://mirror/pyodide/   # offline tests, mirrors
"""
import argparse
import hashlib
import html.parser
import json
import re
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BASE = "https://navigation-index.pages.dev/"
TIMEOUT_S = 20            # per request
RETRIES = 2               # extra attempts after a network error or a 5xx answer
RETRY_WAIT_S = 3          # wait before each retry
MAX_REPORT = 5            # first N problems printed per check
USER_AGENT = "navigation-index-check-deploy/1"
NON_HTML_EXT = {".js", ".mjs", ".json", ".py", ".css"}
PAGE_EXT = {"", ".html", ".htm"}
LOCAL_JS_GLOBS = ("site/**/*.js", "site/**/*.mjs")

IMPORT_RE = re.compile(r"""(?:\bimport|\bexport)\s[^;"'`]*?\bfrom\s*["']([^"']+)["']"""
                       r"""|\bimport\s*["']([^"']+)["']""")
WORKER_URL_RE = re.compile(r"""\bWORKER_URL\s*=\s*["']([^"']+)["']""")
WORKER_V_RE = re.compile(r"""\bWORKER_V\s*=\s*["']([^"']+)["']""")
NAV_PATH_RE = re.compile(r"""\bpath:\s*["']([^"']*)["']""")


class Resp:
    def __init__(self, url, status=0, ctype="", body=b"", error=""):
        self.url, self.status, self.ctype, self.body, self.error = url, status, ctype, body, error

    def text(self):
        return self.body.decode("utf-8", errors="replace")

    def short(self):
        if self.error:
            return f"error {self.error}"
        return f"{self.status} {self.ctype or '(no content-type)'}"


def _opener(url):
    host = urllib.parse.urlsplit(url).hostname or ""
    if host in ("127.0.0.1", "localhost", "::1"):
        return urllib.request.build_opener(urllib.request.ProxyHandler({}))
    return urllib.request.build_opener()


_CACHE = {}


def fetch(url, method="GET"):
    """One request with RETRIES retries on network errors and 5xx. 4xx answers return at once."""
    key = (method, url)
    if key in _CACHE:
        return _CACHE[key]
    headers = {"User-Agent": USER_AGENT, "Cache-Control": "no-cache"}
    resp = None
    for attempt in range(RETRIES + 1):
        if attempt:
            time.sleep(RETRY_WAIT_S)
        req = urllib.request.Request(url, method=method, headers=headers)
        try:
            with _opener(url).open(req, timeout=TIMEOUT_S) as r:
                body = r.read() if method == "GET" else b""
                resp = Resp(r.geturl(), r.status, r.headers.get("Content-Type", ""), body)
        except urllib.error.HTTPError as e:
            with e:
                body = e.read() if method == "GET" else b""
                resp = Resp(url, e.code, e.headers.get("Content-Type", "") if e.headers else "", body or b"")
        except (urllib.error.URLError, TimeoutError, OSError) as e:
            resp = Resp(url, error=str(getattr(e, "reason", e)))
        if resp.status and resp.status < 500:
            break
    _CACHE[key] = resp
    return resp


def ext_of(url):
    path = urllib.parse.urlsplit(url).path
    name = path.rsplit("/", 1)[-1]
    return ("." + name.rsplit(".", 1)[-1].lower()) if "." in name else ""


def strip_query(url):
    s = urllib.parse.urlsplit(url)
    return urllib.parse.urlunsplit((s.scheme, s.netloc, s.path, "", ""))


def is_html(ctype):
    return "text/html" in (ctype or "").lower()


class _Refs(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.anchors, self.assets = [], []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.anchors.append(a["href"])
        elif tag == "script" and a.get("src"):
            self.assets.append(a["src"])
        elif tag == "link" and a.get("href"):
            rel = (a.get("rel") or "").lower()
            if "stylesheet" in rel or "modulepreload" in rel or "preload" in rel or rel == "manifest":
                self.assets.append(a["href"])


def parse_html(text):
    p = _Refs()
    p.feed(text)
    return p


class Site:
    def __init__(self, base):
        self.base = base if base.endswith("/") else base + "/"

    def local(self, ref, against):
        """Absolute URL of ref if it points inside the site, else None. Fragment dropped."""
        if not ref or ref.startswith(("data:", "mailto:", "javascript:", "#")):
            return None
        url = urllib.parse.urljoin(against, ref)
        url = urllib.parse.urldefrag(url)[0]
        return url if url.startswith(self.base) else None

    def rel(self, url):
        return "/" + url[len(self.base):] if url.startswith(self.base) else url


def _result(check, ok, detail, problems=None):
    return {"check": check, "status": "PASS" if ok else "FAIL", "detail": detail,
            "problems": (problems or [])[:MAX_REPORT], "problem_count": len(problems or [])}


def check_missing(site):
    url = site.base + f"__check_deploy_missing__/{secrets.token_hex(4)}.html"
    r = fetch(url)
    ok = r.status == 404
    detail = f"GET {site.rel(url)} => {r.short()}"
    if r.status == 200 and is_html(r.ctype):
        detail += " (host serves a fallback page for missing paths)"
    return _result("1 missing-404", ok, detail)


def discover_pages(site, home):
    """Pages: the home page, its local <a> links that look like pages, and nav.js PAGES."""
    pages, files = [site.base], []
    for href in parse_html(home.text()).anchors:
        u = site.local(href, site.base)
        if not u:
            continue
        (pages if ext_of(u) in PAGE_EXT else files).append(u)
    nav = fetch(site.base + "site/nav.js")
    nav_text = nav.text() if nav.status == 200 else (ROOT / "site/nav.js").read_text()
    m = re.search(r"PAGES\s*=\s*\[(.*?)\];", nav_text, re.S)
    for p in NAV_PATH_RE.findall(m.group(1) if m else ""):
        pages.append(site.base + p)
    return list(dict.fromkeys(pages)), list(dict.fromkeys(files))


def js_imports(site, url, text):
    out = []
    for m in IMPORT_RE.finditer(text):
        ref = m.group(1) or m.group(2)
        if ref.startswith(("./", "../", "/")):
            u = site.local(ref, url)
            if u:
                out.append(u)
    return out


def check_pages_assets(site):
    """Returns (pages result, assets result, context dict with deployed bodies)."""
    home = fetch(site.base)
    pages, linked_files = discover_pages(site, home)
    page_problems, assets = [], {}
    for p in pages:
        r = fetch(p)
        if r.status != 200 or not is_html(r.ctype):
            page_problems.append(f"{site.rel(p)} => {r.short()}")
            continue
        for ref in parse_html(r.text()).assets:
            u = site.local(ref, r.url if r.url.startswith(site.base) else p)
            if u:
                assets.setdefault(u, f"loaded by {site.rel(p)}")
    for f in linked_files:
        assets.setdefault(f, "linked from home")

    ctx = {"manifest_url": None, "manifest": None, "bodies": {}}
    queue = list(assets)
    asset_problems, seen = [], set()

    def add(u, why):
        if u and u not in assets:
            assets[u] = why
            queue.append(u)

    while queue:
        u = queue.pop(0)
        if u in seen:
            continue
        seen.add(u)
        r = fetch(u)
        ext = ext_of(u)
        bad = r.status != 200 or (ext in NON_HTML_EXT and is_html(r.ctype))
        if bad:
            asset_problems.append(f"{site.rel(u)} => {r.short()} ({assets[u]})")
            continue
        path = urllib.parse.urlsplit(u).path
        ctx["bodies"][path] = r.text()
        if ext in (".js", ".mjs"):
            text = r.text()
            for imp in js_imports(site, u, text):
                add(imp, f"imported by {site.rel(u)}")
            wm = WORKER_URL_RE.search(text)
            if wm and path.endswith("/playground.js"):
                add(site.local(wm.group(1), u), f"WORKER_URL in {site.rel(u)}")
            if path.endswith("/playground/worker.js"):
                add(site.local("manifest.json", u), f"fetched by {site.rel(u)}")
        if path.endswith("/playground/manifest.json"):
            try:
                man = json.loads(r.text())
            except ValueError as e:
                asset_problems.append(f"{site.rel(u)} => not JSON ({e})")
                continue
            ctx["manifest_url"], ctx["manifest"] = u, man
            for f in man.get("files", []):
                add(site.local(f.get("src", ""), u), f"manifest files src {f.get('src')}")

    # worker.js and manifest.json must be in the crawl even if playground.js changed shape
    for must in ("site/playground/worker.js", "site/playground/manifest.json"):
        if not any(urllib.parse.urlsplit(a).path.endswith("/" + must) for a in assets):
            asset_problems.append(f"/{must} => not reached from any page (WORKER_URL or manifest lookup failed)")

    pr = _result("2 pages", not page_problems,
                 f"{len(pages) - len(page_problems)}/{len(pages)} pages 200 text/html", page_problems)
    ar = _result("2 assets", not asset_problems,
                 f"{len(assets) - len(asset_problems)}/{len(assets)} assets 200, scripts/data not HTML",
                 asset_problems)
    return pr, ar, ctx


def check_worker_version(site, ctx):
    pg = next((t for p, t in ctx["bodies"].items() if p.endswith("/site/playground/playground.js")), None)
    sv = next((t for p, t in ctx["bodies"].items() if p.endswith("/site/solver/solver.js")), None)
    if pg is None:
        pg = fetch(site.base + "site/playground/playground.js").text()
    if sv is None:
        sv = fetch(site.base + "site/solver/solver.js").text()
    wm, vm = WORKER_URL_RE.search(pg or ""), WORKER_V_RE.search(sv or "")
    pv = urllib.parse.parse_qs(urllib.parse.urlsplit(wm.group(1)).query).get("v", [None])[0] if wm else None
    sv_v = vm.group(1) if vm else None
    ok = pv is not None and pv == sv_v
    return _result("3 worker-version", ok, f"playground.js WORKER_URL v={pv}, solver.js WORKER_V={sv_v}")


def local_js_files():
    try:
        # :(glob) makes "**/" match zero folders too, so site/nav.js is included
        out = subprocess.run(["git", "-C", str(ROOT), "ls-files", "--", *(":(glob)" + g for g in LOCAL_JS_GLOBS)],
                             capture_output=True, text=True, check=True, timeout=TIMEOUT_S).stdout
        files = [ln for ln in out.splitlines() if ln]
        if files:
            return sorted(files)
    except (OSError, subprocess.SubprocessError):
        pass
    return sorted({str(p.relative_to(ROOT)) for g in LOCAL_JS_GLOBS for p in ROOT.glob(g)})


def check_js_equals_local(site):
    files, problems = local_js_files(), []
    for rel in files:
        local = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
        r = fetch(site.base + urllib.parse.quote(rel))
        if r.status != 200:
            problems.append(f"/{rel} => {r.short()}")
        elif hashlib.sha256(r.body).hexdigest() != local:
            problems.append(f"/{rel} => sha256 {hashlib.sha256(r.body).hexdigest()[:12]} deployed, "
                            f"{local[:12]} local")
    if not files:
        problems.append("no local site js files found: nothing compared")
    return _result("3 js-equals-local", not problems,
                   f"{len(files) - len(problems)}/{len(files)} site js files match the local checkout", problems)


def check_pyodide(site, ctx, pyodide_base=None):
    man, murl = ctx["manifest"], ctx["manifest_url"]
    if man is None:
        murl = site.base + "site/playground/manifest.json"
        r = fetch(murl)
        try:
            man = json.loads(r.text()) if r.status == 200 else None
        except ValueError:
            man = None
    if man is None:
        msg = "manifest.json not readable from the deploy"
        return [_result("4 pyodide-base", False, msg), _result("4 local-probe", False, msg)]
    base = pyodide_base or man.get("pyodide_base", "")
    base = base if base.endswith("/") else base + "/"
    r = fetch(base + "pyodide.mjs", method="HEAD")
    ok = r.status == 200 and "javascript" in r.ctype.lower()
    out = [_result("4 pyodide-base", ok, f"HEAD {base}pyodide.mjs => {r.short()}")]
    source = man.get("pyodide_source", "cdn")
    if source == "auto" and man.get("pyodide_local"):
        probe = urllib.parse.urljoin(murl, man["pyodide_local"]) + "pyodide.mjs"
        p = fetch(probe, method="HEAD")
        detail = f"HEAD {site.rel(probe)} => {p.short()}"
        if p.status == 200 and is_html(p.ctype):
            detail += " (fallback page: worker.js must not take it for Pyodide)"
        out.append(_result("4 local-probe", p.status == 404, detail))
    else:
        out.append(_result("4 local-probe", True, f"skipped: pyodide_source is {source}"))
    return out


def run_checks(base=DEFAULT_BASE, pyodide_base=None):
    _CACHE.clear()
    site = Site(base)
    results = [check_missing(site)]
    pr, ar, ctx = check_pages_assets(site)
    results += [pr, ar, check_worker_version(site, ctx), check_js_equals_local(site)]
    results += check_pyodide(site, ctx, pyodide_base)
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description="Post-deploy smoke check for the live site.")
    ap.add_argument("base", nargs="?", default=DEFAULT_BASE, help=f"site base URL (default {DEFAULT_BASE})")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--pyodide-base", help="override manifest pyodide_base (offline tests, mirrors)")
    args = ap.parse_args(argv)
    results = run_checks(args.base, args.pyodide_base)
    failed = sum(r["status"] == "FAIL" for r in results)
    if args.json:
        print(json.dumps({"base": args.base, "failed": failed, "results": results}, indent=2))
    else:
        for r in results:
            print(f"{r['status']}  {r['check']}: {r['detail']}")
            for p in r["problems"]:
                print(f"      {p}")
            more = r["problem_count"] - len(r["problems"])
            if more > 0:
                print(f"      ... {more} more")
        print(f"{len(results) - failed}/{len(results)} checks passed against {args.base}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
