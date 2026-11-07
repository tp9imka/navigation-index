"use strict";

// Stdlib-only behavior checks for the actual browser code. The small document adapter
// supplies event-registration/render targets; filtering and serialization run unchanged.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const { test } = require("node:test");
const { execFileSync } = require("node:child_process");

function browser() {
  const targets = new Map();
  const events = {};
  const context = vm.createContext({
    URLSearchParams, URL, console,
    location: { hash: "", pathname: "/site/", search: "" },
    document: {
      querySelector(selector) {
        if (!targets.has(selector)) targets.set(selector, { value: "", innerHTML: "", addEventListener() {} });
        return targets.get(selector);
      },
      addEventListener(name, callback) { (events[name] ||= []).push(callback); },
    },
    window: { addEventListener() {} },
  });
  const source = fs.readFileSync(path.join(__dirname, "app.js"), "utf8");
  // Loading data is the only operation omitted. Tests supply complete records locally.
  vm.runInContext(source.replace(/\nload\(\);\s*$/, "\n"), context);
  return {
    run: code => vm.runInContext(code, context),
    value: code => JSON.parse(vm.runInContext(`JSON.stringify(${code})`, context)),
    targets,
    events,
    context,
  };
}

test("typing a budget updates the active filter without requiring blur", () => {
  const b = browser();
  b.run('commitSearch = () => {};');
  const target = {dataset: {budget: 'max_download_mb'}, value: '100'};
  for (const callback of b.events.input || []) callback({target});
  assert.equal(b.run('S.b.max_download_mb'), '100');
  target.value = '';
  for (const callback of b.events.input || []) callback({target});
  assert.equal(b.run('S.b.max_download_mb'), undefined);
});

const FIXTURES = [
  { i: "sample:replay", k: "sample", n: "Receiver replay", s: "Receiver log replay", p: "catalog/replay.md", sd: "replay", vs: "ran", v: "Ran locally on recorded data.",
    rd: { compute: "cpu", hardware: "none", offline: "verified", setup_minutes: 0, download_mb: 0, platforms: ["macos-arm64"], validation: "integrated", limitation: "Replay only; live receiver behavior is untested.", evidence: ["samples/replay/README.md"] } },
  { i: "sample:visual", k: "sample", n: "Visual localization", s: "Cached image matching", p: "catalog/visual.md", sd: "visual", vs: "partial", v: "Components tested; full integration untested.",
    rd: { compute: "optional-gpu", hardware: "optional", offline: "cache-required", setup_minutes: 30, download_mb: 250, platforms: ["linux-amd64"], validation: "components", limitation: "Model weights must be cached before disconnecting.", evidence: [] } },
  { i: "sample:unknown", k: "sample", n: "Unmeasured kit", s: "Setup not measured", p: "catalog/unknown.md", sd: "unknown", vs: "sketch", v: "Not run.",
    rd: { compute: "unknown", hardware: "unknown", offline: "unknown", setup_minutes: null, download_mb: null, platforms: [], validation: "unverified", limitation: "The full workflow has not been run.", evidence: [] } },
  { i: "repo:other", k: "repo", n: "Other project", s: "Readiness not recorded", p: "catalog/other.md" },
];

function withFixtures() {
  const b = browser();
  b.context.fixtures = JSON.parse(JSON.stringify(FIXTURES));
  b.run("E = fixtures; E.forEach((e, x) => { e.x = x; byId.set(e.i, e); }); RK = buildRanker(E);");
  return b;
}

test("unset constraints retain records with unknown readiness", () => {
  const b = withFixtures();
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:replay", "sample:visual", "sample:unknown", "repo:other"]);
});

test("verified offline and exact readiness choices exclude unknown or different requirements", () => {
  const b = withFixtures();
  b.run('S.f = { offline: new Set(["verified"]) };');
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:replay"]);
  b.run('S.f = { compute: new Set(["optional-gpu"]), hardware: new Set(["optional"]), validation: new Set(["components"]) };');
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:visual"]);
  b.run('S.f = { compute: new Set(["unknown"]) };');
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:unknown", "repo:other"]);
});

test("tested platform matches an exact label and never assumes an untested platform", () => {
  const b = withFixtures();
  b.run('S.f = { platform: new Set(["macos-arm64"]) };');
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:replay"]);
  b.run('S.f = { platform: new Set(["macos"]) };');
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), []);
});

