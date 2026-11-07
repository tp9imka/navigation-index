#!/usr/bin/env python3
"""Query the navigation index. Stdlib only, reads index/records.jsonl + graph/graph.json.

  query.py search "visual geolocalization satellite"   ranked keyword search
  query.py search lightglue --kind repo --fit high      with filters
  query.py concept concept:magnetic-nav                 everything about a concept
  query.py search "usv spoofing harbor"               guides (kind guide), samples and repos rank together
  query.py decode "Navigate a quadcopter 10 km without GPS"  top 1-3 decoder rows for a pasted statement
For a problem statement, run decode (or read docs/problem-statement-decoder.md) first and search with each
matching row's keywords. Pasting the whole statement works less well: long queries up-weight platform words
(DOMAIN_WORDS) but generic GNSS terms still pull in broad records.
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
import readiness

ROOT = Path(__file__).resolve().parent.parent

# ---- ranker: BM25F + concept boost + priors. site/app.js mirrors this; keep them in sync
# (python3 tools/search_eval.py --parity checks it).
FIELDS = ("name", "tags", "concepts", "summary", "why", "notes", "takeaways", "lang", "kind", "deep")
FIELD_W = {"name": 4.0, "tags": 1.5, "concepts": 1.5, "summary": 1.5, "why": 0.7, "notes": 0.5,
           "takeaways": 0.7, "lang": 1.0, "kind": 1.0, "deep": 1.0}
FIELD_B = {"name": 0.3, "tags": 0.5, "concepts": 0.0, "summary": 0.8, "why": 0.6, "notes": 0.6,
           "takeaways": 0.6, "lang": 0.0, "kind": 0.0, "deep": 0.75}
K1 = 1.2
CONCEPT_MIN = 0.5  # idf-weighted share of the query a concept name must cover to boost its members
CONCEPT_W = 2.5
PRIOR_FIT = {"high": 0.4, "medium": 0.15}
PRIOR_RAN = 0.4  # samples verified by running
DEEP_DOC_CHARS = 1500  # same cut as build.SITE_DOC_BODY, so the web UI indexes the same text
DEEP_DOC_MAX_ABOUT = 4  # hub docs attached to more nodes than this are too generic to index per node
DEEP_DIRS = ("docs/integration-cards/", "docs/dataset-cards/", "docs/paper-digests/", "docs/landscape/")
GUIDE_BODY_CHARS = 6000  # same as build.GUIDE_BODY_CHARS: a guide's own text is its deep field
STOP = frozenset(("a an and are as at be by for from in into is it of on or the to with via using none "
                  "all any but can do does have has how if its not our should so than that their them then there they this we what when where which who will you your").split())
SYNONYM = {"gps": "gnss", "drone": "uav", "uas": "uav", "suas": "uav", "quadcopter": "uav",
           "quadrotor": "uav", "multirotor": "uav", "ladar": "lidar", "harbour": "harbor",
           "defence": "defense", "ship": "vessel", "boat": "vessel"}
NORMALIZE = ((re.compile(r"isation"), "ization"),
             (re.compile(r"fixed[\s_-]+wing"), "fixedwing"),
             (re.compile(r"geo[\s_-]+locali[sz]ation"), "geolocalization"),
             (re.compile(r"geo[\s_-]+locali[sz]e"), "geolocalize"),
             (re.compile(r"night[\s_-]*time"), "night"))
# Platform, environment and timing words decide which samples apply to a statement; in a long query
# they are drowned by generic GNSS / spoofing terms that every record shares.
DOMAIN_WORDS = ("uav fixedwing usv ugv uuv auv vessel maritime harbor underwater subsea indoor underground "
                "tunnel subterranean dismounted pedestrian soldier night timing clock")
DOMAIN_W = 2.0
LONG_QUERY_TERMS = 6  # distinct query tokens from which a query is treated as a statement
# Whole words the suffix rules get wrong: domain acronyms they would merge with English words
# (COTS/CoT, CORS/core, TAK/take, SAM/same), "stated" vs "state", aircraft "plane" vs "planning".
# Agent nouns stay apart on purpose: folding jammer => jam measured worse (jammer localization is
# not jamming detection).
STEM_EXCEPT = {"cots": "cots", "cors": "cors", "take": "take", "takes": "take", "taking": "take",
               "same": "same", "stated": "stated", "plane": "plane", "planes": "plane", "denial": "deny"}


def stem(t):
    if t in STEM_EXCEPT:
        return STEM_EXCEPT[t]
    if len(t) > 4 and t.endswith(("ies", "ied")):
        t = t[:-3] + "y"
    elif len(t) > 3 and t.endswith("s") and not t.endswith(("ss", "us", "is")):
        t = t[:-1]
    if t in SYNONYM:
        return SYNONYM[t]
    # light -ing / -ed / -e folding so "spoofed", "spoofing" and "spoof" meet
    cut = False
    if len(t) > 5 and t.endswith("ing"):
        t, cut = t[:-3], True
    elif len(t) > 4 and t.endswith("ed") and not t.endswith("eed"):
        t, cut = t[:-2], True
    if cut and len(t) > 3 and t[-1] == t[-2] and t[-1] not in "lsz":
        t = t[:-1]
    elif len(t) > 3 and t.endswith("e"):
        t = t[:-1]
    return SYNONYM.get(t, t)


DOMAIN_TERMS = frozenset(stem(w) for w in DOMAIN_WORDS.split())


def words(text):
    text = text.lower()
    for rx, rep in NORMALIZE:
        text = rx.sub(rep, text)
    return [t for t in re.split(r"[^a-z0-9]+", text) if t and t not in STOP]


def tokens(text):
    return [stem(t) for t in words(text)]


def query_terms(query):
    """[(token, weight)]: distinct tokens; in a long query, domain terms weigh DOMAIN_W."""
    q = list(dict.fromkeys(tokens(query)))
    long = len(q) >= LONG_QUERY_TERMS
    return [(t, DOMAIN_W if long and t in DOMAIN_TERMS else 1.0) for t in q]


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


def sample_ran(r):
    """Same rule as build.sample_status == "ran": the explicit verified_status wins over the text."""
    if r.get("verified_status"):
        return r["verified_status"] == "ran"
    return verified_ran(r.get("verified"))


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
        for t, qw in q:
            tfw = 0.0
            for f in FIELDS:
                c = e["tf"][f].get(t)
                if c:
                    norm = 1 - FIELD_B[f] + FIELD_B[f] * len(e["f"][f]) / self.avg[f]
                    tfw += FIELD_W[f] * c / norm
            if tfw > 0:
                base += qw * self.idf_of(t) * tfw / (K1 + tfw)
        if base <= 0:
            return 0.0
        best = 0.0
        for c in e["concepts"]:
            best = max(best, cboost.get(c, 0.0))
        return base + CONCEPT_W * best + e["prior"]

    def rank(self, query):
        """[(score, entry)] best first."""
        q = query_terms(query)
        if not q:
            return []
        total = sum(qw * self.idf_of(t) for t, qw in q)
        cboost = {}
        for cid, toks in self.concept_tokens.items():
            m = sum(qw * self.idf_of(t) for t, qw in q if t in toks) / total
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
    if r["kind"] == "guide" and (ROOT / r["path"]).is_file():
        fields["deep"] = md_plain((ROOT / r["path"]).read_text())[:GUIDE_BODY_CHARS]
    prior = PRIOR_FIT.get(r.get("hackathon_fit"), 0.0)
    if r["kind"] == "sample" and sample_ran(r):
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
    if not query.strip():
        return [(0.0, r) for r in recs.values() if filters is None or matches_filters(r, filters)]
    return [(s, e["ref"]) for s, e in ranker(recs).rank(query)
            if filters is None or matches_filters(e["ref"], filters)]


# ---- problem-statement decoder: rows and wording triggers parsed from the doc at call time
DECODER_DOC = "docs/problem-statement-decoder.md"
DECODE_MAX_ROWS = 3
DECODE_TRIGGER_W = 2.0   # per matched trigger group, times the row's position decay in the Rows cell
DECODE_TRIGGER_DECAY = 0.5
DECODE_PHRASE_W = 1.0    # extra share per additional word of a multi-word trigger: "ground robot" beats "underground"
# idf of statement tokens found in each row column; the problem statement is the row's own wording
DECODE_FIELD_W = {"name": 1.5, "approach": 0.3, "pitch": 0.3, "risk": 0.15, "datasets": 0.15}
DECODE_KEEP = 0.35       # rows after the first are kept when they score at least this share of the best
DECODE_PLATFORM_CONFLICT = 0.2  # a named platform outweighs generic GNSS / distance cues for another platform
# Without a matching wording trigger, require overlap with a meaningful share of the brief.
# This rejects incidental phone/map words without a closed list of permitted navigation verbs.
DECODE_MIN_COVERAGE = 0.4
# Platforms (from the doc), sensors and environments support ranking, but do not by
# themselves establish a task in fallback matches. Other shared task wording stays open.
DECODE_CONTEXT = frozenset(stem(w) for w in (
    "camera imu inertial sensor visual lidar radar gnss stereo monocular depth "
    "indoor outdoor building floor corridor street urban forest warehouse tunnel underground "
    "night thermal smoke weather map offline").split())
# Calibrated on tools/decode_eval.json (python3 tools/decode_eval.py --sweep): a best row under DECODE_FLOOR
# is returned flagged low_confidence; a statement that shares fewer than DECODE_MIN_EVIDENCE distinct words
# with all rows together (a single generic word such as "team" or "hours") gets no row at all.
DECODE_FLOOR = 5.0
DECODE_MIN_EVIDENCE = 2
DECODE_KEYWORD_CARDS = 2
DECODE_NUM_RATIO = 2.0   # "10 km" in a statement matches a "5 km" trigger, not a "30 km" one
# "detect" meets "detection", "jamming" meets "jammer": the ranker's stemmer keeps these apart on purpose
DECODE_SUFFIXES = ("ation", "ion", "er", "or")
DECODE_ROOT_MIN = 4
DECODE_WINDOW_SLACK = 2  # a multi-word trigger matches its words in any order within len + slack tokens
# Triggers keep the search stopwords ("how long" must not fire on "long"); only these connectors are
# dropped from both the trigger and the statement, so "jammed and spoofed" still meets "jammed or spoofed".
DECODE_CONNECTORS = frozenset("a an the and or".split())
# Generic English words in the row columns that would match any statement; triggers still see them.
DECODE_STOP = STOP | frozenset("after before each every must need know give way share keep make get use only also "
                               "no up out over through while more less one two three many much some other own "
                               "show want new good able long plan".split())
DECODE_LOW_NOTE = ("low confidence: no row clearly matches; read docs/problem-statement-decoder.md by hand "
                   "and run search with your own nouns")
LINK = re.compile(r"\[([^\]]*)\]\(([^)]*)\)")


def md_cells(line):
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]


def md_tables(text):
    """[(header cells, [row cells])] for every pipe table in a markdown text."""
    out, block = [], []
    for line in text.splitlines() + [""]:
        if line.lstrip().startswith("|"):
            block.append(md_cells(line))
            continue
        if len(block) >= 2 and all(re.fullmatch(r":?-+:?", c) for c in block[1] if c):
            out.append((block[0], block[2:]))
        block = []
    return out


def column(header, *keys):
    for k in keys:
        for i, h in enumerate(header):
            if k in h.lower():
                return i
    return None


def plain(cell):
    return re.sub(r"\s+", " ", re.sub(r"[`*]", "", LINK.sub(r"\1", cell))).strip()


def trigger_tokens(text):
    """Decode-only tokens: stemmed like search, but stopwords stay so phrase triggers keep their meaning."""
    text = text.lower()
    for rx, rep in NORMALIZE:
        text = rx.sub(rep, text)
    return [stem(t) for t in re.split(r"[^a-z0-9]+", text) if t and t not in DECODE_CONNECTORS]


def pattern(text):
    return tuple(trigger_tokens(text))


def root(t):
    for suf in DECODE_SUFFIXES:
        if t.endswith(suf) and len(t) - len(suf) >= DECODE_ROOT_MIN:
            t = t[:-len(suf)]
            return t[:-1] if t[-1] == t[-2] else t
    return t


def tok_match(a, b, near_numbers=True):
    if a.isdigit() or b.isdigit():
        if not near_numbers:
            return a == b
        return a.isdigit() and b.isdigit() and int(a) > 0 and int(b) > 0 and \
            max(int(a), int(b)) <= DECODE_NUM_RATIO * min(int(a), int(b))
    return a == b or root(a) == root(b)


def has_seq(seq, pat):
    n = len(pat)
    span = n + DECODE_WINDOW_SLACK if n > 1 else 1
    return n > 0 and any(all(any(tok_match(p, s) for s in seq[i:i + span]) for p in pat)
                         for i in range(max(1, len(seq) - n + 1)))


def trigger_groups(cell):
    """Quoted phrases (each with " / " alternatives). A "+" makes the trigger a conjunction:
    '"detect", "map" + jamming / interference' needs one group from each side."""
    sides = []
    for part in cell.rsplit("+", 1):
        groups = [[a.strip() for a in q.split(" / ") if a.strip()] for q in re.findall(r'"([^"]+)"', part)]
        bare = re.sub(r'"[^"]*"', "", part).strip(" ,")
        if not groups and bare:
            groups = [[a.strip() for a in bare.split("/") if a.strip()]]
        sides.append([{"text": " / ".join(g), "patterns": {pattern(a) for a in g} - {()}} for g in groups if g])
    return [s for s in sides if s]


def links(cell, kind):
    out = []
    for label, href in LINK.findall(cell):
        href = href.split("#", 1)[0].rstrip("/")
        name = href.rsplit("/", 1)[-1]
        if kind == "sample" and "samples/" in href:
            out.append({"id": f"sample:{name}", "name": label, "path": f"samples/{name}/README.md"})
        elif kind == "sample" and "templates/" in href:
            out.append({"name": label, "path": "templates/" + href.split("templates/", 1)[1]})
        elif kind == "card" and name.endswith(".md"):
            path = posix_join("docs", href)
            rid = ("repo:" + name[:-3].replace("__", "/") if "/repos/" in path or "integration-cards/" in path
                   else "res:" + name[:-3] if "/resources/" in path else None)
            out.append({"id": rid, "name": label, "path": path})
    return out


def posix_join(base, href):
    parts = []
    for part in (base + "/" + href).split("/"):
        if part == "..":
            if parts:
                parts.pop()
        elif part and part != ".":
            parts.append(part)
    return "/".join(parts)


def decoder_rows(text=None):
    """(rows, triggers) parsed from the decoder doc; tolerant of added rows and reordered columns."""
    if text is None:
        text = (ROOT / DECODER_DOC).read_text()
    rows, triggers = [], []
    for header, body in md_tables(text):
        wi, ri = column(header, "words"), column(header, "rows")
        pi, ei = column(header, "platform"), column(header, "explicit wording")
        if pi is not None and ei is not None and ri is not None:
            for cells in body:
                if len(cells) <= max(pi, ei, ri):
                    continue
                triggers.append({"platform": plain(cells[pi]), "words": cells[ei],
                                 "rows": [int(x) for x in re.findall(r"\d+", cells[ri])],
                                 "sides": trigger_groups(cells[ei])})
        elif wi is not None and ri is not None:
            for cells in body:
                if len(cells) <= max(wi, ri):
                    continue
                refs = [int(x) for x in re.findall(r"\d+", cells[ri])]
                read_as = column(header, "read as")
                triggers.append({"words": cells[wi], "read_as": plain(cells[read_as]) if read_as is not None
                                 and read_as < len(cells) else "", "rows": refs, "sides": trigger_groups(cells[wi])})
        elif "#" in header and column(header, "problem statement") is not None:
            ni = header.index("#")
            col = {k: column(header, *keys) for k, keys in (
                ("name", ("problem statement",)), ("approach", ("approach",)), ("stack", ("stack",)),
                ("datasets", ("dataset",)), ("start", ("start from",)), ("risk", ("risk",)), ("pitch", ("pitch",)))}
            for cells in body:
                if len(cells) <= ni or not cells[ni].isdigit():
                    continue
                get = lambda k: cells[col[k]] if col[k] is not None and col[k] < len(cells) else ""  # noqa: E731
                rows.append({"row": int(cells[ni]), "name": plain(get("name")), "approach": plain(get("approach")),
                             "start_from": links(get("start"), "sample"), "start_from_text": plain(get("start")),
                             "cards": links(get("stack"), "card"), "datasets": plain(get("datasets")),
                             "risk": plain(get("risk")), "pitch": plain(get("pitch"))})
    for row in rows:
        row["platforms"] = [tr["platform"] for tr in triggers
                            if tr.get("platform") and row["row"] in tr["rows"]]
    return rows, triggers


def row_keywords(row):
    """Search keywords for a row: its statement's content words plus its first stack names."""
    kw = list(dict.fromkeys(w for w in re.findall(r"[A-Za-z0-9][\w-]*", row["name"]) if w.lower() not in STOP))
    for c in row["cards"][:DECODE_KEYWORD_CARDS]:
        kw.append(re.sub(r"\s*\(.*?\)|\s+card$", "", c["name"]).strip())
    return " ".join(k for k in kw if k)


