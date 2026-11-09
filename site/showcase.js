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


// ---------- story: what we tested ----------
// Two replays from data/showcase/story/ (schema close-area-story-replay/1), written by
// samples/close-area-safety-filter/export_replay.py (kill_test.json) and
// samples/close-area-relocalize/export_replay.py (relocalize.json). Each file carries its own
// headline numbers, recomputed from the samples' result JSONs; the cards below only format them.
const STORY_DIR = "data/showcase/story/";
const SAFETY = "samples/close-area-safety-filter/", RELOC = "samples/close-area-relocalize/";
const readme = dir => `index.html#page=${encodeURIComponent(dir + "README.md")}`;
const pct = v => `${(+v).toFixed(1)} %`;
const ci = c => `[${c[0].toFixed(1)}, ${c[1].toFixed(1)}]`;
const ARM_COL = { F0: "--warn", F2: "--vs", F5: "--accent", estimator: "--warn", single: "--vs", multi_ig: "--accent" };

function killCard(h) {
  const H = h.F5_jump_heldout, J = h.F5_jump_seeds012, F4 = h.F4_jump_seeds012, F2 = h.F2_jump_seeds012;
  const others = Object.values(h.F5_other_cases_seeds012), oc = others.reduce((a, c) => a + c.collisions, 0);
  return `<div class="row"><span class="badge collision">${esc(h.verdict)}</span><span class="badge synthetic">${esc(h.input)}</span></div>
    <h3>Integrity-aware safety filter (F5)</h3>
    <p class="shows">Margin = live protection level from a VIO + UWB integrity monitor, hover when the monitor is ambiguous. Bar (doc 04 section 3.4): collisions &lt;= 1 % in every fault case, reach &gt;= 90 % of PX4-CBF.</p>
    <ul class="snum">
      <li><b>${pct(H.collision_pct)}</b> ${ci(H.ci95)} collisions under the VIO jump on held-out seeds 1-2 (${H.collisions} of ${H.runs} runs). Bar: 1 %.</li>
      <li><b>${h.F5_jump_reach_ratio_vs_F2.toFixed(2)}</b> of PX4-CBF's reach under the jump (${J.reached} vs ${F2.reached} of ${J.runs} runs, seeds 0-2). Bar: 0.90.</li>
      <li>A hand-tuned fixed 0.2 m bound (MR-CBF, no monitor): <b>${pct(F4.collision_pct)}</b> ${ci(F4.ci95)} under the jump, seeds 0-2. Same safety within noise.</li>
      <li>The other ${others.length} fault cases: ${oc} collisions in ${others.reduce((a, c) => a + c.runs, 0)} runs (upper bound ${others[0].ci95[1].toFixed(1)} % per case).</li>
    </ul>
    <p class="kr"><strong>Still holds:</strong> a range-only filter (PX4-CBF) under the A* planner had 0 collisions with obstacles the fan sees, in every fault case (500 runs, part a). Ours adds nothing there.</p>
    <p class="small"><a href="../${SAFETY}results/kill_e_tables.md">kill_e_tables.md</a> - <a href="${readme(SAFETY)}">sample README, part e</a></p>`;
}
function relocCard(h) {
  const F = h.families, cf = h.crazyflie_4beam_spin_ig_seed0, ca = h.unmapped_obstacles_c_added_seed2;
  const cr = f => { const v = F[f].collision_pct_dropout_jump.map(Math.round); return `${Math.min(...v)}-${Math.max(...v)} %`; };
  return `<div class="row"><span class="badge stuck">${esc(h.verdict)}</span><span class="badge synthetic">${esc(h.input)}</span></div>
    <h3>Relocalization after VIO loss (f)</h3>
    <p class="shows">After a VIO loss: hover, keep up to 5 scan-match hypotheses, fly one info-gain move on a tie, accept after 3 consistent scans. Bar per family: reached &gt;= 95 % and 0 wrong commits, held-out seeds ${h.matrix_seeds[0]}-${h.matrix_seeds[h.matrix_seeds.length - 1]}, both faults pooled.</p>
    <ul class="snum">
      <li>Random and U trap: <b>${pct(F.random.reached_pct)}</b> ${ci(F.random.ci95)} reached, ${F.random.wrong_commits + F.u_trap.wrong_commits} wrong commits (${F.random.runs} runs each). PASS.</li>
      <li>Narrow gap <b>${pct(F.narrow_gap.reached_pct)}</b> ${ci(F.narrow_gap.ci95)}, glass office <b>${pct(F.glass_office.reached_pct)}</b> ${ci(F.glass_office.ci95)}: collisions ${cr("narrow_gap")} and ${cr("glass_office")}.</li>
      <li>Warehouse ${pct(F.warehouse.reached_pct)} ${ci(F.warehouse.ci95)} reached, but <b>${F.warehouse.wrong_commits} wrong commits</b>: repeated aisles look alike.</li>
      <li>4-beam Crazyflie-like sensor with a yaw spin: <b>${pct(cf.dropout.reached_pct)}</b> ${ci(cf.dropout.ci95)} / <b>${pct(cf.jump.reached_pct)}</b> ${ci(cf.jump.ci95)} reached (dropout / jump, seed 0).</li>
      <li>Unmapped obstacles in the prior map: <b>${pct(ca.jump.collision_pct)}</b> ${ci(ca.jump.ci95)} collisions per fault (seed 2).</li>
    </ul>
    <p class="kr"><strong>Still holds:</strong> with a dense 360 deg range fan, an exact map and open layouts, (f) reached B in every run with 0 wrong commits; the estimator alone reached 36 % under the jump (seed 0).</p>
    <p class="small"><a href="../${RELOC}results/reloc_matrix_matrix.md">reloc_matrix_matrix.md</a> - <a href="${readme(RELOC)}">sample README</a>. 95 % Wilson intervals; the 4-beam and unmapped ones computed by export_replay.py from the counts.</p>`;
}

