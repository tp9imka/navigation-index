"""Real-data plausibility check: where were the 8 ESA tetra3 test images taken?

The file names give the mount's nominal pointing (Alt40/60, Azi +-45/+-135) and a timestamp
(2019-07-29T204726, assumed UTC). cedar-solve gives each frame's J2000 RA/Dec. Converting
those to apparent-of-date coordinates with skyfield and fitting latitude, longitude and the
mount's altitude/azimuth zero offsets gives a position. The capture site is not documented
in either repo, so there is no ground truth; the README compares the result with ESA ESTEC.

Needs results/plate_solve.json (plate_solve_eval.py) and the venv.
"""
import json
import math
import os
import re

import numpy as np
from scipy.optimize import least_squares
from skyfield.api import Loader, Star

HERE = os.path.dirname(os.path.abspath(__file__))
UTC = (2019, 7, 29, 20, 47, 26)
ESTEC_LAT, ESTEC_LON = 52.2183, 4.4206    # approximate; Wikipedia infobox 52 13 N 4 25 E
START_GRID = [(la, lo) for la in (-60, -20, 20, 60) for lo in range(-180, 180, 45)]


def unit(ra, dec):
    return np.array([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])


def predicted(p, alt, az, gast, fit_mount):
    lat, lon = p[0], p[1]
    dalt, daz = (p[2], p[3]) if fit_mount else (0.0, 0.0)
    a, A = alt + dalt, az + daz
    dec = np.arcsin(np.sin(lat) * np.sin(a) + np.cos(lat) * np.cos(a) * np.cos(A))
    ha = np.arctan2(-np.sin(A) * np.cos(a),
                    np.cos(lat) * np.sin(a) - np.sin(lat) * np.cos(a) * np.cos(A))
    return unit(gast + lon - ha, dec)


def fit(obs, gast, fit_mount):
    def res(p):
        return np.concatenate([predicted(p, al, az, gast, fit_mount) - unit(ra, de)
                               for al, az, ra, de in obs])
    best = None
    for la, lo in START_GRID:
        p0 = [math.radians(la), math.radians(lo)] + ([0.0, 0.0] if fit_mount else [])
        s = least_squares(res, p0)
        if best is None or s.cost < best.cost:
            best = s
    r = res(best.x).reshape(-1, 3)
    return best.x, np.degrees(np.linalg.norm(r, axis=1))


def main():
    sol = json.load(open(os.path.join(HERE, "results", "plate_solve.json")))
    rows = [r for r in sol["cedar"] if r["name"].startswith("2019-07-29") and "RA" in r]
    load = Loader(os.path.join(HERE, "data"), verbose=False)
    ts, eph = load.timescale(builtin=True), load("de421.bsp")
    t = ts.utc(*UTC)
    obs = []
    for r in rows:
        m = re.search(r"Alt(-?\d+)_Azi(-?\d+)", r["name"])
        star = Star(ra_hours=r["RA"] / 15, dec_degrees=r["Dec"])
        ra, dec, _ = eph["earth"].at(t).observe(star).apparent().radec(epoch="date")
        obs.append((math.radians(float(m[1])), math.radians(float(m[2])), ra.radians, dec.radians))
    gast = math.radians(t.gast * 15)
    print(f"{len(obs)} solved frames, timestamp {UTC} taken as UTC")
    for fit_mount in (False, True):
        p, resid = fit(obs, gast, fit_mount)
        lat, lon = math.degrees(p[0]), (math.degrees(p[1]) + 180) % 360 - 180
        dn = (lat - ESTEC_LAT) * 111.2
        de = (lon - ESTEC_LON) * 111.2 * math.cos(math.radians(lat))
        label = "lat, lon, mount alt/az offsets" if fit_mount else "lat, lon only"
        extra = (f", mount offsets alt {math.degrees(p[2]):+.2f} deg az {math.degrees(p[3]):+.2f}"
                 f" deg" if fit_mount else "")
        print(f"fit {label}: {lat:.3f} N {lon:.3f} E{extra}")
        print(f"  per-frame residual deg: {' '.join(f'{x:.2f}' for x in resid)}")
        print(f"  distance to ESTEC (unverified site): {math.hypot(dn, de):.1f} km "
              f"(N {dn:+.1f}, E {de:+.1f})")


if __name__ == "__main__":
    main()
