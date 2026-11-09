// Check the playground Advisor on its standalone page (site/playground/advisor-demo.html) in headless Chrome.
// Run from the repo root (Node 22+, no npm packages, no network): node site/playground/results/advisor-check.mjs
// Needs Google Chrome at the macOS default path (or CHROME=...). Prints one JSON report to stdout and writes
// viewport screenshots advisor-*.png into site/playground/results/ (1280 x 900 desktop, 390 x 844 phone at 2x).
import { spawn, spawnSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "../../..");
const CHROME = process.env.CHROME || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PORT = 8771, DBG = 9341, DESK = { width: 1280, height: 900 };
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
        else if (m.method === "Network.loadingFailed") this.log.push("load failed: " + m.params.errorText);
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

async function shot(cdp, name) {
  const { data } = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  fs.writeFileSync(path.join(HERE, name), Buffer.from(data, "base64"));
  const h = spawnSync("sips", ["-g", "pixelHeight", "-g", "pixelWidth", path.join(HERE, name)], { encoding: "utf8" }).stdout;
  const ph = +(h.match(/pixelHeight: (\d+)/) || [])[1], pw = +(h.match(/pixelWidth: (\d+)/) || [])[1];
  if (!(ph <= 4000)) throw new Error(`${name} is ${ph} px tall`);
  return { file: name, width: pw, height: ph };
}

