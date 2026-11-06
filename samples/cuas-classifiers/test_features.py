import math
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import pytest

import radar_features as rf_r
import rf_features as rf_s

DT = rf_r.UPDATE_DT_S


def straight_track(n=50, v=(3.0, 0.0, 4.0)):
    vel = np.tile(v, (n, 1))
    pos = np.cumsum(vel * DT, axis=0)
    return pos, vel


def circle_track(n=200, radius=20.0, speed=10.0):
    w = speed / radius
    t = np.arange(n) * DT
    # horizontal plane is (x, z); y is vertical
    pos = np.c_[radius * np.cos(w * t), np.full(n, 30.0), radius * np.sin(w * t)]
    vel = np.c_[-speed * np.sin(w * t), np.zeros(n), speed * np.cos(w * t)]
    return pos, vel


def test_straight_track_has_no_turn_or_accel():
    pos, vel = straight_track()
    f = rf_r.track_features(pos, vel, np.full(len(pos), -20.0))
    assert f["speed_mean"] == pytest.approx(5.0)
    assert f["accel_mean"] == pytest.approx(0.0, abs=1e-9)
    assert f["turn_rate_mean"] == pytest.approx(0.0, abs=1e-9)
    assert f["straightness"] == pytest.approx(1.0, abs=1e-6)
    assert f["climb_ratio"] == pytest.approx(0.0)


def test_circle_curvature_and_turn_rate():
    radius, speed = 20.0, 10.0
    pos, vel = circle_track(radius=radius, speed=speed)
    f = rf_r.track_features(pos, vel, np.full(len(pos), np.nan))
    assert f["curvature_median"] == pytest.approx(1 / radius, rel=0.02)
    assert f["turn_rate_mean"] == pytest.approx(speed / radius, rel=0.02)
    assert f["accel_mean"] == pytest.approx(speed ** 2 / radius, rel=0.02)
    assert f["rcs_missing_frac"] == 1.0
    assert math.isnan(f["rcs_mean"])


def test_vertical_axis_is_y():
    pos, vel = straight_track(v=(0.0, 2.0, 2.0))
    f = rf_r.track_features(pos, vel, np.zeros(len(pos)))
    assert f["vz_abs_mean"] == pytest.approx(2.0)
    assert f["climb_ratio"] == pytest.approx(1.0)


def test_rcs_stats_ignore_nan():
    pos, vel = straight_track(n=10)
    rcs = np.array([-10, np.nan, -20, np.nan, -30, -10, -20, -30, -10, -20], float)
    f = rf_r.track_features(pos, vel, rcs)
    assert f["rcs_missing_frac"] == pytest.approx(0.2)
    assert f["rcs_mean"] == pytest.approx(np.nanmean(rcs))


def test_session_key_merges_dual_radar_files():
    assert rf_r.session_key("tracks_2019-10-11T135549-R1.xlsx") == rf_r.session_key("tracks_2019-10-11T135549-R2.xlsx")
    assert rf_r.session_key("Echodyne_Log_20210318_100525.xlsx") == "Echodyne_Log_20210318_100525"


