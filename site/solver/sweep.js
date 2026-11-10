// Solver sweep logic (pure, no DOM, no workers): run list, aggregation, Wilson interval, ranking,
// headline, start/goal jitter per seed, duplicate-run collapsing, CSV / JSON export, share-link spec
// codec and the time estimate.
// Unit tests: node --test site/solver/test_sweep.mjs

export const SCHEMA = "navidx-solver-sweep/1";

// Same labels as site/playground/playground.js LABELS (copied, playground.js is not imported).
export const PLANNER_LABELS = {
  straight: "straight line to B", freest_beam: "freest beam (reactive)", astar_known: "A* + ESDF, known map",
  astar_unknown: "A* + ESDF, unknown map", apf: "APF + wall follow", vfh_plus: "VFH+",
  dwa: "DWA (dynamic window)", dwa_mem: "DWA + 3 s scan memory", bug2: "Bug2", tangent_bug: "TangentBug",
  dstar_lite: "D* Lite, unknown map (geofenced)", informed_rrt_star: "Informed RRT* 5000, known map",
  thetastar_known: "Theta* (any-angle), known map", lazy_thetastar_known: "Lazy Theta*, known map",
  lazy_thetastar_unknown: "Lazy Theta*, unknown map (geofenced)",
  mppi: "MPPI, goal only (no global plan)", mppi_astar: "MPPI on the unknown-map A* path",
  hybrid_astar: "Hybrid A*, unknown map (geofenced)",
};
export const PRESET_LABELS = { ideal: "ideal: 72 rays, 360 deg, 6 m", crazyflie: "Crazyflie: 4 cone beams, 3 m",
  depth_cam_87: "depth camera: 30 beams, 87 deg forward, 0.3-5 m", lidar_2d: "2D lidar: 360 beams, 360 deg, 0.15-12 m" };
export const FAULT_LABELS = { truth: "off: planner sees truth", none: "VIO EKF, no fault", jump: "VIO jump 0.5 m",
  bias: "VIO bias 0.05 m/s, 10 s", dropout: "VIO dropout 2 s" };
export const SWEEP_PRESETS = ["ideal", "crazyflie", "depth_cam_87", "lidar_2d"];
export const CUSTOM = "custom";                  // variation key of the "Your drone" custom sensor

// Sensor presets in the team-facing schema (copied from samples/close-area-arena/presets.py: SENSOR_PRESETS
// for ideal and crazyflie, SENSOR_SPECS for depth_cam_87 and lidar_2d). Used for labels, CSV columns and
// the beam count of the time estimate; the worker flies its own copy. ideal has no minimum range (ray model)
// and crazyflie's noise grows with range (zranger model, 0.02 m is the floor).
export const PRESET_SPECS = {
  ideal: { beams: 72, fov_deg: 360, max_range_m: 6.0, min_range_m: 0, noise_sigma_m: 0.02, cone_deg: 0, dropout: 0.02 },
  crazyflie: { beams: 4, fov_deg: 360, max_range_m: 3.0, min_range_m: 0.04, noise_sigma_m: 0.02, cone_deg: 27.0, dropout: 0.05 },
  depth_cam_87: { beams: 30, fov_deg: 87.0, max_range_m: 5.0, min_range_m: 0.3, noise_sigma_m: 0.04, cone_deg: 87.0 / 29, dropout: 0.05 },
  lidar_2d: { beams: 360, fov_deg: 360, max_range_m: 12.0, min_range_m: 0.15, noise_sigma_m: 0.03, cone_deg: 0, dropout: 0.02 },
};
// Vehicle: run.DEFAULTS["vehicle"] (= presets.py VEHICLE_SPECS["default"]) and the worker's VEHICLE_CLAMP.
export const VEHICLE_DEFAULT = { radius_m: 0.15, v_max: 2.0, a_max: 3.0, tau: 0.15 };
export const VEHICLE_KEYS = ["radius_m", "v_max", "a_max", "tau"];
export const VEHICLE_CLAMP = { radius_m: [0.05, 0.6], v_max: [0.1, 5.0], a_max: [0.5, 20.0], tau: [0.02, 1.0] };
// Custom sensor: the fields the panel shows, defaults = depth_cam_87 numbers, ranges = worker SENSOR_CLAMP.
// cone_deg and dropout are not sent: the worker fills presets.py SENSOR_SPEC_DEFAULTS (0 deg, 0.02).
export const SENSOR_KEYS = ["beams", "fov_deg", "max_range_m", "min_range_m", "noise_sigma_m"];
export const SENSOR_DEFAULT = { beams: 30, fov_deg: 87, max_range_m: 5, min_range_m: 0.3, noise_sigma_m: 0.04 };
export const SENSOR_CLAMP = { beams: [1, 360], fov_deg: [1, 360], max_range_m: [0.5, 30], min_range_m: [0, 5], noise_sigma_m: [0, 0.5] };
export const MIN_RANGE_GAP_M = 0.1;              // worker: min_range_m <= max_range_m - 0.1
// Yaw policy request (cfg.yaw). "fixed" is the worker default and is never sent.
export const YAW_CHOICES = ["fixed", "look_where_you_go"];
export const YAW_LABELS = { fixed: "fixed (worker default)", look_where_you_go: "look where you go" };
export const EXTRA_FAULTS = ["none", "jump", "bias", "dropout"];
export const OUTCOMES = ["reached", "collision", "stuck", "timeout", "error"];
export const MAX_SEEDS = 50;
// Quick / Thorough buttons (loop-87): with 3 seeds 3/3 (44-100 %) overlaps 0/3 (0-56 %), so Quick could never
// name a winner; with 5 seeds 5/5 (57-100 %) is disjoint from 0/5 (0-43 %).
export const QUICK_SEEDS = 5;
export const THOROUGH_SEEDS = 10;
// Stress button (loop-89): on random_0 17 of 18 planners reached B 5/5 under Quick, so success cannot order
// them. Stress keeps Quick's 5 seeds and adds the variations that make the sensor or the pose worse:
// the drone's sensor (truth pose), crazyflie (4 beams, truth pose) and the drone's sensor with one VIO fault.
export const STRESS_SEEDS = QUICK_SEEDS;
export const STRESS_FAULT = "jump";              // worker faults: none, jump, bias, dropout (worker.js env.faults)
export const STRESS_PRESET = "crazyflie";
// Variation keys of a Stress sweep for the drone's sensor key (a preset name or CUSTOM) and fault.
export function stressVariations(sensorKey, fault = STRESS_FAULT) {
  const d = sensorKey || "ideal", f = EXTRA_FAULTS.includes(fault) ? fault : STRESS_FAULT;
  return [...new Set([`${d}|truth`, `${STRESS_PRESET}|truth`, `${d}|${f}`])];
}
// Headline: more planners than this overlapping the best one => "N planners tie at the top".
export const BIG_TIE = 5;
export const JITTER_RADII = [0.25, 0.5, 1.0];     // m, start/goal jitter radius choices
export const JITTER_DEFAULT = 0.5;
export const JITTER_MARGIN_M = 0.1;              // jittered A/B keep vehicle radius + this from any surface
export const JITTER_DRAWS = 50;                  // draws per point before the exact point is kept
export const VEHICLE_RADIUS_M = 0.15;            // close-area arena default (world.py RADIUS)
// Run time limit (loop-73b). "auto" = by map family, the rule of site/playground/worker.js max_time_for,
// which copies samples/close-area-benchmark/bench.py LONG_FAMILIES. A world without a long family
// (other presets, custom worlds) gets run.DEFAULTS max_time_s = 60 s.
export const LONG_FAMILIES = { maze: 120, warehouse: 120 };
export const DEFAULT_MAX_TIME_S = 60;
export const TIME_LIMITS = ["auto", 60, 120, 180];

