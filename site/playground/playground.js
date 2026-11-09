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
    astar_unknown: "A* + ESDF, unknown map", apf: "APF + wall follow", vfh_plus: "VFH+" },
  preset: { ideal: "ideal: 72 rays, 360 deg, 6 m", crazyflie: "Crazyflie: 4 cone beams, 3 m", crazyflie_bright: "Crazyflie, bright light: 0.73 m" },
  fault: { truth: "off: planner sees truth", none: "VIO EKF, no fault", jump: "VIO jump 0.5 m", bias: "VIO bias 0.05 m/s, 10 s", dropout: "VIO dropout 2 s" },
  filter: { none: "none", F2: "F2: PX4-CBF on ranges" },
};
const DEFAULT_CFG = [
  { planner: "astar_known", preset: "ideal", fault: "truth", filter: "none" },
  { planner: "freest_beam", preset: "ideal", fault: "truth", filter: "none" },
];

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

function setDoc(d, presetName) {
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
    b: css("--b"), plan: css("--plan"), glass: css("--glass") };
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
  if (scanD && ang.length) {
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
    ctx.fillText(`${S.runs.length > 1 ? (slot ? "B " : "A ") : ""}${fl.fault} ${fl.fired_t} s`, fx + 14 * dpr, fy - 10 * dpr + slot * 16 * dpr);
  }
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
    S.runs.forEach((r, k) => drawRun(r, k ? C.b : C.accent, C, k === 0, k));
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
    `<option value="${esc(p.file.replace(/\.json$/, ""))}">${esc(p.label)} (seed ${p.seed}, layout ${p.index})</option>`).join("");
  return idx;
}

async function loadPreset(name) {
  const r = await fetch(`presets/${encodeURIComponent(name)}.json`);
  if (!r.ok) throw new Error(r.status + " preset " + name);
  setDoc(await r.json(), name);
  $("#presetSel").value = name;
  worldMsg(`Preset ${name}: exported with world_json.to_json from the seeded generator (synthetic).`, "");
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
  const rows = [["planner", "Planner"], ["preset", "Sensor"], ["fault", "VIO fault"], ["filter", "Filter"]];
  fs.insertAdjacentHTML("beforeend", rows.map(([k, lbl]) =>
    `<label>${lbl}<select id="${id}_${k}" aria-label="${lbl} ${id}">` +
    Object.entries(LABELS[k]).map(([v, t]) => `<option value="${v}"${cfg[k] === v ? " selected" : ""}>${esc(t)}</option>`).join("") +
    `</select></label>`).join(""));
}
buildCfg(0, DEFAULT_CFG[0]);
buildCfg(1, DEFAULT_CFG[1]);

function readCfg(which) {
  const id = which === 0 ? "A" : "B", o = {};
  for (const k of ["planner", "preset", "fault", "filter"]) o[k] = $(`#${id}_${k}`).value;
  o.seed = Math.max(0, Math.min(9999, parseInt($("#seed").value, 10) || 0));
  return o;
}
function setCfg(which, cfg) {
  const id = which === 0 ? "A" : "B";
  for (const [k, v] of Object.entries(cfg)) { if (k === "seed") $("#seed").value = v; else if ($(`#${id}_${k}`)) $(`#${id}_${k}`).value = v; }
}
$("#compare").onchange = () => {
  $("#cfgB").hidden = !$("#compare").checked;
  $(".cfgs").classList.toggle("two", $("#compare").checked);
};

function applyEnv(env) {        // disable options the worker could not load
  for (const id of ["A", "B"]) {
    for (const o of $(`#${id}_planner`).options) o.disabled = !env.planners.includes(o.value);
    for (const o of $(`#${id}_filter`).options) o.disabled = !env.filters.includes(o.value);
  }
  const errs = Object.entries(env.load_errors || {}).map(([k, v]) => `${k}: ${v}`).join("; ");
  $("#envMsg").textContent = `Pyodide ${env.pyodide}, Python ${env.python}, numpy ${env.numpy}, scipy ${env.scipy}; ` +
    `${env.arena_files} hub .py files loaded.` + (errs ? " Not loaded: " + errs : "");
}

// ---------------------------------------------------------------- worker
const worker = new Worker("worker.js?v=20261109b", { type: "module" });
let readyResolve, readyReject;
const readyP = new Promise((ok, fail) => { readyResolve = ok; readyReject = fail; });
const T_LOAD0 = performance.now();

