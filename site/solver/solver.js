// Solver UI: pick a map, sweep every planner x variation x seed in a pool of Pyodide workers
// (site/playground/worker.js, unchanged), draw the race, rank the planners.
// Pure logic lives in sweep.js (unit tested), the worker pool in pool.js.
// window.SOLVER is a small API for scripted checks (results/measure_solver.mjs).
import * as SW from "./sweep.js?v=20261110c";
import { Pool } from "./pool.js?v=20261110c";

const $ = s => document.querySelector(s);
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const PG = "../playground/";
const SCHEMA = "close-area-world/1";
const PYODIDE_Q = (q => (/^(cdn|local|auto)$/.test(q || "") ? q : null))(new URLSearchParams(location.search).get("pyodide"));
const WORKER_V = "20261110c";       // worker.js cache-busting version, same as playground.js WORKER_URL
const WORKER_URL = new URL(PG + "worker.js?v=" + WORKER_V + (PYODIDE_Q ? "&pyodide=" + PYODIDE_Q : ""), location.href);
const K = SW.poolSize(navigator.hardwareConcurrency);
const T_PAGE0 = performance.now();

// one colour per planner, light and dark sets (index = position in env.planners)
// worker order: straight, freest_beam, astar_known, astar_unknown, apf, vfh_plus, dwa, dwa_mem, bug2, tangent_bug, dstar_lite, informed_rrt_star
const PAL_LIGHT = ["#7f7f7f", "#d9730d", "#2ca02c", "#d62728", "#9467bd", "#0e8f9c", "#e377c2", "#8a8a00", "#8c564b", "#1f77b4", "#111111", "#c49a00"];
const PAL_DARK = ["#a0a0a0", "#ffa94d", "#79d18f", "#ff6b6b", "#c39bff", "#5fd3dc", "#ff9ed8", "#d6d660", "#c9a07a", "#6ea8ff", "#f5f5f5", "#ffd34d"];
const isDark = () => (document.documentElement.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";
function plannerColor(p) {
  const list = (S.env && S.env.planners) || Object.keys(SW.PLANNER_LABELS);
  const i = Math.max(0, list.indexOf(p));
  const pal = isDark() ? PAL_DARK : PAL_LIGHT;
  return pal[i % pal.length];
}

const S = {
  doc: null, worldName: null, pristine: false, presets: [], env: null, pool: null, readyCount: 0, loadMs: null,
  sweep: null, walls: {}, sel: null, anim: null, linkSpec: null, autoStart: false, dirty: false,
};
let readyResolve; const readyP = new Promise(ok => { readyResolve = ok; });
let doneResolve = null;

// ---------------------------------------------------------------- world
function checkDoc(d) {          // light check; Python's world_json.from_json is the real validator
  if (!d || d.schema !== SCHEMA) throw new Error("not a " + SCHEMA + " document");
  const [x0, y0, x1, y1] = d.bounds || [];
  if (![x0, y0, x1, y1].every(Number.isFinite) || !(x0 < x1 && y0 < y1)) throw new Error("bounds must be [xmin, ymin, xmax, ymax]");
  if (!d.a) d.a = [0, 0];
  for (const k of ["a", "b"]) {
    const p = d[k];
    if (!p || !(p[0] > x0 && p[0] < x1 && p[1] > y0 && p[1] < y1)) throw new Error(k.toUpperCase() + " is outside the bounds");
  }
  if (!Array.isArray(d.obstacles)) throw new Error("obstacles must be a list");
  for (const o of d.obstacles) if (!["box", "wall", "cylinder"].includes(o.type)) throw new Error("unsupported obstacle type " + o.type);
  return d;
}

function worldMsg(text, cls) { const el = $("#worldMsg"); el.textContent = text || ""; el.className = "small " + (cls || ""); }

function setWorld(doc, name, msg) {
  if (S.sweep && S.sweep.running) { worldMsg("Cancel the running sweep before changing the map.", "bad"); return false; }
  S.doc = checkDoc(JSON.parse(JSON.stringify(doc)));
  S.worldName = name || null;
  S.pristine = !!name;
  $("#presetSel").value = name || "";
  if (S.sweep) clearSweep();
  worldMsg(msg || "", "ok");
  updateEditLink();
  drawAll();
  return true;
}

async function loadPreset(name) {
  const r = await fetch(PG + "presets/" + encodeURIComponent(name) + ".json");
  if (!r.ok) throw new Error(r.status + " preset " + name);
  const p = S.presets.find(x => x.name === name);
  setWorld(await r.json(), name, `Preset ${p ? p.label : name}: seed 0, layout 0 (synthetic, exported by the playground).`);
}

async function loadPresetIndex() {
  const r = await fetch(PG + "presets/index.json");
  if (!r.ok) throw new Error(r.status + " presets/index.json");
  const idx = await r.json();
  S.presets = idx.presets.map(p => ({ name: p.file.replace(/\.json$/, ""), label: p.label, n: p.obstacles }));
  $("#presetSel").innerHTML = '<option value="">imported / from link</option>' +
    S.presets.map(p => `<option value="${esc(p.name)}">${esc(p.label)} (${esc(p.name)})</option>`).join("");
}

async function worldFromLink(w, srcName) {
  const doc = await SW.decodeWorld(w);
  checkDoc(doc);
  let name = null;
  if (srcName && S.presets.some(p => p.name === srcName)) {     // same as the preset file? then keep its name
    try {
      const r = await fetch(PG + "presets/" + srcName + ".json");
      if (r.ok && JSON.stringify(await r.json()) === JSON.stringify(doc)) name = srcName;
    } catch (err) { /* name only */ }
  }
  return { doc, name };
}

async function updateEditLink() {
  const doc = S.doc;
  try {
    const w = await SW.encodeWorld(doc);
    if (doc !== S.doc) return;
    $("#editLink").href = PG + "index.html" + (S.pristine && S.worldName ? "?src=" + encodeURIComponent(S.worldName) : "") + "#w=" + w;
  } catch (err) { $("#editLink").href = PG + "index.html"; }
}

// ---------------------------------------------------------------- canvas helpers
function fitCanvas(c) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2), w = c.clientWidth, h = c.clientHeight;
  if (w && h && (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr))) { c.width = Math.round(w * dpr); c.height = Math.round(h * dpr); }
  return dpr;
}
function colors() {
  return { bg: css("--panel"), fg: css("--fg"), muted: css("--muted"), line: css("--line"), obst: css("--obst"),
    ok: css("--ok"), bad: css("--bad"), warn: css("--warn"), glass: css("--glass"), accent: css("--accent") };
}
function rectOf(o) {
  if (o.type === "box") return [o.cx - o.hx, o.cy - o.hy, o.cx + o.hx, o.cy + o.hy];
  const h = (o.thickness || 0.1) / 2;
  if (Math.abs(o.y1 - o.y0) < 1e-9) return [Math.min(o.x0, o.x1), o.y0 - h, Math.max(o.x0, o.x1), o.y0 + h];
  return [o.x0 - h, Math.min(o.y0, o.y1), o.x0 + h, Math.max(o.y0, o.y1)];
}

