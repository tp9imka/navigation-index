// Shared nav (site/nav.js): hrefs from every page depth, with and without the GitHub Pages prefix.
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
const EXPECTED = {
  "index.html": { home: "./", solver: "site/solver/", playground: "site/playground/", showcase: "site/showcase.html", search: "site/", graph: "graph/" },
  "site/index.html": { home: "../", solver: "solver/", playground: "playground/", showcase: "showcase.html", search: "./", graph: "../graph/" },
  "site/showcase.html": { home: "../", solver: "solver/", playground: "playground/", showcase: "showcase.html", search: "./", graph: "../graph/" },
  "site/solver/index.html": { home: "../../", solver: "./", playground: "../playground/", showcase: "../showcase.html", search: "../", graph: "../../graph/" },
  "site/playground/index.html": { home: "../../", solver: "../solver/", playground: "./", showcase: "../showcase.html", search: "../", graph: "../../graph/" },
  "graph/index.html": { home: "../", solver: "../site/solver/", playground: "../site/playground/", showcase: "../site/showcase.html", search: "../site/", graph: "./" },
};
const KEY = { "index.html": "home", "site/index.html": "search", "site/showcase.html": "showcase",
  "site/solver/index.html": "solver", "site/playground/index.html": "playground", "graph/index.html": "graph" };

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
      ["site/showcase", "site/showcase.html"], ["graph/", "graph/index.html"],
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
  assert.deepEqual(current("/site/playground/advisor-demo.html", "/"), []);
});

test("base comes from the script URL under any prefix", () => {
  assert.equal(nav.baseFromScript("https://navigation-index.pages.dev/site/nav.js?v=1"), "/");
  assert.equal(nav.baseFromScript("https://tp9imka.github.io/navigation-index/site/nav.js?v=1"), "/navigation-index/");
  assert.equal(nav.baseFromScript("http://localhost:8000/site/nav.js"), "/");
  assert.equal(nav.baseFromScript("file:///Users/x/hub/site/nav.js"), "/Users/x/hub/");
});

test("order and labels are fixed", () => {
  assert.deepEqual(nav.buildNavLinks("/", "/").map(l => l.label),
    ["Home", "Solver", "Playground", "Showcase", "Search", "Graph", "GitHub"]);
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

test("static fallback links in each page match nav.js", () => {
  for (const page of Object.keys(EXPECTED)) {
    const html = fs.readFileSync(path.join(ROOT, page), "utf8");
    const block = html.slice(html.indexOf('id="siteNav"'), html.indexOf("</nav>", html.indexOf('id="siteNav"')));
    const got = [...block.matchAll(/<a href="([^"]+)"/g)].map(m => m[1]);
    assert.deepEqual(got, nav.buildNavLinks("/" + page, "/").map(l => l.href), page);
    assert.match(block, new RegExp(`aria-current="page">${nav.PAGES.find(p => p.key === KEY[page]).label}<`), page);
    assert.match(html, /nav\.js\?v=/, `${page} loads nav.js`);
  }
});
