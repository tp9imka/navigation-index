"""Single-point positioning from a RINEX 3 OBS file with gnss_lib_py, scored against a CORS sheet.

UNVERIFIED SKETCH: written against gnss_lib_py 1.1.0 and georinex sources, syntax-checked only.
Requires: pip install gnss-lib-py (pulls georinex, numpy, pandas).

Usage:
  python3 glp_spp.py data/p730_r3.rnx --truth data/p730_20.coord.txt --epoch 2024.27 \
      --start "2024-04-09T12:00:00" --minutes 120
"""

import argparse
from datetime import datetime, timedelta, timezone

import georinex as gr
import gnss_lib_py as glp
import numpy as np

from compare_pos import ecef_delta_to_enu, ecef_to_geodetic, truth_at

EPHEM_DIR = "data/glp_ephem"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("obs", help="RINEX 3 observation file (glp parses 3.0x band codes like 1C)")
    ap.add_argument("--truth", required=True)
    ap.add_argument("--epoch", type=float, required=True)
    ap.add_argument("--start", required=True, help="UTC ISO time, e.g. 2024-04-09T12:00:00")
    ap.add_argument("--minutes", type=float, default=60.0)
    args = ap.parse_args()

    approx = gr.rinexheader(args.obs).get("position")
    print(f"RINEX header APPROX POSITION XYZ: {approx}")

    t0 = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
    window = [glp.datetime_to_gps_millis(t0),
              glp.datetime_to_gps_millis(t0 + timedelta(minutes=args.minutes))]

    obs = glp.RinexObs(args.obs)
    obs = obs.where("gps_millis", window, condition="between")
    obs = obs.where("gnss_id", "gps").where("signal_type", "l1")

    # Broadcast ephemeris; glp downloads the matching RINEX NAV into EPHEM_DIR if absent.
    full = glp.add_sv_states_rinex(obs, ephemeris_path=EPHEM_DIR, constellations=["gps"])
    # SV clock only; no iono/tropo model, so expect metre-level vertical bias.
    full["corr_pr_m"] = full["raw_pr_m"] + full["b_sv_m"]
    state = glp.solve_wls(full)

    xyz = np.vstack([state["x_rx_wls_m"], state["y_rx_wls_m"], state["z_rx_wls_m"]]).T
    truth = truth_at(args.truth, args.epoch)
    lat, lon, _ = ecef_to_geodetic(*truth)
    enu = np.array([ecef_delta_to_enu(row - np.array(truth), lat, lon) for row in xyz])
    enu = enu[~np.isnan(enu).any(axis=1)]
    rms = np.sqrt((enu**2).mean(axis=0))
    h95 = np.percentile(np.hypot(enu[:, 0], enu[:, 1]), 95)
    print(f"glp WLS SPP: {len(enu)} epochs  E/N/U rms = {rms[0]:.2f} / {rms[1]:.2f} / {rms[2]:.2f} m"
          f"  H95 = {h95:.2f} m")


if __name__ == "__main__":
    main()
