#!/usr/bin/env python3
"""Build catalog pages, indexes and the knowledge graph from data/ and samples/.

Stdlib only. Outputs (all generated, do not hand-edit):
  catalog/{repos,resources,concepts,samples}/*.md
  INDEX.md                     human index by concept
  graph/graph.json             nodes + edges (the knowledge graph)
  graph/index.html             interactive graph viewer (loads graph.json)
  index/records.jsonl          one flat record per node, for LLM retrieval / grep
  llms.txt                     entry point for LLM agents
  reports/quality.md           dangling ids, duplicates, missing metadata
"""
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
LIST_FIELDS = ("concepts", "tags", "domains", "authors", "key_takeaways")
TOP_PER_CONCEPT = 400  # INDEX.md rows per concept before truncation


def load_lane_dir(sub):
    recs = []
    for f in sorted((DATA / sub).glob("*.json")):
        for r in json.loads(f.read_text()):
            r["_lane"] = f.stem
            recs.append(r)
    return recs


def load_samples():
    out = []
    for f in sorted((ROOT / "samples").glob("*/sample.json")):
        s = json.loads(f.read_text())
        s["kind"] = "sample"
        s["_dir"] = f.parent.name
        s["_lane"] = "samples"
        out.append(s)
    return out


def norm_id(i):
    if i.startswith("repo:"):
        return i.lower().rstrip("/").removesuffix(".git")
    return i


def norm_url(u):
    u = re.sub(r"^https?://(www\.)?", "", u.strip().lower())
    return u.split("#")[0].rstrip("/")


def merge(records, aliases):
    """Merge records sharing an id (same repo found by two lanes)."""
    by_id, dups = {}, defaultdict(list)
    for r in records:
        r["id"] = aliases.get(norm_id(r["id"]), norm_id(r["id"]))
        for rel in r.get("related", []):
            rel["id"] = aliases.get(norm_id(rel["id"]), norm_id(rel["id"]))
        cur = by_id.get(r["id"])
        if cur is None:
            r["_lanes"] = [r["_lane"]]
            by_id[r["id"]] = r
            continue
        dups[r["id"]].append(r["_lane"])
        cur["_lanes"].append(r["_lane"])
        for k in LIST_FIELDS:
            cur[k] = list(dict.fromkeys(cur.get(k, []) + r.get(k, [])))
        seen = {(x["id"], x["rel"]) for x in cur.get("related", [])}
        cur.setdefault("related", []).extend(x for x in r.get("related", []) if (x["id"], x["rel"]) not in seen)
        for k in ("summary", "why_it_matters", "hackathon_notes"):
            if len(r.get(k, "")) > len(cur.get(k, "")):
                cur[k] = r[k]
    return by_id, dups


def slug(node_id):
    s = node_id.split(":", 1)[1]
    return re.sub(r"[^a-z0-9._-]+", "__", s.lower()).strip("_")


FOLDER = {"repo": "repos", "concept": "concepts", "sample": "samples"}


def page_path(n):
    return f"catalog/{FOLDER.get(n['kind'], 'resources')}/{slug(n['id'])}.md"


def link(nodes, nid, from_catalog=True):
    n = nodes.get(nid)
    if not n:
        return f"`{nid}` (not indexed)"
    target = page_path(n)
    if from_catalog:
        target = "../" + target.split("/", 1)[1]
    return f"[{label(n)}]({target})"


def label(n):
    return n.get("name") or n.get("title") or n["id"]


def stars(meta):
    s = meta.get("stargazers_count")
    return f"{s:,}" if isinstance(s, int) else "?"


