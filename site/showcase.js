"use strict";
// Showcase page: live counters from data/index.json, arena replays from data/showcase/replays_v2/
// (+ the v1 runs in data/showcase/replays/), results grid from samples/close-area-benchmark/results/matrix_0.md,
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
// v2: data/showcase/replays_v2/ (close-area-replay-index/2, 8 families x 9 planners, each replay embeds
// its world as close-area-world/1). v1: data/showcase/replays/ (4 runs, incl. a drifting EKF), kept as
// the "Pose faults (v1)" tile because v2 flies every run on the true pose.
const V2_DIR = "data/showcase/replays_v2/";
const MATRIX_URL = ROOT + "samples/close-area-benchmark/results/matrix_0.md";
const LEGACY = "pose_faults";
const DEFAULT = { family: "office", planner: "astar_known" };
// Family blurbs paraphrase samples/close-area-arena/README.md (world.py and worlds_complex.py tables).
const FAMILY_INFO = {
  random: ["Clutter", "8-15 boxes and cylinders"],
  u_trap: ["U trap", "a cup on the A-B line, opening towards A, plus clutter"],
  narrow_gap: ["Narrow gap", "a wall across the area with one 0.5-0.9 m gap"],
  office: ["Office", "a corridor, 3-6 rooms, one 0.8-1.0 m doorway each, A and B in different rooms"],
  warehouse: ["Warehouse", "shelf rows, 1.2-1.6 m aisles, pallets, A bottom aisle, B top aisle"],
  forest: ["Forest", "40-90 poles with 0.3-0.6 m tight spots"],
  maze: ["Maze", "10 x 10 cells of 2 m, a few walls removed for loops"],
  glass_office: ["Glass office", "an office with 1-3 glass panels across the corridor"],
  [LEGACY]: ["Pose faults (v1)", "the first four replays, one on a drifting EKF with a 0.5 m position jump"],
};
// Preset text from samples/close-area-benchmark/README.md.
const PRESET_INFO = { ideal: "ideal (72 rays, 360 deg, 6 m, sees glass)", crazyflie: "crazyflie (4 cone beams of 27 deg, 3 m, glass invisible)" };
const OUT_LABEL = { reached: "reached B", stuck: "stuck", collision: "collision", timeout: "timeout" };
const R = { fams: [], famByKey: {}, cache: new Map(), fam: null, a: null, b: null, view: "overlay",
  t: 0, playing: !REDUCED, speed: 4, last: 0, touched: false, pinned: false, advanceTimer: 0, seq: 0,
  preset: null, matrix: null };
const cv = $("#arenaCanvas"), cvB = $("#arenaCanvasB"), sp = $("#spark"), sctx = sp.getContext("2d");

function fitCanvas(c) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2), w = c.clientWidth, h = c.clientHeight;
  if (!w || !h) return 0;
  if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
  return dpr;
}

function idxAt(arr, t) { // last index with arr[i] <= t
  let lo = 0, hi = arr.length - 1;
  if (t >= arr[hi]) return hi;
  while (lo < hi) { const m = (lo + hi + 1) >> 1; if (arr[m] <= t) lo = m; else hi = m - 1; }
  return lo;
}
const endOf = run => (run ? run.t[run.t.length - 1] : 0);
const endAll = () => Math.max(endOf(R.a), endOf(R.b));
const worldKey = run => `${run.world.family}/${run.world.seed}/${run.world.index}`;
const famName = k => (FAMILY_INFO[k] || [k])[0];
function fmt(v, unit) { return v == null ? "-" : `${v} ${unit}`; }

// ----- normalise both replay formats to one shape -----
function normV2(d, file) {
  return { key: d.planner, planner: d.planner, label: d.label, world: d.world, preset: d.preset, t: d.t, truth: d.truth,
    clearance: d.clearance, est: d.est || null, dark: [], fault: null, score: d.score, radius: d.world.radius,
    tol: d.goal_tol_m, hz: d.hz, src: V2_DIR + file, file, code: d.planner_sample, filter: d.filter,
    matrixMatch: d.matrix ? d.matrix.match : null, poseCase: "truth", note: "", v: 2 };
}
function normV1(d, file) {
  const obstacles = d.boxes.map(([cx, cy, hx, hy]) => ({ type: "box", cx, cy, hx, hy, material: "matte" }))
    .concat(d.cylinders.map(([cx, cy, r]) => ({ type: "cylinder", cx, cy, r, material: "matte" })));
  const world = { bounds: d.area, a: d.a, b: d.b, radius: d.radius, obstacles, family: d.family, seed: d.seed, index: d.index };
  return { key: d.name, planner: d.planner, label: d.title, world, preset: null, t: d.t, truth: d.truth, clearance: d.clearance,
    est: d.est || null, dark: d.dark_zones || [], fault: d.fault_log || null, score: d.score, radius: d.radius, tol: d.goal_tol_m,
    hz: d.hz, src: REPLAY_DIR + file, file, code: null, filter: null, matrixMatch: null, poseCase: d.case || "truth",
    note: d.note || "", env: d.env, v: 1 };
}
async function loadRun(fam, entry) {
  const url = fam.dir + entry.file;
  if (!R.cache.has(url)) R.cache.set(url, getJSON(url).then(d => (fam.key === LEGACY ? normV1(d, entry.file) : normV2(d, entry.file))));
  try { return await R.cache.get(url); } catch (err) { R.cache.delete(url); throw err; }
}