export const plannerLabel = p => PLANNER_LABELS[p] || p;
export const variationKey = (preset, fault) => `${preset}|${fault}`;
const g = v => String(Math.round(v * 1000) / 1000);
// "custom 30 beams 87 deg 5 m"
export const customLabel = s => (s ? `custom ${s.beams} beams ${g(s.fov_deg)} deg ${g(s.max_range_m)} m` : "custom");
export const presetName = (p, spec) => (p === CUSTOM ? customLabel(spec && spec.sensor) : p);
export const variationLabel = (key, spec) => { const [p, f] = key.split("|"); return `${presetName(p, spec)} / ${f === "truth" ? "truth pose" : "VIO " + f}`; };
// Sensor spec of a variation preset: the custom dict, or the preset table.
export const sensorSpecOf = (preset, spec) => (preset === CUSTOM ? (spec && spec.sensor) || null : PRESET_SPECS[preset] || null);

// Browser Python seconds per run from site/playground/README.md (synthetic, one preset each) and the
// spike table there; only a prior for the estimate before this browser has measured its own runs.
export const PRIOR_WALL_S = { straight: 0.1, freest_beam: 0.2, astar_known: 0.7, astar_unknown: 3.0, apf: 0.3, vfh_plus: 0.3,
  dwa: 1.0, dwa_mem: 2.4, bug2: 0.2, tangent_bug: 0.25, dstar_lite: 1.3, informed_rrt_star: 0.8,
  // loop-73: mean of random_0 and maze_0, site/playground/results/playground_loop73.md
  thetastar_known: 6.6, lazy_thetastar_known: 4.3, lazy_thetastar_unknown: 20.5, mppi: 1.7, mppi_astar: 7.7,
  hybrid_astar: 1.7 };
export const PRIOR_DEFAULT_S = 1.0;
// The priors were measured with the ideal sensor (72 beams). A run with b beams gets prior x b / 72, at least
// x BEAM_FACTOR_MIN [proposal: planner time does not vanish with 4 beams]. Measured times are not scaled.
export const PRIOR_BEAMS = 72;
export const BEAM_FACTOR_MIN = 0.25;
export const beamFactor = beams => (Number.isFinite(beams) && beams > 0 ? Math.max(BEAM_FACTOR_MIN, beams / PRIOR_BEAMS) : 1);

// ------------------------------------------------------------ vehicle, sensor, yaw
const clampNum = (v, [lo, hi], dflt) => { const n = Number(v); return v === "" || v == null || !Number.isFinite(n) ? dflt : Math.min(hi, Math.max(lo, n)); };
// All four keys, each clamped to the worker's range; missing or not a number => arena default.
export function normVehicle(v) {
  const s = v && typeof v === "object" ? v : {};
  return Object.fromEntries(VEHICLE_KEYS.map(k => [k, clampNum(s[k], VEHICLE_CLAMP[k], VEHICLE_DEFAULT[k])]));
}
export const isDefaultVehicle = v => VEHICLE_KEYS.every(k => normVehicle(v)[k] === VEHICLE_DEFAULT[k]);
// Custom sensor dict as the worker will fly it (same clamping, beams an integer, min range below max).
export function normSensor(v) {
  const s = v && typeof v === "object" ? v : {};
  const out = Object.fromEntries(SENSOR_KEYS.map(k => [k, clampNum(s[k], SENSOR_CLAMP[k], SENSOR_DEFAULT[k])]));
  out.beams = Math.round(out.beams);
  if (out.min_range_m > out.max_range_m - MIN_RANGE_GAP_M) out.min_range_m = Math.round((out.max_range_m - MIN_RANGE_GAP_M) * 1e6) / 1e6;
  return out;
}
export const normYaw = v => (YAW_CHOICES.includes(v) ? v : "fixed");
// "Your drone" sensor choice: a sweep preset name or "custom".
export const normSensorChoice = v => (v === CUSTOM || SWEEP_PRESETS.includes(v) ? v : "ideal");