def render_repo(n, nodes, back, meta):
    m = meta.get(n["id"], {})
    lines = [
        f"# {label(n)}",
        "",
        f"`{n['id']}` - <{n['url']}>",
        "",
        "| stars | language | license | last push | archived | maturity | hackathon fit |",
        "|---|---|---|---|---|---|---|",
        f"| {stars(m)} | {m.get('language') or n.get('language', '?')} | {m.get('license') or '?'} | "
        f"{(m.get('pushed_at') or '?')[:10]} | {m.get('archived', '?')} | {n.get('maturity', '?')} | "
        f"{n.get('hackathon_fit', '?')} |",
        "",
        n.get("summary", ""),
        "",
    ]
    if n.get("why_it_matters"):
        lines += ["**Why it matters:** " + n["why_it_matters"], ""]
    if n.get("hackathon_notes"):
        lines += ["**Hackathon notes:** " + n["hackathon_notes"], ""]
    lines += common_tail(n, nodes, back)
    if m.get("fetched"):
        lines += ["", f"_GitHub metadata fetched {m['fetched']}._"]
    return "\n".join(lines) + "\n"


def render_resource(n, nodes, back, meta):
    lines = [
        f"# {label(n)}",
        "",
        f"`{n['id']}` - {n.get('kind')} - <{n.get('url', '')}>",
        "",
        f"**By:** {', '.join(n.get('authors', [])) or '?'} - **Year:** {n.get('year', '?')} - "
        f"**Level:** {n.get('level', '?')} - **Access:** {n.get('access', '?')}",
        "",
        n.get("summary", ""),
        "",
    ]
    if n.get("key_takeaways"):
        lines += ["## Key takeaways", ""] + [f"- {t}" for t in n["key_takeaways"]] + [""]
    lines += common_tail(n, nodes, back)
    return "\n".join(lines) + "\n"


def render_sample(n, nodes, back, meta):
    lines = [
        f"# Sample: {label(n)}",
        "",
        f"`{n['id']}` - code and walkthrough in [samples/{n['_dir']}](../../samples/{n['_dir']}/)",
        "",
        n.get("summary", ""),
        "",
        f"**Verification:** {n.get('verified', 'unverified sketch')}",
        "",
    ]
    lines += common_tail(n, nodes, back)
    return "\n".join(lines) + "\n"


ATTACH_DIRS = ("docs/integration-cards", "docs/dataset-cards", "docs/paper-digests", "docs/landscape")
ATTACH_RE = re.compile(r"<!--\s*about:\s*([^>]+?)\s*-->")


def load_attachments():
    """Deep-dive docs declare the nodes they describe with <!-- about: id1, id2 --> anywhere in the file."""
    att = defaultdict(list)
    for d in ATTACH_DIRS:
        for f in sorted((ROOT / d).glob("*.md")):
            for m in ATTACH_RE.finditer(f.read_text()):
                for nid in m.group(1).split(","):
                    att[norm_id(nid.strip())].append(f.relative_to(ROOT).as_posix())
    return att


ATTACHMENTS = {}


def common_tail(n, nodes, back):
    lines = []
    docs = ATTACHMENTS.get(n["id"], [])
    if docs:
        lines += ["## Deep dives", ""] + [f"- [{Path(d).stem}](../../{d}) ({Path(d).parent.name})" for d in docs] + [""]
    if n.get("concepts"):
        lines += ["**Concepts:** " + ", ".join(link(nodes, c) for c in n["concepts"]), ""]
    if n.get("tags"):
        lines += ["**Tags:** " + ", ".join(f"`{t}`" for t in n["tags"]), ""]
    if n.get("domains"):
        lines += ["**Domains:** " + ", ".join(n["domains"]), ""]
    if n.get("related"):
        lines += ["## Related", ""] + [f"- {x['rel']}: {link(nodes, x['id'])}" for x in n["related"]] + [""]
    incoming = [e for e in back.get(n["id"], []) if e[1] != "about"]
    if incoming:
        lines += ["## Referenced by", ""] + [f"- {link(nodes, s)} ({rel})" for s, rel in sorted(set(incoming))] + [""]
    lines += [f"_Indexed by lane(s): {', '.join(n.get('_lanes', [n.get('_lane', '?')]))}_"]
    return lines


