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
import math
import re
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---- ranker: BM25F + concept boost + priors. site/app.js mirrors this; keep them in sync
# (python3 tools/search_eval.py --parity checks it).
FIELDS = ("name", "tags", "concepts", "summary", "why", "notes", "takeaways", "lang", "kind", "deep")
FIELD_W = {"name": 4.0, "tags": 1.5, "concepts": 1.5, "summary": 1.5, "why": 0.7, "notes": 0.5,
           "takeaways": 0.7, "lang": 1.0, "kind": 1.0, "deep": 1.0}
FIELD_B = {"name": 0.3, "tags": 0.3, "concepts": 0.0, "summary": 0.6, "why": 0.6, "notes": 0.6,
           "takeaways": 0.6, "lang": 0.0, "kind": 0.0, "deep": 0.75}
K1 = 1.2
CONCEPT_MIN = 0.5  # idf-weighted share of the query a concept name must cover to boost its members
CONCEPT_W = 2.5
PRIOR_FIT = {"high": 0.4, "medium": 0.15}
PRIOR_RAN = 0.4  # samples verified by running
DEEP_DOC_CHARS = 1500  # same cut as build.SITE_DOC_BODY, so the web UI indexes the same text
DEEP_DOC_MAX_ABOUT = 4  # hub docs attached to more nodes than this are too generic to index per node
DEEP_DIRS = ("docs/integration-cards/", "docs/dataset-cards/", "docs/paper-digests/", "docs/landscape/")
STOP = frozenset("a an and are as at be by for from in into is it of on or the to with via using none".split())
SYNONYM = {"gps": "gnss", "drone": "uav", "uas": "uav", "suas": "uav", "quadcopter": "uav",
           "quadrotor": "uav", "multirotor": "uav", "ladar": "lidar"}
NORMALIZE = ((re.compile(r"isation"), "ization"),
             (re.compile(r"geo[\s_-]+locali[sz]ation"), "geolocalization"),
             (re.compile(r"geo[\s_-]+locali[sz]e"), "geolocalize"))


def stem(t):
    if len(t) > 4 and t.endswith("ies"):
        t = t[:-3] + "y"
    elif len(t) > 3 and t.endswith("s") and not t.endswith(("ss", "us", "is")):
        t = t[:-1]
    return SYNONYM.get(t, t)


def tokens(text):
    text = text.lower()
    for rx, rep in NORMALIZE:
        text = rx.sub(rep, text)
    return [stem(t) for t in re.split(r"[^a-z0-9]+", text) if t and t not in STOP]


