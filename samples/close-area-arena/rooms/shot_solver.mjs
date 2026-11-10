// Import the room worlds into the Solver through its "Import world JSON" file input (headless Chrome,
// CDP DOM.setFileInputFiles), read the page's message, take one viewport screenshot.
// Run from the repo root (Node 22+, no npm packages): node samples/close-area-arena/rooms/shot_solver.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...). Writes results/room_in_solver.png and
// results/room_in_solver.json. No sweep is run.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ARENA = path.resolve(HERE, "..");
const ROOT = path.resolve(ARENA, "../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8793, DBG = 9363, VIEW = { width: 1280, height: 900 };
const sleep = t => new Promise(r => setTimeout(r, t));

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
        } else if (m.method === "Runtime.exceptionThrown") this.log.push("exception: " + JSON.stringify(m.params.exceptionDetails).slice(0, 400));
        else if (m.method === "Runtime.consoleAPICalled" && ["error", "warning"].includes(m.params.type))
          this.log.push(m.params.type + ": " + m.params.args.map(a => a.value || a.description).join(" ").slice(0, 400));
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
    if (r.exceptionDetails) throw new Error("eval failed: " + JSON.stringify(r.exceptionDetails).slice(0, 400));
    return r.result.value;
  }
}

async function importFile(cdp, file) {
  const { root } = await cdp.send("DOM.getDocument", { depth: -1 });
  const { nodeId } = await cdp.send("DOM.querySelector", { nodeId: root.nodeId, selector: "#fileIn" });
  await cdp.send("DOM.setFileInputFiles", { nodeId, files: [file] });
  for (let i = 0; i < 40; i++) {
    await sleep(250);
    const msg = await cdp.eval(`document.querySelector("#worldMsg").textContent`);
    if (msg.includes(path.basename(file))) return msg;
  }
  return await cdp.eval(`document.querySelector("#worldMsg").textContent`);
}

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "room-solver-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", `--window-size=${VIEW.width},${VIEW.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", page: `http://127.0.0.1:${PORT}/site/solver/` };
  try {
    let version = null;
    for (let i = 0; i < 240 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser;
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable"); await cdp.send("DOM.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...VIEW, deviceScaleFactor: 1, mobile: false });
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
    await cdp.send("Page.navigate", { url: out.page });
    // wait until the default preset has loaded, so it cannot overwrite the import
    for (let i = 0; i < 120; i++) {
      await sleep(250);
      const ready = await cdp.eval(`document.querySelector("#presetSel").options.length > 1 && document.querySelector("#worldMsg").textContent.length > 0`).catch(() => false);
      if (ready) break;
    }
    out.imports = [];
    for (const f of ["hall_8x6.world.json", "sketch_hall.world.json"]) {
      const msg = await importFile(cdp, path.join(HERE, f));
      const cls = await cdp.eval(`document.querySelector("#worldMsg").className`);
      out.imports.push({ file: f, message: msg, ok: msg.startsWith("Imported") && cls.includes("ok") });
    }
    await sleep(500);
    await cdp.eval(`(() => { const e = document.querySelector(".sv-grid"); window.scrollTo({ top: e.getBoundingClientRect().top + window.scrollY - 16, behavior: "instant" }); return true; })()`);
    await sleep(300);
    const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
    fs.writeFileSync(path.join(ARENA, "results", "room_in_solver.png"), Buffer.from(data, "base64"));
    out.screenshot = "results/room_in_solver.png (viewport 1280 x 900, after importing sketch_hall.world.json)";
    out.console = cdp.log;
  } finally {
    chrome.kill(); server.kill();
    await sleep(1500);                       // Chrome writes its profile while exiting
    try { fs.rmSync(profile, { recursive: true, force: true, maxRetries: 5, retryDelay: 300 }); } catch { /* temp dir, ignore */ }
  }
  fs.writeFileSync(path.join(ARENA, "results", "room_in_solver.json"), JSON.stringify(out, null, 1) + "\n");
  console.log(JSON.stringify(out, null, 1));
  process.exit(out.imports.every(r => r.ok) ? 0 : 1);
}

main().catch(e => { console.error(e); process.exit(1); });