def render_concept(c, nodes, members, children):
    lines = [f"# {c['name']}", "", f"`{c['id']}`", "", c["summary"], ""]
    if c.get("parent"):
        lines += ["**Parent:** " + link(nodes, c["parent"]), ""]
    if children.get(c["id"]):
        lines += ["**Sub-concepts:** " + ", ".join(link(nodes, k) for k in children[c["id"]]), ""]
    mem = [nodes[m] for m in members.get(c["id"], [])]
    for kind_label, pred in (
        ("Samples", lambda x: x["kind"] == "sample"),
        ("Repositories", lambda x: x["kind"] == "repo"),
        ("Documents, talks, courses, datasets", lambda x: x["kind"] not in ("repo", "sample")),
    ):
        group = [x for x in mem if pred(x)]
        if not group:
            continue
        lines += [f"## {kind_label} ({len(group)})", ""]
        for x in sorted(group, key=sort_key):
            extra = f" - {x.get('kind')}" if x["kind"] not in ("repo", "sample") else ""
            fit = f" - fit: {x['hackathon_fit']}" if x.get("hackathon_fit") else ""
            lines.append(f"- {link(nodes, x['id'])}{extra}{fit} - {first_sentence(x.get('summary', ''))}")
        lines.append("")
    return "\n".join(lines) + "\n"


FIT_RANK = {"high": 0, "medium": 1, "low": 2}


def sort_key(x):
    return (FIT_RANK.get(x.get("hackathon_fit"), 3), -(x.get("_stars") or 0), label(x).lower())


def first_sentence(s):
    m = re.match(r"(.+?[.!?])(\s|$)", s)
    return (m.group(1) if m else s)[:220]


def main():
    concepts = json.loads((DATA / "concepts.json").read_text())
    meta_path = DATA / "github_meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {}
    aliases = {}
    for rid, m in meta.items():
        full = m.get("full_name")
        if full and f"repo:{full.lower()}" != rid:
            aliases[rid] = f"repo:{full.lower()}"
    meta = {aliases.get(k, k): v for k, v in meta.items()}

    raw_resources = load_lane_dir("resources")
    first_by_url = {}
    for r in raw_resources:
        key = norm_url(r.get("url", ""))
        if not key:
            continue
        if key in first_by_url and first_by_url[key] != r["id"]:
            aliases[r["id"]] = first_by_url[key]
        else:
            first_by_url.setdefault(key, r["id"])
    repos, repo_dups = merge(load_lane_dir("repos"), aliases)
    resources, res_dups = merge(raw_resources, aliases)
    samples, _ = merge(load_samples(), aliases)
    for r in repos.values():
        r["_stars"] = meta.get(r["id"], {}).get("stargazers_count")
    nodes = {c["id"]: {**c, "kind": "concept"} for c in concepts}
    nodes.update(repos)
    nodes.update(resources)
    nodes.update(samples)

    edges, back, members = [], defaultdict(list), defaultdict(list)
    dangling, bad_concepts = defaultdict(list), defaultdict(list)
    for n in list(repos.values()) + list(resources.values()) + list(samples.values()):
        for c in n.get("concepts", []):
            if c not in nodes or nodes[c]["kind"] != "concept":
                bad_concepts[c].append(n["id"])
                continue
            edges.append({"source": n["id"], "target": c, "rel": "about"})
            members[c].append(n["id"])
        for x in n.get("related", []):
            if x["id"] not in nodes:
                dangling[x["id"]].append(n["id"])
                continue
            edges.append({"source": n["id"], "target": x["id"], "rel": x["rel"]})
            back[x["id"]].append((n["id"], x["rel"]))
    children = defaultdict(list)
    for c in concepts:
        if c.get("parent"):
            children[c["parent"]].append(c["id"])
            edges.append({"source": c["id"], "target": c["parent"], "rel": "subconcept_of"})

    ATTACHMENTS.update({aliases.get(k, k): v for k, v in load_attachments().items()})
    for sub in ("repos", "resources", "concepts", "samples"):
        d = ROOT / "catalog" / sub
        d.mkdir(parents=True, exist_ok=True)
        for old in d.glob("*.md"):
            old.unlink()
    renderers = {"repo": render_repo, "sample": render_sample}
    for n in nodes.values():
        if n["kind"] == "concept":
            text = render_concept(n, nodes, members, children)
        else:
            text = renderers.get(n["kind"], render_resource)(n, nodes, back, meta)
        (ROOT / page_path(n)).write_text(text)
    # Merged ids (renamed repos, duplicate resource URLs) keep a stub page so links to the old id survive.
    for old, new in aliases.items():
        target = nodes.get(new)
        if not target or old in nodes:
            continue
        stub = {"id": old, "kind": target["kind"]}
        path = ROOT / page_path(stub)
        if not path.exists():
            path.write_text(f"# Moved\n\n`{old}` was merged into {link(nodes, new)}.\n")

    write_index(nodes, concepts, members, children)
    write_graph(nodes, edges, meta)
    write_records(nodes, meta)
    write_quality(nodes, repo_dups, res_dups, dangling, bad_concepts, meta)
    write_llms(nodes, concepts, members)
    write_site(nodes, edges, meta)
    kinds = defaultdict(int)
    for n in nodes.values():
        kinds[n["kind"]] += 1
    print("nodes:", dict(kinds), "edges:", len(edges), "dangling:", len(dangling), "bad concepts:", len(bad_concepts))


