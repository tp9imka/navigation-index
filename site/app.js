"use strict";

const DATA_URL = "data/index.json";
const ROOT = "../"; // repo root relative to site/
const PAGE_SIZE = 50;
const FACET_COLLAPSED = 8;
const FIT_RANK = { high: 0, medium: 1, low: 2 };
const DOC_KINDS = { "integration-card": "integration card", "dataset-card": "dataset card", "paper-digest": "paper digest", "guide": "guide" };
const STAR_BUCKETS = [["10k+", 10000, Infinity], ["1k-10k", 1000, 10000], ["100-1k", 100, 1000], ["10-100", 10, 100], ["<10", 0, 10]];
const VERIFY_LABEL = { ran: "ran", partial: "partly ran", sketch: "sketch / not run", pending: "pending", placeholder: "placeholder" };

const FACETS = [
  { key: "kind", title: "Kind", vals: e => [e.k] },
  { key: "fit", title: "Hackathon fit", vals: e => e.f ? [e.f] : [], order: ["high", "medium", "low"] },
  { key: "domain", title: "Domain", vals: e => e.d || [] },
  { key: "maturity", title: "Maturity", vals: e => e.m ? [e.m] : [] },
  { key: "has", title: "Has", vals: e => [e.hs && "sample", e.hi && "integration card", e.dd && e.dd.length && "any deep dive"].filter(Boolean) },
  { key: "stars", title: "GitHub stars", vals: e => typeof e.st === "number" ? [STAR_BUCKETS.find(b => e.st >= b[1] && e.st < b[2])[0]] : [], order: STAR_BUCKETS.map(b => b[0]) },
  { key: "language", title: "Language", vals: e => e.lg ? [e.lg] : [] },
  { key: "license", title: "License", vals: e => e.l ? [e.l] : [] },
];

const S = { q: "", f: {}, concept: "", view: "search", page: "", anchor: "", limit: PAGE_SIZE, sel: -1, expanded: new Set() };
let E = [], byId = new Map(), byPage = new Map(), incoming = new Map(), children = new Map(), concepts = [];
let shown = [], RK = null;
const $ = s => document.querySelector(s);

function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function load() {
  let data;
  try {
    data = await (await fetch(DATA_URL)).json();
  } catch (err) {
    $("#results").innerHTML = `<div class="empty">Could not load <code>${DATA_URL}</code>. Serve the repo root over HTTP (<code>python3 -m http.server</code>) and open <code>/site/</code>; run <code>python3 tools/build.py</code> if the file is missing.</div>`;
    return;
  }
  E = data.nodes.concat(data.docs);
  E.forEach((e, i) => {
    e.x = i;
    e.isDoc = e.i.startsWith("doc:");
    byId.set(e.i, e);
    byPage.set(e.p, e);
    if (e.sd) byPage.set(`samples/${e.sd}/README.md`, e);
  });
  E.forEach(e => {
    (e.r || []).forEach(([t, rel]) => {
      if (!incoming.has(t)) incoming.set(t, []);
      incoming.get(t).push([e.x, rel]);
    });
    (e.ab || []).forEach(t => {
      if (!incoming.has(t)) incoming.set(t, []);
      incoming.get(t).push([e.x, "deep dive"]);
    });
  });
  concepts = E.filter(e => e.k === "concept");
  RK = buildRanker(E);
  concepts.forEach(c => {
    const p = c.pa || "";
    if (!children.has(p)) children.set(p, []);
    children.get(p).push(c.i);
  });
  const nRepo = data.nodes.filter(n => n.k === "repo").length;
  $("#q").placeholder = `Search ${nRepo} repos, ${data.nodes.length - nRepo} other nodes, ${data.docs.length} deep-dive docs  ( / )`;
  readHash();
  if (S.view === "search") lastSearchHash = searchHash();
  render();
}

// ---------- search ----------

// ---- ranker begin
// Port of the Ranker in tools/query.py (BM25F + concept boost + priors); keep constants and
// arithmetic order identical. `python3 tools/search_eval.py --parity` runs this block under node.
const FIELDS = ["name", "tags", "concepts", "summary", "why", "notes", "takeaways", "lang", "kind", "deep"];
const FIELD_W = { name: 4.0, tags: 1.5, concepts: 1.5, summary: 1.5, why: 0.7, notes: 0.5, takeaways: 0.7, lang: 1.0, kind: 1.0, deep: 1.0 };
const FIELD_B = { name: 0.3, tags: 0.3, concepts: 0.0, summary: 0.6, why: 0.6, notes: 0.6, takeaways: 0.6, lang: 0.0, kind: 0.0, deep: 0.75 };
const K1 = 1.2, CONCEPT_MIN = 0.5, CONCEPT_W = 2.5;
const PRIOR_FIT = { high: 0.4, medium: 0.15 }, PRIOR_RAN = 0.4;
const DEEP_DOC_MAX_ABOUT = 4;
const DEEP_DOC_CHARS = 1500, GUIDE_BODY_CHARS = 6000;
const STOP = new Set(("a an and are as at be by for from in into is it of on or the to with via using none " +
  "all any but can do does have has how if its not our should so than that their them then there they this we what when where which who will you your").split(" "));
