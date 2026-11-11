/* Shared top bar and footer for every site page. Plain script, no deps.
 *
 * Each page has <nav class="site-nav" id="siteNav"> with static links (the no-JS fallback).
 * This script rebuilds that list from one table so labels, groups, order and hrefs match on every
 * page: brand mark + "Navigation Index" (links Home), groups Arena (Solver, Playground, Results) and
 * Index (Search, Learn, Graph) with small group labels, the current page underlined
 * (aria-current="page"), GitHub and the theme toggle on the right, a "Menu" toggle at phone width,
 * and the shared footer (licence, cite, contribute, scope and ethics, how it was built).
 *
 * Theme: a page that has its own #themeBtn (its script redraws canvases on click) keeps it; the
 * button moves into the bar. Otherwise this script adds one. Both write localStorage
 * "navidx-theme" and set <html data-theme>; a "navidx-theme" event fires on document after a
 * toggle made here.
 *
 * Paths: the hub root is the folder above this file (this file is <root>/site/nav.js), taken from
 * document.currentScript.src. That works under any prefix: "/" on Cloudflare Pages and
 * `python3 -m http.server`, "/navigation-index/" on GitHub Pages. Hrefs are relative to the page.
 *
 * Node: module.exports exposes the pure functions for site/test_nav.mjs.
 */
