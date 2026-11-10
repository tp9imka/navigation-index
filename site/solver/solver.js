// Solver UI: pick a map, sweep every planner x variation x seed in a pool of Pyodide workers
// (site/playground/worker.js, unchanged), draw the race, rank the planners.
// Pure logic lives in sweep.js (unit tested), the worker pool in pool.js.
// window.SOLVER is a small API for scripted checks (results/measure_solver.mjs).
import * as SW from "./sweep.js?v=20261110g";
import { Pool } from "./pool.js?v=20261110c";
import * as REC from "./recommend.js?v=20261110h";

const $ = s => document.querySelector(s);
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const css = name => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
const PG = "../playground/";
const SCHEMA = "close-area-world/1";
const PYODIDE_Q = (q => (/^(cdn|local|auto)$/.test(q || "") ? q : null))(new URLSearchParams(location.search).get("pyodide"));
const WORKER_V = "20261110d";       // worker.js cache-busting version, same as playground.js WORKER_URL
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
  vars: null,                    // explicit variation keys (Stress); null = every preset x fault
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
  const offered = SW.SWEEP_PRESETS.filter(p => avail.includes(p));
  $("#presetList").innerHTML = offered.map(p =>
    `<label><input type="checkbox" name="preset" value="${p}"${wantP.includes(p) ? " checked" : ""}><span>${esc(SW.PRESET_LABELS[p])}</span></label>`).join("");
  buildDroneControls(offered);
  const faults = SW.EXTRA_FAULTS.filter(f => (env.faults || []).includes(f));
  $("#faultSel").innerHTML = '<option value="">truth only (planner sees truth)</option>' +
    faults.map(f => `<option value="${f}">truth + ${esc(SW.FAULT_LABELS[f])}</option>`).join("");
  if (S.linkSpec && faults.includes(S.linkSpec.fault)) $("#faultSel").value = S.linkSpec.fault;
  if (S.linkSpec && Array.isArray(S.linkSpec.vars) && S.linkSpec.vars.length) S.vars = S.linkSpec.vars.slice();
  if (S.linkSpec && S.linkSpec.seeds) $("#seedsIn").value = SW.normSpec({ seeds: S.linkSpec.seeds }).seeds;
  if (S.linkSpec && S.linkSpec.time_limit != null) $("#tlimSel").value = String(SW.normTimeLimit(S.linkSpec.time_limit));
  if (S.linkSpec && S.linkSpec.jitter != null) {
    const j = SW.normSpec({ jitter: S.linkSpec.jitter }).jitter;
    $("#jitterOn").checked = j > 0;
    if (j > 0) $("#jitterR").value = String(j);
  }
  for (const el of document.querySelectorAll("#plannerList input")) el.onchange = updateCount;
  for (const el of document.querySelectorAll("#presetList input")) el.onchange = manualVariations;
  updateCount();
}