const SYNONYM = { gps: "gnss", drone: "uav", uas: "uav", suas: "uav", quadcopter: "uav", quadrotor: "uav", multirotor: "uav", ladar: "lidar", harbour: "harbor", defence: "defense", ship: "vessel", boat: "vessel" };
const NORMALIZE = [[/isation/g, "ization"], [/geo[\s_-]+locali[sz]ation/g, "geolocalization"], [/geo[\s_-]+locali[sz]e/g, "geolocalize"]];

function stem(t) {
  const syn = w => Object.prototype.hasOwnProperty.call(SYNONYM, w);
  if (t.length > 4 && t.endsWith("ies")) t = t.slice(0, -3) + "y";
  else if (t.length > 3 && t.endsWith("s") && !t.endsWith("ss") && !t.endsWith("us") && !t.endsWith("is")) t = t.slice(0, -1);
  if (syn(t)) return SYNONYM[t];
  let cut = false;
  if (t.length > 5 && t.endsWith("ing")) { t = t.slice(0, -3); cut = true; }
  else if (t.length > 4 && t.endsWith("ed")) { t = t.slice(0, -2); cut = true; }
  if (cut && t.length > 3 && t[t.length - 1] === t[t.length - 2] && !"lsz".includes(t[t.length - 1])) t = t.slice(0, -1);
  else if (t.length > 3 && t.endsWith("e")) t = t.slice(0, -1);
  return syn(t) ? SYNONYM[t] : t;
}

function tokens(text) {
  text = String(text || "").toLowerCase();
  for (const [rx, rep] of NORMALIZE) text = text.replace(rx, rep);
  return text.split(/[^a-z0-9]+/).filter(t => t && !STOP.has(t)).map(stem);
}

