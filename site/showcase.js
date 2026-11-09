"use strict";
// Showcase page: live counters from data/index.json, arena replays from data/showcase/replays/,
// sample cards from samples/*/sample.json (+ samples/_meta_overrides.json). No dependencies.

const ROOT = "../";
const INDEX_URL = "data/index.json";
const REPLAY_DIR = "data/showcase/replays/";
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const $ = s => document.querySelector(s);
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const getJSON = async url => { const r = await fetch(url); if (!r.ok) throw new Error(r.status + " " + url); return r.json(); };

// ---------- theme (same key as app.js) ----------
function toggleTheme() {
  const cur = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("navidx-theme", next); } catch (err) { /* storage blocked */ }
  draw();
}
$("#themeBtn").onclick = toggleTheme;
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => draw());

// ---------- counters ----------
function countUp(el, target) {
  if (REDUCED) { el.textContent = target.toLocaleString("en-US"); return; }
  let k = 0; const n = 40; // 40 steps x 25 ms, timers so it also finishes in background tabs
  const step = () => {
    k++; const e = 1 - Math.pow(1 - k / n, 3);
    el.textContent = Math.round(target * e).toLocaleString("en-US");
    if (k < n) setTimeout(step, 25);
  };
  step();
}

async function loadIndex() {
  try {
    const data = await getJSON(INDEX_URL);
    const counts = {};
    for (const n of data.nodes) counts[n.k] = (counts[n.k] || 0) + 1;
    document.querySelectorAll(".counter .num").forEach(el => countUp(el, counts[el.dataset.k] || 0));
    const docs = (data.docs || []).length;
    $("#counterNote").innerHTML = `Counted live from <code>site/data/index.json</code>: ${data.nodes.length.toLocaleString("en-US")} records in all, plus ${docs} deep-dive docs (integration cards, dataset cards, paper digests).`;
    return data;
  } catch (err) {
    $("#counterNote").textContent = `Could not load ${INDEX_URL} (${err.message}). Serve the repo root with python3 -m http.server.`;
    return null;
  }
}

// ---------- arena replay ----------
const R = { runs: [], cur: null, t: 0, playing: !REDUCED, speed: 4, last: 0, touched: false, advanceTimer: 0 };
const cv = $("#arenaCanvas"), ctx = cv.getContext("2d");
const sp = $("#spark"), sctx = sp.getContext("2d");
const OUT_LABEL = { reached: "reached B", stuck: "stuck", collision: "collision", timeout: "timeout" };

function fitCanvas(c) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2), w = c.clientWidth, h = c.clientHeight;
  if (!w || !h) return 1;
  if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
  return dpr;
}

function idxAt(arr, t) { // last index with arr[i] <= t
  let lo = 0, hi = arr.length - 1;
  if (t >= arr[hi]) return hi;
  while (lo < hi) { const m = (lo + hi + 1) >> 1; if (arr[m] <= t) lo = m; else hi = m - 1; }
  return lo;
}

