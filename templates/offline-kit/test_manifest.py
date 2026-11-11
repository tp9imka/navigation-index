"""Stdlib tests for manifest building and selection. Run: python3 -m unittest test_manifest"""
import json
import re
import os
import sys
import tempfile
import unittest

KIT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KIT)
import build_manifest as bm  # noqa: E402
import prep  # noqa: E402


class ParserTests(unittest.TestCase):
    def test_requirements_split_vcs_and_comments(self):
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("# header\nnumpy==2.5.4\n\npyserial  # live only\n"
                    "lightglue @ git+https://github.com/cvg/LightGlue@abc\n# websockets\n")
        try:
            reqs, vcs = bm.parse_requirements(f.name)
        finally:
            os.unlink(f.name)
        self.assertEqual(reqs, ["numpy==2.5.4", "pyserial"])
        self.assertEqual(vcs, ["lightglue @ git+https://github.com/cvg/LightGlue@abc"])

    def test_card_pip_skips_flags_paths_and_requirement_files(self):
        text = ("| Install | `pip install -r requirements.txt` then `pip install --upgrade pyubx2`; "
                "`pip install 'adsbcot[with_pymodes]' imufusion==1.3.3`; `pip install -e .`; "
                "`pip install git+https://github.com/esa/tetra3.git` |\n| Other | `pip install notme` |")
        self.assertEqual(bm.parse_card_pip(text), ["pyubx2", "adsbcot[with_pymodes]", "imufusion==1.3.3"])

    def test_card_docker_takes_image_after_flags(self):
        text = ("`docker run -p 8088:8088 -p 8080:8080 ghcr.io/kdudkov/goatak_server:latest`\n"
                "docker run --rm -v \"$PWD:/data\" -w /data ghcr.io/osgeo/gdal:ubuntu-small-latest bash\n"
                "docker run --rm -it mins ./build/mins/mins_cli\n")
        self.assertEqual(bm.parse_card_docker(text),
                         ["ghcr.io/kdudkov/goatak_server:latest", "ghcr.io/osgeo/gdal:ubuntu-small-latest"])

    def test_dockerfile_from_skips_build_stages(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as f:
            f.write("FROM ubuntu:24.04 AS build\nRUN true\nFROM build AS x\nFROM python:3.12-slim\nFROM ${BASE}\n")
        try:
            self.assertEqual(bm.parse_dockerfile_from(f.name), ["ubuntu:24.04", "python:3.12-slim"])
        finally:
            os.unlink(f.name)

    def test_fetch_vendor_pairs(self):
        pairs = bm.parse_fetch_vendor(os.path.join(bm.ROOT, "templates", "demo-dashboard", "fetch-vendor.sh"))
        self.assertTrue(pairs)
        for url, dst in pairs:
            self.assertTrue(url.startswith("https://unpkg.com/") and "@" in url, url)
            self.assertFalse("/" in dst)


class ManifestTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.built = bm.build()
        with open(bm.OUT) as f:
            cls.committed = json.load(f)

    def test_committed_manifest_is_current(self):
        self.assertEqual(self.committed, json.loads(json.dumps(self.built)),
                         "manifest.json is stale: run python3 build_manifest.py")

    def test_every_dataset_url_is_backed_by_its_card(self):
        for ds in bm.DATASETS:
            self.assertEqual(bm.check_evidence(ds), [], ds["id"])
            text = bm.card_text(ds["card"])
            for var, val in re.findall(r"^([A-Z]+)=(\S+)$", text, re.M):
                text = text.replace("${%s}" % var, val).replace("$" + var, val)
            for f in ds["files"]:
                key = f.get("id") or f.get("record") or f.get("dataset") or f.get("path") or f.get("url") or f.get("prefix") or f["evidence"][-1]
                tail = key.rstrip("/").split("/")[-1].split("?")[0]
                stem = tail.split(".h5.part-")[0]
                self.assertTrue(stem in text or tail in text, f"{ds['id']}: {tail} not in {ds['card']}")

    def test_ids_unique_and_fields_present(self):
        ids = [it["id"] for it in self.built["items"]]
        self.assertEqual(len(ids), len(set(ids)))
        for it in self.built["items"]:
            self.assertIn(it["tier"], bm.TIERS, it["id"])
            self.assertIn(it["type"], prep.TYPES, it["id"])
            self.assertTrue(it.get("license"), it["id"])
            self.assertIn(it["type"], prep.FETCHERS)

    def test_unknown_sizes_are_null_not_guessed(self):
        for it in self.built["items"]:
            if it["type"] in ("pip", "docker", "docker-build", "git", "js", "tool", "tiles"):
                self.assertIsNone(it["size"], it["id"])
            if it["type"] == "dataset":
                sizes = [f.get("size") for f in it["files"]]
                self.assertEqual(it["size_complete"], all(s is not None for s in sizes), it["id"])

    def test_repo_tiers(self):
        git = sorted((it for it in self.built["items"] if it["type"] == "git"), key=lambda i: i["rank"])
        self.assertEqual(sum(1 for g in git if g["tier"] == "minimal"), bm.REPOS_MINIMAL)
        self.assertEqual(sum(1 for g in git if g["tier"] in ("minimal", "standard")), bm.REPOS_STANDARD)
        self.assertTrue(all(g["url"].startswith("https://github.com/") for g in git))

    def test_sample_requirements_all_present(self):
        import glob
        files = {os.path.relpath(p, bm.ROOT) for p in glob.glob(os.path.join(bm.ROOT, "samples", "*", "requirements*.txt"))
                 if any(bm.parse_requirements(p))}
        pips = [it for it in self.built["items"] if it["type"] == "pip" and it["id"] != "pip:integration-cards"]
        self.assertEqual(files, {it["source"] for it in pips})

    def test_profiles_nest(self):
        sel = {p: {i["id"] for i in prep.select(self.built, p, None, None)} for p in bm.TIERS}
        self.assertTrue(sel["minimal"] < sel["standard"] < sel["full"])
        self.assertEqual(len(sel["full"]), len(self.built["items"]))

    def test_select_filters(self):
        got = prep.select(self.built, "full", {"js"}, None)
        self.assertTrue(got and all(i["type"] == "js" for i in got))
        got = prep.select(self.built, "full", None, ["dataset:nclt*"])
        self.assertEqual([i["id"] for i in got], ["dataset:nclt-2012-01-08"])


class CloseAreaBundleTests(unittest.TestCase):
    """bundles.json close-area: wheel sets match the requirement files, rehearsal stays offline and in {run}."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(KIT, "bundles.json")) as f:
            cls.d = next(b for b in json.load(f)["bundles"] if b["id"] == "close-area")
        cls.items = {i["id"]: i for i in cls.d["extra_items"]}
        cls.steps = {c["name"]: c for c in cls.d["rehearse_commands"]}

    @staticmethod
    def expand(path):
        reqs, _ = bm.parse_requirements(path)
        out = []
        for r in reqs:
            if r.startswith("-r "):
                out += CloseAreaBundleTests.expand(os.path.join(os.path.dirname(path), r[3:].strip()))
            else:
                out.append(r)
        return out

    def test_wheel_sets_match_requirement_files(self):
        arena = os.path.join(bm.ROOT, "samples", "close-area-arena")
        py312 = self.expand(os.path.join(arena, "requirements-image.txt")) + self.expand(
            os.path.join(bm.ROOT, "samples", "close-area-benchmark", "requirements.txt"))
        py311 = self.expand(os.path.join(arena, "requirements.txt"))  # templates/flight-repo Makefile venv
        self.assertEqual(sorted(self.d["prep_items"]), sorted(self.items))
        self.assertEqual(sorted(set(py312)), sorted(self.items["pip:close-area-py312"]["requirements"]))
        self.assertEqual(sorted(set(py311)), sorted(self.items["pip:close-area-py311"]["requirements"]))
        self.assertEqual({i["python_version"] for i in self.items.values()}, {"3.11", "3.12"})
        for it in self.items.values():
            self.assertEqual(it["type"], "pip")
            self.assertIn(it["tier"], bm.TIERS)
        for tag in ("cp311", "cp312"):
            self.assertIn("pip/{pip_platform}/numpy-*-%s-*.whl" % tag, self.d["cache_inputs"])

    def test_uv_never_reaches_an_index_or_downloads_python(self):
        uv = [c for c in self.d["rehearse_commands"] + self.d["verify_commands"] if c["argv"][0] == "uv"]
        self.assertTrue(uv)
        for c in uv:
            if c["argv"][1] == "venv":
                self.assertIn("--no-python-downloads", c["argv"], c["name"])
            else:
                for flag in ("--offline", "--no-index", "--no-build", "--find-links"):
                    self.assertIn(flag, c["argv"], c["name"])
                self.assertEqual(c["argv"][c["argv"].index("--find-links") + 1], "{cache}/pip/{pip_platform}")
        versions = {c["argv"][c["argv"].index("--python") + 1] for c in uv if c["argv"][1] == "venv"}
        self.assertEqual(versions, {"3.11", "3.12"})

    def test_day1_steps_and_budget(self):
        pack = self.steps["pack-hall_8x6"]["argv"]
        self.assertEqual(pack[1:5], ["pack.py", "run", "packs/hall_8x6.json", "--workers"])
        self.assertEqual(pack[5], "4")
        self.assertTrue(pack[pack.index("--out") + 1].startswith("{run}/"))
        self.assertIn("pack-verdicts-match", self.steps)
        flight = self.steps["first-flight"]
        self.assertEqual(flight["argv"][:3], ["make", "first-flight", "PLANNER=bench:dstar_lite"])
        self.assertIn("ARM=F0", flight["argv"])
        self.assertIn("WORLD={repo}/samples/close-area-arena/rooms/hall_8x6.world.json", flight["argv"])
        self.assertTrue(flight["cwd"].startswith("{run}/"), "flight must not write templates/flight-repo/results")
        self.assertEqual(sum(1 for c in self.d["rehearse_commands"] if c["argv"][0] == "make"), 1)
        self.assertIn("'results'", self.steps["flight-copy"]["argv"][2])  # committed results are not copied
        for spec in self.d["expected_outputs"]:
            self.assertTrue(spec["path"].startswith("{run}/"), spec["path"])
        world = os.path.join(bm.ROOT, "samples", "close-area-arena", "rooms", "hall_8x6.world.json")
        self.assertTrue(os.path.isfile(world))

    def test_browser_pointer_and_guarded_venue_kit(self):
        self.assertTrue(os.path.isfile(os.path.join(bm.ROOT, "tools", "offline_browser_kit.py")))
        self.assertEqual(self.d["browser"]["verify"], "python3 tools/offline_browser_kit.py verify")
        self.assertTrue(os.path.isfile(os.path.join(bm.ROOT, self.d["browser"]["doc"].split("#")[0])))
        step = self.steps["offline-browser-kit-verify"]
        self.assertEqual(step["skip_unless_exists"], "{repo}/site/playground/pyodide-local")
        import bundle
        commands = []
        with tempfile.TemporaryDirectory() as td:
            bundle.run_step(step, dict(repo=td, python=sys.executable), dict(os.environ), td, commands)
        self.assertEqual(len(commands), 1)
        self.assertTrue(commands[0]["skipped"].startswith("not found: "))
        self.assertIsNone(commands[0]["returncode"])

    def test_repo_inputs_exist(self):
        import glob
        for pattern in self.d["repo_inputs"]:
            self.assertTrue(glob.glob(os.path.join(bm.ROOT, pattern)), pattern)


class HelperTests(unittest.TestCase):
    def test_human(self):
        self.assertEqual(prep.human(None), "unknown")
        self.assertEqual(prep.human(999), "999 B")
        self.assertEqual(prep.human(1_500_000_000), "1.50 GB")


if __name__ == "__main__":
    unittest.main()