// One player per replay: arm toggles (overlay compare), play / pause, speed, scrub.
function makePlayer(key, data, paint, hud) {
  const P = { key, data, paint, hud, t: 0, playing: false, speed: 2, last: 0, sel: new Set(data.arms.map(a => a.arm)),
    cv: $(`#${key}Canvas`) };
  P.end = () => Math.max(...data.arms.filter(a => P.sel.has(a.arm)).map(a => a.T[a.T.length - 1]), 0.1);
  P.draw = () => {
    paint(P); hud(P);
    $(`#${key}Clock`).textContent = P.t.toFixed(1) + " s";
    $(`#${key}Scrub`).value = Math.round((P.t / P.end()) * 1000);
    $(`#${key}Play`).textContent = P.playing ? "Pause" : P.t >= P.end() - 1e-6 ? "Replay" : "Play";
  };
  const arms = $(`#${key}Arms`);
  const renderArms = () => {
    arms.innerHTML = data.arms.map(a => `<button class="run-btn sarm" data-a="${esc(a.arm)}" aria-pressed="${P.sel.has(a.arm)}" style="--c: var(${ARM_COL[a.arm]})"><span class="dot ${esc(a.score.outcome)}"></span>${esc(a.label)}</button>`).join("");
  };
  renderArms();
  arms.onclick = e => {
    const b = e.target.closest(".sarm"); if (!b) return;
    const k = b.dataset.a;
    if (P.sel.has(k) && P.sel.size > 1) P.sel.delete(k); else P.sel.add(k);
    renderArms(); P.t = Math.min(P.t, P.end()); P.draw();
  };
  $(`#${key}Play`).onclick = () => { if (!P.playing && P.t >= P.end() - 1e-6) P.t = 0; P.playing = !P.playing; P.draw(); };
  $(`#${key}Speed`).onchange = e => { P.speed = +e.target.value; };
  $(`#${key}Scrub`).oninput = e => { P.playing = false; P.t = (+e.target.value / 1000) * P.end(); P.draw(); };
  P.seek = t => { P.started = true; P.playing = false; P.t = Math.max(0, Math.min(t, P.end())); P.draw(); };
  return P;
}

