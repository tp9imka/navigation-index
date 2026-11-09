// Measure the Pyodide spike in headless Chrome and the same driver under native CPython.
// Run from the repo root (Node 22+, no npm packages):
//   node site/playground/results/measure.mjs
// Needs: samples/close-area-arena/.venv (uv venv + uv pip install -r requirements.txt, see the sample README),
// Google Chrome at the macOS default path, network access to cdn.jsdelivr.net.
// Writes into site/playground/results/: native_baseline.json, spike_cold.json, spike_warm.json,
// spike_bench.png, spike_interactive.png (1280 x 900 viewport) and spike_timing.md.
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const ARENA = path.join(ROOT, "samples/close-area-arena");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8765, DBG = 9333, VIEW = { width: 1280, height: 900 };
const sleep = t => new Promise(r => setTimeout(r, t));
const write = (name, data) => fs.writeFileSync(path.join(HERE, name), typeof data === "string" ? data : JSON.stringify(data, null, 1) + "\n");

// ---------- native baseline: the same DRIVER_PY string, under the sample venv ----------
function native() {
  const js = fs.readFileSync(path.join(HERE, "../spike.js"), "utf8");
  const driver = js.match(/const DRIVER_PY = String\.raw`([\s\S]*?)`;/)[1];
  const pre = `
import importlib.util, os, sys
ARENA = ${JSON.stringify(ARENA)}
spec = importlib.util.spec_from_file_location("close_area_arena", os.path.join(ARENA, "__init__.py"),
                                              submodule_search_locations=[ARENA])
pkg = importlib.util.module_from_spec(spec); sys.modules["close_area_arena"] = pkg; spec.loader.exec_module(pkg)
`;
  const post = `
import platform
CASES = [("straight", "random", 0), ("astar_esdf_known", "random", 0), ("astar_esdf_unknown", "random", 0),
         ("straight", "u_trap", 1), ("astar_esdf_known", "u_trap", 1), ("astar_esdf_unknown", "u_trap", 1)]
out = {"env": json.loads(env_json()), "cpu": platform.processor(), "cases": []}
for planner, family, index in CASES:
    for rep in (1, 2, 3, 4):
        buf = []
        emit = (lambda t, x, y: buf.append((x, y))) if rep < 4 else None
        r = json.loads(bench_case(planner, family, index, 0, emit))
        for k in ("trace", "path", "world"):
            r.pop(k)
        r["rep"], r["stream_on"] = rep, emit is not None
        out["cases"].append(r)
print(json.dumps(out))
`;
  const py = path.join(ARENA, ".venv/bin/python");
  const t0 = Date.now();
  const p = spawnSync(py, ["-"], { input: pre + driver + post, encoding: "utf8", maxBuffer: 64 << 20 });
  if (p.status !== 0) throw new Error("native baseline failed:\n" + p.stderr);
  const out = JSON.parse(p.stdout);
  out.wall_s = (Date.now() - t0) / 1e3;
  out.cpu_model = os.cpus()[0].model;
  out.input = "synthetic";
  return out;
}

// ---------- minimal DevTools protocol client ----------
class CDP {
  constructor(url) { this.ws = new WebSocket(url); this.id = 0; this.pending = new Map(); this.log = []; }
  open() {
    return new Promise((ok, fail) => {
      this.ws.onopen = ok; this.ws.onerror = fail;
      this.ws.onmessage = ev => {
        const m = JSON.parse(ev.data);
        if (m.id && this.pending.has(m.id)) {
          const [res, rej] = this.pending.get(m.id); this.pending.delete(m.id);
          m.error ? rej(new Error(JSON.stringify(m.error))) : res(m.result);
        } else if (m.method === "Runtime.exceptionThrown") {
          this.log.push("exception: " + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
        } else if (m.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(m.params.type)) {
          this.log.push(m.params.type + ": " + m.params.args.map(a => a.value || a.description).join(" ").slice(0, 400));
        }
      };
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((res, rej) => this.pending.set(id, [res, rej]));
  }
  async eval(expr) { return (await this.send("Runtime.evaluate", { expression: expr, returnByValue: true })).result.value; }
}

async function runPage(cdp, url, timeoutS) {
  await cdp.send("Page.navigate", { url });
  const t0 = Date.now();
  await sleep(500);
  while (!(await cdp.eval("window.SPIKE_DONE === true").catch(() => false))) {
    if ((Date.now() - t0) / 1e3 > timeoutS) throw new Error("timeout waiting for SPIKE_DONE at " + url);
    await sleep(500);
  }
  const res = JSON.parse(await cdp.eval("JSON.stringify(window.SPIKE_RESULT)"));
  res.driver_wait_s = (Date.now() - t0) / 1e3;
  return res;
}

async function shot(cdp, name) {
  const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  fs.writeFileSync(path.join(HERE, name), Buffer.from(data, "base64"));
}

async function browser() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "spike-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
    "--disable-renderer-backgrounding", `--window-size=${VIEW.width},${VIEW.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  let chromeErr = "";
  chrome.stderr.on("data", d => { chromeErr += d; });
  chrome.on("exit", code => { if (code) console.error("chrome exited", code, chromeErr.slice(-2000)); });
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) {          // up to 60 s: Chrome starts slowly on a loaded host
      await sleep(250);
      version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null);
    }
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...VIEW, deviceScaleFactor: 1, mobile: false });
    const base = `http://127.0.0.1:${PORT}/site/playground/spike.html`;
    const cold = await runPage(cdp, base + "?bench=1", 900);          // fresh profile => cold HTTP cache
    cold.console = cdp.log.splice(0);
    await shot(cdp, "spike_bench.png");
    const warm = await runPage(cdp, base, 300);                        // same profile => warm HTTP cache
    await sleep(6000);                                                  // let the 4x replay animation finish
    warm.console = cdp.log.splice(0);
    await shot(cdp, "spike_interactive.png");
    cdp.ws.close();
    return { version, cold, warm };
  } finally {
    const gone = new Promise(r => chrome.once("exit", r));
    chrome.kill(); server.kill();
    await Promise.race([gone, sleep(5000)]);
    await sleep(1000);
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 500 }); }
    catch (err) { console.error("could not remove temp profile", profile, err.code); }
  }
}