def decode(statement, limit=DECODE_MAX_ROWS, text=None):
    """Top decoder rows for a problem statement: trigger wording plus idf overlap with each row's columns.
    Deterministic. Every row carries low_confidence; [] when nothing or only one generic word matched."""
    rows, triggers = decoder_rows(text)
    if not rows:
        return []
    seq = trigger_tokens(statement)
    context = DECODE_CONTEXT | {t for tr in triggers if tr.get("platform")
                                for side in tr["sides"] for g in side for p in g["patterns"] for t in p}
    platforms = {tr["platform"] for tr in triggers if tr.get("platform") and tr["sides"] and
                 all(any(has_seq(seq, p) for g in side for p in g["patterns"]) for side in tr["sides"])}
    toks = {stem(t) for t in words(statement) if t not in DECODE_STOP}
    fields = {r["row"]: {f: {stem(t) for t in words(r.get(f, "")) if t not in DECODE_STOP} for f in DECODE_FIELD_W}
              for r in rows}
    df = defaultdict(int)
    for cols in fields.values():
        for t in set().union(*cols.values()):
            df[t] += 1
    idf = lambda t: math.log(1 + (len(rows) - df[t] + 0.5) / (df[t] + 0.5))  # noqa: E731
    score = {r["row"]: 0.0 for r in rows}
    why = {r["row"]: [] for r in rows}
    evidence = {r["row"]: set() for r in rows}
    task_evidence = {r["row"]: set() for r in rows}
    for tr in triggers:
        if tr.get("platform"):
            continue
        hit, used = [], set()
        for side in tr["sides"]:
            got = [g for g in side if any(has_seq(seq, p) for p in g["patterns"])]
            if not got:
                hit = []
                break
            hit += got
        if not hit:
            continue
        weight = 0.0
        for g in hit:
            best = max((p for p in g["patterns"] if has_seq(seq, p)), key=len)
            weight += 1 + DECODE_PHRASE_W * (len(best) - 1)
            used |= {s for s in seq for t in best if tok_match(t, s)}
        for pos, n in enumerate(tr["rows"]):
            if n in score:
                score[n] += DECODE_TRIGGER_W * weight / (1 + DECODE_TRIGGER_DECAY * pos)
                why[n] += [g["text"] for g in hit if g["text"] not in why[n]]
                evidence[n] |= used
    for n, cols in fields.items():
        seen = set()
        for f, w in DECODE_FIELD_W.items():
            hit = {t for t in cols[f] - seen if any(tok_match(t, s, False) for s in toks)}
            score[n] += w * sum(idf(t) for t in hit)
            seen |= cols[f]
            shared = {s for s in toks for t in hit if tok_match(t, s, False)}
            evidence[n] |= shared
            if f in ("name", "approach", "pitch"):
                task_evidence[n] |= shared - context
    for row in rows:
        if platforms and row["platforms"] and not platforms.intersection(row["platforms"]):
            score[row["row"]] *= DECODE_PLATFORM_CONFLICT
    ranked = sorted((r for r in rows if score[r["row"]] > 0 and
                     (why[r["row"]] or (task_evidence[r["row"]] and
                      len(evidence[r["row"]] & toks) / max(1, len(toks)) >= DECODE_MIN_COVERAGE))),
                    key=lambda r: (-score[r["row"]], r["row"]))
    if not ranked or len(set().union(*(evidence[r["row"]] for r in ranked))) < DECODE_MIN_EVIDENCE:
        return []
    best = score[ranked[0]["row"]]
    low = best < DECODE_FLOOR
    keep = [r for i, r in enumerate(ranked[:max(1, limit)]) if i == 0 or score[r["row"]] >= DECODE_KEEP * best]
    return [{**r, "score": round(score[r["row"]], 3), "low_confidence": low, "matched_wording": why[r["row"]],
             "keywords": row_keywords(r)} for r in keep]


