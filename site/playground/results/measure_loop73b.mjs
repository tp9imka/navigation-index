// loop-73b: browser = native for every maze_0 and warehouse_0 case, after the run time limit became the
// benchmark's (worker.js max_time_for = bench.py LONG_FAMILIES: maze, warehouse 120 s, else 60 s).
// Cases: the maze_0 / warehouse_0 rows of native_parity.json and native_parity_loop73.json. Also checks that
// the result reports max_time_s and the score table shows "(limit N s)" next to the outcome.
// Copy of measure_loop73.mjs (not imported). Run from the repo root (Node 22+, no npm packages), after
//   samples/close-area-arena/.venv/bin/python site/playground/results/native_parity.py
//   samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_loop73.py
//   node site/playground/results/measure_loop73b.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network access to cdn.jsdelivr.net.
// Writes site/playground/results/playground_loop73b.json and playground_loop73b.md.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8777, DBG = 9345, DESK = { width: 1280, height: 900 };
const SLOW_S = 60;                         // a planner slower than this per run stays out of the playground list
const sleep = t => new Promise(r => setTimeout(r, t));
const write = (name, data) => fs.writeFileSync(path.join(HERE, name), typeof data === "string" ? data : JSON.stringify(data, null, 1) + "\n");
const NP = JSON.parse(fs.readFileSync(path.join(HERE, "native_parity.json"), "utf8"));
const NP73 = JSON.parse(fs.readFileSync(path.join(HERE, "native_parity_loop73.json"), "utf8"));
const NATIVE = { native_env: NP.native_env, cases: [...NP.cases.map(c => ({ ...c, src: "native_parity.json" })),
  ...NP73.cases.map(c => ({ ...c, src: "native_parity_loop73.json" }))].filter(c => ["maze_0", "warehouse_0"].includes(c.world)) };
const KEYS = NP.keys;

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
          this.log.push("exception: " + JSON.stringify(m.params.exceptionDetails).slice(0, 600));
        } else if (m.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(m.params.type)) {
          this.log.push(m.params.type + ": " + m.params.args.map(a => a.value || a.description).join(" ").slice(0, 600));
        }
      };
    });
  }
  send(method, params = {}) {
    const id = ++this.id;
    this.ws.send(JSON.stringify({ id, method, params }));
    return new Promise((res, rej) => this.pending.set(id, [res, rej]));
  }
  async eval(expr) {
    const r = await this.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 600));
    return r.result.value;
  }
}

