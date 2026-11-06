#!/usr/bin/env python3
"""Fail when tools/stdlib-sample-tests.txt drifts from the samples that carry tests.

A sample directory with test_*.py at its top level or a tests/ folder must be listed,
or named in EXEMPT with the reason it cannot run under plain python3 in CI. Every
listed directory must exist. Exit 1 on any problem.

Usage: python3 tools/check_sample_tests.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SAMPLES = ROOT / "samples"
LIST_FILE = ROOT / "tools" / "stdlib-sample-tests.txt"

# sample dir name => why its tests are not run by the stdlib CI loop
EXEMPT = {}


def has_tests(d):
    return any(d.glob("test_*.py")) or (d / "tests").is_dir()


def main():
    listed = [ln.strip() for ln in LIST_FILE.read_text().splitlines() if ln.strip()]
    problems = []

    seen = set()
    for name in listed:
        if name in seen:
            problems.append(f"duplicate in {LIST_FILE.name}: {name}")
        seen.add(name)
        if not (SAMPLES / name).is_dir():
            problems.append(f"listed but missing: samples/{name}/")
        if name in EXEMPT:
            problems.append(f"both listed and exempt: {name}")

    for name in sorted(EXEMPT):
        if not (SAMPLES / name).is_dir():
            problems.append(f"exempt but missing: samples/{name}/")

    with_tests = sorted(d.name for d in SAMPLES.iterdir() if d.is_dir() and has_tests(d))
    for name in with_tests:
        if name not in seen and name not in EXEMPT:
            problems.append(f"has tests but not in {LIST_FILE.name} or EXEMPT: samples/{name}/")

    for p in problems:
        print(p)
    print(f"{len(with_tests)} samples with tests, {len(listed)} listed, "
          f"{len(EXEMPT)} exempt, {len(problems)} problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