def format_decoded(rows):
    out = [DECODE_LOW_NOTE, ""] if rows and rows[0]["low_confidence"] else []
    for r in rows:
        out.append(f"row {r['row']}: {r['name']}  (score {r['score']})")
        if r["matched_wording"]:
            out.append("  wording:    " + "; ".join(r["matched_wording"]))
        out.append("  approach:   " + r["approach"])
        out.append("  start from: " + (", ".join(s.get("id") or s["path"] for s in r["start_from"])
                                       or r["start_from_text"]))
        out.append("  cards:      " + ", ".join(c["name"] for c in r["cards"]))
        out.append("  risk:       " + r["risk"])
        out.append(f'  search:     python3 tools/query.py search "{r["keywords"]}"')
    return "\n".join(out) if out else ("no decoder row matched (the statement may be outside the hub's scope); "
                                       "read docs/problem-statement-decoder.md by hand or run search with your own nouns")


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
    return readiness.matches(r, a)


def brief(r):
    stars = (r.get("github") or {}).get("stargazers_count")
    bits = [r["kind"], r["id"], r.get("name") or r.get("title")]
    if stars:
        bits.append(f"★{stars}")
    if r.get("hackathon_fit"):
        bits.append(f"fit:{r['hackathon_fit']}")
    if r.get("status"):
        bits.append(f"status:{r['status']}" + (f", {r['deps']}" if r.get("deps") else ""))
    if r.get('readiness'):
        rd = r['readiness']
        bits.append(f"compute:{rd['compute']}, offline:{rd['offline']}, validation:{rd['validation']}")
    where = r.get("url") or r.get("readme") or r.get("page", "")
    limitation = (r.get('readiness') or {}).get('limitation')
    return (" | ".join(str(b) for b in bits) + "\n    " + (r.get("summary", "")[:200]) + f"\n    {where}"
            + (f"\n    Limitation: {limitation}" if limitation else ''))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["search", "decode", "concept", "show", "neighbors", "concepts"])
    p.add_argument("arg", nargs="?")
    p.add_argument("--kind")
    p.add_argument("--fit", choices=["high", "medium", "low"])
    p.add_argument("--domain")
    p.add_argument("--concept")
    for key, choices in readiness.ENUMS.items():
        p.add_argument('--' + key, choices=choices)
    p.add_argument('--platform', help='tested OS/architecture label, e.g. macos-arm64')
    for key in readiness.BUDGETS:
        p.add_argument('--' + key.replace('_', '-'), type=float)
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--depth", type=int, default=1)
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    try:
        readiness.filter_options(vars(a))
    except ValueError as exc:
        p.error(str(exc))
    if a.cmd == "decode":
        rows = decode(a.arg or "", min(a.limit, DECODE_MAX_ROWS))
        print(json.dumps(rows, indent=1, ensure_ascii=False) if a.json else format_decoded(rows))
        return
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