// ----- drawing -----
function palette() {
  return { bg: css("--panel"), fg: css("--fg"), muted: css("--muted"), line: css("--line"), accent: css("--accent"), vs: css("--vs"),
    obst: css("--obst"), glass: css("--glass"), est: css("--est"), ok: css("--ok"), bad: css("--bad"), warn: css("--warn"), dark: css("--dark-zone") };
}
function frame(c, world, pad) {
  const dpr = fitCanvas(c); if (!dpr) return null;
  const W = c.width, H = c.height, [x0, y0, x1, y1] = world.bounds;
  const s = Math.min(W / (x1 - x0 + 2 * pad), H / (y1 - y0 + 2 * pad));
  const ox = (W - (x1 - x0 + 2 * pad) * s) / 2, oy = (H - (y1 - y0 + 2 * pad) * s) / 2;
  return { dpr, W, H, s, x0, y0, x1, y1, P: (x, y) => [ox + (x - x0 + pad) * s, oy + (y1 + pad - y) * s] };
}
function drawWorld(g, F, world, C, o) {
  const { P, s, dpr, x0, y0, x1, y1 } = F;
  g.setTransform(1, 0, 0, 1, 0, 0); g.fillStyle = C.bg; g.fillRect(0, 0, F.W, F.H);
  if (o.grid) { // 5 m grid
    g.strokeStyle = C.line; g.lineWidth = dpr;
    for (let v = Math.ceil(x0 / 5) * 5; v <= x1; v += 5) { const [a] = P(v, 0); g.beginPath(); g.moveTo(a, P(0, y1)[1]); g.lineTo(a, P(0, y0)[1]); g.stroke(); }
    for (let v = Math.ceil(y0 / 5) * 5; v <= y1; v += 5) { const [, b] = P(0, v); g.beginPath(); g.moveTo(P(x0, 0)[0], b); g.lineTo(P(x1, 0)[0], b); g.stroke(); }
  }
  for (const [zx0, zy0, zx1, zy1] of o.dark || []) {
    const [a, b] = P(zx0, zy1), [c, d] = P(zx1, zy0);
    g.fillStyle = C.dark; g.fillRect(a, b, c - a, d - b);
    g.setLineDash([4 * dpr, 4 * dpr]); g.strokeStyle = C.muted; g.lineWidth = dpr; g.strokeRect(a, b, c - a, d - b); g.setLineDash([]);
  }
  for (const ob of world.obstacles) {
    const glass = ob.material === "glass" || ob.material === "mirror";
    g.fillStyle = glass ? C.glass : C.obst; g.globalAlpha = glass ? 0.9 : 1;
    if (ob.type === "cylinder") {
      const [a, b] = P(ob.cx, ob.cy); g.beginPath(); g.arc(a, b, Math.max(ob.r * s, 0.8 * dpr), 0, 2 * Math.PI); g.fill();
    } else {
      let xa, xb, ya, yb;
      if (ob.type === "box") { xa = ob.cx - ob.hx; xb = ob.cx + ob.hx; ya = ob.cy - ob.hy; yb = ob.cy + ob.hy; }
      else { // wall: axis-aligned segment, flat ends, thickness across it
        const h = (ob.thickness || 0.1) / 2;
        xa = Math.min(ob.x0, ob.x1); xb = Math.max(ob.x0, ob.x1); ya = Math.min(ob.y0, ob.y1); yb = Math.max(ob.y0, ob.y1);
        if (ob.y0 === ob.y1) { ya -= h; yb += h; } else { xa -= h; xb += h; }
      }
      let [a, b] = P(xa, yb); const [c, d] = P(xb, ya); let w = c - a, h = d - b;
      const min = (glass ? 2.5 : 1.2) * dpr; // keep thin walls and glass visible at thumbnail scale
      if (w < min) { a -= (min - w) / 2; w = min; } if (h < min) { b -= (min - h) / 2; h = min; }
      g.fillRect(a, b, w, h);
    }
    g.globalAlpha = 1;
  }
  { const [a, b] = P(x0, y1); g.strokeStyle = C.obst; g.lineWidth = o.wall * dpr; g.strokeRect(a, b, (x1 - x0) * s, (y1 - y0) * s); }
  const [ax, ay] = P(world.a[0], world.a[1]), [bx, by] = P(world.b[0], world.b[1]);
  const tol = Math.max(o.tol * s, (o.labels ? 6 : 2.5) * dpr);
  g.fillStyle = C.ok; g.beginPath(); g.arc(ax, ay, tol, 0, 2 * Math.PI); g.fill();
  g.lineWidth = (o.labels ? 3 : 1.5) * dpr; g.strokeStyle = C.bad; g.beginPath(); g.arc(bx, by, tol, 0, 2 * Math.PI); g.stroke();
  if (o.bFilled) { g.fillStyle = C.ok; g.beginPath(); g.arc(bx, by, tol, 0, 2 * Math.PI); g.fill(); }
  if (o.labels) {
    g.fillStyle = C.fg; g.font = `700 ${13 * dpr}px system-ui, sans-serif`; g.textBaseline = "middle";
    g.fillText("A", ax + tol + 4 * dpr, ay - tol); g.fillText("B", bx - 4 * dpr, by - tol - 10 * dpr);
  }
}
function drawRun(g, F, run, color, C, showEst) {
  const { P, s, dpr } = F, end = endOf(run), done = R.t >= end - 1e-6, i = idxAt(run.t, Math.min(R.t, end));
  if (showEst && run.est) { // estimated path (what the planner believed)
    const j = idxAt(run.est.map(r => r[0]), R.t);
    g.strokeStyle = C.est; g.lineWidth = 2.2 * dpr; g.setLineDash([6 * dpr, 5 * dpr]); g.beginPath();
    for (let k = 0; k <= j; k++) { const [px, py] = P(run.est[k][1], run.est[k][2]); k ? g.lineTo(px, py) : g.moveTo(px, py); }
    g.stroke(); g.setLineDash([]);
    const e = run.est[j], [ex, ey] = P(e[1], e[2]);
    g.globalAlpha = 0.18; g.fillStyle = C.est; g.beginPath(); g.arc(ex, ey, Math.max(2 * e[3] * s, 3 * dpr), 0, 2 * Math.PI); g.fill(); g.globalAlpha = 1;
    g.fillStyle = C.est; g.beginPath(); g.arc(ex, ey, 4 * dpr, 0, 2 * Math.PI); g.fill();
  }
  g.strokeStyle = color; g.lineWidth = 3 * dpr; g.lineJoin = "round"; g.beginPath();
  for (let k = 0; k <= i; k++) { const [px, py] = P(run.truth[k][0], run.truth[k][1]); k ? g.lineTo(px, py) : g.moveTo(px, py); }
  g.stroke();
  const fl = run.fault;
  if (fl && fl.fired_t != null && R.t >= fl.fired_t) {
    const k = idxAt(run.t, fl.fired_t), [fx, fy] = P(run.truth[k][0], run.truth[k][1]);
    g.strokeStyle = C.bad; g.lineWidth = 2 * dpr; g.beginPath(); g.arc(fx, fy, 9 * dpr, 0, 2 * Math.PI); g.stroke();
    g.fillStyle = C.bad; g.font = `700 ${12 * dpr}px system-ui, sans-serif`; g.textBaseline = "middle";
    g.fillText(`${fl.step_m} m jump`, fx + 12 * dpr, fy - 10 * dpr);
  }
  const [vx, vy] = P(run.truth[i][0], run.truth[i][1]);
  g.fillStyle = color; g.strokeStyle = C.bg; g.lineWidth = 2 * dpr;
  g.beginPath(); g.arc(vx, vy, Math.max(run.radius * s, 5 * dpr), 0, 2 * Math.PI); g.fill(); g.stroke();
  if (done && run.score.outcome !== "reached") {
    g.strokeStyle = run.score.outcome === "collision" ? C.bad : C.warn; g.lineWidth = 3 * dpr;
    g.beginPath(); g.arc(vx, vy, 14 * dpr, 0, 2 * Math.PI); g.stroke();
  }
}
function paintStage(c, items, C) {
  const run0 = items[0].run, F = frame(c, run0.world, 0.5); if (!F) return;
  const g = c.getContext("2d");
  const bFilled = items.some(({ run }) => R.t >= endOf(run) - 1e-6 && run.score.outcome === "reached");
  drawWorld(g, F, run0.world, C, { grid: true, dark: run0.dark, labels: true, bFilled, wall: 4, tol: run0.tol });
  for (const it of items) drawRun(g, F, it.run, it.color, C, it.est);
  const [sx, sy] = F.P(F.x0 + 0.3, F.y0 - 0.32); // scale bar
  g.fillStyle = C.muted; g.font = `${10 * F.dpr}px system-ui, sans-serif`; g.textBaseline = "middle";
  g.fillRect(sx, sy - F.dpr, 5 * F.s, 2 * F.dpr); g.fillText("5 m", sx + 5 * F.s + 5 * F.dpr, sy + F.dpr);
}
function drawStage() {
  if (!R.a) return;
  const C = palette();
  if (R.b && R.view === "side") {
    paintStage(cv, [{ run: R.a, color: C.accent, est: true }], C);
    paintStage(cvB, [{ run: R.b, color: C.vs, est: true }], C);
  } else {
    paintStage(cv, R.b ? [{ run: R.b, color: C.vs, est: true }, { run: R.a, color: C.accent, est: true }] : [{ run: R.a, color: C.accent, est: true }], C);
  }
}
function drawThumb(f) {
  const c = document.querySelector(`.thumb[data-fam="${f.key}"]`);
  if (!c || !f.thumb) return;
  const F = frame(c, f.thumb.world, 0.3); if (!F) return;
  drawWorld(c.getContext("2d"), F, f.thumb.world, palette(), { grid: false, labels: false, wall: 1.5, tol: f.thumb.tol });
}
function drawSpark() {
  const runs = [[R.a, "--accent"], [R.b, "--vs"]].filter(([r]) => r); if (!runs.length) return;
  const dpr = fitCanvas(sp); if (!dpr) return;
  const W = sp.width, H = sp.height, pad = 4 * dpr, T = endAll() || 1;
  let cmax = 1; for (const [r] of runs) for (const c of r.clearance) if (c > cmax) cmax = c;
  cmax *= 1.05;
  const X = t => pad + (t / T) * (W - 2 * pad), Y = c => H - pad - (Math.max(0, c) / cmax) * (H - 2 * pad);
  sctx.setTransform(1, 0, 0, 1, 0, 0); sctx.clearRect(0, 0, W, H);
  sctx.strokeStyle = css("--bad"); sctx.lineWidth = 1.5 * dpr; sctx.setLineDash([4 * dpr, 3 * dpr]);
  sctx.beginPath(); sctx.moveTo(pad, Y(R.a.radius)); sctx.lineTo(W - pad, Y(R.a.radius)); sctx.stroke(); sctx.setLineDash([]);
  const now = [];
  for (const [run, col] of runs) {
    const line = (upto, color, w) => {
      sctx.strokeStyle = color; sctx.lineWidth = w * dpr; sctx.beginPath();
      for (let k = 0; k <= upto; k++) { const x = X(run.t[k]), y = Y(run.clearance[k]); k ? sctx.lineTo(x, y) : sctx.moveTo(x, y); }
      sctx.stroke();
    };
    const i = idxAt(run.t, Math.min(R.t, endOf(run)));
    line(run.t.length - 1, css("--line"), 1.5);
    line(i, css(col), 2);
    sctx.fillStyle = css(col); sctx.beginPath(); sctx.arc(X(run.t[i]), Y(run.clearance[i]), 3.5 * dpr, 0, 2 * Math.PI); sctx.fill();
    now.push(run.clearance[i].toFixed(2) + " m");
  }
  $("#clearNow").textContent = now.join(" / ");
}
function setBadge(el, run) {
  const done = R.t >= endOf(run) - 1e-6, o = run.score.outcome;
  el.className = "badge " + (done ? o : "flying");
  el.textContent = done ? OUT_LABEL[o] || o : "flying";
}
function updateHud() {
  if (!R.a) return;
  const end = endAll(), done = R.t >= end - 1e-6;
  setBadge($("#badge"), R.a);
  if (R.b) setBadge($("#badgeB"), R.b);
  $("#clock").textContent = R.t.toFixed(1) + " s";
  $("#scrub").value = Math.round((R.t / (end || 1)) * 1000);
  $("#playBtn").textContent = R.playing ? "Pause" : done ? "Replay" : "Play";
}
function drawFrame() { drawStage(); drawSpark(); updateHud(); }
function draw() { for (const f of R.fams) drawThumb(f); drawFrame(); }

