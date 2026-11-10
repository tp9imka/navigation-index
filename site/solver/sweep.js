// Solver sweep logic (pure, no DOM, no workers): run list, aggregation, Wilson interval, ranking,
// headline, CSV / JSON export, share-link spec codec and the time estimate.
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
  return { planners, presets: presets.length ? presets : ["ideal"], faults: extra ? ["truth", extra] : ["truth"], fault: extra, seeds };
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
  return { planner: run.planner, preset: run.preset, fault: run.fault, seed: run.seed, outcome: sc.outcome,
    time_to_goal_s: num(sc.time_to_goal_s), path_length_m: num(sc.path_length_m), min_clearance_m: num(sc.min_clearance_m),
    duration_s: num(sc.duration_s), wall_s: result.worker_ms != null ? result.worker_ms / 1000 : num(result.wall_s), error: null };
}
export function recordFromError(run, message) {
  return { planner: run.planner, preset: run.preset, fault: run.fault, seed: run.seed, outcome: "error",
    time_to_goal_s: null, path_length_m: null, min_clearance_m: null, duration_s: null, wall_s: null, error: String(message || "error") };
}
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

// Stats of one group of records. n counts every record, errors included.
export function stats(recs) {
  const c = Object.fromEntries(OUTCOMES.map(o => [o, 0]));
  for (const r of recs) c[OUTCOMES.includes(r.outcome) ? r.outcome : "error"]++;
  const n = recs.length, flown = recs.filter(r => r.outcome !== "error");
  const clr = flown.map(r => r.min_clearance_m).filter(v => v != null);
  return { n, ...c, success: wilson(c.reached, n),
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
const nText = (a, b) => (b && a.n !== b.n ? `n=${a.n} and ${b.n}` : `n=${a.n}`);

// The headline names a winner only when its 95 % Wilson interval does not overlap the runner-up's.
export function headline(ranking) {
  if (!ranking.length) return { kind: "empty", text: "No runs yet." };
  const [a, b] = ranking;
  if (a.reached === 0) return { kind: "none", planner: null, text: `No planner reached B on this map (${nText(a)} per planner).` };
  if (!b) return { kind: "single", planner: a.planner,
    text: `Only ${plannerLabel(a.planner)} was run: ${a.reached}/${a.n} reached B (95 % CI ${pct(a.success.lo)}-${pct(a.success.hi)}).` };
  if (overlaps(a.success, b.success)) return { kind: "tie", planner: null, planners: [a.planner, b.planner],
    text: `No clear winner: ${plannerLabel(a.planner)} and ${plannerLabel(b.planner)} are within noise on this map (${nText(a, b)}).` };
  return { kind: "winner", planner: a.planner,
    text: `${plannerLabel(a.planner)} wins on this map: ${a.reached}/${a.n} reached B (95 % CI ${pct(a.success.lo)}-${pct(a.success.hi)})` +
      (a.median_time_s != null ? `, median ${a.median_time_s.toFixed(1)} s to B` : "") +
      `; runner-up ${plannerLabel(b.planner)} ${b.reached}/${b.n} (${pct(b.success.lo)}-${pct(b.success.hi)}).` };
}

// ------------------------------------------------------------ export
export const CSV_COLS = ["planner", "planner_label", "preset", "fault", "seed", "outcome", "time_to_goal_s", "path_length_m",
  "min_clearance_m", "duration_s", "wall_s", "error"];
const csvCell = v => { if (v == null) return ""; const s = String(v); return /[",\n\r]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s; };
export function toCSV(records) {
  return [CSV_COLS.join(","), ...records.map(r => CSV_COLS.map(c => csvCell(c === "planner_label" ? plannerLabel(r.planner) : r[c])).join(","))].join("\n") + "\n";
}

export function exportDoc({ spec, world, worldName, records, env, pool, started, finished, cancelled }) {
  const agg = aggregate(records, spec);
  return { schema: SCHEMA, input: "synthetic",
    note: "SYNTHETIC SIMULATION, 2.5D POINT MASS. Scored on truth. Not a flight result. n seeds on one map is a small sample.",
    world_name: worldName || null, spec, run_count: runCount(spec), records_n: records.length, cancelled: !!cancelled,
    started: started || null, finished: finished || null, pool: pool || null, env: env || null,
    headline: agg.headline, ranking: agg.ranking, matrix: agg.cells, records, world };
}

// ------------------------------------------------------------ share link (world + sweep spec, no results)
export function specToQuery(spec, src) {
  const q = new URLSearchParams();
  q.set("planners", spec.planners.join(","));
  q.set("presets", spec.presets.join(","));
  if (spec.fault) q.set("fault", spec.fault);
  q.set("seeds", String(spec.seeds));
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