function buildRanker(entries) {
  const cname = new Map(entries.filter(e => e.k === "concept").map(e => [e.i, e.n || ""]));
  const docBody = new Map(), users = new Map();
  // code-point slicing, so cuts match Python's str slicing
  const cut = (s, n) => Array.from(s || "").slice(0, n).join("");
  for (const e of entries) {
    if (e.i.startsWith("doc:")) docBody.set(e.p, e.b || "");
    else if (e.k === "guide") docBody.set(e.p, cut(e.b, DEEP_DOC_CHARS));
    else for (const d of e.dd || []) users.set(d, (users.get(d) || 0) + 1);
  }
  const join = v => Array.isArray(v) ? v.join(" ") : String(v || "");
  const prep = e => {
    const isDoc = e.i.startsWith("doc:");
    const cs = (e.c || []).concat(e.k === "concept" ? [e.i] : []);
    const fields = isDoc
      ? { name: e.n, summary: e.s, deep: e.b, concepts: cs.map(c => cname.get(c) || "").join(" ") }
      : {
          name: e.n, tags: join(e.g), concepts: cs.map(c => cname.get(c) || "").join(" "), summary: join(e.s),
          why: join(e.w), notes: join(e.h), takeaways: join(e.kt), lang: e.lg || "", kind: e.k,
          deep: e.k === "guide" ? cut(e.b, GUIDE_BODY_CHARS)
            : (e.dd || []).filter(d => docBody.has(d) && users.get(d) <= DEEP_DOC_MAX_ABOUT).map(d => docBody.get(d)).join(" "),
        };
    const f = {}, tf = {};
    for (const k of FIELDS) {
      f[k] = tokens(fields[k]);
      tf[k] = new Map();
      for (const t of f[k]) tf[k].set(t, (tf[k].get(t) || 0) + 1);
    }
    let prior = isDoc ? 0 : (PRIOR_FIT[e.f] || 0.0);
    if (e.k === "sample" && e.vs === "ran") prior += PRIOR_RAN;
    return { e, f, tf, cs, prior, id: e.i, stars: e.st || 0 };
  };
  const corpus = [], extra = [];
  for (const e of entries) (e.i.startsWith("doc:") ? extra : corpus).push(prep(e));
  const n = corpus.length, avg = {}, df = new Map();
  for (const k of FIELDS) {
    let sum = 0;
    for (const x of corpus) sum += x.f[k].length;
    avg[k] = (sum / n) || 1.0;
  }
  for (const x of corpus) {
    const seen = new Set();
    for (const k of FIELDS) for (const t of x.f[k]) seen.add(t);
    for (const t of seen) df.set(t, (df.get(t) || 0) + 1);
  }
  const idfUnseen = Math.log(1 + (n + 0.5) / 0.5);
  const idf = t => df.has(t) ? Math.log(1 + (n - df.get(t) + 0.5) / (df.get(t) + 0.5)) : idfUnseen;
  const conceptTokens = [...cname].map(([cid, name]) => [cid, new Set(tokens(name + " " + cid.split(":").slice(1).join(":")))]);

  function score(x, q, cboost) {
    let base = 0.0;
    for (const t of q) {
      let tfw = 0.0;
      for (const k of FIELDS) {
        const c = x.tf[k].get(t);
        if (c) {
          const norm = 1 - FIELD_B[k] + FIELD_B[k] * x.f[k].length / avg[k];
          tfw += FIELD_W[k] * c / norm;
        }
      }
      if (tfw > 0) base += idf(t) * tfw / (K1 + tfw);
    }
    if (base <= 0) return 0.0;
    let best = 0.0;
    for (const c of x.cs) best = Math.max(best, cboost.get(c) || 0.0);
    return base + CONCEPT_W * best + x.prior;
  }

  function rank(query) {
    const q = [...new Set(tokens(query))];
    if (!q.length) return [];
    let total = 0;
    for (const t of q) total += idf(t);
    const cboost = new Map();
    for (const [cid, toks] of conceptTokens) {
      let m = 0;
      for (const t of q) if (toks.has(t)) m += idf(t);
      m = m / total;
      if (m >= CONCEPT_MIN) cboost.set(cid, m);
    }
    const hits = [];
    for (const x of corpus.concat(extra)) {
      const s = score(x, q, cboost);
      if (s > 0) hits.push([Math.floor(s * 1e6 + 0.5), x]);
    }
    hits.sort((a, b) => b[0] - a[0] || b[1].stars - a[1].stars || (a[1].id < b[1].id ? -1 : a[1].id > b[1].id ? 1 : 0));
    return hits.map(([s, x]) => [s / 1e6, x.e]);
  }
  return { rank };
}
// ---- ranker end

function conceptSet(id) {
  const out = new Set([id]);
  const walk = c => (children.get(c) || []).forEach(k => { out.add(k); walk(k); });
  walk(id);
  return out;
}

function passes(e, skipKey, cset) {
  if (cset && !(e.c || []).some(c => cset.has(c)) && !cset.has(e.i)) return false;
  for (const fd of FACETS) {
    if (fd.key === skipKey) continue;
    const sel = S.f[fd.key];
    if (!sel || !sel.size) continue;
    if (!fd.vals(e).some(v => sel.has(v))) return false;
  }
  return true;
}

function search() {
  const cset = S.concept ? conceptSet(S.concept) : null;
  let base;
  if (S.q.trim()) {
    base = RK.rank(S.q).map(x => x[1]);
  } else {
    base = E.slice().sort((a, b) =>
      (FIT_RANK[a.f] ?? 3) - (FIT_RANK[b.f] ?? 3) || (b.st || 0) - (a.st || 0) || a.n.localeCompare(b.n));
  }
  return { base, cset, hits: base.filter(e => passes(e, null, cset)) };
}

// ---------- state <-> hash ----------

function readHash() {
  const h = new URLSearchParams(location.hash.slice(1));
  S.q = h.get("q") || "";
  S.concept = h.get("concept") || "";
  S.page = h.get("page") || "";
  S.anchor = h.get("a") || "";
  S.view = S.page ? "page" : (h.get("view") === "kits" ? "kits" : "search");
  S.f = {};
  for (const fd of FACETS) {
    const v = h.get(fd.key);
    if (v) S.f[fd.key] = new Set(v.split(","));
  }
  $("#q").value = S.q;
}

function searchHash() {
  const h = new URLSearchParams();
  if (S.q) h.set("q", S.q);
  if (S.concept) h.set("concept", S.concept);
  for (const fd of FACETS) if (S.f[fd.key] && S.f[fd.key].size) h.set(fd.key, [...S.f[fd.key]].join(","));
  return h.toString();
}