function storyPath(g, F, pts, upto, color, w, dash) {
  const { P, dpr } = F; if (upto < 0) return;
  g.strokeStyle = color; g.lineWidth = w * dpr; g.lineJoin = "round"; g.setLineDash(dash ? [6 * dpr, 5 * dpr] : []);
  g.beginPath();
  for (let k = 0; k <= upto; k++) { const [x, y] = P(pts[k][0], pts[k][1]); k ? g.lineTo(x, y) : g.moveTo(x, y); }
  g.stroke(); g.setLineDash([]);
}
function storyMark(g, F, xy, color, label, kind, below) {
  const { P, dpr } = F, [x, y] = P(xy[0], xy[1]);
  g.strokeStyle = color; g.fillStyle = color; g.lineWidth = 2.5 * dpr;
  if (kind === "x") { const r = 7 * dpr; g.beginPath(); g.moveTo(x - r, y - r); g.lineTo(x + r, y + r); g.moveTo(x + r, y - r); g.lineTo(x - r, y + r); g.stroke(); }
  else if (kind === "ok") { g.beginPath(); g.arc(x, y, 5 * dpr, 0, 2 * Math.PI); g.fill(); }
  else { g.beginPath(); g.arc(x, y, 9 * dpr, 0, 2 * Math.PI); g.stroke(); }
  if (label) {
    g.font = `700 ${11.5 * dpr}px system-ui, sans-serif`; g.textBaseline = "middle";
    const w = g.measureText(label).width, right = x + 12 * dpr + w < F.W;
    g.fillText(label, right ? x + 12 * dpr : x - 12 * dpr - w, y + (below ? 20 : -11) * dpr);
  }
}
function storyBase(P, extra) {
  const d = P.data, F = frame(P.cv, d.world, 0.5); if (!F) return null;
  const g = P.cv.getContext("2d"), C = palette();
  const done = d.arms.filter(a => P.sel.has(a.arm)).some(a => P.t >= a.T[a.T.length - 1] - 1e-6 && a.score.outcome === "reached");
  drawWorld(g, F, d.world, C, Object.assign({ grid: true, labels: true, bFilled: done, wall: 4, tol: d.goal_tol_m || 0.3 }, extra));
  return { F, g, C };
}
function vehicle(g, F, xy, color, C, r) {
  const [x, y] = F.P(xy[0], xy[1]);
  g.fillStyle = color; g.strokeStyle = C.bg; g.lineWidth = 2 * F.dpr;
  g.beginPath(); g.arc(x, y, Math.max(r * F.s, 5 * F.dpr), 0, 2 * Math.PI); g.fill(); g.stroke();
}
function jumpMark(g, F, a, i, C) {
  const ft = a.fault && a.fault.fired_t;
  if (ft == null || a.T[i] < ft) return;
  const k = idxAt(a.T, ft);
  storyMark(g, F, a.TR[k], C.bad, `${a.fault.step_m} m jump`, "ring");
}

// ----- kill test -----
function paintKill(P) {
  const b = storyBase(P, {}); if (!b) return;
  const { F, g, C } = b, d = P.data, { P: Pt, s, dpr } = F;
  const uc = css("--uns");
  for (const u of d.unsensed) { // in the map and in truth, never in a scan
    const [x, y] = Pt(u.cx, u.cy);
    g.fillStyle = uc; g.strokeStyle = uc; g.lineWidth = 2 * dpr; g.setLineDash([3 * dpr, 3 * dpr]);
    if (u.kind === "pole") {
      g.beginPath(); g.arc(x, y, Math.max(u.r * s, 2.5 * dpr), 0, 2 * Math.PI); g.fill();
      g.beginPath(); g.arc(x, y, Math.max(0.4 * s, 11 * dpr), 0, 2 * Math.PI); g.stroke();
    } else {
      const [a0, b0] = Pt(u.cx - u.hx, u.cy + u.hy), [a1, b1] = Pt(u.cx + u.hx, u.cy - u.hy);
      g.fillRect(a0 - dpr, b0 - dpr, Math.max(a1 - a0, 3 * dpr), Math.max(b1 - b0, 3 * dpr));
      g.strokeRect(a0 - 6 * dpr, b0 - 6 * dpr, a1 - a0 + 12 * dpr, b1 - b0 + 12 * dpr);
    }
    g.setLineDash([]);
    g.font = `700 ${11.5 * dpr}px system-ui, sans-serif`; g.textBaseline = "middle";
    const lbl = `unsensed ${u.kind === "pole" ? "pole" : "glass"}`, w = g.measureText(lbl).width;
    g.fillText(lbl, x + 16 * dpr + w < F.W ? x + 16 * dpr : x - 16 * dpr - w, y - 18 * dpr);
  }
  const arms = d.arms.filter(a => P.sel.has(a.arm));
  let jumped = false;
  for (const a of arms) {
    const col = css(ARM_COL[a.arm]), i = idxAt(a.T, Math.min(P.t, a.T[a.T.length - 1]));
    g.globalAlpha = 0.8; storyPath(g, F, a.est, i, col, 1.8, true); g.globalAlpha = 1;
    storyPath(g, F, a.TR, i, col, 3, false);
    if (!jumped) { jumpMark(g, F, a, i, C); jumped = a.fault && a.fault.fired_t != null && a.T[i] >= a.fault.fired_t; }
    vehicle(g, F, a.TR[i], col, C, d.world.radius);
    if (a.hover && a.hover[i]) { const [x, y] = Pt(a.TR[i][0], a.TR[i][1]); g.strokeStyle = col; g.lineWidth = 2 * dpr; g.setLineDash([2 * dpr, 3 * dpr]); g.beginPath(); g.arc(x, y, 14 * dpr, 0, 2 * Math.PI); g.stroke(); g.setLineDash([]); }
    if (a.hit && P.t >= a.hit.t - 1e-6) storyMark(g, F, a.hit.xy, C.bad, `${a.arm} hit ${a.hit.unsensed ? "unsensed " : ""}${a.hit.what}`, "x", true);
  }
}
function hudKill(P) {
  const parts = P.data.arms.filter(a => P.sel.has(a.arm)).map(a => {
    const end = a.T[a.T.length - 1], i = idxAt(a.T, Math.min(P.t, end));
    const st = P.t >= end - 1e-6 ? (a.score.outcome === "collision" ? `hit the ${a.hit.what}` : a.score.outcome + (a.score.ended_in_hover ? " (hovering)" : ""))
      : a.hover && a.hover[i] ? "hovering" : a.intervened[i] ? "filter acting" : "flying";
    const e = Math.hypot(a.TR[i][0] - a.est[i][0], a.TR[i][1] - a.est[i][1]);
    return `${a.arm}: ${st}, pose error ${e.toFixed(2)} m`;
  });
  $("#killNow").textContent = parts.join(" | ");
}

