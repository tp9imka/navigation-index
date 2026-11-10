// Solver "Recommend" export (pure, no DOM): turns a finished sweep (SW.exportDoc) plus the playground's
// benchmark summary (site/playground/data/advisor.json) into recommend.md and recommend.json: the pick
// (winner, tied set or nobody), the templates/flight-repo command to fly it, the arm choice from the
// world's narrowest passage, what the sweep flew, and the benchmark rows of the pick.
// Unit tests: node --test site/solver/test_sweep.mjs
import { clearanceAt, overlaps, plannerLabel, timeLimitText, variationLabel, sensorSpecOf, customLabel,
  isDefaultVehicle, normVehicle } from "./sweep.js?v=20261110d";

export const SCHEMA = "navidx-solver-recommend/1";
// F2 (samples/close-area-safety-filter/filters.py, eps = 0.7 m) holds the vehicle centre 0.7 m from every
// return, so a passage narrower than 2 x 0.7 = 1.4 m is closed to it (flight-repo results/first_flight_bench.txt:
// narrow_gap_0, gap 0.764 m, F2 stuck, F0 reached).
export const F2_EPS_M = 0.7;
export const NARROW_PASSAGE_M = 2 * F2_EPS_M;
export const GRID_M = 0.05;                  // ESDF grid of the bottleneck search
export const GOAL_TOL_M = 0.2;               // flight-repo loop.py GOAL_TOL_M
export const CAVEAT = "synthetic 2.5D simulation, scored on truth, not a flight result; n seeds on one map is a small sample";
// What `make first-flight` flies (samples/close-area-arena/run.py DEFAULTS, read by flight-repo arena_adapter.py).
export const FLIGHT_DEFAULTS = { vehicle: { radius_m: 0.15, v_max: 2.0, a_max: 3.0, tau: 0.15 },
  sensor: "ideal: 72 beams, 360 deg, 6 m, noise 0.02 m, dropout 0.02 (run.DEFAULTS)", pose: "truth (no FAULT=)", seed: 0,
  loop_hz: 20, ab: "the world file's exact A and B" };
const PRESET_PATH = name => `../../site/playground/presets/${name}.json`;   // relative to templates/flight-repo

// ------------------------------------------------------------ narrowest passage
// Bottleneck (max-min) clearance of the best route from A to B on an ESDF grid: every cell centre gets
// clearanceAt (centre to the nearest surface, bounds count as walls); a maximin Dijkstra (8-connected)
// finds the route whose lowest clearance is highest. Cells within F2_EPS_M of A count as free (a filter
// lets the vehicle back away from a close return at the start); the goal is any cell within GOAL_TOL_M of B.
// Returns { clearance_m, passage_m = 2 x clearance, at: [x, y] of the bottleneck cell, grid_m } or null
// when no free route exists on the grid.
export function narrowestPassage(doc, res = GRID_M) {
  const [x0, y0, x1, y1] = doc.bounds;
  const nx = Math.max(1, Math.ceil((x1 - x0) / res)), ny = Math.max(1, Math.ceil((y1 - y0) / res)), N = nx * ny;
  const cx = i => x0 + (i + 0.5) * res, cy = j => y0 + (j + 0.5) * res;
  const a = doc.a || [0, 0], b = doc.b;
  const val = new Float64Array(N), goal = new Uint8Array(N);
  for (let j = 0; j < ny; j++) for (let i = 0; i < nx; i++) {
    const k = j * nx + i, x = cx(i), y = cy(j), v = clearanceAt(doc, x, y);
    val[k] = v > 0 && Math.hypot(x - a[0], y - a[1]) <= F2_EPS_M ? Infinity : v;
    if (v > 0 && Math.hypot(x - b[0], y - b[1]) <= GOAL_TOL_M) goal[k] = 1;
  }
  const ia = Math.min(nx - 1, Math.max(0, Math.floor((a[0] - x0) / res))), ja = Math.min(ny - 1, Math.max(0, Math.floor((a[1] - y0) / res)));
  const s = ja * nx + ia;
  if (!(val[s] > 0)) return null;
  const best = new Float64Array(N).fill(-Infinity), from = new Int32Array(N).fill(-1);
  // binary max-heap of [value, cell]
  const hv = [], hk = [];
  const push = (v, k) => { let i = hv.length; hv.push(v); hk.push(k);
    while (i > 0) { const p = (i - 1) >> 1; if (hv[p] >= hv[i]) break; [hv[p], hv[i]] = [hv[i], hv[p]]; [hk[p], hk[i]] = [hk[i], hk[p]]; i = p; } };
  const pop = () => { const v = hv[0], k = hk[0], lv = hv.pop(), lk = hk.pop();
    if (hv.length) { hv[0] = lv; hk[0] = lk; let i = 0;
      for (;;) { const l = 2 * i + 1, r = l + 1; let m = i;
        if (l < hv.length && hv[l] > hv[m]) m = l; if (r < hv.length && hv[r] > hv[m]) m = r;
        if (m === i) break; [hv[m], hv[i]] = [hv[i], hv[m]]; [hk[m], hk[i]] = [hk[i], hk[m]]; i = m; } }
    return [v, k]; };
  best[s] = val[s]; push(val[s], s);
  while (hv.length) {
    const [v, k] = pop();
    if (v < best[k]) continue;
    if (goal[k]) {
      // walk back to the cell that set the bottleneck
      let at = k, c = k;
      while (c >= 0) { if (val[c] < val[at]) at = c; c = from[c]; }
      const clr = Math.round(v * 1e4) / 1e4;
      return { clearance_m: clr, passage_m: Math.round(2 * v * 1e4) / 1e4, at: [+cx(at % nx).toFixed(3), +cy(Math.floor(at / nx)).toFixed(3)], grid_m: res };
    }
    const i = k % nx, j = (k - i) / nx;
    for (let dj = -1; dj <= 1; dj++) for (let di = -1; di <= 1; di++) {
      if (!di && !dj) continue;
      const ii = i + di, jj = j + dj;
      if (ii < 0 || jj < 0 || ii >= nx || jj >= ny) continue;
      const n = jj * nx + ii;
      if (!(val[n] > 0)) continue;
      const w = Math.min(v, val[n]);
      if (w > best[n]) { best[n] = w; from[n] = k; push(w, n); }
    }
  }
  return null;
}