// ----- pickers, stats, URL -----
function renderArenaPicker() {
  $("#arenaPicker").innerHTML = R.fams.map(f => {
    const n = f.runs.filter(r => r.outcome === "reached").length;
    const sub = f.key === LEGACY ? `${f.runs.length} runs, EKF fault` : `${n}/${f.runs.length} reached` + (f.preset === "crazyflie" ? ", 4 beams" : "");
    return `<button class="arena-tile" role="tab" data-fam="${esc(f.key)}" aria-selected="${R.fam === f}" title="${esc(famName(f.key) + ": " + (FAMILY_INFO[f.key] || ["", ""])[1])}">` +
      `<canvas class="thumb" data-fam="${esc(f.key)}" aria-hidden="true"></canvas><span class="an">${esc(famName(f.key))}</span><span class="as">${esc(sub)}</span></button>`;
  }).join("");
  for (const f of R.fams) drawThumb(f);
}
function markArenaPicker() {
  document.querySelectorAll(".arena-tile").forEach(b => b.setAttribute("aria-selected", String(R.fam && b.dataset.fam === R.fam.key)));
}
function renderRunPicker() {
  const f = R.fam;
  $("#runPicker").innerHTML = f.runs.map(r => {
    const sel = R.a && r.key === R.a.key, vs = R.b && r.key === R.b.key;
    const tt = r.outcome === "reached" && r.ttg != null ? `<span class="tt">${r.ttg.toFixed(1)} s</span>` : "";
    return `<button class="run-btn${vs ? " is-vs" : ""}" role="tab" data-k="${esc(r.key)}" aria-selected="${!!sel}" title="${esc(r.key)}: ${esc(OUT_LABEL[r.outcome] || r.outcome)}"><span class="dot ${esc(r.outcome)}"></span>${esc(r.label)}${tt}</button>`;
  }).join("");
  const opts = R.a ? f.loaded.filter(r => r.key !== R.a.key && worldKey(r) === worldKey(R.a)) : [];
  $("#vsSel").innerHTML = `<option value="">none</option>` + opts.map(r => `<option value="${esc(r.key)}"${R.b && R.b.key === r.key ? " selected" : ""}>${esc(r.label)}</option>`).join("");
  $("#vsSel").disabled = !opts.length;
}
function statsTable() {
  const runs = [R.a, R.b].filter(Boolean), anyEst = runs.some(r => r.est);
  const rows = [
    ["Outcome", r => OUT_LABEL[r.score.outcome] || r.score.outcome],
    ["Time to goal", r => fmt(r.score.time_to_goal_s, "s")],
    ["Run ended at", r => fmt(r.score.duration_s, "s") + (r.score.max_time_s ? ` (limit ${r.score.max_time_s} s)` : "")],
    ["Min clearance", r => fmt(r.score.min_clearance_m, "m")],
    ["Path length", r => fmt(r.score.path_length_m, "m")],
    ["Hit", r => (r.score.outcome === "collision" ? r.score.hit_material || "surface" : "-")],
    ["Pose", r => (r.poseCase !== "truth" ? `EKF, fault "${r.poseCase}"` : "true pose")],
  ];
  if (anyEst) rows.push(["Max pose error", r => fmt(r.score.max_pose_error_m, "m")]);
  rows.push(
    ["Code", r => (r.code ? `${r.code} / ${r.planner}` : r.planner) + (r.filter ? ` + ${r.filter}` : "")],
    ["Sensor", r => (r.preset ? PRESET_INFO[r.preset] || r.preset : "-")],
    ["Layout", r => `${famName(r.world.family)} #${r.world.index}, seed ${r.world.seed}, ${r.score.n_obstacles != null ? r.score.n_obstacles : r.world.obstacles.length} obstacles` + (r.score.n_glass ? `, ${r.score.n_glass} glass` : "")],
    ["Input", () => "synthetic (simulated)"]);
  const head = R.b ? `<thead><tr><th></th><th class="ca">${esc(R.a.label)}</th><th class="cb">${esc(R.b.label)}</th></tr></thead>` : "";
  return head + "<tbody>" + rows.map(([lbl, fn]) => `<tr><th scope="row">${esc(lbl)}</th>${runs.map(r => `<td>${esc(fn(r))}</td>`).join("")}</tr>`).join("") + "</tbody>";
}
function renderSide() {
  const a = R.a, b = R.b, f = R.fam, side = !!b && R.view === "side";
  $("#runTitle").textContent = a.label;
  $("#headB").hidden = !b; if (b) $("#runTitleB").textContent = b.label;
  const [name, blurb] = FAMILY_INFO[f.key] || [f.key, ""];
  $("#runNote").textContent = f.key === LEGACY ? [a.note, b && b.note].filter(Boolean).join(" ") :
    `${name}: ${blurb}. Sensor preset ${PRESET_INFO[a.preset] || a.preset}.`;
  $("#stats").innerHTML = statsTable();
  $("#legendB").hidden = !b;
  $("#legendEst").hidden = ![a, b].some(r => r && r.est);
  $("#legendDark").hidden = ![a, b].some(r => r && r.dark.length);
  const src = [a, b].filter(Boolean).map(r => `<a href="${esc(r.src)}">${esc(r.file)}</a>`).join(", ");
  $("#replaySrc").innerHTML = a.v === 2
    ? `Data: ${src}, written by <code>close-area-benchmark/export_replays.py</code>, ${a.hz} Hz. Outcome and min clearance match the row in <code>results/matrix_0.json</code>: ${[a, b].filter(Boolean).map(r => (r.matrixMatch ? "yes" : "no")).join(", ")}. Stuck = moved under 0.2 m in 10 s.`
    : `Data: ${src}, written by <code>close-area-arena/export_replay.py</code> (${esc(a.env.system)} ${esc(a.env.machine)}, Python ${esc(a.env.python)}, numpy ${esc(a.env.numpy)}). Stuck = moved under 0.2 m in 10 s.`;
  document.querySelector(".arena-grid").classList.toggle("side", side);
  $("#wrapB").hidden = !side; $("#capA").hidden = !side;
  if (side) { $("#capA").textContent = a.label; $("#capB").textContent = b.label; }
  $("#viewSeg").hidden = !b;
  document.querySelectorAll("#viewSeg .seg-btn").forEach(x => x.setAttribute("aria-pressed", String(x.dataset.v === R.view)));
  const t = document.querySelector(".compare-row .try");
  t.title = f.key === LEGACY ? "Draw or load an arena and run the planners in your browser" : `Load preset ${f.key}_0 there and run the planners in your browser`;
}
function updateURL() {
  if (!R.fam || !R.a) return;
  const q = new URLSearchParams();
  q.set("family", R.fam.key); q.set("planner", R.a.key);
  if (R.b) { q.set("vs", R.b.key); if (R.view === "side") q.set("view", "side"); }
  try { history.replaceState(null, "", location.pathname + "?" + q.toString() + location.hash); } catch (err) { /* file:// */ }
}
function selectPair(aKey, bKey, opts) {
  const f = R.fam;
  R.a = f.loaded.find(r => r.key === aKey) || f.loaded[0];
  const b = bKey ? f.loaded.find(r => r.key === bKey) : null;
  R.b = b && b !== R.a && worldKey(b) === worldKey(R.a) ? b : null;
  clearTimeout(R.advanceTimer);
  R.t = REDUCED ? endAll() : 0; R.playing = !REDUCED;
  renderRunPicker(); renderSide(); renderMatrix(); drawFrame();
  if (!opts || !opts.quiet) updateURL();
}
async function selectFamily(key, aKey, bKey, opts) {
  const f = R.famByKey[key] || R.famByKey[DEFAULT.family] || R.fams[0], seq = ++R.seq;
  R.fam = f; markArenaPicker();
  const [name, blurb] = FAMILY_INFO[f.key] || [f.key, ""];
  if (!opts || !opts.msg) $("#familyNote").textContent = f.key === LEGACY
    ? `${name}: ${blurb}. Written by samples/close-area-arena/export_replay.py. Compare works between runs on the same layout.`
    : `${name}: ${blurb}. Layout 0, seed 0, sensor preset ${PRESET_INFO[f.preset] || f.preset}. ${f.runs.length} planners.`;
  try { f.loaded = await Promise.all(f.runs.map(r => loadRun(f, r))); }
  catch (err) { $("#familyNote").textContent = `Could not load ${f.key} replays (${err.message}).`; return; }
  if (seq !== R.seq) return;
  selectPair(f.runs.some(r => r.key === aKey) ? aKey : (f.runs.some(r => r.key === DEFAULT.planner) ? DEFAULT.planner : f.runs[0].key), bKey, opts);
}
function readURL() { // ?family=office&planner=astar_known&vs=vfh_plus&view=side, or ?run=<v1 name | v1 index | family__planner>
  const q = new URLSearchParams(location.search), st = { family: null, planner: null, vs: null, msg: "" };
  const run = (q.get("run") || "").replace(/\.json$/, "");
  if (run) {
    const leg = R.famByKey[LEGACY], [rf, rp] = run.split("__");
    const hit = leg && (leg.runs.find(r => r.key === run) || (/^\d+$/.test(run) ? leg.runs[+run] : null));
    if (hit) { st.family = LEGACY; st.planner = hit.key; }
    else if (R.famByKey[rf] && R.famByKey[rf].runs.some(r => r.key === rp)) { st.family = rf; st.planner = rp; }
    else st.msg = `No replay "${run}". Showing the default.`;
  }
  const fam = q.get("family");
  if (fam) { if (R.famByKey[fam]) st.family = fam; else st.msg = `No arena family "${fam}". Showing the default.`; }
  const f = R.famByKey[st.family || DEFAULT.family];
  const pl = q.get("planner"), vs = q.get("vs");
  if (pl) { if (f && f.runs.some(r => r.key === pl)) st.planner = pl; else st.msg = `No planner "${pl}" in ${f ? f.key : "this arena"}.`; }
  if (vs) { if (f && f.runs.some(r => r.key === vs)) st.vs = vs; else st.msg = `No planner "${vs}" to compare in ${f ? f.key : "this arena"}.`; }
  if (q.get("view") === "side") R.view = "side";
  R.pinned = !!(run || fam || pl || vs);
  return st;
}
function tick(now) {
  if (R.a && R.playing) {
    const dt = Math.min(0.1, (now - (R.last || now)) / 1000), end = endAll();
    R.t = Math.min(end, R.t + dt * R.speed);
    if (R.t >= end) {
      R.playing = false;
      if (!R.touched && !R.pinned && !R.b) R.advanceTimer = setTimeout(() => { // tour the planners of this arena
        if (R.touched || R.b) return;
        const runs = R.fam.runs, k = runs.findIndex(r => r.key === R.a.key);
        selectPair(runs[(k + 1) % runs.length].key, null, { quiet: true });
      }, 2500);
    }
    drawFrame();
  }
  R.last = now;
  requestAnimationFrame(tick);
}
function touch() { R.touched = true; clearTimeout(R.advanceTimer); }