// Draw the world on canvas c; returns the world => pixel transform.
function drawWorld(c, doc, C) {
  const ctx = c.getContext("2d"), dpr = fitCanvas(c), pad = 0.4;
  const [x0, y0, x1, y1] = doc.bounds;
  const s = Math.min(c.width / (x1 - x0 + 2 * pad), c.height / (y1 - y0 + 2 * pad));
  const P = (x, y) => [(x - x0 + pad) * s, (y1 + pad - y) * s];
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, c.width, c.height);
  ctx.strokeStyle = C.line; ctx.lineWidth = 1;
  for (let g = Math.ceil(x0); g <= x1; g++) { ctx.globalAlpha = g % 5 === 0 ? 0.9 : 0.35; const [a] = P(g, 0); ctx.beginPath(); ctx.moveTo(a, P(0, y1)[1]); ctx.lineTo(a, P(0, y0)[1]); ctx.stroke(); }
  for (let g = Math.ceil(y0); g <= y1; g++) { ctx.globalAlpha = g % 5 === 0 ? 0.9 : 0.35; const [, b] = P(0, g); ctx.beginPath(); ctx.moveTo(P(x0, 0)[0], b); ctx.lineTo(P(x1, 0)[0], b); ctx.stroke(); }
  ctx.globalAlpha = 1;
  for (const o of doc.obstacles) {
    const m = o.material || "matte";
    ctx.fillStyle = m === "glass" || m === "mirror" ? C.glass : m === "dark" ? C.fg : C.obst;
    ctx.globalAlpha = m === "glass" || m === "mirror" ? 0.75 : 1;
    if (o.type === "cylinder") { const [a, b] = P(o.cx, o.cy); ctx.beginPath(); ctx.arc(a, b, Math.max(o.r * s, 1.5 * dpr), 0, 2 * Math.PI); ctx.fill(); }
    else { const [rx0, ry0, rx1, ry1] = rectOf(o), [a, b] = P(rx0, ry1); ctx.fillRect(a, b, Math.max((rx1 - rx0) * s, 1.5 * dpr), Math.max((ry1 - ry0) * s, 1.5 * dpr)); }
  }
  ctx.globalAlpha = 1;
  const tol = Math.max(0.3 * s, 5 * dpr), [ax, ay] = P(doc.a[0], doc.a[1]), [bx, by] = P(doc.b[0], doc.b[1]);
  ctx.fillStyle = C.ok; ctx.beginPath(); ctx.arc(ax, ay, tol, 0, 2 * Math.PI); ctx.fill();
  ctx.lineWidth = 3 * dpr; ctx.strokeStyle = C.bad; ctx.beginPath(); ctx.arc(bx, by, tol, 0, 2 * Math.PI); ctx.stroke();
  ctx.fillStyle = C.fg; ctx.font = `700 ${13 * dpr}px system-ui, sans-serif`; ctx.textBaseline = "middle";
  ctx.fillText("A", ax + tol + 3 * dpr, ay - tol); ctx.fillText("B", bx + tol + 3 * dpr, by - tol);
  return { ctx, P, s, dpr };
}

function markX(ctx, a, b, q, col, dpr) {
  ctx.strokeStyle = col; ctx.lineWidth = 3 * dpr; ctx.beginPath();
  ctx.moveTo(a - q, b - q); ctx.lineTo(a + q, b + q); ctx.moveTo(a + q, b - q); ctx.lineTo(a - q, b + q); ctx.stroke();
}
function markCheck(ctx, a, b, q, col, dpr) {
  ctx.strokeStyle = col; ctx.lineWidth = 3 * dpr; ctx.lineCap = "round"; ctx.beginPath();
  ctx.moveTo(a - q, b); ctx.lineTo(a - q / 3, b + q * 0.7); ctx.lineTo(a + q, b - q * 0.8); ctx.stroke(); ctx.lineCap = "butt";
}
function markRing(ctx, a, b, q, col, dpr) { ctx.strokeStyle = col; ctx.lineWidth = 2.5 * dpr; ctx.beginPath(); ctx.arc(a, b, q, 0, 2 * Math.PI); ctx.stroke(); }
function endMark(ctx, tr, a, b, col, C, dpr, big) {
  const q = (big ? 8 : 5) * dpr;
  if (tr.outcome === "collision") markX(ctx, a, b, q, big ? C.bad : col, dpr);
  else if (tr.outcome === "reached") markCheck(ctx, a, b, q, big ? col : col, dpr);
  else markRing(ctx, a, b, q, big ? C.warn : col, dpr);
}