// ----- relocalization -----
function paintReloc(P) {
  const d = P.data, b = storyBase(P, { dark: d.dark_zones }); if (!b) return;
  const { F, g, C } = b, { P: Pt, s, dpr } = F;
  const arms = d.arms.filter(a => P.sel.has(a.arm));
  let jumped = false;
  for (const a of arms) {
    const col = css(ARM_COL[a.arm]), end = a.T[a.T.length - 1], i = idxAt(a.T, Math.min(P.t, end));
    // ghosts: hypotheses of the latest matched scan, shown for 0.6 s
    let h = i; while (h >= 0 && !a.H[h]) h--;
    if (h >= 0 && a.T[i] - a.T[h] <= 0.6 + 1e-6) {
      const hy = a.H[h], best = hy[0][2] || 1;
      hy.forEach((q, k) => {
        const [x, y] = Pt(q[0], q[1]);
        g.globalAlpha = 0.15 + 0.6 * Math.max(0, Math.min(1, (q[2] / best - 0.8) / 0.2));
        g.fillStyle = col; g.beginPath(); g.arc(x, y, Math.max(0.15 * s, 5 * dpr), 0, 2 * Math.PI); g.fill();
        g.globalAlpha = 1; g.strokeStyle = col; g.lineWidth = (k ? 1 : 2) * dpr;
        g.beginPath(); g.arc(x, y, Math.max(0.15 * s, 5 * dpr), 0, 2 * Math.PI); g.stroke();
      });
    }
    g.globalAlpha = 0.8; storyPath(g, F, a.SEEN, i, col, 1.8, true); g.globalAlpha = 1;
    storyPath(g, F, a.TR, i, col, 3, false);
    if (!jumped) { jumpMark(g, F, a, i, C); jumped = a.fault && a.fault.fired_t != null && a.T[i] >= a.fault.fired_t; }
    for (const e of a.events) if (e.accepted_xy && e.t_end != null && P.t >= e.t_end - 1e-6 && P.t <= e.t_end + 2.5)
      storyMark(g, F, e.accepted_xy, e.wrong ? C.bad : C.ok, e.wrong ? `wrong commit ${e.err_m.toFixed(2)} m` : "", e.wrong ? "x" : "ok");
    vehicle(g, F, a.TR[i], col, C, d.world.radius);
    if (a.L[i]) { const [x, y] = Pt(a.TR[i][0], a.TR[i][1]); g.strokeStyle = col; g.lineWidth = 2 * dpr; g.setLineDash([2 * dpr, 3 * dpr]); g.beginPath(); g.arc(x, y, 14 * dpr, 0, 2 * Math.PI); g.stroke(); g.setLineDash([]); }
  }
}
function hudReloc(P) {
  const parts = P.data.arms.filter(a => P.sel.has(a.arm)).map(a => {
    const end = a.T[a.T.length - 1], i = idxAt(a.T, Math.min(P.t, end));
    let h = i; while (h >= 0 && !a.H[h]) h--;
    const nh = h >= 0 && a.T[i] - a.T[h] <= 0.6 + 1e-6 ? a.H[h].length : 0;
    const st = P.t >= end - 1e-6 ? a.score.outcome : a.L[i] ? `lost, ${a.M[i] ? "flying a move" : "hovering"}${nh ? `, ${nh} hypotheses` : ""}` : "flying";
    const e = Math.hypot(a.TR[i][0] - a.SEEN[i][0], a.TR[i][1] - a.SEEN[i][1]);
    return `${a.label.split(" ")[0]}: ${st}, pose error ${e.toFixed(2)} m`;
  });
  $("#relocNow").textContent = parts.join(" | ");
}