let lastSearchHash = "";
function commitSearch(push) {
  S.view = "search"; S.page = ""; S.limit = PAGE_SIZE; S.sel = -1;
  const h = searchHash();
  lastSearchHash = h;
  const url = location.pathname + location.search + (h ? "#" + h : "");
  if (push) history.pushState(null, "", url); else history.replaceState(null, "", url);
  render();
}

function pageHref(path, anchor) {
  return "#page=" + encodeURIComponent(path) + (anchor ? "&a=" + encodeURIComponent(anchor) : "");
}

// ---------- rendering ----------

function render() {
  $("#results").hidden = S.view !== "search";
  $("#toolbar").hidden = S.view !== "search";
  $("#page").hidden = S.view !== "page";
  $("#kits").hidden = S.view !== "kits";
  const r = search();
  renderFacets(r);
  renderTree(r);
  if (S.view === "search") renderResults(r);
  else if (S.view === "page") renderPage();
  else renderKits();
}

function renderFacets(r) {
  const html = [];
  for (const fd of FACETS) {
    const counts = new Map();
    for (const e of r.base) {
      if (!passes(e, fd.key, r.cset)) continue;
      for (const v of fd.vals(e)) counts.set(v, (counts.get(v) || 0) + 1);
    }
    const sel = S.f[fd.key] || new Set();
    sel.forEach(v => { if (!counts.has(v)) counts.set(v, 0); });
    let vals = [...counts.keys()];
    if (fd.order) vals.sort((a, b) => fd.order.indexOf(a) - fd.order.indexOf(b));
    else vals.sort((a, b) => counts.get(b) - counts.get(a) || a.localeCompare(b));
    if (!vals.length) continue;
    const open = S.expanded.has(fd.key);
    const visible = open ? vals : vals.slice(0, FACET_COLLAPSED).concat(vals.slice(FACET_COLLAPSED).filter(v => sel.has(v)));
    html.push(`<section class="facet"><h3>${fd.title}</h3>`);
    for (const v of visible) {
      const label = DOC_KINDS[v] || v;
      html.push(`<label class="${counts.get(v) ? "" : "zero"}"><input type="checkbox" data-facet="${fd.key}" value="${esc(v)}" ${sel.has(v) ? "checked" : ""}> ${esc(label)}<span class="n">${counts.get(v)}</span></label>`);
    }
    if (vals.length > FACET_COLLAPSED) html.push(`<button class="link-btn more" data-expand="${fd.key}">${open ? "fewer" : `all ${vals.length}`}</button>`);
    html.push("</section>");
  }
  $("#facets").innerHTML = html.join("");
}

function renderTree(r) {
  const pool = r.base.filter(e => passes(e, null, null) && e.c);
  const total = id => {
    const cs = conceptSet(id);
    return pool.reduce((n, e) => n + (e.c.some(c => cs.has(c)) ? 1 : 0), 0);
  };
  const emit = parent => {
    const kids = children.get(parent) || [];
    if (!kids.length) return "";
    return "<ul>" + kids.map(id => {
      const c = byId.get(id);
      return `<li><div data-concept="${esc(id)}" class="${S.concept === id ? "on" : ""}" title="${esc(c.s)}">${esc(c.n)}<span class="n">${total(id)}</span></div>${emit(id)}</li>`;
    }).join("") + "</ul>";
  };
  $("#tree").innerHTML = emit("");
}

function fmtStars(n) {
  return typeof n === "number" ? n.toLocaleString("en-US") : "";
}

function kindBadge(e) {
  const cls = e.isDoc || e.k === "guide" ? "k-doc-card" : "k-" + e.k;
  return `<span class="kind ${cls}">${esc(DOC_KINDS[e.k] || e.k)}</span>`;
}

function metaLine(e) {
  const bits = [];
  if (typeof e.st === "number") bits.push(`<span title="GitHub stars">&#9733; ${fmtStars(e.st)}</span>`);
  if (e.lg) bits.push(esc(e.lg));
  if (e.l) bits.push(`<span title="license">${esc(e.l)}</span>`);
  if (e.pu) bits.push(`pushed ${esc(e.pu)}`);
  if (e.ar) bits.push(`<span class="fit-low">archived</span>`);
  if (e.f) bits.push(`<span class="fit-${e.f}">fit: ${esc(e.f)}</span>`);
  if (e.m) bits.push(esc(e.m));
  if (e.y) bits.push(esc(e.y));
  if (e.lv) bits.push(esc(e.lv));
  if (e.d) bits.push(esc(e.d.join(", ")));
  if (e.vs) bits.push(`<span class="badge ${e.vs}">${VERIFY_LABEL[e.vs]}</span>`);
  return bits.length ? `<div class="meta">${bits.map(b => b.startsWith("<span") ? b : `<span>${b}</span>`).join("")}</div>` : "";
}

