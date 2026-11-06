#!/usr/bin/env python3
"""Pre-hackathon offline cache: datasets, Docker images, pip wheels, git bundles, JS, map tiles.

  python3 prep.py --dry-run --profile full            # sizes, totals, licenses from the manifest
  python3 prep.py --dry-run --probe                   # also ask hosts for unknown sizes
  python3 prep.py --profile standard --out /Volumes/USB/navkit
  python3 prep.py --types dataset --items 'dataset:nclt*'
  python3 prep.py --verify --out DIR                  # recheck SHA256SUMS
  python3 prep.py --serve 8000 --out DIR              # share with teammates (Range-capable)
  python3 prep.py --pull-from http://10.0.0.5:8000 --out DIR

Stdlib only. Downloads resume (.part + HTTP Range); finished items are recorded in
DIR/.prep-state.json and skipped on the next run. See README.md.
"""
import argparse
import datetime
import fnmatch
import hashlib
import html.parser
import http.server
import json
import os
import platform
import re
import shutil
import socketserver
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile

KIT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(KIT, "..", ".."))
UA = "navigation-index-offline-kit/1"
CHUNK = 1 << 20
RETRIES = 6
BACKOFF_S = 5
HTTP_TIMEOUT_S = 60
PROTOMAPS_LOOKBACK_DAYS = 10
TYPES = ("dataset", "script", "pip", "docker", "docker-build", "git", "js", "tool", "tiles")


class FetchError(Exception):
    pass


def human(n):
    if n is None:
        return "unknown"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1000 or unit == "TB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.2f} {unit}"
        n /= 1000


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------- HTTP

def request(url, method="GET", headers=None, timeout=HTTP_TIMEOUT_S):
    hdrs = {"User-Agent": UA}
    if "api.github.com" in url and os.environ.get("GITHUB_TOKEN"):
        hdrs["Authorization"] = "Bearer " + os.environ["GITHUB_TOKEN"]
    hdrs.update(headers or {})
    last = None
    for attempt in range(RETRIES):
        try:
            return urllib.request.urlopen(urllib.request.Request(url, method=method, headers=hdrs), timeout=timeout)
        except urllib.error.HTTPError as e:
            if e.code == 416:
                raise
            if e.code not in (408, 429, 500, 502, 503, 504):
                raise FetchError(f"HTTP {e.code} for {url}") from e
            wait = int(e.headers.get("Retry-After") or BACKOFF_S * 2 ** attempt)
            last = e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            wait, last = BACKOFF_S * 2 ** attempt, e
        log(f"    retry in {wait}s ({last})")
        time.sleep(wait)
    raise FetchError(f"giving up on {url}: {last}")


def get_json(url):
    with request(url) as r:
        return json.load(r)


def get_text(url):
    with request(url) as r:
        return r.read().decode("utf-8", "replace")


def head_size(url):
    """Content-Length from HEAD, else the total from a one-byte ranged GET."""
    try:
        with request(url, method="HEAD") as r:
            n = r.headers.get("Content-Length")
            if n:
                return int(n)
        with request(url, headers={"Range": "bytes=0-0"}) as r:
            m = re.search(r"/(\d+)$", r.headers.get("Content-Range") or "")
            return int(m.group(1)) if m else None
    except (FetchError, urllib.error.HTTPError):
        return None


def file_hash(path, algo="sha256"):
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(CHUNK), b""):
            h.update(block)
    return h.hexdigest()


