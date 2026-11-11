#!/usr/bin/env python3
"""tools/check_deploy.py against a local http.server serving the repo root. No network.

Two handlers mimic the two host behaviours seen in production:
  Host404      missing path => 404 with the root 404.html (Cloudflare Pages with 404.html)
  HostFallback missing path => 200 index.html (Cloudflare Pages without 404.html, before a42d49f)
Both serve a fake Pyodide CDN at /_fake_cdn/ so check 4 needs no network.

Run: python3 -m unittest tools/test_check_deploy.py
"""
import contextlib
import functools
import http.server
import io
import json
import sys
import threading
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_deploy  # noqa: E402

ROOT = check_deploy.ROOT
FAKE_CDN = "/_fake_cdn/"


class Host404(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _fake_cdn(self):
        if not self.path.startswith(FAKE_CDN):
            return False
        body = b"export function loadPyodide() {}\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/javascript")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command == "GET":
            self.wfile.write(body)
        return True

    def _missing(self):
        path = Path(self.translate_path(self.path))
        return not path.exists()

    def _send_file(self, status, name):
        body = (ROOT / name).read_bytes()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command == "GET":
            self.wfile.write(body)

    def on_missing(self):
        self._send_file(404, "404.html")

    def do_GET(self):
        if self._fake_cdn():
            return
        if self._missing():
            return self.on_missing()
        super().do_GET()

    def do_HEAD(self):
        if self._fake_cdn():
            return
        if self._missing():
            return self.on_missing()
        super().do_HEAD()


class HostFallback(Host404):
    def on_missing(self):
        self._send_file(200, "index.html")


class HostStaleShowcase(Host404):
    """site/showcase.html answers the old full page (no redirect to results.html)."""
    def do_GET(self):
        if self.path.split("?")[0] == "/site/showcase.html":
            body = b"<!doctype html><title>Showcase</title><p>old page</p>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


@contextlib.contextmanager
def serve(handler):
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(handler, directory=str(ROOT)))
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    try:
        yield f"http://127.0.0.1:{srv.server_address[1]}/"
    finally:
        srv.shutdown()
        srv.server_close()


def by_check(results):
    return {r["check"]: r for r in results}


class CheckDeployTest(unittest.TestCase):
    def setUp(self):
        self._wait = check_deploy.RETRY_WAIT_S
        check_deploy.RETRY_WAIT_S = 0

    def tearDown(self):
        check_deploy.RETRY_WAIT_S = self._wait

    def test_host_with_404_passes_every_check(self):
        with serve(Host404) as base:
            results = check_deploy.run_checks(base, pyodide_base=base + FAKE_CDN.lstrip("/"))
            pages = check_deploy.discover_pages(check_deploy.Site(base), check_deploy.fetch(base))[0]
        failed = [r for r in results if r["status"] == "FAIL"]
        self.assertEqual(failed, [], json.dumps(failed, indent=2))
        res = by_check(results)
        self.assertEqual(len(results), 7)
        # the crawl reached the playground worker, the manifest and its .py files
        self.assertRegex(res["2 assets"]["detail"], r"^(\d+)/\1 ")
        self.assertGreater(int(res["2 assets"]["detail"].split("/")[0]), 40)
        # Results and Learn are crawled; the showcase stub counts as a redirect, not a page
        self.assertIn("1/1 redirect stubs reach their target", res["2 pages"]["detail"])
        rel = {p[len(base):] for p in pages}
        self.assertTrue({"site/results.html", "site/learn.html"} <= rel, rel)
        self.assertNotIn("site/showcase.html", rel)

    def test_showcase_without_redirect_fails_pages(self):
        with serve(HostStaleShowcase) as base:
            results = check_deploy.run_checks(base, pyodide_base=base + FAKE_CDN.lstrip("/"))
        res = by_check(results)
        self.assertEqual(res["2 pages"]["status"], "FAIL")
        self.assertIn("site/showcase.html => no redirect to results.html", json.dumps(res["2 pages"]))

    def test_host_with_html_fallback_fails_check_1_and_local_probe(self):
        with serve(HostFallback) as base:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                code = check_deploy.main([base, "--json", "--pyodide-base", base + FAKE_CDN.lstrip("/")])
        self.assertEqual(code, 1)
        res = by_check(json.loads(out.getvalue())["results"])
        self.assertEqual(res["1 missing-404"]["status"], "FAIL")
        self.assertIn("200 text/html", res["1 missing-404"]["detail"])
        self.assertEqual(res["4 local-probe"]["status"], "FAIL")
        for name in ("2 pages", "2 assets", "3 worker-version", "3 js-equals-local", "4 pyodide-base"):
            self.assertEqual(res[name]["status"], "PASS", res[name])


if __name__ == "__main__":
    unittest.main()