(function () {
  "use strict";

  var GITHUB = "https://github.com/tp9imka/navigation-index";
  var BLOB = GITHUB + "/blob/main/";

  // key, label, target path relative to the hub root, group. Directory pages end in "/".
  var PAGES = [
    { key: "home", label: "Home", path: "", group: "" },
    { key: "solver", label: "Solver", path: "site/solver/", group: "Arena" },
    { key: "playground", label: "Playground", path: "site/playground/", group: "Arena" },
    { key: "results", label: "Results", path: "site/results.html", group: "Arena" },
    { key: "search", label: "Search", path: "site/", group: "Index" },
    { key: "learn", label: "Learn", path: "site/learn.html", group: "Index" },
    { key: "graph", label: "Graph", path: "graph/", group: "Index" },
  ];
  var GROUPS = ["Arena", "Index"];
  // Old page paths that now serve another nav entry (site/showcase.html redirects to Results).
  var ALIASES = { "site/showcase.html": "site/results.html" };

  // Footer links (spec section 4). Repo-root files open on GitHub.
  var FOOTER_NOTE = "Code Apache-2.0, docs and data CC BY 4.0";
  var FOOTER = [
    { key: "cite", label: "How to cite", href: BLOB + "CITATION.cff" },
    { key: "contribute", label: "Contribute", href: BLOB + "CONTRIBUTING.md" },
    { key: "ethics", label: "Scope and ethics", href: BLOB + "docs/export-control-and-ethics.md" },
    { key: "built", label: "How it was built", href: BLOB + "docs/how-it-was-built.md" },
  ];

  function ensureSlash(p) { return p.charAt(p.length - 1) === "/" ? p : p + "/"; }

  // Page path relative to the hub root, normalized: "index.html" dropped, pretty URLs
  // ("/site/solver", "/site/results") mapped back to the page they serve.
  function normalize(pagePath, basePath) {
    var base = ensureSlash(basePath || "/");
    var p = pagePath || "/";
    if (p + "/" === base) p = base;
    var rel = p.indexOf(base) === 0 ? p.slice(base.length) : p.replace(/^\/+/, "");
    if (/(^|\/)index\.html?$/.test(rel)) rel = rel.replace(/index\.html?$/, "");
    if (rel && rel.charAt(rel.length - 1) !== "/") {
      var targets = PAGES.map(function (pg) { return pg.path; }).concat(Object.keys(ALIASES));
      for (var i = 0; i < targets.length; i++) {
        var t = targets[i];
        if (t && t.charAt(t.length - 1) === "/" && rel + "/" === t) return t;
        if (/\.html$/.test(t) && rel === t.replace(/\.html$/, "")) return t;
      }
    }
    return rel;
  }

  function currentKey(pagePath, basePath) {
    var rel = normalize(pagePath, basePath);
    if (ALIASES[rel]) rel = ALIASES[rel];
    for (var i = 0; i < PAGES.length; i++) if (PAGES[i].path === rel) return PAGES[i].key;
    return "";
  }

  // Relative href from the page's folder to target (both relative to the hub root).
  function relativeHref(fromRel, target) {
    var fromDir = fromRel.slice(0, fromRel.lastIndexOf("/") + 1);
    var a = fromDir ? fromDir.split("/").slice(0, -1) : [];
    var b = target.split("/");
    var n = 0;
    while (n < a.length && n < b.length - 1 && a[n] === b[n]) n++;
    var up = "";
    for (var i = n; i < a.length; i++) up += "../";
    var href = up + b.slice(n).join("/");
    return href || "./";
  }

  /* Pure: the link list for a page.
   * pagePath: location.pathname of the page, e.g. "/navigation-index/site/solver/index.html".
   * basePath: pathname of the hub root, e.g. "/navigation-index/" (derived from this script's URL).
   * Returns [{key, label, group, href, current, external}]: Home first (the brand link), then the
   * grouped pages, the GitHub link last. */
  function buildNavLinks(pagePath, basePath) {
    var rel = normalize(pagePath, basePath);
    var cur = currentKey(pagePath, basePath);
    var out = PAGES.map(function (pg) {
      return { key: pg.key, label: pg.label, group: pg.group, href: relativeHref(rel, pg.path), current: pg.key === cur, external: false };
    });
    out.push({ key: "github", label: "GitHub", group: "", href: GITHUB, current: false, external: true });
    return out;
  }

  /* Pure: grouped view of buildNavLinks for rendering: [{group, links: [...]}] in GROUPS order. */
  function navGroups(pagePath, basePath) {
    var links = buildNavLinks(pagePath, basePath);
    return GROUPS.map(function (g) {
      return { group: g, links: links.filter(function (l) { return l.group === g; }) };
    });
  }

  /* Pure: footer links [{key, label, href}]. */
  function buildFooterLinks() {
    return FOOTER.map(function (f) { return { key: f.key, label: f.label, href: f.href }; });
  }

  // Hub root pathname from this script's URL: <root>/site/nav.js => <root>/.
  function baseFromScript(src) {
    var path = src.replace(/[?#].*$/, "").replace(/^[a-z]+:\/\/[^/]*/i, "");
    return path.replace(/site\/nav\.js$/, "") || "/";
  }

  var api = { PAGES: PAGES, GROUPS: GROUPS, ALIASES: ALIASES, GITHUB: GITHUB, FOOTER: FOOTER, FOOTER_NOTE: FOOTER_NOTE,
    buildNavLinks: buildNavLinks, navGroups: navGroups, buildFooterLinks: buildFooterLinks, normalize: normalize,
    currentKey: currentKey, relativeHref: relativeHref, baseFromScript: baseFromScript };

  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof document === "undefined") return;

  var script = document.currentScript;
  var base = baseFromScript(script && script.src ? script.src : "/site/nav.js");

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  function isDark() {
    var root = document.documentElement;
    return root.dataset.theme ? root.dataset.theme === "dark" : !!(window.matchMedia && matchMedia("(prefers-color-scheme: dark)").matches);
  }
  function toggleTheme() {
    var next = isDark() ? "light" : "dark";
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem("navidx-theme", next); } catch (e) { /* storage blocked */ }
    try { document.dispatchEvent(new CustomEvent("navidx-theme", { detail: next })); } catch (e) { /* old browser */ }
  }

  function renderNav() {
    var nav = document.getElementById("siteNav");
    if (!nav) return;
    var links = buildNavLinks(location.pathname, base);
    var home = links[0], gh = links[links.length - 1];
    var cur = links.filter(function (l) { return l.current; })[0];
    var top = nav.closest ? nav.closest(".top") : null;

    var brand = document.querySelector(".top .brand");
    if (brand) {
      brand.setAttribute("href", home.href); brand.setAttribute("title", "Home");
      if (!brand.querySelector(".mark")) brand.innerHTML = '<span class="mark" aria-hidden="true"></span><span class="brand-name">Navigation Index</span>';
      if (cur && cur.key === "home") brand.setAttribute("aria-current", "page");
    }

    var items = navGroups(location.pathname, base).map(function (g) {
      return '<li class="nav-grp" aria-hidden="true">' + esc(g.group) + "</li>" + g.links.map(function (l) {
        return '<li><a href="' + esc(l.href) + '"' + (l.current ? ' aria-current="page"' : "") + ">" + esc(l.label) + "</a></li>";
      }).join("");
    }).join("") + '<li class="nav-gh"><a href="' + esc(gh.href) + '" class="nav-ext" rel="noopener">GitHub</a></li>';
    nav.innerHTML =
      '<button type="button" class="nav-toggle" aria-expanded="false" aria-controls="siteNavList">' +
      '<span class="nav-toggle-label">Menu</span><span class="nav-caret" aria-hidden="true"></span>' +
      '<span class="nav-sr"> (' + esc(cur && cur.key !== "home" ? cur.label : "site") + ")</span></button>" +
      '<ul class="nav-list" id="siteNavList">' + items + "</ul>";
    nav.classList.add("nav-js");

    // Right side: GitHub link + theme toggle (the page's own #themeBtn if it has one).
    if (top && !top.querySelector(".nav-tools")) {
      var tools = document.createElement("div");
      tools.className = "nav-tools";
      tools.innerHTML = '<a class="nav-ext nav-gh-top" href="' + esc(gh.href) + '" rel="noopener">GitHub</a>';
      var own = document.getElementById("themeBtn");
      if (!own && (!cur || cur.key !== "graph")) { // the graph viewer has no light / dark override
        own = document.createElement("button");
        own.type = "button"; own.id = "themeBtn"; own.className = "icon-btn";
        own.title = "Toggle dark / light theme"; own.setAttribute("aria-label", "Toggle theme");
        own.innerHTML = "&#9680;";
        own.addEventListener("click", toggleTheme);
      }
      if (own) { own.classList.add("theme-btn"); tools.appendChild(own); }
      top.appendChild(tools);
      top.classList.add("top-js");
    }

    var btn = nav.querySelector(".nav-toggle");
    function setOpen(open, focusBtn) {
      nav.classList.toggle("open", open);
      btn.setAttribute("aria-expanded", String(open));
      if (!open && focusBtn) btn.focus();
    }
    btn.addEventListener("click", function () {
      var open = !nav.classList.contains("open");
      setOpen(open);
      if (open) { var a = nav.querySelector(".nav-list a"); if (a) a.focus(); }
    });
    nav.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape" && nav.classList.contains("open")) {
        ev.stopPropagation();
        setOpen(false, true);
      }
    });
    document.addEventListener("click", function (ev) {
      if (nav.classList.contains("open") && !nav.contains(ev.target)) setOpen(false);
    });
    nav.addEventListener("focusout", function (ev) {
      if (nav.classList.contains("open") && ev.relatedTarget && !nav.contains(ev.relatedTarget)) setOpen(false);
    });
  }

  function renderFooter() {
    if (document.querySelector(".site-foot")) return;
    var f = document.createElement("footer");
    f.className = "site-foot";
    f.innerHTML = "<span>" + esc(FOOTER_NOTE) + "</span>" + buildFooterLinks().map(function (l) {
      return '<a href="' + esc(l.href) + '" rel="noopener">' + esc(l.label) + "</a>";
    }).join("");
    document.body.appendChild(f);
  }

  function render() { renderNav(); renderFooter(); }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
})();
