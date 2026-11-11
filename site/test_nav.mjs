// Shared nav (site/nav.js): grouped links and hrefs from every page depth, with and without the
// GitHub Pages prefix, and the injected footer.
// Run: node --test site/test_nav.mjs
import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const nav = require("./nav.js");
const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, "..");

const hrefs = (page, base) => Object.fromEntries(nav.buildNavLinks(page, base).map(l => [l.key, l.href]));
const current = (page, base) => nav.buildNavLinks(page, base).filter(l => l.current).map(l => l.key);

// Expected relative hrefs per page (keyed by the page path below the hub root).
const SITE = { home: "../", solver: "solver/", playground: "playground/", results: "results.html", search: "./", learn: "learn.html", graph: "../graph/" };
const EXPECTED = {
  "index.html": { home: "./", solver: "site/solver/", playground: "site/playground/", results: "site/results.html", search: "site/", learn: "site/learn.html", graph: "graph/" },
  "site/index.html": SITE,
  "site/results.html": SITE,
  "site/learn.html": SITE,
  "site/showcase.html": SITE,
  "site/solver/index.html": { home: "../../", solver: "./", playground: "../playground/", results: "../results.html", search: "../", learn: "../learn.html", graph: "../../graph/" },
  "site/playground/index.html": { home: "../../", solver: "../solver/", playground: "./", results: "../results.html", search: "../", learn: "../learn.html", graph: "../../graph/" },
  "graph/index.html": { home: "../", solver: "../site/solver/", playground: "../site/playground/", results: "../site/results.html", search: "../site/", learn: "../site/learn.html", graph: "./" },
};
const KEY = { "index.html": "home", "site/index.html": "search", "site/results.html": "results", "site/learn.html": "learn",
  "site/showcase.html": "results", "site/solver/index.html": "solver", "site/playground/index.html": "playground", "graph/index.html": "graph" };
// Pages whose static fallback nav must match nav.js. site/showcase.html is a redirect stub without a
// nav; graph/index.html is a generated-tree file outside this wave (its fallback is listed as a driver edit).
const FALLBACK_PAGES = ["index.html", "site/index.html", "site/results.html", "site/learn.html",
  "site/solver/index.html", "site/playground/index.html"];

for (const base of ["/", "/navigation-index/"]) {
  test(`hrefs and current page from every depth, base ${base}`, () => {
    for (const [page, want] of Object.entries(EXPECTED)) {
      const got = hrefs(base + page, base);
      for (const [k, v] of Object.entries(want)) assert.equal(got[k], v, `${base}${page} => ${k}`);
      assert.equal(got.github, nav.GITHUB);
      assert.deepEqual(current(base + page, base), [KEY[page]], `${base}${page} current`);
    }
  });

  test(`directory and pretty URLs map to the same page, base ${base}`, () => {
    const same = [
      ["", "index.html"], ["site/", "site/index.html"], ["site/solver/", "site/solver/index.html"],
      ["site/solver", "site/solver/index.html"], ["site/playground", "site/playground/index.html"],
      ["site/results", "site/results.html"], ["site/learn", "site/learn.html"], ["site/showcase", "site/showcase.html"],
      ["graph/", "graph/index.html"],
    ];
    for (const [alias, page] of same) {
      assert.deepEqual(hrefs(base + alias, base), hrefs(base + page, base), `${base}${alias}`);
      assert.deepEqual(current(base + alias, base), [KEY[page]], `${base}${alias} current`);
    }
  });
}

test("GitHub Pages root without trailing slash is Home", () => {
  assert.deepEqual(current("/navigation-index", "/navigation-index/"), ["home"]);
  assert.equal(hrefs("/navigation-index", "/navigation-index/").solver, "site/solver/");
});

test("non-nav pages get working hrefs and no current link", () => {
  const got = hrefs("/navigation-index/site/playground/advisor-demo.html", "/navigation-index/");
  assert.equal(got.home, "../../");
  assert.equal(got.solver, "../solver/");
  assert.equal(got.results, "../results.html");
  assert.deepEqual(current("/site/playground/advisor-demo.html", "/"), []);
});

