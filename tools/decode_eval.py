#!/usr/bin/env python3
"""Evaluate `query.py decode` against hand-judged statements (tools/decode_eval.json). Stdlib only.

  decode_eval.py            hit@1 / hit@3 over real statements, nonsense controls rejected, per split;
                            exits 1 below the MIN_* thresholds
  decode_eval.py -v         plus one line per statement
  decode_eval.py --sweep    hit@1 / confident-miss / nonsense for a range of DECODE_FLOOR values (calibration)

A hit counts any acceptable row; a low-confidence answer still counts, a confident wrong first row is
reported separately because that is the case that sends a team the wrong way.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import query  # noqa: E402

EVAL = Path(__file__).resolve().parent / "decode_eval.json"
# Preserve the original 29/29 baseline and require the new independently written breadth cases too.
MIN_HIT1 = 1.0
MIN_HIT3 = 1.0
MIN_NONSENSE = 1.0
SWEEP_FLOORS = (2.0, 3.0, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0)


def check_rows(spec, text):
    rows, _ = query.decoder_rows(text)
    names = {r["row"]: r["name"] for r in rows}
    bad = [f"row {n}: expected '{want}', found '{names.get(int(n))}'" for n, want in spec["row_names"].items()
           if not (names.get(int(n)) or "").startswith(want)]
    for s in spec["statements"]:
        bad += [f"{s['text'][:40]}: row {n} not pinned in row_names" for n in s["rows"] if str(n) not in spec["row_names"]]
    return bad


def run(spec, text):
    out = []
    for s in spec["statements"]:
        got = query.decode(s["text"], query.DECODE_MAX_ROWS, text)
        out.append({**s, "got": [r["row"] for r in got], "low": bool(got and got[0].get("low_confidence")),
                    "scores": [r["score"] for r in got],
                    "contract_failures": (
                        ["returned a row with incompatible platform or sensor placement"]
                        if set(s.get("excluded_rows", [])) & {r["row"] for r in got} else []) + (
                        ["missing honest disclosure of no runnable starter"]
                        if s.get("no_runnable_starter") and (not got or got[0]["start_from"] or
                            "no runnable" not in got[0]["start_from_text"].lower()) else [])})
    return out


def metrics(res):
    real = [r for r in res if r["rows"]]
    junk = [r for r in res if not r["rows"]]
    hit1 = [r for r in real if r["got"][:1] and r["got"][0] in r["rows"]]
    hit3 = [r for r in real if set(r["got"][:3]) & set(r["rows"])]
    wrong = [r for r in real if r["got"] and not r["low"] and r["got"][0] not in r["rows"]]
    rejected = [r for r in junk if not r["got"]]
    return {"n": len(real), "hit1": len(hit1) / max(1, len(real)), "hit3": len(hit3) / max(1, len(real)),
            "confident_miss": len(wrong), "low": sum(r["low"] for r in real),
            "nonsense_n": len(junk), "nonsense": len(rejected) / max(1, len(junk))}


def fmt(name, m):
    return (f"{name:8s} n={m['n']:2d}  hit@1 {m['hit1']:.2f}  hit@3 {m['hit3']:.2f}  low-confidence {m['low']:2d}  "
            f"confident-miss {m['confident_miss']}  nonsense rejected {m['nonsense']:.2f} (n={m['nonsense_n']})")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-v", action="store_true")
    p.add_argument("--sweep", action="store_true")
    a = p.parse_args()
    spec = json.loads(EVAL.read_text())
    text = (query.ROOT / query.DECODER_DOC).read_text()
    bad = check_rows(spec, text)
    if bad:
        print("decode_eval.json no longer matches the decoder (renumbered rows?):\n  " + "\n  ".join(bad))
        return 1
    if a.sweep:
        real = [r for r in run(spec, text) if r["rows"] and r["got"]]
        right = sorted(r["scores"][0] for r in real if r["got"][0] in r["rows"])
        wrong = sorted(r["scores"][0] for r in real if r["got"][0] not in r["rows"])
        print(f"best-row score when right: {right}\nbest-row score when wrong: {wrong}")
        keep = query.DECODE_FLOOR
        for f in SWEEP_FLOORS:
            query.DECODE_FLOOR = f
            print(f"floor {f:4.1f}  " + fmt("all", metrics(run(spec, text))))
        query.DECODE_FLOOR = keep
        return 0
    res = run(spec, text)
    if a.v:
        for r in res:
            ok = (not r["got"]) if not r["rows"] else bool(r["got"][:1] and r["got"][0] in r["rows"])
            print(f"{'ok ' if ok else 'MISS'} {r['split'][:5]:5s} want {r['rows']!s:9s} got {r['got']!s:13s} "
                  f"{'low ' if r['low'] else '    '}{r['scores']!s:24s} {r['text'][:70]}")
    for split in dict.fromkeys(r["split"] for r in res):
        print(fmt(split, metrics([r for r in res if r["split"] == split])))
    m = metrics(res)
    print(fmt("all", m))
    fails = [f"{k} {m[k]:.2f} < {lim}" for k, lim in (("hit1", MIN_HIT1), ("hit3", MIN_HIT3),
                                                       ("nonsense", MIN_NONSENSE)) if m[k] < lim]
    fails += [f"{r['text'][:65]}: {problem}" for r in res for problem in r["contract_failures"]]
    if fails:
        print("FAIL: " + "; ".join(fails))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