// F2 by default; F0 (no filter) with a warning when the narrowest passage is below 1.4 m.
export function chooseArm(passage) {
  if (!passage) return { arm: "F2", warning: "No free route from A to B was found on the 0.05 m grid; F2 (default) kept. Check the world in the playground editor." };
  if (passage.passage_m < NARROW_PASSAGE_M) return { arm: "F0",
    warning: `WARNING: ARM=F0 flies with NO safety filter. The narrowest passage on the best route A=>B is about ${passage.passage_m.toFixed(2)} m ` +
      `(at ${passage.at[0]}, ${passage.at[1]}), below ${NARROW_PASSAGE_M} m: F2 keeps the centre ${F2_EPS_M} m from every return and cannot pass ` +
      "(flight-repo results/first_flight_bench.txt: narrow_gap_0, F2 stuck, F0 reached). Retry F2 with a smaller eps before a real flight." };
  return { arm: "F2", warning: null };
}

// ------------------------------------------------------------ benchmark rows
// Solver (worker) planner id => close-area-benchmark id (advisor.planners[id].playground, filter none).
export function benchId(pid, advisor) {
  const pl = (advisor && advisor.planners) || {};
  for (const [id, p] of Object.entries(pl)) if (p.playground && p.playground.planner === pid && (p.playground.filter || "none") === "none") return id;
  return (advisor && advisor.playground_to_bench && advisor.playground_to_bench[pid]) || pid;
}
// One row per family: reached / collision % with the ideal and crazyflie sensors (advisor.cells).
export function benchRows(id, advisor) {
  if (!advisor || !advisor.cells) return [];
  return (advisor.families || Object.keys(advisor.cells)).map(f => {
    const row = { family: f, label: (advisor.family_labels || {})[f] || f };
    for (const p of ["ideal", "crazyflie"]) {
      const c = advisor.cells[f] && advisor.cells[f][p] && advisor.cells[f][p][id];
      row[p] = c ? { n: c.n, reached_pct: c.reached, collision_pct: c.collision, median_time_s: c.median_time_s } : null;
    }
    return row;
  });
}

// ------------------------------------------------------------ the pick
const pct = v => `${Math.round(v * 100)} %`;
const f2 = v => (v == null ? "-" : v.toFixed(2));
const rowOf = (r, advisor) => ({ planner: r.planner, label: plannerLabel(r.planner), bench_id: benchId(r.planner, advisor),
  reached: r.reached, n: r.n, n_distinct: r.n_distinct, reached_distinct: r.reached_distinct,
  wilson_95: { lo: r.success.lo, hi: r.success.hi, p: r.success.p }, median_time_s: r.median_time_s,
  min_clearance_m: r.min_clearance_m, collisions: r.collision, stuck: r.stuck, timeout: r.timeout, error: r.error });