// ------------------------------------------------------------ spec
// presets: the checked named presets, then "custom" when the drone's sensor is Custom (spec.sensor = its dict).
export function normSpec(spec, available) {
  const s = spec || {};
  const ok = available && available.length ? new Set(available) : null;
  const planners = [...new Set((s.planners || []).filter(p => typeof p === "string" && (!ok || ok.has(p))))];
  const sensor_choice = normSensorChoice(s.sensor_choice);
  const custom = sensor_choice === CUSTOM;
  const named = SWEEP_PRESETS.filter(p => (s.presets || (custom ? [] : ["ideal"])).includes(p));
  const presets = custom ? [...named, CUSTOM] : named.length ? named : ["ideal"];
  const extra = EXTRA_FAULTS.includes(s.fault) ? s.fault : null;
  const seeds = Math.max(1, Math.min(MAX_SEEDS, parseInt(s.seeds, 10) || 5));
  // jitter: radius in m (one of JITTER_RADII), 0 = off; missing => default ON
  const jv = s.jitter == null || s.jitter === "" ? JITTER_DEFAULT : Number(s.jitter);
  const jitter = jv === 0 ? 0 : JITTER_RADII.includes(jv) ? jv : JITTER_DEFAULT;
  const faults = extra ? ["truth", extra] : ["truth"];
  // vars (loop-89, Stress): an explicit subset of presets x faults, kept in cross-product order; missing,
  // empty or nothing valid => null (every preset x fault)
  const asked = Array.isArray(s.vars) ? new Set(s.vars) : null;
  const vars = asked ? presets.flatMap(p => faults.map(f => `${p}|${f}`)).filter(k => asked.has(k)) : [];
  const out = { planners, presets, faults, fault: extra, seeds, jitter,
    time_limit: normTimeLimit(s.time_limit), vehicle: normVehicle(s.vehicle), sensor_choice,
    sensor: custom ? normSensor(s.sensor) : null, yaw: normYaw(s.yaw) };
  if (vars.length) out.vars = vars;
  return out;
}

// The run message's cfg extras: vehicle only when it differs from the arena default, sensor for the custom
// variation (it replaces cfg.preset), yaw only when not "fixed".
export function cfgExtras(spec, preset) {
  const out = {};
  if (spec.vehicle && !isDefaultVehicle(spec.vehicle)) out.vehicle = { ...normVehicle(spec.vehicle) };
  if (preset === CUSTOM) out.sensor = { ...normSensor(spec.sensor) };
  if (normYaw(spec.yaw) !== "fixed") out.yaw = normYaw(spec.yaw);
  return out;
}
// Vehicle radius for the jitter clearance: the larger of the world's and the sweep vehicle's.
export const sweepRadius = (doc, spec) => Math.max(vehicleRadius(doc), (spec && spec.vehicle && spec.vehicle.radius_m) || 0);

// ------------------------------------------------------------ run time limit
// "auto" (also missing or not a choice) or one of the fixed choices in s.
export function normTimeLimit(v) {
  if (v == null || v === "" || v === "auto") return "auto";
  const n = Number(v);
  return TIME_LIMITS.includes(n) ? n : "auto";
}
// The limit a run on doc gets: { s, source: "family" | "default" | "fixed", family }.
export function timeLimitFor(doc, choice) {
  const c = normTimeLimit(choice), fam = doc && typeof doc.family === "string" ? doc.family : null;
  if (c !== "auto") return { s: c, source: "fixed", family: fam };
  if (fam && Object.prototype.hasOwnProperty.call(LONG_FAMILIES, fam)) return { s: LONG_FAMILIES[fam], source: "family", family: fam };
  return { s: DEFAULT_MAX_TIME_S, source: "default", family: fam };
}
// cfg.max_time_s for the worker: absent under Auto (the worker applies the same family rule itself).
export const cfgTimeLimit = spec => (normTimeLimit(spec && spec.time_limit) === "auto" ? undefined : normTimeLimit(spec.time_limit));
// Distinct limits the worker reported in the records (result.max_time_s), ascending.
export const limitsUsed = records => [...new Set(records.map(r => r.max_time_s).filter(v => typeof v === "number"))].sort((a, b) => a - b);
// One line for the result header: the limit used, and why.
export function timeLimitText(spec, doc, records) {
  const t = timeLimitFor(doc, spec && spec.time_limit), used = limitsUsed(records || []);
  const s = used.length ? used.map(v => `${v} s`).join(" and ") : `${t.s} s`;
  const why = t.source === "fixed" ? "fixed in the sweep"
    : t.source === "family" ? `Auto: ${t.family} family, as the benchmark`
      : `Auto: ${t.family && t.family !== "custom" ? t.family + " family" : "no benchmark family"}, default`;
  return `Run time limit: ${s} of sim time (${why}).`;
}

// ------------------------------------------------------------ start/goal jitter
// With the ideal sensor and truth pose a deterministic planner flies the same run on every seed, so
// seeds alone sample nothing. Seed k > 0 moves A and B by a seeded pseudo-random offset (same for
// every planner, preset and fault, so planners stay comparable). Seed 0 is the exact map.