const OUTCOME = { reached: "reached B", stuck: "stuck", collision: "collision", timeout: "timeout" };
function storyStats(d, rows) {
  const head = `<thead><tr><th></th>${d.arms.map(a => `<th style="color: var(${ARM_COL[a.arm]})">${esc(a.label.split(":")[0])}</th>`).join("")}</tr></thead>`;
  return head + "<tbody>" + rows.map(([lbl, fn]) => `<tr><th scope="row">${esc(lbl)}</th>${d.arms.map(a => `<td>${esc(fn(a))}</td>`).join("")}</tr>`).join("") + "</tbody>";
}
function prepKill(d) {
  for (const a of d.arms) { a.T = a.t; a.TR = a.truth; }
  const fired = d.arms[0].fault.fired_t;
  $("#killNote").innerHTML = `<span class="badge synthetic">synthetic</span> Random layout ${d.index}, seed ${d.seed}, A* on a known map that includes both unsensed obstacles; the 0.5 m VIO jump fires near ${fired.toFixed(1)} s. ${esc(d.selection[0].toUpperCase() + d.selection.slice(1))}. Rates over all runs are in the card above.`;
  $("#killStats").innerHTML = storyStats(d, [
    ["Outcome", a => OUTCOME[a.score.outcome] + (a.hit ? ` (${a.hit.unsensed ? "unsensed " : ""}${a.hit.what}, ${a.hit.t} s)` : "")],
    ["Min clearance", a => `${a.score.min_clearance_m} m`],
    ["Max pose error", a => `${a.score.max_pose_error_m} m`],
    ["Filter acting", a => `${Math.round(100 * a.score.intervention_frac)} % of steps`],
    ["Ended hovering", a => (a.score.ended_in_hover == null ? "-" : a.score.ended_in_hover ? "yes" : "no")],
    ["Matches published row", a => (a.check.match ? "yes" : "NO")],
  ]);
  $("#killSrc").innerHTML = `Data: <a href="${STORY_DIR}kill_test.json">kill_test.json</a>, ${d.hz} Hz, from <code>close-area-safety-filter/export_replay.py</code>. Outcome, min clearance, path length and unsensed hit match <a href="../${SAFETY}results/kill_a_unsensed_on_0.json">kill_a</a> (F0) and <a href="../${SAFETY}results/kill_d_unsensed_on_0.json">kill_d</a> (F2, F5).`;
}
function prepReloc(d) {
  for (const a of d.arms) {
    a.T = a.rows.map(r => r[0]); a.TR = a.rows.map(r => [r[1], r[2]]); a.SEEN = a.rows.map(r => [r[3], r[4]]);
    a.L = a.rows.map(r => r[5]); a.M = a.rows.map(r => r[6]); a.H = a.rows.map(r => r[7]);
  }
  $("#relocNote").innerHTML = `<span class="badge synthetic">synthetic</span> Random layout ${d.index}, seed ${d.seed}, A* on the exact map, 72-beam 6 m fan; the 0.5 m VIO jump fires at ${d.arms[0].fault.fired_t.toFixed(1)} s. ${esc(d.selection[0].toUpperCase() + d.selection.slice(1))}. In 100 seed-0 jump runs, (b) made 4 wrong commits and still reached B every time.`;
  $("#relocStats").innerHTML = storyStats(d, [
    ["Outcome", a => OUTCOME[a.score.outcome] + (a.score.time_to_goal_s ? `, ${a.score.time_to_goal_s} s` : "")],
    ["Max pose error", a => `${a.score.max_pose_error_m} m`],
    ["Loss events", a => (a.arm === "estimator" ? "-" : `${a.events.length}`)],
    ["Wrong commits", a => (a.score.wrong_commits == null ? "-" : `${a.score.wrong_commits}`)],
    ["Lost (hover or move)", a => (a.score.hover_s == null ? "-" : `${a.score.hover_s} s`)],
    ["Matches published row", a => (a.check.match ? "yes" : "NO")],
  ]);
  $("#relocSrc").innerHTML = `Data: <a href="${STORY_DIR}relocalize.json">relocalize.json</a>, ${d.hz} Hz, from <code>close-area-relocalize/export_replay.py</code>. Outcome, min clearance, path length and wrong commits match <a href="../${RELOC}results/reloc_random_0.json">reloc_random_0</a> (a) and <a href="../${RELOC}results/disamb_random_0.json">disamb_random_0</a> (b, f).`;
}
function relocEvents(P) {
  const items = [];
  for (const a of P.data.arms) for (const e of a.events) {
    const mv = e.moves.length ? `, flew ${e.moves.length} move${e.moves.length > 1 ? "s" : ""} (${e.moves.map(m => Math.hypot(m[0], m[1]).toFixed(1) + " m").join(", ")})` : "";
    const res = e.result === "accepted" ? `accepted after ${e.recover_s} s, ${e.err_m.toFixed(2)} m from truth` : e.result;
    items.push({ t: e.t_trigger, a, html: `<b style="color: var(${ARM_COL[a.arm]})">${esc(a.label.split(" ")[0])}</b> ${e.t_trigger.toFixed(1)} s, ${esc(e.reason.replace("_", " "))}${esc(mv)}: ${esc(res)}${e.wrong ? ' <span class="badge collision">wrong commit</span>' : ""}` });
  }
  items.sort((x, y) => x.t - y.t || x.a.arm.localeCompare(y.a.arm));
  const ul = $("#relocEvents");
  ul.innerHTML = items.map(it => `<li><button class="ev-btn" data-t="${it.t}" data-a="${esc(it.a.arm)}">${it.html}</button></li>`).join("");
  ul.onclick = e => {
    const b = e.target.closest(".ev-btn"); if (!b) return;
    P.sel.add(b.dataset.a); $(`#relocArms .sarm[data-a="${b.dataset.a}"]`).setAttribute("aria-pressed", "true");
    P.seek(+b.dataset.t - 0.3); P.playing = true;
  };
}

