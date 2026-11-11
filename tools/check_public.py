#!/usr/bin/env python3
"""Fail on employer, event, tooling and machine-path wording in tracked, non-generated files.

Rules: the public-release spec, hygiene section. Output one `path:line:term` per hit (line 0 = the
file path itself matches), exit 1 on any hit that the allow-list does not cover.

  python3 tools/check_public.py                 # strict: exit 1 on any hit
  python3 tools/check_public.py --warn          # print the hits, exit 0
  python3 tools/check_public.py --json          # machine-readable hits + counts
  python3 tools/check_public.py --include-generated   # also scan catalog/, INDEX.md, ... (after a rebuild)

Allow-list: tools/public_allowlist.json, a list of entries
  {"path": "...", "term": "<term name or *>", "line": <int, optional>, "text": "<substring, optional>",
   "reason": "<why this is a third-party fact or a placeholder>"}
An entry covers a hit when path and term match and, if given, the line number matches and the line
contains `text`. Entries without a reason are an error. Entries that cover nothing are reported.
Stdlib only.
"""
import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST = ROOT / "tools" / "public_allowlist.json"

# (term name, regex). The name is what an allow-list entry and the output refer to.
TERMS = [
    ("EDGE", re.compile(r"\bEDGE\b")),
    ("EDGE Group", re.compile(r"\bEDGE Group\b", re.I)),
    ("Autonomous Frontiers", re.compile(r"Autonomous Frontiers", re.I)),
    ("Challenge 2", re.compile(r"\bchallenge[ _-]2\b", re.I)),
    ("/Users/", re.compile(r"/Users/")),
    ("/home/<name>/", re.compile(r"/home/[A-Za-z_][A-Za-z0-9._-]*/")),
    ("loop-NN", re.compile(r"\bloop-[0-9]+[a-z]?\b")),
    ("farmout", re.compile(r"farmout", re.I)),
    ("Kiro", re.compile(r"\bKiro\b")),
    ("Codex lane", re.compile(r"\bCodex lanes?\b", re.I)),
    ("Ivan", re.compile(r"\bIvan\b")),
    ("hackathon day", re.compile(r"\bhackathon day\b", re.I)),
    ("on the day", re.compile(r"\bon the day\b", re.I)),
    ("Day 1", re.compile(r"\bday[ _-]?1\b", re.I)),
    ("organiser", re.compile(r"\borgani[sz]ers?\b", re.I)),
    ("judges", re.compile(r"\bjudges\b", re.I)),
]
TERM_NAMES = [n for n, _ in TERMS]

# Generated files are checked after a rebuild (--include-generated), not allow-listed.
GENERATED_PREFIXES = ("catalog/", "graph/", "index/", "reports/", "site/data/")
GENERATED_FILES = {"INDEX.md", "llms.txt", "samples/README.md", "templates/offline-kit/manifest.json",
                   "docs/integration-cards/README.md", "docs/practical-readiness.md"}
# loop/ was the private build log; it now lives outside the tree and is gitignored.
SKIP_PREFIXES = ("loop/",)
MAX_BYTES = 50_000_000  # scan big result JSON too: run logs in them carry paths


def is_generated(path):
    return path in GENERATED_FILES or path.startswith(GENERATED_PREFIXES)


def tracked_files(root):
    # Tracked plus new files that are not git-ignored, so the check also works before a commit.
    out = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                         cwd=root, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8", "replace").split("\0") if p]


def read_text(path):
    """Text of a file, or None for binaries and very large files."""
    try:
        if path.stat().st_size > MAX_BYTES:
            return None
        raw = path.read_bytes()
    except OSError:
        return None
    if b"\0" in raw[:8192]:
        return None
    return raw.decode("utf-8", "replace")


def scan_text(path, text):
    """Hits in the path name (line 0) and in each line. `text` is the whole stripped line."""
    hits = [{"path": path, "line": 0, "term": name, "text": path} for name, rx in TERMS if rx.search(path)]
    present = [(name, rx) for name, rx in TERMS if rx.search(text)]  # skip the line loop for clean files
    if present:
        for i, line in enumerate(text.splitlines(), 1):
            for name, rx in present:
                if rx.search(line):
                    hits.append({"path": path, "line": i, "term": name, "text": line.strip()})
    return hits


def scan(root, files, include_generated=False, skip=()):
    hits = []
    for p in files:
        if p in skip or p.startswith(SKIP_PREFIXES) or (is_generated(p) and not include_generated):
            continue
        text = read_text(Path(root) / p)
        if text is None:
            text = ""  # binary: still check the path name
        hits += scan_text(p, text)
    return hits


def load_allowlist(path):
    if not Path(path).exists():
        return []
    entries = json.loads(Path(path).read_text())
    bad = [e for e in entries if not str(e.get("reason", "")).strip() or not e.get("path") or not e.get("term")]
    if bad:
        raise ValueError(f"allow-list entries need path, term and reason: {bad[:3]}")
    unknown = [e for e in entries if e["term"] != "*" and e["term"] not in TERM_NAMES]
    if unknown:
        raise ValueError(f"allow-list entries with unknown term: {unknown[:3]}")
    return entries


def covers(entry, hit):
    if entry["path"] != hit["path"] or entry["term"] not in ("*", hit["term"]):
        return False
    if "line" in entry and entry["line"] != hit["line"]:
        return False
    return "text" not in entry or entry["text"] in hit["text"]


def apply_allowlist(hits, entries):
    used = [False] * len(entries)
    left = []
    for h in hits:
        idx = next((i for i, e in enumerate(entries) if covers(e, h)), None)
        if idx is None:
            left.append(h)
        else:
            used[idx] = True
    return left, [e for e, u in zip(entries, used) if not u]


def counts(hits):
    return {"by_term": dict(Counter(h["term"] for h in hits).most_common()),
            "by_folder": dict(Counter(h["path"].split("/", 1)[0] if "/" in h["path"] else "(root)"
                                      for h in hits).most_common()),
            "files": len({h["path"] for h in hits}), "total": len(hits)}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Public-release hygiene check (spec section 6).")
    ap.add_argument("--warn", action="store_true", help="print hits but exit 0")
    ap.add_argument("--json", action="store_true", help="print hits and counts as JSON")
    ap.add_argument("--include-generated", action="store_true", help="also scan generated files")
    ap.add_argument("--root", default=str(ROOT), help=argparse.SUPPRESS)
    ap.add_argument("--allowlist", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    root = Path(a.root)
    allow_path = Path(a.allowlist or root / "tools" / "public_allowlist.json").resolve()
    entries = load_allowlist(allow_path)
    # The allow-list quotes the lines it covers, so it is not scanned itself.
    skip = {allow_path.relative_to(root.resolve()).as_posix()} if allow_path.is_relative_to(root.resolve()) else set()
    hits, unused = apply_allowlist(scan(root, tracked_files(root), a.include_generated, skip), entries)
    c = counts(hits)
    if a.json:
        print(json.dumps({"hits": hits, "counts": c, "unused_allowlist": unused}, indent=1))
    else:
        for h in hits:
            print(f"{h['path']}:{h['line']}:{h['term']}")
        for e in unused:
            print(f"allow-list entry covers nothing: {e['path']} {e['term']} {e.get('line', '')}".rstrip(),
                  file=sys.stderr)
        print(f"check_public: {c['total']} hits in {c['files']} files"
              + ("" if not hits else f"; by term {c['by_term']}; by folder {c['by_folder']}"), file=sys.stderr)
    return 0 if a.warn or not hits else 1


if __name__ == "__main__":
    sys.exit(main())
