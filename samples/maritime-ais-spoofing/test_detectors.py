"""Stdlib-only tests: python3 -m unittest -v (run from this directory)."""
import csv
import math
import os
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

import detectors as D
import evaluate
import export
import inject
from geo import circumradius_m, destination, haversine_m

HERE = os.path.dirname(os.path.abspath(__file__))
KN = D.KN_TO_MS
T0 = 1_793_664_000.0
LAT0, LON0 = 55.5, 11.0


def straight(mmsi=219000001, kn=10.0, brg=90.0, n=600, dt=10.0, ship_type="Cargo", length=150.0,
             mobile="Class A", lat=LAT0, lon=LON0):
    fixes = []
    for i in range(n):
        la, lo = destination(lat, lon, brg, kn * KN * dt * i)
        fixes.append(D.Fix(T0 + dt * i, la, lo, kn, brg, brg))
    return D.Track(mmsi, fixes, ship_type=ship_type, length_m=length, mobile=mobile, name=f"V{mmsi}")


def circling(mmsi, center, r, kn=10.0, n=200, dt=10.0, reported_cog=90.0, length=150.0, phase=0.0):
    omega = kn * KN / r
    fixes = []
    for i in range(n):
        la, lo = destination(center[0], center[1], math.degrees(phase + omega * dt * i), r)
        fixes.append(D.Fix(T0 + dt * i, la, lo, kn, reported_cog, reported_cog))
    return D.Track(mmsi, fixes, ship_type="Cargo", length_m=length)


def kinds(flags):
    return {f.kind for f in flags}


class GeoTest(unittest.TestCase):
    def test_destination_roundtrip(self):
        la, lo = destination(LAT0, LON0, 45.0, 10_000.0)
        self.assertAlmostEqual(haversine_m(LAT0, LON0, la, lo), 10_000.0, delta=1.0)

    def test_circumradius(self):
        pts = [destination(LAT0, LON0, b, 500.0) for b in (0, 70, 150)]
        self.assertAlmostEqual(circumradius_m(*pts), 500.0, delta=5.0)
        line = [destination(LAT0, LON0, 90, d) for d in (0, 100, 200)]
        self.assertGreater(circumradius_m(*line), 1e5)


class KinematicTest(unittest.TestCase):
    def test_clean_straight_track_is_silent(self):
        tr = straight()
        self.assertEqual(D.detect_kinematic(tr) + D.detect_turn(tr), [])

    def test_teleport_is_jump(self):
        tr = straight()
        tr.fixes = [f._replace(**dict(zip(("lat", "lon"), destination(f.lat, f.lon, 0, 30_000))))
                    if 200 <= i < 300 else f for i, f in enumerate(tr.fixes)]
        jumps = [f for f in D.detect_kinematic(tr) if f.kind == "jump"]
        self.assertEqual([round(f.t) for f in jumps], [round(tr.fixes[200].t), round(tr.fixes[300].t)])

    def test_sub_threshold_offset_is_not_a_jump(self):
        tr = straight()
        tr.fixes = [f._replace(**dict(zip(("lat", "lon"), destination(f.lat, f.lon, 0, 300))))
                    if i >= 200 else f for i, f in enumerate(tr.fixes)]
        self.assertNotIn("jump", kinds(D.detect_kinematic(tr)))

    def test_sustained_impossible_speed(self):
        tr = straight(kn=60.0, dt=2.0, ship_type="Tanker")
        self.assertIn("speed", kinds(D.detect_kinematic(tr)))
        hsc = straight(kn=40.0, dt=2.0, ship_type="HSC")
        self.assertNotIn("speed", kinds(D.detect_kinematic(hsc)))

    def test_reported_sog_and_cog_mismatch(self):
        tr = straight(kn=10.0)
        tr.fixes = [f._replace(sog=2.0) for f in tr.fixes]
        self.assertIn("sog_mismatch", kinds(D.detect_kinematic(tr)))
        tr = straight(kn=10.0, brg=0.0)
        tr.fixes = [f._replace(cog=90.0) for f in tr.fixes]
        self.assertIn("cog_mismatch", kinds(D.detect_kinematic(tr)))

    def test_stale_repeat_dropped_frozen_run_kept(self):
        tr = straight(n=10)
        fx = list(tr.fixes)
        fx[5] = fx[5]._replace(lat=fx[4].lat, lon=fx[4].lon)
        self.assertEqual(len(D.drop_stale_repeats(D.Track(1, fx)).fixes), 9)
        frozen = fx[:4] + [fx[3]._replace(t=fx[k].t) for k in range(4, 10)]
        self.assertEqual(len(D.drop_stale_repeats(D.Track(1, frozen)).fixes), 10)
        self.assertIn("sog_mismatch", kinds(D.detect_kinematic(D.Track(1, frozen + [
            fx[9]._replace(t=fx[9].t + 60 * k, lat=fx[3].lat, lon=fx[3].lon) for k in range(1, 6)]))))

    def test_turn_radius_vs_length(self):
        tr = circling(1, (LAT0, LON0), r=100.0, kn=8.0, length=200.0)
        self.assertIn("turn", kinds(D.detect_turn(tr)))
        small = circling(2, (LAT0, LON0), r=100.0, kn=8.0, length=30.0)
        self.assertEqual(D.detect_turn(small), [])


