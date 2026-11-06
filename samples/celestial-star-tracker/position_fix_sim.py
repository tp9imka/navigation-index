"""Celestial position fix from star elevations above an IMU vertical, with error sweeps.

Truth: skyfield topocentric apparent alt/az (precession, nutation, aberration, refraction)
of Hipparcos stars from the cedar-solve database, seen from a known place and time through a
camera of given FOV. The navigator only gets: identified stars (as a plate solver gives),
their measured directions (centroid noise), a gravity-derived vertical (level bias,
vibration, accelerometer bias) and a clock (time error). It reduces each star to an observed
elevation, removes refraction with the Bennett formula, takes GHA/dec of the stars from
skyfield at its own clock time and solves the fix with celestial_geom.solve_fix (stdlib).

Needs the venv (numpy, skyfield, cedar-solve for the star table) and data/de421.bsp.
"""
import argparse
import dataclasses
import functools
import json
import math
import os
import time

import numpy as np
from skyfield.api import Loader, Star, wgs84

import celestial_geom as cg

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "results")
WGS84_A = 6378137.0
WGS84_E2 = 6.69437999014e-3
PRIOR_OFFSET_DEG = 1.0      # dead-reckoning prior handed to the solver, per axis
MIN_STARS = 3


@dataclasses.dataclass(frozen=True)
class Scenario:
    lat_deg: float = 50.0
    lon_deg: float = 10.0
    height_m: float = 0.0
    utc: tuple = (2026, 1, 15, 22, 0, 0)
    pressure_hpa: float = 1013.25
    temp_c: float = 10.0
    boresight_elev_deg: float = 60.0
    fov_deg: float = 20.0
    mag_max: float = 6.0
    centroid_noise_arcsec: float = 20.0
    level_err_arcmin: float = 0.0
    vib_sigma_deg: float = 0.0
    vib_samples: int = 1
    accel_bias_mg: float = 0.0
    time_err_s: float = 0.0
    correct_refraction: bool = True


@functools.lru_cache(maxsize=1)
def _eph():
    load = Loader(os.path.join(HERE, "data"), verbose=False)
    return load.timescale(builtin=True), load("de421.bsp")


@functools.lru_cache(maxsize=1)
def _catalog():
    import tetra3
    path = os.path.join(os.path.dirname(tetra3.__file__), "data", "default_database.npz")
    st = np.load(path)["star_table"]
    return st[:, 0].astype(float), st[:, 1].astype(float), st[:, 5].astype(float)


@functools.lru_cache(maxsize=64)
def _sky(sc_key):
    """Truth refracted alt/az (topocentric) and the navigator's apparent GHA/dec, per star."""
    lat, lon, h, utc, p, tc, mag_max, dt = sc_key
    ts, eph = _eph()
    ra, dec, mag = _catalog()
    sel = mag <= mag_max
    stars = Star(ra_hours=np.degrees(ra[sel]) / 15, dec_degrees=np.degrees(dec[sel]))
    t = ts.utc(*utc)
    earth = eph["earth"]
    obs = earth + wgs84.latlon(lat, lon, elevation_m=h)
    alt, az, _ = obs.at(t).observe(stars).apparent().altaz(temperature_C=tc, pressure_mbar=p)
    t_nav = ts.tt_jd(t.tt + dt / 86400.0)
    ra_d, dec_d, _ = earth.at(t_nav).observe(stars).apparent().radec(epoch="date")
    gha = np.radians(t_nav.gast * 15.0) - ra_d.radians
    return alt.radians, az.radians, gha, dec_d.radians


def _enu(h, az):
    return np.stack([np.cos(h) * np.sin(az), np.cos(h) * np.cos(az), np.sin(h)], -1)


def _small_rotation(vecs, sigma, rng):
    """Perturb each unit vector by an isotropic angular error of std `sigma` per axis."""
    if sigma == 0:
        return vecs
    a = np.cross(vecs, rng.normal(size=vecs.shape))
    a /= np.linalg.norm(a, axis=1, keepdims=True)
    b = np.cross(vecs, a)
    d = rng.normal(scale=sigma, size=(len(vecs), 2))
    out = vecs + d[:, :1] * a + d[:, 1:] * b
    return out / np.linalg.norm(out, axis=1, keepdims=True)