// "Your drone": vehicle (every run), sensor (a preset name checks that preset; Custom adds one variation), yaw.
const VEH_IN = { radius_m: "#vehR", v_max: "#vehV", a_max: "#vehA" };
const CS_IN = { beams: "#csBeams", fov_deg: "#csFov", max_range_m: "#csMax", min_range_m: "#csMin", noise_sigma_m: "#csNoise" };
function buildDroneControls(offered) {
  $("#droneSensor").innerHTML = offered.map(p => `<option value="${p}">${esc(SW.PRESET_LABELS[p] || p)}</option>`).join("") +
    `<option value="${SW.CUSTOM}">Custom (beams, FoV, range, noise)</option>`;
  const L = S.linkSpec || {};
  if (L.vehicle) { const v = SW.normVehicle(L.vehicle); for (const [k, sel] of Object.entries(VEH_IN)) $(sel).value = String(v[k]); }
  const choice = SW.normSensorChoice(L.sensor_choice);
  $("#droneSensor").value = offered.includes(choice) || choice === SW.CUSTOM ? choice : "ideal";
  if (L.sensor) { const s = SW.normSensor(L.sensor); for (const [k, sel] of Object.entries(CS_IN)) $(sel).value = String(s[k]); }
  $("#yawSel").value = SW.normYaw(L.yaw);
  if (L.vehicle || L.sensor_choice || L.yaw) $("#droneBox").open = !SW.isDefaultVehicle(L.vehicle) || choice !== "ideal" || SW.normYaw(L.yaw) !== "fixed";
  for (const sel of [...Object.values(VEH_IN), ...Object.values(CS_IN)]) $(sel).oninput = updateCount;
  $("#yawSel").onchange = updateCount;
  $("#droneSensor").onchange = () => {
    const v = $("#droneSensor").value;
    const box = document.querySelector(`#presetList input[value="${v}"]`);
    if (box) box.checked = true;
    manualVariations();
  };
}
function readDrone() {
  const vehicle = { tau: SW.VEHICLE_DEFAULT.tau }, sensor = {};
  for (const [k, sel] of Object.entries(VEH_IN)) vehicle[k] = $(sel).value;
  for (const [k, sel] of Object.entries(CS_IN)) sensor[k] = $(sel).value;
  return { vehicle, sensor_choice: $("#droneSensor").value || "ideal", sensor, yaw: $("#yawSel").value };
}
function droneSummary(spec) {
  const v = spec.vehicle;
  const veh = SW.isDefaultVehicle(v) ? "arena default vehicle" : `radius ${v.radius_m} m, v_max ${v.v_max} m/s, a_max ${v.a_max} m/s^2`;
  const sen = spec.sensor_choice === SW.CUSTOM ? SW.customLabel(spec.sensor) : spec.sensor_choice;
  return `${veh}; sensor ${sen}; yaw ${spec.yaw}`;
}