// mulberry32: small seeded PRNG, uniform in [0, 1). Deterministic across JS engines.
export function mulberry32(seed) {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// Distance from (x, y) to the nearest surface: obstacles (box, axis-aligned wall, cylinder) and the
// area bounds (the arena treats them as walls). Negative inside an obstacle or outside the bounds.
export function clearanceAt(doc, x, y) {
  const [x0, y0, x1, y1] = doc.bounds;
  let d = Math.min(x - x0, x1 - x, y - y0, y1 - y);
  for (const o of doc.obstacles || []) {
    let e;
    if (o.type === "cylinder") e = Math.hypot(x - o.cx, y - o.cy) - o.r;
    else {
      let cx, cy, hx, hy;
      if (o.type === "box") ({ cx, cy, hx, hy } = o);
      else {                                    // wall: axis-aligned segment with thickness
        const h = (o.thickness || 0.1) / 2;
        cx = (o.x0 + o.x1) / 2; cy = (o.y0 + o.y1) / 2;
        const horiz = Math.abs(o.y1 - o.y0) < 1e-9;
        hx = horiz ? Math.abs(o.x1 - o.x0) / 2 : h; hy = horiz ? h : Math.abs(o.y1 - o.y0) / 2;
      }
      const qx = Math.abs(x - cx) - hx, qy = Math.abs(y - cy) - hy;
      e = Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0);
    }
    if (e < d) d = e;
  }
  return d;
}

export const vehicleRadius = doc => (Number.isFinite(doc && doc.radius) && doc.radius > 0 ? doc.radius : VEHICLE_RADIUS_M);
const r4 = v => Math.round(v * 1e4) / 1e4;

// One point: up to `draws` uniform draws in the disc of radius R around p; the first that keeps
// minClear from every surface wins. None => the exact point, kept = true.
export function jitterPoint(doc, p, rng, R, minClear, draws = JITTER_DRAWS) {
  for (let i = 1; i <= draws; i++) {
    const r = R * Math.sqrt(rng()), th = 2 * Math.PI * rng();
    const q = [r4(p[0] + r * Math.cos(th)), r4(p[1] + r * Math.sin(th))];
    if (clearanceAt(doc, q[0], q[1]) >= minClear) return { p: q, kept: false, draws: i };
  }
  return { p: [p[0], p[1]], kept: true, draws };
}

// A and B for one seed. Depends only on (world, seed, R): every planner gets the same points.
// radius: vehicle radius for the clearance (default: the world's, else 0.15 m).
export function seedJitter(doc, seed, R, radius) {
  const a = [doc.a ? doc.a[0] : 0, doc.a ? doc.a[1] : 0], b = [doc.b[0], doc.b[1]];
  if (!seed || !R) return { seed, a, b, exact: true, a_kept: false, b_kept: false, draws: 0 };
  const rng = mulberry32((Math.imul(seed, 0x9E3779B1) ^ 0x5EED) >>> 0);
  const minClear = (radius > 0 ? radius : vehicleRadius(doc)) + JITTER_MARGIN_M;
  const ja = jitterPoint(doc, a, rng, R, minClear), jb = jitterPoint(doc, b, rng, R, minClear);
  return { seed, a: ja.p, b: jb.p, exact: false, a_kept: ja.kept, b_kept: jb.kept, draws: ja.draws + jb.draws };
}
export const seedJitters = (doc, spec) => Array.from({ length: spec.seeds }, (_, s) => seedJitter(doc, s, spec.jitter, sweepRadius(doc, spec)));

// A copy of the world with A and B replaced (the worker re-centres on A; result.offset maps back).
export function jitterWorld(doc, j) {
  const w = JSON.parse(JSON.stringify(doc));
  w.a = [j.a[0], j.a[1]]; w.b = [j.b[0], j.b[1]];
  return w;
}

// Every preset x fault, or spec.vars when the sweep chose a subset (Stress).
export const variations = spec => (spec.vars && spec.vars.length ? spec.vars.slice()
  : spec.presets.flatMap(p => spec.faults.map(f => variationKey(p, f))));
export const runCount = spec => spec.planners.length * variations(spec).length * spec.seeds;

// Seed outermost, planner innermost: every planner advances at the same pace through the FIFO queue.
export function buildRuns(spec) {
  const out = [], keys = variations(spec);
  for (let seed = 0; seed < spec.seeds; seed++)
    for (const key of keys) {
      const [preset, fault] = key.split("|");
      for (const planner of spec.planners)
        out.push({ planner, preset, fault, seed, filter: "none", key,
          beams: (sensorSpecOf(preset, spec) || {}).beams || null });
    }
  return out;
}

// ------------------------------------------------------------ one run => one record
// A worker result becomes a flat record. A worker error, a crash or a result without a score becomes
// outcome "error" with its message: errors are counted (as not reached), never dropped.
export function recordFromResult(run, result) {
  const sc = result && result.score;
  if (!sc || !OUTCOMES.includes(sc.outcome) || sc.outcome === "error") return recordFromError(run, "result has no valid score");
  const fs = result.sensor && typeof result.sensor === "object" ? result.sensor : null;
  return { planner: run.planner, preset: run.preset, fault: run.fault, seed: run.seed, ...abOf(run), ...droneOf(run),
    yaw_policy: fs && typeof fs.yaw_policy === "string" ? fs.yaw_policy : null, outcome: sc.outcome,
    time_to_goal_s: num(sc.time_to_goal_s), path_length_m: num(sc.path_length_m), min_clearance_m: num(sc.min_clearance_m),
    duration_s: num(sc.duration_s), max_time_s: num(result.max_time_s),
    wall_s: result.worker_ms != null ? result.worker_ms / 1000 : num(result.wall_s), error: null };
}
export function recordFromError(run, message) {
  return { planner: run.planner, preset: run.preset, fault: run.fault, seed: run.seed, ...abOf(run), ...droneOf(run), yaw_policy: null,
    outcome: "error", time_to_goal_s: null, path_length_m: null, min_clearance_m: null, duration_s: null, max_time_s: null, wall_s: null,
    error: String(message || "error") };
}
// Vehicle (always, arena default when the sweep did not change it), sensor spec (custom dict; a named
// preset's table entry) and the yaw request. yaw_policy is what the worker reported it flew.
const droneOf = run => ({ vehicle: run.vehicle ? normVehicle(run.vehicle) : { ...VEHICLE_DEFAULT },
  sensor: run.preset === CUSTOM ? (run.sensor ? normSensor(run.sensor) : null) : PRESET_SPECS[run.preset] ? { ...PRESET_SPECS[run.preset] } : null,
  yaw: normYaw(run.yaw) });