def _imu_up(sc, rng):
    """Up vector in the local ENU frame as the IMU senses it: (east, north) tilt components."""
    tilt = np.zeros(2)
    if sc.level_err_arcmin:
        d = rng.uniform(0, 2 * math.pi)
        tilt += math.radians(sc.level_err_arcmin / 60) * np.array([math.sin(d), math.cos(d)])
    if sc.accel_bias_mg:
        d = rng.uniform(0, 2 * math.pi)
        e = cg.level_error_from_accel(sc.accel_bias_mg * 1e-3 * cg.G0)
        tilt += e * np.array([math.sin(d), math.cos(d)])
    if sc.vib_sigma_deg:
        tilt += rng.normal(scale=math.radians(sc.vib_sigma_deg), size=(sc.vib_samples, 2)).mean(0)
    up = np.array([tilt[0], tilt[1], 1.0])
    return up / np.linalg.norm(up), float(np.hypot(*tilt))


def _err_m(lat, lon, lat_t, lon_t, h=0.0):
    s = math.sin(lat_t)
    w = math.sqrt(1 - WGS84_E2 * s * s)
    m_rad = WGS84_A * (1 - WGS84_E2) / w ** 3 + h
    n_rad = WGS84_A / w + h
    dn = (lat - lat_t) * m_rad
    de = ((lon - lon_t + math.pi) % (2 * math.pi) - math.pi) * n_rad * math.cos(lat_t)
    return math.hypot(dn, de), dn, de


def run_once(sc, seed=0):
    rng = np.random.default_rng(seed)
    key = (sc.lat_deg, sc.lon_deg, sc.height_m, sc.utc, sc.pressure_hpa, sc.temp_c, sc.mag_max,
           sc.time_err_s)
    alt, az, gha, dec = _sky(key)
    b_az = rng.uniform(0, 2 * math.pi)
    bore = _enu(math.radians(sc.boresight_elev_deg), b_az)
    v = _enu(alt, az)
    inside = (v @ bore > math.cos(math.radians(sc.fov_deg / 2))) & (alt > 0)
    idx = np.flatnonzero(inside)
    if len(idx) < MIN_STARS:
        return {"seed": seed, "n": int(len(idx)), "err_m": float("nan")}
    meas = _small_rotation(v[idx], math.radians(sc.centroid_noise_arcsec / 3600), rng)
    up, tilt = _imu_up(sc, rng)
    h_obs = np.arcsin(np.clip(meas @ up, -1, 1))
    obs = []
    for k, i in enumerate(idx):
        h = float(h_obs[k])
        if sc.correct_refraction:
            h -= cg.refraction_bennett(h, sc.pressure_hpa, sc.temp_c)
        obs.append((float(gha[i]), float(dec[i]), h))
    lat_t, lon_t = math.radians(sc.lat_deg), math.radians(sc.lon_deg)
    off = math.radians(PRIOR_OFFSET_DEG)
    sol = cg.solve_fix(obs, lat0=lat_t + rng.uniform(-off, off), lon0=lon_t + rng.uniform(-off, off))
    err, dn, de = _err_m(sol["lat"], sol["lon"], lat_t, lon_t, sc.height_m)
    return {"seed": seed, "n": len(obs), "err_m": err, "dn_m": dn, "de_m": de,
            "tilt_arcmin": math.degrees(tilt) * 60, "rms_arcsec": math.degrees(sol["rms"]) * 3600,
            "converged": sol["converged"]}


