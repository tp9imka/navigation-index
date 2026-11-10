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
};
export const PRESET_LABELS = { ideal: "ideal: 72 rays, 360 deg, 6 m", crazyflie: "Crazyflie: 4 cone beams, 3 m" };
export const FAULT_LABELS = { truth: "off: planner sees truth", none: "VIO EKF, no fault", jump: "VIO jump 0.5 m",
  bias: "VIO bias 0.05 m/s, 10 s", dropout: "VIO dropout 2 s" };
export const SWEEP_PRESETS = ["ideal", "crazyflie"];
export const EXTRA_FAULTS = ["none", "jump", "bias", "dropout"];
export const OUTCOMES = ["reached", "collision", "stuck", "timeout", "error"];
export const MAX_SEEDS = 50;
export const JITTER_RADII = [0.25, 0.5, 1.0];     // m, start/goal jitter radius choices
export const JITTER_DEFAULT = 0.5;
export const JITTER_MARGIN_M = 0.1;              // jittered A/B keep vehicle radius + this from any surface
export const JITTER_DRAWS = 50;                  // draws per point before the exact point is kept
export const VEHICLE_RADIUS_M = 0.15;            // close-area arena default (world.py RADIUS)

export const plannerLabel = p => PLANNER_LABELS[p] || p;
export const variationKey = (preset, fault) => `${preset}|${fault}`;
export const variationLabel = key => { const [p, f] = key.split("|"); return `${p} / ${f === "truth" ? "truth pose" : "VIO " + f}`; };

// Browser Python seconds per run from site/playground/README.md (synthetic, one preset each) and the
// spike table there; only a prior for the estimate before this browser has measured its own runs.
export const PRIOR_WALL_S = { straight: 0.1, freest_beam: 0.2, astar_known: 0.7, astar_unknown: 3.0, apf: 0.3, vfh_plus: 0.3,
  dwa: 1.0, dwa_mem: 2.4, bug2: 0.2, tangent_bug: 0.25, dstar_lite: 1.3, informed_rrt_star: 0.8 };
export const PRIOR_DEFAULT_S = 1.0;

// ------------------------------------------------------------ spec
export function normSpec(spec, available) {
  const s = spec || {};
  const ok = available && available.length ? new Set(available) : null;
  const planners = [...new Set((s.planners || []).filter(p => typeof p === "string" && (!ok || ok.has(p))))];
  const presets = SWEEP_PRESETS.filter(p => (s.presets || ["ideal"]).includes(p));
  const extra = EXTRA_FAULTS.includes(s.fault) ? s.fault : null;
  const seeds = Math.max(1, Math.min(MAX_SEEDS, parseInt(s.seeds, 10) || 5));
  // jitter: radius in m (one of JITTER_RADII), 0 = off; missing => default ON
  const jv = s.jitter == null || s.jitter === "" ? JITTER_DEFAULT : Number(s.jitter);
  const jitter = jv === 0 ? 0 : JITTER_RADII.includes(jv) ? jv : JITTER_DEFAULT;
  return { planners, presets: presets.length ? presets : ["ideal"], faults: extra ? ["truth", extra] : ["truth"], fault: extra, seeds, jitter };
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
export function seedJitter(doc, seed, R) {
  const a = [doc.a ? doc.a[0] : 0, doc.a ? doc.a[1] : 0], b = [doc.b[0], doc.b[1]];
  if (!seed || !R) return { seed, a, b, exact: true, a_kept: false, b_kept: false, draws: 0 };
  const rng = mulberry32((Math.imul(seed, 0x9E3779B1) ^ 0x5EED) >>> 0);
  const minClear = vehicleRadius(doc) + JITTER_MARGIN_M;
  const ja = jitterPoint(doc, a, rng, R, minClear), jb = jitterPoint(doc, b, rng, R, minClear);
  return { seed, a: ja.p, b: jb.p, exact: false, a_kept: ja.kept, b_kept: jb.kept, draws: ja.draws + jb.draws };
}
export const seedJitters = (doc, spec) => Array.from({ length: spec.seeds }, (_, s) => seedJitter(doc, s, spec.jitter));

// A copy of the world with A and B replaced (the worker re-centres on A; result.offset maps back).
export function jitterWorld(doc, j) {
  const w = JSON.parse(JSON.stringify(doc));
  w.a = [j.a[0], j.a[1]]; w.b = [j.b[0], j.b[1]];
  return w;
}

export const variations = spec => spec.presets.flatMap(p => spec.faults.map(f => variationKey(p, f)));
export const runCount = spec => spec.planners.length * spec.presets.length * spec.faults.length * spec.seeds;

// Seed outermost, planner innermost: every planner advances at the same pace through the FIFO queue.
export function buildRuns(spec) {
  const out = [];
  for (let seed = 0; seed < spec.seeds; seed++)
    for (const preset of spec.presets)
      for (const fault of spec.faults)
        for (const planner of spec.planners)
          out.push({ planner, preset, fault, seed, filter: "none", key: variationKey(preset, fault) });
  return out;
}

// ------------------------------------------------------------ one run => one record
// A worker result becomes a flat record. A worker error, a crash or a result without a score becomes
// outcome "error" with its message: errors are counted (as not reached), never dropped.
export function recordFromResult(run, result) {
  const sc = result && result.score;
  if (!sc || !OUTCOMES.includes(sc.outcome) || sc.outcome === "error") return recordFromError(run, "result has no valid score");
  return { planner: run.planner, preset: run.preset, fault: run.fault, seed: run.seed, ...abOf(run), outcome: sc.outcome,
    time_to_goal_s: num(sc.time_to_goal_s), path_length_m: num(sc.path_length_m), min_clearance_m: num(sc.min_clearance_m),
    duration_s: num(sc.duration_s), wall_s: result.worker_ms != null ? result.worker_ms / 1000 : num(result.wall_s), error: null };
}
export function recordFromError(run, message) {
  return { planner: run.planner, preset: run.preset, fault: run.fault, seed: run.seed, ...abOf(run), outcome: "error",
    time_to_goal_s: null, path_length_m: null, min_clearance_m: null, duration_s: null, wall_s: null, error: String(message || "error") };
}
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
  if (overlaps(a.success, b.success)) return { kind: "tie", planner: null, planners: [a.planner, b.planner],
    text: `No clear winner: ${plannerLabel(a.planner)} and ${plannerLabel(b.planner)} are within noise on this map (${nText(a, b)}).${dupNote(a, b)}` };
  return { kind: "winner", planner: a.planner,
    text: `${plannerLabel(a.planner)} wins on this map: ${reachText(a)} (95 % CI ${pct(a.success.lo)}-${pct(a.success.hi)}, ${nOne(a)})` +
      (a.median_time_s != null ? `, median ${a.median_time_s.toFixed(1)} s to B` : "") +
      `; runner-up ${plannerLabel(b.planner)} ${b.reached}/${b.n} (${pct(b.success.lo)}-${pct(b.success.hi)}, ${nOne(b)}).${dupNote(a, b)}` };
}