test("budget ceilings include the boundary and zero but exclude missing or malformed measurements", () => {
  const b = withFixtures();
  b.context.location.hash = "#max_setup_minutes=30&max_download_mb=250";
  b.run("readHash();");
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:replay", "sample:visual"]);
  b.context.location.hash = "#max_setup_minutes=0&max_download_mb=0";
  b.run("readHash();");
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:replay"]);
  b.run('E[0].rd.setup_minutes = "0";');
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), []);
});

test("readiness, platform, concept and budget constraints combine", () => {
  const b = withFixtures();
  b.context.location.hash = "#compute=cpu&offline=verified&platform=macos-arm64&max_download_mb=0";
  b.run("readHash();");
  assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), ["sample:replay"]);
  assert.deepEqual(b.value('E.filter(e => passes(e, null, new Set(["concept:vio"]))).map(e => e.i)'), []);
});

test("saved constraints round-trip and copy identical CLI and MCP arguments without a text query", () => {
  const b = withFixtures();
  b.context.location.hash = "#kind=sample&compute=cpu&hardware=none&offline=verified&platform=macos-arm64&validation=integrated&max_setup_minutes=0&max_download_mb=12.5";
  b.run("readHash(); location.hash = '#' + searchHash(); readHash();");
  const expected = { query: "", kind: "sample", compute: "cpu", hardware: "none", offline: "verified", platform: "macos-arm64", validation: "integrated", max_setup_minutes: 0, max_download_mb: 12.5 };
  assert.deepEqual(b.value("mcpSearch()"), { tool: "search", arguments: expected });
  const argv = JSON.parse(execFileSync("python3", ["-c", "import json,shlex,sys; print(json.dumps(shlex.split(sys.stdin.read())))"], { input: b.value("cliSearch()"), encoding: "utf8" }));
  assert.deepEqual(argv, ["python3", "tools/query.py", "search", "", "--kind", "sample", "--compute", "cpu", "--hardware", "none", "--offline", "verified", "--platform", "macos-arm64", "--validation", "integrated", "--max-setup-minutes", "0", "--max-download-mb", "12.5"]);
  const hash = new URLSearchParams(b.value("searchHash()"));
  assert.equal(hash.get("max_setup_minutes"), "0");
  assert.equal(hash.get("platform"), "macos-arm64");
  assert.equal(b.value("dropped()"), "");
});

test("copied concept searches retain readiness and shell-sensitive query text stays literal", () => {
  const b = withFixtures();
  b.context.location.hash = "#concept=concept%3Avio&offline=cache-required&max_setup_minutes=30";
  b.run("readHash();");
  assert.deepEqual(b.value("mcpSearch()"), { tool: "concept", arguments: { id: "concept:vio", offline: "cache-required", max_setup_minutes: 30 } });
  const query = "road $(touch /tmp/never-run) `echo no` 'quote'";
  b.context.queryText = query;
  b.run("S.q = queryText;");
  const argv = JSON.parse(execFileSync("python3", ["-c", "import json,shlex,sys; print(json.dumps(shlex.split(sys.stdin.read())))"], { input: b.value("cliSearch()"), encoding: "utf8" }));
  assert.equal(argv[3], query);
  assert.ok(b.value("cliSearch()").startsWith("python3 tools/query.py search 'road $"));
});

test("invalid saved budgets show no matches and cannot copy a misleading unconstrained query", () => {
  const b = withFixtures();
  for (const raw of ["-1", "NaN", "Infinity", "bad"]) {
    b.context.location.hash = "#q=replay&max_setup_minutes=" + raw;
    b.run("readHash();");
    assert.deepEqual(b.value("E.filter(e => passes(e)).map(e => e.i)"), []);
    assert.equal(b.value("mcpSearch()"), null);
  }
});

test("cards and starter kits show limitations, unknown measurements and tested platform evidence", () => {
  const b = withFixtures();
  const card = b.value("card(E[0], 0)");
  assert.match(card, /Replay only; live receiver behavior is untested\./);
  assert.match(card, /macos-arm64/);
  assert.match(card.replace(/<[^>]*>/g, " ").replace(/\s+/g, " "), /Dataset download 0 MB/);
  const unknown = b.value("card(E[2], 2)");
  assert.match(unknown.replace(/<[^>]*>/g, " ").replace(/\s+/g, " "), /Setup unknown/);
  assert.match(unknown, /No tested platform recorded/);
  b.run("renderKits();");
  assert.match(b.targets.get("#kits").innerHTML, /The full workflow has not been run\./);
  assert.match(b.targets.get("#kits").innerHTML, /Model weights must be cached before disconnecting\./);
});
