#!/usr/bin/env python3
"""Fetch GitHub metadata for every indexed repo via `gh api` into data/github_meta.json.

Incremental: repos already in the cache are skipped unless --refresh is passed.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = ROOT / "data" / "github_meta.json"
WORKERS = 8
FIELDS = (
    "{full_name, description, stargazers_count, forks_count, archived, pushed_at, "
    "language, license: .license.spdx_id, topics, html_url}"
)


def repo_ids():
    ids = set()
    for f in sorted((ROOT / "data" / "repos").glob("*.json")):
        for r in json.loads(f.read_text()):
            ids.add(r["id"])
    return sorted(i for i in ids if i.count("/") == 1)  # GitHub only


def fetch(rid):
    slug = rid.removeprefix("repo:")
    p = subprocess.run(["gh", "api", f"repos/{slug}", "--jq", FIELDS], capture_output=True, text=True)
    if p.returncode != 0:
        return rid, {"error": p.stderr.strip()[:200]}
    return rid, json.loads(p.stdout)


def main():
    refresh = "--refresh" in sys.argv
    cache = json.loads(META.read_text()) if META.exists() else {}
    todo = [i for i in repo_ids() if refresh or i not in cache or "error" in cache[i]]
    with ThreadPoolExecutor(WORKERS) as ex:
        for rid, meta in ex.map(fetch, todo):
            meta["fetched"] = date.today().isoformat()
            cache[rid] = meta
    META.write_text(json.dumps(dict(sorted(cache.items())), indent=1, ensure_ascii=False) + "\n")
    errors = [k for k, v in cache.items() if "error" in v]
    print(f"fetched {len(todo)}, cached {len(cache)}, errors {len(errors)}")
    for e in errors:
        print("  ERR", e, cache[e]["error"])


if __name__ == "__main__":
    main()