const STORY = [];
function storyTick(now) {
  for (const P of STORY) {
    if (P.playing) {
      const dt = Math.min(0.1, (now - (P.last || now)) / 1000), end = P.end();
      P.t = Math.min(end, P.t + dt * P.speed);
      if (P.t >= end) P.playing = false;
      P.draw();
    }
    P.last = now;
  }
  requestAnimationFrame(storyTick);
}
async function loadStory() {
  const [k, r] = await Promise.allSettled([getJSON(STORY_DIR + "kill_test.json"), getJSON(STORY_DIR + "relocalize.json")]);
  if (k.status === "fulfilled") {
    $("#cardKill").innerHTML = killCard(k.value.headline);
    prepKill(k.value);
    STORY.push(makePlayer("kill", k.value, paintKill, hudKill));
  } else $("#cardKill").innerHTML = `<p class="muted">Could not load kill_test.json (${esc(k.reason.message)}). Run <code>.venv/bin/python export_replay.py</code> in samples/close-area-safety-filter.</p>`;
  if (r.status === "fulfilled") {
    $("#cardReloc").innerHTML = relocCard(r.value.headline);
    prepReloc(r.value);
    const P = makePlayer("reloc", r.value, paintReloc, hudReloc);
    relocEvents(P);
    STORY.push(P);
  } else $("#cardReloc").innerHTML = `<p class="muted">Could not load relocalize.json (${esc(r.reason.message)}). Run <code>.venv/bin/python export_replay.py</code> in samples/close-area-relocalize.</p>`;
  for (const P of STORY) { P.t = REDUCED ? P.end() : 0; P.draw(); }
  if (!REDUCED && "IntersectionObserver" in window) { // play each replay once when it scrolls into view
    const io = new IntersectionObserver(es => es.forEach(e => {
      const P = STORY.find(p => p.cv === e.target);
      if (P && e.isIntersecting && !P.started) { P.started = true; P.playing = true; }
    }), { threshold: 0.5 });
    for (const P of STORY) io.observe(P.cv);
  }
  requestAnimationFrame(storyTick);
}
window.addEventListener("resize", () => STORY.forEach(P => P.draw()));
$("#themeBtn").addEventListener("click", () => STORY.forEach(P => P.draw()));
loadStory();