def md_plain(text):  # same as build.md_plain
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[#*`|>]+|\s+", " ", text).strip()


def text_of(r, field):
    v = r.get(field, "")
    return " ".join(v) if isinstance(v, list) else str(v or "")


def verified_ran(v):
    low = (v or "").lower()
    if not low or "placeholder" in low:
        return False
    return bool(re.search(r"\b(ran|run on|built and ran|tests? pass)", low)) and not low.startswith(
        ("not run", "unverified", "sketch"))


class Ranker:
    """entries: dicts with id, fields {field: text}, concepts (ids), prior, stars, ref."""

    def __init__(self, entries, concept_names):
        self.entries = [self._prep(e) for e in entries]
        n = len(self.entries)
        self.avg = {f: (sum(len(e["f"][f]) for e in self.entries) / n) or 1.0 for f in FIELDS}
        df = defaultdict(int)
        for e in self.entries:
            for t in {t for f in FIELDS for t in e["f"][f]}:
                df[t] += 1
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.idf_unseen = math.log(1 + (n + 0.5) / 0.5)
        self.concept_tokens = {cid: set(tokens(name + " " + cid.split(":", 1)[-1]))
                               for cid, name in concept_names.items()}

    @staticmethod
    def _prep(e):
        f = {k: tokens(e["fields"].get(k) or "") for k in FIELDS}
        tf = {k: defaultdict(int) for k in FIELDS}
        for k in FIELDS:
            for t in f[k]:
                tf[k][t] += 1
        return {**e, "f": f, "tf": tf}

    def idf_of(self, t):
        return self.idf.get(t, self.idf_unseen)

    def score(self, e, q, cboost):
        base = 0.0
        for t in q:
            tfw = 0.0
            for f in FIELDS:
                c = e["tf"][f].get(t)
                if c:
                    norm = 1 - FIELD_B[f] + FIELD_B[f] * len(e["f"][f]) / self.avg[f]
                    tfw += FIELD_W[f] * c / norm
            if tfw > 0:
                base += self.idf_of(t) * tfw / (K1 + tfw)
        if base <= 0:
            return 0.0
        best = 0.0
        for c in e["concepts"]:
            best = max(best, cboost.get(c, 0.0))
        return base + CONCEPT_W * best + e["prior"]

    def rank(self, query):
        """[(score, entry)] best first."""
        q = list(dict.fromkeys(tokens(query)))
        if not q:
            return []
        total = sum(self.idf_of(t) for t in q)
        cboost = {}
        for cid, toks in self.concept_tokens.items():
            m = sum(self.idf_of(t) for t in q if t in toks) / total
            if m >= CONCEPT_MIN:
                cboost[cid] = m
        hits = []
        for e in self.entries:
            s = self.score(e, q, cboost)
            if s > 0:
                hits.append((math.floor(s * 1e6 + 0.5), e))
        hits.sort(key=lambda h: (-h[0], -(h[1]["stars"] or 0), h[1]["id"]))
        return [(s / 1e6, e) for s, e in hits]


def deep_text(recs):
    """Plain text per deep-dive doc, skipping hub docs attached to many nodes."""
    users = defaultdict(int)
    for r in recs.values():
        for d in r.get("deep_dives", []):
            users[d] += 1
    out = {}
    for d, c in users.items():
        if c <= DEEP_DOC_MAX_ABOUT and d.startswith(DEEP_DIRS) and (ROOT / d).is_file():
            out[d] = md_plain((ROOT / d).read_text())[:DEEP_DOC_CHARS]
    return out


def record_entry(r, cname, docs):
    concepts = list(r.get("concepts", [])) + ([r["id"]] if r["kind"] == "concept" else [])
    fields = {
        "name": r.get("name") or r.get("title") or r["id"], "tags": text_of(r, "tags"),
        "concepts": " ".join(cname.get(c, "") for c in concepts), "summary": text_of(r, "summary"),
        "why": text_of(r, "why_it_matters"), "notes": text_of(r, "hackathon_notes"),
        "takeaways": text_of(r, "key_takeaways"),
        "lang": (r.get("github") or {}).get("language") or r.get("language") or "", "kind": r["kind"],
        "deep": " ".join(docs[d] for d in r.get("deep_dives", []) if d in docs),
    }
    prior = PRIOR_FIT.get(r.get("hackathon_fit"), 0.0)
    if r["kind"] == "sample" and verified_ran(r.get("verified")):
        prior += PRIOR_RAN
    return {"id": r["id"], "fields": fields, "concepts": concepts, "prior": prior,
            "stars": (r.get("github") or {}).get("stargazers_count"), "ref": r}


_RANKER = []  # [(recs, Ranker)], one slot


def ranker(recs):
    if not _RANKER or _RANKER[0][0] is not recs:
        cname = {r["id"]: r.get("name", "") for r in recs.values() if r["kind"] == "concept"}
        docs = deep_text(recs)
        _RANKER[:] = [(recs, Ranker([record_entry(r, cname, docs) for r in recs.values()], cname))]
    return _RANKER[0][1]


def search(recs, query, filters=None):
    """[(score, record)] best first, filtered after ranking so corpus stats do not depend on filters."""
    return [(s, e["ref"]) for s, e in ranker(recs).rank(query)
            if filters is None or matches_filters(e["ref"], filters)]


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
        res = [r for _, r in search(recs, a.arg or "", a)[: a.limit]]
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
