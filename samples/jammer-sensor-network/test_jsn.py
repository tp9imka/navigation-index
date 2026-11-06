import json
import math
import random
import threading
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET

import siblings  # noqa: F401
import jsn_aggregator as A
import jsn_localize as L
import jsn_model as M
import jsn_outputs as O
import jsn_protocol as P
import jsn_scenarios as S

HALF = 2000.0
AREA = (-HALF, -HALF, HALF, HALF)


def snapshot(jammers, sigma_db=0.0, n=16, seed=3, cal_err=0.0, obs=10):
    """[(Meas)] for n static nodes averaging `obs` epochs; jammers [(x, y, eirp)]."""
    rng = random.Random(seed)
    env = M.Environment(sigma_db=sigma_db, rng=rng)
    js = [M.Jammer(M.static_path((x, y)), e) for x, y, e in jammers]
    out = []
    for i, p in enumerate(S.node_layout(n, HALF, rng)):
        node = M.SimNode(f"s{i}", M.static_path(p), True, rng, agc_cal_err_db=cal_err)
        meta = {"static": True, **node.meta()}
        ms = []
        for t in range(obs):
            f, _ = node.observe(float(t), M.total_jammer_dbm(env, p, js, float(t)))
            ms.append(P.to_measurement({"id": node.id, "t": float(t), **f}, meta, f["xy"]))
        out.append(A._window_mean(ms))
    return out


class ModelTest(unittest.TestCase):
    def test_cn0_drop_inverts_and_is_sv_independent(self):
        for j in (-112.0, -100.0, -95.0):
            drops = [c - M.cn0_effective(c, j) for c in (38.0, 43.5, 48.0)]
            self.assertLess(max(drops) - min(drops), 1e-9)
            self.assertAlmostEqual(M.jammer_dbm_from_cn0_drop(drops[0]), j, places=6)
            self.assertAlmostEqual(M.cn0_drop_from_jammer_dbm(j), drops[0], places=6)

    def test_reference_values(self):
        # Q=2, Rc=1.023e6, N0=-172 dBm/Hz: 1 dB drop at about -114.8 dBm
        self.assertAlmostEqual(M.jammer_dbm_from_cn0_drop(1.0), -114.8, delta=0.1)
        self.assertAlmostEqual(M.cn0_effective(45.0, -200.0), 45.0, places=6)
        self.assertIsNone(M.jammer_dbm_from_cn0_drop(0.0))
        self.assertAlmostEqual(M.jammer_dbm_from_agc_reduction(M.agc_reduction_db(-100.0)), -100.0, places=6)

    def test_shadow_field_sigma_and_correlation(self):
        f = M.ShadowField(6.0, 50.0, random.Random(1))
        tx = (0.0, 0.0)
        vals = [f((x * 997.0, y * 991.0), tx) for x in range(30) for y in range(30)]
        sd = math.sqrt(sum(v * v for v in vals) / len(vals))
        self.assertTrue(4.5 < sd < 7.5, sd)
        near = [f((x * 997.0, 0.0), tx) - f((x * 997.0 + 5.0, 0.0), tx) for x in range(200)]
        self.assertLess(math.sqrt(sum(v * v for v in near) / len(near)), 2.0)

    def test_building_blockage(self):
        self.assertTrue(M.segment_hits_rect((0, 0), (10, 10), (4, 4, 6, 6)))
        self.assertFalse(M.segment_hits_rect((0, 0), (10, 0), (4, 4, 6, 6)))
        env = M.Environment(sigma_db=0, buildings=[(4, -1, 6, 1)], building_loss_db=15.0)
        self.assertAlmostEqual(env.received_dbm((0, 0), (10, 0), 0) - env.received_dbm((0, 0), (0, 10), 0), -15.0)

    def test_node_loses_fix_close_to_jammer(self):
        node = M.SimNode("v", M.static_path((0, 0)), False, random.Random(2))
        f, _ = node.observe(0.0, -80.0)
        self.assertEqual((f["fix"], f["nsv"], f["jst"], f["pf"]), (0, 0, M.JAM_STATE_CRITICAL, "dr"))
        f, _ = node.observe(1.0, None)
        self.assertEqual((f["fix"], f["jst"], f["pf"]), (1, M.JAM_STATE_OK, "gnss"))