def write_index(nodes, concepts, members, children):
    kinds = defaultdict(int)
    for n in nodes.values():
        kinds[n["kind"]] += 1
    lines = [
        "# Navigation Index",
        "",
        "Generated by `tools/build.py` - do not edit by hand.",
        "",
        " - ".join(f"**{v}** {k}s" for k, v in sorted(kinds.items())),
        "",
        "Browse by concept below, open [the graph](graph/index.html), or grep `index/records.jsonl`.",
        "",
    ]
    roots = [c for c in concepts if not c.get("parent")]

    def emit(c, depth):
        mem = members.get(c["id"], [])
        nrepo = sum(1 for m in mem if nodes[m]["kind"] == "repo")
        nres = len(mem) - nrepo
        lines.append(
            f"{'  ' * depth}- [{c['name']}](catalog/concepts/{slug(c['id'])}.md) - {nrepo} repos, {nres} docs/samples"
        )
        for k in children.get(c["id"], []):
            emit(nodes[k], depth + 1)

    lines += ["## Concept tree", ""]
    for c in roots:
        emit(c, 0)
    lines += ["", "## High hackathon-fit repositories", "", "| repo | stars | concepts | why |", "|---|---|---|---|"]
    top = [n for n in nodes.values() if n["kind"] == "repo" and n.get("hackathon_fit") == "high"]
    for n in sorted(top, key=sort_key)[:TOP_PER_CONCEPT]:
        cs = ", ".join(nodes[c]["name"] for c in n.get("concepts", []) if c in nodes)
        why = first_sentence(n.get("why_it_matters", "")).replace("|", "/")
        stars_s = f"{n['_stars']:,}" if n.get("_stars") else "?"
        lines.append(f"| [{label(n)}]({page_path(n)}) | {stars_s} | {cs} | {why} |")
    (ROOT / "INDEX.md").write_text("\n".join(lines) + "\n")


def write_graph(nodes, edges, meta):
    out = []
    for n in nodes.values():
        out.append({
            "id": n["id"],
            "kind": n["kind"],
            "label": label(n),
            "url": n.get("url"),
            "page": page_path(n),
            "concepts": n.get("concepts", []),
            "stars": n.get("_stars"),
            "fit": n.get("hackathon_fit"),
        })
    gdir = ROOT / "graph"
    gdir.mkdir(exist_ok=True)
    (gdir / "graph.json").write_text(json.dumps({"nodes": out, "edges": edges}, ensure_ascii=False) + "\n")