// ---------- compare scores with the published native results ----------
function published(planner, family, index) {
  const f = path.join(ARENA, `results/astar_esdf_${family}_0.json`);
  if (!fs.existsSync(f)) return null;
  const mode = { straight: "straight", astar_esdf_known: "astar_esdf known_map", astar_esdf_unknown: "astar_esdf unknown_map" }[planner];
  return JSON.parse(fs.readFileSync(f, "utf8")).modes[mode].runs[index];
}
const SCORE_KEYS = ["outcome", "time_to_goal_s", "duration_s", "min_clearance_m", "path_length_m"];
const same = (a, b) => a && b && SCORE_KEYS.every(k => a[k] === b[k]);

function med(a) { const s = a.filter(v => v != null).sort((p, q) => p - q); return s.length ? s[(s.length - 1) >> 1] : null; }

function report(nat, br) {
  const { cold, warm, version } = br;
  const L = [];
  const r2 = v => (v == null ? "-" : Math.round(v * 100) / 100);
  L.push("# Spike timing: close-area arena under Pyodide in headless Chrome", "");
  L.push(`Written by \`node site/playground/results/measure.mjs\` on ${new Date().toISOString().slice(0, 10)}. ` +
    "Input: synthetic (simulated layouts, vehicle and range sensor from samples/close-area-arena). " +
    "Raw data: [spike_cold.json](spike_cold.json), [spike_warm.json](spike_warm.json), [native_baseline.json](native_baseline.json).", "");
  L.push("## Environment", "");
  L.push("| | browser | native |", "|---|---|---|");
  L.push(`| runtime | ${version.Browser} headless=new, Pyodide ${cold.pyodide_version} | CPython ${nat.env.python} |`);
  L.push(`| Python / numpy / scipy | ${cold.env.python} / ${cold.env.numpy} / ${cold.env.scipy} | ${nat.env.python} / ${nat.env.numpy} / ${nat.env.scipy} |`);
  L.push(`| machine | ${nat.cpu_model} (${os.cpus().length} cores), ${os.type()} ${os.release()} ${os.arch()} | same machine |`, "");
  const la = nat.loadavg, f1 = a => a.map(v => v.toFixed(0)).join(" / ");
  L.push(`Host load average (1 / 5 / 15 min): ${f1(la.before_native)} before native, ${f1(la.after_native)} after native, ` +
    `${f1(la.after_browser)} after Chrome. The host was shared with other jobs, so absolute times are pessimistic and noisy; ` +
    "native and browser ran one after the other, not interleaved.", "");
  L.push("## Load (once per page)", "");
  L.push("| step | cold cache ms | warm cache ms |", "|---|---|---|");
  const rows = [["pyodide.js script", "pyodide_script_ms"], ["loadPyodide() (wasm + stdlib)", "pyodide_init_ms"],
    ["loadPackage numpy + scipy", "packages_ms"], ["fetch 11 arena .py files (parallel with packages)", "arena_fetch_ms"],
    ["load total (script start => files written)", "load_total_ms"], ["arena import (DRIVER_PY incl. numpy, scipy.ndimage)", "import_ms"],
    ["ready, since navigation start", "ready_ms"]];
  for (const [n, k] of rows) L.push(`| ${n} | ${cold.t[k]} | ${warm.t[k]} |`);
  L.push(`| of which numpy + scipy.ndimage import (Python perf_counter) | ${cold.env.imports.numpy_scipy_import_ms} | ${warm.env.imports.numpy_scipy_import_ms} |`);
  L.push(`| of which arena modules import | ${cold.env.imports.arena_import_ms} | ${warm.env.imports.arena_import_ms} |`, "");
  const dl = cold.resources.filter(r => r.host.includes("jsdelivr"));
  const tot = dl.reduce((n, r) => n + r.transfer_kb, 0), dec = dl.reduce((n, r) => n + r.decoded_kb, 0);
  L.push(`Cold download from cdn.jsdelivr.net: ${dl.length} files, ${(tot / 1024).toFixed(1)} MB transferred, ` +
    `${(dec / 1024).toFixed(1)} MB decoded (Resource Timing). Largest:`, "");
  L.push("| file | transferred KB | decoded KB | ms |", "|---|---|---|---|");
  for (const r of [...dl].sort((a, b) => b.decoded_kb - a.decoded_kb).slice(0, 5)) L.push(`| ${r.name.split("/").pop()} | ${r.transfer_kb} | ${r.decoded_kb} | ${r.ms} |`);
  L.push("", `Arena source: ${cold.arena_files} files, ${(cold.arena_bytes / 1024).toFixed(1)} KB, from the local server.`, "");
  L.push("## Runs (cold page, 3 streamed runs + 1 without streaming per case)", "");
  L.push("Wall = `run_one` only (layout build excluded, listed separately). 30 s projection = median wall per simulated second x 30. " +
    `Target: under 15 s.`, "");
  L.push("| planner | layout | outcome | sim s | browser first run s | browser median s | browser wall per sim s | 30 s run => browser wall s | verdict | no-stream run s | native median wall per sim s | browser / native | layout build ms (browser) |",
    "|---|---|---|---|---|---|---|---|---|---|---|---|---|");
  const keys = [...new Set(cold.cases.map(c => `${c.planner}|${c.family}|${c.index}`))];
  const out = [];
  for (const k of keys) {
    const [p, f, i] = k.split("|");
    const pick = (arr, s) => arr.filter(c => c.planner === p && c.family === f && String(c.index) === i && c.stream_on === s);
    const bs = pick(cold.cases, true), bp = pick(cold.cases, false), ns = pick(nat.cases, true);
    const bw = med(bs.map(c => c.wall_per_sim_s)), nw = med(ns.map(c => c.wall_per_sim_s));
    const proj = bw * 30;
    out.push({ case: k, bw, nw, proj });
    L.push(`| ${p} | ${f}/${i} | ${bs[0].row.outcome} | ${bs[0].sim_s} | ${bs[0].run_s} | ${med(bs.map(c => c.run_s))} | ${bw} | ${r2(proj)} | ` +
      `${proj < 15 ? "PASS" : "FAIL"} | ${bp[0] ? bp[0].run_s : "-"} | ${nw} | ${r2(bw / nw)}x | ${med(bs.map(c => c.world_ms))} |`);
  }
  L.push("", "## Same scores as native", "");
  L.push(`Fields compared: ${SCORE_KEYS.join(", ")}.`, "");
  L.push("| planner | layout | browser = published results/astar_esdf_{family}_0.json | browser = native run today |", "|---|---|---|---|");
  for (const k of keys) {
    const [p, f, i] = k.split("|");
    const b = cold.cases.find(c => c.planner === p && c.family === f && String(c.index) === i).row;
    const n = nat.cases.find(c => c.planner === p && c.family === f && String(c.index) === i).row;
    const pub = published(p, f, +i);
    L.push(`| ${p} | ${f}/${i} | ${pub ? (same(b, pub) ? "yes" : "no: " + SCORE_KEYS.map(x => `${x} ${b[x]} vs ${pub[x]}`).join(", ")) : "n/a"} | ` +
      `${same(b, n) ? "yes" : "no: " + SCORE_KEYS.map(x => `${x} ${b[x]} vs ${n[x]}`).join(", ")} |`);
  }
  L.push("", "## Memory (Chrome)", "");
  L.push("| point | wasm heap MB | JS heap used MB |", "|---|---|---|");
  const mem = cold.memory;
  for (const m of [mem[0], mem[1], mem[2], mem[mem.length - 1]].filter(Boolean)) L.push(`| ${m.label} | ${m.wasm_heap_mb ?? "-"} | ${m.js_heap_used_mb ?? "-"} |`);
  L.push("", "## Interactive page (warm cache, 2 cases, 1 run each)", "");
  L.push("| planner | layout | outcome | sim s | wall s | positions streamed |", "|---|---|---|---|---|---|");
  for (const c of warm.cases) L.push(`| ${c.planner} | ${c.family}/${c.index} | ${c.row.outcome} | ${c.sim_s} | ${c.run_s} | ${c.stream_n} |`);
  L.push("", `Console errors / warnings: cold ${cold.console.length}, warm ${warm.console.length}. Page errors: cold ${cold.errors.length}, warm ${warm.errors.length}.`);
  L.push("", "Screenshots (1280 x 900 viewport): [bench](spike_bench.png), [interactive](spike_interactive.png).", "");
  return { md: L.join("\n"), out };
}

const load = { before_native: os.loadavg() };
const nat = native();
load.after_native = os.loadavg();
console.log("native done", nat.wall_s, "s");
const br = await browser();
load.after_browser = os.loadavg();
nat.loadavg = load;
write("native_baseline.json", nat);
write("spike_cold.json", { chrome: br.version, ...br.cold });
write("spike_warm.json", { chrome: br.version, ...br.warm });
const { md, out } = report(nat, br);
write("spike_timing.md", md);
console.log(JSON.stringify(out, null, 1));
console.log("console:", br.cold.console, br.warm.console, "errors:", br.cold.errors, br.warm.errors);