// A and B the run actually flew (jittered for seed > 0) and whether a jitter fell back to the exact point.
const abOf = run => ({ a: run.a || null, b: run.b || null, ab_kept: run.ab_kept || null });
const num = v => (typeof v === "number" && Number.isFinite(v) ? v : null);

// ------------------------------------------------------------ statistics
// Wilson score interval for k successes in n trials (z = 1.96 => 95 %). n = 0 => p null, [0, 1].
export function wilson(k, n, z = 1.96) {
  if (!n) return { p: null, lo: 0, hi: 1 };
  const p = k / n, z2 = z * z, den = 1 + z2 / n;
  const c = (p + z2 / (2 * n)) / den, h = (z * Math.sqrt(p * (1 - p) / n + z2 / (4 * n * n))) / den;
  return { p, lo: Math.max(0, c - h), hi: Math.min(1, c + h) };
}

export function median(xs) {
  const v = xs.filter(x => typeof x === "number" && Number.isFinite(x)).sort((a, b) => a - b);
  if (!v.length) return null;
  const m = v.length >> 1;
  return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2;
}
const mean = xs => { const v = xs.filter(x => typeof x === "number" && Number.isFinite(x)); return v.length ? v.reduce((a, b) => a + b, 0) / v.length : null; };

// Two runs are the same run when variation, outcome, time to B and path length (3 dp) all match.
// The variation is part of the key, so a pooled group never merges runs of different variations.
const r3 = v => (v == null ? "-" : (Math.round(v * 1000) / 1000).toFixed(3));
export const runSignature = r => [r.preset, r.fault, r.outcome, r3(r.time_to_goal_s), r3(r.path_length_m)].join("|");

// Stats of one group of records. n counts every record, errors included. n_distinct counts distinct
// runs (runSignature); identical runs are one trial, so the Wilson interval uses the distinct runs:
// success = wilson(distinct runs that reached B, n_distinct). Error records each count as distinct.
// `identical` = runs that have at least one
// identical twin in the group (0 when every run is distinct).
export function stats(recs) {
  const c = Object.fromEntries(OUTCOMES.map(o => [o, 0]));
  for (const r of recs) c[OUTCOMES.includes(r.outcome) ? r.outcome : "error"]++;
  const n = recs.length, flown = recs.filter(r => r.outcome !== "error");
  const clr = flown.map(r => r.min_clearance_m).filter(v => v != null);
  const groups = new Map();
  // errors are never collapsed: each one is its own failed trial (collapsing would flatter a crashing planner)
  recs.forEach((r, i) => { const k = r.outcome === "error" ? `error#${i}` : runSignature(r); groups.set(k, (groups.get(k) || 0) + 1); });
  const n_distinct = groups.size;
  const reached_distinct = [...groups.keys()].filter(k => k.split("|")[2] === "reached").length;
  const identical = [...groups.values()].filter(v => v > 1).reduce((a, b) => a + b, 0);
  return { n, n_distinct, identical, ...c, reached_distinct, success: wilson(reached_distinct, n_distinct),
    median_time_s: median(recs.filter(r => r.outcome === "reached").map(r => r.time_to_goal_s)),
    median_path_m: median(flown.map(r => r.path_length_m)),
    min_clearance_m: clr.length ? Math.min(...clr) : null,
    collision_rate: n ? c.collision / n : null,
    mean_wall_s: mean(flown.map(r => r.wall_s)) };
}

// Matrix (planner x variation) plus the pooled row per planner, the ranking and the headline.
export function aggregate(records, spec) {
  const planners = spec ? spec.planners : [...new Set(records.map(r => r.planner))];
  const keys = spec ? variations(spec) : [...new Set(records.map(r => variationKey(r.preset, r.fault)))];
  const cells = {}, pooled = {};
  for (const p of planners) {
    const mine = records.filter(r => r.planner === p);
    cells[p] = {};
    for (const k of keys) cells[p][k] = stats(mine.filter(r => variationKey(r.preset, r.fault) === k));
    pooled[p] = stats(mine);
  }
  const ranking = rank(pooled);
  return { planners, variations: keys, cells, pooled, ranking, headline: headline(ranking), n_records: records.length };
}

// Success rate (descending), then median time to B (ascending, none = last), then planner id.
export function rank(pooled) {
  return Object.entries(pooled).filter(([, s]) => s.n > 0).map(([planner, s]) => ({ planner, ...s }))
    .sort((a, b) => (b.success.p - a.success.p) ||
      ((a.median_time_s == null) - (b.median_time_s == null)) || ((a.median_time_s || 0) - (b.median_time_s || 0)) ||
      (a.planner < b.planner ? -1 : a.planner > b.planner ? 1 : 0));
}

export const overlaps = (a, b) => a.lo <= b.hi && b.lo <= a.hi;
const pct = v => `${Math.round(v * 100)} %`;