function trim(s, n) {
  s = s || "";
  return s.length > n ? s.slice(0, n).replace(/\s+\S*$/, "") + "..." : s;
}

function card(e, i) {
  const chips = (e.c || []).map(c => byId.get(c)).filter(Boolean)
    .map(c => `<button class="chip" data-concept="${esc(c.i)}">${esc(c.n)}</button>`).join("");
  const links = [`<a href="${pageHref(e.p)}">${e.isDoc ? "Read card" : e.k === "guide" ? "Read guide" : "Catalog page"}</a>`];
  if (e.u) links.push(`<a href="${esc(e.u)}" target="_blank" rel="noopener">Source</a>`);
  if (e.sd) links.push(`<a href="${pageHref(`samples/${e.sd}/README.md`)}">Sample README</a>`);
  for (const d of e.dd || []) links.push(`<a href="${pageHref(d)}">${esc(DOC_KINDS[kindOfDoc(d)] || "doc")}</a>`);
  if (e.ab && e.ab.length) links.push(`<span class="muted">about ${e.ab.length} node${e.ab.length > 1 ? "s" : ""}</span>`);
  links.push(`<button data-act="related">Related</button>`);
  links.push(`<button data-act="copy" title="Copy an MCP call for this node">Copy MCP</button>`);
  return `<article class="card${i === S.sel ? " sel" : ""}" role="listitem" data-x="${e.x}" data-i="${i}">
    <div class="card-head">${kindBadge(e)}<a class="title" href="${pageHref(e.p)}">${esc(e.n)}</a><span class="id">${esc(e.i)}</span></div>
    ${metaLine(e)}
    <p class="sum">${esc(trim(e.s, 320))}</p>
    ${chips ? `<div class="chips">${chips}</div>` : ""}
    <div class="actions">${links.join("")}</div>
    <div class="related" hidden></div>
  </article>`;
}

function kindOfDoc(path) {
  const e = byPage.get(path);
  return e ? e.k : "";
}

function renderResults(r) {
  shown = r.hits;
  $("#count").textContent = `${r.hits.length} result${r.hits.length === 1 ? "" : "s"}` + (S.q ? ` for "${S.q}"` : "");
  const pills = [];
  if (S.concept && byId.get(S.concept)) pills.push(`<button class="pill" data-clear-concept>${esc(byId.get(S.concept).n)} &times;</button>`);
  for (const fd of FACETS) (S.f[fd.key] || []).forEach(v => pills.push(`<button class="pill" data-unfacet="${fd.key}" data-v="${esc(v)}">${esc(DOC_KINDS[v] || v)} &times;</button>`));
  $("#active").innerHTML = pills.join("");
  if (!r.hits.length) {
    $("#results").innerHTML = `<div class="empty">No matches. Remove a filter or try fewer words.</div>`;
    return;
  }
  const page = r.hits.slice(0, S.limit);
  $("#results").innerHTML = page.map(card).join("") +
    (r.hits.length > S.limit ? `<button class="btn more-btn" id="moreBtn">Show ${Math.min(PAGE_SIZE, r.hits.length - S.limit)} more</button>` : "");
}

function relatedHtml(e) {
  const groups = new Map();
  const add = (rel, x) => { if (!groups.has(rel)) groups.set(rel, []); groups.get(rel).push(x); };
  (e.r || []).forEach(([t, rel]) => add(rel.replace(/_/g, " "), E[t]));
  (incoming.get(e.x) || []).forEach(([s, rel]) => add(rel === "deep dive" ? "described in" : `${rel.replace(/_/g, " ")} (from)`, E[s]));
  (e.ab || []).forEach(t => add("about", E[t]));
  if (e.k === "concept") (children.get(e.i) || []).forEach(k => add("sub-concept", byId.get(k)));
  if (!groups.size) return `<div class="muted">No graph edges for this node.</div>`;
  const out = [];
  for (const [rel, xs] of groups) {
    const uniq = [...new Map(xs.filter(Boolean).map(x => [x.x, x])).values()];
    out.push(`<h4>${esc(rel)} (${uniq.length})</h4><ul>` + uniq.map(x =>
      `<li><a href="${pageHref(x.p)}">${esc(x.n)}</a> <span class="muted">${esc(DOC_KINDS[x.k] || x.k)}</span></li>`).join("") + "</ul>");
  }
  return out.join("");
}

// ---------- page view ----------