def write_records(nodes, meta):
    idir = ROOT / "index"
    idir.mkdir(exist_ok=True)
    with (idir / "records.jsonl").open("w") as f:
        for n in nodes.values():
            rec = {k: v for k, v in n.items() if not k.startswith("_")}
            rec["page"] = page_path(n)
            if ATTACHMENTS.get(n["id"]):
                rec["deep_dives"] = ATTACHMENTS[n["id"]]
            if n["kind"] == "repo" and n["id"] in meta:
                m = meta[n["id"]]
                rec["github"] = {k: m.get(k) for k in ("stargazers_count", "license", "pushed_at", "archived", "language")}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def write_llms(nodes, concepts, members):
    nrepo = sum(1 for n in nodes.values() if n["kind"] == "repo")
    nsample = sum(1 for n in nodes.values() if n["kind"] == "sample")
    nres = len(nodes) - nrepo - nsample - len(concepts)
    lines = [
        "# navigation-index",
        "",
        f"> Knowledge hub for navigation / PNT / GNSS-denied autonomy with a defense lens: {nrepo} open-source repos, "
        f"{nres} documents, talks, courses and datasets, {nsample} usage samples, linked in one graph over {len(concepts)} concepts.",
        "",
        "Read AGENTS.md for how to query and extend. Query without reading everything: "
        "`python3 tools/query.py search \"<terms>\"` or the MCP server tools/mcp_server.py.",
        "",
        "## Entry points",
        "",
        "- [AGENTS.md](AGENTS.md): how agents use and extend the hub",
        "- [INDEX.md](INDEX.md): concept tree and high hackathon-fit repos",
        "- [docs/hackathon-playbook.md](docs/hackathon-playbook.md): project ideas, reference architectures",
        "- [docs/reference-stacks.md](docs/reference-stacks.md): opinionated picks per capability",
        "- [docs/primer/README.md](docs/primer/README.md): navigation primer chapters",
        "- [docs/SCHEMA.md](docs/SCHEMA.md): data model",
        "- [index/records.jsonl](index/records.jsonl): every node as one JSON line",
        "- [graph/graph.json](graph/graph.json): nodes and edges",
        "",
        "## Concepts",
        "",
    ]
    for c in concepts:
        lines.append(f"- [{c['name']}](catalog/concepts/{slug(c['id'])}.md): {len(members.get(c['id'], []))} items - {c['summary']}")
    lines += ["", "## Samples", ""]
    for n in nodes.values():
        if n["kind"] == "sample":
            lines.append(f"- [{label(n)}](samples/{n['_dir']}/README.md): {first_sentence(n.get('summary', ''))}")
    (ROOT / "llms.txt").write_text("\n".join(lines) + "\n")


def write_quality(nodes, repo_dups, res_dups, dangling, bad_concepts, meta):
    lines = ["# Quality report", "", "Generated by `tools/build.py`.", ""]
    missing = [n["id"] for n in nodes.values() if n["kind"] == "repo" and n["id"].count("/") == 1 and n["id"] not in meta]
    errors = [k for k, v in meta.items() if "error" in v]
    archived = [k for k, v in meta.items() if v.get("archived")]
    sections = [
        ("Referenced but not indexed (candidates to add)", [f"`{k}` <- {', '.join(sorted(set(v)))}" for k, v in sorted(dangling.items())]),
        ("Unknown concept ids", [f"`{k}` <- {', '.join(v)}" for k, v in bad_concepts.items()]),
        ("Found by multiple lanes (merged)", [f"`{k}` also in {', '.join(v)}" for k, v in sorted({**repo_dups, **res_dups}.items())]),
        ("Repos without GitHub metadata (run tools/enrich.py)", [f"`{m}`" for m in missing]),
        ("GitHub API errors", [f"`{e}`: {meta[e]['error']}" for e in errors]),
        ("Archived upstream", [f"`{a}`" for a in archived]),
    ]
    for title, items in sections:
        lines += [f"## {title} ({len(items)})", ""] + [f"- {i}" for i in items] + [""]
    rdir = ROOT / "reports"
    rdir.mkdir(exist_ok=True)
    (rdir / "quality.md").write_text("\n".join(lines))


DOC_KIND = {"docs/integration-cards": "integration-card", "docs/dataset-cards": "dataset-card",
            "docs/paper-digests": "paper-digest", "docs/landscape": "landscape"}
SITE_DOC_SUMMARY = 400  # chars of a deep-dive doc's lead paragraph shown on its card
SITE_DOC_BODY = 1500  # chars of plain text per deep-dive doc kept for search