function posAt(pts, t) {        // interpolated [x, y] at time t (clamped to the run)
  if (t <= pts[0][0]) return [pts[0][1], pts[0][2], 0];
  const n = pts.length - 1;
  if (t >= pts[n][0]) return [pts[n][1], pts[n][2], n];
  let lo = 0, hi = n;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; if (pts[m][0] <= t) lo = m; else hi = m; }
  const [ta, xa, ya] = pts[lo], [tb, xb, yb] = pts[hi], u = tb > ta ? (t - ta) / (tb - ta) : 0;
  return [xa + u * (xb - xa), ya + u * (yb - ya), lo];
}

// ---------------------------------------------------------------- drawing
function drawPreview() {
  if (!S.doc) return;
  drawWorld($("#preview"), S.doc, colors());
}

function raceRuns() {           // finished trajectories matching the race filter
  const sw = S.sweep; if (!sw) return [];
  const key = $("#raceVar").value;
  return sw.traj.filter(t => !key || t.key === key);
}

// The race shows A and B of the chosen seed (jittered for seed > 0) and a small + at the exact map's A and B.
function raceSeedJitter() {
  const sw = S.sweep; if (!sw || !sw.jitters) return null;
  const seed = S.anim ? S.anim.seed : +$("#raceSeed").value || 0;
  return sw.jitters[seed] || null;
}
function drawRace() {
  const c = $("#race"), base = (S.sweep && S.sweep.world) || S.doc;
  if (!base) return;
  const j = raceSeedJitter(), doc = j && !j.exact ? SW.jitterWorld(base, j) : base;
  const C = colors(), { ctx, P, dpr } = drawWorld(c, doc, C);
  if (doc !== base) {
    const q = 5 * dpr;
    ctx.strokeStyle = C.fg; ctx.lineWidth = 1.5 * dpr; ctx.globalAlpha = 0.8;
    for (const p of [base.a || [0, 0], base.b]) {
      const [a, b] = P(p[0], p[1]);
      ctx.beginPath(); ctx.moveTo(a - q, b); ctx.lineTo(a + q, b); ctx.moveTo(a, b - q); ctx.lineTo(a, b + q); ctx.stroke();
    }
    ctx.globalAlpha = 1;
  }
  if (S.anim) return drawAnim(ctx, P, dpr, C);
  const runs = raceRuns();
  ctx.lineJoin = "round";
  for (const tr of runs) {
    const col = plannerColor(tr.planner);
    ctx.strokeStyle = col; ctx.globalAlpha = runs.length > 60 ? 0.35 : 0.55; ctx.lineWidth = 1.6 * dpr;
    ctx.beginPath(); tr.pts.forEach(([, x, y], k) => { const [a, b] = P(x, y); k ? ctx.lineTo(a, b) : ctx.moveTo(a, b); }); ctx.stroke();
  }
  ctx.globalAlpha = 1;
  for (const tr of runs) {
    if (tr.outcome === "reached") continue;
    const e = tr.pts[tr.pts.length - 1], [a, b] = P(e[1], e[2]);
    endMark(ctx, tr, a, b, plannerColor(tr.planner), C, dpr, false);
  }
}

function drawAnim(ctx, P, dpr, C) {
  const A = S.anim, T = A.t;
  ctx.lineJoin = "round";
  for (const tr of A.runs) {
    const col = plannerColor(tr.planner), [vx, vy, i] = posAt(tr.pts, T);
    ctx.strokeStyle = col; ctx.lineWidth = 2.5 * dpr; ctx.globalAlpha = 0.85;
    ctx.beginPath();
    for (let k = 0; k <= i; k++) { const [a, b] = P(tr.pts[k][1], tr.pts[k][2]); k ? ctx.lineTo(a, b) : ctx.moveTo(a, b); }
    { const [a, b] = P(vx, vy); ctx.lineTo(a, b); }
    ctx.stroke(); ctx.globalAlpha = 1;
  }
  for (const tr of A.runs) {
    const col = plannerColor(tr.planner), [vx, vy] = posAt(tr.pts, T), [a, b] = P(vx, vy);
    const done = T >= tr.pts[tr.pts.length - 1][0] - 1e-6;
    ctx.fillStyle = col; ctx.beginPath(); ctx.arc(a, b, 5 * dpr, 0, 2 * Math.PI); ctx.fill();
    ctx.strokeStyle = C.bg; ctx.lineWidth = 1.5 * dpr; ctx.stroke();
    if (done) endMark(ctx, tr, a, b, col, C, dpr, true);
  }
  $("#clock").textContent = T.toFixed(1) + " s";
  $("#scrub").value = String(Math.round(1000 * T / Math.max(A.tmax, 1e-6)));
}

function drawAll() { drawPreview(); drawRace(); }

function schedule() {
  if (S.dirty) return;
  S.dirty = true;
  requestAnimationFrame(() => { S.dirty = false; renderSweep(); });
}