worker.onmessage = ev => {
  const m = ev.data;
  if (m.type === "progress") {
    const exp = m.mb_expected || 22;
    const pct = m.stage === "ready" ? 100 : Math.min(97, Math.round(100 * (m.mb || 0) / exp));
    $("#loadBar").value = pct;
    if (m.stage) S.loadStage = `step ${m.step} of ${m.steps}: ${m.stage}`;
    $("#loadText").textContent = `Loading Python: ${S.loadStage || ""} (${(m.mb || 0).toFixed(1)} of about ${exp} MB downloaded)`;
  } else if (m.type === "ready") {
    S.ready = true; S.env = m.env; S.loadTimings = m.timings; S.loadMb = m.mb;
    S.readyMs = Math.round(performance.now() - T_LOAD0);
    $("#load").classList.add("done");
    $("#loadText").textContent = `Python ready in ${(S.readyMs / 1000).toFixed(1)} s (${m.mb} MB downloaded this visit; cached after).`;
    $("#runMsg").textContent = "Ready.";
    applyEnv(m.env); syncButtons(); readyResolve(m.env);
  } else if (m.type === "result" || m.type === "error") {
    if (m.fatal) {
      $("#load").classList.add("err"); $("#loadText").textContent = m.message + " (needs network access to cdn.jsdelivr.net)";
      readyReject(new Error(m.message)); return;
    }
    const p = S.pending.get(m.id); if (!p) return;
    S.pending.delete(m.id);
    m.type === "result" ? p.ok(m.result) : p.fail(new Error(m.message));
  }
};
worker.onerror = ev => { $("#load").classList.add("err"); $("#loadText").textContent = "Worker failed: " + (ev.message || "unknown error"); };

function runInWorker(world, cfg) {
  const id = S.nextId++;
  return new Promise((ok, fail) => { S.pending.set(id, { ok, fail }); worker.postMessage({ type: "run", id, world, cfg }); });
}