// kind: winner (headline winner or the only planner run), tie (every planner whose Wilson interval overlaps
// the best one's), none (no planner reached B), empty.
export function pick(doc) {
  const rk = doc.ranking || [], h = doc.headline || { kind: "empty" };
  if (!rk.length || h.kind === "empty") return { kind: "empty", top: null, set: [] };
  if (h.kind === "none" || rk[0].reached === 0) return { kind: "none", top: null, set: rk };
  if (h.kind === "tie") return { kind: "tie", top: rk[0], set: rk.filter(r => overlaps(r.success, rk[0].success)) };
  return { kind: "winner", top: rk[0], set: rk.slice(0, 2) };     // winner and runner-up (both intervals)
}

export function worldFile(doc) {
  if (doc.world_name) return { path: PRESET_PATH(doc.world_name), inline: false,
    how: `Preset ${doc.world_name}: the hub ships it at site/playground/presets/${doc.world_name}.json (the path below is relative to templates/flight-repo). The same world is inline in recommend.json ("world").` };
  return { path: "my_world.json", inline: true,
    how: "Custom world: save it from recommend.json (its \"world\" field) next to the Makefile: " +
      "python3 -c \"import json; json.dump(json.load(open('recommend.json'))['world'], open('my_world.json', 'w'))\"" };
}
export const flightCommand = (id, file, arm) => `make first-flight PLANNER=bench:${id} WORLD=${file} ARM=${arm}`;

// What to try when no planner reached B (at most 5 items).
function nextSteps(doc, passage, advisor) {
  const rk = doc.ranking || [], out = [];
  const radius = (doc.spec && doc.spec.vehicle && doc.spec.vehicle.radius_m) || 0.15;
  if (!passage || passage.passage_m < 2 * radius)
    out.push(`The map may have no route for the vehicle: the widest route's narrowest passage is ${passage ? passage.passage_m.toFixed(2) + " m" : "none on the grid"} vs ${2 * radius} m vehicle diameter. Check A, B and the walls in the playground editor.`);
  const tout = rk.reduce((a, r) => a + r.timeout, 0), stuck = rk.reduce((a, r) => a + r.stuck, 0), coll = rk.reduce((a, r) => a + r.collision, 0);
  if (tout) out.push(`${tout} runs timed out: raise the Run time limit to 120 or 180 s.`);
  out.push(`Outcomes over all planners: ${stuck} stuck, ${coll} collision, ${tout} timeout. Run Thorough (10 seeds, ideal + crazyflie) before concluding.`);
  const fam = doc.world && doc.world.family, rec = advisor && advisor.recommend && fam && advisor.recommend[fam] && advisor.recommend[fam].ideal;
  if (rec) for (const k of ["no_map", "prior_map"]) if (rec[k] && rec[k].winner) {
    const ran = rk.some(r => benchId(r.planner, advisor) === rec[k].winner);
    out.push(`Benchmark best on ${fam} (${k === "no_map" ? "no prior map" : "prior map"}, ideal sensor): ${rec[k].winner}` + (ran ? " (in this sweep, failed here)" : " (not in this sweep: add it)") + `. ${rec[k].reason}`);
  }
  return out.slice(0, 5);
}

