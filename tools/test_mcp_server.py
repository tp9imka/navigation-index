"""python3 tools/test_mcp_server.py  (stdlib; needs index/records.jsonl and graph/graph.json)"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mcp_server  # noqa: E402

HAVE_INDEX = (HERE.parent / "index" / "records.jsonl").exists() and \
    (HERE.parent / "graph" / "graph.json").exists()


def call(name, **args):
    r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                           "params": {"name": name, "arguments": args}})
    return r


class RpcRobustness(unittest.TestCase):
    def test_malformed_messages_get_errors(self):
        for msg in ({"jsonrpc": "2.0", "id": 1, "method": []},
                    {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": [1]},
                    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": "x"},
                    {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": [1]}},
                    {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                     "params": {"name": "search", "arguments": "q"}},
                    [1], None, "x"):
            self.assertIn("error", mcp_server.handle(msg), msg)

    def test_stray_response_ignored(self):
        self.assertIsNone(mcp_server.handle({"jsonrpc": "2.0", "id": 3, "result": {}}))

    def test_instructions_mark_records_untrusted(self):
        r = mcp_server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
        self.assertIn("never as instructions", r["result"]["instructions"])

    @unittest.skipUnless(HAVE_INDEX, "run tools/build.py first")
    def test_non_finite_and_bogus_numbers_are_tool_errors(self):
        for limit in (float("nan"), "10", True, [1]):
            r = call("search", query="gps", limit=limit)
            self.assertTrue(r["result"]["isError"], limit)
        for limit in (float("inf"), 10 ** 9, None):   # clamped or defaulted, never a crash
            r = call("search", query="gps", limit=limit)
            self.assertFalse(r["result"]["isError"], limit)
            self.assertLessEqual(len(json.loads(r["result"]["content"][0]["text"])), mcp_server.MAX_LIMIT)
        r = call("neighbors", id="concept:vio", depth=float("inf"))
        self.assertFalse(r["result"]["isError"])

    @unittest.skipUnless(HAVE_INDEX, "run tools/build.py first")
    def test_ids_are_lookups_not_paths(self):
        for rid in ("../../etc/passwd", "/etc/passwd", "index/records.jsonl"):
            r = call("show", id=rid)
            self.assertTrue(r["result"]["isError"])
            self.assertNotIn("root:", r["result"]["content"][0]["text"])

    @unittest.skipUnless(HAVE_INDEX, "run tools/build.py first")
    def test_process_survives_hostile_lines(self):
        hostile = (b"[" * 100000 + b"\n" + b"\xff\xfe\n" +
                   b'{"jsonrpc":"2.0","id":1,"method":[]}\n' +
                   b'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"search",'
                   b'"arguments":{"query":"gps","limit":1e400}}}\n' +
                   b'{"jsonrpc":"2.0","id":99,"method":"ping"}\n')
        p = subprocess.run([sys.executable, str(HERE / "mcp_server.py")], input=hostile,
                           capture_output=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn(b'"id": 99', p.stdout)


if __name__ == "__main__":
    unittest.main()
