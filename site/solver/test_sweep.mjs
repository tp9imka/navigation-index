// node --test site/solver/test_sweep.mjs  (plain node, no npm packages)
import { test } from "node:test";
import assert from "node:assert/strict";
import * as S from "./sweep.js";

const near = (a, b, tol = 5e-4) => assert.ok(Math.abs(a - b) <= tol, `${a} != ${b}`);
const rec = (planner, outcome, extra = {}) => ({ planner, preset: "ideal", fault: "truth", seed: 0, outcome,
  time_to_goal_s: outcome === "reached" ? 20 : null, path_length_m: 24, min_clearance_m: 0.4, duration_s: 20, wall_s: 0.5, error: null, ...extra });
const many = (planner, k, n, t = 20) => Array.from({ length: n }, (_, i) =>
  rec(planner, i < k ? "reached" : "collision", { seed: i, time_to_goal_s: i < k ? t + i * 0.1 : null, path_length_m: 24 + i * 0.01 }));

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
  const spec = S.normSpec({ planners: ["dwa", "bug2"], presets: ["crazyflie"], fault: "bias", seeds: 7, jitter: "0.25" });
  const back = S.specFromQuery("?" + S.specToQuery(spec, "random_0"));
  assert.equal(back.src, "random_0");
  assert.deepEqual(S.normSpec(back.spec, ["dwa"]), { planners: ["dwa"], presets: ["crazyflie"], faults: ["truth", "bias"], fault: "bias", seeds: 7, jitter: 0.25, time_limit: "auto",
    vehicle: S.VEHICLE_DEFAULT, sensor_choice: "ideal", sensor: null, yaw: "fixed" });
  assert.equal(S.normSpec({}).jitter, 0.5);                 // default ON, 0.5 m
  assert.equal(S.normSpec({ jitter: 0 }).jitter, 0);
  assert.equal(S.normSpec({ jitter: "1" }).jitter, 1);
  assert.equal(S.normSpec({ jitter: "7" }).jitter, 0.5);    // not a choice => default
  assert.equal(S.normSpec(S.specFromQuery("?jitter=0").spec).jitter, 0);
  assert.equal(S.normSpec({ seeds: "999" }).seeds, S.MAX_SEEDS);
  assert.equal(S.normSpec({ fault: "rm -rf" }).fault, null);
});