// ------------------------------------------------------------ the export
export function recommend(doc, advisor) {
  const p = pick(doc), passage = narrowestPassage(doc.world), armc = chooseArm(passage), wf = worldFile(doc);
  const spec = doc.spec || {}, seeds = spec.seeds, fam = doc.world && doc.world.family;
  const rows = p.set.map(r => rowOf(r, advisor));
  let flyId = p.top ? benchId(p.top.planner, advisor) : null, flyNote = null;
  if (p.kind === "none") {
    const rec = advisor && advisor.recommend && fam && advisor.recommend[fam] && advisor.recommend[fam].ideal;
    flyId = rec && rec.no_map && rec.no_map.winner || null;
    flyNote = flyId ? `No planner reached B here; this is the benchmark's best map-free planner on ${fam}, untested on this map.` : null;
  }
  const command = flyId ? flightCommand(flyId, wf.path, armc.arm) : null;
  const winClr = p.top ? p.top.min_clearance_m : null;
  const passageNote = "Narrowest passage = 2 x the bottleneck clearance of the best route A=>B on a 0.05 m ESDF grid of the world " +
    "(maximin search, cells within 0.7 m of A free, goal = within 0.2 m of B). Chosen over 2 x the winner's min clearance because a run's " +
    "min clearance is its closest approach to any surface (a corner it cut), not the width it had to pass: in site/solver/results/quick_random_0.json D* Lite's 0.583 m gives 1.17 m " +
    "(=> F0) on a map whose best route never narrows below 3.6 m. Grid error up to about 0.05 m.";
  const flown = {
    vehicle: normVehicle(spec.vehicle), vehicle_default: isDefaultVehicle(spec.vehicle),
    sensors: (spec.presets || []).map(pr => ({ preset: pr, label: pr === "custom" ? customLabel(spec.sensor) : pr, spec: sensorSpecOf(pr, spec) })),
    variations: (spec.presets || []).flatMap(pr => (spec.faults || []).map(f => variationLabel(`${pr}|${f}`, spec))),
    yaw: spec.yaw || "fixed", yaw_policy_flown: (doc.drone && doc.drone.yaw_policy_flown) || [],
    jitter_m: spec.jitter || 0, time_limit: timeLimitText(spec, doc.world, doc.records || []),
    seeds, runs: doc.records_n, cancelled: !!doc.cancelled, finished: doc.finished || null };
  const fbench = flyId ? benchRows(flyId, advisor) : [];
  const json = { schema: SCHEMA, input: "synthetic", caveat: CAVEAT.replace("n seeds", `${seeds} seeds`),
    world_name: doc.world_name || null, family: fam || null, headline: doc.headline, kind: p.kind,
    pick: rows, fly: flyId ? { planner_bench_id: flyId, command, arm: armc.arm, arm_warning: armc.warning, note: flyNote,
      cwd: "templates/flight-repo", out: `results/first_flight_bench_${flyId}_${wf.path.replace(/^.*\//, "").replace(/\.json$/, "")}`,
      flies: FLIGHT_DEFAULTS } : null,
    passage: { ...(passage || { clearance_m: null, passage_m: null }), method: passageNote, narrow_below_m: NARROW_PASSAGE_M,
      winner_min_clearance_x2_m: winClr == null ? null : Math.round(2 * winClr * 1e4) / 1e4 },
    world_file: wf, flown, next_steps: p.kind === "none" ? nextSteps(doc, passage, advisor) : [],
    benchmark: { source: "site/playground/data/advisor.json", from: advisor && advisor.sources ? advisor.sources.matrix : null,
      run: advisor && advisor.bench ? { command: advisor.bench.command, layouts: advisor.bench.layouts, seed: advisor.bench.seed, date: advisor.bench.date, pose: advisor.bench.pose } : null,
      planner: flyId, rows: fbench,
      tied_family: p.kind === "tie" && fam ? rows.map(r => ({ planner: r.bench_id, rows: benchRows(r.bench_id, advisor).filter(x => x.family === fam) })) : [] },
    sweep_source: { schema: doc.schema, started: doc.started || null, finished: doc.finished || null },
    world: doc.world };
  return { json, md: toMarkdown(json, p) };
}

