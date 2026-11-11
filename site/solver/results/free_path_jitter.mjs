// How often did the old jitter picker wall A or B in? Pure node, no browser, no runs.
// For every preset in site/playground/presets plus the two room worlds, seeds 1..49 and each jitter radius,
// counts the seeds whose first drawn A/B pair (the earlier rule) has no free path at the world radius
// (SW.hasFreePath, the worker's free_path rule; parity 10/10 in measure_import.json), and how many the
// redraw fixed. Run from the repo root: node site/solver/results/free_path_jitter.mjs
// Writes site/solver/results/free_path_jitter.json. Synthetic worlds.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as SW from "../sweep.js";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const PRESETS = path.join(ROOT, "site/playground/presets");
const worlds = JSON.parse(fs.readFileSync(path.join(PRESETS, "index.json"), "utf8")).presets
  .map(p => [p.file.replace(/\.json$/, ""), path.join(PRESETS, p.file)])
  .concat([["hall_8x6", "samples/close-area-arena/rooms/hall_8x6.world.json"], ["sketch_hall", "samples/close-area-arena/rooms/sketch_hall.world.json"]]
    .map(([n, f]) => [n, path.join(ROOT, f)]));
const SEEDS = 49;
const out = { date: new Date().toISOString(), input: "synthetic", command: "node site/solver/results/free_path_jitter.mjs",
  seeds: `1..${SEEDS}`, radii_m: SW.JITTER_RADII, path_tries: SW.JITTER_PATH_TRIES, worlds: {} };
for (const [name, file] of worlds) {
  const doc = JSON.parse(fs.readFileSync(file, "utf8")), rad = SW.vehicleRadius(doc), min = rad + SW.JITTER_MARGIN_M;
  const w = out.worlds[name] = { radius_m: rad, exact_free_path: SW.hasFreePath(doc, doc.a || [0, 0], doc.b, rad) };
  for (const R of SW.JITTER_RADII) {
    let walled = 0, fixed = 0, kept = 0;
    for (let s = 1; s <= SEEDS; s++) {
      const rng = SW.mulberry32((Math.imul(s, 0x9E3779B1) ^ 0x5EED) >>> 0);
      const a = SW.jitterPoint(doc, doc.a || [0, 0], rng, R, min).p, b = SW.jitterPoint(doc, doc.b, rng, R, min).p;
      if (SW.hasFreePath(doc, a, b, rad)) continue;
      walled++;
      const j = SW.seedJitter(doc, s, R, rad);
      if (j.free_path && !j.path_kept) fixed++; else kept++;
    }
    w[`R${R}`] = { first_draw_no_path: walled, redraw_connected: fixed, exact_kept: kept };
  }
}
const tot = k => Object.values(out.worlds).reduce((a, w) => a + SW.JITTER_RADII.reduce((b, R) => b + w[`R${R}`][k], 0), 0);
out.total = { seed_draws: worlds.length * SW.JITTER_RADII.length * SEEDS, first_draw_no_path: tot("first_draw_no_path"),
  redraw_connected: tot("redraw_connected"), exact_kept: tot("exact_kept") };
fs.writeFileSync(path.join(HERE, "free_path_jitter.json"), JSON.stringify(out, null, 1) + "\n");
console.log(JSON.stringify(out.total), Object.entries(out.worlds).map(([n, w]) => `${n}: ${SW.JITTER_RADII.map(R => w[`R${R}`].first_draw_no_path).join("/")}`).join("; "));
