#!/usr/bin/env python3
"""Fail if any relative markdown link in the repo points at a missing file."""
import os
import re
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)\s]+)\)")
EXTERNAL = re.compile(r"^(https?:|mailto:|#)")
SKIP_PARTS = {".git", "node_modules", ".venv", "venv"}


def exists_exact_case(path):
    """Path.exists() is case-insensitive on macOS; CI runs on Linux, so compare names exactly."""
    if not path.exists():
        return False
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return True
    cur = ROOT
    for part in rel.parts:
        if part not in os.listdir(cur):
            return False
        cur = cur / part
    return True


def main():
    broken, total = [], 0
    for f in ROOT.rglob("*.md"):
        if SKIP_PARTS & set(f.parts):
            continue
        for m in LINK.finditer(f.read_text(errors="replace")):
            target = m.group(1)
            if EXTERNAL.match(target):
                continue
            total += 1
            path = (f.parent / urllib.parse.unquote(target.split("#")[0])).resolve()
            if not exists_exact_case(path):
                broken.append(f"{f.relative_to(ROOT)}: {target}")
    print(f"relative links: {total}, broken: {len(broken)}")
    for b in broken:
        print("  " + b)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