// ------------------------------------------------------------ export
export const CSV_COLS = ["planner", "planner_label", "preset", "fault", "seed", "a_x", "a_y", "b_x", "b_y", "outcome", "time_to_goal_s",
  "path_length_m", "min_clearance_m", "duration_s", "wall_s", "error"];
const csvCell = v => { if (v == null) return ""; const s = String(v); return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
const csvVal = (r, c) => {
  if (c === "planner_label") return plannerLabel(r.planner);
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
    jitter: { radius_m: spec.jitter || 0, min_clearance_m: vehicleRadius(world) + JITTER_MARGIN_M, max_draws: JITTER_DRAWS,
      prng: "mulberry32", seed0: "exact map", per_seed: jitters || null },
    headline: agg.headline, ranking: agg.ranking, matrix: agg.cells, records, world };
}

// ------------------------------------------------------------ share link (world + sweep spec, no results)
export function specToQuery(spec, src) {
  const q = new URLSearchParams();
  q.set("planners", spec.planners.join(","));
  q.set("presets", spec.presets.join(","));
  if (spec.fault) q.set("fault", spec.fault);
  q.set("seeds", String(spec.seeds));
  if (spec.jitter != null) q.set("jitter", String(spec.jitter));
  if (src) q.set("src", src);
  return q.toString();
}
export function specFromQuery(search) {
  const q = new URLSearchParams(search || "");
  const list = k => (q.get(k) || "").split(",").map(s => s.trim()).filter(Boolean);
  const out = {};
  if (q.has("planners")) out.planners = list("planners");
  if (q.has("presets")) out.presets = list("presets");
  if (q.has("fault")) out.fault = q.get("fault");
  if (q.has("seeds")) out.seeds = q.get("seeds");
  if (q.has("jitter")) out.jitter = q.get("jitter");
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
// browser when available, else the prior. Returns { s, measured } (measured = no prior was used).
export function estimateSeconds(pending, measuredWall, K, prior = PRIOR_WALL_S) {
  let total = 0, measured = true;
  for (const r of pending) {
    const m = measuredWall && measuredWall[r.planner];
    if (m != null) total += m;
    else { total += prior[r.planner] != null ? prior[r.planner] : PRIOR_DEFAULT_S; measured = false; }
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