def download(url, dest, size=None, md5=None, sha256=None):
    """Resumable download to dest via dest.part. Returns sha256 of the result."""
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    if os.path.exists(dest) and (size is None or os.path.getsize(dest) == size):
        digest = file_hash(dest)
        if sha256 and digest != sha256:
            raise FetchError(f"sha256 mismatch on existing {dest}")
        return digest
    part = dest + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    if size is not None and have > size:
        os.remove(part)
        have = 0
    if have:
        log(f"    resuming at {human(have)}")
    for attempt in range(RETRIES):
        headers = {"Range": f"bytes={have}-"} if have else {}
        try:
            r = request(url, headers=headers, timeout=HTTP_TIMEOUT_S)
        except urllib.error.HTTPError as e:
            if e.code == 416 and have:
                break
            raise FetchError(f"HTTP {e.code} for {url}") from e
        with r:
            if have and r.status != 206:
                have = 0
            mode = "ab" if have else "wb"
            total = r.headers.get("Content-Length")
            if (r.headers.get("Content-Type") or "").startswith("text/html") and "drive.usercontent" in url:
                raise FetchError("Google Drive returned an HTML page (quota or confirm wall); retry later or use gdown")
            try:
                with open(part, mode) as f:
                    for block in iter(lambda: r.read(CHUNK), b""):
                        f.write(block)
                        have += len(block)
                break
            except (TimeoutError, ConnectionError, urllib.error.URLError) as e:
                log(f"    interrupted at {human(have)} ({e}); resuming")
                time.sleep(BACKOFF_S)
    else:
        raise FetchError(f"could not complete {url}")
    got = os.path.getsize(part)
    if size is not None and got != size:
        raise FetchError(f"size mismatch for {dest}: got {got}, expected {size} (kept .part for resume)")
    if md5 and file_hash(part, "md5") != md5:
        os.remove(part)
        raise FetchError(f"md5 mismatch for {dest}; .part deleted")
    digest = file_hash(part)
    if sha256 and digest != sha256:
        os.remove(part)
        raise FetchError(f"sha256 mismatch for {dest}; .part deleted")
    os.replace(part, dest)
    return digest


def run(cmd, cwd=None, check=True, capture=False):
    log("    $ " + " ".join(cmd))
    p = subprocess.run(cmd, cwd=cwd, text=True, capture_output=capture)
    if check and p.returncode:
        raise FetchError(f"command failed ({p.returncode}): {' '.join(cmd)}\n{(p.stderr or '')[-800:] if capture else ''}")
    return p


# ---------------------------------------------------------------- dataset resolvers

class _Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href and not href.startswith(("?", "#", "/")) and "://" not in href:
                self.links.append(href)