def md_plain(text):
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[#*`|>]+|\s+", " ", text).strip()


def site_doc(path):
    text = (ROOT / path).read_text()
    title = next((ln[2:].strip() for ln in text.splitlines() if ln.startswith("# ")), Path(path).stem)
    lead = ""
    for block in re.split(r"\n\s*\n", re.sub(r"<!--.*?-->", "", text, flags=re.S)):
        b = block.strip()
        if b and not b.startswith(("#", "|", "```", "<")):
            lead = md_plain(b)
            break
    about = [norm_id(x.strip()) for m in ATTACH_RE.finditer(text) for x in m.group(1).split(",")]
    return title, lead, about, md_plain(text)


def site_verify_status(v):
    low = (v or "").lower()
    if not low or "placeholder" in low:
        return "placeholder"
    if re.search(r"\b(ran|run on|built and ran|tests? pass)", low) and not low.startswith(("not run", "unverified", "sketch")):
        return "ran"
    return "sketch"


def write_site(nodes, edges, meta):
    """Compact search/facet index for the static web UI in site/ (site/data/index.json)."""
    ids = list(nodes)
    pos = {nid: i for i, nid in enumerate(ids)}
    related = defaultdict(list)
    for e in edges:
        if e["rel"] != "about" and e["source"] in pos and e["target"] in pos:
            related[e["source"]].append([pos[e["target"]], e["rel"]])
    sample_linked = {x["id"] for n in nodes.values() if n["kind"] == "sample" for x in n.get("related", [])}
    out_nodes = []
    for nid in ids:
        n = nodes[nid]
        m = meta.get(nid, {}) if n["kind"] == "repo" else {}
        dd = ATTACHMENTS.get(nid, [])
        rec = {
            "i": nid, "k": n["kind"], "n": label(n), "s": n.get("summary", ""),
            "w": n.get("why_it_matters"), "h": n.get("hackathon_notes"),
            "kt": " ".join(n.get("key_takeaways", [])), "g": n.get("tags"), "c": n.get("concepts"),
            "d": n.get("domains"), "f": n.get("hackathon_fit"), "m": n.get("maturity"),
            "l": m.get("license"), "lg": m.get("language") or n.get("language"),
            "st": m.get("stargazers_count"), "pu": (m.get("pushed_at") or "")[:10], "ar": m.get("archived"),
            "u": n.get("url"), "p": page_path(n), "dd": dd, "y": n.get("year"), "lv": n.get("level"),
            "pa": n.get("parent"), "r": related.get(nid),
            "hs": 1 if nid in sample_linked or n["kind"] == "sample" else None,
            "hi": 1 if any(d.startswith("docs/integration-cards/") for d in dd) else None,
        }
        if n["kind"] == "sample":
            rec.update({"v": n.get("verified", ""), "vs": site_verify_status(n.get("verified")), "sd": n.get("_dir")})
        out_nodes.append({k: v for k, v in rec.items() if v not in (None, "", [], False)})
    out_docs = []
    for d, kind in DOC_KIND.items():
        for f in sorted((ROOT / d).glob("*.md")):
            path = f.relative_to(ROOT).as_posix()
            title, lead, about, body = site_doc(path)
            about_ix = [pos[a] for a in dict.fromkeys(about) if a in pos]
            concepts = list(dict.fromkeys(
                c for a in about if a in nodes
                for c in ([a] if nodes[a]["kind"] == "concept" else nodes[a].get("concepts", []))))
            rec = {"i": "doc:" + path, "k": kind, "n": title, "s": lead[:SITE_DOC_SUMMARY],
                   "b": body[:SITE_DOC_BODY], "c": concepts, "p": path, "ab": about_ix}
            out_docs.append({k: v for k, v in rec.items() if v not in (None, "", [])})
    sdir = ROOT / "site" / "data"
    sdir.mkdir(parents=True, exist_ok=True)
    payload = {"generated_by": "tools/build.py", "nodes": out_nodes, "docs": out_docs}
    (sdir / "index.json").write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