// ---------------------------------------------------------------- sweep panel
function buildSweepControls(env) {
  const planners = env.planners.filter(p => typeof p === "string");
  const want = S.linkSpec && S.linkSpec.planners ? new Set(S.linkSpec.planners) : null;
  $("#plannerList").innerHTML = planners.map(p =>
    `<label><input type="checkbox" name="planner" value="${esc(p)}"${!want || want.has(p) ? " checked" : ""}><span>${esc(SW.plannerLabel(p))}</span></label>`).join("");
  const avail = env.presets || SW.SWEEP_PRESETS;
  const wantP = (S.linkSpec && S.linkSpec.presets) || ["ideal"];
  $("#presetList").innerHTML = SW.SWEEP_PRESETS.filter(p => avail.includes(p)).map(p =>
    `<label><input type="checkbox" name="preset" value="${p}"${wantP.includes(p) ? " checked" : ""}><span>${esc(SW.PRESET_LABELS[p])}</span></label>`).join("");
  const faults = SW.EXTRA_FAULTS.filter(f => (env.faults || []).includes(f));
  $("#faultSel").innerHTML = '<option value="">truth only (planner sees truth)</option>' +
    faults.map(f => `<option value="${f}">truth + ${esc(SW.FAULT_LABELS[f])}</option>`).join("");
  if (S.linkSpec && faults.includes(S.linkSpec.fault)) $("#faultSel").value = S.linkSpec.fault;
  if (S.linkSpec && S.linkSpec.seeds) $("#seedsIn").value = SW.normSpec({ seeds: S.linkSpec.seeds }).seeds;
  if (S.linkSpec && S.linkSpec.time_limit != null) $("#tlimSel").value = String(SW.normTimeLimit(S.linkSpec.time_limit));
  if (S.linkSpec && S.linkSpec.jitter != null) {
    const j = SW.normSpec({ jitter: S.linkSpec.jitter }).jitter;
    $("#jitterOn").checked = j > 0;
    if (j > 0) $("#jitterR").value = String(j);
  }
  for (const el of document.querySelectorAll("#plannerList input, #presetList input")) el.onchange = updateCount;
  updateCount();
}