function readSpec() {
  const vals = name => [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(i => i.value);
  return SW.normSpec({ planners: vals("planner"), presets: vals("preset"), fault: $("#faultSel").value || null,
    seeds: $("#seedsIn").value, jitter: $("#jitterOn").checked ? $("#jitterR").value : 0, time_limit: $("#tlimSel").value, ...readDrone(),
    ...(S.vars ? { vars: S.vars } : {}) },
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
  $("#customBox").hidden = spec.sensor_choice !== SW.CUSTOM;
  $("#droneSum").textContent = "(" + droneSummary(spec) + ")";
  const nv = SW.variations(spec).length;
  $("#countMsg").innerHTML = `<b>${n} runs</b> = ${spec.planners.length} planners x ` +
    (spec.vars ? `${nv} variations (${esc(SW.variations(spec).map(k => SW.variationLabel(k, spec)).join("; "))})` : `${spec.presets.length} sensor x ${spec.faults.length} fault`) +
    ` x ${spec.seeds} seeds. ` +
    `Estimate: about ${SW.fmtDuration(est.s)} on ${K} worker${K > 1 ? "s" : ""} ` +
    `<span class="muted">(${est.measured ? "from run times measured in this browser" : "rough prior from the playground README timings, scaled by beams / 72; refined after the first runs"})</span>. ` +
    esc(SW.timeLimitText(spec, S.doc, [])) +
    `<br><span class="muted">${esc(SW.separationNote(spec.seeds, SW.seedsName(spec.seeds)))}</span>`;
  $("#runBtn").disabled = !n || !S.readyCount || !!(S.sweep && S.sweep.running);
}

function setBusy(on) {
  $("#runBtn").disabled = on || !S.readyCount;
  $("#cancelBtn").disabled = !on;
  for (const el of document.querySelectorAll("#plannerList input, #presetList input, #droneBox input, #droneBox select, #faultSel, #seedsIn, #tlimSel, #jitterOn, #jitterR, #quickBtn, #thoroughBtn, #stressBtn, #presetSel, #fileIn, #linkForm button"))
    el.disabled = on;
  if (!on) $("#jitterR").disabled = !$("#jitterOn").checked;
}

function clearSweep() {
  stopAnim();
  S.sweep = null; S.sel = null;
  $("#detail").hidden = true;
  $("#csvBtn").disabled = $("#jsonBtn").disabled = $("#recBtn").disabled = true;
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
  const sw = { spec, world, worldName: S.pristine ? S.worldName : null, total: runs.length, runs, done: 0, jitters,
    records: new Array(runs.length).fill(null), traj: [], running: true, cancelled: false,
    started: new Date().toISOString(), finished: null, t0: performance.now() };
  S.sweep = sw; S.sel = null; $("#detail").hidden = true;
  const jobs = runs.map((r, idx) => {
    const j = jitters[r.seed];
    return { ...r, idx, sweep: sw, world: worlds[r.seed], a: j.a, b: j.b,
      ab_kept: j.a_kept || j.b_kept ? { a: j.a_kept, b: j.b_kept } : null, free_path_pred: j.free_path,
      vehicle: spec.vehicle, sensor: r.preset === SW.CUSTOM ? spec.sensor : null, yaw: spec.yaw,
      cfg: { planner: r.planner, ...(r.preset === SW.CUSTOM ? {} : { preset: r.preset }), fault: r.fault, filter: "none", seed: r.seed,
        ...SW.cfgExtras(spec, r.preset) } };
  });
  // run time limit: Auto sends none (the worker applies the family rule), a fixed choice is sent as cfg.max_time_s.
  // The watchdog grows with the limit (180 s wall at 60 s of sim time).
  const tlim = SW.cfgTimeLimit(spec), simS = SW.timeLimitFor(world, spec.time_limit).s;
  for (const j of jobs) { if (tlim != null) j.cfg.max_time_s = tlim; j.timeoutS = Math.round(180 * Math.max(1, simS / 60)); }
  const kept = jitters.filter(j => j.a_kept || j.b_kept).length;
  const redrawn = jitters.filter(j => j.path_redraws > 0 && !j.path_kept).length, walled = jitters.filter(j => !j.free_path).length;
  const jmsg = [];
  if (spec.jitter && kept) jmsg.push(`${kept} seed(s) kept an exact A or B (no free point in ${SW.JITTER_DRAWS} draws, or no connected pair in ${SW.JITTER_PATH_TRIES})`);
  if (spec.jitter && redrawn) jmsg.push(`${redrawn} seed(s) redrawn because A and B were not connected at the vehicle radius`);
  if (walled) jmsg.push(`${walled} seed(s) have no free path A=>B at the vehicle radius before any run (shown as no path)`);
  if (jmsg.length) $("#poolMsg").textContent = "Jitter: " + jmsg.join("; ") + ".";
  // race filters
  $("#raceVar").innerHTML = '<option value="">all variations</option>' +
    SW.variations(spec).map(k => `<option value="${esc(k)}">${esc(SW.variationLabel(k, spec))}</option>`).join("");
  if (SW.variations(spec).length === 1) $("#raceVar").value = SW.variations(spec)[0];
  $("#paretoVar").innerHTML = '<option value="">all variations pooled</option>' +
    SW.variations(spec).map(k => `<option value="${esc(k)}">${esc(SW.variationLabel(k, spec))}</option>`).join("");
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
  $("#recBtn").disabled = !sw.done;
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
    const pending = sw.records.map((r, i) => (r ? null : i)).filter(i => i != null).map(i => sw.runs[i]);
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
      `<td>${recs.length}/${per}${c.no_path ? ` <span class="muted">(no path ${c.no_path})</span>` : ""}</td><td class="c-ok">${c.reached}</td><td class="c-bad">${c.collision}</td>` +
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
    $("#ranking").innerHTML = ""; $("#matrix").innerHTML = ""; $("#limitLine").textContent = ""; $("#paretoBox").hidden = true; return;
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
    (r.median_time_s == null ? "no run reached B" : `median ${r.median_time_s.toFixed(1)} s to B`) + (r.error ? `, <span class="c-bad">${r.error} error</span>` : "") +
    (r.no_path ? `, <span class="muted">no path (${r.no_path}), not counted</span>` : "") + "</li>").join("");
  const order = agg.ranking.map(r => r.planner).concat(agg.planners.filter(p => !agg.ranking.some(r => r.planner === p)));
  const head = "<thead><tr><th>planner</th>" + agg.variations.map(k => `<th>${esc(SW.variationLabel(k, sw.spec))}</th>`).join("") + "</tr></thead>";
  const body = order.map(p => "<tr><th>" + `<span class="swatch" style="background:${plannerColor(p)}"></span>${esc(SW.plannerLabel(p))}</th>` +
    agg.variations.map(k => {
      const c = agg.cells[p][k];
      if (!c.n && c.no_path) return `<td class="na"><span class="cell muted" title="worker free_path false: A and B not connected at the vehicle radius; not counted">no path (${c.no_path})</span></td>`;
      if (!c.n) return '<td class="na"><span class="cell muted">-</span></td>';
      const cls = c.success.p >= 0.8 ? "hi" : c.success.p >= 0.4 ? "mid" : "lo";
      const sel = S.sel && S.sel.planner === p && S.sel.key === k ? " sel" : "";
      return `<td class="${cls}${sel}"><button class="cell" data-p="${esc(p)}" data-k="${esc(k)}" title="details">` +
        `<b>${pct(c.success.p)}</b> <span class="ci">[${pct(c.success.lo)}-${pct(c.success.hi)}]</span> <span class="n">${esc(SW.nOne(c))}</span><br>` +
        (c.identical ? `<span class="dup">deterministic: ${c.identical} identical runs</span><br>` : "") +
        (c.no_path ? `<span class="n" title="worker free_path false: A and B not connected at the vehicle radius; not counted">no path (${c.no_path})</span><br>` : "") +
        `<span class="n">${c.median_time_s == null ? "no run reached B" : "median " + c.median_time_s.toFixed(1) + " s to B"}</span></button></td>`;
    }).join("") + "</tr>").join("");
  $("#matrix").innerHTML = head + "<tbody>" + body + "</tbody>";
  if (S.sel) renderDetail(agg);
  renderPareto(agg);
}

// ---------------------------------------------------------------- Pareto view (loop-89)
// x = median time to B, y = min clearance, dot area grows with the success rate; ring + id label = Pareto-optimal
// within the best success group (SW.paretoFront). Faded = outside that group. No time to B => not plotted.
function niceTicks(lo, hi, n) {
  const span = Math.max(hi - lo, 1e-9), raw = span / Math.max(1, n), mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 2.5, 5, 10].map(m => m * mag).find(st => st >= raw) || 10 * mag;
  const out = [];
  for (let v = Math.ceil(lo / step) * step; v <= hi + 1e-9; v += step) out.push(+v.toFixed(6));
  return out;
}
let paretoLast = null;
function renderPareto(agg) {
  const sw = S.sweep, key = $("#paretoVar").value;
  if (key && !agg.variations.includes(key)) $("#paretoVar").value = "";
  const rows = SW.paretoRows(agg, $("#paretoVar").value), par = SW.paretoFront(rows);
  paretoLast = { rows, par, key: $("#paretoVar").value };
  $("#paretoBox").hidden = false;
  drawPareto();
  const where = $("#paretoVar").value ? SW.variationLabel($("#paretoVar").value, sw.spec) : "all variations pooled";
  const byId = Object.fromEntries(rows.map(r => [r.planner, r]));
  const nb = t => t.replace(/ (s|m|%)\b/g, "&nbsp;$1").replace(/ %/g, "&nbsp;%");
  const one = id => `<b>${esc(SW.plannerLabel(id))}</b> ${nb(`${byId[id].median_time_s.toFixed(2)} s, ${byId[id].min_clearance_m.toFixed(3)} m, ${pct(byId[id].success.p)}`)}`;
  const top = rows[0];
  let html;
  if (!par.group.length) html = `No Pareto set (${esc(where)}): no planner reached B.`;
  else html = `Pareto-optimal (${esc(where)}): ${par.front.length ? par.front.map(one).join("; ") : "none"}.` +
    ` <span class="muted">Best success group: ${par.group.length} planner${par.group.length > 1 ? "s" : ""} whose 95 % interval overlaps ${esc(SW.plannerLabel(top.planner))}'s (${pct(top.success.lo)}-${pct(top.success.hi)})` +
    (par.excluded.length ? `; no time to B, not ranked: ${esc(par.excluded.map(SW.plannerLabel).join(", "))}` : "") + ".</span>";
  if (sw.running) html += ' <span class="muted">(live, changes as runs finish)</span>';
  $("#paretoList").innerHTML = html;
  $("#pareto").setAttribute("aria-label", "Scatter of median time to B against min clearance per planner. " + $("#paretoList").textContent);
}
function drawPareto() {
  const c = $("#pareto"); if (!paretoLast || $("#paretoBox").hidden) return;
  const { par } = paretoLast, C = colors(), ctx = c.getContext("2d"), dpr = fitCanvas(c), W = c.width, H = c.height;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  const pts = par.points.filter(q => q.t != null && q.c != null);
  ctx.font = `${11 * dpr}px system-ui, sans-serif`; ctx.textBaseline = "middle";
  if (!pts.length) { ctx.fillStyle = C.muted; ctx.textAlign = "center"; ctx.fillText("no planner reached B", W / 2, H / 2); ctx.textAlign = "start"; return; }
  const L = 46 * dpr, R = 14 * dpr, T = 12 * dpr, B = 38 * dpr;
  let t0 = Math.min(...pts.map(q => q.t)), t1 = Math.max(...pts.map(q => q.t));
  const tp = Math.max((t1 - t0) * 0.08, 0.5); t0 = Math.max(0, t0 - tp); t1 += tp;
  const c0 = Math.min(0, ...pts.map(q => q.c)), c1 = Math.max(...pts.map(q => q.c)) * 1.12 + 0.02;
  const X = t => L + (t - t0) / (t1 - t0) * (W - L - R), Y = v => H - B - (v - c0) / (c1 - c0) * (H - B - T);
  // axes, grid, ticks
  ctx.strokeStyle = C.line; ctx.fillStyle = C.muted; ctx.lineWidth = 1;
  const nx = W < 500 * dpr ? 4 : 6;
  ctx.textAlign = "center";
  for (const v of niceTicks(t0, t1, nx)) { const x = X(v); ctx.globalAlpha = 0.5; ctx.beginPath(); ctx.moveTo(x, T); ctx.lineTo(x, H - B); ctx.stroke(); ctx.globalAlpha = 1; ctx.fillText(String(v), x, H - B + 10 * dpr); }
  ctx.textAlign = "right";
  for (const v of niceTicks(c0, c1, 4)) { const y = Y(v); ctx.globalAlpha = 0.5; ctx.beginPath(); ctx.moveTo(L, y); ctx.lineTo(W - R, y); ctx.stroke(); ctx.globalAlpha = 1; ctx.fillText(v.toFixed(2), L - 5 * dpr, y); }
  ctx.strokeStyle = C.muted; ctx.beginPath(); ctx.moveTo(L, T); ctx.lineTo(L, H - B); ctx.lineTo(W - R, H - B); ctx.stroke();
  ctx.fillStyle = C.fg; ctx.textAlign = "center";
  ctx.fillText("median time to B, s (left = faster)", L + (W - L - R) / 2, H - 10 * dpr);
  ctx.save(); ctx.translate(12 * dpr, T + (H - B - T) / 2); ctx.rotate(-Math.PI / 2); ctx.fillText("min clearance, m (up = safer)", 0, 0); ctx.restore();
  // front as a staircase
  const fr = pts.filter(q => q.pareto).sort((a, b) => a.t - b.t);
  if (fr.length > 1) {
    ctx.strokeStyle = C.accent; ctx.lineWidth = 1.5 * dpr; ctx.setLineDash([4 * dpr, 3 * dpr]); ctx.beginPath();
    fr.forEach((q, i) => { const x = X(q.t), y = Y(q.c); if (!i) ctx.moveTo(x, y); else { ctx.lineTo(x, Y(fr[i - 1].c)); ctx.lineTo(x, y); } });
    ctx.stroke(); ctx.setLineDash([]);
  }
  // dots: faded outside the group, front last (on top)
  const order = [...pts.filter(q => !q.in_group), ...pts.filter(q => q.in_group && !q.pareto), ...fr];
  for (const q of order) {
    const x = X(q.t), y = Y(q.c), r = (2.5 + 5 * (q.p || 0)) * dpr;
    ctx.globalAlpha = q.in_group ? 0.95 : 0.3;
    ctx.fillStyle = plannerColor(q.planner); ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.fill();
    ctx.strokeStyle = C.bg; ctx.lineWidth = 1 * dpr; ctx.stroke();
    if (q.pareto) { ctx.globalAlpha = 1; ctx.strokeStyle = C.fg; ctx.lineWidth = 2 * dpr; ctx.beginPath(); ctx.arc(x, y, r + 3 * dpr, 0, 2 * Math.PI); ctx.stroke(); }
  }
  ctx.globalAlpha = 1; ctx.fillStyle = C.fg; ctx.font = `600 ${11 * dpr}px system-ui, sans-serif`;
  // labels: first candidate spot (right/left of the dot, stepping up and down a line) that overlaps no placed label
  const placed = [], lh = 13 * dpr;
  const hit = (a, b) => a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];
  for (const q of [...fr].sort((a, b) => b.c - a.c)) {
    const x = X(q.t), y = Y(q.c), r = (2.5 + 5 * (q.p || 0)) * dpr + 5 * dpr, w = ctx.measureText(q.planner).width;
    let box = null;
    for (const dy of [-0.6, 0.6, -1.6, 1.6, -2.6, 2.6, -3.6, 3.6]) for (const side of [1, -1]) {
      if (box) break;
      const x0 = side > 0 ? x + r : x - r - w, cy = y + dy * lh, b = [x0, cy - lh / 2, x0 + w, cy + lh / 2];
      if (b[0] >= L && b[2] <= W - R && b[1] >= 0 && b[3] <= H - B && !placed.some(p => hit(p, b))) box = b;
    }
    if (!box) { const x0 = Math.min(x + r, W - R - w); box = [x0, y - lh, x0 + w, y]; }
    placed.push(box);
    ctx.textAlign = "left"; ctx.fillText(q.planner, box[0], (box[1] + box[3]) / 2);
  }
  ctx.textAlign = "start";
}
$("#paretoVar").onchange = () => schedule();