test("run time limit: Auto by family (bench.py LONG_FAMILIES), fixed choices, share link round trip", () => {
  assert.deepEqual(S.LONG_FAMILIES, { maze: 120, warehouse: 120 });
  assert.equal(S.normSpec({}).time_limit, "auto");
  assert.equal(S.timeLimitFor({ family: "maze" }, "auto").s, 120);
  assert.equal(S.timeLimitFor({ family: "warehouse" }).s, 120);
  assert.equal(S.timeLimitFor({ family: "office" }, "auto").s, 60);
  assert.deepEqual(S.timeLimitFor({ family: "custom" }, "auto"), { s: 60, source: "default", family: "custom" });
  assert.equal(S.timeLimitFor({}, "auto").source, "default");                  // no family => 60 s
  assert.equal(S.timeLimitFor({ family: "constructor" }, "auto").s, 60);       // not an own key
  assert.deepEqual(S.timeLimitFor({ family: "maze" }, "60"), { s: 60, source: "fixed", family: "maze" });
  for (const tl of ["auto", 60, 120, 180]) {
    const spec = S.normSpec({ planners: ["bug2"], time_limit: tl });
    const q = S.specToQuery(spec, "maze_0");
    assert.match(q, new RegExp(`(^|&)tlim=${tl}(&|$)`));
    const back = S.normSpec(S.specFromQuery("?" + q).spec);
    assert.equal(back.time_limit, tl);
    assert.equal(S.cfgTimeLimit(back), tl === "auto" ? undefined : tl);
  }
  assert.equal(S.normSpec(S.specFromQuery("?planners=bug2").spec).time_limit, "auto");   // old links: Auto
  assert.equal(S.normSpec({ time_limit: "999" }).time_limit, "auto");                    // not a choice
  const run = { planner: "bug2", preset: "ideal", fault: "truth", seed: 0 };
  const r = S.recordFromResult(run, { score: { outcome: "reached", time_to_goal_s: 105.2, path_length_m: 65.5, duration_s: 105.2 }, max_time_s: 120 });
  assert.equal(r.max_time_s, 120);
  assert.equal(S.recordFromError(run, "x").max_time_s, null);
  assert.match(S.toCSV([r]).split("\n")[0], /,duration_s,max_time_s,wall_s,/);
  const spec = S.normSpec({ planners: ["bug2"] });
  const doc = S.exportDoc({ spec, world: { family: "maze", bounds: [0, 0, 1, 1] }, records: [r] });
  assert.equal(doc.spec.time_limit, "auto");
  assert.deepEqual([doc.time_limit.choice, doc.time_limit.expected_s, doc.time_limit.source, doc.time_limit.used_s], ["auto", 120, "family", [120]]);
  assert.match(S.timeLimitText(spec, { family: "maze" }, [r]), /120 s .*maze family/);
  assert.match(S.timeLimitText(spec, { family: "custom" }, []), /60 s .*no benchmark family/);
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

// ------------------------------------------------------------ jitter and duplicates
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
const PRESETS = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../playground/presets");
const presetDocs = () => JSON.parse(fs.readFileSync(path.join(PRESETS, "index.json"), "utf8")).presets
  .map(p => [p.file, JSON.parse(fs.readFileSync(path.join(PRESETS, p.file), "utf8"))]);

test("clearanceAt: boxes, cylinders, walls and bounds", () => {
  const doc = { bounds: [0, 0, 10, 10], obstacles: [{ type: "box", cx: 5, cy: 5, hx: 1, hy: 1 },
    { type: "cylinder", cx: 2, cy: 8, r: 0.5 }, { type: "wall", x0: 7, y0: 2, x1: 9, y1: 2, thickness: 0.2 }] };
  near(S.clearanceAt(doc, 5, 7), 1);           // above the box
  near(S.clearanceAt(doc, 5, 5), -1);          // box centre: inside
  near(S.clearanceAt(doc, 2, 9), 0.5);         // cylinder edge 0.5 below, bound 1.0 above
  near(S.clearanceAt(doc, 8, 2.6), 0.5);       // wall half thickness 0.1
  near(S.clearanceAt(doc, 0.3, 3), 0.3);       // left bound
  assert.ok(S.clearanceAt(doc, -1, 3) < 0);
});

test("jitter: seed 0 exact, same seed => same offsets, different seeds differ", () => {
  const doc = JSON.parse(fs.readFileSync(path.join(PRESETS, "random_0.json"), "utf8"));
  const j0 = S.seedJitter(doc, 0, 0.5);
  assert.equal(j0.exact, true); assert.deepEqual(j0.a, doc.a); assert.deepEqual(j0.b, doc.b);
  const a = S.seedJitters(doc, { seeds: 5, jitter: 0.5 }), b = S.seedJitters(doc, { seeds: 5, jitter: 0.5 });
  assert.deepEqual(a, b);
  assert.deepEqual(S.seedJitter(doc, 3, 0.5), a[3]);           // order independent
  assert.notDeepEqual(a[1].a, a[2].a);
  for (const j of a.slice(1)) {
    assert.ok(Math.hypot(j.a[0] - doc.a[0], j.a[1] - doc.a[1]) <= 0.5 + 1e-4);
    assert.ok(Math.hypot(j.b[0] - doc.b[0], j.b[1] - doc.b[1]) <= 0.5 + 1e-4);
    assert.notDeepEqual(j.a, doc.a);
  }
  assert.deepEqual(S.seedJitters(doc, { seeds: 3, jitter: 0 }).map(j => j.exact), [true, true, true]);
  const w = S.jitterWorld(doc, a[1]);
  assert.deepEqual(w.a, a[1].a); assert.deepEqual(doc.a, [0, 0]);           // original untouched
  assert.deepEqual(w.obstacles, doc.obstacles);
});

test("jitter: offsets avoid obstacles and bounds on every preset", () => {
  for (const [name, doc] of presetDocs()) {
    const min = S.vehicleRadius(doc) + S.JITTER_MARGIN_M;
    for (const R of S.JITTER_RADII)
      for (const j of S.seedJitters(doc, { seeds: 20, jitter: R }).slice(1)) {
        for (const [k, p] of [["a", j.a], ["b", j.b]]) {
          const kept = j[k + "_kept"];
          if (!kept) assert.ok(S.clearanceAt(doc, p[0], p[1]) >= min - 1e-9, `${name} R=${R} seed ${j.seed} ${k} too close`);
          else assert.deepEqual(p, doc[k]);
        }
      }
  }
});

test("jitter: no free point in 50 draws => exact point kept and recorded", () => {
  const doc = { bounds: [0, 0, 10, 10], a: [5, 5], b: [8, 8], radius: 0.15,
    obstacles: [{ type: "box", cx: 5, cy: 5, hx: 3, hy: 3 }] };           // A buried: every draw is inside
  const j = S.seedJitter(doc, 1, 0.5);
  assert.equal(j.a_kept, true); assert.deepEqual(j.a, [5, 5]);
  assert.equal(j.b_kept, false);
  const r = S.recordFromResult({ planner: "dwa", preset: "ideal", fault: "truth", seed: 1, a: j.a, b: j.b, ab_kept: { a: true, b: false } },
    { score: { outcome: "stuck", path_length_m: 1 } });
  assert.deepEqual(r.a, [5, 5]); assert.deepEqual(r.ab_kept, { a: true, b: false });
  const csv = S.toCSV([r]).split("\n");
  assert.match(csv[0], /,a_x,a_y,b_x,b_y,/);
  assert.match(csv[1], new RegExp(`,1,5,5,${j.b[0]},${j.b[1]},stuck,`));
});

test("identical runs collapse to one trial in the interval and the headline", () => {
  const same = planner => [0, 1, 2].map(seed => rec(planner, "reached", { seed, time_to_goal_s: 19.38, path_length_m: 24.0001 }));
  const recs = [...same("astar_known"), ...many("dwa", 3, 3)];
  const agg = S.aggregate(recs, null);
  const c = agg.cells.astar_known["ideal|truth"];
  assert.equal(c.n, 3); assert.equal(c.n_distinct, 1); assert.equal(c.identical, 3); assert.equal(c.reached_distinct, 1);
  assert.deepEqual(c.success, S.wilson(1, 1));
  assert.equal(agg.cells.dwa["ideal|truth"].n_distinct, 3);
  assert.equal(agg.cells.dwa["ideal|truth"].identical, 0);
  assert.equal(agg.pooled.astar_known.n_distinct, 1);
  // dwa 3/3 distinct ranks above astar_known 1/1? same p = 1, then median time: dwa 20.1 vs 19.38
  assert.equal(agg.ranking[0].planner, "astar_known");
  assert.equal(agg.headline.kind, "tie");
  assert.match(agg.headline.text, /\(n=3, 1 distinct and n=3\)\. Identical runs count once in the interval\.$/);
  // a 2 + 1 split: 2 identical, 2 distinct
  const split = S.stats([rec("x", "reached", { seed: 0 }), rec("x", "reached", { seed: 1 }), rec("x", "reached", { seed: 2, time_to_goal_s: 21 })]);
  assert.equal(split.n_distinct, 2); assert.equal(split.identical, 2);
  // the 3 dp rounding decides: 19.3801 == 19.3804, 19.380 != 19.381
  assert.equal(S.stats([rec("x", "reached", { time_to_goal_s: 19.3801 }), rec("x", "reached", { time_to_goal_s: 19.3804 })]).n_distinct, 1);
  assert.equal(S.stats([rec("x", "reached", { time_to_goal_s: 19.380 }), rec("x", "reached", { time_to_goal_s: 19.381 })]).n_distinct, 2);
  // same numbers in different variations are different runs in the pooled row
  const two = [rec("x", "reached"), rec("x", "reached", { preset: "crazyflie" })];
  assert.equal(S.stats(two).n_distinct, 2);
});

test("all identical everywhere => headline says n and distinct", () => {
  const same = planner => [0, 1, 2].map(seed => rec(planner, "reached", { seed, time_to_goal_s: planner === "a" ? 18 : 19 }));
  const h = S.aggregate([...same("a"), ...same("b")], null).headline;
  assert.equal(h.text, "No clear winner: a and b are within noise on this map (n=3, 1 distinct). Identical runs count once in the interval.");
});


// ------------------------------------------------------------ your drone (loop-76)
const DRONE = { vehicle: { radius_m: 0.25, v_max: 1.5, a_max: 4, tau: 0.15 }, sensor_choice: "custom",
  sensor: { beams: 30, fov_deg: 87, max_range_m: 5, min_range_m: 0.3, noise_sigma_m: 0.04 }, yaw: "look_where_you_go" };

test("custom sensor is one more variation key next to the presets, labelled by its spec", () => {
  const spec = S.normSpec({ planners: ["a"], presets: ["ideal", "depth_cam_87"], seeds: 2, ...DRONE });
  assert.deepEqual(spec.presets, ["ideal", "depth_cam_87", "custom"]);
  assert.deepEqual(S.variations(spec), ["ideal|truth", "depth_cam_87|truth", "custom|truth"]);
  assert.equal(S.runCount(spec), 6);
  assert.equal(S.variationLabel("custom|truth", spec), "custom 30 beams 87 deg 5 m / truth pose");
  assert.equal(S.variationLabel("lidar_2d|jump"), "lidar_2d / VIO jump");
  // Custom with no preset checked => the custom variation alone; a preset choice adds no custom key
  assert.deepEqual(S.normSpec({ ...DRONE, presets: [] }).presets, ["custom"]);
  assert.deepEqual(S.normSpec({ presets: ["lidar_2d"], sensor_choice: "lidar_2d" }).presets, ["lidar_2d"]);
  assert.equal(S.normSpec({ presets: ["lidar_2d"], sensor_choice: "lidar_2d" }).sensor, null);
  assert.equal(S.normSpec({ sensor_choice: "rm -rf" }).sensor_choice, "ideal");
  // runs carry beams for the estimate; the custom spec is in each record
  const runs = S.buildRuns(spec);
  assert.deepEqual(runs.map(r => r.beams), [72, 30, 30, 72, 30, 30]);
  const run = { ...runs[2], vehicle: spec.vehicle, sensor: spec.sensor, yaw: spec.yaw };
  const r = S.recordFromResult(run, { score: { outcome: "reached", time_to_goal_s: 15, path_length_m: 16 }, sensor: { yaw_policy: "look_where_you_go" } });
  assert.equal(r.preset, "custom");
  assert.deepEqual(r.sensor, spec.sensor);
  assert.deepEqual(r.vehicle, DRONE.vehicle);
  assert.equal(r.yaw, "look_where_you_go"); assert.equal(r.yaw_policy, "look_where_you_go");
  const e = S.recordFromError(run, "boom");
  assert.deepEqual(e.sensor, spec.sensor); assert.equal(e.yaw_policy, null);
  // a named preset record gets the preset table spec, and the default vehicle when none was set
  const p = S.recordFromResult({ planner: "a", preset: "depth_cam_87", fault: "truth", seed: 0 }, { score: { outcome: "stuck" } });
  assert.equal(p.sensor.beams, 30); assert.equal(p.sensor.fov_deg, 87);
  assert.deepEqual(p.vehicle, S.VEHICLE_DEFAULT); assert.equal(p.yaw, "fixed");
  const agg = S.aggregate([r, p], spec);
  assert.equal(agg.cells.a["custom|truth"].reached, 1);
});

test("cfg extras: vehicle only when changed, sensor for custom, yaw only when not fixed", () => {
  const spec = S.normSpec({ planners: ["a"], ...DRONE });
  assert.deepEqual(S.cfgExtras(spec, "custom"), { vehicle: DRONE.vehicle, sensor: DRONE.sensor, yaw: "look_where_you_go" });
  assert.deepEqual(S.cfgExtras(spec, "ideal"), { vehicle: DRONE.vehicle, yaw: "look_where_you_go" });
  assert.deepEqual(S.cfgExtras(S.normSpec({ planners: ["a"] }), "ideal"), {});
  assert.equal("yaw" in S.cfgExtras(S.normSpec({ yaw: "fixed" }), "ideal"), false);
  // clamped to the worker's ranges, min range kept 0.1 m below max
  assert.deepEqual(S.normVehicle({ radius_m: 9, v_max: "x", a_max: 0.1 }), { radius_m: 0.6, v_max: 2, a_max: 0.5, tau: 0.15 });
  const s = S.normSensor({ beams: 30.6, fov_deg: 500, max_range_m: 1, min_range_m: 2, noise_sigma_m: 0.04 });
  assert.deepEqual(s, { beams: 31, fov_deg: 360, max_range_m: 1, min_range_m: 0.9, noise_sigma_m: 0.04 });
  // jitter keeps the larger vehicle radius from surfaces
  assert.equal(S.sweepRadius({ radius: 0.15 }, spec), 0.25);
  assert.equal(S.sweepRadius({ radius: 0.15 }, S.normSpec({})), 0.15);
});

test("share link carries vehicle, sensor and yaw; old links open with the defaults", () => {
  const spec = S.normSpec({ planners: ["dwa"], presets: ["lidar_2d"], seeds: 3, ...DRONE });
  const q = S.specToQuery(spec, "office_0");
  assert.match(q, /(^|&)veh=0\.25%2C1\.5%2C4%2C0\.15(&|$)/);
  assert.match(q, /(^|&)sensor=custom(&|$)/);
  assert.match(q, /(^|&)cs=30%2C87%2C5%2C0\.3%2C0\.04(&|$)/);
  assert.match(q, /(^|&)yaw=look_where_you_go(&|$)/);
  assert.match(q, /(^|&)presets=lidar_2d(&|$)/);                         // custom is implied by sensor=custom
  const back = S.normSpec(S.specFromQuery("?" + q).spec);
  assert.deepEqual(back, spec);
  const plain = S.specToQuery(S.normSpec({ planners: ["dwa"], sensor_choice: "depth_cam_87", presets: ["depth_cam_87"] }));
  assert.doesNotMatch(plain, /yaw=|cs=/);
  assert.equal(S.normSpec(S.specFromQuery("?" + plain).spec).sensor_choice, "depth_cam_87");
  const old = S.normSpec(S.specFromQuery("?planners=bug2&presets=ideal").spec);
  assert.deepEqual([old.vehicle, old.sensor_choice, old.sensor, old.yaw], [S.VEHICLE_DEFAULT, "ideal", null, "fixed"]);
});

test("CSV and JSON exports carry vehicle, sensor and yaw", () => {
  const spec = S.normSpec({ planners: ["a"], presets: ["depth_cam_87"], seeds: 1, ...DRONE });
  const runs = S.buildRuns(spec).map(r => ({ ...r, vehicle: spec.vehicle, sensor: r.preset === "custom" ? spec.sensor : null, yaw: spec.yaw }));
  const recs = runs.map(r => S.recordFromResult(r, { score: { outcome: "reached", time_to_goal_s: 12, path_length_m: 14 }, sensor: { yaw_policy: "look_where_you_go" } }));
  const [head, ...rows] = S.toCSV(recs).trim().split("\n");
  const cols = head.split(",");
  for (const c of ["sensor_label", "sensor_beams", "sensor_fov_deg", "sensor_max_range_m", "sensor_noise_sigma_m", "vehicle_radius_m",
    "vehicle_v_max", "vehicle_a_max", "vehicle_tau", "yaw", "yaw_policy"]) assert.ok(cols.includes(c), c);
  const row = Object.fromEntries(rows[1].split(",").map((v, i) => [cols[i], v]));
  assert.deepEqual([row.preset, row.sensor_label, row.sensor_beams, row.sensor_fov_deg, row.vehicle_radius_m, row.yaw, row.yaw_policy],
    ["custom", "custom 30 beams 87 deg 5 m", "30", "87", "0.25", "look_where_you_go", "look_where_you_go"]);
  const row0 = Object.fromEntries(rows[0].split(",").map((v, i) => [cols[i], v]));
  assert.deepEqual([row0.sensor_label, row0.sensor_min_range_m], ["depth_cam_87", "0.3"]);
  const doc = S.exportDoc({ spec, world: { bounds: [0, 0, 1, 1], radius: 0.15 }, records: recs });
  assert.deepEqual(doc.spec.vehicle, DRONE.vehicle);
  assert.equal(doc.spec.yaw, "look_where_you_go");
  assert.deepEqual(doc.drone.sensor, DRONE.sensor);
  assert.equal(doc.drone.custom_label, "custom 30 beams 87 deg 5 m");
  assert.equal(doc.drone.vehicle_sent, true); assert.equal(doc.drone.yaw_sent, true);
  assert.deepEqual(doc.drone.yaw_policy_flown, ["look_where_you_go"]);
  assert.equal(doc.drone.sensor_specs.depth_cam_87.beams, 30);
  near(doc.jitter.min_clearance_m, 0.35);
  assert.deepEqual(doc.records[1].sensor, DRONE.sensor);
});

test("estimate: prior scaled by beams / 72 (floor 0.25), measured times unscaled", () => {
  const p = S.PRIOR_WALL_S.dwa;
  near(S.estimateSeconds([{ planner: "dwa", beams: 360 }], {}, 1).s, 5 * p);
  near(S.estimateSeconds([{ planner: "dwa", beams: 30 }], {}, 1).s, p * 30 / 72);
  near(S.estimateSeconds([{ planner: "dwa", beams: 4 }], {}, 1).s, p * 0.25);
  near(S.estimateSeconds([{ planner: "dwa", beams: 72 }], {}, 1).s, p);
  assert.equal(S.estimateSeconds([{ planner: "dwa", beams: 360 }], { dwa: 2 }, 1).s, 2);
});