// ----- results grid from matrix_0.md -----
function parseMatrix(md) {
  const out = { cmd: (md.match(/^`([^`]+)`/) || [])[1] || "", presets: {} };
  const parts = md.split(/^### Preset `([^`]+)`.*$/m);
  for (let k = 1; k < parts.length; k += 2) {
    const lines = parts[k + 1].split(/^### /m)[0].split("\n").filter(l => l.startsWith("|"));
    if (lines.length < 3) continue;
    const cellsOf = l => l.split("|").slice(1, -1).map(x => x.trim());
    const fams = cellsOf(lines[0]).slice(1);
    const rows = lines.slice(2).map(l => {
      const c = cellsOf(l);
      return { planner: c[0], cells: c.slice(1).map(x => { const m = x.match(/^(\d+(?:\.\d+)?) \/ (\d+(?:\.\d+)?)$/); return m ? [+m[1], +m[2]] : null; }) };
    });
    out.presets[parts[k]] = { fams, rows };
  }
  return out;
}
function renderMatrix() {
  const M = R.matrix, wrap = $("#matrixWrap"); if (!M) return;
  if (!R.preset) R.preset = R.fam && R.fam.preset && M.presets[R.fam.preset] ? R.fam.preset : "ideal";
  document.querySelectorAll("#presetSeg .seg-btn").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.p === R.preset)));
  const p = M.presets[R.preset];
  if (!p) { wrap.innerHTML = `<p class="muted">No preset ${esc(R.preset)} in matrix_0.md.</p>`; return; }
  const labels = {}; for (const f of R.fams) for (const r of f.runs) if (f.key !== LEGACY) labels[r.key] = r.label;
  const curF = R.fam && R.fam.key, curP = R.a && curF !== LEGACY ? R.a.key : null, curB = R.b && curF !== LEGACY ? R.b.key : null;
  const head = `<tr><th scope="col">planner</th>${p.fams.map(f => `<th scope="col"${f === curF ? ' class="cur"' : ""}>${esc(famName(f))}</th>`).join("")}</tr>`;
  const body = p.rows.map(r => `<tr${r.planner === curP ? ' class="cur"' : r.planner === curB ? ' class="cur-b"' : ""}><th scope="row" title="${esc(r.planner)}">${esc(labels[r.planner] || r.planner)}</th>` +
    r.cells.map((c, k) => {
      if (!c) return "<td>-</td>";
      const cls = (c[0] >= 90 ? "hi" : c[0] >= 50 ? "mid" : "lo") + (c[1] > 0 ? " coll" : "") + (p.fams[k] === curF ? " curc" : "");
      return `<td class="${cls}"><button class="cell" data-fam="${esc(p.fams[k])}" data-pl="${esc(r.planner)}" aria-label="${esc(r.planner)} on ${esc(p.fams[k])}: ${c[0]} % reached, ${c[1]} % collision. Replay layout 0">${c[0]}<span class="sl"> / </span><span class="cp">${c[1]}</span></button></td>`;
    }).join("") + "</tr>").join("");
  wrap.innerHTML = `<p class="muted small mcap">Preset ${esc(PRESET_INFO[R.preset] || R.preset)}. Replays above use crazyflie on glass_office and ideal elsewhere.</p>` +
    `<div class="grid-scroll"><table class="matrix"><thead>${head}</thead><tbody>${body}</tbody></table></div>`;
}
async function loadMatrix() {
  try {
    const r = await fetch(MATRIX_URL); if (!r.ok) throw new Error(r.status + " " + MATRIX_URL);
    R.matrix = parseMatrix(await r.text());
    if (R.matrix.cmd) $("#matrixCmd").textContent = R.matrix.cmd;
    renderMatrix();
  } catch (err) {
    $("#matrixWrap").innerHTML = `<p class="muted">Could not load matrix_0.md (${esc(err.message)}).</p>`;
  }
}

