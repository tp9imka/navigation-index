"use strict";
// Arena playground (loop-48b). Vanilla JS, no build step, no dependencies.
// The editor holds one close-area-world/1 document (samples/close-area-arena/world_json.py).
// Runs go to worker.js, which executes the hub's real Python arena under Pyodide and returns the trace.
// window.PG is a small API for scripted checks (results/measure_playground.mjs).

const $ = s => document.querySelector(s);
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const STORE_KEY = "navidx-playground-world";
const SCHEMA = "close-area-world/1";
const ND = 4;
const r4 = v => Math.round(v * 1e4) / 1e4;

const LABELS = {
  planner: { straight: "straight line to B", freest_beam: "freest beam (reactive)", astar_known: "A* + ESDF, known map",
    astar_unknown: "A* + ESDF, unknown map", apf: "APF + wall follow", vfh_plus: "VFH+",
    dwa: "DWA (dynamic window)", dwa_mem: "DWA + 3 s scan memory", bug2: "Bug2", tangent_bug: "TangentBug",
    dstar_lite: "D* Lite, unknown map (geofenced)", informed_rrt_star: "Informed RRT* 5000, known map",
    thetastar_known: "Theta* (any-angle), known map", lazy_thetastar_known: "Lazy Theta*, known map",
    lazy_thetastar_unknown: "Lazy Theta*, unknown map (geofenced)",
    mppi: "MPPI, goal only (no global plan)", mppi_astar: "MPPI on the unknown-map A* path",
    hybrid_astar: "Hybrid A*, unknown map (geofenced)" },
  preset: { ideal: "ideal: 72 rays, 360 deg, 6 m", crazyflie: "Crazyflie: 4 cone beams, 3 m", crazyflie_bright: "Crazyflie, bright light: 0.73 m" },
  fault: { truth: "off: planner sees truth", none: "VIO EKF, no fault", jump: "VIO jump 0.5 m", bias: "VIO bias 0.05 m/s, 10 s", dropout: "VIO dropout 2 s" },
  filter: { none: "none", F2: "F2: PX4-CBF on ranges" },
  recovery: { none: "none: VIO EKF only", single: "single: commit to the best match", multi: "multi: hover until one wins",
    multi_ig: "multi + info-gain move" },
};
const DEFAULT_CFG = [
  { planner: "astar_known", preset: "ideal", fault: "truth", filter: "none", recovery: "none" },
  { planner: "freest_beam", preset: "ideal", fault: "truth", filter: "none", recovery: "none" },
];
// VIO loss recovery (pg_reloc.py): active with these faults; the arm flies A* known map, no filter.
const RELOC_FAULTS = ["jump", "dropout"];
const ARMS = ["none", "single", "multi", "multi_ig"];
const ARM_SHORT = { none: "none", single: "single", multi: "multi", multi_ig: "multi+IG" };
// status codes per frame, same order as pg_reloc.STATUS
const STATUS = ["nominal", "lost", "hovering", "moving", "accepted", "wrong"];
const STATUS_LABEL = { nominal: "VIO nominal", lost: "lost (no hypothesis wins)", hovering: "hovering (ambiguous / pending)",
  moving: "info-gain move", accepted: "accepted (re-anchored)", wrong: "wrong commit (> 0.5 m)" };
// worlds outside presets/ that the preset menu also offers (written by results/native_parity.py)
const EXTRA_WORLDS = { reloc_demo_random_1_97: { file: "results/reloc_demo_random_1_97.json",
  label: "VIO-loss demo: random seed 1, layout 97 (jump)", cfg: { fault: "jump", recovery: "multi_ig", seed: 1 } } };
const worldUrl = name => (EXTRA_WORLDS[name] ? EXTRA_WORLDS[name].file : `presets/${encodeURIComponent(name)}.json`);

const S = {
  doc: null, presetName: null, pristine: false, sel: null, tool: "select", undo: [], drag: null,
  runs: null, mode: "edit", t: 0, playing: false, speed: 4, last: 0,
  ready: false, env: null, nextId: 1, pending: new Map(), busy: false, parity: null,
};
window.PG_STATE = S;

// ---------------------------------------------------------------- world document helpers
function blankDoc() {
  return { schema: SCHEMA, frame: "local ENU m, origin at A", family: "custom", seed: 0, index: 0,
    bounds: [0, 0, 20, 20], a: [1.5, 1.5], b: [18.5, 18.5], z: 1.0, radius: 0.15, obstacles: [] };
}

function rectOf(o) {            // [x0, y0, x1, y1] for box and wall
  if (o.type === "box") return [o.cx - o.hx, o.cy - o.hy, o.cx + o.hx, o.cy + o.hy];
  const h = o.thickness / 2;
  if (Math.abs(o.y1 - o.y0) < 1e-9) return [Math.min(o.x0, o.x1), o.y0 - h, Math.max(o.x0, o.x1), o.y0 + h];
  return [o.x0 - h, Math.min(o.y0, o.y1), o.x0 + h, Math.max(o.y0, o.y1)];
}

function moved(o, dx, dy) {
  const n = { ...o };
  if (o.type === "wall") { n.x0 = r4(o.x0 + dx); n.x1 = r4(o.x1 + dx); n.y0 = r4(o.y0 + dy); n.y1 = r4(o.y1 + dy); }
  else { n.cx = r4(o.cx + dx); n.cy = r4(o.cy + dy); }
  return n;
}

function hitObstacle(o, x, y, tol) {
  if (o.type === "cylinder") return Math.hypot(x - o.cx, y - o.cy) <= o.r + tol;
  const [x0, y0, x1, y1] = rectOf(o);
  return x >= x0 - tol && x <= x1 + tol && y >= y0 - tol && y <= y1 + tol;
}

function checkDoc(d) {          // light check; Python's world_json.from_json is the real validator
  if (!d || d.schema !== SCHEMA) throw new Error("not a " + SCHEMA + " document");
  const [x0, y0, x1, y1] = d.bounds || [];
  if (![x0, y0, x1, y1].every(Number.isFinite) || !(x0 < x1 && y0 < y1)) throw new Error("bounds must be [xmin, ymin, xmax, ymax]");
  for (const k of ["a", "b"]) {
    const p = d[k] || (k === "a" ? [0, 0] : null);
    if (!p || !(p[0] > x0 && p[0] < x1 && p[1] > y0 && p[1] < y1)) throw new Error(k.toUpperCase() + " is outside the bounds");
  }
  if (!Array.isArray(d.obstacles)) throw new Error("obstacles must be a list");
  for (const o of d.obstacles) {
    if (!["box", "wall", "cylinder"].includes(o.type)) throw new Error("unsupported obstacle type " + o.type);
    if (o.type === "wall" && Math.abs(o.x1 - o.x0) > 1e-9 && Math.abs(o.y1 - o.y0) > 1e-9) throw new Error("only axis-aligned walls are supported");
  }
  if (!d.a) d.a = [0, 0];
  return d;
}

function worldMsg(text, cls) { const el = $("#worldMsg"); el.textContent = text || ""; el.className = "small " + (cls || ""); }

