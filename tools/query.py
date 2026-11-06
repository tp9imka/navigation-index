#!/usr/bin/env python3
"""Query the navigation index. Stdlib only, reads index/records.jsonl + graph/graph.json.

  query.py search "visual geolocalization satellite"   ranked keyword search
  query.py search lightglue --kind repo --fit high      with filters
  query.py concept concept:magnetic-nav                 everything about a concept
  query.py show repo:px4/px4-autopilot                  full record
  query.py neighbors repo:px4/px4-autopilot --depth 2   graph walk
  query.py concepts                                     list concept ids with counts
Add --json to any command for machine-readable output.
"""
import argparse
import json
import re
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WEIGHTS = {"name": 5, "title": 5, "tags": 3, "summary": 2, "why_it_matters": 1, "hackathon_notes": 1, "key_takeaways": 1}


def load():
    recs = {}
    for line in (ROOT / "index" / "records.jsonl").read_text().splitlines():
        r = json.loads(line)
        recs[r["id"]] = r
    g = json.loads((ROOT / "graph" / "graph.json").read_text())
    adj = defaultdict(list)
    for e in g["edges"]:
        adj[e["source"]].append((e["target"], e["rel"], "out"))
        adj[e["target"]].append((e["source"], e["rel"], "in"))
    return recs, adj


def text_of(r, field):
    v = r.get(field, "")
    return " ".join(v) if isinstance(v, list) else str(v)


def score(r, terms):
    s = 0
    for field, w in WEIGHTS.items():
        t = text_of(r, field).lower()
        s += sum(w * len(re.findall(re.escape(term), t)) for term in terms)
    return s


def matches_filters(r, a):
    if a.kind and r["kind"] != a.kind:
        return False
    if a.fit and r.get("hackathon_fit") != a.fit:
        return False
    if a.domain and a.domain not in r.get("domains", []):
        return False
    if a.concept and a.concept not in r.get("concepts", []):
        return False
    return True


def brief(r):
    stars = (r.get("github") or {}).get("stargazers_count")
    bits = [r["kind"], r["id"], r.get("name") or r.get("title")]
    if stars:
        bits.append(f"★{stars}")
    if r.get("hackathon_fit"):
        bits.append(f"fit:{r['hackathon_fit']}")
    return " | ".join(str(b) for b in bits) + "\n    " + (r.get("summary", "")[:200]) + f"\n    {r.get('url', '')}"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["search", "concept", "show", "neighbors", "concepts"])
    p.add_argument("arg", nargs="?")
    p.add_argument("--kind")
    p.add_argument("--fit", choices=["high", "medium", "low"])
    p.add_argument("--domain")
    p.add_argument("--concept")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--depth", type=int, default=1)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    recs, adj = load()

    if a.cmd == "concepts":
        counts = defaultdict(int)
        for r in recs.values():
            for c in r.get("concepts", []):
                counts[c] += 1
        out = [{"id": c["id"], "name": c["name"], "count": counts[c["id"]]} for c in recs.values() if c["kind"] == "concept"]
        print(json.dumps(out, indent=1) if a.json else "\n".join(f"{o['count']:4d}  {o['id']}  {o['name']}" for o in out))
        return
    if a.cmd == "show":
        print(json.dumps(recs.get(a.arg, {"error": "not found"}), indent=1, ensure_ascii=False))
        return
    if a.cmd == "search":
        terms = [t for t in a.arg.lower().split() if t]
        hits = [(score(r, terms), r) for r in recs.values() if matches_filters(r, a)]
        hits = [h for h in hits if h[0] > 0]
        hits.sort(key=lambda h: (-h[0], -((h[1].get("github") or {}).get("stargazers_count") or 0)))
        res = [r for _, r in hits[: a.limit]]
    elif a.cmd == "concept":
        a.concept = a.arg
        res = [r for r in recs.values() if matches_filters(r, a)]
        res.sort(key=lambda r: ({"high": 0, "medium": 1, "low": 2}.get(r.get("hackathon_fit"), 3), r["kind"]))
        res = res[: a.limit]
    else:  # neighbors
        seen, q, res = {a.arg}, deque([(a.arg, 0)]), []
        while q:
            node, d = q.popleft()
            if d >= a.depth:
                continue
            for nb, rel, direction in adj[node]:
                if nb in seen:
                    continue
                seen.add(nb)
                if nb in recs and matches_filters(recs[nb], a):
                    res.append({**recs[nb], "_via": f"{node} -{rel}-> " if direction == "out" else f"{node} <-{rel}- "})
                q.append((nb, d + 1))
    if a.json:
        print(json.dumps(res, indent=1, ensure_ascii=False))
    else:
        for r in res:
            via = f"  [{r['_via']}]" if r.get("_via") else ""
            print(brief(r) + via)


if __name__ == "__main__":
    main()
