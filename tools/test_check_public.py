"""Tests for tools/check_public.py: python3 -m unittest tools/test_check_public.py (stdlib only)."""
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_public as cp  # noqa: E402

FIXTURES = {
    "docs/clean.md": "Resilient PNT for small drones. Edge cases and an edge detector are fine.\n",
    "docs/employer.md": "Built for the EDGE Group event.\nChallenge 2 brief.\nAutonomous Frontiers track.\n",
    "docs/paths.md": "see /Users/someone/x and /home/alice/y\n",
    "docs/tags.md": "added in loop-13b, loop80 is a file suffix\n",
    "docs/tools.md": "made with farmout and Kiro, the Codex lane, thanks Ivan\n",
    "docs/event.md": "On the day, Day-1 and day1 and Day 1; organisers and organizers; the judges\nhackathon day\n",
    "docs/ok-words.md": "day 10 and day12 and kirov and Ivanov and judged\n",
    "catalog/generated.md": "EDGE in a generated file\n",
    "loop/notes.md": "loop-13 inside loop/ is allowed\n",
    "data/loop-05.json": "{}\n",
}


def terms_of(hits, path):
    return sorted({h["term"] for h in hits if h["path"] == path})


class TestScan(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        for p, text in FIXTURES.items():
            (cls.tmp / p).parent.mkdir(parents=True, exist_ok=True)
            (cls.tmp / p).write_text(text)
        (cls.tmp / "docs" / "blob.bin").write_bytes(b"\0EDGE\0")
        cls.hits = cp.scan(cls.tmp, list(FIXTURES) + ["docs/blob.bin"])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_clean_file_has_no_hits(self):
        self.assertEqual(terms_of(self.hits, "docs/clean.md"), [])
        self.assertEqual(terms_of(self.hits, "docs/ok-words.md"), [])

    def test_employer_terms(self):
        self.assertEqual(terms_of(self.hits, "docs/employer.md"),
                         ["Autonomous Frontiers", "Challenge 2", "EDGE", "EDGE Group"])

    def test_machine_paths(self):
        self.assertEqual(terms_of(self.hits, "docs/paths.md"), ["/Users/", "/home/<name>/"])

    def test_wave_tags_need_the_hyphen(self):
        h = [x for x in self.hits if x["path"] == "docs/tags.md"]
        self.assertEqual([(x["line"], x["term"]) for x in h], [(1, "loop-NN")])

    def test_tooling_words(self):
        self.assertEqual(terms_of(self.hits, "docs/tools.md"), ["Codex lane", "Ivan", "Kiro", "farmout"])

    def test_event_framing(self):
        self.assertEqual(terms_of(self.hits, "docs/event.md"),
                         ["Day 1", "hackathon day", "judges", "on the day", "organiser"])
        self.assertEqual(sum(1 for h in self.hits if h["path"] == "docs/event.md" and h["term"] == "Day 1"), 1)

    def test_generated_and_loop_skipped(self):
        self.assertEqual(terms_of(self.hits, "catalog/generated.md"), [])
        self.assertEqual(terms_of(self.hits, "loop/notes.md"), [])
        self.assertIn("EDGE", terms_of(cp.scan(self.tmp, ["catalog/generated.md"], include_generated=True),
                                       "catalog/generated.md"))

    def test_path_name_is_checked(self):
        self.assertIn({"path": "data/loop-05.json", "line": 0, "term": "loop-NN", "text": "data/loop-05.json"},
                      self.hits)

    def test_binary_content_skipped(self):
        self.assertEqual(terms_of(self.hits, "docs/blob.bin"), [])

    def test_output_format_fields(self):
        h = next(x for x in self.hits if x["path"] == "docs/paths.md")
        self.assertEqual((h["line"], h["term"]), (1, "/Users/"))


class TestAllowlist(unittest.TestCase):
    HITS = [{"path": "a.md", "line": 3, "term": "Ivan", "text": "authors: Ivan Petrov"},
            {"path": "a.md", "line": 9, "term": "Ivan", "text": "thanks Ivan"},
            {"path": "b.md", "line": 1, "term": "judges", "text": "judges"}]

    def test_text_entry_covers_only_its_line(self):
        left, unused = cp.apply_allowlist(self.HITS, [{"path": "a.md", "term": "Ivan", "text": "Ivan Petrov", "reason": "author"}])
        self.assertEqual([h["line"] for h in left if h["path"] == "a.md"], [9])
        self.assertEqual(unused, [])

    def test_line_entry_and_wildcard(self):
        entries = [{"path": "a.md", "term": "Ivan", "line": 9, "reason": "r"},
                   {"path": "b.md", "term": "*", "reason": "r"},
                   {"path": "c.md", "term": "Kiro", "reason": "stale"}]
        left, unused = cp.apply_allowlist(self.HITS, entries)
        self.assertEqual([h["line"] for h in left], [3])
        self.assertEqual([e["path"] for e in unused], ["c.md"])

    def test_reason_required(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "allow.json"
            p.write_text(json.dumps([{"path": "a.md", "term": "Ivan", "reason": " "}]))
            with self.assertRaises(ValueError):
                cp.load_allowlist(p)
            p.write_text(json.dumps([{"path": "a.md", "term": "NotATerm", "reason": "x"}]))
            with self.assertRaises(ValueError):
                cp.load_allowlist(p)

    def test_repo_allowlist_is_valid(self):
        for e in cp.load_allowlist(cp.ALLOWLIST):
            self.assertTrue(e["reason"].strip())

    def test_counts(self):
        c = cp.counts(self.HITS)
        self.assertEqual(c["by_term"], {"Ivan": 2, "judges": 1})
        self.assertEqual(c["by_folder"], {"(root)": 3})
        self.assertEqual((c["files"], c["total"]), (2, 3))


@unittest.skipUnless(shutil.which("git"), "git not installed")
class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True)
        (self.tmp / "tools").mkdir()
        (self.tmp / "README.md").write_text("Day 1 plan\n")
        (self.tmp / "ok.md").write_text("nothing here\n")
        (self.tmp / "tools" / "public_allowlist.json").write_text("[]")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = cp.main(["--root", str(self.tmp), *args])
        return code, out.getvalue(), err.getvalue()

    def test_strict_fails_and_prints_path_line_term(self):
        code, out, _ = self.run_cli()
        self.assertEqual(code, 1)
        self.assertEqual(out.strip(), "README.md:1:Day 1")

    def test_warn_exits_zero(self):
        code, out, _ = self.run_cli("--warn")
        self.assertEqual(code, 0)
        self.assertIn("README.md:1:Day 1", out)

    def test_json(self):
        code, out, _ = self.run_cli("--json", "--warn")
        d = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual(d["counts"]["by_term"], {"Day 1": 1})

    def test_allowlisted_tree_passes(self):
        (self.tmp / "tools" / "public_allowlist.json").write_text(
            json.dumps([{"path": "README.md", "term": "Day 1", "text": "Day 1 plan", "reason": "fixture"}]))
        self.assertEqual(self.run_cli()[0], 0)


if __name__ == "__main__":
    unittest.main()