function dropLink() {           // the world no longer matches a link in the address bar: remove it, so reload does not bring it back
  const keep = new URLSearchParams(location.search).get("pyodide");      // the Pyodide source choice survives
  const want = location.pathname + (keep ? "?pyodide=" + encodeURIComponent(keep) : "");
  if ((/[#&]w=/.test(location.hash) || location.search) && location.pathname + location.search !== want) history.replaceState(null, "", want);
  else if (/[#&]w=/.test(location.hash)) history.replaceState(null, "", want);
}

function setDoc(d, presetName, keepLink) {
  if (!keepLink) dropLink();
  S.doc = checkDoc(JSON.parse(JSON.stringify(d)));
  S.presetName = presetName || null;
  S.pristine = !!presetName;
  S.sel = null; S.undo = [];
  clearRuns();
  syncButtons();
  draw();
}

function pushUndo() {
  S.undo.push(JSON.stringify(S.doc));
  if (S.undo.length > 200) S.undo.shift();
}

function changed() {           // the world was edited: earlier runs no longer match it
  S.pristine = false;
  dropLink();
  clearRuns();
  syncButtons();
  draw();
}

function undo() {
  if (!S.undo.length) return;
  S.doc = JSON.parse(S.undo.pop());
  S.sel = null;
  changed();
}

// ---------------------------------------------------------------- view transform
const cv = $("#arena"), ctx = cv.getContext("2d");
const V = { s: 1, dpr: 1, pad: 0.4 };

function fitCanvas(c) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2), w = c.clientWidth, h = c.clientHeight;
  if (!w || !h) return dpr;
  if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
  return dpr;
}

function view() {
  const [x0, y0, x1, y1] = S.doc.bounds;
  V.dpr = fitCanvas(cv);
  V.s = Math.min(cv.width / (x1 - x0 + 2 * V.pad), cv.height / (y1 - y0 + 2 * V.pad));
  V.x0 = x0; V.y1 = y1;
}
const P = (x, y) => [(x - V.x0 + V.pad) * V.s, (V.y1 + V.pad - y) * V.s];

function worldAt(ev) {
  const b = cv.getBoundingClientRect();
  const px = (ev.clientX - b.left) * (cv.width / b.width), py = (ev.clientY - b.top) * (cv.height / b.height);
  return [px / V.s + V.x0 - V.pad, V.y1 + V.pad - py / V.s];
}
const snapOn = () => $("#snap").checked;
const snap = v => (snapOn() ? Math.round(v * 10) / 10 : r4(v));

// ---------------------------------------------------------------- drawing
function colors() {
  return { bg: css("--panel"), fg: css("--fg"), muted: css("--muted"), line: css("--line"), accent: css("--accent"),
    obst: css("--obst"), est: css("--est"), ok: css("--ok"), bad: css("--bad"), warn: css("--warn"), dark: css("--dark-zone"),
    b: css("--b"), plan: css("--plan"), glass: css("--glass"), c3: css("--c3"), c4: css("--c4") };
}
const runColor = (C, k) => [C.accent, C.b, C.c3, C.c4][k % 4];
const runLabel = k => (S.runLabels && S.runLabels[k]) || (k ? "B" : "A");
function statusColor(C, name) {
  return { nominal: null, lost: C.bad, hovering: C.warn, moving: C.accent, accepted: C.ok, wrong: C.fg }[name];
}

function drawObstacle(o, C, selected) {
  const m = o.material || "matte";
  const s = V.s;
  ctx.save();
  if (m === "glass" || m === "mirror") { ctx.fillStyle = C.glass; ctx.globalAlpha = 0.75; }
  else if (m === "dark") { ctx.fillStyle = C.fg; ctx.globalAlpha = 0.85; }
  else ctx.fillStyle = C.obst;
  if (o.type === "cylinder") {
    const [a, b] = P(o.cx, o.cy);
    ctx.beginPath(); ctx.arc(a, b, Math.max(o.r * s, 1.5 * V.dpr), 0, 2 * Math.PI); ctx.fill();
    if (selected) { ctx.globalAlpha = 1; ctx.strokeStyle = C.accent; ctx.lineWidth = 2.5 * V.dpr; ctx.stroke(); }
  } else {
    const [x0, y0, x1, y1] = rectOf(o), [a, b] = P(x0, y1);
    const w = Math.max((x1 - x0) * s, 1.5 * V.dpr), h = Math.max((y1 - y0) * s, 1.5 * V.dpr);
    ctx.fillRect(a, b, w, h);
    if (selected) { ctx.globalAlpha = 1; ctx.strokeStyle = C.accent; ctx.lineWidth = 2.5 * V.dpr; ctx.strokeRect(a - 2 * V.dpr, b - 2 * V.dpr, w + 4 * V.dpr, h + 4 * V.dpr); }
  }
  ctx.restore();
}

function drawBase(C) {
  const d = S.doc, [x0, y0, x1, y1] = d.bounds, dpr = V.dpr;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, cv.width, cv.height);
  ctx.strokeStyle = C.line; ctx.lineWidth = 1;
  for (let g = Math.ceil(x0); g <= x1; g += 1) {
    ctx.globalAlpha = g % 5 === 0 ? 1 : 0.45; const [a] = P(g, 0);
    ctx.beginPath(); ctx.moveTo(a, P(0, y1)[1]); ctx.lineTo(a, P(0, y0)[1]); ctx.stroke();
  }
  for (let g = Math.ceil(y0); g <= y1; g += 1) {
    ctx.globalAlpha = g % 5 === 0 ? 1 : 0.45; const [, b] = P(0, g);
    ctx.beginPath(); ctx.moveTo(P(x0, 0)[0], b); ctx.lineTo(P(x1, 0)[0], b); ctx.stroke();
  }
  ctx.globalAlpha = 1;
  return { x0, y0, x1, y1, dpr };
}

function drawAB(C, reached) {
  const d = S.doc, dpr = V.dpr, tol = Math.max(0.3 * V.s, 6 * dpr);
  const [ax, ay] = P(d.a[0], d.a[1]), [bx, by] = P(d.b[0], d.b[1]);
  ctx.fillStyle = C.ok; ctx.beginPath(); ctx.arc(ax, ay, tol, 0, 2 * Math.PI); ctx.fill();
  ctx.lineWidth = 3 * dpr; ctx.strokeStyle = C.bad; ctx.beginPath(); ctx.arc(bx, by, tol, 0, 2 * Math.PI); ctx.stroke();
  if (reached) { ctx.fillStyle = C.ok; ctx.globalAlpha = 0.6; ctx.fill(); ctx.globalAlpha = 1; }
  ctx.fillStyle = C.fg; ctx.font = `700 ${13 * dpr}px system-ui, sans-serif`; ctx.textBaseline = "middle";
  ctx.fillText("A", ax + tol + 3 * dpr, ay - tol);
  ctx.fillText("B", bx + tol + 3 * dpr, by - tol);
  if ((S.sel === "a" || S.sel === "b") && S.mode === "edit") {
    const [x, y] = S.sel === "a" ? [ax, ay] : [bx, by];
    ctx.strokeStyle = C.accent; ctx.lineWidth = 2 * dpr; ctx.beginPath(); ctx.arc(x, y, tol + 4 * dpr, 0, 2 * Math.PI); ctx.stroke();
  }
}

function frameAt(run, t) {      // last frame index with frames[i][0] <= t
  const F = run.frames;
  let lo = 0, hi = F.length - 1;
  if (hi < 0) return -1;
  if (t >= F[hi][0]) return hi;
  while (lo < hi) { const m = (lo + hi + 1) >> 1; if (F[m][0] <= t) lo = m; else hi = m - 1; }
  return lo;
}

function drawDarkZones(C) {     // under the obstacles; drawn once per distinct zone (A and B share them on one seed)
  const seen = new Set(), dpr = V.dpr;
  for (const run of S.runs) {
    const [ox, oy] = run.offset;
    for (const z of run.dark_zones || []) {
      const key = z.join(","); if (seen.has(key)) continue; seen.add(key);
      const [a, b] = P(z[0] + ox, z[3] + oy), [c, d] = P(z[2] + ox, z[1] + oy);
      ctx.fillStyle = C.dark; ctx.fillRect(a, b, c - a, d - b);
      ctx.setLineDash([4 * dpr, 4 * dpr]); ctx.strokeStyle = C.muted; ctx.lineWidth = 1 * dpr; ctx.strokeRect(a, b, c - a, d - b); ctx.setLineDash([]);
    }
  }
}

function drawRun(run, col, C, primary, slot) {
  const dpr = V.dpr, [ox, oy] = run.offset, T = S.t, s = V.s;
  const Q = (x, y) => P(x + ox, y + oy);
  const i = frameAt(run, T);
  if (i < 0) return;
  const F = run.frames, f = F[i], done = T >= run.end[0] - 1e-6;
  // planned path (latest snapshot)
  let path = null;
  for (const [pt, pts] of run.paths) { if (pt <= T) path = pts; else break; }
  if (path && path.length > 1) {
    ctx.strokeStyle = primary ? C.plan : col; ctx.globalAlpha = primary ? 0.9 : 0.5; ctx.lineWidth = 1.6 * dpr; ctx.setLineDash([2 * dpr, 4 * dpr]);
    ctx.beginPath(); path.forEach(([x, y], k) => { const [a, b] = Q(x, y); k ? ctx.lineTo(a, b) : ctx.moveTo(a, b); }); ctx.stroke();
    ctx.setLineDash([]); ctx.globalAlpha = 1;
  }
  // range beams at this frame
  const scanD = f[9], ang = run.scan_angles, [tx, ty] = Q(f[1], f[2]);
  if (scanD && ang.length && (primary || S.runs.length <= 2)) {      // 3+ runs: beams of the first run only
    ctx.lineWidth = 1 * dpr;
    for (let k = 0; k < ang.length; k++) {
      const d = scanD[k], hitp = d != null, L = hitp ? d : run.max_range, a = f[3] + ang[k];
      const [ex, ey] = Q(f[1] + L * Math.cos(a), f[2] + L * Math.sin(a));
      ctx.strokeStyle = col; ctx.globalAlpha = hitp ? 0.28 : 0.08;
      ctx.beginPath(); ctx.moveTo(tx, ty); ctx.lineTo(ex, ey); ctx.stroke();
      if (hitp) { ctx.globalAlpha = 0.7; ctx.fillStyle = col; ctx.fillRect(ex - 1.5 * dpr, ey - 1.5 * dpr, 3 * dpr, 3 * dpr); }
    }
    ctx.globalAlpha = 1;
  }
  // estimate (what the planner believed)
  const hasEst = run.config.fault !== "truth";
  if (hasEst) {
    ctx.strokeStyle = primary ? C.est : col; ctx.lineWidth = 2 * dpr; ctx.setLineDash([6 * dpr, 5 * dpr]); ctx.globalAlpha = primary ? 1 : 0.7;
    ctx.beginPath(); for (let k = 0; k <= i; k++) { const [a, b] = Q(F[k][4], F[k][5]); k ? ctx.lineTo(a, b) : ctx.moveTo(a, b); } ctx.stroke();
    ctx.setLineDash([]);
    const [ex, ey] = Q(f[4], f[5]), sg = f[6] || 0;
    ctx.globalAlpha = 0.18; ctx.fillStyle = primary ? C.est : col; ctx.beginPath(); ctx.arc(ex, ey, Math.max(2 * sg * s, 3 * dpr), 0, 2 * Math.PI); ctx.fill();
    ctx.globalAlpha = 1; ctx.beginPath(); ctx.arc(ex, ey, 3.5 * dpr, 0, 2 * Math.PI); ctx.fill();
  }
  // truth path
  ctx.strokeStyle = col; ctx.lineWidth = 3 * dpr; ctx.lineJoin = "round"; ctx.beginPath();
  for (let k = 0; k <= i; k++) { const [a, b] = Q(F[k][1], F[k][2]); k ? ctx.lineTo(a, b) : ctx.moveTo(a, b); }
  let vx = f[1], vy = f[2];
  if (done) { vx = run.end[1]; vy = run.end[2]; }
  { const [a, b] = Q(vx, vy); ctx.lineTo(a, b); }
  ctx.stroke();
  // fault marker
  const fl = run.fault_log;
  if (fl && fl.fired_t != null && T >= fl.fired_t) {
    const k = frameAt(run, fl.fired_t), [fx, fy] = Q(F[k][1], F[k][2]);
    ctx.strokeStyle = C.bad; ctx.lineWidth = 2 * dpr; ctx.beginPath(); ctx.arc(fx, fy, (9 + 4 * slot) * dpr, 0, 2 * Math.PI); ctx.stroke();
    ctx.fillStyle = C.bad; ctx.font = `700 ${12 * dpr}px system-ui, sans-serif`;
    ctx.fillText(`${S.runs.length > 1 ? runLabel(slot) + " " : ""}${fl.fault} ${fl.fired_t} s`, fx + 14 * dpr, fy - 10 * dpr + slot * 16 * dpr);
  }
  drawReloc(run, col, C, Q, T, i);
  // vehicle: true size disc + heading
  const [a, b] = Q(vx, vy), rr = Math.max(run.radius * s, 4 * dpr);
  ctx.fillStyle = col; ctx.beginPath(); ctx.arc(a, b, rr, 0, 2 * Math.PI); ctx.fill();
  ctx.strokeStyle = C.bg; ctx.lineWidth = 2 * dpr; ctx.beginPath(); ctx.moveTo(a, b);
  ctx.lineTo(a + Math.cos(f[3]) * rr * 1.6, b - Math.sin(f[3]) * rr * 1.6); ctx.stroke();
  if (done && run.score.outcome !== "reached") {
    ctx.strokeStyle = run.score.outcome === "collision" ? C.bad : C.warn; ctx.lineWidth = 3 * dpr;
    const q = 8 * dpr; ctx.beginPath(); ctx.moveTo(a - q, b - q); ctx.lineTo(a + q, b + q); ctx.moveTo(a + q, b - q); ctx.lineTo(a - q, b + q); ctx.stroke();
  }
}

// Relocalization overlay: hypotheses as ghost markers (the last GHOST_S seconds, older = fainter,
// alpha also scaled by score / best), accepted poses (ring; dark cross = wrong commit) and info-gain moves (blue arrow).
const GHOST_S = 2.0;
function drawReloc(run, col, C, Q, T, i) {
  const R = run.reloc;
  if (!R || R.arm === "none") return;
  const dpr = V.dpr, s = V.s, F = run.frames, sep = (R.params && R.params.SEP_M) || 0.5;
  const few = S.runs.length <= 2;
  let cur = null;
  for (const rec of R.hyps) {
    const [t, hs] = rec;
    if (t > T) break;
    if (T - t > GHOST_S) continue;
    cur = rec;
    const age = (T - t) / GHOST_S, best = hs[0][2] || 1;
    hs.forEach(([x, y, sc]) => {
      const [a, b] = Q(x, y);
      ctx.globalAlpha = Math.max(0.05, 0.55 * (1 - age) * Math.max(0, sc / best));
      ctx.strokeStyle = col; ctx.lineWidth = 1.5 * dpr;
      ctx.beginPath(); ctx.arc(a, b, Math.max(sep / 2 * s, 5 * dpr), 0, 2 * Math.PI); ctx.stroke();
    });
  }
  if (cur && T - cur[0] < 0.15) {            // the set from the scan at this frame
    const best = cur[1][0][2] || 1;
    cur[1].forEach(([x, y, sc], k) => {
      const [a, b] = Q(x, y);
      ctx.globalAlpha = Math.max(0.25, sc / best);
      ctx.fillStyle = col; ctx.beginPath(); ctx.arc(a, b, 3.5 * dpr, 0, 2 * Math.PI); ctx.fill();
      ctx.strokeStyle = col; ctx.lineWidth = (k ? 1.5 : 2.5) * dpr; ctx.setLineDash(k ? [3 * dpr, 3 * dpr] : []);
      ctx.beginPath(); ctx.arc(a, b, Math.max(sep / 2 * s, 5 * dpr), 0, 2 * Math.PI); ctx.stroke(); ctx.setLineDash([]);
      if (few) { ctx.globalAlpha = 1; ctx.fillStyle = C.fg; ctx.font = `${10 * dpr}px system-ui, sans-serif`; ctx.fillText(sc.toFixed(2), a + 6 * dpr, b - 8 * dpr); }
    });
  }
  ctx.globalAlpha = 1;
  for (const ev of R.events) {
    for (const mv of ev.moves || []) {     // info-gain move: arrow from the estimate when it started
      if (!mv.move || mv.t > T) continue;
      const k = frameAt(run, mv.t), [a, b] = Q(F[k][4], F[k][5]), [c, d] = Q(F[k][4] + mv.move[0], F[k][5] + mv.move[1]);
      ctx.strokeStyle = C.accent; ctx.lineWidth = 2.5 * dpr; ctx.beginPath(); ctx.moveTo(a, b); ctx.lineTo(c, d); ctx.stroke();
      const ang = Math.atan2(d - b, c - a), h = 8 * dpr;
      ctx.beginPath(); ctx.moveTo(c, d); ctx.lineTo(c - h * Math.cos(ang - 0.45), d - h * Math.sin(ang - 0.45));
      ctx.lineTo(c - h * Math.cos(ang + 0.45), d - h * Math.sin(ang + 0.45)); ctx.closePath(); ctx.fillStyle = C.accent; ctx.fill();
    }
    if (ev.result !== "accepted" || ev.t_end == null || ev.t_end > T || !ev.accepted_xy) continue;
    const [a, b] = Q(ev.accepted_xy[0], ev.accepted_xy[1]), wrong = ev.err_m > ((R.params && R.params.WRONG_M) || 0.5);
    const fresh = T - ev.t_end < 3, r = (fresh ? 9 : 5) * dpr;
    ctx.strokeStyle = wrong ? C.fg : C.ok; ctx.lineWidth = (fresh ? 2.5 : 1.5) * dpr;
    ctx.beginPath(); ctx.arc(a, b, r, 0, 2 * Math.PI); ctx.stroke();
    if (wrong) { ctx.beginPath(); ctx.moveTo(a - r, b - r); ctx.lineTo(a + r, b + r); ctx.moveTo(a + r, b - r); ctx.lineTo(a - r, b + r); ctx.stroke(); }
    if (fresh && few) {
      ctx.fillStyle = wrong ? C.fg : C.ok; ctx.font = `700 ${11 * dpr}px system-ui, sans-serif`;
      ctx.fillText(`${wrong ? "wrong commit" : "accepted"} ${ev.err_m.toFixed(2)} m`, a + r + 4 * dpr, b + 12 * dpr);
    }
  }
}

function draw() {
  if (!S.doc) return;
  view();
  const C = colors();
  const { x0, y0, x1, y1, dpr } = drawBase(C);
  if (S.mode === "replay" && S.runs) drawDarkZones(C);
  S.doc.obstacles.forEach((o, k) => drawObstacle(o, C, S.mode === "edit" && S.sel === k));
  { const [a, b] = P(x0, y1); ctx.strokeStyle = C.obst; ctx.lineWidth = 4 * dpr; ctx.strokeRect(a, b, (x1 - x0) * V.s, (y1 - y0) * V.s); }
  let reached = false;
  if (S.mode === "replay" && S.runs) {
    S.runs.forEach((r, k) => drawRun(r, runColor(C, k), C, k === 0, k));
    reached = S.runs.some(r => r.score.outcome === "reached" && S.t >= r.end[0] - 1e-6);
  }
  drawAB(C, reached);
  const g = S.drag;
  if (g && g.kind !== "move") {        // preview of the shape being drawn
    const o = shapeFrom(g);
    if (o) { ctx.globalAlpha = 0.55; drawObstacle(o, C, true); ctx.globalAlpha = 1; }
  }
  drawSpark(C);
}

// ---------------------------------------------------------------- editor input
function shapeFrom(g) {
  const [ax, ay] = g.p0, [bx, by] = g.p1, dx = bx - ax, dy = by - ay;
  if (g.kind === "box") {
    if (Math.abs(dx) < 0.1 || Math.abs(dy) < 0.1) return null;
    return { type: "box", cx: r4((ax + bx) / 2), cy: r4((ay + by) / 2), hx: r4(Math.abs(dx) / 2), hy: r4(Math.abs(dy) / 2), material: "matte", tag: "box" };
  }
  if (g.kind === "cylinder") {
    const r = Math.hypot(dx, dy);
    return { type: "cylinder", cx: r4(ax), cy: r4(ay), r: r4(r < 0.05 ? 0.25 : snapOn() ? Math.max(0.05, Math.round(r * 20) / 20) : r), material: "matte", tag: "pole" };
  }
  const glass = g.kind === "glass", th = glass ? 0.04 : 0.1;
  const o = Math.abs(dx) >= Math.abs(dy)
    ? { type: "wall", x0: r4(Math.min(ax, bx)), y0: r4(ay), x1: r4(Math.max(ax, bx)), y1: r4(ay), thickness: th }
    : { type: "wall", x0: r4(ax), y0: r4(Math.min(ay, by)), x1: r4(ax), y1: r4(Math.max(ay, by)), thickness: th };
  if (Math.hypot(o.x1 - o.x0, o.y1 - o.y0) < 0.1) return null;
  o.material = glass ? "glass" : "matte";
  o.tag = glass ? "glass" : "wall";
  return o;
}

function pickAt(x, y) {
  const tolAB = Math.max(0.35, 10 * V.dpr / V.s), tol = 6 * V.dpr / V.s, d = S.doc;
  if (Math.hypot(x - d.b[0], y - d.b[1]) <= tolAB) return "b";
  if (Math.hypot(x - d.a[0], y - d.a[1]) <= tolAB) return "a";
  for (let k = d.obstacles.length - 1; k >= 0; k--) if (hitObstacle(d.obstacles[k], x, y, tol)) return k;
  return null;
}

cv.addEventListener("pointerdown", ev => {
  if (!S.doc || S.mode !== "edit") return;
  view();
  const [x, y] = worldAt(ev), p = [snap(x), snap(y)];
  if (S.tool === "select") {
    const hit = pickAt(x, y);
    S.sel = hit;
    if (hit != null) {
      const orig = hit === "a" || hit === "b" ? S.doc[hit].slice() : { ...S.doc.obstacles[hit] };
      S.drag = { kind: "move", start: p, orig, pushed: false };
    }
  } else {
    S.drag = { kind: S.tool, p0: p, p1: p };
  }
  try { cv.setPointerCapture(ev.pointerId); } catch (err) { /* old browser */ }
  syncButtons(); draw();
  ev.preventDefault();
});

cv.addEventListener("pointermove", ev => {
  const g = S.drag; if (!g) return;
  const [x, y] = worldAt(ev), p = [snap(x), snap(y)];
  if (g.kind === "move") {
    const dx = r4(p[0] - g.start[0]), dy = r4(p[1] - g.start[1]);
    if (!dx && !dy && !g.pushed) return;
    if (!g.pushed) { pushUndo(); g.pushed = true; }
    if (S.sel === "a" || S.sel === "b") {
      const [bx0, by0, bx1, by1] = S.doc.bounds, e = 0.05;
      S.doc[S.sel] = [r4(Math.min(bx1 - e, Math.max(bx0 + e, g.orig[0] + dx))), r4(Math.min(by1 - e, Math.max(by0 + e, g.orig[1] + dy)))];
    } else S.doc.obstacles[S.sel] = moved(g.orig, dx, dy);
    if (S.runs) clearRuns();
    S.pristine = false;
  } else g.p1 = p;
  draw();
});

function endDrag() {
  const g = S.drag; S.drag = null;
  if (!g) return;
  if (g.kind === "move") { if (g.pushed) changed(); return; }
  const o = shapeFrom(g);
  if (o) { pushUndo(); S.doc.obstacles.push(o); S.sel = S.doc.obstacles.length - 1; changed(); }
  else draw();
}
cv.addEventListener("pointerup", endDrag);
cv.addEventListener("pointercancel", endDrag);

function setTool(t) {
  S.tool = t;
  document.querySelectorAll(".tool").forEach(b => b.setAttribute("aria-pressed", String(b.dataset.tool === t)));
  cv.classList.toggle("select", t === "select");
  if (S.mode !== "edit") setMode("edit");
}
document.querySelectorAll(".tool").forEach(b => b.addEventListener("click", () => setTool(b.dataset.tool)));

function deleteSel() {
  if (typeof S.sel !== "number") return;
  pushUndo(); S.doc.obstacles.splice(S.sel, 1); S.sel = null; changed();
}
$("#delBtn").onclick = deleteSel;
$("#undoBtn").onclick = undo;
$("#matSel").onchange = () => {
  if (typeof S.sel !== "number") return;
  pushUndo(); S.doc.obstacles[S.sel] = { ...S.doc.obstacles[S.sel], material: $("#matSel").value }; changed();
};

document.addEventListener("keydown", ev => {
  const typing = /^(INPUT|SELECT|TEXTAREA)$/.test((ev.target && ev.target.tagName) || "");
  if ((ev.ctrlKey || ev.metaKey) && ev.key.toLowerCase() === "z" && !typing) { ev.preventDefault(); undo(); return; }
  if (typing || ev.ctrlKey || ev.metaKey || ev.altKey) return;
  if (ev.key === "Delete" || ev.key === "Backspace") { if (typeof S.sel === "number" && S.mode === "edit") { ev.preventDefault(); deleteSel(); } return; }
  const t = { v: "select", b: "box", w: "wall", c: "cylinder", g: "glass" }[ev.key.toLowerCase()];
  if (t) setTool(t);
  if (ev.key === " " && S.mode === "replay") { ev.preventDefault(); togglePlay(); }
});

function syncButtons() {
  const obs = typeof S.sel === "number";
  $("#delBtn").disabled = !obs || S.mode !== "edit";
  $("#undoBtn").disabled = !S.undo.length;
  $("#matSel").disabled = !obs || S.mode !== "edit";
  if (obs) $("#matSel").value = S.doc.obstacles[S.sel].material || "matte";
  $("#runBtn").disabled = !S.ready || S.busy;
}

// ---------------------------------------------------------------- files, presets, storage
async function loadPresets() {
  const r = await fetch("presets/index.json");
  if (!r.ok) throw new Error(r.status + " presets/index.json");
  const idx = await r.json();
  $("#presetSel").innerHTML = '<option value="">choose...</option>' + idx.presets.map(p =>
    `<option value="${esc(p.file.replace(/\.json$/, ""))}">${esc(p.label)} (seed ${p.seed}, layout ${p.index})</option>`).join("") +
    Object.entries(EXTRA_WORLDS).map(([k, w]) => `<option value="${esc(k)}">${esc(w.label)}</option>`).join("");
  return idx;
}

async function loadPreset(name) {
  const r = await fetch(worldUrl(name));
  if (!r.ok) throw new Error(r.status + " preset " + name);
  setDoc(await r.json(), name);
  $("#presetSel").value = name;
  const x = EXTRA_WORLDS[name];
  if (x) {                       // the demo world comes with its config: seed 1, jump, all arms
    setCfg(0, x.cfg);
    if ($("#compare").checked) { $("#compare").checked = false; $("#compare").onchange(); }
    $("#armsCmp").checked = !$("#armsCmp").disabled;
    worldMsg(`${x.label}: world.make_world("random", 1, 97) through world_json (synthetic), the demo-script H1 case. ` +
      "Set: seed 1, VIO jump, compare all recovery arms. Press Run.", "");
  } else worldMsg(`Preset ${name}: exported with world_json.to_json from the seeded generator (synthetic).`, "");
}
$("#presetSel").onchange = () => { const v = $("#presetSel").value; if (v) loadPreset(v).catch(err => worldMsg(err.message, "bad")); };
$("#newBtn").onclick = () => { setDoc(blankDoc(), null); $("#presetSel").value = ""; worldMsg("Empty 20 x 20 m walled area. Draw obstacles, drag A and B.", ""); };

$("#saveBtn").onclick = () => {
  const blob = new Blob([JSON.stringify(S.doc, null, 1) + "\n"], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${S.presetName || S.doc.family || "custom"}${S.pristine ? "" : "_edited"}.json`;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
};

$("#fileIn").onchange = ev => {
  const f = ev.target.files && ev.target.files[0];
  if (!f) return;
  const rd = new FileReader();
  rd.onload = () => {
    try { setDoc(JSON.parse(rd.result), null); $("#presetSel").value = ""; worldMsg(`Opened ${f.name}.`, "ok"); }
    catch (err) { worldMsg(`Could not open ${f.name}: ${err.message}`, "bad"); }
  };
  rd.readAsText(f);
  ev.target.value = "";
};

$("#storeBtn").onclick = () => {
  try { localStorage.setItem(STORE_KEY, JSON.stringify(S.doc)); worldMsg("Saved in this browser.", "ok"); }
  catch (err) { worldMsg("This browser blocks storage: " + err.message, "bad"); }
};
$("#restoreBtn").onclick = () => {
  try {
    const t = localStorage.getItem(STORE_KEY);
    if (!t) { worldMsg("Nothing saved in this browser yet.", ""); return; }
    setDoc(JSON.parse(t), null); $("#presetSel").value = ""; worldMsg("Loaded the world saved in this browser.", "ok");
  } catch (err) { worldMsg("Could not load from browser storage: " + err.message, "bad"); }
};

// ---------------------------------------------------------------- config panel
function buildCfg(which, cfg) {
  const fs = $(which === 0 ? "#cfgA" : "#cfgB"), id = which === 0 ? "A" : "B";
  const rows = [["planner", "Planner"], ["preset", "Sensor"], ["fault", "VIO fault"], ["recovery", "VIO loss recovery"], ["filter", "Filter"]];
  fs.insertAdjacentHTML("beforeend", rows.map(([k, lbl]) =>
    `<label>${lbl}<select id="${id}_${k}" aria-label="${lbl} ${id}">` +
    Object.entries(LABELS[k]).map(([v, t]) => `<option value="${v}"${cfg[k] === v ? " selected" : ""}>${esc(t)}</option>`).join("") +
    `</select></label>`).join(""));
  for (const k of ["fault", "recovery"]) $(`#${id}_${k}`).addEventListener("change", () => lockCfg(id));
}
buildCfg(0, DEFAULT_CFG[0]);
buildCfg(1, DEFAULT_CFG[1]);

// Recovery is offered with the jump or dropout fault only. An arm brings its own planner (A* + ESDF
// known map behind the hover gate, as run_disambiguate.py) and runs without the F2 filter.
function lockCfg(id) {
  const rec = $(`#${id}_recovery`), fault = $(`#${id}_fault`).value;
  const can = RELOC_FAULTS.includes(fault) && !(S.env && S.env.recovery && S.env.recovery.length < 2);
  if (!can) rec.value = "none";
  rec.disabled = !can;
  const on = rec.value !== "none";
  if (on) { $(`#${id}_planner`).value = "astar_known"; $(`#${id}_filter`).value = "none"; }
  $(`#${id}_planner`).disabled = on; $(`#${id}_filter`).disabled = on;
  if (id === "A") syncArms();
}

function readCfg(which) {
  const id = which === 0 ? "A" : "B", o = {};
  for (const k of CFG_KEYS) o[k] = $(`#${id}_${k}`).value;
  o.seed = Math.max(0, Math.min(9999, parseInt($("#seed").value, 10) || 0));
  return o;
}
function setCfg(which, cfg) {
  const id = which === 0 ? "A" : "B";
  // fault first, so the recovery select is enabled before its value is set
  const keys = Object.keys(cfg).sort((a, b) => (b === "fault") - (a === "fault"));
  for (const k of keys) {
    const v = cfg[k];
    if (k === "seed") $("#seed").value = v;
    else if ($(`#${id}_${k}`)) { $(`#${id}_${k}`).value = v; if (k === "fault") lockCfg(id); }
  }
  lockCfg(id);
}
$("#compare").onchange = () => {
  if ($("#compare").checked) $("#armsCmp").checked = false;
  $("#cfgB").hidden = !$("#compare").checked;
  $(".cfgs").classList.toggle("two", $("#compare").checked);
};
// Compare all recovery arms: config A with each of none / single / multi / multi + IG on one world.
function syncArms() {
  const ok = RELOC_FAULTS.includes($("#A_fault").value) && !$("#A_recovery").disabled;
  $("#armsCmp").disabled = !ok;
  if (!ok) $("#armsCmp").checked = false;
}
$("#armsCmp").onchange = () => {
  if ($("#armsCmp").checked && $("#compare").checked) { $("#compare").checked = false; $("#compare").onchange(); }
};
lockCfg("A"); lockCfg("B");
const armsCfgs = a => ARMS.map(arm => ({ ...a, recovery: arm, ...(arm !== "none" ? { planner: "astar_known", filter: "none" } : {}) }));

function applyEnv(env) {        // disable options the worker could not load
  for (const id of ["A", "B"]) {
    for (const o of $(`#${id}_planner`).options) o.disabled = !env.planners.includes(o.value);
    for (const o of $(`#${id}_filter`).options) o.disabled = !env.filters.includes(o.value);
    for (const o of $(`#${id}_recovery`).options) o.disabled = !(env.recovery || ["none"]).includes(o.value);
    lockCfg(id);
  }
  const errs = Object.entries(env.load_errors || {}).map(([k, v]) => `${k}: ${v}`).join("; ");
  $("#envMsg").textContent = `Pyodide ${env.pyodide} from ${env.pyodide_source === "local" ? "the local folder " + env.pyodide_base : "cdn.jsdelivr.net"}, ` +
    `Python ${env.python}, numpy ${env.numpy}, scipy ${env.scipy}; ${env.arena_files} hub .py files loaded.` + (errs ? " Not loaded: " + errs : "");
}

// ---------------------------------------------------------------- shareable link
// URL = page ? config query params # w=<world JSON, deflate (zlib, CompressionStream), base64url>.
// Params: planner, preset, fault, filter, recovery (config A), the same with _b (config B), compare=1,
// arms=1 (compare all recovery arms on config A), seed,
// src=<preset name> when the world is an unedited preset (only used to show the native parity note).
const CFG_KEYS = ["planner", "preset", "fault", "filter", "recovery"];

function b64url(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
function unb64url(text) {
  const t = text.replace(/-/g, "+").replace(/_/g, "/"), bin = atob(t + "===".slice((t.length + 3) % 4));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
async function pipeBytes(bytes, stream) {
  const buf = await new Response(new Blob([bytes]).stream().pipeThrough(stream)).arrayBuffer();
  return new Uint8Array(buf);
}
async function encodeWorld(doc) {
  return b64url(await pipeBytes(new TextEncoder().encode(JSON.stringify(doc)), new CompressionStream("deflate")));
}
async function decodeWorld(text) {
  let bytes;
  try { bytes = await pipeBytes(unb64url(text), new DecompressionStream("deflate")); }
  catch (err) { throw new Error("w= is not deflate + base64url data"); }
  return JSON.parse(new TextDecoder().decode(bytes));
}

async function shareUrl() {
  const q = new URLSearchParams(), cmp = $("#compare").checked, a = readCfg(0);
  for (const k of CFG_KEYS) q.set(k, a[k]);
  if (cmp) { const b = readCfg(1); q.set("compare", "1"); for (const k of CFG_KEYS) q.set(k + "_b", b[k]); }
  if ($("#armsCmp").checked) q.set("arms", "1");
  q.set("seed", String(a.seed));
  if (S.pristine && S.presetName) q.set("src", S.presetName);
  return location.origin + location.pathname + "?" + q.toString() + "#w=" + await encodeWorld(S.doc);
}

function cfgFromQuery(q, suffix) {     // unknown values are dropped, the panel keeps its default
  const c = {}, bad = [];
  for (const k of CFG_KEYS) {
    const v = q.get(k + suffix);
    if (v == null) continue;
    if (Object.prototype.hasOwnProperty.call(LABELS[k], v)) c[k] = v; else bad.push(`${k}${suffix}=${v}`);
  }
  return [c, bad];
}

// Restore world + config from the current URL. Returns true when the link held a world.
async function restoreFromUrl() {
  const h = new URLSearchParams(location.hash.replace(/^#/, ""));
  const w = h.get("w");
  if (!w) return false;
  const doc = await decodeWorld(w);
  const q = new URLSearchParams(location.search);
  setDoc(doc, null, true);
  $("#presetSel").value = "";
  const src = q.get("src");
  if (src && /^[a-z0-9_]+$/.test(src)) {         // same world as the preset file? then the parity note applies
    try {
      const r = await fetch(worldUrl(src));
      if (r.ok && JSON.stringify(await r.json()) === JSON.stringify(S.doc)) { S.presetName = src; S.pristine = true; $("#presetSel").value = src; }
    } catch (err) { /* parity note only */ }
  }
  const [ca, badA] = cfgFromQuery(q, ""), [cb, badB] = cfgFromQuery(q, "_b");
  const seed = parseInt(q.get("seed"), 10);
  if (Number.isFinite(seed)) ca.seed = Math.max(0, Math.min(9999, seed));
  setCfg(0, ca); setCfg(1, cb);
  $("#compare").checked = q.get("compare") === "1"; $("#compare").onchange();
  $("#armsCmp").checked = q.get("arms") === "1" && !$("#armsCmp").disabled; $("#armsCmp").onchange();
  const bad = badA.concat(badB);
  worldMsg(`World and config restored from the link (${doc.obstacles.length} obstacles).` + (bad.length ? " Ignored: " + bad.join(", ") : ""), bad.length ? "bad" : "ok");
  S.fromLink = true;
  return true;
}

$("#linkBtn").onclick = async () => {
  try {
    const url = await shareUrl();
    S.lastLink = url;
    history.replaceState(null, "", url);
    let copied = false;
    try { await navigator.clipboard.writeText(url); copied = true; } catch (err) { /* blocked: the address bar has it */ }
    worldMsg((copied ? "Link copied" : "Clipboard blocked; the link is in the address bar") +
      ` (${url.length} characters). Opening it restores this world and config and runs it.`, "ok");
  } catch (err) { worldMsg("Could not build a link: " + err.message, "bad"); }
};

// ---------------------------------------------------------------- worker
// The worker retries each load step itself (worker.js step()). When it gives up, or the load runs
// longer than SLOW_S, the Retry button starts a fresh worker. readyP resolves on the first ready.
// ?pyodide=cdn|local|auto in the page URL is passed on to the worker (manifest.json pyodide_source).
const WORKER_URL = "worker.js?v=20261110c";   // bump when worker.js changes (also solver.js WORKER_V)
const SLOW_S = 45;
const PYODIDE_Q = (q => (/^(cdn|local|auto)$/.test(q || "") ? q : null))(new URLSearchParams(location.search).get("pyodide"));
let worker = null, readyResolve;
const readyP = new Promise(ok => { readyResolve = ok; });
const T_LOAD0 = performance.now();
S.load = { attempt: 0, failed: false, retries: [], message: "" };

function loadText(text, bad) {
  $("#loadText").textContent = text;
  $("#load").classList.toggle("err", !!bad);
}
function showRetry(on, why) {
  $("#retryBtn").hidden = !on;
  if (on && why) $("#retryBtn").title = why;
}

function startWorker() {
  if (worker) worker.terminate();
  for (const p of S.pending.values()) p.fail(new Error("Python restarted"));
  S.pending.clear();
  S.load.attempt += 1; S.load.failed = false; S.load.t0 = performance.now(); S.loadStage = "";
  const url = WORKER_URL + (PYODIDE_Q ? "&pyodide=" + PYODIDE_Q : "");
  const w = new Worker(url, { type: "module" });
  worker = w;
  showRetry(false);
  $("#load").classList.remove("done", "err");
  $("#loadBar").value = 0;
  loadText(S.load.attempt > 1 ? `Retry ${S.load.attempt - 1}: loading Python again...` : "Loading Python (about 22 MB on first visit, cached after)...");
  clearTimeout(S.load.slowTimer);
  S.load.slowTimer = setTimeout(() => {
    if (!S.ready && worker === w) {
      showRetry(true, "Start the load again in a fresh worker");
      $("#loadText").textContent += ` Still loading after ${SLOW_S} s: press Retry to start again.`;
    }
  }, SLOW_S * 1000);
  w.onmessage = ev => { if (worker === w) onWorkerMsg(ev.data); };
  w.onerror = ev => {
    if (worker !== w) return;
    S.load.failed = true; S.load.message = "Worker failed: " + (ev.message || "unknown error");
    loadText(S.load.message, true); showRetry(true);
  };
}

function onWorkerMsg(m) {
  if (m.type === "progress") {
    const exp = m.mb_expected || 22;
    const pct = m.stage === "ready" ? 100 : Math.min(97, Math.round(100 * (m.mb || 0) / exp));
    $("#loadBar").value = pct;
    if (m.stage) S.loadStage = `step ${m.step} of ${m.steps}: ${m.stage}`;
    loadText(`Loading Python: ${S.loadStage || ""} (${(m.mb || 0).toFixed(1)} of about ${exp} MB downloaded)`);
  } else if (m.type === "retry") {
    S.load.retries.push(m);
    loadText(`${m.step}: attempt ${m.attempt} of ${m.attempts} failed (${m.error}). Trying again in ${m.wait_s} s...`, true);
    showRetry(true, "Start the load again now in a fresh worker");
  } else if (m.type === "ready") {
    S.ready = true; S.env = m.env; S.loadTimings = m.timings; S.loadMb = m.mb;
    S.readyMs = Math.round(performance.now() - T_LOAD0);
    clearTimeout(S.load.slowTimer); showRetry(false);
    $("#load").classList.add("done");
    const tries = (m.env.load_attempts || []).filter(a => !a.ok).length;
    loadText(`Python ready in ${(S.readyMs / 1000).toFixed(1)} s (${m.mb} MB downloaded this visit; cached after)` +
      (S.load.attempt > 1 || tries ? `; Retry pressed ${S.load.attempt - 1} time(s), ${tries} automatic retries in this worker.` : "."));
    $("#runMsg").textContent = "Ready.";
    applyEnv(m.env); syncButtons(); readyResolve(m.env);
  } else if (m.type === "result" || m.type === "error") {
    if (m.fatal) {
      S.load.failed = true; S.load.message = m.message; S.load.attempts = m.attempts;
      clearTimeout(S.load.slowTimer);
      loadText(m.message + ". Needs cdn.jsdelivr.net, or a local Pyodide folder (README: Offline / blocked CDN).", true);
      showRetry(true, "Start the load again in a fresh worker");
      return;
    }
    const p = S.pending.get(m.id); if (!p) return;
    S.pending.delete(m.id);
    m.type === "result" ? p.ok(m.result) : p.fail(new Error(m.message));
  }
}
function retryLoad() { if (!S.ready) startWorker(); }
$("#retryBtn").onclick = retryLoad;
startWorker();

function runInWorker(world, cfg) {
  const id = S.nextId++;
  return new Promise((ok, fail) => { S.pending.set(id, { ok, fail }); worker.postMessage({ type: "run", id, world, cfg }); });
}

// cfgs: scripted run (1 or 2 configs, shown in the panel). opts.arms: compare all recovery arms on config A.
async function runNow(cfgs, opts) {
  if (S.busy) return null;
  try { checkDoc(S.doc); } catch (err) { runMsg(err.message, true); return null; }
  if (cfgs) {                    // scripted run: show the configs it uses in the panel
    cfgs.slice(0, 2).forEach((c, k) => setCfg(k, { recovery: "none", ...c }));
    $("#compare").checked = cfgs.length > 1 && !(opts && opts.arms); $("#compare").onchange();
    $("#armsCmp").checked = !!(opts && opts.arms) && !$("#armsCmp").disabled;
  }
  const arms = $("#armsCmp").checked && !$("#armsCmp").disabled;
  let labels = null;
  if (arms) { cfgs = armsCfgs(readCfg(0)); labels = cfgs.map(c => ARM_SHORT[c.recovery]); }
  else cfgs = cfgs ? cfgs.slice(0, 2) : [readCfg(0)].concat($("#compare").checked ? [readCfg(1)] : []);
  labels = labels || cfgs.map((c, k) => (k ? "B" : "A"));
  S.busy = true; syncButtons();
  const world = JSON.parse(JSON.stringify(S.doc)), t0 = performance.now();
  let label = labels[0];
  const tick = setInterval(() => runMsg(`Python is computing run ${label}: ${((performance.now() - t0) / 1000).toFixed(1)} s. The page stays responsive.`), 100);
  try {
    if (!S.ready) runMsg("Waiting for Python to finish loading...");
    await readyP;
    const out = [];
    for (let k = 0; k < cfgs.length; k++) { label = labels[k]; out.push(await runInWorker(world, cfgs[k])); }
    S.lastRunMs = Math.round(performance.now() - t0);
    if (JSON.stringify(world) !== JSON.stringify(S.doc)) { runMsg("The world changed while computing; run again.", true); return null; }
    S.runs = out; S.runLabels = labels;
    runMsg(`Done in ${(S.lastRunMs / 1000).toFixed(2)} s: ` + out.map((r, k) => `${labels[k]} ${r.sim_s} s simulated in ${r.wall_s} s of Python`).join(", ") + ".");
    S.t = 0; S.playing = !REDUCED;
    if (REDUCED) S.t = duration();
    setMode("replay"); showScore();
    return out;
  } catch (err) {
    runMsg("Run failed: " + err.message, true);
    return null;
  } finally {
    clearInterval(tick); S.busy = false; syncButtons();
  }
}
function runMsg(text, bad) { const el = $("#runMsg"); el.textContent = text; el.classList.toggle("bad", !!bad); el.classList.toggle("muted", !bad); }
$("#runBtn").onclick = () => runNow();

// ---------------------------------------------------------------- replay + score
function clearRuns() {
  if (!S.runs && S.mode === "edit") return;
  S.runs = null; S.runLabels = null; S.playing = false;
  setMode("edit");
  $("#resultBox").hidden = true;
}
function setMode(m) {
  S.mode = m;
  $("#replayCtl").hidden = m !== "replay";
  $("#hint").hidden = m === "replay";
  cv.classList.toggle("replay", m === "replay");
  if (m === "edit" && S.runs) { S.runs = null; $("#resultBox").hidden = true; }
  syncButtons(); draw();
}
$("#editBtn").onclick = () => setMode("edit");
const duration = () => (S.runs ? Math.max(...S.runs.map(r => r.end[0])) : 0);
function togglePlay() {
  if (!S.runs) return;
  if (!S.playing && S.t >= duration() - 1e-6) S.t = 0;
  S.playing = !S.playing; S.last = 0; syncReplay();
}
$("#playBtn").onclick = togglePlay;
$("#speed").onchange = () => { S.speed = parseFloat($("#speed").value) || 4; };
$("#scrub").addEventListener("input", () => { S.t = duration() * $("#scrub").value / 1000; S.playing = false; syncReplay(); draw(); });

function syncReplay() {
  $("#playBtn").textContent = S.playing ? "Pause" : "Play";
  const D = duration() || 1;
  $("#scrub").value = String(Math.round(1000 * S.t / D));
  $("#clock").textContent = `${S.t.toFixed(1)} / ${D.toFixed(1)} s`;
}

function loop(now) {
  if (S.mode === "replay" && S.runs && S.playing) {
    if (S.last) S.t = Math.min(duration(), S.t + ((now - S.last) / 1000) * S.speed);
    if (S.t >= duration()) S.playing = false;
    syncReplay(); draw();
  }
  S.last = S.playing ? now : 0;
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

const sp = $("#sparkC"), sctx = sp.getContext("2d");
function drawSpark(C) {
  if (!S.runs || $("#resultBox").hidden) return;
  const dpr = fitCanvas(sp), W = sp.width, H = sp.height, D = duration() || 1;
  const all = S.runs.flatMap(r => r.clearance), ymax = Math.max(1, Math.min(4, Math.max(...all) * 1.05));
  const X = t => 4 * dpr + (W - 8 * dpr) * t / D, Y = v => H - 4 * dpr - (H - 8 * dpr) * Math.max(0, Math.min(v, ymax)) / ymax;
  sctx.setTransform(1, 0, 0, 1, 0, 0);
  sctx.fillStyle = C.bg; sctx.fillRect(0, 0, W, H);
  sctx.strokeStyle = C.bad; sctx.setLineDash([4 * dpr, 4 * dpr]); sctx.lineWidth = 1 * dpr;
  sctx.beginPath(); sctx.moveTo(X(0), Y(0.15)); sctx.lineTo(X(D), Y(0.15)); sctx.stroke(); sctx.setLineDash([]);
  (S.runs || []).forEach((r, k) => {
    sctx.strokeStyle = runColor(C, k); sctx.lineWidth = 2 * dpr; sctx.beginPath();
    r.clearance.forEach((v, i) => { const t = Math.min(i / r.hz, r.end[0]); i ? sctx.lineTo(X(t), Y(v)) : sctx.moveTo(X(t), Y(v)); });
    sctx.stroke();
  });
  sctx.strokeStyle = C.muted; sctx.lineWidth = 1 * dpr;
  sctx.beginPath(); sctx.moveTo(X(S.t), 0); sctx.lineTo(X(S.t), H); sctx.stroke();
  sctx.fillStyle = C.muted; sctx.font = `${11 * dpr}px system-ui, sans-serif`; sctx.textBaseline = "top";
  sctx.fillText(`${ymax.toFixed(1)} m`, 6 * dpr, 4 * dpr);
  const now = S.runs.map((r, k) => { const i = Math.min(r.clearance.length - 1, Math.floor(S.t * r.hz)); return `${runLabel(k)} ${r.clearance[i].toFixed(2)} m`; });
  $("#sparkNow").textContent = now.join("  ");
  drawStrip(C);
}

const OUT_LABEL = { reached: "reached B", stuck: "stuck", collision: "collision", timeout: "timeout" };
const fmt = (v, n) => (v == null ? "-" : typeof v === "number" ? (n == null ? String(v) : v.toFixed(n)) : esc(v));

function showScore() {
  const R = S.runs; if (!R) return;
  $("#resultBox").hidden = false;
  $("#badges").innerHTML = R.map((r, k) => `<span class="who">${esc(runLabel(k))}</span><span class="badge ${esc(r.score.outcome)}">${esc(OUT_LABEL[r.score.outcome] || r.score.outcome)}</span>`).join(" ") +
    ' <span class="badge synthetic">synthetic</span>';
  const rows = [
    ["Planner", r => esc(LABELS.planner[r.config.planner])],
    ["Sensor", r => esc(r.config.preset)],
    ["VIO fault", r => esc(LABELS.fault[r.config.fault])],
    ["Safety filter", r => esc(r.config.filter)],
    ["VIO loss recovery", r => esc(LABELS.recovery[r.config.recovery || "none"])],
    // run time limit from worker.js max_time_for: 120 s for maze / warehouse (as the benchmark), else 60 s
    ["Outcome", r => esc(r.score.outcome) + (r.max_time_s != null ? ` <span class="muted" title="Sim time before a run ends as timeout: 120 s for the maze and warehouse families (as close-area-benchmark), 60 s otherwise">(limit ${esc(r.max_time_s)} s)</span>` : "")],
    ["Time to B, s", r => fmt(r.score.time_to_goal_s)],
    ["Duration, s", r => fmt(r.score.duration_s)],
    ["Min clearance, m", r => fmt(r.score.min_clearance_m)],
    ["Path length, m", r => fmt(r.score.path_length_m)],
    ["Max pose error, m", r => fmt(r.score.max_pose_error_m)],
    ["Median pose error, m", r => fmt(r.score.est_err_median_m)],
    ["F2 intervened, % of steps", r => (r.score.intervention_frac == null ? "-" : (100 * r.score.intervention_frac).toFixed(1))],
    ["Fault fired at, s", r => (r.fault_log ? fmt(r.fault_log.fired_t) : "-")],
    ...(R.some(r => r.reloc && r.reloc.arm !== "none") ? [
      ["Loss events (triggers)", r => relocF(r, s => s.events)],
      ["Relocs accepted / wrong (> 0.5 m)", r => relocF(r, s => `${s.accepted} / ${s.wrong_commits}`)],
      ["Still hovering at end", r => relocF(r, s => s.open_at_end)],
      ["First recovery, s", r => relocF(r, s => fmt(s.first_recover_s))],
      ["Hovering while lost, s", r => relocF(r, s => fmt(s.hover_s))],
      ["Info-gain moves flown", r => relocF(r, s => s.moves)],
    ] : []),
    ["Free path for 0.15 m (BFS)", r => (r.free_path ? "yes" : "no")],
    ["Python wall time, s", r => fmt(r.wall_s)],
  ];
  const head = `<thead><tr><th></th>${R.map((r, k) => `<th><span class="sw-${"abcd"[k % 4]}"></span> ${esc(runLabel(k))}</th>`).join("")}</tr></thead>`;
  $("#score").innerHTML = head + "<tbody>" + rows.map(([n, f]) => {
    const vals = R.map(f), diff = R.length > 1 && vals.some(v => v !== vals[0]);
    return `<tr><th>${n}</th>${vals.map(v => `<td${diff ? ' class="diff"' : ""}>${v}</td>`).join("")}</tr>`;
  }).join("") + "</tbody>";
  parityNote();
  syncReplay(); draw();
}

// pg_reloc.event_key: the per-event fields compared with native
const eventKey = evs => (evs || []).map(e => [e.t_trigger, e.reason, e.result, e.recover_s, e.err_m,
  (e.moves || []).filter(m => m.move != null).length]);
function relocF(r, f) { return r.reloc && r.reloc.arm !== "none" ? f(r.reloc.summary) : "-"; }

// Verdict strip: one row per run with a relocalization trace, coloured by the status at each 10 Hz frame.
const st = $("#stripC"), stx = st.getContext("2d");
function drawStrip(C) {
  const rows = S.runs.map((r, k) => [r, k]).filter(([r]) => r.reloc);
  $("#stripWrap").hidden = !rows.length;
  if (!rows.length) return;
  const rowH = 16, gap = 4, lab = 64;
  st.style.height = `${rows.length * (rowH + gap) + 2}px`;
  const dpr = fitCanvas(st), W = st.width, D = duration() || 1;
  const X = t => (lab + 4) * dpr + (W - (lab + 8) * dpr) * t / D;
  stx.setTransform(1, 0, 0, 1, 0, 0);
  stx.fillStyle = C.bg; stx.fillRect(0, 0, W, st.height);
  stx.font = `${11 * dpr}px system-ui, sans-serif`; stx.textBaseline = "middle";
  rows.forEach(([r, k], j) => {
    const y = (1 + j * (rowH + gap)) * dpr, h = rowH * dpr, names = r.reloc.status_names || STATUS, F = r.frames;
    stx.fillStyle = runColor(C, k); stx.fillRect(0, y + h / 2 - 4 * dpr, 8 * dpr, 8 * dpr);
    stx.fillStyle = C.fg; stx.fillText(runLabel(k), 12 * dpr, y + h / 2);
    stx.fillStyle = C.line; stx.fillRect(X(0), y, X(r.end[0]) - X(0), h);
    r.reloc.status.forEach((code, i) => {
      const col = statusColor(C, names[code]);
      if (!col) return;
      const t0 = F[i][0], t1 = i + 1 < F.length ? F[i + 1][0] : r.end[0];
      stx.fillStyle = col; stx.fillRect(X(t0), y, Math.max(1, X(t1) - X(t0) + 0.5), h);
    });
  });
  stx.strokeStyle = C.muted; stx.lineWidth = 1 * dpr;
  stx.beginPath(); stx.moveTo(X(S.t), 0); stx.lineTo(X(S.t), st.height); stx.stroke();
  const now = rows.map(([r, k]) => {
    const i = frameAt(r, S.t), names = r.reloc.status_names || STATUS;
    return `${runLabel(k)}: ${i < 0 ? "-" : names[r.reloc.status[i]]}`;
  });
  $("#stripNow").textContent = now.join("; ");
}

async function parityNote() {
  const el = $("#parityMsg"); el.textContent = "";
  if (!S.pristine || !S.presetName) { el.textContent = "Custom or edited world: no stored native reference to compare with."; return; }
  try {
    if (!S.parity) S.parity = await (await fetch("results/native_parity.json")).json();
  } catch (err) { return; }
  const keys = S.parity.keys, msgs = [];
  (S.runs || []).forEach((r, k) => {
    const c = r.config, rec = c.recovery || "none";
    const match = x => x.world === S.presetName && x.planner === c.planner && x.preset === c.preset && x.fault === c.fault && x.filter === c.filter;
    const ref = rec === "none" ? c.seed === 0 && S.parity.cases.find(match)
      : (S.parity.reloc_cases || []).find(x => match(x) && x.seed === c.seed && x.recovery === rec);
    if (!ref) return;
    let same = keys.every(key => ref.score[key] === r.score[key]);
    if (ref.events) same = same && JSON.stringify(ref.events) === JSON.stringify(eventKey(r.reloc.events));
    msgs.push(`${runLabel(k)}: ${same ? "same score" + (ref.events ? " and loss events" : "") + " as" : "differs from"} native CPython ${S.parity.native_env.python}`);
  });
  el.innerHTML = msgs.length ? esc(msgs.join("; ")) + ' on this world (<a href="results/native_parity.json">native_parity.json</a>).'
    : "No stored native reference for this preset and config.";
}

// ---------------------------------------------------------------- theme, resize, start
$("#themeBtn").onclick = () => {
  const cur = document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("navidx-theme", next); } catch (err) { /* storage blocked */ }
  draw();
};
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => draw());
if (window.ResizeObserver) new ResizeObserver(() => draw()).observe(cv); else window.addEventListener("resize", draw);

setDoc(blankDoc(), null, true);
async function startFromUrl() {          // a shared link: restore it and run once Python is ready
  let ok = false;
  try { ok = await restoreFromUrl(); }
  catch (err) { S.linkError = "This link does not hold a readable world (" + err.message + "). Loaded the default preset random_0."; }
  if (ok) { S.linkRun = readyP.then(() => runNow()); return true; }
  return false;
}
const started = loadPresets().catch(err => { worldMsg("Could not load presets: " + err.message + ". Serve the repo root with python3 -m http.server.", "bad"); })
  .then(startFromUrl)
  .then(fromLink => {
    if (!fromLink) return loadPreset("random_0").then(() => { if (S.linkError) worldMsg(S.linkError, "bad"); }).catch(err => worldMsg(err.message, "bad"));
  });
window.addEventListener("hashchange", () => { if (/[#&]w=/.test(location.hash)) startFromUrl(); });

// Scripted API (headless checks, console use)
window.PG = {
  ready: readyP,
  started,
  shareUrl, encodeWorld, decodeWorld,
  linkRun: () => S.linkRun || Promise.resolve(null),
  config: () => ({ a: readCfg(0), b: $("#compare").checked ? readCfg(1) : null, compare: $("#compare").checked, arms: $("#armsCmp").checked }),
  loadPreset,
  setWorld: d => setDoc(d, null),
  world: () => JSON.parse(JSON.stringify(S.doc)),
  addObstacle(o) { pushUndo(); S.doc.obstacles.push({ material: "matte", ...o }); changed(); return S.doc.obstacles.length - 1; },
  setTool, undo, setCfg,
  setCompare(on) { $("#compare").checked = !!on; $("#compare").onchange(); },
  run: cfgs => runNow(cfgs),
  runArms: cfg => runNow([cfg], { arms: true }),     // config A with every recovery arm, overlaid
  loadState: () => ({ ready: S.ready, failed: S.load.failed, attempt: S.load.attempt, retries: S.load.retries, message: S.load.message,
    retry_visible: !$("#retryBtn").hidden, text: $("#loadText").textContent, attempts: S.load.attempts || (S.env && S.env.load_attempts) || null }),
  retryLoad,
  status: () => (S.runs || []).map((r, k) => { const i = r.reloc ? frameAt(r, S.t) : -1; return { run: runLabel(k), status: i < 0 ? null : r.reloc.status_names[r.reloc.status[i]] }; }),
  seek(t) { S.t = Math.max(0, Math.min(duration(), t)); S.playing = false; syncReplay(); draw(); },
  play() { if (!S.playing) togglePlay(); },
  duration,
};

// Advisor panel (advisor.js, loop-65): benchmark success rates per planner for the loaded preset family.
if (window.Advisor) window.PG_ADVISOR = Advisor.mount($("#advisorBox"), {
  getFamily: () => (S.pristine && S.presetName && S.doc.family !== "custom") ? S.doc.family
    : { custom: true, from: S.doc && S.doc.family !== "custom" ? S.doc.family : null },
  getPreset: () => $("#A_preset").value,
  getAvailable: () => Array.from($("#A_planner").options).filter(o => !o.disabled).map(o => o.value),
  onPick: (planner, cfg) => { setCfg(0, { planner, filter: cfg.filter }); $("#cfgA").scrollIntoView({ block: "nearest" }); },
});