class ProtocolTest(unittest.TestCase):
    def setUp(self):
        self.meta = P.make_meta("n1", 69.28, 16.03, True, hw="M8", agc_ref=5000, agc_db_per_cnt=1 / 60)
        node = M.SimNode("n1", M.static_path((0, 0)), True, random.Random(4))
        f, _ = node.observe(5.0, -105.0)
        self.obs = P.make_obs("n1", 69.28, 16.03, f)

    def test_valid_and_topic(self):
        P.validate(self.meta)
        P.validate(self.obs)
        self.assertEqual(P.topic(self.obs), "jsn/v1/n1/obs")
        line = f"jsn/v1/n1/meta {json.dumps(self.meta)}"
        self.assertEqual(P.parse_line(line), self.meta)
        with self.assertRaises(ValueError):
            P.parse_line(f"jsn/v1/n2/meta {json.dumps(self.meta)}")

    def test_rejects_bad_messages(self):
        for mut in ({"v": 2}, {"k": "x"}, {"jst": 7}, {"fix": True}, {"lat": 95.0}, {"pf": "wifi"},
                    {"cn0": "40"}):
            with self.subTest(mut=mut), self.assertRaises(ValueError):
                P.validate({**self.obs, **mut})
        bad = dict(self.obs)
        del bad["agc"]
        with self.assertRaises(ValueError):
            P.validate(bad)

    def test_measurement_kinds(self):
        rng = random.Random(5)
        node = M.SimNode("n", M.static_path((0, 0)), True, rng, agc_cal_err_db=0)
        meta = {"static": True, **node.meta()}
        clear, _ = node.observe(0.0, None)
        jam, _ = node.observe(1.0, -100.0)
        lost, _ = node.observe(2.0, -70.0)
        m = [P.to_measurement({"id": "n", **f}, meta, (0, 0)) for f in (clear, jam, lost)]
        self.assertEqual(m[0].kind, "upper")
        self.assertEqual(m[1].kind, "val")
        self.assertAlmostEqual(m[1].j_dbm, -100.0, delta=2.5)
        self.assertEqual((m[2].kind, m[2].source), ("val", "agc"))
        self.assertAlmostEqual(m[2].j_dbm, -70.0, delta=2.5)
        no_agc = P.to_measurement({"id": "n", **lost}, None, (0, 0))
        self.assertEqual(no_agc.kind, "lower")


class LocalizeTest(unittest.TestCase):
    def test_noiseless_single_source(self):
        meas = snapshot([(300.0, -200.0, 10.0)])
        ls = L.rss_ls(meas, AREA, sigma_sh=1.0)
        x, y, p0 = ls["sources"][0]
        self.assertLess(math.hypot(x - 300, y + 200), 30.0)
        self.assertAlmostEqual(p0 + M.FSPL_D0_DB, 10.0, delta=1.0)
        g = L.GridFilter(AREA, sigma_sh=1.0)
        g.set_static(meas)
        e = g.estimate()
        self.assertLess(math.hypot(e["x"] - 300, e["y"] + 200), 60.0)
        self.assertTrue(L.inside_ellipse(300 - e["x"], -200 - e["y"], e["cov"]))
        wc = L.weighted_centroid(meas)
        self.assertLess(math.hypot(wc[0] - 300, wc[1] + 200), 600.0)

    def test_two_sources_selected_only_when_present(self):
        two = snapshot([(-900.0, 600.0, 12.0), (800.0, -500.0, 12.0)], n=25)
        r = L.select_sources(two, AREA, sigma_sh=1.0)
        self.assertEqual(len(r["sources"]), 2)
        got = sorted((round(s[0]), round(s[1])) for s in r["sources"])
        self.assertLess(math.hypot(got[0][0] + 900, got[0][1] - 600), 80)
        self.assertLess(math.hypot(got[1][0] - 800, got[1][1] + 500), 80)
        one = snapshot([(300.0, -200.0, 12.0)], n=25)
        self.assertEqual(len(L.select_sources(one, AREA, sigma_sh=1.0)["sources"]), 1)

    def test_no_jammer_no_estimate(self):
        meas = snapshot([])
        self.assertTrue(all(m.kind == "upper" for m in meas))
        self.assertIsNone(L.weighted_centroid(meas))
        self.assertIsNone(L.rss_ls(meas, AREA))

    def test_censored_clear_nodes_push_mass_away(self):
        clear = [P.Meas("c", 0, 0.0, 0.0, 0.5, "upper", P.J_UPPER_CN0, 0.5, True, "clear")]
        g = L.GridFilter(AREA, n=21, sigma_sh=4.0)
        g.set_static(clear)
        cell = g.estimate()["cell_probs"]
        centre = min(range(len(g.cells)), key=lambda i: math.hypot(*g.cells[i]))
        self.assertLess(cell[centre], 1.0 / len(cell))

    def test_diffuse_spreads_mass(self):
        g = L.GridFilter(AREA, n=21, p0_range=(-30, -30), p0_step=1)
        g.R[0] = [0.0 if i == 220 else -50.0 for i in range(len(g.cells))]
        before = g.estimate()["cov"][0][0]
        g.diffuse(300.0)
        after = g.estimate()
        self.assertGreater(after["cov"][0][0], before + 300.0 ** 2 * 0.5)
        self.assertAlmostEqual(after["x"], g.cells[220][0], delta=40)

    def test_denial_radius(self):
        p0 = 10.0 - M.FSPL_D0_DB
        r = L.denial_radius_m(p0)
        j = p0 - 10 * M.PLE_DEFAULT * math.log10(r)
        self.assertAlmostEqual(43.5 - M.cn0_effective(43.5, j), 43.5 - M.TRACK_LOSS_CN0_DBHZ, delta=0.01)