function readSpec() {
  const vals = name => [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(i => i.value);
  return SW.normSpec({ planners: vals("planner"), presets: vals("preset"), fault: $("#faultSel").value || null,
    seeds: $("#seedsIn").value, jitter: $("#jitterOn").checked ? $("#jitterR").value : 0, time_limit: $("#tlimSel").value },
  S.env ? S.env.planners : null);
}

function measuredMeans() {
  const out = {};
  for (const [p, w] of Object.entries(S.walls)) if (w.length) out[p] = w.reduce((a, b) => a + b, 0) / w.length;
  return out;
}

function updateCount() {
  if (!S.env) { $("#countMsg").textContent = ""; return; }
  const spec = readSpec(), n = SW.runCount(spec);
  const est = SW.estimateSeconds(SW.buildRuns(spec), measuredMeans(), K);
  $("#countMsg").innerHTML = `<b>${n} runs</b> = ${spec.planners.length} planners x ${spec.presets.length} sensor x ${spec.faults.length} fault x ${spec.seeds} seeds. ` +
    `Estimate: about ${SW.fmtDuration(est.s)} on ${K} worker${K > 1 ? "s" : ""} ` +
    `<span class="muted">(${est.measured ? "from run times measured in this browser" : "rough prior from the playground README timings; refined after the first runs"})</span>. ` +
    esc(SW.timeLimitText(spec, S.doc, []));
  $("#runBtn").disabled = !n || !S.readyCount || !!(S.sweep && S.sweep.running);
}

function setBusy(on) {
  $("#runBtn").disabled = on || !S.readyCount;
  $("#cancelBtn").disabled = !on;
  for (const el of document.querySelectorAll("#plannerList input, #presetList input, #faultSel, #seedsIn, #tlimSel, #jitterOn, #jitterR, #quickBtn, #thoroughBtn, #presetSel, #fileIn, #linkForm button"))
    el.disabled = on;
  if (!on) $("#jitterR").disabled = !$("#jitterOn").checked;
}

function clearSweep() {
  stopAnim();
  S.sweep = null; S.sel = null;
  $("#detail").hidden = true;
  $("#csvBtn").disabled = $("#jsonBtn").disabled = true;
  renderSweep();
}

function startSweep() {
  if (!S.readyCount || (S.sweep && S.sweep.running)) return;
  const spec = readSpec();
  if (!spec.planners.length) { $("#poolMsg").textContent = "Pick at least one planner."; return; }
  stopAnim();
  const world = JSON.parse(JSON.stringify(S.doc));
  const runs = SW.buildRuns(spec);
  // A and B per seed (seed 0 exact); one world per seed, shared by every planner and variation
  const jitters = SW.seedJitters(world, spec);
  const worlds = jitters.map(j => (j.exact ? world : SW.jitterWorld(world, j)));
  const sw = { spec, world, worldName: S.pristine ? S.worldName : null, total: runs.length, done: 0, jitters,
    records: new Array(runs.length).fill(null), traj: [], running: true, cancelled: false,
    started: new Date().toISOString(), finished: null, t0: performance.now() };
  S.sweep = sw; S.sel = null; $("#detail").hidden = true;
  const jobs = runs.map((r, idx) => {
    const j = jitters[r.seed];
    return { ...r, idx, sweep: sw, world: worlds[r.seed], a: j.a, b: j.b,
      ab_kept: j.a_kept || j.b_kept ? { a: j.a_kept, b: j.b_kept } : null,
      cfg: { planner: r.planner, preset: r.preset, fault: r.fault, filter: "none", seed: r.seed } };
  });
  // run time limit: Auto sends none (the worker applies the family rule), a fixed choice is sent as cfg.max_time_s.
  // The watchdog grows with the limit (180 s wall at 60 s of sim time).
  const tlim = SW.cfgTimeLimit(spec), simS = SW.timeLimitFor(world, spec.time_limit).s;
  for (const j of jobs) { if (tlim != null) j.cfg.max_time_s = tlim; j.timeoutS = Math.round(180 * Math.max(1, simS / 60)); }
  const kept = jitters.filter(j => j.a_kept || j.b_kept).length;
  if (spec.jitter && kept) $("#poolMsg").textContent = `Jitter: ${kept} seed(s) kept an exact A or B (no free point in ${SW.JITTER_DRAWS} draws).`;
  // race filters
  $("#raceVar").innerHTML = '<option value="">all variations</option>' +
    SW.variations(spec).map(k => `<option value="${esc(k)}">${esc(SW.variationLabel(k))}</option>`).join("");
  if (SW.variations(spec).length === 1) $("#raceVar").value = SW.variations(spec)[0];
  $("#raceSeed").innerHTML = Array.from({ length: spec.seeds }, (_, i) => `<option value="${i}">${i}</option>`).join("");
  setBusy(true);
  S.pool.add(jobs);
  renderSweep();
  return new Promise(ok => { doneResolve = ok; });
}

function onDone(job, result, error) {
  const sw = job.sweep;
  if (!sw || sw !== S.sweep || !sw.running) return;
  const rec = error ? SW.recordFromError(job, error) : SW.recordFromResult(job, result);
  rec.worker = job.worker;
  sw.records[job.idx] = rec;
  if (!error && result && Array.isArray(result.frames) && result.frames.length && rec.outcome !== "error") {
    const [ox, oy] = result.offset || [0, 0];
    const pts = result.frames.map(f => [f[0], f[1] + ox, f[2] + oy]);
    if (result.end) pts.push([result.end[0], result.end[1] + ox, result.end[2] + oy]);
    sw.traj.push({ planner: job.planner, key: job.key, seed: job.seed, outcome: rec.outcome, pts });
  }
  if (rec.wall_s != null) (S.walls[job.planner] = S.walls[job.planner] || []).push(rec.wall_s);
  sw.done++;
  if (sw.done >= sw.total) finishSweep(false);
  schedule();
}

function finishSweep(cancelled, why) {
  const sw = S.sweep; if (!sw || !sw.running) return;
  sw.running = false; sw.cancelled = cancelled; sw.finished = new Date().toISOString();
  sw.elapsed_s = Math.round(performance.now() - sw.t0) / 1000;
  sw.why = why || null;
  setBusy(false);
  $("#csvBtn").disabled = $("#jsonBtn").disabled = !sw.done;
  $("#animBtn").disabled = !sw.traj.length;
  updateCount();
  renderSweep();
  if (doneResolve) { doneResolve(sw); doneResolve = null; }
}

function cancelSweep(why) {
  if (!S.sweep || !S.sweep.running) return;
  S.pool.cancel();
  finishSweep(true, why || "cancelled");
  startPool();                   // a fresh pool for the next sweep (loads from the browser cache)
}

function renderSweep() {
  const sw = S.sweep;
  const total = sw ? sw.total : 0, done = sw ? sw.done : 0;
  $("#sweepBar").max = Math.max(1, total); $("#sweepBar").value = done;
  let txt = `${done}/${total}`;
  if (sw && sw.running) {
    const pending = sw.records.map((r, i) => (r ? null : i)).filter(i => i != null).map(i => ({ planner: sw.spec.planners[i % sw.spec.planners.length] }));
    const est = SW.estimateSeconds(pending, measuredMeans(), Math.max(1, S.readyCount));
    txt += done ? `, about ${SW.fmtDuration(est.s)} left` : ", waiting for the first results";
  } else if (sw && sw.cancelled) txt += `, ${sw.why === "cancelled" ? "cancelled" : "stopped: " + sw.why}: ${total - done} runs not run`;
  else if (sw) txt += `, done in ${SW.fmtDuration(sw.elapsed_s)}`;
  $("#sweepText").textContent = txt;
  $("#animBtn").disabled = !(sw && sw.traj.length);
  renderLegend();
  renderResults();
  if (!S.anim) drawRace();
}

function renderLegend() {
  const sw = S.sweep;
  const planners = sw ? sw.spec.planners : [];
  if (!planners.length) { $("#legend").innerHTML = '<tbody><tr><td class="muted">Planners appear here when a sweep starts.</td></tr></tbody>'; return; }
  const per = sw.total / planners.length;
  const rows = planners.map(p => {
    const recs = sw.records.filter(r => r && r.planner === p), c = SW.stats(recs);
    return `<tr><td><span class="swatch" style="background:${plannerColor(p)}"></span>${esc(SW.plannerLabel(p))}</td>` +
      `<td>${recs.length}/${per}</td><td class="c-ok">${c.reached}</td><td class="c-bad">${c.collision}</td>` +
      `<td class="c-warn">${c.stuck + c.timeout}</td><td>${c.error ? `<b class="c-bad">${c.error}</b>` : 0}</td></tr>`;
  }).join("");
  $("#legend").innerHTML = '<thead><tr><th>planner</th><th>done</th><th>reached</th><th>collision</th><th title="stuck or timeout">stuck</th><th>error</th></tr></thead><tbody>' + rows + "</tbody>";
}

const pct = v => (v == null ? "-" : Math.round(v * 100) + " %");
const f1 = (v, u) => (v == null ? "-" : v.toFixed(v < 10 ? 2 : 1) + (u ? " " + u : ""));

function renderResults() {
  const sw = S.sweep;
  const recs = sw ? sw.records.filter(Boolean) : [];
  if (!recs.length) {
    $("#headline").textContent = "Run a sweep to see the ranking."; $("#headline").className = "headline";
    $("#ranking").innerHTML = ""; $("#matrix").innerHTML = ""; $("#limitLine").textContent = ""; return;
  }
  const agg = SW.aggregate(recs, sw.spec);
  const partial = sw.running ? ` (live: ${recs.length}/${sw.total} runs)` : sw.cancelled ? ` (cancelled: ${recs.length}/${sw.total} runs)` : "";
  $("#headline").textContent = agg.headline.text + partial;
  $("#headline").className = "headline " + agg.headline.kind;
  $("#limitLine").textContent = SW.timeLimitText(sw.spec, sw.world, recs);
  $("#ranking").innerHTML = agg.ranking.map(r =>
    `<li><span class="swatch" style="background:${plannerColor(r.planner)}"></span><b>${esc(SW.plannerLabel(r.planner))}</b>: ` +
    `${r.reached}/${r.n} reached` + (r.n_distinct < r.n ? ` <span class="dup">(${r.reached_distinct}/${r.n_distinct} distinct)</span>` : "") +
    ` <span class="ci">(95 % CI ${pct(r.success.lo)}-${pct(r.success.hi)}, ${esc(SW.nOne(r))})</span>, ` +
    (r.median_time_s == null ? "no run reached B" : `median ${r.median_time_s.toFixed(1)} s to B`) + (r.error ? `, <span class="c-bad">${r.error} error</span>` : "") + "</li>").join("");
  const order = agg.ranking.map(r => r.planner).concat(agg.planners.filter(p => !agg.ranking.some(r => r.planner === p)));
  const head = "<thead><tr><th>planner</th>" + agg.variations.map(k => `<th>${esc(SW.variationLabel(k))}</th>`).join("") + "</tr></thead>";
  const body = order.map(p => "<tr><th>" + `<span class="swatch" style="background:${plannerColor(p)}"></span>${esc(SW.plannerLabel(p))}</th>` +
    agg.variations.map(k => {
      const c = agg.cells[p][k];
      if (!c.n) return '<td class="na"><span class="cell muted">-</span></td>';
      const cls = c.success.p >= 0.8 ? "hi" : c.success.p >= 0.4 ? "mid" : "lo";
      const sel = S.sel && S.sel.planner === p && S.sel.key === k ? " sel" : "";
      return `<td class="${cls}${sel}"><button class="cell" data-p="${esc(p)}" data-k="${esc(k)}" title="details">` +
        `<b>${pct(c.success.p)}</b> <span class="ci">[${pct(c.success.lo)}-${pct(c.success.hi)}]</span> <span class="n">${esc(SW.nOne(c))}</span><br>` +
        (c.identical ? `<span class="dup">deterministic: ${c.identical} identical runs</span><br>` : "") +
        `<span class="n">${c.median_time_s == null ? "no run reached B" : "median " + c.median_time_s.toFixed(1) + " s to B"}</span></button></td>`;
    }).join("") + "</tr>").join("");
  $("#matrix").innerHTML = head + "<tbody>" + body + "</tbody>";
  if (S.sel) renderDetail(agg);
}

function jitterList(sw) {
  if (!sw || !sw.jitters) return "-";
  const xy = p => `(${p[0].toFixed(2)}, ${p[1].toFixed(2)})`;
  const list = sw.jitters.slice(0, 10).map(j => `seed ${j.seed}: A ${xy(j.a)} B ${xy(j.b)}` +
    (j.exact ? " exact map" : j.a_kept || j.b_kept ? ` (kept exact ${[j.a_kept && "A", j.b_kept && "B"].filter(Boolean).join(" and ")})` : ""));
  return (sw.spec.jitter ? `jitter radius ${sw.spec.jitter} m<br>` : "jitter off<br>") + list.join("<br>") +
    (sw.jitters.length > 10 ? `<br>... ${sw.jitters.length - 10} more in the JSON export` : "");
}

function renderDetail(agg) {
  const { planner: p, key: k } = S.sel, c = agg.cells[p] && agg.cells[p][k];
  if (!c) { $("#detail").hidden = true; return; }
  const errs = S.sweep.records.filter(r => r && r.planner === p && SW.variationKey(r.preset, r.fault) === k && r.outcome === "error");
  $("#detail").hidden = false;
  $("#detail").innerHTML = `<b>${esc(SW.plannerLabel(p))}</b>, ${esc(SW.variationLabel(k))}` +
    `<dl><dt>reached B</dt><dd>${c.reached}/${c.n} runs; distinct runs ${c.reached_distinct}/${c.n_distinct} = ${pct(c.success.p)} ` +
    `(95 % Wilson on the ${c.n_distinct} distinct runs: ${pct(c.success.lo)}-${pct(c.success.hi)})</dd>` +
    (c.identical ? `<dt>deterministic</dt><dd class="dup">${c.identical} of ${c.n} runs are identical to another run (same outcome, time to B and path length at 3 dp); each set counts as one trial.</dd>` : "") +
    `<dt>A and B per seed</dt><dd class="mono small">${jitterList(S.sweep)}</dd>` +
    `<dt>median time to B</dt><dd>${f1(c.median_time_s, "s")}</dd>` +
    `<dt>median path length</dt><dd>${f1(c.median_path_m, "m")}</dd>` +
    `<dt>min clearance</dt><dd>${c.min_clearance_m == null ? "-" : c.min_clearance_m.toFixed(3) + " m"} (lowest over the runs, centre to surface)</dd>` +
    `<dt>collision rate</dt><dd>${pct(c.collision_rate)} (${c.collision}/${c.n}); stuck ${c.stuck}, timeout ${c.timeout}, error ${c.error}</dd>` +
    `<dt>mean wall time</dt><dd>${c.mean_wall_s == null ? "-" : c.mean_wall_s.toFixed(2) + " s per run in the worker"}</dd>` +
    (errs.length ? `<dt>errors</dt><dd class="c-bad">${errs.slice(0, 3).map(e => `seed ${e.seed}: ${esc(e.error)}`).join("<br>")}</dd>` : "") +
    "</dl><p class=\"small muted\">This variation is now loaded in the race view.</p>";
}

$("#matrix").addEventListener("click", ev => {
  const b = ev.target.closest("button.cell"); if (!b) return;
  S.sel = { planner: b.dataset.p, key: b.dataset.k };
  stopAnim();
  $("#raceVar").value = b.dataset.k;
  renderSweep();
});

// ---------------------------------------------------------------- race animation
function startAnim(key, seed) {
  const sw = S.sweep; if (!sw) return false;
  if (key == null) key = $("#raceVar").value || SW.variations(sw.spec)[0];
  if (seed == null) seed = +$("#raceSeed").value || 0;
  $("#raceVar").value = key; $("#raceSeed").value = String(seed);
  const runs = sw.traj.filter(t => t.key === key && t.seed === seed);
  if (!runs.length) { $("#poolMsg").textContent = `No finished run for ${SW.variationLabel(key)}, seed ${seed} yet.`; return false; }
  const tmax = Math.max(...runs.map(t => t.pts[t.pts.length - 1][0]));
  S.anim = { key, seed, runs, tmax, t: 0, playing: true, last: performance.now() };
  $("#timeline").hidden = false; $("#playBtn").hidden = false; $("#speedLbl").hidden = false;
  $("#playBtn").textContent = "Pause"; $("#animBtn").textContent = "Restart";
  requestAnimationFrame(tick);
  return true;
}
function stopAnim() {
  S.anim = null;
  $("#timeline").hidden = true; $("#playBtn").hidden = true; $("#speedLbl").hidden = true;
  $("#animBtn").textContent = "Animate race";
}
function tick(now) {
  const A = S.anim; if (!A) return;
  if (A.playing) {
    A.t = Math.min(A.tmax, A.t + (now - A.last) / 1000 * (+$("#speed").value || 4));
    if (A.t >= A.tmax) { A.playing = false; $("#playBtn").textContent = "Play"; }
  }
  A.last = now;
  drawRace();
  if (A.playing) requestAnimationFrame(tick);
}
function setAnimT(t) {
  const A = S.anim; if (!A) return;
  A.t = Math.max(0, Math.min(A.tmax, t)); A.playing = false; $("#playBtn").textContent = "Play"; drawRace();
}
$("#animBtn").onclick = () => startAnim();
$("#playBtn").onclick = () => {
  const A = S.anim; if (!A) return;
  if (A.t >= A.tmax) A.t = 0;
  A.playing = !A.playing; A.last = performance.now();
  $("#playBtn").textContent = A.playing ? "Pause" : "Play";
  if (A.playing) requestAnimationFrame(tick);
};
$("#scrub").oninput = () => { if (S.anim) setAnimT(S.anim.tmax * (+$("#scrub").value) / 1000); };
$("#raceVar").onchange = () => { if (S.anim) startAnim(); else drawRace(); };
$("#raceSeed").onchange = () => { if (S.anim) startAnim(); else drawRace(); };

// ---------------------------------------------------------------- pool
function loadText(text, bad) { $("#loadText").textContent = text; $("#load").classList.toggle("err", !!bad); }

function startPool() {
  S.readyCount = 0;
  S.pool = new Pool({ url: WORKER_URL, size: K,
    onProgress: (i, m) => {
      if (i !== 0 || S.env) return;
      if (m.type === "retry") { loadText(`${m.step}: attempt ${m.attempt}/${m.attempts} failed (${m.error}); retrying in ${m.wait_s} s`, true); return; }
      if (m.steps) $("#loadBar").value = Math.round(100 * (m.step - 1) / m.steps);
      if (m.stage) loadText(`Step ${m.step}/${m.steps}: ${m.stage}` + (m.mb ? ` (${m.mb} MB so far)` : ""));
    },
    onReady: (i, m, n) => {
      S.readyCount = n;
      if (!S.env) {
        S.env = m.env;
        S.loadMs = Math.round(performance.now() - T_PAGE0);
        $("#load").classList.add("done");
        buildSweepControls(m.env);
        readyResolve(m.env);
        if (S.autoStart) { S.autoStart = false; startSweep(); }
      }
      const e = S.env, errs = Object.keys(e.load_errors || {});
      loadText(`Python ready (${(S.loadMs / 1000).toFixed(1)} s). Pyodide ${e.pyodide}, Python ${e.python}, numpy ${e.numpy}, scipy ${e.scipy}; ${e.planners.length} planners` +
        (errs.length ? `; not loaded: ${errs.join(", ")}` : "") + ".");
      $("#poolMsg").textContent = `Workers ready: ${n}/${K} (K = min(4, ${navigator.hardwareConcurrency || "?"} cores - 1)). Each loads Pyodide once.`;
      updateCount();
    },
    onDone,
    onFatal: why => {
      loadText("Python could not load: " + why + ". Reload the page to try again.", true);
      if (S.sweep && S.sweep.running) { S.pool.cancel(); finishSweep(true, "all workers failed: " + why); }
    },
  }).start();
}

// ---------------------------------------------------------------- buttons
$("#runBtn").onclick = () => startSweep();
$("#cancelBtn").onclick = () => cancelSweep("cancelled");
$("#seedsIn").oninput = updateCount;
$("#jitterOn").onchange = () => { $("#jitterR").disabled = !$("#jitterOn").checked; updateCount(); };
$("#jitterR").onchange = updateCount;
$("#faultSel").onchange = updateCount;
$("#tlimSel").onchange = updateCount;
$("#allBtn").onclick = () => { document.querySelectorAll('input[name="planner"]').forEach(i => { i.checked = true; }); updateCount(); };
$("#noneBtn").onclick = () => { document.querySelectorAll('input[name="planner"]').forEach(i => { i.checked = false; }); updateCount(); };

function preset(seeds, presets, resetFault) {
  $("#seedsIn").value = seeds;
  document.querySelectorAll('input[name="preset"]').forEach(i => { i.checked = presets.includes(i.value); });
  if (resetFault) $("#faultSel").value = "";
  updateCount();
  if (S.readyCount) return startSweep();
  S.autoStart = true;
  $("#poolMsg").textContent = "The sweep starts when Python is ready.";
  return null;
}
const quick = () => preset(3, ["ideal"], true);          // Quick: 3 seeds, ideal only, truth pose only
const thorough = () => preset(10, ["ideal", "crazyflie"], false);
$("#quickBtn").onclick = quick;
$("#thoroughBtn").onclick = thorough;

$("#presetSel").onchange = () => { const v = $("#presetSel").value; if (v) loadPreset(v).catch(err => worldMsg(err.message, "bad")); };
$("#fileIn").onchange = ev => {
  const f = ev.target.files && ev.target.files[0];
  if (!f) return;
  const rd = new FileReader();
  rd.onload = () => {
    try { setWorld(JSON.parse(rd.result), null, `Imported ${f.name} (${JSON.parse(rd.result).obstacles.length} obstacles).`); }
    catch (err) { worldMsg(`Could not import ${f.name}: ${err.message}`, "bad"); }
  };
  rd.readAsText(f);
  ev.target.value = "";
};
$("#linkForm").onsubmit = async ev => {
  ev.preventDefault();
  const w = SW.worldParamFrom($("#linkIn").value);
  if (!w) { worldMsg("No #w= world found in that text. Copy a link with the playground's Copy link button.", "bad"); return; }
  try {
    const src = (() => { try { return new URL($("#linkIn").value.trim()).searchParams.get("src"); } catch (err) { return null; } })();
    const { doc, name } = await worldFromLink(w, src);
    setWorld(doc, name, `World loaded from the pasted link (${doc.obstacles.length} obstacles).`);
  } catch (err) { worldMsg("Could not load the link: " + err.message, "bad"); }
};

function download(name, text, type) {
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
const baseName = () => `solver_${(S.sweep && S.sweep.worldName) || "custom"}`;
function exportJSON() {
  const sw = S.sweep; if (!sw) return null;
  const doc = SW.exportDoc({ spec: sw.spec, world: sw.world, worldName: sw.worldName, records: sw.records.filter(Boolean), env: S.env,
    pool: { workers: K, hardware_concurrency: navigator.hardwareConcurrency || null, ready_workers: S.readyCount,
      python_ready_s: S.loadMs != null ? S.loadMs / 1000 : null, sweep_wall_s: sw.elapsed_s != null ? sw.elapsed_s : null, user_agent: navigator.userAgent },
    started: sw.started, finished: sw.finished, cancelled: sw.cancelled, jitters: sw.jitters });
  return JSON.stringify(doc, null, 1) + "\n";
}
$("#csvBtn").onclick = () => { if (S.sweep) download(baseName() + ".csv", SW.toCSV(S.sweep.records.filter(Boolean)), "text/csv"); };
$("#jsonBtn").onclick = () => { const t = exportJSON(); if (t) download(baseName() + ".json", t, "application/json"); };

async function shareUrl() {
  const spec = S.env ? readSpec() : SW.normSpec(S.linkSpec || {});
  return location.origin + location.pathname + "?" + SW.specToQuery(spec, S.pristine ? S.worldName : null) + "#w=" + await SW.encodeWorld(S.doc);
}
$("#shareBtn").onclick = async () => {
  const el = $("#shareMsg");
  try {
    const url = await shareUrl();
    history.replaceState(null, "", url);
    let copied = false;
    try { await navigator.clipboard.writeText(url); copied = true; } catch (err) { /* blocked: the address bar has it */ }
    el.textContent = (copied ? "Link copied" : "Clipboard blocked; the link is in the address bar") + ` (${url.length} characters; world + sweep spec, no results).`;
    el.className = "small ok";
  } catch (err) { el.textContent = "Could not build a link: " + err.message; el.className = "small bad"; }
};

$("#themeBtn").onclick = () => {
  const next = isDark() ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  try { localStorage.setItem("navidx-theme", next); } catch (err) { /* storage blocked */ }
  drawAll(); renderSweep();
};
matchMedia("(prefers-color-scheme: dark)").addEventListener("change", () => { drawAll(); renderSweep(); });
if (window.ResizeObserver) { const ro = new ResizeObserver(() => drawAll()); ro.observe($("#race")); ro.observe($("#preview")); }
else window.addEventListener("resize", drawAll);

// ---------------------------------------------------------------- start
async function init() {
  startPool();                   // Python loads while the map is chosen
  const q = SW.specFromQuery(location.search);
  if (Object.keys(q.spec).length) S.linkSpec = q.spec;
  try { await loadPresetIndex(); } catch (err) { worldMsg("Could not load the preset list: " + err.message, "bad"); }
  const w = new URLSearchParams(location.hash.replace(/^#/, "")).get("w");
  if (w) {
    try {
      const { doc, name } = await worldFromLink(w, q.src);
      setWorld(doc, name, `World restored from the link (${doc.obstacles.length} obstacles)` + (S.linkSpec ? ", with its sweep spec." : "."));
      return;
    } catch (err) { worldMsg("The link's world could not be read (" + err.message + "); loaded random_0 instead.", "bad"); }
  }
  const m = new URLSearchParams(location.search).get("map");
  const name = m && S.presets.some(p => p.name === m) ? m : "random_0";
  try { await loadPreset(name); } catch (err) { worldMsg(err.message, "bad"); }
}
const started = init();

window.SOLVER = { S, K, ready: readyP, started, quick, thorough, run: startSweep, cancel: () => cancelSweep("cancelled"),
  exportJSON, csv: () => (S.sweep ? SW.toCSV(S.sweep.records.filter(Boolean)) : null), animate: startAnim, setT: setAnimT,
  shareUrl, loadPreset, allReady: () => S.readyCount >= K };