async function open(cdp, query) {
  await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/site/playground/advisor-demo.html${query}` });
  for (let i = 0; i < 80; i++) {
    await sleep(100);
    const ok = await cdp.eval("!!document.querySelector('.adv-table, .adv-note')").catch(() => false);
    if (ok) return;
  }
  throw new Error("advisor did not render for " + query);
}

const T = (name, ok, detail) => ({ name, ok: !!ok, detail });

async function main() {
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), "adv-chrome-"));
  const server = spawn("python3", ["-m", "http.server", String(PORT), "--bind", "127.0.0.1"], { cwd: ROOT, stdio: "ignore" });
  const chrome = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${DBG}`, `--user-data-dir=${profile}`,
    "--no-first-run", "--no-default-browser-check", `--window-size=${DESK.width},${DESK.height}`, "--hide-scrollbars", "about:blank"],
  { stdio: ["ignore", "ignore", "pipe"] });
  const out = { date: new Date().toISOString(), input: "synthetic", checks: [], shots: [] };
  try {
    let version = null;
    for (let i = 0; i < 120 && !version; i++) { await sleep(250); version = await fetch(`http://127.0.0.1:${DBG}/json/version`).then(r => r.json()).catch(() => null); }
    out.chrome = version.Browser;
    const page = (await (await fetch(`http://127.0.0.1:${DBG}/json/list`)).json()).find(t => t.type === "page");
    const cdp = new CDP(page.webSocketDebuggerUrl);
    await cdp.open();
    await cdp.send("Runtime.enable"); await cdp.send("Page.enable"); await cdp.send("Network.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
    const data = JSON.parse(fs.readFileSync(path.join(ROOT, "site/playground/data/advisor.json"), "utf8"));

    // 1. maze x crazyflie: recommendation text, table rows, Use this => onPick
    await open(cdp, "?family=maze&preset=crazyflie");
    const r1 = await cdp.eval(`(() => { const c = [...document.querySelectorAll('.adv-card')];
      return { cards: c.map(x => x.querySelector('.adv-win strong').textContent), rows: document.querySelectorAll('.adv-table tbody tr').length,
               firstRow: document.querySelector('.adv-table tbody tr .adv-name').textContent.trim() }; })()`);
    const R = data.recommend.maze.crazyflie;
    // a tied planner the page offers replaces a winner it does not offer (astar_mpc is not a playground option yet)
    const okCard = (g, label) => [g.winner].concat(g.ties).map(p => data.planners[p].label).includes(label);
    out.checks.push(T("maze/crazyflie cards = advisor.json winner or tie", okCard(R.prior_map, r1.cards[0]) && r1.cards[1] === data.planners[R.no_map.winner].label, r1.cards));
    out.checks.push(T("prior-map card shows an offered planner", r1.cards[0] === "A* known map", r1.cards[0]));
    out.checks.push(T("table lists all 14 planners", r1.rows === 14, r1.rows));
    const pick = await cdp.eval(`(() => { document.querySelectorAll('.adv-card')[1].querySelector('button.primary').click();
      return { log: document.querySelector('#pickLog').textContent, planner: document.querySelector('#planner').value, filter: document.querySelector('#filter').value }; })()`);
    out.checks.push(T("Use this (no map) => onPick sets planner + filter", pick.planner === "astar_unknown" && pick.filter === "F2", pick));
    await cdp.eval("document.querySelector('.adv').scrollIntoView({behavior: 'instant'}); window.scrollBy(0, -10); true");
    out.shots.push(await shot(cdp, "advisor-maze-crazyflie.png"));

    // 2. sort by collision, then reached
    const s1 = await cdp.eval(`(() => { document.querySelector('[data-sort=collision]').click();
      const v = [...document.querySelectorAll('.adv-table tbody tr')].map(r => parseFloat(r.children[4].textContent));
      return v; })()`);
    out.checks.push(T("sort by collision ascending", s1.every((v, i) => i === 0 || v >= s1[i - 1]), s1));
    const s2 = await cdp.eval(`(() => { document.querySelector('[data-sort=collision]').click();
      const v = [...document.querySelectorAll('.adv-table tbody tr')].map(r => parseFloat(r.children[4].textContent));
      return v; })()`);
    out.checks.push(T("second click sorts descending", s2.every((v, i) => i === 0 || v <= s2[i - 1]), s2));

    // 3. (i) popover with a real mouse click, Escape closes it
    await open(cdp, "?family=office&preset=crazyflie");
    const b = await cdp.eval(`(() => { const e = document.querySelector('.adv-table [data-info="planner:astar_unknown"]'); e.scrollIntoView({block: 'center', behavior: 'instant'});
      const r = e.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()`);
    for (const type of ["mousePressed", "mouseReleased"]) await cdp.send("Input.dispatchMouseEvent", { type, x: b.x, y: b.y, button: "left", clickCount: 1 });
    await sleep(150);
    const pop = await cdp.eval(`(() => { const p = document.querySelector('.adv-pop'); if (!p) return null; const r = p.getBoundingClientRect();
      return { text: p.textContent.slice(0, 600), left: r.left, right: r.right }; })()`);
    out.checks.push(T("(i) opens the planner popover", pop && pop.text.includes("A* unknown map") && pop.text.includes("Fails"), pop));
    out.shots.push(await shot(cdp, "advisor-popover.png"));
    await cdp.send("Input.dispatchKeyEvent", { type: "keyDown", key: "Escape", code: "Escape", windowsVirtualKeyCode: 27 });
    await sleep(100);
    out.checks.push(T("Escape closes the popover", await cdp.eval("!document.querySelector('.adv-pop')")));
    const fpop = await cdp.eval(`(() => { document.querySelector('[data-info="filter:F2"]').click(); const p = document.querySelector('.adv-pop'); const t = p ? p.textContent : ''; document.querySelector('.adv-x').click(); return t; })()`);
    out.checks.push(T("F2 popover shows the office line", fpop.includes("On office") && fpop.includes("A* unknown map without => with F2"), fpop.slice(0, 200)));

    // 4. custom worlds and the unbenchmarked sensor
    await open(cdp, "?family=custom:&preset=ideal");
    const c0 = await cdp.eval("({ note: document.querySelector('.adv-note').textContent, table: !!document.querySelector('.adv-table') })");
    out.checks.push(T("custom world from empty: no benchmark, no table", c0.note.includes("No benchmark for custom worlds") && !c0.table, c0));
    await open(cdp, "?family=custom:maze&preset=crazyflie_bright");
    const c1 = await cdp.eval("({ notes: [...document.querySelectorAll('.adv-note')].map(n => n.textContent), table: !!document.querySelector('.adv-table') })");
    out.checks.push(T("custom from maze + crazyflie_bright: nearest family and preset", c1.table && c1.notes.join(" ").includes("Maze") && c1.notes.join(" ").includes("Showing Crazyflie: 4 cone beams"), c1));
    out.shots.push(await shot(cdp, "advisor-custom.png"));

    // 5. live change through the picker (polling): forest ideal
    await cdp.eval("document.querySelector('#fam').value = 'forest'; document.querySelector('#preset').value = 'ideal'; true");
    await sleep(700);
    const live = await cdp.eval("document.querySelector('.adv .muted').textContent");
    out.checks.push(T("panel follows the family / sensor picker", live.includes("Forest") && live.includes("ideal"), live.slice(0, 120)));

    // 6. dark theme, warehouse x crazyflie (weak pick)
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "dark" }] });
    await open(cdp, "?family=warehouse&preset=crazyflie");
    const dk = await cdp.eval("({ bg: getComputedStyle(document.querySelector('.adv')).backgroundColor, weak: !!document.querySelector('.adv-card .adv-warn') })");
    out.checks.push(T("dark theme panel + weak-pick warning", dk.bg === "rgb(29, 29, 27)" && dk.weak, dk));
    await cdp.eval("document.querySelector('.adv').scrollIntoView({behavior: 'instant'}); true");
    out.shots.push(await shot(cdp, "advisor-warehouse-dark.png"));

    // 7. phone 390 px
    await cdp.send("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
    await cdp.send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: false });
    await open(cdp, "?family=maze&preset=ideal");
    // showcase.css hides page-level x overflow, so measure the panel itself: nothing outside the table's own scroller
    // may stick out past the viewport.
    const ph = await cdp.eval(`(() => { const cw = document.documentElement.clientWidth; let maxRight = 0;
      for (const e of document.querySelectorAll('.adv *')) { if (e.closest('.adv-scroll')) continue; maxRight = Math.max(maxRight, e.getBoundingClientRect().right); }
      const sc = document.querySelector('.adv-scroll').getBoundingClientRect();
      return { cw, maxRight: Math.round(maxRight), scrollerRight: Math.round(sc.right) }; })()`);
    out.checks.push(T("390 px: panel fits the viewport (table scrolls inside its box)", ph.maxRight <= ph.cw && ph.scrollerRight <= ph.cw, ph));
    await cdp.eval("document.querySelector('.adv-recs').scrollIntoView({behavior: 'instant'}); true");
    out.shots.push(await shot(cdp, "advisor-phone-390.png"));
    await cdp.eval("document.querySelector('.adv-table').scrollIntoView({behavior: 'instant'}); true");
    const pb = await cdp.eval(`(() => { const e = document.querySelector('.adv-table [data-info]'); e.scrollIntoView({block: 'center', behavior: 'instant'}); const r = e.getBoundingClientRect(); const h = document.elementFromPoint(r.left + 9, r.top + 9); return { x: r.left + 9, y: r.top + 9, hit: h && h.outerHTML.slice(0, 80) }; })()`);
    out.phone_click = pb;
    for (const type of ["mousePressed", "mouseReleased"]) await cdp.send("Input.dispatchMouseEvent", { type, x: pb.x, y: pb.y, button: "left", clickCount: 1 });
    await sleep(150);
    const pp = await cdp.eval("(() => { const p = document.querySelector('.adv-pop'); if (!p) return null; const r = p.getBoundingClientRect(); return { left: r.left, right: r.right }; })()");
    out.checks.push(T("390 px: popover inside the viewport", pp && pp.left >= 0 && pp.right <= 390, pp));
    out.shots.push(await shot(cdp, "advisor-phone-390-popover.png"));

    out.console = cdp.log.slice();
    out.checks.push(T("no console errors or exceptions", cdp.log.length === 0, cdp.log));

    // 8. the wiring from ADVISOR.md, injected into the real playground page (index.html and playground.js unchanged).
    // Pyodide may load or fail in the background; only the editor, presets and config selects are used here.
    await cdp.send("Emulation.setDeviceMetricsOverride", { ...DESK, deviceScaleFactor: 1, mobile: false });
    await cdp.send("Page.navigate", { url: `http://127.0.0.1:${PORT}/site/playground/index.html` });
    for (let i = 0; i < 100; i++) { await sleep(100); if (await cdp.eval("typeof PG === 'object' && document.querySelectorAll('#presetSel option').length > 2").catch(() => false)) break; }
    await cdp.eval(`new Promise((ok, fail) => {
      const l = document.createElement('link'); l.rel = 'stylesheet'; l.href = 'advisor.css'; document.head.appendChild(l);
      document.querySelector('main').insertAdjacentHTML('beforeend', '<div id="advisorBox"></div>');
      const s = document.createElement('script'); s.src = 'advisor.js'; s.onload = ok; s.onerror = fail; document.head.appendChild(s); })`);
    const WIRE = fs.readFileSync(path.join(HERE, "..", "ADVISOR.md"), "utf8").match(/<!-- wire-js -->\s*```js\n([\s\S]*?)```/)[1];
    await cdp.eval(WIRE + "; true");
    await cdp.eval("PG.loadPreset('maze_0')");
    await cdp.eval("document.querySelector('#A_preset').value = 'crazyflie'; true");
    await sleep(700);
    const w1 = await cdp.eval("document.querySelector('#advisorBox .adv .muted').textContent");
    out.checks.push(T("playground wiring: panel shows the loaded preset family and sensor", w1.includes("Maze") && w1.includes("Crazyflie"), w1.slice(0, 120)));
    const w2 = await cdp.eval(`(() => { document.querySelectorAll('#advisorBox .adv-card')[1].querySelector('button.primary').click();
      return { planner: document.querySelector('#A_planner').value, filter: document.querySelector('#A_filter').value }; })()`);
    out.checks.push(T("playground wiring: Use this sets Config A planner and filter", w2.planner === "astar_unknown" && w2.filter === "F2", w2));
    await cdp.eval("PG.addObstacle({type: 'box', cx: 5, cy: 5, hx: 0.3, hy: 0.3}); true");
    await sleep(700);
    const w3 = await cdp.eval("document.querySelector('#advisorBox .adv-note') && document.querySelector('#advisorBox .adv-note').textContent");
    out.checks.push(T("playground wiring: an edited preset shows the custom-world note", w3 && w3.includes("No benchmark for custom worlds") && w3.includes("Maze"), w3));
    await cdp.eval("document.querySelector('#advisorBox').scrollIntoView({behavior: 'instant'}); true");
    out.shots.push(await shot(cdp, "advisor-in-playground.png"));
  } finally {
    chrome.kill(); server.kill();
  }
  out.pass = out.checks.filter(c => c.ok).length + " / " + out.checks.length;
  console.log(JSON.stringify(out, null, 1));
  if (out.checks.some(c => !c.ok)) process.exitCode = 1;
}
main().catch(e => { console.error(e); process.exit(1); });