test("base comes from the script URL under any prefix", () => {
  assert.equal(nav.baseFromScript("https://navigation-index.pages.dev/site/nav.js?v=1"), "/");
  assert.equal(nav.baseFromScript("https://tp9imka.github.io/navigation-index/site/nav.js?v=1"), "/navigation-index/");
  assert.equal(nav.baseFromScript("http://localhost:8000/site/nav.js"), "/");
  assert.equal(nav.baseFromScript("file:///Users/x/hub/site/nav.js"), "/Users/x/hub/");
});

test("order, labels and groups are fixed", () => {
  assert.deepEqual(nav.buildNavLinks("/", "/").map(l => l.label),
    ["Home", "Solver", "Playground", "Results", "Search", "Learn", "Graph", "GitHub"]);
  assert.deepEqual(nav.navGroups("/", "/").map(g => [g.group, g.links.map(l => l.label)]),
    [["Arena", ["Solver", "Playground", "Results"]], ["Index", ["Search", "Learn", "Graph"]]]);
});

test("footer links: licence line, cite, contribute, scope and ethics, how it was built", () => {
  assert.equal(nav.FOOTER_NOTE, "Code Apache-2.0, docs and data CC BY 4.0");
  const f = nav.buildFooterLinks();
  assert.deepEqual(f.map(l => l.label), ["How to cite", "Contribute", "Scope and ethics", "How it was built"]);
  const blob = nav.GITHUB + "/blob/main/";
  assert.deepEqual(f.map(l => l.href.replace(blob, "")),
    ["CITATION.cff", "CONTRIBUTING.md", "docs/export-control-and-ethics.md", "docs/how-it-was-built.md"]);
  // the one footer target that exists before waves 2 and 4 must exist now
  assert.ok(fs.existsSync(path.join(ROOT, "docs/export-control-and-ethics.md")));
});

test("every href resolves to a file in the repo", () => {
  for (const page of Object.keys(EXPECTED)) {
    for (const l of nav.buildNavLinks("/" + page, "/")) {
      if (l.external) continue;
      let p = path.join(ROOT, path.dirname(page), l.href);
      if (l.href.endsWith("/") || l.href === "./") p = path.join(p, "index.html");
      assert.ok(fs.existsSync(p), `${page} => ${l.href} (${p})`);
    }
  }
});

test("static fallback links in each page match nav.js (Home is the brand link)", () => {
  for (const page of FALLBACK_PAGES) {
    const html = fs.readFileSync(path.join(ROOT, page), "utf8");
    const block = html.slice(html.indexOf('id="siteNav"'), html.indexOf("</nav>", html.indexOf('id="siteNav"')));
    const got = [...block.matchAll(/<a href="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(got, nav.buildNavLinks("/" + page, "/").filter(l => l.key !== "home").map(l => l.href), page);
    const brand = html.match(/<a class="brand" href="([^"]+)"/);
    assert.ok(brand, `${page} has a brand link`);
    assert.equal(brand[1], hrefs("/" + page, "/").home, `${page} brand => Home`);
    if (KEY[page] !== "home") {
      assert.match(block, new RegExp(`aria-current="page">${nav.PAGES.find(p => p.key === KEY[page]).label}<`), page);
    }
    for (const g of nav.GROUPS) assert.match(block, new RegExp(`class="nav-grp"[^>]*>${g}<`), `${page} group ${g}`);
    assert.match(html, /nav\.js\?v=/, `${page} loads nav.js`);
  }
});

test("showcase.html is a redirect stub to results.html", () => {
  const html = fs.readFileSync(path.join(ROOT, "site/showcase.html"), "utf8");
  assert.match(html, /<meta http-equiv="refresh" content="0; url=results\.html"/);
  assert.match(html, /<a href="results\.html">/);
});