def test_load_dataset_joins_labels_and_drops_short_tracks(tmp_path):
    pos, vel = straight_track(n=20)
    rows = []
    for tid, n in ((7, 20), (8, 5)):
        for i in range(n):
            rows.append({"SystemTrackID": tid, "azimuth": 0, "elevation": 0, "range": 100,
                         "posX": pos[i, 0], "posY": pos[i, 1], "posZ": pos[i, 2],
                         "veloX": vel[i, 0], "veloY": vel[i, 1], "veloZ": vel[i, 2], "rcs": -15})
    rows.append({k: np.nan for k in rows[0]} | {"SystemTrackID": "N/A"})
    d = tmp_path / "data" / "Demo-9"
    d.mkdir(parents=True)
    with pd.ExcelWriter(d / "tracks_x-R1.xlsx") as w:
        pd.DataFrame(rows).to_excel(w, index=False, sheet_name="tracks")
        pd.DataFrame({"SystemTrackID": [7, 8], "Classification": ["UAV", "Bird"]}).to_excel(
            w, index=False, sheet_name="Sheet1")
    (tmp_path / "metadata").mkdir()
    pd.DataFrame({"folder": ["Demo-9", "Demo-9"], "file": ["tracks_x-R1.xlsx"] * 2,
                  "system_track_id": [7, 8], "label": ["UAV", "BIRD"]}).to_csv(
        tmp_path / "metadata" / "track_labels.csv", index=False)
    df = rf_r.load_dataset(tmp_path)
    assert list(df["track_id"]) == [7]
    assert df.iloc[0]["label"] == "UAV"
    assert df.iloc[0]["session"] == "Demo-9/tracks_x"
    assert df.iloc[0]["speed_mean"] == pytest.approx(5.0)


def test_band_power_peak_at_tone():
    n = 200_000
    t = np.arange(n)
    rng = np.random.default_rng(0)
    x = np.sin(2 * np.pi * 0.25 * t) * 5 + rng.normal(size=n)
    bp = rf_s.band_powers(x)
    assert int(np.argmax(bp)) == int(0.25 / 0.5 * rf_s.N_BANDS)
    assert np.median(bp) == pytest.approx(0.0)


def test_band_powers_gain_invariant():
    x = np.random.default_rng(1).normal(size=100_000)
    assert np.allclose(rf_s.band_powers(x), rf_s.band_powers(x * 37.0))


def test_burstiness_separates_bursty_from_stationary():
    rng = np.random.default_rng(2)
    n = 200_000
    steady = rng.normal(size=n)
    bursty = rng.normal(size=n) * 0.1
    for start in range(0, n, 20_000):
        bursty[start:start + 2_000] *= 30
    assert rf_s.burstiness(bursty)["env_p99_over_median_db"] > rf_s.burstiness(steady)["env_p99_over_median_db"] + 10
    assert rf_s.burstiness(bursty)["env_active_frac"] < 0.2


def test_segment_files_and_classes(tmp_path):
    seg = tmp_path / "RF Data_10100_L" / "10100L_3.csv"
    seg.parent.mkdir()
    x = np.random.default_rng(3).integers(-50, 50, size=50_000).astype(float)
    seg.write_text(",".join(f"{v:.6f}" for v in x))
    (tmp_path / "notes.csv").write_text("1,2,3")
    segs = list(rf_s.iter_segments(tmp_path))
    assert [(s[1], s[2], s[3], s[4]) for s in segs] == [("10100", "L", 3, "ar_drone")]
    assert np.array_equal(rf_s.read_segment(seg), x)
    feats = rf_s.segment_features(x)
    assert len(feats) == rf_s.N_WINDOWS
    assert len([k for k in feats[0] if k.startswith("band_")]) == rf_s.N_BANDS
    assert rf_s.bui_class("00000") == "background"
    assert rf_s.bui_class("10011") == "bebop"
    assert rf_s.bui_class("11000") == "phantom"


def test_cot_detection_event():
    import cuas_cot
    last = pd.Series({"azimuth": 90.0, "elevation": 0.0, "range": 1000.0,
                      "veloX": 0.0, "veloY": 0.0, "veloZ": 5.0})
    ev = ET.fromstring(cuas_cot.detection_event(42, 0.93, last, (45.0, -73.0, 10.0), boresight_deg=0.0))
    assert ev.get("type") == "a-u-A-M-H-Q"
    assert ev.get("how") == "m-a"
    pt = ev.find("point")
    assert float(pt.get("lat")) == pytest.approx(45.0, abs=1e-6)
    assert float(pt.get("lon")) > -73.0
    assert ev.find("detail/track").get("course") == "0.0"
    assert "P(UAV)=0.93" in ev.find("detail/remarks").text