async function runNow(cfgs) {
  if (S.busy) return null;
  try { checkDoc(S.doc); } catch (err) { runMsg(err.message, true); return null; }
  if (cfgs) {                    // scripted run: show the configs it uses in the panel
    cfgs.forEach((c, k) => setCfg(k, c));
    $("#compare").checked = cfgs.length > 1; $("#compare").onchange();
  }
  cfgs = cfgs || [readCfg(0)].concat($("#compare").checked ? [readCfg(1)] : []);
  S.busy = true; syncButtons();
  const world = JSON.parse(JSON.stringify(S.doc)), t0 = performance.now();
  let label = "A";
  const tick = setInterval(() => runMsg(`Python is computing run ${label}: ${((performance.now() - t0) / 1000).toFixed(1)} s. The page stays responsive.`), 100);
  try {
    if (!S.ready) runMsg("Waiting for Python to finish loading...");
    await readyP;
    const out = [];
    for (let k = 0; k < cfgs.length; k++) { label = k ? "B" : "A"; out.push(await runInWorker(world, cfgs[k])); }
    S.lastRunMs = Math.round(performance.now() - t0);
    if (JSON.stringify(world) !== JSON.stringify(S.doc)) { runMsg("The world changed while computing; run again.", true); return null; }
    S.runs = out;
    runMsg(`Done in ${(S.lastRunMs / 1000).toFixed(2)} s: ` + out.map((r, k) => `${k ? "B" : "A"} ${r.sim_s} s simulated in ${r.wall_s} s of Python`).join(", ") + ".");
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
  S.runs = null; S.playing = false;
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
  S.runs.forEach((r, k) => {
    sctx.strokeStyle = k ? C.b : C.accent; sctx.lineWidth = 2 * dpr; sctx.beginPath();
    r.clearance.forEach((v, i) => { const t = Math.min(i / r.hz, r.end[0]); i ? sctx.lineTo(X(t), Y(v)) : sctx.moveTo(X(t), Y(v)); });
    sctx.stroke();
  });
  sctx.strokeStyle = C.muted; sctx.lineWidth = 1 * dpr;
  sctx.beginPath(); sctx.moveTo(X(S.t), 0); sctx.lineTo(X(S.t), H); sctx.stroke();
  sctx.fillStyle = C.muted; sctx.font = `${11 * dpr}px system-ui, sans-serif`; sctx.textBaseline = "top";
  sctx.fillText(`${ymax.toFixed(1)} m`, 6 * dpr, 4 * dpr);
  const now = S.runs.map((r, k) => { const i = Math.min(r.clearance.length - 1, Math.floor(S.t * r.hz)); return `${k ? "B" : "A"} ${r.clearance[i].toFixed(2)} m`; });
  $("#sparkNow").textContent = now.join("  ");
}

const OUT_LABEL = { reached: "reached B", stuck: "stuck", collision: "collision", timeout: "timeout" };
const fmt = (v, n) => (v == null ? "-" : typeof v === "number" ? (n == null ? String(v) : v.toFixed(n)) : esc(v));

function showScore() {
  const R = S.runs; if (!R) return;
  $("#resultBox").hidden = false;
  $("#badges").innerHTML = R.map((r, k) => `<span class="who">${k ? "B" : "A"}</span><span class="badge ${esc(r.score.outcome)}">${esc(OUT_LABEL[r.score.outcome] || r.score.outcome)}</span>`).join(" ") +
    ' <span class="badge synthetic">synthetic</span>';
  const rows = [
    ["Planner", r => esc(LABELS.planner[r.config.planner])],
    ["Sensor", r => esc(r.config.preset)],
    ["VIO fault", r => esc(LABELS.fault[r.config.fault])],
    ["Safety filter", r => esc(r.config.filter)],
    ["Outcome", r => esc(r.score.outcome)],
    ["Time to B, s", r => fmt(r.score.time_to_goal_s)],
    ["Duration, s", r => fmt(r.score.duration_s)],
    ["Min clearance, m", r => fmt(r.score.min_clearance_m)],
    ["Path length, m", r => fmt(r.score.path_length_m)],
    ["Max pose error, m", r => fmt(r.score.max_pose_error_m)],
    ["Median pose error, m", r => fmt(r.score.est_err_median_m)],
    ["F2 intervened, % of steps", r => (r.score.intervention_frac == null ? "-" : (100 * r.score.intervention_frac).toFixed(1))],
    ["Fault fired at, s", r => (r.fault_log ? fmt(r.fault_log.fired_t) : "-")],
    ["Free path for 0.15 m (BFS)", r => (r.free_path ? "yes" : "no")],
    ["Python wall time, s", r => fmt(r.wall_s)],
  ];
  const head = `<thead><tr><th></th>${R.map((r, k) => `<th><span class="sw-${k ? "b" : "a"}"></span> ${k ? "B" : "A"}</th>`).join("")}</tr></thead>`;
  $("#score").innerHTML = head + "<tbody>" + rows.map(([n, f]) => {
    const vals = R.map(f), diff = R.length > 1 && vals[0] !== vals[1];
    return `<tr><th>${n}</th>${vals.map(v => `<td${diff ? ' class="diff"' : ""}>${v}</td>`).join("")}</tr>`;
  }).join("") + "</tbody>";
  parityNote();
  syncReplay(); draw();
}

async function parityNote() {
  const el = $("#parityMsg"); el.textContent = "";
  if (!S.pristine || !S.presetName) { el.textContent = "Custom or edited world: no stored native reference to compare with."; return; }
  try {
    if (!S.parity) S.parity = await (await fetch("results/native_parity.json")).json();
  } catch (err) { return; }
  const keys = S.parity.keys, msgs = [];
  S.runs.forEach((r, k) => {
    const c = r.config;
    const ref = c.seed === 0 && S.parity.cases.find(x => x.world === S.presetName && x.planner === c.planner && x.preset === c.preset && x.fault === c.fault && x.filter === c.filter);
    if (!ref) return;
    const same = keys.every(key => ref.score[key] === r.score[key]);
    msgs.push(`${k ? "B" : "A"}: ${same ? "same score as" : "differs from"} native CPython ${S.parity.native_env.python}`);
  });
  el.innerHTML = msgs.length ? esc(msgs.join("; ")) + ' on this preset (<a href="results/native_parity.json">native_parity.json</a>).'
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

setDoc(blankDoc(), null);
loadPresets().then(() => loadPreset("random_0")).catch(err => worldMsg("Could not load presets: " + err.message + ". Serve the repo root with python3 -m http.server.", "bad"));

// Scripted API (headless checks, console use)
window.PG = {
  ready: readyP,
  loadPreset,
  setWorld: d => setDoc(d, null),
  world: () => JSON.parse(JSON.stringify(S.doc)),
  addObstacle(o) { pushUndo(); S.doc.obstacles.push({ material: "matte", ...o }); changed(); return S.doc.obstacles.length - 1; },
  setTool, undo, setCfg,
  setCompare(on) { $("#compare").checked = !!on; $("#compare").onchange(); },
  run: cfgs => runNow(cfgs),
  seek(t) { S.t = Math.max(0, Math.min(duration(), t)); S.playing = false; syncReplay(); draw(); },
  play() { if (!S.playing) togglePlay(); },
  duration,
};