class AggregatorHttpTest(unittest.TestCase):
    def test_round_trip(self):
        sc = S.build("static", seed=2, n_static=9, n_mobile=1, df=False)
        agg = A.Aggregator(*S.ORIGIN, S.HALF_M, grid_n=21)
        srv = A.serve(agg, port=0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{srv.server_address[1]}/v1"
        try:
            lines = []
            for n in sc.nodes:
                lat, lon, _ = agg.frame.to_geodetic(*n.path(0))
                lines.append(json.dumps(P.make_meta(n.id, lat, lon, n.static, **n.meta())))
            for t in range(20, 41):
                for n in sc.nodes:
                    f, _ = n.observe(float(t), M.total_jammer_dbm(sc.env, n.path(t), sc.jammers, float(t)))
                    lat, lon, _ = agg.frame.to_geodetic(*f["xy"])
                    msg = P.make_obs(n.id, lat, lon, f)
                    lines.append(f"{P.topic(msg)} {json.dumps(msg)}" if t % 2 else json.dumps(msg))
            lines.append(json.dumps({"v": 1, "k": "obs", "id": "bad"}))
            req = urllib.request.Request(base + "/msg", data="\n".join(lines).encode(), method="POST")
            with urllib.request.urlopen(req) as r:
                res = json.loads(r.read())
                self.assertEqual(r.status, 207)
            self.assertEqual(res["accepted"], len(lines) - 1)
            self.assertEqual(len(res["errors"]), 1)
            est = json.loads(urllib.request.urlopen(base + "/estimate").read())
            self.assertTrue(est["detected"])
            self.assertIn("grid", est["methods"])
            cot_xml = urllib.request.urlopen(base + "/cot").read().split(b"\n")
            types = [ET.fromstring(c).get("type") for c in cot_xml]
            self.assertEqual(types[:2], ["a-u-G", "u-d-c-e"])
            self.assertEqual(types.count(O.SENSOR_COT_TYPE), len(sc.nodes))
            zones = json.loads(urllib.request.urlopen(base + "/zones.geojson").read())
            self.assertIn("jamming", {f["properties"]["kind"] for f in zones["features"]})
            with self.assertRaises(urllib.error.HTTPError):
                urllib.request.urlopen(base + "/nope")
        finally:
            srv.shutdown()
            srv.server_close()


class OutputsTest(unittest.TestCase):
    def test_ellipse_ring_geometry(self):
        agg = A.Aggregator(*S.ORIGIN, S.HALF_M, grid_n=5)
        ring = O.ellipse_ring(agg.frame, 100.0, 50.0, (300.0, 100.0, 90.0))
        self.assertEqual(ring[0], ring[-1])
        pts = [agg.frame.to_enu(la, lo)[:2] for lo, la in ring]
        self.assertAlmostEqual(max(p[0] for p in pts), 400.0, delta=1.0)   # major axis east
        self.assertAlmostEqual(max(p[1] for p in pts), 150.0, delta=1.0)


if __name__ == "__main__":
    unittest.main()