let pageToken = 0;
async function renderPage() {
  const path = S.page;
  const token = ++pageToken;
  const e = byPage.get(path);
  $("#backLink").href = "#" + lastSearchHash;
  $("#rawLink").href = ROOT + path;
  $("#pageSide").innerHTML = e ? pageSide(e) : "";
  $("#pageBody").innerHTML = `<p class="muted">Loading ${esc(path)}...</p>`;
  let text;
  try {
    const res = await fetch(ROOT + path);
    if (!res.ok) throw new Error(res.status);
    text = await res.text();
  } catch (err) {
    if (token === pageToken) $("#pageBody").innerHTML = `<p>Could not fetch <code>${esc(path)}</code> (${esc(err.message)}).</p>`;
    return;
  }
  if (token !== pageToken) return;
  const body = $("#pageBody");
  if (window.marked && window.DOMPurify) {
    body.innerHTML = DOMPurify.sanitize(marked.parse(text, { gfm: true }));
    rewriteLinks(body, path);
  } else {
    body.innerHTML = `<p class="muted">Markdown renderer not loaded (CDN unreachable); showing raw text.</p><pre>${esc(text)}</pre>`;
  }
  document.title = (e ? e.n : path) + " - Navigation Index";
  if (S.anchor) {
    const t = document.getElementById(S.anchor);
    if (t) t.scrollIntoView();
  } else window.scrollTo(0, 0);
}

function pageSide(e) {
  const links = [];
  if (e.u) links.push(`<a href="${esc(e.u)}" target="_blank" rel="noopener">Source</a>`);
  if (e.sd) links.push(`<a href="${pageHref(`samples/${e.sd}/README.md`)}">Sample README</a>`);
  if (!e.isDoc && e.p !== S.page) links.push(`<a href="${pageHref(e.p)}">${e.k === "guide" ? "Read guide" : "Catalog page"}</a>`);
  links.push(`<button class="link-btn" data-copy-show="${esc(e.i)}">Copy MCP</button>`);
  return `<div class="box"><div class="card-head">${kindBadge(e)}<strong>${esc(e.n)}</strong></div>
    <div class="id muted">${esc(e.i)}</div>${metaLine(e)}<div class="actions">${links.join("")}</div></div>
    <div class="box related"><h3>Related</h3>${relatedHtml(e)}</div>`;
}

function slugify(s) {
  return s.toLowerCase().trim().replace(/[^\w\- ]+/g, "").replace(/ /g, "-");
}

function resolveRepoPath(base, href) {
  const u = new URL(href, "https://repo.invalid/" + base);
  if (u.host !== "repo.invalid") return null;
  return { path: decodeURIComponent(u.pathname.slice(1)), hash: decodeURIComponent(u.hash.slice(1)) };
}

function rewriteLinks(root, base) {
  root.querySelectorAll("h1,h2,h3,h4,h5,h6").forEach(h => { if (!h.id) h.id = slugify(h.textContent); });
  root.querySelectorAll("a[href]").forEach(a => {
    const href = a.getAttribute("href");
    if (/^[a-z][a-z0-9+.-]*:/i.test(href)) {
      a.target = "_blank"; a.rel = "noopener";
      return;
    }
    if (href.startsWith("#")) {
      a.href = pageHref(base, decodeURIComponent(href.slice(1)));
      return;
    }
    const r = resolveRepoPath(base, href);
    if (!r) return;
    if (r.path.endsWith(".md")) a.href = pageHref(r.path, r.hash);
    else if (r.path === "" || r.path.endsWith("/")) a.href = pageHref(r.path + "README.md");
    else { a.href = ROOT + r.path; a.target = "_blank"; a.rel = "noopener"; }
  });
  root.querySelectorAll("img[src]").forEach(img => {
    const src = img.getAttribute("src");
    if (/^[a-z][a-z0-9+.-]*:/i.test(src)) return;
    const r = resolveRepoPath(base, src);
    if (r) img.src = ROOT + r.path;
  });
}

// ---------- starter kits ----------

