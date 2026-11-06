"""Stdlib tests for manifest building and selection. Run: python3 -m unittest test_manifest"""
import json
import re
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
        samples = {os.path.basename(os.path.dirname(p)) for p in glob.glob(os.path.join(bm.ROOT, "samples", "*", "requirements*.txt"))
                   if any(bm.parse_requirements(p))}
        got = {it["id"][4:] for it in self.built["items"] if it["type"] == "pip"} - {"integration-cards"}
        self.assertEqual(samples, got)

    def test_profiles_nest(self):
        sel = {p: {i["id"] for i in prep.select(self.built, p, None, None)} for p in bm.TIERS}
        self.assertTrue(sel["minimal"] < sel["standard"] < sel["full"])
        self.assertEqual(len(sel["full"]), len(self.built["items"]))

    def test_select_filters(self):
        got = prep.select(self.built, "full", {"js"}, None)
        self.assertTrue(got and all(i["type"] == "js" for i in got))
        got = prep.select(self.built, "full", None, ["dataset:nclt*"])
        self.assertEqual([i["id"] for i in got], ["dataset:nclt-2012-01-08"])


class HelperTests(unittest.TestCase):
    def test_human(self):
        self.assertEqual(prep.human(None), "unknown")
        self.assertEqual(prep.human(999), "999 B")
        self.assertEqual(prep.human(1_500_000_000), "1.50 GB")


if __name__ == "__main__":
    unittest.main()
