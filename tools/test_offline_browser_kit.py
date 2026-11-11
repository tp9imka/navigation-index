#!/usr/bin/env python3
"""Unit tests for tools/offline_browser_kit.py: lock parsing, dependency order, sha256 checks, file listing.
No network. Run: python3 -m unittest tools/test_offline_browser_kit.py"""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import offline_browser_kit as vk  # noqa: E402

LOCK = {
    "info": {"python": "3.14.2"},
    "packages": {
        "numpy": {"name": "numpy", "file_name": "numpy-2.4.6-cp314.whl", "sha256": "AA" * 32, "depends": [], "version": "2.4.6"},
        "scipy": {"name": "scipy", "file_name": "scipy-1.18.0-cp314.whl", "sha256": "bb" * 32, "depends": ["numpy", "libfoo"]},
        "libfoo": {"name": "libfoo", "file_name": "https://example.org/x/libfoo-1.0.zip", "sha256": "cc" * 32, "depends": ["numpy"]},
        "loop-a": {"file_name": "a.whl", "sha256": "dd" * 32, "depends": ["loop_b"]},
        "loop-b": {"file_name": "b.whl", "sha256": "ee" * 32, "depends": ["loop-a"]},
    },
}


class LockTests(unittest.TestCase):
    def setUp(self):
        self.lock = vk.parse_lock(json.dumps(LOCK))

    def test_parse_normalizes_and_lowercases_sha(self):
        self.assertEqual(self.lock["numpy"]["sha256"], "aa" * 32)
        self.assertEqual(self.lock["loop-a"]["depends"], ["loop-b"])

    def test_resolve_deps_first_each_once(self):
        self.assertEqual(vk.resolve(self.lock, ["scipy", "numpy"]), ["numpy", "libfoo", "scipy"])

    def test_resolve_cycle_terminates(self):
        self.assertEqual(sorted(vk.resolve(self.lock, ["loop-a"])), ["loop-a", "loop-b"])

    def test_missing_package_names_parent(self):
        bad = vk.parse_lock(json.dumps({"packages": {"x": {"file_name": "x.whl", "sha256": "0", "depends": ["nope"]}}}))
        with self.assertRaisesRegex(KeyError, "needed by x"):
            vk.resolve(bad, ["x"])

    def test_wheel_entries_basename(self):
        self.assertEqual(vk.wheel_entries(self.lock, ["scipy"])[1], ("libfoo-1.0.zip", "cc" * 32))

    def test_parse_rejects_bad_lock(self):
        with self.assertRaises(ValueError):
            vk.parse_lock('{"packages": {}}')
        with self.assertRaises(ValueError):
            vk.parse_lock('{"packages": {"a": {"file_name": "a.whl"}}}')

    def test_check_wheels(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "ok.whl").write_bytes(b"hello")
            (Path(d) / "bad.whl").write_bytes(b"x")
            good = hashlib.sha256(b"hello").hexdigest()
            self.assertEqual(vk.check_wheels(d, [("ok.whl", good), ("bad.whl", good), ("gone.whl", good)]),
                             [("ok.whl", "ok"), ("bad.whl", "mismatch"), ("gone.whl", "missing")])


class ListingTests(unittest.TestCase):
    def make_tree(self, d):
        root = Path(d)
        files = ["site/index.html", "site/playground/manifest.json", "site/playground/worker.js",
                 "site/playground/__pycache__/x.pyc", "site/.DS_Store", "site/playground/pyodide-local/pyodide.mjs",
                 "site/playground/pyodide-local/venue-kit-verify.json", "site/playground/pyodide-local/scipy.whl.part",
                 "samples/a/a.py", "samples/a/unused.py"]
        for f in files:
            (root / f).parent.mkdir(parents=True, exist_ok=True)
            (root / f).write_text("x")
        manifest = {"pyodide_local": "pyodide-local/",
                    "files": [{"src": "../../samples/a/a.py", "dst": "a.py"}, {"src": "../../samples/a/a.py", "dst": "b.py"}]}
        return root, manifest

    def test_manifest_files_relative_to_root(self):
        with tempfile.TemporaryDirectory() as d:
            root, m = self.make_tree(d)
            self.assertEqual(vk.manifest_files(m, root / "site/playground", root), ["samples/a/a.py"])

    def test_manifest_file_outside_root_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root, _ = self.make_tree(d)
            with self.assertRaisesRegex(ValueError, "outside"):
                vk.manifest_files({"files": [{"src": "../../../etc/passwd"}]}, root / "site/playground", root)

    def test_bundle_entries_skip_caches_and_reports(self):
        with tempfile.TemporaryDirectory() as d:
            root, m = self.make_tree(d)
            self.assertEqual(vk.bundle_entries(root, m, root / "site/playground"),
                             ["samples/a/a.py", "site/index.html", "site/playground/manifest.json",
                              "site/playground/pyodide-local/pyodide.mjs", "site/playground/worker.js"])

    def test_bundle_entries_missing_manifest_file(self):
        with tempfile.TemporaryDirectory() as d:
            root, m = self.make_tree(d)
            m["files"].append({"src": "../../samples/a/missing.py"})
            with self.assertRaises(FileNotFoundError):
                vk.bundle_entries(root, m, root / "site/playground")

    def test_local_dir_from_manifest(self):
        self.assertEqual(vk.local_dir({"pyodide_local": "pyodide-local/"}, Path("/r/site/playground")),
                         Path("/r/site/playground/pyodide-local").resolve())

    def test_real_manifest_files_exist(self):
        rels = vk.manifest_files(vk.load_manifest())
        self.assertGreater(len(rels), 20)
        for rel in rels:
            self.assertTrue((vk.ROOT / rel).is_file(), rel)


if __name__ == "__main__":
    unittest.main()