function renderKits() {
  const kits = E.filter(e => e.k === "sample").sort((a, b) =>
    Object.keys(VERIFY_LABEL).indexOf(a.vs) - Object.keys(VERIFY_LABEL).indexOf(b.vs) || a.n.localeCompare(b.n));
  const tally = kits.reduce((m, k) => (m[k.vs] = (m[k.vs] || 0) + 1, m), {});
  $("#kits").innerHTML = `<div class="kits-head"><h2>Starter kits</h2>
    <p class="muted">The ${kits.length} samples under <code>samples/</code>. The badge is derived from the <code>verified</code> text in each
    <code>sample.json</code> (${Object.entries(tally).map(([k, v]) => `${v} ${VERIFY_LABEL[k]}`).join(", ")}); read the full text, it says what was run, on what, and what was not.</p></div>
    <div class="results">` + kits.map(k => {
      const rel = (k.r || []).map(([t, rel]) => E[t]).filter(x => x.k === "repo").slice(0, 8)
        .map(x => `<a href="${pageHref(x.p)}">${esc(x.n)}</a>`).join(", ");
      return `<article class="card kit">
        <div class="card-head"><span class="badge ${k.vs}">${VERIFY_LABEL[k.vs]}</span><a class="title" href="${pageHref(`samples/${k.sd}/README.md`)}">${esc(k.n)}</a><span class="id">${esc(k.i)}</span></div>
        <p class="sum">${esc(trim(k.s, 360))}</p>
        <div class="verify"><strong>Verification:</strong> ${esc(k.v)}</div>
        ${rel ? `<div class="meta">Uses / explains: ${rel}</div>` : ""}
        <div class="actions"><a href="${pageHref(`samples/${k.sd}/README.md`)}">README</a><a href="${pageHref(k.p)}">Catalog page</a><a href="${ROOT}samples/${esc(k.sd)}/" target="_blank" rel="noopener">Files</a></div>
      </article>`;
    }).join("") + "</div>";
}

// ---------- copy ----------

function single(key, mcpKey) {
  const s = S.f[key];
  return s && s.size === 1 ? { [mcpKey]: [...s][0] } : {};
}

function mcpSearch() {
  if (!S.q && !S.concept) return null;
  const args = { ...single("kind", "kind"), ...single("fit", "fit"), ...single("domain", "domain") };
  if (!S.q) return { tool: "concept", arguments: { id: S.concept, ...args } };
  return { tool: "search", arguments: { query: S.q, ...(S.concept ? { concept: S.concept } : {}), ...args } };
}

function cliSearch() {
  const m = mcpSearch();
  if (!m) return null;
  const a = m.arguments;
  const flags = ["kind", "fit", "domain"].filter(k => a[k]).map(k => ` --${k} ${a[k]}`).join("");
  if (m.tool === "concept") return `python3 tools/query.py concept ${a.id}${flags}`;
  return `python3 tools/query.py search ${JSON.stringify(a.query)}${a.concept ? ` --concept ${a.concept}` : ""}${flags}`;
}

async function copy(text) {
  try {
    await navigator.clipboard.writeText(text);
  } catch (err) {
    const ta = document.createElement("textarea");
    ta.value = text; document.body.appendChild(ta); ta.select();
    try { document.execCommand("copy"); } catch (e2) { /* clipboard unavailable */ }
    ta.remove();
  }
  toast("Copied: " + trim(text, 90));
}

let toastTimer;
function toast(msg) {
  const t = $("#toast");
  t.textContent = msg; t.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove("show"), 1800);
}

function copyShow(id) {
  const e = byId.get(id);
  if (e && e.isDoc) copy(e.p);
  else copy(JSON.stringify({ tool: "show", arguments: { id } }));
}

function dropped() {
  const multi = FACETS.filter(fd => S.f[fd.key] && (S.f[fd.key].size > 1 || !["kind", "fit", "domain"].includes(fd.key)));
  return multi.length ? ` (not expressible there: ${multi.map(fd => fd.title).join(", ")})` : "";
}

// ---------- interaction ----------

function selectCard(i) {
  const cards = [...document.querySelectorAll("#results .card")];
  if (!cards.length) return;
  S.sel = Math.max(0, Math.min(cards.length - 1, i));
  cards.forEach((c, j) => c.classList.toggle("sel", j === S.sel));
  cards[S.sel].scrollIntoView({ block: "nearest" });
}

function selectedEntry() {
  const c = document.querySelectorAll("#results .card")[S.sel];
  return c ? [c, E[+c.dataset.x]] : [null, null];
}

function toggleRelated(cardEl, e) {
  const box = cardEl.querySelector(".related");
  if (box.hidden) box.innerHTML = relatedHtml(e);
  box.hidden = !box.hidden;
}

function setTheme() {
  const cur = document.documentElement.dataset.theme ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("navidx-theme", next); } catch (err) { /* storage blocked */ }
}

function toggleConcept(id) {
  S.concept = S.concept === id ? "" : id;
  closeSide();
  commitSearch(true);
}

function closeSide() {
  $("#side").classList.remove("open");
  $("#filtersBtn").setAttribute("aria-expanded", "false");
}