// ------------------------------------------------------------ what n seeds can separate
// Do kA/n and kB/n (n distinct runs each) have disjoint 95 % Wilson intervals?
export const separates = (kA, kB, n) => !overlaps(wilson(kA, n), wilson(kB, n));
// Smallest n (up to maxN) at which success rates pA and pB, flown n distinct runs each (k = round(p x n)),
// have disjoint 95 % Wilson intervals; null when none does (pA = pB never separates).
export function seedsToSeparate(pA, pB, maxN = 1000) {
  if (Math.round(pA * 1e9) === Math.round(pB * 1e9)) return null;
  for (let n = 1; n <= maxN; n++) if (separates(Math.round(pA * n), Math.round(pB * n), n)) return n;
  return null;
}
const ci = w => `${pct(w.lo)}-${pct(w.hi)}`;
// "Quick" / "Thorough" when the seed count is that button's, else null (the count names itself).
export const seedsName = n => (n === QUICK_SEEDS ? "Quick" : n === THOROUGH_SEEDS ? "Thorough" : null);
// One line for the sweep summary: what `seeds` seeds per planner can and cannot tell apart, e.g.
// "Quick separates 5/5 from 0/5; telling 5/5 from 4/5 needs about N seeds." (N from seedsToSeparate).
export function separationNote(seeds, name) {
  const n = Math.max(1, seeds | 0), who = name || `${n} seed${n > 1 ? "s" : ""}`, verb = name || n === 1 ? "separates" : "separate";
  const top = wilson(n, n), zero = wilson(0, n);
  if (n === 1 || !separates(n, 0, n))
    return `${who} cannot separate ${n}/${n} from 0/${n}; that needs ${seedsToSeparate(1, 0)} seeds ` +
      `(95 % Wilson: ${n}/${n} ${ci(top)}, 0/${n} ${ci(zero)}).`;
  const need = seedsToSeparate(1, (n - 1) / n);
  return `${who} ${verb} ${n}/${n} from 0/${n}; telling ${n}/${n} from ${n - 1}/${n} needs ` +
    `${need == null ? "more than 1000" : "about " + need} seeds (95 % Wilson: ${n}/${n} ${ci(top)}, 0/${n} ${ci(zero)}).`;
}
// "n=3" when every run is distinct, "n=3, 1 distinct" when identical runs were collapsed.
export const nOne = s => (s.n_distinct != null && s.n_distinct < s.n ? `n=${s.n}, ${s.n_distinct} distinct` : `n=${s.n}`);
const nText = (a, b) => (b && nOne(a) !== nOne(b) ? `${nOne(a)} and ${nOne(b)}` : nOne(a));
const anyDup = (...xs) => xs.some(s => s && s.n_distinct < s.n);
const dupNote = (...xs) => (anyDup(...xs) ? " Identical runs count once in the interval." : "");
// "3/3 reached B" or, with duplicates, "3/3 reached B (1/1 distinct)"
const reachText = s => `${s.reached}/${s.n} reached B` + (s.n_distinct < s.n ? ` (${s.reached_distinct}/${s.n_distinct} distinct)` : "");

// The headline names a winner only when its 95 % Wilson interval does not overlap the runner-up's.
// Intervals are on the distinct runs (stats), and the n shown says how many were distinct.
export function headline(ranking) {
  if (!ranking.length) return { kind: "empty", text: "No runs yet." };
  const [a, b] = ranking;
  if (a.reached === 0) return { kind: "none", planner: null, text: `No planner reached B on this map (${nText(a)} per planner).` };
  if (!b) return { kind: "single", planner: a.planner,
    text: `Only ${plannerLabel(a.planner)} was run: ${reachText(a)} (95 % CI ${pct(a.success.lo)}-${pct(a.success.hi)}, ${nOne(a)}).${dupNote(a)}` };
  const top = ranking.filter(r => overlaps(r.success, a.success));
  if (top.length > BIG_TIE) return { kind: "tie", planner: null, planners: top.map(r => r.planner), top_n: top.length,
    text: `${top.length} planners tie at the top; run Thorough or more seeds to separate them (${nText(a)} per planner, best ${reachText(a)}, 95 % CI ${pct(a.success.lo)}-${pct(a.success.hi)}).${dupNote(...top)}` };
  if (overlaps(a.success, b.success)) return { kind: "tie", planner: null, planners: [a.planner, b.planner], top_n: top.length,
    text: `No clear winner: ${plannerLabel(a.planner)} and ${plannerLabel(b.planner)} are within noise on this map (${nText(a, b)}).${dupNote(a, b)}` };
  return { kind: "winner", planner: a.planner,
    text: `${plannerLabel(a.planner)} wins on this map: ${reachText(a)} (95 % CI ${pct(a.success.lo)}-${pct(a.success.hi)}, ${nOne(a)})` +
      (a.median_time_s != null ? `, median ${a.median_time_s.toFixed(1)} s to B` : "") +
      `; runner-up ${plannerLabel(b.planner)} ${b.reached}/${b.n} (${pct(b.success.lo)}-${pct(b.success.hi)}, ${nOne(b)}).${dupNote(a, b)}` };
}