const pick = s => Object.fromEntries(KEYS.map(k => [k, s[k]]));
const same = (a, b) => KEYS.every(k => a[k] === b[k]);

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "pg73b-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  let chrome = null;
  const out = { date: new Date().toISOString(), input: "synthetic", page: `http://127.0.0.1:${PORT}/site/playground/index.html?pyodide=cdn`,
    native: ["native_parity.json", "native_parity_loop73.json"], host: { cpus: os.cpus().length, loadavg: os.loadavg().map(x => Math.round(x * 10) / 10) } };
  try {
    chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
      "--no-first-run", "--no-default-browser-check", "--disable-background-timer-throttling",
      "--disable-renderer-backgrounding", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
    { stdio: ["ignore", "ignore", "pipe"] });
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    out.chrome = version.Browser;
    await cdp.send("Page.navigate", { url: out.page });
    await sleep(800);
    await cdp.eval("PG.ready.then(() => true)");
    await cdp.eval("PG.started.then(() => true)");
    const env = await cdp.eval("PG_STATE.env");
    out.env = { pyodide: env.pyodide, python: env.python, numpy: env.numpy, scipy: env.scipy, planners: env.planners,
      load_errors: env.load_errors, imports_ms: env.imports_ms, arena_files: env.arena_files };
    console.log("ready; planners", env.planners.length, "load errors", JSON.stringify(env.load_errors));
    out.parity = [];
    for (const c of NATIVE.cases) {
      await cdp.eval(`PG.loadPreset(${JSON.stringify(c.world)})`);
      const cfg = { planner: c.planner, preset: c.preset, fault: c.fault, filter: c.filter, seed: 0 };
      const r = await cdp.eval(`PG.run([${JSON.stringify(cfg)}]).then(x => x && x.map(y => ({score: y.score, wall_s: y.wall_s, sim_s: y.sim_s, worker_ms: y.worker_ms, max_time_s: y.max_time_s, max_time_source: y.max_time_source})))`);
      if (!r) throw new Error("run failed for " + JSON.stringify(c) + " " + await cdp.eval("document.querySelector('#runMsg').textContent"));
      const b = r[0];
      await sleep(300);
      const shown = await cdp.eval("(() => { const m = (document.querySelector('#resultBox') || {}).textContent || ''; const k = m.match(/\\(limit ([0-9.]+) s\\)/); return k ? +k[1] : null; })()");
      const row = { world: c.world, planner: c.planner, preset: c.preset, fault: c.fault, filter: c.filter,
        src: c.src, browser: pick(b.score), native: c.score, same: same(b.score, c.score),
        max_time_s: { browser: b.max_time_s, source: b.max_time_source, native: c.max_time_s, shown_in_table: shown },
        browser_wall_s: b.wall_s, worker_ms: b.worker_ms, native_wall_s: c.native_wall_s, sim_s: b.sim_s };
      out.parity.push(row);
      console.log(c.world, c.planner, row.same ? "same" : "DIFF", b.wall_s, "s browser,", c.native_wall_s, "s native");
    }
    out.console = cdp.log;
  } finally {
    if (chrome) chrome.kill();
    server.kill();
  }
  const n = out.parity.filter(r => r.same).length;
  out.summary = `${n}/${out.parity.length} cases identical (browser = native)`;
  out.slow = out.parity.filter(r => r.browser_wall_s > SLOW_S).map(r => [r.world, r.planner, r.browser_wall_s]);
  out.limit_ok = out.parity.every(r => r.max_time_s.browser === r.max_time_s.native && r.max_time_s.shown_in_table === r.max_time_s.browser);
  write("playground_loop73b.json", out);
  const f = v => (v == null ? "-" : v);
  const md = [`# Playground loop-73b: maze_0 and warehouse_0 with the benchmark run time limit, browser vs native`, "",
    `\`node site/playground/results/measure_loop73b.mjs\`, ${out.date}. Input: **synthetic** (2.5D point-mass arena, preset worlds, seed 0, sensor ideal, truth pose, no filter).`,
    `Browser: ${out.chrome}, Pyodide ${out.env.pyodide} (Python ${out.env.python}, numpy ${out.env.numpy}, scipy ${out.env.scipy}). Native: ${NATIVE.native_env.python}, numpy ${NATIVE.native_env.numpy}, scipy ${NATIVE.native_env.scipy} ([native_parity.json](native_parity.json), [native_parity_loop73.json](native_parity_loop73.json)).`,
    `Host: ${out.host.cpus} CPUs, load average ${out.host.loadavg.join(" / ")} at start. Load errors in the worker: ${JSON.stringify(out.env.load_errors)}.`, "",
    `**${out.summary}.** Run time limit reported by the worker = native and shown in the score table: ${out.limit_ok ? "yes, every case" : "NO"}. Runs over ${SLOW_S} s of browser Python: ${out.slow.length ? JSON.stringify(out.slow) : "none"}.`, "",
    "| world | planner | limit s (browser / native / table) | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |",
    "|---|---|---|---|---|---|---|---|",
    ...out.parity.map(r => `| ${r.world} | ${r.planner} | ${r.max_time_s.browser} / ${r.max_time_s.native} / ${r.max_time_s.shown_in_table} | ${r.browser.outcome} / ${f(r.browser.time_to_goal_s)} / ${r.browser.min_clearance_m} / ${r.browser.path_length_m} | ${r.native.outcome} / ${f(r.native.time_to_goal_s)} / ${r.native.min_clearance_m} / ${r.native.path_length_m} | ${r.same ? "yes" : "NO"} | ${r.browser_wall_s} | ${r.native_wall_s} |`),
    "", `Console errors / warnings: ${out.console.length}`, ...out.console.map(x => "- " + x), ""];
  write("playground_loop73b.md", md.join("\n"));
  console.log(out.summary);
}

main().catch(err => { console.error(err); process.exit(1); });
