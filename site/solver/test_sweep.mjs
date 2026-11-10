// node --test site/solver/test_sweep.mjs  (plain node, no npm packages)
import { test } from "node:test";
import assert from "node:assert/strict";
import * as S from "./sweep.js";

const near = (a, b, tol = 5e-4) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);
const rec = (planner, outcome, extra = {}) => ({ planner, preset: "ideal", fault: "truth", seed: 0, outcome,
  time_to_goal_s: outcome === "reached" ? 20 : null, path_length_m: 24, min_clearance_m: 0.4, duration_s: 20, wall_s: 0.5, error: null, ...extra });
const many = (planner, k, n, t = 20) => Array.from({ length: n }, (_, i) =>
  rec(planner, i < k ? "reached" : "collision", { seed: i, time_to_goal_s: i < k ? t + i * 0.1 : null }));

test("Wilson interval matches published values", () => {
  // 8/10: 0.4902-0.9433 (Wilson 1927 formula, z = 1.96)
  const a = S.wilson(8, 10);
  near(a.p, 0.8); near(a.lo, 0.4902); near(a.hi, 0.9433);
  const b = S.wilson(0, 5);
  near(b.lo, 0); near(b.hi, 0.4345);
  const c = S.wilson(5, 5);
  near(c.lo, 0.5655); near(c.hi, 1);
  assert.deepEqual(S.wilson(0, 0), { p: null, lo: 0, hi: 1 });
});

test("ranking: success rate first, then median time to B", () => {
  const recs = [...many("slow", 5, 5, 30), ...many("fast", 5, 5, 18), ...many("bad", 1, 5, 10)];
  const agg = S.aggregate(recs, { planners: ["slow", "fast", "bad"], presets: ["ideal"], faults: ["truth"], seeds: 5 });
  assert.deepEqual(agg.ranking.map(r => r.planner), ["fast", "slow", "bad"]);
  near(agg.ranking[0].median_time_s, 18.2);
  assert.equal(agg.ranking[2].median_time_s, 10);
});

test("no clear winner when the top two Wilson intervals overlap", () => {
  const recs = [...many("astar_known", 5, 5), ...many("dwa", 4, 5)];
  const h = S.aggregate(recs, null).headline;
  assert.equal(h.kind, "tie");
  assert.equal(h.text, "No clear winner: A* + ESDF, known map and DWA (dynamic window) are within noise on this map (n=5).");
});

test("a winner is named only when the intervals are disjoint", () => {
  const recs = [...many("astar_known", 30, 30), ...many("bug2", 3, 30)];
  const h = S.aggregate(recs, null).headline;
  assert.equal(h.kind, "winner");
  assert.equal(h.planner, "astar_known");
  assert.match(h.text, /^A\* \+ ESDF, known map wins on this map: 30\/30 reached B/);
});

test("nobody reached B => no winner", () => {
  const h = S.aggregate([...many("a", 0, 3), ...many("b", 0, 3)], null).headline;
  assert.equal(h.kind, "none");
});

test("errors count as runs, never dropped", () => {
  const run = { planner: "dwa", preset: "ideal", fault: "truth", seed: 2 };
  const e1 = S.recordFromError(run, "worker crashed");
  const e2 = S.recordFromResult(run, { score: null });
  const e3 = S.recordFromResult(run, { score: { outcome: "weird" } });
  const ok = S.recordFromResult(run, { score: { outcome: "reached", time_to_goal_s: 19.4, path_length_m: 23.8, min_clearance_m: 0.56, duration_s: 19.4 }, worker_ms: 650 });
  for (const e of [e1, e2, e3]) assert.equal(e.outcome, "error");
  assert.equal(ok.wall_s, 0.65);
  const st = S.stats([e1, e2, e3, ok]);
  assert.equal(st.n, 4);
  assert.equal(st.error, 3);
  assert.equal(st.reached, 1);
  near(st.success.p, 0.25);
  assert.equal(st.mean_wall_s, 0.65);         // error runs have no wall time
  const csv = S.toCSV([e1, ok]);
  assert.equal(csv.trim().split("\n").length, 3);
  assert.match(csv, /,error,.*worker crashed/);
});

test("matrix cells split by variation; pooled row and stats", () => {
  const spec = S.normSpec({ planners: ["a"], presets: ["ideal", "crazyflie"], fault: "jump", seeds: 2 });
  assert.deepEqual(spec.faults, ["truth", "jump"]);
  assert.equal(S.runCount(spec), 8);
  const runs = S.buildRuns(spec);
  assert.equal(runs.length, 8);
  assert.deepEqual(S.variations(spec), ["ideal|truth", "ideal|jump", "crazyflie|truth", "crazyflie|jump"]);
  const recs = runs.map((r, i) => ({ ...rec("a", i % 2 ? "reached" : "stuck"), preset: r.preset, fault: r.fault, seed: r.seed }));
  const agg = S.aggregate(recs, spec);
  assert.equal(agg.cells.a["ideal|jump"].n, 2);
  assert.equal(agg.cells.a["ideal|jump"].reached, 2);
  assert.equal(agg.cells.a["ideal|truth"].stuck, 2);
  assert.equal(agg.pooled.a.n, 8);
});

test("run order interleaves planners (seed outermost)", () => {
  const runs = S.buildRuns(S.normSpec({ planners: ["a", "b"], seeds: 2 }));
  assert.deepEqual(runs.map(r => r.planner + r.seed), ["a0", "b0", "a1", "b1"]);
});

test("spec query round trip and unknown planners dropped", () => {
  const spec = S.normSpec({ planners: ["dwa", "bug2"], presets: ["crazyflie"], fault: "bias", seeds: 7 });
  const back = S.specFromQuery("?" + S.specToQuery(spec, "random_0"));
  assert.equal(back.src, "random_0");
  assert.deepEqual(S.normSpec(back.spec, ["dwa"]), { planners: ["dwa"], presets: ["crazyflie"], faults: ["truth", "bias"], fault: "bias", seeds: 7 });
  assert.equal(S.normSpec({ seeds: "999" }).seeds, S.MAX_SEEDS);
  assert.equal(S.normSpec({ fault: "rm -rf" }).fault, null);
});

test("world link codec round trip and w= from a pasted playground URL", async () => {
  const doc = { schema: "close-area-world/1", bounds: [0, 0, 20, 20], a: [1, 1], b: [18, 18], obstacles: [{ type: "box", cx: 5, cy: 5, hx: 1, hy: 1 }] };
  const w = await S.encodeWorld(doc);
  assert.match(w, /^[A-Za-z0-9_-]+$/);
  assert.deepEqual(await S.decodeWorld(w), doc);
  assert.equal(S.worldParamFrom(`http://localhost:8000/site/playground/index.html?planner=dwa&seed=3#w=${w}`), w);
  assert.equal(S.worldParamFrom("no link here"), null);
  await assert.rejects(S.decodeWorld("notdeflate"));
});

test("estimate uses measured wall times, else the prior, divided by K", () => {
  const pending = [{ planner: "dwa" }, { planner: "dwa" }, { planner: "bug2" }];
  const e = S.estimateSeconds(pending, { dwa: 2, bug2: 1 }, 2);
  assert.equal(e.s, 2.5); assert.equal(e.measured, true);
  const p = S.estimateSeconds(pending, {}, 1);
  near(p.s, 2 * S.PRIOR_WALL_S.dwa + S.PRIOR_WALL_S.bug2); assert.equal(p.measured, false);
  assert.equal(S.poolSize(16), 4); assert.equal(S.poolSize(1), 1); assert.equal(S.poolSize(undefined), 1); assert.equal(S.poolSize(3), 2);
});
