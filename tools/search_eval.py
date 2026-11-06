#!/usr/bin/env python3
"""Evaluate search ranking against hand-judged queries (tools/search_queries.json). Stdlib only.

  search_eval.py                 MRR / nDCG@10 / recall@10 for the legacy and current rankers, train vs holdout
  search_eval.py -v              plus per-query rows
  search_eval.py --parity        compare top-10 of tools/query.py with site/app.js (needs node + site/data/index.json)
"""
import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import query  # noqa: E402

ROOT = query.ROOT
K = 10
LEGACY_WEIGHTS = {"name": 5, "title": 5, "tags": 3, "summary": 2, "why_it_matters": 1, "hackathon_notes": 1,
                  "key_takeaways": 1}


def legacy_rank(recs, q):
    """The pre-BM25 ranker: weighted substring counts, ties by stars."""
    terms = [t for t in q.lower().split() if t]
    hits = []
    for r in recs.values():
        s = sum(w * len(re.findall(re.escape(t), query.text_of(r, f).lower()))
                for f, w in LEGACY_WEIGHTS.items() for t in terms)
        if s > 0:
            hits.append((s, r))
    hits.sort(key=lambda h: (-h[0], -((h[1].get("github") or {}).get("stargazers_count") or 0)))
    return [r["id"] for _, r in hits]


def current_rank(recs, q):
    return [r["id"] for _, r in query.search(recs, q)]


def metrics(ranked, relevant):
    rel = set(relevant)
    top = ranked[:K]
    rr = next((1 / (i + 1) for i, x in enumerate(ranked) if x in rel), 0.0)
    dcg = sum(1 / math.log2(i + 2) for i, x in enumerate(top) if x in rel)
    idcg = sum(1 / math.log2(i + 2) for i in range(min(len(rel), K)))
    return {"mrr": rr, "ndcg": dcg / idcg, "recall": len(rel & set(top)) / min(len(rel), K)}


def evaluate(recs, queries, rank, verbose=False, label=""):
    by_split = {}
    for item in queries:
        ranked = rank(recs, item["q"])
        m = metrics(ranked, item["relevant"])
        by_split.setdefault(item["split"], []).append(m)
        by_split.setdefault("all", []).append(m)
        if verbose:
            first = next((i + 1 for i, x in enumerate(ranked) if x in set(item["relevant"])), None)
            print(f"  {label:8} {item['split']:7} {item['q'][:34]:34} rr={m['mrr']:.2f} ndcg={m['ndcg']:.2f} "
                  f"rec={m['recall']:.2f} first_rel@{first} top1={ranked[0] if ranked else '-'}")
    return {s: {k: sum(m[k] for m in ms) / len(ms) for k in ("mrr", "ndcg", "recall")} | {"n": len(ms)}
            for s, ms in by_split.items()}


NODE_HARNESS = r"""
const fs = require("fs"), vm = require("vm");
const [appPath, dataPath, queriesPath] = process.argv.slice(2);
const src = fs.readFileSync(appPath, "utf8");
const a = src.indexOf("// ---- ranker begin"), b = src.indexOf("// ---- ranker end");
if (a < 0 || b < 0) throw new Error("ranker markers not found in app.js");
const ctx = {};
vm.createContext(ctx);
vm.runInContext(src.slice(a, b) + "\nthis.buildRanker = buildRanker;", ctx);
const data = JSON.parse(fs.readFileSync(dataPath, "utf8"));
const E = data.nodes.concat(data.docs);
const rk = ctx.buildRanker(E);
const out = {};
for (const q of JSON.parse(fs.readFileSync(queriesPath, "utf8")))
  out[q] = rk.rank(q).filter(([s, e]) => !e.i.startsWith("doc:")).slice(0, 10).map(([s, e]) => [e.i, s]);
process.stdout.write(JSON.stringify(out));
"""


def parity(recs, queries):
    node = shutil.which("node")
    if not node:
        print("parity: node not found, skipped")
        return 2
    data = ROOT / "site" / "data" / "index.json"
    with tempfile.TemporaryDirectory() as td:
        h, qf = Path(td) / "harness.js", Path(td) / "q.json"
        h.write_text(NODE_HARNESS)
        qf.write_text(json.dumps([x["q"] for x in queries]))
        js = json.loads(subprocess.run([node, str(h), str(ROOT / "site" / "app.js"), str(data), str(qf)],
                                       check=True, capture_output=True, text=True).stdout)
    bad = 0
    for item in queries:
        py = [(r["id"], s) for s, r in query.search(recs, item["q"])[:K]]
        jj = [tuple(x) for x in js[item["q"]]]
        same_ids = [i for i, _ in py] == [i for i, _ in jj]
        max_diff = max((abs(a[1] - b[1]) for a, b in zip(py, jj)), default=0.0)
        if not same_ids or max_diff > 1e-6:
            bad += 1
            print(f"MISMATCH {item['q']!r}\n  py: {py}\n  js: {jj}")
    print(f"parity: {len(queries) - bad}/{len(queries)} queries have identical top-{K} ids and scores")
    return 1 if bad else 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-v", "--verbose", action="store_true")
    p.add_argument("--parity", action="store_true")
    a = p.parse_args()
    recs, _ = query.load()
    queries = json.loads((ROOT / "tools" / "search_queries.json").read_text())["queries"]
    missing = [(x["q"], r) for x in queries for r in x["relevant"] if r not in recs]
    for q, r in missing:
        print(f"warning: judged id not in index: {q!r} {r}")
    if a.parity:
        sys.exit(parity(recs, queries))
    print(f"{'ranker':8} {'split':8} {'n':>3} {'MRR':>6} {'nDCG@10':>8} {'R@10':>6}")
    for label, fn in (("legacy", legacy_rank), ("bm25f", current_rank)):
        res = evaluate(recs, queries, fn, a.verbose, label)
        for split in ("train", "holdout", "all"):
            m = res[split]
            print(f"{label:8} {split:8} {m['n']:3d} {m['mrr']:6.3f} {m['ndcg']:8.3f} {m['recall']:6.3f}")


if __name__ == "__main__":
    main()
