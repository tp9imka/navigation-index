/* Shared top nav for every site page. Plain script, no deps.
 *
 * Each page has <nav class="site-nav" id="siteNav"> with static links (the no-JS fallback).
 * This script rebuilds that list from one table so labels, order and hrefs match on every page,
 * marks the current page with aria-current="page", points the brand link at Home and adds a
 * compact "Menu" toggle for phone width (styles in nav.css).
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

  // key, label, target path relative to the hub root. Directory pages end in "/".
  var PAGES = [
    { key: "home", label: "Home", path: "" },
    { key: "solver", label: "Solver", path: "site/solver/" },
    { key: "playground", label: "Playground", path: "site/playground/" },
    { key: "showcase", label: "Showcase", path: "site/showcase.html" },
    { key: "search", label: "Search", path: "site/" },
    { key: "graph", label: "Graph", path: "graph/" },
  ];

  function ensureSlash(p) { return p.charAt(p.length - 1) === "/" ? p : p + "/"; }

  // Page path relative to the hub root, normalized: "index.html" dropped, pretty URLs
  // ("/site/solver", "/site/showcase") mapped back to the page they serve.
  function normalize(pagePath, basePath) {
    var base = ensureSlash(basePath || "/");
    var p = pagePath || "/";
    if (p + "/" === base) p = base;
    var rel = p.indexOf(base) === 0 ? p.slice(base.length) : p.replace(/^\/+/, "");
    if (/(^|\/)index\.html?$/.test(rel)) rel = rel.replace(/index\.html?$/, "");
    if (rel && rel.charAt(rel.length - 1) !== "/") {
      for (var i = 0; i < PAGES.length; i++) {
        var t = PAGES[i].path;
        if (t && t.charAt(t.length - 1) === "/" && rel + "/" === t) return t;
        if (/\.html$/.test(t) && rel === t.replace(/\.html$/, "")) return t;
      }
    }
    return rel;
  }

  function currentKey(pagePath, basePath) {
    var rel = normalize(pagePath, basePath);
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
   * Returns [{key, label, href, current, external}], the GitHub link last. */
  function buildNavLinks(pagePath, basePath) {
    var rel = normalize(pagePath, basePath);
    var cur = currentKey(pagePath, basePath);
    var out = PAGES.map(function (pg) {
      return { key: pg.key, label: pg.label, href: relativeHref(rel, pg.path), current: pg.key === cur, external: false };
    });
    out.push({ key: "github", label: "GitHub", href: GITHUB, current: false, external: true });
    return out;
  }

  // Hub root pathname from this script's URL: <root>/site/nav.js => <root>/.
  function baseFromScript(src) {
    var path = src.replace(/[?#].*$/, "").replace(/^[a-z]+:\/\/[^/]*/i, "");
    return path.replace(/site\/nav\.js$/, "") || "/";
  }

  var api = { PAGES: PAGES, GITHUB: GITHUB, buildNavLinks: buildNavLinks, normalize: normalize,
    currentKey: currentKey, relativeHref: relativeHref, baseFromScript: baseFromScript };

  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof document === "undefined") return;

  var script = document.currentScript;
  var base = baseFromScript(script && script.src ? script.src : "/site/nav.js");

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; });
  }

  function render() {
    var nav = document.getElementById("siteNav");
    if (!nav) return;
    var links = buildNavLinks(location.pathname, base);
    var home = links[0];
    var brand = document.querySelector(".top .brand");
    if (brand) { brand.setAttribute("href", home.href); brand.setAttribute("title", "Home"); }

    var items = links.map(function (l) {
      var attrs = ' href="' + esc(l.href) + '"';
      if (l.current) attrs += ' aria-current="page"';
      if (l.external) attrs += ' class="nav-ext" rel="noopener"';
      return "<li><a" + attrs + ">" + esc(l.label) + "</a></li>";
    }).join("");
    var cur = links.filter(function (l) { return l.current; })[0];
    nav.innerHTML =
      '<button type="button" class="nav-toggle" aria-expanded="false" aria-controls="siteNavList">' +
      '<span class="nav-toggle-label">' + esc(cur ? cur.label : "Menu") + '</span><span class="nav-caret" aria-hidden="true"></span>' +
      '<span class="nav-sr"> menu</span></button>' +
      '<ul class="nav-list" id="siteNavList">' + items + "</ul>";
    nav.classList.add("nav-js");

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

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", render);
  else render();
})();