def resolve_files(spec):
    """Expand one manifest file spec into [(url, relpath, size, md5, sha256)]."""
    m = spec["method"]
    dest = spec["dest"]
    if m in ("http", "gdrive"):
        url = spec["url"] if m == "http" else (
            f"https://drive.usercontent.google.com/download?id={spec['id']}&export=download&confirm=t")
        md5 = spec.get("md5")
        if spec.get("md5_url"):
            md5 = get_text(spec["md5_url"]).split()[0]
        return [(url, dest, spec.get("size"), md5, spec.get("sha256"))]
    if m == "zenodo":
        rec = get_json(f"https://zenodo.org/api/records/{spec['record']}")
        return [(f["links"]["self"], os.path.join(dest, f["key"]), f["size"],
                 f["checksum"].split(":", 1)[1] if f["checksum"].startswith("md5:") else None, None)
                for f in rec["files"]]
    if m == "mendeley":
        rec = get_json(f"https://data.mendeley.com/public-api/datasets/{spec['dataset']}")
        return [(f["content_details"]["download_url"], os.path.join(dest, f["filename"]), f["content_details"]["size"],
                 None, f["content_details"].get("sha256_hash")) for f in rec["files"]]
    if m == "s3prefix":
        out, token = [], None
        while True:
            q = {"list-type": "2", "prefix": spec["prefix"]}
            if token:
                q["continuation-token"] = token
            xml = get_text(spec["endpoint"] + "/?" + urllib.parse.urlencode(q))
            for key, etag, size in re.findall(r"<Key>([^<]+)</Key>.*?<ETag>&quot;([^&]+)&quot;</ETag><Size>(\d+)</Size>", xml):
                sub = key[len(spec["prefix"]):]
                if any(sub.startswith(inc) for inc in spec["include"]):
                    out.append((f"{spec['endpoint']}/{urllib.parse.quote(key)}", os.path.join(dest, sub), int(size),
                                etag if "-" not in etag else None, None))
            token = (re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", xml) or [None, None])[1]
            if not token:
                return out
    if m == "httpdir":
        out, todo = [], [spec["url"]]
        while todo:
            base = todo.pop()
            p = _Links()
            p.feed(get_text(base))
            for href in p.links:
                url = urllib.parse.urljoin(base, href)
                rel = os.path.join(dest, urllib.parse.unquote(url[len(spec["url"]):]))
                if href.endswith("/"):
                    todo.append(url)
                else:
                    out.append((url, rel, head_size(url), None, None))
        return out
    if m == "lfs":
        ptr = get_text(f"https://raw.githubusercontent.com/{spec['repo']}/{spec['ref']}/{spec['path']}")
        oid = re.search(r"oid sha256:([0-9a-f]{64})", ptr)
        size = re.search(r"^size (\d+)", ptr, re.M)
        if not oid:
            raise FetchError(f"{spec['path']} is not an LFS pointer")
        return [(f"https://media.githubusercontent.com/media/{spec['repo']}/{spec['ref']}/{spec['path']}", dest,
                 int(size.group(1)), None, oid.group(1))]
    raise FetchError(f"no resolver for method {m}")


# ---------------------------------------------------------------- fetchers

def fetch_dataset(item, ctx):
    base = os.path.join(ctx.out, "datasets", item["id"].split(":", 1)[1])
    files, manual = {}, []
    for spec in item["files"]:
        if spec["method"] == "manual":
            manual.append(spec["instructions"])
            continue
        if spec["method"] == "git":
            files.update(git_bundle(spec["url"], os.path.join(base, spec["dest"]), ctx))
            continue
        for url, rel, size, md5, sha in resolve_files(spec):
            dest = os.path.normpath(os.path.join(base, rel))
            log(f"    {rel} ({human(size)})")
            files[os.path.relpath(dest, ctx.out)] = download(url, dest, size, md5, sha)
    if manual:
        for m in manual:
            log(f"    MANUAL: {m}")
        return files, "manual"
    return files, "done"


def git_bundle(url, dest_base, ctx):
    name = dest_base.rstrip("/")
    mirror = os.path.join(ctx.out, "git", "mirrors", os.path.basename(name) + ".git")
    bundle = name + ".bundle"
    os.makedirs(os.path.dirname(bundle), exist_ok=True)
    if os.path.isdir(mirror):
        run(["git", "-C", mirror, "remote", "update", "--prune"])
    else:
        os.makedirs(os.path.dirname(mirror), exist_ok=True)
        run(["git", "clone", "--mirror", url, mirror])
    run(["git", "-C", mirror, "bundle", "create", bundle + ".part", "--all"])
    run(["git", "-C", mirror, "bundle", "verify", bundle + ".part"], capture=True)
    os.replace(bundle + ".part", bundle)
    if not ctx.keep_mirrors:
        shutil.rmtree(mirror)
    return {os.path.relpath(bundle, ctx.out): file_hash(bundle)}


def fetch_git(item, ctx):
    owner_name = item["id"].split(":", 1)[1].replace("/", "__")
    return git_bundle(item["url"], os.path.join(ctx.out, "git", "bundles", owner_name), ctx), "done"


def docker_save(image, plat, ctx):
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", image)
    dest = os.path.join(ctx.out, "docker", f"{safe}__{plat.replace('/', '-')}.tar")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    run(["docker", "save", "--platform", plat, "-o", dest + ".part", image])
    os.replace(dest + ".part", dest)
    return {os.path.relpath(dest, ctx.out): file_hash(dest)}


def fetch_docker(item, ctx):
    files = {}
    for plat in ctx.docker_platforms or item["platforms"]:
        run(["docker", "pull", "--platform", plat, item["image"]])
        files.update(docker_save(item["image"], plat, ctx))
    return files, "done"


def native_docker_platform():
    arch = {"x86_64": "amd64", "amd64": "amd64", "arm64": "arm64", "aarch64": "arm64"}[platform.machine().lower()]
    return "linux/" + arch


def fetch_docker_build(item, ctx):
    ctxdir = os.path.join(ctx.repo, item["context"])
    run(["docker", "build", "-t", item["image"], "-f", os.path.join(ctxdir, item["dockerfile"]), ctxdir])
    return docker_save(item["image"], native_docker_platform(), ctx), "done"


def fetch_pip(item, ctx):
    pip, failures = ctx.pip, []
    sdist = os.path.join(ctx.out, "pip", "sdist")
    reqs = item["requirements"]
    groups = [[r] for r in reqs] if item.get("each") else [reqs]
    for plat_key, tags in ctx.manifest["pip_platforms"].items():
        if ctx.pip_platforms and plat_key not in ctx.pip_platforms:
            continue
        base = pip + ["download", "-q", "-d", os.path.join(ctx.out, "pip", plat_key), "--only-binary=:all:",
                      "--implementation", "cp", "--python-version", ctx.python_version] + [a for t in tags for a in ("--platform", t)]
        for group in groups:
            if not group or run(base + group, check=False).returncode == 0:
                continue
            for req in group:
                if len(group) > 1 and run(base + [req], check=False).returncode == 0:
                    continue
                ok = run(pip + ["download", "-q", "-d", sdist, "--no-deps", "--no-binary=:all:", req], check=False).returncode == 0
                failures.append(f"{plat_key}: {req} has no wheel" + (" (sdist saved, needs a build toolchain offline)" if ok else " and no sdist"))
    for req in item.get("vcs", []):
        if run(pip + ["download", "-q", "-d", sdist, "--no-deps", req], check=False).returncode:
            failures.append(f"vcs: {req} failed")
    for f in failures:
        log(f"    WARN {f}")
    return {}, "partial" if failures else "done"


def fetch_js(item, ctx):
    dest = os.path.join(ctx.out, "js", item["dest"])
    return {os.path.relpath(dest, ctx.out): download(item["url"], dest)}, "done"


def this_tool_platform():
    sysname = platform.system().lower()
    arch = {"x86_64": "amd64", "amd64": "amd64", "arm64": "arm64", "aarch64": "arm64"}[platform.machine().lower()]
    return f"{sysname}-{arch}"


def fetch_tool(item, ctx):
    rel = get_json(f"https://api.github.com/repos/{item['repo']}/releases/tags/{item['tag']}")
    files = {}
    for key, pattern in item["assets"].items():
        asset = next((a for a in rel["assets"] if pattern in a["name"]), None)
        if not asset:
            log(f"    no asset matching {pattern}")
            continue
        d = os.path.join(ctx.out, "tools", "pmtiles", key)
        arch = os.path.join(d, asset["name"])
        digest = (asset.get("digest") or "").split("sha256:")[-1] or None
        files[os.path.relpath(arch, ctx.out)] = download(asset["browser_download_url"], arch, asset["size"], sha256=digest)
        if arch.endswith(".zip"):
            with zipfile.ZipFile(arch) as z:
                z.extract("pmtiles", d)
        else:
            with tarfile.open(arch) as t:
                try:
                    t.extract("pmtiles", d, filter="data")
                except TypeError:
                    t.extract("pmtiles", d)
        os.chmod(os.path.join(d, "pmtiles"), 0o755)
    return files, "done"


def pmtiles_bin(ctx):
    local = os.path.join(ctx.out, "tools", "pmtiles", this_tool_platform(), "pmtiles")
    return local if os.path.exists(local) else shutil.which("pmtiles")


def protomaps_build(item, ctx):
    if ctx.build_date:
        return item["source_url"].format(date=ctx.build_date)
    day = datetime.date.today()
    for _ in range(PROTOMAPS_LOOKBACK_DAYS):
        url = item["source_url"].format(date=day.strftime("%Y%m%d"))
        if head_size(url):
            return url
        day -= datetime.timedelta(days=1)
    raise FetchError("no Protomaps daily build found in the last days; pass --build-date YYYYMMDD")


def tiles_args(item, ctx):
    return [f"--bbox={ctx.bbox or item['bbox']}", f"--maxzoom={ctx.maxzoom if ctx.maxzoom is not None else item['maxzoom']}"]


def fetch_tiles(item, ctx):
    pm = pmtiles_bin(ctx)
    if not pm:
        raise FetchError("pmtiles CLI not found: run the tool:pmtiles item first (or --types tool)")
    dest = os.path.join(ctx.out, "tiles", item["dest"])
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    src = protomaps_build(item, ctx)
    run([pm, "extract", src, dest + ".part.pmtiles"] + tiles_args(item, ctx))
    os.replace(dest + ".part.pmtiles", dest)
    run([pm, "show", dest], capture=True)
    with open(dest + ".source.txt", "w") as f:
        f.write(f"{src} {' '.join(tiles_args(item, ctx))}\n")
    return {os.path.relpath(dest, ctx.out): file_hash(dest)}, "done"


def fetch_script(item, ctx):
    run(["sh", os.path.join(ctx.repo, item["path"])])
    log(f"    output stays in the repo checkout: {item['outputs']}")
    return {}, "done"


FETCHERS = dict(dataset=fetch_dataset, script=fetch_script, pip=fetch_pip, docker=fetch_docker,
                git=fetch_git, js=fetch_js, tool=fetch_tool, tiles=fetch_tiles)
FETCHERS["docker-build"] = fetch_docker_build


# ---------------------------------------------------------------- probe (dry run)

def probe_size(item, ctx):
    t = item["type"]
    try:
        if t == "dataset":
            total, unknown = 0, False
            for spec in item["files"]:
                if spec["method"] in ("manual",):
                    total += spec.get("size") or 0
                    unknown |= spec.get("size") is None
                    continue
                if spec["method"] == "git":
                    s = github_repo_size(spec["url"])
                    total += s or 0
                    unknown |= s is None
                    continue
                if spec["method"] in ("http", "gdrive") and spec.get("size") is not None:
                    total += spec["size"]
                    continue
                for url, _, size, _, _ in resolve_files(spec):
                    size = size if size is not None else head_size(url)
                    total += size or 0
                    unknown |= size is None
            return total, not unknown
        if t == "git":
            s = github_repo_size(item["url"])
            return s, s is not None
        if t == "js":
            s = head_size(item["url"])
            return s, s is not None
        if t == "tool":
            rel = get_json(f"https://api.github.com/repos/{item['repo']}/releases/tags/{item['tag']}")
            sizes = [a["size"] for a in rel["assets"] if any(p in a["name"] for p in item["assets"].values())]
            return sum(sizes), True
        if t == "tiles":
            pm = pmtiles_bin(ctx)
            if not pm:
                return None, False
            src = protomaps_build(item, ctx)
            p = run([pm, "extract", src, os.path.join(tempfile.gettempdir(), "probe.pmtiles"), "--dry-run"] + tiles_args(item, ctx),
                    check=False, capture=True)
            text = (p.stdout or "") + (p.stderr or "")
            m = re.search(r"archive size of\s+([\d.]+)\s*([KMGT]?B)", text, re.I)
            if m:
                mult = {"B": 1, "KB": 10**3, "MB": 10**6, "GB": 10**9, "TB": 10**12}[m.group(2).upper()]
                return int(float(m.group(1)) * mult), True
            log("    pmtiles dry-run output not parsed:\n" + text[-400:])
    except (FetchError, urllib.error.HTTPError, KeyError) as e:
        log(f"    probe failed for {item['id']}: {e}")
    return item.get("size"), item.get("size_complete", False)


def github_repo_size(url):
    m = re.match(r"https://github.com/([^/]+/[^/]+?)(?:\.git)?/?$", url)
    if not m:
        return None
    try:
        return get_json(f"https://api.github.com/repos/{m.group(1)}")["size"] * 1024
    except (FetchError, KeyError):
        return None


# ---------------------------------------------------------------- selection, state, reports

def select(manifest, profile, types, patterns):
    limit = manifest["tiers"].index(profile)
    out = []
    for it in manifest["items"]:
        if manifest["tiers"].index(it["tier"]) > limit:
            continue
        if types and it["type"] not in types:
            continue
        if patterns and not any(fnmatch.fnmatch(it["id"], p) for p in patterns):
            continue
        out.append(it)
    return out


def load_state(out):
    path = os.path.join(out, ".prep-state.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def save_state(out, state):
    path = os.path.join(out, ".prep-state.json")
    with open(path + ".tmp", "w") as f:
        json.dump(state, f, indent=1)
    os.replace(path + ".tmp", path)


def write_reports(out, manifest, state):
    sums = []
    for root, dirs, names in os.walk(out):
        dirs[:] = [d for d in dirs if d != "mirrors"]
        for n in sorted(names):
            p = os.path.join(root, n)
            rel = os.path.relpath(p, out)
            if n.endswith(".part") or ".part." in n or rel in (".prep-state.json", "SHA256SUMS", "LICENSES.txt"):
                continue
            known = next((st["files"][rel] for st in state.values() if st.get("files", {}).get(rel)), None)
            sums.append(f"{known or file_hash(p)}  {rel}")
    with open(os.path.join(out, "SHA256SUMS"), "w") as f:
        f.write("\n".join(sorted(sums, key=lambda s: s.split("  ", 1)[1])) + "\n")
    by_id = {it["id"]: it for it in manifest["items"]}
    with open(os.path.join(out, "LICENSES.txt"), "w") as f:
        for iid in sorted(state):
            it = by_id.get(iid, {})
            f.write(f"{iid}\t{state[iid]['status']}\t{it.get('license', '?')}\t{it.get('source', '')}\n")


def dry_run(items, ctx):
    totals, unknown = {}, {}
    log(f"{'tier':9} {'type':12} {'size':>11}  id  [license]")
    for it in items:
        size, complete = (probe_size(it, ctx) if ctx.probe else (it.get("size"), it.get("size_complete", False)))
        mark = "" if complete else ("+?" if size else "")
        log(f"{it['tier']:9} {it['type']:12} {human(size) + mark:>11}  {it['id']}  [{it['license']}]")
        if it.get("note"):
            log(f"{'':35}note: {it['note']}")
        totals[it["type"]] = totals.get(it["type"], 0) + (size or 0)
        if not complete:
            unknown[it["type"]] = unknown.get(it["type"], 0) + 1
    log("\nTotals (known sizes only; '+?' = partly unknown):")
    for t in TYPES:
        if t in totals:
            log(f"  {t:12} {human(totals[t]):>11}   {unknown.get(t, 0)} item(s) with unknown or partial size")
    log(f"  {'ALL':12} {human(sum(totals.values())):>11}   {sum(unknown.values())} item(s) with unknown or partial size, {len(items)} items")


def verify(out, patterns=None):
    path = os.path.join(out, "SHA256SUMS")
    if not os.path.exists(path):
        sys.exit("no SHA256SUMS in " + out)
    bad = 0
    for line in open(path):
        digest, rel = line.rstrip("\n").split("  ", 1)
        if patterns and not any(fnmatch.fnmatch(rel, p) for p in patterns):
            continue
        p = os.path.join(out, rel)
        if not os.path.exists(p):
            log(f"MISSING {rel}")
            bad += 1
        elif file_hash(p) != digest:
            log(f"BAD     {rel}")
            bad += 1
    log(f"verify: {bad} problem(s)")
    return bad == 0


# ---------------------------------------------------------------- sharing

class RangeHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler plus single-range GET, so wget -c / PMTiles readers work."""

    def send_head(self):
        rng = self.headers.get("Range")
        path = self.translate_path(self.path)
        if not rng or os.path.isdir(path) or not os.path.exists(path):
            return super().send_head()
        m = re.match(r"bytes=(\d*)-(\d*)$", rng)
        size = os.path.getsize(path)
        if not m:
            return super().send_head()
        start = int(m.group(1)) if m.group(1) else max(0, size - int(m.group(2)))
        end = int(m.group(2)) if m.group(1) and m.group(2) else size - 1
        if start >= size:
            self.send_error(416)
            return None
        end = min(end, size - 1)
        f = open(path, "rb")
        f.seek(start)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        self._remaining = end - start + 1
        return f

    def copyfile(self, source, outputfile):
        remaining = getattr(self, "_remaining", None)
        if remaining is None:
            return super().copyfile(source, outputfile)
        while remaining > 0:
            block = source.read(min(CHUNK, remaining))
            if not block:
                break
            outputfile.write(block)
            remaining -= len(block)
        self._remaining = None


def serve(out, port, bind):
    os.chdir(out)
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer((bind, port), RangeHandler) as httpd:
        log(f"serving {out} on port {port}; teammates run: prep.py --pull-from http://<your-ip>:{port} --out DIR")
        httpd.serve_forever()


def pull_from(base, out, patterns):
    base = base.rstrip("/")
    os.makedirs(out, exist_ok=True)
    lines = get_text(base + "/SHA256SUMS").splitlines()
    for extra in ("SHA256SUMS", "LICENSES.txt"):
        download(base + "/" + extra, os.path.join(out, extra))
    bad = 0
    for line in lines:
        digest, rel = line.split("  ", 1)
        if patterns and not any(fnmatch.fnmatch(rel, p) for p in patterns):
            continue
        log(f"  {rel}")
        try:
            download(base + "/" + urllib.parse.quote(rel), os.path.join(out, rel), sha256=digest)
        except FetchError as e:
            log(f"    FAILED {e}")
            bad += 1
    log(f"pull: {bad} failure(s)")


# ---------------------------------------------------------------- main

class Ctx:
    pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", default=os.path.join(KIT, "manifest.json"))
    ap.add_argument("--out", default=os.path.join(os.getcwd(), "navkit-cache"))
    ap.add_argument("--repo", default=REPO, help="navigation-index checkout (for docker builds and sample scripts)")
    ap.add_argument("--profile", choices=("minimal", "standard", "full"), default="standard")
    ap.add_argument("--types", help="comma list of: " + ",".join(TYPES))
    ap.add_argument("--items", action="append", help="fnmatch pattern on item id, repeatable")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--probe", action="store_true", help="with --dry-run: query hosts for unknown sizes")
    ap.add_argument("--force", action="store_true", help="refetch items already marked done")
    ap.add_argument("--keep-mirrors", action="store_true", help="keep git --mirror dirs for fast incremental updates")
    ap.add_argument("--pip", default=None, help="pip command, default: current python -m pip")
    ap.add_argument("--pip-platforms", help="comma list of manifest pip_platforms keys")
    ap.add_argument("--python-version", default=None)
    ap.add_argument("--docker-platforms", help="comma list, e.g. linux/amd64")
    ap.add_argument("--bbox", help="min_lon,min_lat,max_lon,max_lat for the basemap extract")
    ap.add_argument("--maxzoom", type=int)
    ap.add_argument("--build-date", help="Protomaps daily build YYYYMMDD (default: newest found)")
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--serve", type=int, metavar="PORT")
    ap.add_argument("--bind", default="0.0.0.0", help="address for --serve")
    ap.add_argument("--pull-from", metavar="URL")
    a = ap.parse_args(argv)

    out = os.path.abspath(a.out)
    if a.serve:
        return serve(out, a.serve, a.bind)
    if a.pull_from:
        return pull_from(a.pull_from, out, a.items)
    if a.verify:
        return 0 if verify(out, a.items) else 1

    with open(a.manifest) as f:
        manifest = json.load(f)
    ctx = Ctx()
    ctx.manifest, ctx.out, ctx.repo, ctx.probe = manifest, out, os.path.abspath(a.repo), a.probe
    ctx.keep_mirrors = a.keep_mirrors
    ctx.pip = a.pip.split() if a.pip else [sys.executable, "-m", "pip"]
    ctx.pip_platforms = a.pip_platforms.split(",") if a.pip_platforms else None
    ctx.python_version = a.python_version or manifest["python_version"]
    ctx.docker_platforms = a.docker_platforms.split(",") if a.docker_platforms else None
    ctx.bbox, ctx.maxzoom, ctx.build_date = a.bbox, a.maxzoom, a.build_date
    types = set(a.types.split(",")) if a.types else None
    items = select(manifest, a.profile, types, a.items)
    if a.dry_run:
        log(f"profile={a.profile} items={len(items)} out={out}\n")
        return dry_run(items, ctx)

    os.makedirs(out, exist_ok=True)
    state = load_state(out)
    failed = []
    for it in items:
        st = state.get(it["id"], {})
        if st.get("status") == "done" and not a.force:
            log(f"skip {it['id']} (done {st.get('at', '')})")
            continue
        log(f"\n== {it['id']}  [{it['type']}, {it['tier']}]\n   license: {it['license']}\n   source:  {it.get('source', '')}")
        if it.get("note"):
            log(f"   note:    {it['note']}")
        try:
            files, status = FETCHERS[it["type"]](it, ctx)
        except (FetchError, OSError, urllib.error.HTTPError) as e:
            log(f"   FAILED: {e}")
            failed.append(it["id"])
            state[it["id"]] = dict(status="failed", error=str(e)[:500], at=datetime.datetime.now().isoformat(timespec="seconds"))
            save_state(out, state)
            continue
        state[it["id"]] = dict(status=status, files=files, at=datetime.datetime.now().isoformat(timespec="seconds"))
        save_state(out, state)
        log(f"   {status}")
    write_reports(out, manifest, state)
    log(f"\n{len(items) - len(failed)}/{len(items)} items ok; failed: {failed or 'none'}")
    log(f"wrote {os.path.join(out, 'SHA256SUMS')} and LICENSES.txt")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