// ------------------------------------------------------------ Pareto view (loop-89)
// When success ties, which planners are fast AND safe? ranking: rank() rows (pooled, or one variation's cells).
// Group = the best success group: every planner whose 95 % Wilson interval overlaps the top one's (the tied set
// of the headline and Recommend; just the top planner when it is a clear winner). Empty when nobody reached B.
// Eligible = in the group with a median time to B and a min clearance (a planner without a time never reached B
// in this group, so it cannot be "fast"; it is listed as excluded, never on the front).
// A dominates B when A is no slower (median time to B, compared at 0.01 s) and no closer (min clearance, at
// 0.001 m) and better in at least one. Equal points do not dominate each other: both stay on the front.
// Returns { group, front, excluded, points } with planner ids in ranking order; points has one entry per
// ranking row: { planner, t, c, p, in_group, eligible, pareto, dominated_by }.
export const PARETO_T_DP = 2, PARETO_C_DP = 3;
const rnd = (v, dp) => Math.round(v * 10 ** dp) / 10 ** dp;
export function dominates(a, b) {
  const ta = rnd(a.t, PARETO_T_DP), tb = rnd(b.t, PARETO_T_DP), ca = rnd(a.c, PARETO_C_DP), cb = rnd(b.c, PARETO_C_DP);
  return ta <= tb && ca >= cb && (ta < tb || ca > cb);
}
export function paretoFront(ranking) {
  const rk = ranking || [], top = rk[0];
  const ok = !!(top && top.reached > 0 && top.success);
  const points = rk.map(r => {
    const in_group = ok && overlaps(r.success, top.success);
    const t = typeof r.median_time_s === "number" ? r.median_time_s : null, c = typeof r.min_clearance_m === "number" ? r.min_clearance_m : null;
    return { planner: r.planner, t, c, p: r.success ? r.success.p : null, in_group, eligible: in_group && t != null && c != null, pareto: false, dominated_by: null };
  });
  const el = points.filter(q => q.eligible);
  for (const q of el) {
    const d = el.find(o => o !== q && dominates(o, q));
    q.dominated_by = d ? d.planner : null;
    q.pareto = !d;
  }
  return { group: points.filter(q => q.in_group).map(q => q.planner), front: points.filter(q => q.pareto).map(q => q.planner),
    excluded: points.filter(q => q.in_group && !q.eligible).map(q => q.planner), points };
}
// Rows for one variation key (cells of aggregate()), or the pooled ranking when key is empty.
export function paretoRows(agg, key) {
  if (!key) return agg.ranking;
  return rank(Object.fromEntries(agg.planners.map(p => [p, agg.cells[p] && agg.cells[p][key]]).filter(([, c]) => c)));
}

// ------------------------------------------------------------ export
export const CSV_COLS = ["planner", "planner_label", "preset", "fault", "seed", "a_x", "a_y", "b_x", "b_y", "outcome", "time_to_goal_s",
  "path_length_m", "min_clearance_m", "duration_s", "max_time_s", "wall_s",
  "sensor_label", "sensor_beams", "sensor_fov_deg", "sensor_max_range_m", "sensor_min_range_m", "sensor_noise_sigma_m",
  "vehicle_radius_m", "vehicle_v_max", "vehicle_a_max", "vehicle_tau", "yaw", "yaw_policy", "error"];