async function loadReplays() {
  let v2, v1 = null;
  try { v2 = await getJSON(V2_DIR + "index.json"); }
  catch (err) {
    $("#arenaPicker").innerHTML = `<p class="muted">No replays (${esc(err.message)}). Run <code>.venv/bin/python export_replays.py</code> in samples/close-area-benchmark.</p>`;
    return;
  }
  try { v1 = await getJSON(REPLAY_DIR + "index.json"); } catch (err) { /* v1 tile is optional */ }
  R.fams = v2.families.map(f => ({ key: f.family, preset: f.preset, dir: V2_DIR,
    runs: f.runs.map(r => ({ key: r.planner, file: r.file, label: r.label, outcome: r.outcome, ttg: r.time_to_goal_s })) }));
  if (v1) R.fams.push({ key: LEGACY, preset: null, dir: REPLAY_DIR,
    runs: v1.runs.map(r => ({ key: r.name, file: r.file, label: r.title, outcome: r.outcome, ttg: null })) });
  for (const f of R.fams) R.famByKey[f.key] = f;
  renderArenaPicker();
  const st = readURL();
  if (st.msg) $("#familyNote").textContent = st.msg;
  for (const f of R.fams) loadRun(f, f.runs[0]).then(r => { f.thumb = r; drawThumb(f); }).catch(() => { /* no thumbnail */ });

  $("#arenaPicker").onclick = e => {
    const b = e.target.closest(".arena-tile"); if (!b) return;
    touch(); selectFamily(b.dataset.fam, R.a && R.a.key, R.b && R.b.key);
  };
  $("#runPicker").onclick = e => {
    const b = e.target.closest(".run-btn"); if (!b) return;
    touch(); const k = b.dataset.k;
    selectPair(k, R.b && R.b.key !== k ? R.b.key : null);
  };
  $("#vsSel").onchange = e => { touch(); selectPair(R.a.key, e.target.value || null); };
  document.querySelectorAll("#viewSeg .seg-btn").forEach(b => b.onclick = () => { touch(); R.view = b.dataset.v; renderSide(); drawFrame(); updateURL(); });
  document.querySelectorAll("#presetSeg .seg-btn").forEach(b => b.onclick = () => { R.preset = b.dataset.p; renderMatrix(); });
  $("#matrixWrap").onclick = e => {
    const b = e.target.closest(".cell"); if (!b) return;
    touch(); selectFamily(b.dataset.fam, b.dataset.pl, null);
    document.getElementById("arena").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth" });
  };
  $("#playBtn").onclick = () => {
    touch(); if (!R.a) return;
    if (!R.playing && R.t >= endAll() - 1e-6) R.t = 0;
    R.playing = !R.playing; updateHud();
  };
  $("#speedSel").onchange = e => { R.speed = +e.target.value; };
  $("#scrub").oninput = e => { touch(); if (!R.a) return; R.playing = false; R.t = (+e.target.value / 1000) * endAll(); drawFrame(); };

  await selectFamily(st.family || DEFAULT.family, st.planner, st.vs, { quiet: true, msg: !!st.msg });
  requestAnimationFrame(tick);
  loadMatrix();
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