function drawArena() {
  const run = R.cur; if (!run) return;
  const dpr = fitCanvas(cv), W = cv.width, H = cv.height;
  const [x0, y0, x1, y1] = run.area, pad = 0.5;
  const s = Math.min(W / (x1 - x0 + 2 * pad), H / (y1 - y0 + 2 * pad));
  const P = (x, y) => [(x - x0 + pad) * s, (y1 + pad - y) * s];
  const C = { bg: css("--panel"), fg: css("--fg"), muted: css("--muted"), line: css("--line"), accent: css("--accent"),
    obst: css("--obst"), est: css("--est"), ok: css("--ok"), bad: css("--bad"), warn: css("--warn"), dark: css("--dark-zone"), okbg: css("--ok-bg") };
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);

  // 5 m grid
  ctx.strokeStyle = C.line; ctx.lineWidth = 1 * dpr;
  for (let g = Math.ceil(x0 / 5) * 5; g <= x1; g += 5) { const [a] = P(g, 0); ctx.beginPath(); ctx.moveTo(a, P(0, y1)[1]); ctx.lineTo(a, P(0, y0)[1]); ctx.stroke(); }
  for (let g = Math.ceil(y0 / 5) * 5; g <= y1; g += 5) { const [, b] = P(0, g); ctx.beginPath(); ctx.moveTo(P(x0, 0)[0], b); ctx.lineTo(P(x1, 0)[0], b); ctx.stroke(); }

  // dark zones
  for (const [zx0, zy0, zx1, zy1] of run.dark_zones || []) {
    const [a, b] = P(zx0, zy1), [c, d] = P(zx1, zy0);
    ctx.fillStyle = C.dark; ctx.fillRect(a, b, c - a, d - b);
    ctx.setLineDash([4 * dpr, 4 * dpr]); ctx.strokeStyle = C.muted; ctx.strokeRect(a, b, c - a, d - b); ctx.setLineDash([]);
  }

  // obstacles and walls
  ctx.fillStyle = C.obst;
  for (const [cx, cy, hx, hy] of run.boxes) { const [a, b] = P(cx - hx, cy + hy); ctx.fillRect(a, b, 2 * hx * s, 2 * hy * s); }
  for (const [cx, cy, r] of run.cylinders) { const [a, b] = P(cx, cy); ctx.beginPath(); ctx.arc(a, b, r * s, 0, 2 * Math.PI); ctx.fill(); }
  { const [a, b] = P(x0, y1); ctx.strokeStyle = C.obst; ctx.lineWidth = 4 * dpr; ctx.strokeRect(a, b, (x1 - x0) * s, (y1 - y0) * s); }

  const end = run.t[run.t.length - 1], done = R.t >= end - 1e-6;
  const i = idxAt(run.t, R.t);

  // A and B
  const [ax, ay] = P(run.a[0], run.a[1]), [bx, by] = P(run.b[0], run.b[1]);
  const tol = Math.max(run.goal_tol_m * s, 6 * dpr);
  ctx.fillStyle = C.ok; ctx.beginPath(); ctx.arc(ax, ay, tol, 0, 2 * Math.PI); ctx.fill();
  ctx.lineWidth = 3 * dpr; ctx.strokeStyle = C.bad; ctx.beginPath(); ctx.arc(bx, by, tol, 0, 2 * Math.PI); ctx.stroke();
  if (done && run.score.outcome === "reached") { ctx.fillStyle = C.ok; ctx.beginPath(); ctx.arc(bx, by, tol, 0, 2 * Math.PI); ctx.fill(); }
  ctx.fillStyle = C.fg; ctx.font = `700 ${13 * dpr}px system-ui, sans-serif`; ctx.textBaseline = "middle";
  ctx.fillText("A", ax + tol + 4 * dpr, ay - tol);
  ctx.fillText("B", bx - 4 * dpr, by - tol - 10 * dpr);

  // estimated path (what the planner believed)
  if (run.est) {
    const j = idxAt(run.est.map(r => r[0]), R.t);
    ctx.strokeStyle = C.est; ctx.lineWidth = 2.2 * dpr; ctx.setLineDash([6 * dpr, 5 * dpr]); ctx.beginPath();
    for (let k = 0; k <= j; k++) { const [px, py] = P(run.est[k][1], run.est[k][2]); k ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
    ctx.stroke(); ctx.setLineDash([]);
    const e = run.est[j], [ex, ey] = P(e[1], e[2]);
    ctx.globalAlpha = 0.18; ctx.fillStyle = C.est; ctx.beginPath(); ctx.arc(ex, ey, Math.max(2 * e[3] * s, 3 * dpr), 0, 2 * Math.PI); ctx.fill(); ctx.globalAlpha = 1;
    ctx.fillStyle = C.est; ctx.beginPath(); ctx.arc(ex, ey, 4 * dpr, 0, 2 * Math.PI); ctx.fill();
  }

  // truth path
  ctx.strokeStyle = C.accent; ctx.lineWidth = 3 * dpr; ctx.lineJoin = "round"; ctx.beginPath();
  for (let k = 0; k <= i; k++) { const [px, py] = P(run.truth[k][0], run.truth[k][1]); k ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
  ctx.stroke();

  // fault marker
  const fl = run.fault_log;
  if (fl && fl.fired_t != null && R.t >= fl.fired_t) {
    const k = idxAt(run.t, fl.fired_t), [fx, fy] = P(run.truth[k][0], run.truth[k][1]);
    ctx.strokeStyle = C.bad; ctx.lineWidth = 2 * dpr; ctx.beginPath(); ctx.arc(fx, fy, 9 * dpr, 0, 2 * Math.PI); ctx.stroke();
    ctx.fillStyle = C.bad; ctx.font = `700 ${12 * dpr}px system-ui, sans-serif`;
    ctx.fillText(`${fl.step_m} m jump`, fx + 12 * dpr, fy - 10 * dpr);
  }

  // vehicle
  const [vx, vy] = P(run.truth[i][0], run.truth[i][1]);
  ctx.fillStyle = C.accent; ctx.strokeStyle = C.bg; ctx.lineWidth = 2 * dpr;
  ctx.beginPath(); ctx.arc(vx, vy, Math.max(run.radius * s, 5 * dpr), 0, 2 * Math.PI); ctx.fill(); ctx.stroke();
  if (done && run.score.outcome !== "reached") {
    ctx.strokeStyle = run.score.outcome === "collision" ? C.bad : C.warn; ctx.lineWidth = 3 * dpr;
    ctx.beginPath(); ctx.arc(vx, vy, 14 * dpr, 0, 2 * Math.PI); ctx.stroke();
  }

  // scale bar
  ctx.fillStyle = C.muted; ctx.font = `${11 * dpr}px system-ui, sans-serif`;
  const [sx, sy] = P(x0 + 0.3, y0 - 0.32);
  ctx.font = `${10 * dpr}px system-ui, sans-serif`;
  ctx.fillRect(sx, sy - 1 * dpr, 5 * s, 2 * dpr); ctx.fillText("5 m", sx + 5 * s + 5 * dpr, sy + 1 * dpr);
}

function drawSpark() {
  const run = R.cur; if (!run) return;
  const dpr = fitCanvas(sp), W = sp.width, H = sp.height, pad = 4 * dpr;
  const T = run.t[run.t.length - 1] || 1, cmax = Math.max(1, ...run.clearance) * 1.05;
  const X = t => pad + (t / T) * (W - 2 * pad), Y = c => H - pad - (Math.max(0, c) / cmax) * (H - 2 * pad);
  sctx.setTransform(1, 0, 0, 1, 0, 0); sctx.clearRect(0, 0, W, H);
  sctx.strokeStyle = css("--bad"); sctx.lineWidth = 1.5 * dpr; sctx.setLineDash([4 * dpr, 3 * dpr]);
  sctx.beginPath(); sctx.moveTo(pad, Y(run.radius)); sctx.lineTo(W - pad, Y(run.radius)); sctx.stroke(); sctx.setLineDash([]);
  const line = (upto, color, w) => {
    sctx.strokeStyle = color; sctx.lineWidth = w * dpr; sctx.beginPath();
    for (let k = 0; k <= upto; k++) { const x = X(run.t[k]), y = Y(run.clearance[k]); k ? sctx.lineTo(x, y) : sctx.moveTo(x, y); }
    sctx.stroke();
  };
  line(run.t.length - 1, css("--line"), 1.5);
  const i = idxAt(run.t, R.t);
  line(i, css("--accent"), 2);
  sctx.fillStyle = css("--accent"); sctx.beginPath(); sctx.arc(X(run.t[i]), Y(run.clearance[i]), 3.5 * dpr, 0, 2 * Math.PI); sctx.fill();
  $("#clearNow").textContent = run.clearance[i].toFixed(2) + " m";
}

function updateHud() {
  const run = R.cur; if (!run) return;
  const end = run.t[run.t.length - 1], done = R.t >= end - 1e-6, o = run.score.outcome;
  const b = $("#badge");
  b.className = "badge " + (done ? o : "flying");
  b.textContent = done ? OUT_LABEL[o] || o : "flying";
  $("#clock").textContent = R.t.toFixed(1) + " s";
  $("#scrub").value = Math.round((R.t / end) * 1000);
  $("#playBtn").textContent = R.playing ? "Pause" : done ? "Replay" : "Play";
}

function draw() { drawArena(); drawSpark(); updateHud(); }

function fmt(v, unit) { return v == null ? "-" : `${v} ${unit}`; }

function selectRun(k) {
  R.cur = R.runs[k]; R.t = REDUCED ? R.cur.t[R.cur.t.length - 1] : 0;
  document.querySelectorAll(".run-btn").forEach((b, j) => b.setAttribute("aria-selected", String(j === k)));
  const run = R.cur, sc = run.score;
  $("#runTitle").textContent = run.title;
  $("#runNote").textContent = run.note;
  const rows = [
    ["Outcome", OUT_LABEL[sc.outcome] || sc.outcome],
    ["Planner", run.planner + (run.case !== "truth" ? ` on EKF, fault "${run.case}"` : ", true pose")],
    ["Layout", `${run.family} #${run.index}, seed ${run.seed}, ${sc.n_obstacles} obstacles`],
    ["Time to goal", fmt(sc.time_to_goal_s, "s")],
    ["Run ended at", fmt(sc.duration_s, "s")],
    ["Min clearance", fmt(sc.min_clearance_m, "m")],
    ["Path length", fmt(sc.path_length_m, "m")],
  ];
  if (run.est) rows.push(["Max pose error", fmt(sc.max_pose_error_m, "m")]);
  rows.push(["Input", "synthetic (simulated)"]);
  $("#stats").innerHTML = rows.map(([a, b]) => `<dt>${esc(a)}</dt><dd>${esc(b)}</dd>`).join("");
  $("#replaySrc").innerHTML = `Data: <a href="${REPLAY_DIR}${esc(run.name)}.json">${esc(run.name)}.json</a>, written by <code>export_replay.py</code> (${esc(run.env.system)} ${esc(run.env.machine)}, Python ${esc(run.env.python)}, numpy ${esc(run.env.numpy)}). Stuck = moved under 0.2 m in 10 s.`;
  draw();
}

function tick(now) {
  const run = R.cur;
  if (run && R.playing) {
    const dt = Math.min(0.1, (now - (R.last || now)) / 1000);
    const end = run.t[run.t.length - 1];
    R.t = Math.min(end, R.t + dt * R.speed);
    if (R.t >= end) {
      R.playing = false;
      if (!R.touched) R.advanceTimer = setTimeout(() => { if (!R.touched) { selectRun((R.runs.indexOf(R.cur) + 1) % R.runs.length); R.playing = true; } }, 2500);
    }
    draw();
  }
  R.last = now;
  requestAnimationFrame(tick);
}

function touch() { R.touched = true; clearTimeout(R.advanceTimer); }

async function loadReplays() {
  try {
    const list = await getJSON(REPLAY_DIR + "index.json");
    R.runs = await Promise.all(list.runs.map(r => getJSON(REPLAY_DIR + r.file)));
  } catch (err) {
    $("#runPicker").innerHTML = `<p class="muted">No replays (${esc(err.message)}). Run <code>.venv/bin/python export_replay.py</code> in samples/close-area-arena.</p>`;
    return;
  }
  $("#runPicker").innerHTML = R.runs.map((r, k) =>
    `<button class="run-btn" role="tab" data-k="${k}" aria-selected="false"><span class="dot ${esc(r.score.outcome)}"></span>${esc(r.title)}</button>`).join("");
  document.querySelectorAll(".run-btn").forEach(b => b.onclick = () => { touch(); R.playing = !REDUCED; selectRun(+b.dataset.k); });
  $("#playBtn").onclick = () => {
    touch();
    const end = R.cur.t[R.cur.t.length - 1];
    if (!R.playing && R.t >= end - 1e-6) R.t = 0;
    R.playing = !R.playing; updateHud();
  };
  $("#speedSel").onchange = e => { R.speed = +e.target.value; };
  $("#scrub").oninput = e => { touch(); R.playing = false; R.t = (+e.target.value / 1000) * R.cur.t[R.cur.t.length - 1]; draw(); };
  const first = Math.min(R.runs.length - 1, Math.max(0, parseInt(new URLSearchParams(location.search).get("run"), 10) || 0));
  selectRun(first);
  requestAnimationFrame(tick);
}
window.addEventListener("resize", () => draw());

// ---------- sample gallery ----------
const INPUT_LABEL = { real: "real data", mixed: "mixed real + sim", sitl: "SITL", synthetic: "synthetic" };
const INPUT_ORDER = ["real", "mixed", "sitl", "synthetic"];
const G = { cards: [], filter: "all", all: false, limit: matchMedia("(max-width: 640px)").matches ? 4 : 9 };

function krHtml(md) { // markdown links => text, `code` kept, bold dropped
  let s = esc(String(md).replace(/\[([^\]]+)\]\([^)]+\)/g, "$1").replace(/\*\*([^*]+)\*\*/g, "$1"));
  return s.replace(/`([^`]+)`/g, "<code>$1</code>");
}

function renderGallery() {
  const counts = { all: G.cards.length };
  for (const c of G.cards) counts[c.input] = (counts[c.input] || 0) + 1;
  const keys = ["all", ...INPUT_ORDER.filter(k => counts[k]), ...(counts.unstated ? ["unstated"] : [])];
  $("#inputChips").innerHTML = keys.map(k =>
    `<button class="chip" data-f="${k}" aria-pressed="${G.filter === k}">${k === "all" ? "All" : k === "unstated" ? "input not stated" : INPUT_LABEL[k]} <span class="muted">${counts[k]}</span></button>`).join("");
  document.querySelectorAll(".chip").forEach(b => b.onclick = () => { G.filter = b.dataset.f; renderGallery(); });
  const match = G.cards.filter(c => G.filter === "all" || c.input === G.filter);
  const shown = G.all ? match : match.slice(0, G.limit);
  const btn = $("#moreBtn");
  btn.hidden = shown.length >= match.length;
  btn.textContent = `Show all ${match.length}`;
  btn.onclick = () => { G.all = true; renderGallery(); };
  $("#gallery").innerHTML = shown.map(c => `
    <a class="card" href="index.html#page=${encodeURIComponent("samples/" + c.dir + "/README.md")}">
      <div class="row"><span class="badge ${esc(c.status)}">${esc(c.status)}</span><span class="badge ${esc(c.input)}">${esc(c.input === "unstated" ? "input not stated" : INPUT_LABEL[c.input] || c.input)}</span></div>
      <h3>${esc(c.dir)}</h3>
      ${c.group ? `<div class="group">${esc(c.group)}</div>` : ""}
      <p class="shows">${esc(c.shows)}</p>
      <p class="kr">${krHtml(c.key)}</p>
      <span class="more">README =&gt;</span>
    </a>`).join("") || `<p class="muted">No samples match.</p>`;
}

async function loadGallery(index) {
  if (!index) { $("#gallery").innerHTML = `<p class="muted">Needs data/index.json.</p>`; return; }
  const nodes = index.nodes.filter(n => n.k === "sample" && n.sd);
  let over = {};
  try { over = await getJSON(ROOT + "samples/_meta_overrides.json"); } catch (err) { /* optional sidecar */ }
  const metas = await Promise.all(nodes.map(n => getJSON(`${ROOT}samples/${n.sd}/sample.json`).catch(() => ({}))));
  const groupRank = g => (/close-area/i.test(g || "") ? 0 : 1);
  G.cards = nodes.map((n, k) => {
    const m = Object.assign({}, over[n.sd] || {}, metas[k]);
    const inp = String(m.input || "").toLowerCase();
    return { dir: n.sd, status: m.verified_status || n.vs || "unknown", input: INPUT_LABEL[inp] ? inp : "unstated",
      group: m.group || "", shows: m.shows || n.n, key: m.key_result };
  }).filter(c => c.key)
    .sort((a, b) => groupRank(a.group) - groupRank(b.group) || INPUT_ORDER.indexOf(a.input) - INPUT_ORDER.indexOf(b.input) || a.dir.localeCompare(b.dir));
  renderGallery();
  // the gallery changes the page height, so redo the #anchor jump the browser made before it loaded
  const target = location.hash && document.getElementById(location.hash.slice(1));
  if (target && target.id !== "hero") target.scrollIntoView({ behavior: "instant" });
}

loadReplays();
loadIndex().then(loadGallery);