let qTimer;
$("#q").addEventListener("input", () => {
  clearTimeout(qTimer);
  qTimer = setTimeout(() => { S.q = $("#q").value.trim(); commitSearch(false); }, 80);
});
$("#q").addEventListener("keydown", ev => {
  if (ev.key === "ArrowDown" || ev.key === "Enter") {
    ev.preventDefault();
    if (S.view !== "search") { S.q = $("#q").value.trim(); commitSearch(true); }
    $("#q").blur();
    selectCard(0);
  } else if (ev.key === "Escape") {
    if ($("#q").value) { $("#q").value = ""; S.q = ""; commitSearch(false); } else $("#q").blur();
  }
});

document.addEventListener("change", ev => {
  const t = ev.target;
  if (!t.dataset.facet) return;
  const set = S.f[t.dataset.facet] || (S.f[t.dataset.facet] = new Set());
  if (t.checked) set.add(t.value); else set.delete(t.value);
  commitSearch(true);
});

document.addEventListener("click", ev => {
  const t = ev.target.closest("button, [data-concept]");
  if (!t) return;
  if (t.dataset.concept) return toggleConcept(t.dataset.concept);
  if (t.dataset.expand) {
    S.expanded.has(t.dataset.expand) ? S.expanded.delete(t.dataset.expand) : S.expanded.add(t.dataset.expand);
    return render();
  }
  if (t.dataset.unfacet) { S.f[t.dataset.unfacet].delete(t.dataset.v); return commitSearch(true); }
  if (t.hasAttribute("data-clear-concept")) { S.concept = ""; return commitSearch(true); }
  if (t.dataset.copyShow) return copyShow(t.dataset.copyShow);
  if (t.dataset.act) {
    const c = t.closest(".card"), e = E[+c.dataset.x];
    S.sel = +c.dataset.i;
    if (t.dataset.act === "related") toggleRelated(c, e);
    else copyShow(e.i);
    return;
  }
  if (t.id === "moreBtn") { S.limit += PAGE_SIZE; return renderResults(search()); }
});

$("#clearBtn").onclick = () => { S.f = {}; S.concept = ""; S.q = ""; $("#q").value = ""; commitSearch(true); };
$("#themeBtn").onclick = setTheme;
$("#helpBtn").onclick = () => { $("#help").hidden = false; };
$("#helpClose").onclick = () => { $("#help").hidden = true; };
$("#help").onclick = ev => { if (ev.target.id === "help") $("#help").hidden = true; };
$("#filtersBtn").onclick = () => {
  const open = $("#side").classList.toggle("open");
  $("#filtersBtn").setAttribute("aria-expanded", String(open));
};
$("#copyMcp").onclick = () => {
  const m = mcpSearch();
  if (!m) return toast("Type a query or pick a concept first");
  copy(JSON.stringify(m));
  const d = dropped();
  if (d) setTimeout(() => toast("Copied MCP call" + d), 1900);
};
$("#copyCli").onclick = () => {
  const c = cliSearch();
  if (!c) return toast("Type a query or pick a concept first");
  copy(c);
};

window.addEventListener("hashchange", () => {
  readHash();
  if (S.view === "search") { lastSearchHash = searchHash(); S.sel = -1; S.limit = PAGE_SIZE; }
  render();
});

document.addEventListener("keydown", ev => {
  const typing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement.tagName);
  if (typing || ev.metaKey || ev.ctrlKey || ev.altKey) return;
  if (!$("#help").hidden) { if (ev.key === "Escape" || ev.key === "?") $("#help").hidden = true; return; }
  const k = ev.key;
  if (k === "/") { ev.preventDefault(); $("#q").focus(); $("#q").select(); return; }
  if (k === "?") { $("#help").hidden = false; return; }
  if (k === "t") return setTheme();
  if (k === "s") { location.hash = "view=kits"; return; }
  if (k === "Escape") {
    if ($("#side").classList.contains("open")) return closeSide();
    if (S.view !== "search") { location.hash = lastSearchHash; return; }
    return;
  }
  if (S.view !== "search") return;
  if (k === "j" || k === "ArrowDown") { ev.preventDefault(); selectCard(S.sel + 1); }
  else if (k === "k" || k === "ArrowUp") { ev.preventDefault(); if (S.sel <= 0) { $("#q").focus(); } else selectCard(S.sel - 1); }
  else {
    const [c, e] = selectedEntry();
    if (!e) return;
    if (k === "Enter") location.hash = pageHref(e.p).slice(1);
    else if (k === "o" && e.u) window.open(e.u, "_blank", "noopener");
    else if (k === "r") toggleRelated(c, e);
    else if (k === "c") copyShow(e.i);
  }
});

load();