const csvCell = v => { if (v == null) return ""; const s = String(v); return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
const csvVal = (r, c) => {
  if (c === "planner_label") return plannerLabel(r.planner);
  if (c === "sensor_label") return r.preset === CUSTOM ? customLabel(r.sensor) : r.preset;
  if (c.startsWith("sensor_")) return r.sensor ? r.sensor[c.slice(7)] : null;
  if (c.startsWith("vehicle_")) return r.vehicle ? r.vehicle[c.slice(8)] : null;
  const m = /^([ab])_([xy])$/.exec(c);
  return m ? (r[m[1]] ? r[m[1]][m[2] === "x" ? 0 : 1] : null) : r[c];
};
export function toCSV(records) {
  return [CSV_COLS.join(","), ...records.map(r => CSV_COLS.map(c => csvCell(csvVal(r, c))).join(","))].join("\n") + "\n";
}

// jitters: seedJitters(world, spec), the A/B every seed flew. world is the exact map (seed 0).
export function exportDoc({ spec, world, worldName, records, env, pool, started, finished, cancelled, jitters }) {
  const agg = aggregate(records, spec);
  return { schema: SCHEMA, input: "synthetic",
    note: "SYNTHETIC SIMULATION, 2.5D POINT MASS. Scored on truth. Not a flight result. n seeds on one map is a small sample. " +
      "Identical runs (same variation, outcome, time to B and path length at 3 dp) count once in every interval.",
    world_name: worldName || null, spec, run_count: runCount(spec), records_n: records.length, cancelled: !!cancelled,
    started: started || null, finished: finished || null, pool: pool || null, env: env || null,
    drone: droneDoc(spec, records),
    jitter: { radius_m: spec.jitter || 0, min_clearance_m: sweepRadius(world, spec) + JITTER_MARGIN_M, max_draws: JITTER_DRAWS,
      prng: "mulberry32", seed0: "exact map", per_seed: jitters || null },
    time_limit: { choice: normTimeLimit(spec.time_limit), expected_s: timeLimitFor(world, spec.time_limit).s,
      source: timeLimitFor(world, spec.time_limit).source, used_s: limitsUsed(records), long_families: LONG_FAMILIES,
      default_s: DEFAULT_MAX_TIME_S, rule: "auto: world.family in long_families => that limit, else default_s (bench.py LONG_FAMILIES)" },
    headline: agg.headline, ranking: agg.ranking, matrix: agg.cells, records, world };
}

// "Your drone" block of the JSON export: what was asked, and the yaw policies the worker reported.
export function droneDoc(spec, records) {
  const v = normVehicle(spec.vehicle);
  return { vehicle: v, vehicle_default: { ...VEHICLE_DEFAULT }, vehicle_sent: !isDefaultVehicle(v),
    sensor_choice: normSensorChoice(spec.sensor_choice), sensor: spec.sensor ? normSensor(spec.sensor) : null,
    custom_label: spec.sensor ? customLabel(normSensor(spec.sensor)) : null,
    custom_defaults: { cone_deg: 0, dropout: 0.02, source: "presets.py SENSOR_SPEC_DEFAULTS, filled by the worker" },
    yaw: normYaw(spec.yaw), yaw_sent: normYaw(spec.yaw) !== "fixed",
    yaw_policy_flown: [...new Set((records || []).map(r => r.yaw_policy).filter(Boolean))].sort(),
    sensor_specs: Object.fromEntries(spec.presets.map(p => [p, sensorSpecOf(p, spec)])) };
}

// ------------------------------------------------------------ share link (world + sweep spec, no results)
export function specToQuery(spec, src) {
  const q = new URLSearchParams();
  q.set("planners", spec.planners.join(","));
  q.set("presets", spec.presets.filter(p => p !== CUSTOM).join(","));
  if (spec.fault) q.set("fault", spec.fault);
  q.set("seeds", String(spec.seeds));
  if (spec.jitter != null) q.set("jitter", String(spec.jitter));
  q.set("tlim", String(normTimeLimit(spec.time_limit)));
  // your drone: veh = radius_m,v_max,a_max,tau; sensor = preset name or custom; cs = custom sensor
  // beams,fov_deg,max_range_m,min_range_m,noise_sigma_m; yaw only when not fixed
  const v = normVehicle(spec.vehicle);
  q.set("veh", VEHICLE_KEYS.map(k => g(v[k])).join(","));
  const choice = normSensorChoice(spec.sensor_choice);
  q.set("sensor", choice);
  if (choice === CUSTOM) { const s = normSensor(spec.sensor); q.set("cs", SENSOR_KEYS.map(k => g(s[k])).join(",")); }
  if (normYaw(spec.yaw) !== "fixed") q.set("yaw", normYaw(spec.yaw));
  if (spec.vars && spec.vars.length) q.set("vars", spec.vars.join(","));
  if (src) q.set("src", src);
  return q.toString();
}
const zipKeys = (keys, text) => { const v = String(text || "").split(","); return Object.fromEntries(keys.map((k, i) => [k, v[i] === undefined ? undefined : v[i].trim()])); };
export function specFromQuery(search) {
  const q = new URLSearchParams(search || "");
  const list = k => (q.get(k) || "").split(",").map(s => s.trim()).filter(Boolean);
  const out = {};
  if (q.has("planners")) out.planners = list("planners");
  if (q.has("presets")) out.presets = list("presets");
  if (q.has("fault")) out.fault = q.get("fault");
  if (q.has("seeds")) out.seeds = q.get("seeds");
  if (q.has("jitter")) out.jitter = q.get("jitter");
  if (q.has("tlim")) out.time_limit = q.get("tlim");
  if (q.has("veh")) out.vehicle = zipKeys(VEHICLE_KEYS, q.get("veh"));
  if (q.has("sensor")) out.sensor_choice = q.get("sensor");
  if (q.has("cs")) out.sensor = zipKeys(SENSOR_KEYS, q.get("cs"));
  if (q.has("yaw")) out.yaw = q.get("yaw");
  if (q.has("vars")) out.vars = list("vars");
  const src = q.get("src");
  return { spec: out, src: src && /^[a-z0-9_]+$/.test(src) ? src : null };
}

// Same coding as site/playground/playground.js encodeWorld / decodeWorld: deflate (zlib) + base64url, no padding.
export function b64url(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}
export function unb64url(text) {
  const t = text.replace(/-/g, "+").replace(/_/g, "/"), bin = atob(t + "===".slice((t.length + 3) % 4));
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out;
}
async function pipeBytes(bytes, stream) {
  return new Uint8Array(await new Response(new Blob([bytes]).stream().pipeThrough(stream)).arrayBuffer());
}
export async function encodeWorld(doc) {
  return b64url(await pipeBytes(new TextEncoder().encode(JSON.stringify(doc)), new CompressionStream("deflate")));
}
export async function decodeWorld(text) {
  let bytes;
  try { bytes = await pipeBytes(unb64url(text), new DecompressionStream("deflate")); }
  catch (err) { throw new Error("w= is not deflate + base64url data"); }
  return JSON.parse(new TextDecoder().decode(bytes));
}
// w= value from a pasted playground or solver URL, or from a bare "#w=..." / "w=..." text.
export function worldParamFrom(text) {
  const t = String(text || "").trim();
  const i = t.indexOf("#");
  const hash = i >= 0 ? t.slice(i + 1) : t;
  return new URLSearchParams(hash).get("w") || null;
}

// ------------------------------------------------------------ time estimate
// Seconds left for the runs not done yet on K workers: per-planner mean wall time measured in this
// browser when available, else the prior scaled by the run's beam count (beamFactor; no beams => x 1).
// Returns { s, measured } (measured = no prior was used).
export function estimateSeconds(pending, measuredWall, K, prior = PRIOR_WALL_S) {
  let total = 0, measured = true;
  for (const r of pending) {
    const m = measuredWall && measuredWall[r.planner];
    if (m != null) total += m;
    else { total += (prior[r.planner] != null ? prior[r.planner] : PRIOR_DEFAULT_S) * beamFactor(r.beams); measured = false; }
  }
  return { s: total / Math.max(1, K), measured };
}
export function fmtDuration(s) {
  if (s == null || !Number.isFinite(s)) return "-";
  if (s < 60) return `${Math.max(1, Math.round(s))} s`;
  const m = Math.floor(s / 60), r = Math.round(s - 60 * m);
  return r ? `${m} min ${r} s` : `${m} min`;
}
export const poolSize = hwc => Math.max(1, Math.min(4, (Number.isFinite(hwc) && hwc > 0 ? hwc : 2) - 1));