def sweep(sc, runs):
    rs = [run_once(sc, s) for s in range(runs)]
    ok = [r for r in rs if not math.isnan(r["err_m"])]
    e = np.array([r["err_m"] for r in ok])
    return {"runs": runs, "fixes": len(ok), "median_m": float(np.median(e)),
            "p95_m": float(np.percentile(e, 95)), "max_m": float(e.max()),
            "stars_median": float(np.median([r["n"] for r in ok])),
            "mean_abs_de_m": float(np.mean([abs(r["de_m"]) for r in ok])),
            "mean_abs_dn_m": float(np.mean([abs(r["dn_m"]) for r in ok])),
            "tilt_median_arcmin": float(np.median([r["tilt_arcmin"] for r in ok]))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=100)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    base = Scenario()
    res = {"scenario": dataclasses.asdict(base), "runs": a.runs}

    def row(label, sc, extra=""):
        s = sweep(sc, a.runs)
        print(f"  {label:34s} stars {s['stars_median']:4.0f}  median {s['median_m']:9.1f} m"
              f"  p95 {s['p95_m']:9.1f} m{extra}")
        return s

    print(f"Truth {base.lat_deg} N {base.lon_deg} E, {base.utc} UTC, camera {base.fov_deg} deg FOV"
          f" at {base.boresight_elev_deg} deg elevation, random azimuth, stars mag <= {base.mag_max};"
          f" {a.runs} runs per row\n")
    print("1. Floor: no level, vibration or clock error")
    res["floor"] = {
        "noise_free": row("centroid noise 0", dataclasses.replace(base, centroid_noise_arcsec=0)),
        "noise_20": row("centroid noise 20 arcsec/star", base),
        "noise_60": row("centroid noise 60 arcsec/star",
                        dataclasses.replace(base, centroid_noise_arcsec=60))}

    print("\n2. IMU level error (bias, random direction), centroid noise 20 arcsec")
    res["level"] = {}
    for lv in (0.5, 1, 2, 5, 10, 30):
        s = row(f"level error {lv} arcmin", dataclasses.replace(base, level_err_arcmin=lv))
        s["m_per_arcmin"] = s["median_m"] / lv
        print(f"  {'':34s} => {s['m_per_arcmin']:.0f} m per arcmin")
        res["level"][str(lv)] = s
    clean = [run_once(dataclasses.replace(base, centroid_noise_arcsec=0, level_err_arcmin=1.0), s)
             for s in range(a.runs)]
    slope = [r["err_m"] / r["tilt_arcmin"] for r in clean]
    res["level_slope_noise_free"] = {"min": min(slope), "max": max(slope),
                                     "mean": float(np.mean(slope))}
    print(f"  noise-free, 1 arcmin: {min(slope):.0f}-{max(slope):.0f} m per arcmin "
          f"(sphere R*1': {cg.position_error_from_level_error(cg.ARCMIN):.0f} m)")

    print("\n3. Clock error (east-west only), centroid noise 0 to isolate it")
    res["time"] = {}
    for dt in (0.1, 1, 10, 60):
        s = row(f"clock error {dt} s", dataclasses.replace(base, time_err_s=dt,
                                                                centroid_noise_arcsec=0))
        exp = cg.east_error_from_time_error(dt, math.radians(base.lat_deg))
        print(f"  {'':34s} => mean |dE| {s['mean_abs_de_m']:.0f} m, |dN| {s['mean_abs_dn_m']:.0f} m;"
              f" predicted R cos(lat) w dt = {exp:.0f} m")
        s["predicted_east_m"] = exp
        res["time"][str(dt)] = s

    print("\n4. Vibration: per-sample tilt noise averaged over K IMU samples (no bias)")
    res["vibration"] = {}
    for sig, k in ((0.5, 1), (0.5, 100), (0.5, 10000), (3.0, 10000)):
        s = row(f"sigma {sig} deg, K = {k}",
                dataclasses.replace(base, vib_sigma_deg=sig, vib_samples=k))
        res["vibration"][f"{sig}deg_K{k}"] = s

    print("\n5. Accelerometer bias / unmodelled horizontal acceleration")
    res["accel"] = {}
    for mg in (0.1, 1, 5, 10):
        s = row(f"{mg} mg => {cg.level_error_from_accel(mg * 1e-3 * cg.G0) / cg.ARCMIN:.2f} arcmin",
                dataclasses.replace(base, accel_bias_mg=mg))
        res["accel"][str(mg)] = s

    print("\n6. Refraction: corrected (Bennett) vs ignored, by boresight elevation, noise 0")
    res["refraction"] = {}
    for h_m, p, tc, tag in ((0.0, 1013.25, 10.0, "sea level"), (10000.0, 265.0, -50.0, "10 km")):
        for el in (30, 45, 60, 90):
            for corr in (True, False):
                sc = dataclasses.replace(base, centroid_noise_arcsec=0, height_m=h_m,
                                         pressure_hpa=p, temp_c=tc,
                                         boresight_elev_deg=el, correct_refraction=corr)
                lab = f"{tag}, elev {el}, {'corrected' if corr else 'ignored'}"
                res["refraction"][lab] = row(lab, sc)

    print("\n7. Field of view and star count")
    res["fov"] = {}
    for fov, mag in ((10, 6.0), (20, 4.0), (20, 6.0), (30, 6.0)):
        lab = f"FOV {fov} deg, mag <= {mag}"
        res["fov"][lab] = row(lab, dataclasses.replace(base, fov_deg=fov, mag_max=mag))

    res["elapsed_s"] = time.time() - t0
    with open(os.path.join(OUT, "position_fix.json"), "w") as f:
        json.dump(res, f, indent=1)
    print(f"\nwrote results/position_fix.json ({res['elapsed_s']:.0f} s)")


if __name__ == "__main__":
    main()
