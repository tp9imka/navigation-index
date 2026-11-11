// Browser = native check for the planners added on 2026-11-10 (Theta* / Lazy Theta*, MPPI, Hybrid A*).
// Same CDP recipe as measure_playground.mjs (copied, that file is not imported). Run from the repo root
// (Node 22+, no npm packages), after native_parity_loop73.py:
//   samples/close-area-arena/.venv/bin/python site/playground/results/native_parity_loop73.py
//   node site/playground/results/measure_loop73.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and network access to cdn.jsdelivr.net.
// Writes site/playground/results/playground_loop73.json and playground_loop73.md.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8776, DBG = 9344, DESK = { width: 1280, height: 900 };
const SLOW_S = 60;                         // a planner slower than this per run stays out of the playground list
const sleep = t => new Promise(r => setTimeout(r, t));
const write = (name, data) => fs.writeFileSync(path.join(HERE, name), typeof data === "string" ? data : JSON.stringify(data, null, 1) + "\n");
const NATIVE = JSON.parse(fs.readFileSync(path.join(HERE, "native_parity_loop73.json"), "utf8"));
const KEYS = NATIVE.keys;

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
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "pg73-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  let chrome = null;
  const out = { date: new Date().toISOString(), input: "synthetic", page: `http://127.0.0.1:${PORT}/site/playground/index.html?pyodide=cdn`,
    native: "native_parity_loop73.json", host: { cpus: os.cpus().length, loadavg: os.loadavg().map(x => Math.round(x * 10) / 10) } };
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
      const r = await cdp.eval(`PG.run([${JSON.stringify(cfg)}]).then(x => x && x.map(y => ({score: y.score, wall_s: y.wall_s, sim_s: y.sim_s, worker_ms: y.worker_ms})))`);
      if (!r) throw new Error("run failed for " + JSON.stringify(c) + " " + await cdp.eval("document.querySelector('#runMsg').textContent"));
      const b = r[0];
      const row = { world: c.world, planner: c.planner, preset: c.preset, fault: c.fault, filter: c.filter,
        browser: pick(b.score), native: c.score, same: same(b.score, c.score),
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
  write("playground_loop73.json", out);
  const f = v => (v == null ? "-" : v);
  const md = [`# Playground: new planners, browser vs native`, "",
    `\`node site/playground/results/measure_loop73.mjs\`, ${out.date}. Input: **synthetic** (2.5D point-mass arena, preset worlds, seed 0, sensor ideal, truth pose, no filter).`,
    `Browser: ${out.chrome}, Pyodide ${out.env.pyodide} (Python ${out.env.python}, numpy ${out.env.numpy}, scipy ${out.env.scipy}). Native: ${NATIVE.native_env.python}, numpy ${NATIVE.native_env.numpy}, scipy ${NATIVE.native_env.scipy} ([native_parity_loop73.json](native_parity_loop73.json)).`,
    `Host: ${out.host.cpus} CPUs, load average ${out.host.loadavg.join(" / ")} at start. Load errors in the worker: ${JSON.stringify(out.env.load_errors)}.`, "",
    `**${out.summary}.** Runs over ${SLOW_S} s of browser Python: ${out.slow.length ? JSON.stringify(out.slow) : "none"}.`, "",
    "| world | planner | browser outcome / time to goal s / min clearance m / path m | native | same | browser Python s | native Python s |",
    "|---|---|---|---|---|---|---|",
    ...out.parity.map(r => `| ${r.world} | ${r.planner} | ${r.browser.outcome} / ${f(r.browser.time_to_goal_s)} / ${r.browser.min_clearance_m} / ${r.browser.path_length_m} | ${r.native.outcome} / ${f(r.native.time_to_goal_s)} / ${r.native.min_clearance_m} / ${r.native.path_length_m} | ${r.same ? "yes" : "NO"} | ${r.browser_wall_s} | ${r.native_wall_s} |`),
    "", `Console errors / warnings: ${out.console.length}`, ...out.console.map(x => "- " + x), ""];
  write("playground_loop73.md", md.join("\n"));
  console.log(out.summary);
}

main().catch(err => { console.error(err); process.exit(1); });
