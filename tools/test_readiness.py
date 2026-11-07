"""Evidence-backed readiness and query contract tests (stdlib only)."""
import json
import ast
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import readiness
import query
import mcp_server
import build
from unittest import mock


class ReadinessTests(unittest.TestCase):
    def test_curated_download_ceiling_cannot_round_pinned_bytes_down(self):
        source = ast.parse((query.ROOT / 'samples/ugv-gnss-outage-real/fetch_nclt.py').read_text())
        assignment = next(n for n in source.body if isinstance(n, ast.Assign)
                          and any(isinstance(t, ast.Name) and t.id == 'SESSIONS' for t in n.targets))
        session = ast.literal_eval(assignment.value)['2013-01-10']
        required_mb = (session['sen_bytes'] + session['gt_bytes']) / 1e6
        rd = json.loads((query.ROOT / 'data/readiness.json').read_text())['sample:ugv-gnss-outage-real']
        self.assertGreaterEqual(rd['download_mb'], required_mb)
        self.assertFalse(readiness.matches({'readiness': rd}, {'max_download_mb': 42}))

    def test_missing_readiness_is_unknown_not_free_or_verified(self):
        value = readiness.normalize({})
        self.assertEqual(value['compute'], 'unknown')
        self.assertEqual(value['offline'], 'unknown')
        self.assertIsNone(value['setup_minutes'])
        self.assertEqual(value['platforms'], [])
        self.assertFalse(readiness.matches({}, {'max_download_mb': 100}))
        self.assertFalse(readiness.matches({}, {'offline': 'verified'}))
        self.assertTrue(readiness.matches({}, {}))

    def test_inline_evidence_overrides_curated_source_and_unknown_ids_fail(self):
        nodes = {'sample:a': {'kind': 'sample', 'readiness': {'hardware': 'required'}}}
        readiness.apply(nodes, {'sample:a': {'hardware': 'none', 'compute': 'cpu'}})
        self.assertEqual(nodes['sample:a']['readiness']['hardware'], 'required')
        self.assertEqual(nodes['sample:a']['readiness']['compute'], 'cpu')
        with self.assertRaisesRegex(ValueError, 'unknown record'):
            readiness.apply(nodes, {'sample:absent': {}})

    def test_invalid_measurements_and_values_are_rejected(self):
        for obj in ({'compute': 'fast'}, {'setup_minutes': -1}, {'download_mb': True},
                    {'setup_minutes': float('inf')}, {'platforms': 'linux'},
                    {'offline': 'verified'}, {'evidence': ['../../secret']}, {'typo': 3}):
            with self.subTest(obj=obj), self.assertRaises(ValueError):
                readiness.normalize(obj)

    def test_verified_offline_needs_existing_evidence_and_limitation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            obj = {'offline': 'verified', 'evidence': ['receipt.json'], 'limitation': 'One laptop only.'}
            with self.assertRaisesRegex(ValueError, 'evidence'):
                readiness.normalize(obj, root)
            (root / 'receipt.json').write_text('{}')
            self.assertEqual(readiness.normalize(obj, root)['offline'], 'verified')

    def test_filters_use_zero_and_unknown_correctly(self):
        record = {'readiness': readiness.normalize({'compute': 'cpu', 'hardware': 'none',
                  'setup_minutes': 0, 'download_mb': 42, 'platforms': ['macos-arm64']})}
        self.assertTrue(readiness.matches(record, {'max_setup_minutes': 0, 'max_download_mb': 42}))
        self.assertFalse(readiness.matches(record, {'max_download_mb': 41}))
        self.assertTrue(readiness.matches(record, {'platform': 'macos-arm64', 'compute': 'cpu'}))
        self.assertFalse(readiness.matches(record, {'platform': 'linux-amd64'}))

    def test_query_keeps_legacy_namespace_and_applies_constraints(self):
        record = {'id': 'sample:a', 'kind': 'sample', 'readiness': {'compute': 'cpu'}}
        args = SimpleNamespace(kind=None, fit=None, domain=None, concept=None)
        self.assertTrue(query.matches_filters(record, args))
        args.compute = 'gpu'
        self.assertFalse(query.matches_filters(record, args))
        args.compute = 'cpu'
        self.assertEqual([r['id'] for _, r in query.search({'sample:a': record}, '', args)], ['sample:a'])

    def test_mcp_validates_and_preserves_readiness_filters(self):
        args = mcp_server.filters({'compute': 'cpu', 'max_download_mb': 0, 'platform': 'macos-arm64'})
        self.assertEqual(args.compute, 'cpu')
        self.assertEqual(args.max_download_mb, 0)
        for bad in ({'max_setup_minutes': -1}, {'max_download_mb': True}, {'compute': 'fast'},
                    {'max_setup_minutes': '10'}, {'platform': ['macos-arm64']}):
            with self.subTest(bad=bad), self.assertRaises(mcp_server.ToolError):
                mcp_server.filters(bad)

    def test_build_and_mcp_preserve_constraints_and_limitations(self):
        rd = readiness.normalize({'compute': 'cpu', 'hardware': 'none', 'download_mb': 0,
                                  'limitation': 'Synthetic poses only.'})
        node = {'id': 'sample:a', 'title': 'A', 'kind': 'sample', '_dir': 'a', 'readiness': rd}
        with tempfile.TemporaryDirectory() as td, mock.patch.object(build, 'ROOT', Path(td)):
            build.write_records({'sample:a': node}, {})
            record = json.loads((Path(td) / 'index/records.jsonl').read_text())
            self.assertEqual(record['readiness'], rd)
            build.write_site({'sample:a': node}, [], {})
            compact = json.loads((Path(td) / 'site/data/index.json').read_text())['nodes'][0]
            self.assertEqual(compact['rd'], rd)
        self.assertEqual(mcp_server.brief(record)['readiness']['limitation'], 'Synthetic poses only.')


if __name__ == '__main__':
    unittest.main()
