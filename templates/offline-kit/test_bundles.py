"""Offline bundle contracts; no network, Docker or optional packages required."""
import json
import importlib.util
import zipfile
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


KIT = Path(__file__).resolve().parent
sys.path.insert(0, str(KIT))
import bundle  # noqa: E402


class BundleTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec('pip'), 'pip is not bundled with this interpreter')
    def test_real_vision_spec_resolves_lightglue_metadata_in_empty_wheelhouse(self):
        """Metadata-only resolver probe; no network, real wheels, or installed packages."""
        definitions = json.loads((KIT / 'bundles.json').read_text())['bundles']
        vision = next(d for d in definitions if d['id'] == 'vision')
        manifest = json.loads((KIT / 'manifest.json').read_text())
        requirements = [r for item in bundle.selection(vision, manifest) if item['type'] == 'pip'
                        for r in item['requirements']]
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            def wheel(name, version, deps=()):
                normalized = name.replace('-', '_')
                info = f'{normalized}-{version}.dist-info'
                with zipfile.ZipFile(folder / f'{normalized}-{version}-py3-none-any.whl', 'w') as out:
                    out.writestr(info + '/METADATA', f'Metadata-Version: 2.1\nName: {name}\nVersion: {version}\n'
                                 + ''.join('Requires-Dist: ' + d + '\n' for d in deps))
                    out.writestr(info + '/WHEEL', 'Wheel-Version: 1.0\nGenerator: metadata-fixture\nRoot-Is-Purelib: true\nTag: py3-none-any\n')
                    out.writestr(info + '/RECORD', '')
            for req in requirements:
                name, version = req.split('==', 1)
                wheel(name, version)
            # Declared by LightGlue at 5a650c444718caffc2669dc0094cde908f42dd73.
            wheel('lightglue', '0.0', ['torch>=1.9.1', 'torchvision>=0.3', 'numpy',
                                     'kornia>=0.6.11', 'opencv-python', 'matplotlib'])
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--dry-run',
                '--ignore-installed', '--no-index', '--find-links', str(folder),
                '--target', str(folder / 'target'), *requirements, 'lightglue==0.0'],
                capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.cache = self.root / "cache"
        self.source = self.root / "source.txt"
        self.source.write_text("recorded fixture bytes\n")
        self.script = self.repo / "replay.py"
        self.script.write_text("import json, pathlib, sys\n"
                               "pathlib.Path(sys.argv[1]).write_text(json.dumps({'epochs': 3}))\n")
        self.manifest = self.root / "manifest.json"
        self.manifest.write_text(json.dumps({"tiers": ["minimal", "standard", "full"],
            "python_version": "3.12", "pip_platforms": {}, "items": [
                {"id": "dataset:tiny", "type": "dataset", "tier": "minimal",
                 "license": "test fixture", "files": [{"method": "http",
                     "url": self.source.as_uri(), "dest": "capture.txt", "size": self.source.stat().st_size}]}]}))
        self.definition = {"id": "tiny", "sample": "fixture", "prep_items": ["dataset:tiny"],
            "repo_inputs": ["replay.py"], "cache_inputs": ["datasets/tiny/capture.txt"],
            "prepare_commands": [], "rehearse_commands": [
                {"argv": ["{python}", "{repo}/replay.py", "{run}/result.json"], "cwd": "{repo}"}],
            "expected_outputs": [{"path": "{run}/result.json", "kind": "json"}],
            "packages": [], "requires_venv": False}
        self.definitions = self.root / "bundles.json"
        self.write_definitions()

    def write_definitions(self):
        self.definitions.write_text(json.dumps({"version": 1, "bundles": [self.definition]}))

    def cli(self, action, *args):
        return subprocess.run([sys.executable, str(KIT / "bundle.py"), action, "tiny",
            "--definitions", str(self.definitions), "--manifest", str(self.manifest),
            "--repo", str(self.repo), "--cache", str(self.cache), *args],
            text=True, capture_output=True)

    def receipt(self, action):
        return json.loads((self.cache / "bundles" / "tiny" / (action + ".json")).read_text())

    def test_selective_plan_rejects_unknown_items(self):
        p = self.cli("plan")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["selected_items"], ["dataset:tiny"])
        self.definition["prep_items"] = ["dataset:missing"]
        self.write_definitions()
        self.assertNotEqual(self.cli("plan").returncode, 0)

    def test_prepare_uses_fetcher_and_checks_copy_for_corruption(self):
        p = self.cli("prepare")
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)
        self.assertFalse(self.receipt("prepare")["offline_ready"])
        self.assertEqual(self.cli("verify").returncode, 0)
        capture = self.cache / "datasets/tiny/capture.txt"
        capture.write_text("corrupt cache\n")
        self.assertNotEqual(self.cli("verify").returncode, 0)
        self.assertNotEqual(self.cli("rehearse").returncode, 0)
        self.assertFalse(self.receipt("rehearse")["offline_ready"])

    def test_missing_asset_and_missing_receipt_never_pass(self):
        self.assertNotEqual(self.cli("verify").returncode, 0)
        self.assertEqual(self.cli("prepare").returncode, 0)
        (self.cache / "datasets/tiny/capture.txt").unlink()
        self.assertNotEqual(self.cli("verify").returncode, 0)

    def test_failed_rehearsal_records_actual_exit_status(self):
        self.script.write_text("raise SystemExit(7)\n")
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.assertNotEqual(self.cli("rehearse", "--network-disabled").returncode, 0)
        receipt = self.receipt("rehearse")
        self.assertFalse(receipt["offline_ready"])
        self.assertEqual(receipt["commands"][0]["returncode"], 7)

    def test_zero_exit_without_expected_output_fails(self):
        self.script.write_text("pass\n")
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.assertNotEqual(self.cli("rehearse").returncode, 0)

    def test_receipt_distinguishes_run_from_declared_offline_run(self):
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.assertEqual(self.cli("rehearse").returncode, 0)
        receipt = self.receipt("rehearse")
        self.assertFalse(receipt["offline_ready"])
        self.assertGreater(receipt["commands"][0]["elapsed_s"], 0)
        self.assertEqual(self.cli("rehearse", "--network-disabled").returncode, 0)
        self.assertTrue(self.receipt("rehearse")["offline_ready"])

    def test_changed_source_or_definition_invalidates_preparation(self):
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.script.write_text("# different source\n")
        self.assertNotEqual(self.cli("verify").returncode, 0)
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.definition["cache_inputs"].append("unknown-weights.pth")
        self.write_definitions()
        self.assertNotEqual(self.cli("verify").returncode, 0)
        self.assertNotEqual(self.cli("prepare").returncode, 0)

    def test_partial_prep_state_does_not_pass_cache_verification(self):
        self.assertEqual(self.cli("prepare").returncode, 0)
        state_path = self.cache / ".prep-state.json"
        state = json.loads(state_path.read_text())
        state["dataset:tiny"]["status"] = "partial"
        state_path.write_text(json.dumps(state))
        self.assertNotEqual(self.cli("verify").returncode, 0)

    def test_cached_only_never_fetches_an_unknown_item(self):
        self.assertNotEqual(self.cli("prepare", "--cached-only").returncode, 0)
        self.assertFalse((self.cache / "datasets/tiny/capture.txt").exists())
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.source.unlink()
        self.assertEqual(self.cli("prepare", "--cached-only").returncode, 0)

    def test_replay_with_silently_skipped_logs_fails(self):
        self.script.write_text("import pathlib,sys; pathlib.Path(sys.argv[1]).write_text('{\"results\": []}')\n")
        self.definition['expected_outputs'][0].update(kind='replay', expected_files=['capture.ubx'])
        self.write_definitions()
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.assertNotEqual(self.cli("rehearse").returncode, 0)

    def test_old_output_cannot_satisfy_successful_noop_rehearsal(self):
        self.script.write_text("pass\n")
        output = self.repo / 'old-result.json'
        output.write_text('{"old": true}')
        self.definition['expected_outputs'][0]['path'] = '{repo}/old-result.json'
        self.write_definitions()
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.assertNotEqual(self.cli("rehearse").returncode, 0)

    def test_shared_prep_checksums_ignore_mutable_bundle_receipts(self):
        self.assertEqual(self.cli("prepare").returncode, 0)
        self.assertEqual(self.cli("rehearse").returncode, 0)
        p = subprocess.run([sys.executable, str(KIT / 'prep.py'), '--verify', '--out', str(self.cache)],
                           text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)

    def test_stdlib_bundle_needs_no_wheel_platform(self):
        # A stdlib replay should work on a platform with no configured wheel target.
        bundle.install_runtime([], sys.executable, self.repo, self.cache, None, {}, self.root, [])

    def test_missing_or_changed_runtime_tool_invalidates_verification(self):
        version = self.root / 'tool-version.txt'
        version.write_text('v1')
        self.definition['runtime_tools'] = {'fixture-tool': [sys.executable, '-c',
            'from pathlib import Path; print(Path(' + repr(str(version)) + ').read_text())']}
        self.write_definitions()
        self.assertEqual(self.cli('prepare').returncode, 0)
        version.write_text('v2')
        self.assertNotEqual(self.cli('verify').returncode, 0)
        version.unlink()
        self.assertNotEqual(self.cli('verify').returncode, 0)


if __name__ == "__main__":
    unittest.main()