function jitterList(sw) {
  if (!sw || !sw.jitters) return "-";
  const xy = p => `(${p[0].toFixed(2)}, ${p[1].toFixed(2)})`;
  const list = sw.jitters.slice(0, 10).map(j => `seed ${j.seed}: A ${xy(j.a)} B ${xy(j.b)}` +
    (j.exact ? " exact map" : j.path_kept ? " (no connected pair, kept exact A and B)" : j.a_kept || j.b_kept ? ` (kept exact ${[j.a_kept && "A", j.b_kept && "B"].filter(Boolean).join(" and ")})` : "") +
    (!j.exact && !j.path_kept && j.path_redraws ? ` (redrawn ${j.path_redraws}x: A and B not connected)` : "") +
    (j.free_path === false ? " NO PATH" : ""));
  return (sw.spec.jitter ? `jitter radius ${sw.spec.jitter} m<br>` : "jitter off<br>") + list.join("<br>") +
    (sw.jitters.length > 10 ? `<br>... ${sw.jitters.length - 10} more in the JSON export` : "");
}

const sensorText = s => (s ? `${s.beams} beams, FoV ${+s.fov_deg.toFixed(1)} deg, ${s.min_range_m}-${s.max_range_m} m, noise ${s.noise_sigma_m} m` +
  (s.cone_deg != null ? `, cone ${+s.cone_deg.toFixed(2)} deg, dropout ${s.dropout}` : ", cone 0 deg and dropout 0.02 (worker defaults)") : "-");
