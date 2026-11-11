// README hero GIF: the Home page race replay, captured in headless Chrome and assembled with ffmpeg.
// Run from the repo root (Node 22+, no npm packages): node tools/capture_hero.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...) and ffmpeg (FFMPEG=..., default
// /opt/homebrew/bin/ffmpeg). Serves the repo root with python3 -m http.server on a free port, opens
// index.html at 1200x675 (dark theme), waits for the committed race (site/solver/results/
// race_glass_office_0.json) to load, then takes FRAMES PNG screenshots spread over one replay loop
// (SPAN_S seconds of page time: the page plays the 60 s race at 4x, then holds 2.5 s). Frames go
// to a temp dir; ffmpeg builds docs/design/hero.gif (palettegen + paletteuse, WIDTH px, FPS, loop
// forever). Env overrides: FRAMES (100), SPAN_S (17), FPS (10), WIDTH (800), THEME (dark).
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import net from "node:net";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const FFMPEG = process.env.FFMPEG || "/opt/homebrew/bin/ffmpeg";
const FRAMES = Number(process.env.FRAMES || 100);
const SPAN_S = Number(process.env.SPAN_S || 17);
const FPS = Number(process.env.FPS || 10);
const WIDTH = Number(process.env.WIDTH || 800);
const THEME = process.env.THEME || "dark";
const OUT = path.join(ROOT, "docs/design/hero.gif");
const W = 1200, H = 675;
const sleep = t => new Promise(r => setTimeout(r, t));

function freePort() {
  return new Promise((ok, fail) => {
    const s = net.createServer();
    s.once("error", fail);
    s.listen(0, "127.0.0.1", () => { const { port } = s.address(); s.close(() => ok(port)); });
  });
}

// same minimal DevTools client as site/screenshots/capture_public.mjs
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
        } else if (m.method === "Runtime.exceptionThrown") this.log.push("exception: " + (m.params.exceptionDetails.exception?.description || m.params.exceptionDetails.text).slice(0, 300));
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
    if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 300));
    return r.result.value;
  }
}

async function main() {
  const [port, dbg] = [await freePort(), await freePort()];
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "hero-chrome-"));
  const frames = fs.mkdtempSync(path.join(os.tmpdir(), "hero-frames-"));
  const server = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${dbg}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", "--hide-scrollbars", `--window-size=${W},${H}`, "about:blank"], { stdio: ["ignore", "ignore", "pipe"] });
  const clocks = [];
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${dbg}/json/version`).then(r => r.json()).catch(() => null); }
    if (!version) throw new Error("Chrome did not start: " + CHROME);
    const page = (await (await fetch(`http://127.0.0.1:${dbg}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { width: W, height: H, deviceScaleFactor: 1, mobile: false });
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: THEME }, { name: "prefers-reduced-motion", value: "no-preference" }] });
    await cdp.send("Page.navigate", { url: `http://127.0.0.1:${port}/index.html` });
    // wait for the replay to start (the clock line appears once the race JSON has loaded)
    let clock = "";
    for (let i = 0; i < 100 && !/^t = /.test(clock); i++) { await sleep(100); clock = await cdp.eval("(document.getElementById('raceClock') || {}).textContent || ''"); }
    if (!/^t = /.test(clock)) throw new Error("race replay did not start; note: " + await cdp.eval("document.getElementById('raceNote').textContent"));
    // start on a fresh loop: wait until the replay clock is back near t = 0
    for (let i = 0; i < 400; i++) {
      const t = parseFloat((await cdp.eval("document.getElementById('raceClock').textContent")).slice(4));
      if (t < 1.5) break;
      await sleep(50);
    }
    const t0 = Date.now(), step = SPAN_S * 1000 / FRAMES;
    for (let k = 0; k < FRAMES; k++) {
      const wait = t0 + k * step - Date.now();
      if (wait > 0) await sleep(wait);
      const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
      fs.writeFileSync(path.join(frames, `f${String(k).padStart(4, "0")}.png`), Buffer.from(data, "base64"));
      clocks.push(await cdp.eval("document.getElementById('raceClock').textContent"));
    }
    if (cdp.log.length) console.log("page errors:\n  " + cdp.log.join("\n  "));
  } finally {
    chrome.kill(); server.kill();
  }
  const filter = `fps=${FPS},scale=${WIDTH}:-1:flags=lanczos,split[a][b];[a]palettegen=stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle`;
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  const ff = spawnSync(FFMPEG, ["-y", "-loglevel", "error", "-framerate", String(FPS), "-i", path.join(frames, "f%04d.png"),
    "-filter_complex", filter, "-loop", "0", OUT], { stdio: "inherit" });
  if (ff.status !== 0) throw new Error("ffmpeg failed with status " + ff.status);
  const mb = fs.statSync(OUT).size / 1e6;
  console.log(`frames: ${FRAMES} in ${frames} (page clock first "${clocks[0]}", middle "${clocks[Math.floor(FRAMES / 2)]}", last "${clocks[FRAMES - 1]}")`);
  console.log(`wrote ${path.relative(ROOT, OUT)}: ${mb.toFixed(2)} MB, ${WIDTH} px wide, ${FPS} fps, ${(FRAMES / FPS).toFixed(1)} s, loop forever`);
}
main().catch(err => { console.error(err); process.exit(1); });