// ------------------------------------------------------------ markdown
const cellTxt = c => (c ? `${c.reached_pct} / ${c.collision_pct}` : "-");
function toMarkdown(j, p) {
  const L = [], name = j.world_name || "custom world";
  L.push(`# Recommend: ${name}`, "");
  L.push(`**${j.caveat.charAt(0).toUpperCase() + j.caveat.slice(1)}.**`, "");
  L.push(`Solver headline: ${j.headline.text}`, "");
  if (p.kind === "winner") L.push(`## Pick: ${j.pick[0].label} (\`bench:${j.pick[0].bench_id}\`)`, "",
    j.pick.length > 1 ? "Its 95 % Wilson interval does not overlap the runner-up's. Both rows:" : "Only this planner was run:");
  else if (p.kind === "tie") L.push(`## Pick: no clear winner, tied set of ${j.pick.length}`, "",
    `Every planner whose 95 % Wilson interval overlaps the best one's (${j.pick[0].label}, ${pct(j.pick[0].wilson_95.lo)}-${pct(j.pick[0].wilson_95.hi)}). ` +
    `The command below flies the top of the ranking (success, then median time to B); any row is an equally supported choice at this n.`);
  else L.push("## Pick: no planner reached B", "", "Every planner in the sweep failed on this map. All rows:");
  L.push("", "| planner | bench id | reached | 95 % Wilson | n | n distinct | median time to B s | min clearance m | collisions |",
    "|---|---|---|---|---|---|---|---|---|");
  for (const r of j.pick) L.push(`| ${r.label} | ${r.bench_id} | ${r.reached}/${r.n} | ${pct(r.wilson_95.lo)}-${pct(r.wilson_95.hi)} | ${r.n} | ${r.n_distinct} | ${f2(r.median_time_s)} | ${r.min_clearance_m == null ? "-" : r.min_clearance_m.toFixed(3)} | ${r.collisions} |`);
  L.push("");
  if (j.next_steps.length) { L.push("What to try next:", ""); j.next_steps.forEach((s, i) => L.push(`${i + 1}. ${s}`)); L.push(""); }
  L.push("## Fly it: templates/flight-repo", "");
  if (j.fly) {
    if (j.fly.note) L.push(j.fly.note, "");
    L.push("```sh", "cd templates/flight-repo", j.fly.command, "```", "");
    L.push(`Writes ${j.fly.out}.jsonl, .png and _score.json (score_log.py). ARM=${j.fly.arm}` +
      (j.fly.arm === "F2" ? ` (default): the narrowest passage is ${j.passage.passage_m == null ? "unknown" : j.passage.passage_m.toFixed(2) + " m"}, at least ${NARROW_PASSAGE_M} m.` : "."), "");
    if (j.fly.arm_warning) L.push(`> ${j.fly.arm_warning}`, "");
  } else L.push("No command: no planner to fly.", "");
  L.push(`- World file: ${j.world_file.how}`);
  L.push(`- Narrowest passage: ${j.passage.passage_m == null ? "no route on the grid" : j.passage.passage_m.toFixed(2) + " m (bottleneck clearance " + j.passage.clearance_m.toFixed(3) + " m at " + j.passage.at.join(", ") + ")"}` +
    (j.passage.winner_min_clearance_x2_m != null ? `; proxy 2 x the pick's min clearance = ${j.passage.winner_min_clearance_x2_m.toFixed(2)} m, not used.` : "."));
  L.push(`- How: ${j.passage.method}`);
  L.push(`- The command flies run.DEFAULTS, not the sweep: vehicle radius 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s; sensor ${FLIGHT_DEFAULTS.sensor}; pose truth; seed 0; ${FLIGHT_DEFAULTS.ab}; 20 Hz loop with the arm filter.`, "");
  const f = j.flown, v = f.vehicle || {};
  L.push("## What the sweep flew", "");
  L.push(`- Vehicle: radius ${v.radius_m} m, v_max ${v.v_max} m/s, a_max ${v.a_max} m/s^2, tau ${v.tau} s${f.vehicle_default ? " (arena default)" : ""}`);
  for (const s of f.sensors) { const x = s.spec || {};
    L.push(`- Sensor ${s.label}: ${x.beams} beams, FoV ${x.fov_deg} deg, ${x.min_range_m}-${x.max_range_m} m, noise ${x.noise_sigma_m} m`); }
  L.push(`- Variations: ${f.variations.join("; ")}`);
  L.push(`- Yaw: asked ${f.yaw}${f.yaw_policy_flown.length ? ", worker reported " + f.yaw_policy_flown.join(" and ") : ""}`);
  L.push(`- Start/goal jitter: ${f.jitter_m ? f.jitter_m + " m radius (seed 0 exact map)" : "off"}`);
  L.push(`- ${f.time_limit}`);
  L.push(`- Seeds: ${f.seeds} (0..${f.seeds - 1}), ${f.runs} runs${f.cancelled ? ", CANCELLED before the end" : ""}; finished ${f.finished || "-"}`, "");
  const b = j.benchmark;
  if (b.planner && b.rows.length) {
    L.push(`## Benchmark rows for ${b.planner} (beyond this map)`, "");
    L.push(`From ${b.source} (built from ${b.from}): ${b.run ? `${b.run.layouts} layouts per family, seed ${b.run.seed}, ${b.run.pose}, ${b.run.date}` : ""}; synthetic. Cells: reached % / collision %.`, "");
    L.push("| family | ideal | crazyflie |", "|---|---|---|");
    for (const r of b.rows) L.push(`| ${r.family}${r.family === j.family ? " (this map's family)" : ""} | ${cellTxt(r.ideal)} | ${cellTxt(r.crazyflie)} |`);
    L.push("");
  }
  if (b.tied_family.length) {
    L.push(`Tied set on the ${j.family} family (benchmark, reached % / collision %):`, "", "| bench id | ideal | crazyflie |", "|---|---|---|");
    for (const t of b.tied_family) { const r = t.rows[0]; L.push(`| ${t.planner} | ${cellTxt(r && r.ideal)} | ${cellTxt(r && r.crazyflie)} |`); }
    L.push("");
  }
  L.push("Generated by the Solver's Recommend button (site/solver/recommend.js).", "");
  return L.join("\n");
}
