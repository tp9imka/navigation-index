// Headless dashboard capture over the Chrome DevTools protocol (Node 22+). Copy of samples/golden-demo/screenshot.mjs with the debug port from CDP_PORT.
//   node screenshot.mjs <url> <out.jpg> [chrome path]
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [url, out, chromePath = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'] = process.argv.slice(2);
const DEBUG_PORT = Number(process.env.CDP_PORT || 15802);
const WIDTH = 1440, HEIGHT = 900;
const SETTLE_MS = 6000;
const TIMEOUT_MS = 60000;

const profile = mkdtempSync(join(tmpdir(), 'px4golden-chrome-'));
const chrome = spawn(chromePath, ['--headless=new', '--use-angle=swiftshader', '--enable-unsafe-swiftshader',
  `--remote-debugging-port=${DEBUG_PORT}`, `--user-data-dir=${profile}`, `--window-size=${WIDTH},${HEIGHT}`,
  '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const done = (code) => { chrome.kill(); setTimeout(() => { rmSync(profile, { recursive: true, force: true }); process.exit(code); }, 500); };
setTimeout(() => { console.error('timeout'); done(1); }, TIMEOUT_MS);

let targets;
for (let i = 0; i < 50 && !targets; i++) {
  await sleep(200);
  try { targets = await (await fetch(`http://127.0.0.1:${DEBUG_PORT}/json`)).json(); } catch { /* not up yet */ }
}
const ws = new WebSocket(targets.find((t) => t.type === 'page').webSocketDebuggerUrl);
await new Promise((r) => ws.addEventListener('open', r));
let id = 0;
const pending = new Map();
ws.addEventListener('message', (e) => {
  const m = JSON.parse(e.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  if (m.method === 'Runtime.exceptionThrown') console.error('page exception:', m.params.exceptionDetails.text);
});
const send = (method, params = {}) => new Promise((r) => { const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });

await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', { width: WIDTH, height: HEIGHT, deviceScaleFactor: 1, mobile: false });
await send('Page.navigate', { url });
for (let i = 0; i < 100; i++) {
  await sleep(200);
  const r = await send('Runtime.evaluate', { expression: '!!(window.navdash && window.navdash.tracks && window.navdash.tracks.length)', returnByValue: true });
  if (r.result?.result?.value) break;
}
await sleep(SETTLE_MS);
const panel = await send('Runtime.evaluate', { expression: 'document.querySelector("#metrics, .metrics, aside")?.innerText || ""', returnByValue: true });
console.log((panel.result?.result?.value || '').replace(/\n+/g, ' | '));
const shot = await send('Page.captureScreenshot', { format: 'jpeg', quality: 80 });
writeFileSync(out, Buffer.from(shot.result.data, 'base64'));
console.log(out);
done(0);