function vehText(spec, key) {
  const v = spec.vehicle, flown = [...new Set(S.sweep.records.filter(r => r && SW.variationKey(r.preset, r.fault) === key).map(r => r.yaw_policy).filter(Boolean))];
  return `radius ${v.radius_m} m, v_max ${v.v_max} m/s, a_max ${v.a_max} m/s^2, tau ${v.tau} s` + (SW.isDefaultVehicle(v) ? " (arena default, not sent)" : " (sent as cfg.vehicle)") +
    `; yaw asked ${spec.yaw}` + (flown.length ? `, worker reported ${flown.join(" and ")}` : "");
}
function renderDetail(agg) {
  const { planner: p, key: k } = S.sel, c = agg.cells[p] && agg.cells[p][k];
  if (!c) { $("#detail").hidden = true; return; }
  const errs = S.sweep.records.filter(r => r && r.planner === p && SW.variationKey(r.preset, r.fault) === k && r.outcome === "error");
  $("#detail").hidden = false;
  $("#detail").innerHTML = `<b>${esc(SW.plannerLabel(p))}</b>, ${esc(SW.variationLabel(k, S.sweep.spec))}` +
    `<dl><dt>reached B</dt><dd>${c.reached}/${c.n} runs; distinct runs ${c.reached_distinct}/${c.n_distinct} = ${pct(c.success.p)} ` +
    `(95 % Wilson on the ${c.n_distinct} distinct runs: ${pct(c.success.lo)}-${pct(c.success.hi)})</dd>` +
    (c.no_path ? `<dt>no path</dt><dd>${c.no_path} run${c.no_path > 1 ? "s" : ""} (seeds ${esc(S.sweep.records.filter(r => r && r.planner === p && SW.variationKey(r.preset, r.fault) === k && SW.isNoPath(r)).map(r => r.seed).join(", "))}): the worker found no free path from A to B at the vehicle radius; kept out of n, the interval and the ranking.</dd>` : "") +
    (c.identical ? `<dt>deterministic</dt><dd class="dup">${c.identical} of ${c.n} runs are identical to another run (same outcome, time to B and path length at 3 dp); each set counts as one trial.</dd>` : "") +
    `<dt>sensor</dt><dd class="small">${esc(sensorText(SW.sensorSpecOf(k.split("|")[0], S.sweep.spec)))}</dd>` +
    `<dt>vehicle, yaw</dt><dd class="small">${esc(vehText(S.sweep.spec, k))}</dd>` +
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
  if (!runs.length) { $("#poolMsg").textContent = `No finished run for ${SW.variationLabel(key, sw.spec)}, seed ${seed} yet.`; return false; }
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
$("#faultSel").onchange = manualVariations;
$("#tlimSel").onchange = updateCount;
$("#allBtn").onclick = () => { document.querySelectorAll('input[name="planner"]').forEach(i => { i.checked = true; }); updateCount(); };
$("#noneBtn").onclick = () => { document.querySelectorAll('input[name="planner"]').forEach(i => { i.checked = false; }); updateCount(); };

// A manual change to the sensor presets, the fault or the drone's sensor drops the Stress variation subset.
function manualVariations() { S.vars = null; updateCount(); }
function preset(seeds, presets, resetFault, vars, fault) {
  $("#seedsIn").value = seeds;
  document.querySelectorAll('input[name="preset"]').forEach(i => { i.checked = presets.includes(i.value); });
  if (resetFault) $("#faultSel").value = "";
  if (fault) $("#faultSel").value = fault;
  S.vars = vars || null;
  updateCount();
  if (S.readyCount) return startSweep();
  S.autoStart = true;
  $("#poolMsg").textContent = "The sweep starts when Python is ready.";
  return null;
}
// Quick: 5 seeds (SW.QUICK_SEEDS), your drone's sensor only (ideal by default; Custom => the custom variation alone), truth pose only.
// Thorough: 10 seeds (SW.THOROUGH_SEEDS), ideal + crazyflie + your drone's sensor, keeps the fault.
const droneP = () => { const c = $("#droneSensor").value || "ideal"; return c === SW.CUSTOM ? [] : [c]; };
const quick = () => preset(SW.QUICK_SEEDS, droneP(), true);
const thorough = () => preset(SW.THOROUGH_SEEDS, [...new Set(["ideal", "crazyflie", ...droneP()])], false);
// Stress (loop-89): 5 seeds (SW.STRESS_SEEDS), the drone's sensor + crazyflie on truth pose, and the drone's sensor
// with one VIO fault (the chosen one, else SW.STRESS_FAULT = jump). crazyflie flies truth pose only (S.vars).
function stress() {
  const c = $("#droneSensor").value || "ideal", key = c === SW.CUSTOM ? SW.CUSTOM : c;
  const offered = [...$("#faultSel").options].map(o => o.value).filter(Boolean);
  const want = $("#faultSel").value || SW.STRESS_FAULT, fault = offered.includes(want) ? want : offered.includes(SW.STRESS_FAULT) ? SW.STRESS_FAULT : null;
  const vars = fault ? SW.stressVariations(key, fault) : SW.stressVariations(key).filter(k => k.endsWith("|truth"));
  return preset(SW.STRESS_SEEDS, [...new Set([...droneP(), SW.STRESS_PRESET])], !fault, vars, fault);
}
$("#quickBtn").onclick = quick;
$("#thoroughBtn").onclick = thorough;
$("#stressBtn").onclick = stress;

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

// Recommend: recommend.md + recommend.json from the export doc and the benchmark summary (advisor.json).
let advisorP = null;
async function recommendNow() {
  const t = exportJSON(); if (!t) return null;
  advisorP = advisorP || fetch(PG + "data/advisor.json").then(r => (r.ok ? r.json() : null)).catch(() => null);
  const adv = await advisorP;
  const r = REC.recommend(JSON.parse(t), adv);
  return { md: r.md, json: JSON.stringify(r.json, null, 1) + "\n", advisor: !!adv };
}
$("#recBtn").onclick = async () => {
  const r = await recommendNow(); if (!r) return;
  download("recommend.md", r.md, "text/markdown");
  download("recommend.json", r.json, "application/json");
  $("#shareMsg").textContent = "recommend.md and recommend.json downloaded" + (r.advisor ? "." : " (benchmark rows missing: advisor.json did not load).");
};

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
if (window.ResizeObserver) { const ro = new ResizeObserver(() => { drawAll(); drawPareto(); }); ro.observe($("#race")); ro.observe($("#preview")); ro.observe($("#pareto")); }
else window.addEventListener("resize", () => { drawAll(); drawPareto(); });

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

window.SOLVER = { S, K, ready: readyP, started, quick, thorough, stress, pareto: () => paretoLast, run: startSweep, cancel: () => cancelSweep("cancelled"),
  exportJSON, recommend: recommendNow, csv: () => (S.sweep ? SW.toCSV(S.sweep.records.filter(Boolean)) : null), animate: startAnim, setT: setAnimT,
  shareUrl, loadPreset, allReady: () => S.readyCount >= K };