class LoiterClusterTest(unittest.TestCase):
    def test_crop_circle_cluster(self):
        c = (LAT0, LON0)
        tracks = [circling(219000100 + k, c, r=400.0, phase=k) for k in range(4)]
        fl = D.detect_loiter_and_clusters(tracks)
        self.assertIn("loiter_underway", kinds(fl))
        self.assertEqual({f.mmsi for f in fl if f.kind == "cluster"}, {t.mmsi for t in tracks})

    def test_two_circlers_are_not_a_cluster(self):
        tracks = [circling(219000200 + k, (LAT0, LON0), r=400.0, phase=k) for k in range(2)]
        self.assertNotIn("cluster", kinds(D.detect_loiter_and_clusters(tracks)))

    def test_moored_or_transiting_vessels_do_not_loiter(self):
        moored = straight(mmsi=219000300, kn=0.0)
        transit = straight(mmsi=219000301, kn=12.0)
        self.assertEqual(D.detect_loiter_and_clusters([moored, transit]), [])


class LandAndMmsiTest(unittest.TestCase):
    def test_on_land_needs_motion(self):
        tr = straight(n=20)
        mask = [True] * 20
        self.assertTrue(D.detect_on_land(tr, mask))
        tr.fixes = [f._replace(sog=0.0) for f in tr.fixes]
        self.assertEqual(D.detect_on_land(tr, mask), [])

    def test_mmsi_rules(self):
        self.assertEqual(D.mmsi_anomalies(219000001, "Class A"), [])
        self.assertEqual(D.mmsi_anomalies(97000106, "Class B"), ["mmsi_not_ship"])
        self.assertEqual(D.mmsi_anomalies(2190045, "Base Station"), [])
        self.assertEqual(D.mmsi_anomalies(555555555, "Class B"), ["mmsi_placeholder"])
        self.assertEqual(D.mmsi_anomalies(200123456, "Class A"), ["mmsi_bad_mid"])
        self.assertIn("mmsi_length", D.mmsi_anomalies(1234567890, "Class A"))


def load_fixture():
    tracks = {}
    with open(os.path.join(HERE, "fixtures", "dma_excerpts.csv")) as fh:
        for r in csv.DictReader(fh):
            t = datetime.strptime(r["# Timestamp"], "%d/%m/%Y %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            lat, lon = float(r["Latitude"]), float(r["Longitude"])
            if abs(lat) > 90:
                continue
            m = int(r["MMSI"])
            tr = tracks.setdefault(m, D.Track(m, [], ship_type="Cargo", mobile=r["Type of mobile"]))
            if tr.fixes and tr.fixes[-1].t == t:
                continue
            tr.fixes.append(D.Fix(t, lat, lon, float(r["SOG"]) if r["SOG"] else None,
                                  float(r["COG"]) if r["COG"] else None, None))
    return tracks


class RealExcerptTest(unittest.TestCase):
    """Two DMA excerpts (Danish Maritime Authority data): one MMSI reported both in Copenhagen
    and in the North Sea; a moored Class B with one fix 20 km inland."""

    def test_shared_mmsi(self):
        tr = load_fixture()[246843000]
        kin = D.detect_kinematic(tr)
        self.assertIn("mmsi_shared", kinds(D.detect_mmsi(tr, kin)))

    def test_inland_teleport(self):
        tr = load_fixture()[219003959]
        jumps = [f for f in D.detect_kinematic(tr) if f.kind == "jump"]
        self.assertEqual(len(jumps), 1)
        self.assertAlmostEqual(jumps[0].lat, 57.417832, places=5)


class PipelineTest(unittest.TestCase):
    def test_aggregate_rules(self):
        weak = [D.Flag(1, T0 + 10 * k, LAT0, LON0, "sog_mismatch", "") for k in range(2)]
        self.assertEqual(D.aggregate(weak), [])
        self.assertEqual(len(D.aggregate(weak + [D.Flag(1, T0 + 30, LAT0, LON0, "cog_mismatch", "")])), 1)
        self.assertEqual(len(D.aggregate([D.Flag(1, T0, LAT0, LON0, "jump", "")])), 1)
        split = [D.Flag(1, T0, LAT0, LON0, "jump", ""), D.Flag(1, T0 + 5000, LAT0, LON0, "jump", "")]
        self.assertEqual(len(D.aggregate(split)), 2)

    def test_inject_detect_score(self):
        tracks = [straight(mmsi=219001000 + k, lat=LAT0 + 0.1 * k, n=720) for k in range(6)]
        inj, eps = inject.inject(tracks, n_offset=2, n_drift=0, n_circle=2, n_groups=0, seed=3)
        self.assertEqual(len(eps), 4)
        for e in eps:
            self.assertEqual(e.end - e.start, inject.EPISODE_S)
        alerts = D.aggregate(D.run_all(inj))
        rows, totals = evaluate.score(alerts, [e for e in eps if e.kind == "circle" or e.param > 1000])
        self.assertTrue(all(r["detected"] for r in rows))
        self.assertEqual(totals["fp_alerts_on_injected"], 0)
        self.assertEqual(D.aggregate(D.run_all(tracks)), [])

    def test_cot_and_geojson(self):
        tr = straight(mmsi=219002000, n=100)
        tr.fixes = [f._replace(lat=f.lat + 0.3) if i >= 50 else f for i, f in enumerate(tr.fixes)]
        alerts = D.aggregate(D.run_all([tr]))
        self.assertEqual(len(alerts), 1)
        ev = ET.fromstring(export.to_cot(alerts[0], tr))
        self.assertEqual(ev.get("type"), export.VESSEL_COT_TYPE)
        self.assertAlmostEqual(float(ev.find("point").get("lat")), tr.fixes[49].lat, places=6)
        self.assertIn("jump", ev.find("detail/remarks").text)
        gj = export.to_geojson(alerts, {tr.mmsi: tr})
        roles = {f["properties"]["role"] for f in gj["features"]}
        self.assertEqual(roles, {"last_flagged_position", "last_pre_alert_position"})


if __name__ == "__main__":
    unittest.main()
