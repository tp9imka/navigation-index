"""Single-point positioning from a RINEX 3 OBS file with gnss_lib_py, scored against a CORS sheet.

Ran with gnss_lib_py 1.1.0 on the P730 file converted to RINEX 3.04 by run_in_docker.sh.
Requires: pip install -r requirements.txt (gnss-lib-py pulls georinex, numpy, pandas).

Three fixes on top of plain glp calls, all needed to get metre-level results:
- glp 1.1.0 RinexObs tags RINEX epochs (GPS time) as UTC and adds the leap seconds, so
  every SV is propagated to the wrong second (km-level errors). We subtract them back.
- add_sv_states_rinex picks one ephemeris per SV at the earliest epoch of its input and
  extrapolates it for the whole input (residuals grew to ~25 m over 2 h here), so it is
  called on EPHEM_CHUNK_MIN chunks.
- add_sv_states_rinex evaluates SVs at the receive time unless receiver position rows
  exist, so a second pass feeds the first WLS fix back for transmit-time SV states.
A third pass adds a 15 deg elevation mask and glp's tropo + Klobuchar iono models
(alpha/beta parsed from the broadcast nav header). solve_wls already applies the
Earth-rotation correction itself.

Usage:
  python3 glp_spp.py data/p730_r3.rnx --truth data/p730_20.coord.txt --epoch 2024.27 \
      --start "2024-04-09T12:00:00" --minutes 120
"""

import argparse
import gzip
from datetime import datetime, timedelta, timezone

import georinex as gr
import gnss_lib_py as glp
import numpy as np

from compare_pos import ecef_delta_to_enu, ecef_to_geodetic, truth_at

EPHEM_DIR = "data/glp_ephem"
MS_PER_S = 1000
EPHEM_CHUNK_MIN = 15
ELEV_MASK_DEG = 15.0  # same as rnx2rtkp -m 15 in run_rtklib.sh


def sv_states(obs):
    """add_sv_states_rinex per chunk, so each chunk gets the ephemeris current at its start."""
    chunk_ms = EPHEM_CHUNK_MIN * 60 * MS_PER_S
    t = obs["gps_millis"]
    parts = []
    for start in np.arange(t.min(), t.max() + 1, chunk_ms):
        part = obs.where("gps_millis", [start, start + chunk_ms - 1], condition="between")
        if len(part):
            parts.append(glp.add_sv_states_rinex(part, ephemeris_path=EPHEM_DIR,
                                                 constellations=["gps"]))
    return glp.concat(*parts)


def klobuchar_params(nav_path):
    """{"gps": 2x4 [alpha; beta]} from the ION ALPHA / ION BETA lines of a RINEX 2 nav header."""
    opener = gzip.open if nav_path.endswith(".gz") else open
    rows = {}
    with opener(nav_path, "rt") as fh:
        for line in fh:
            label = line[60:].strip()
            if label in ("ION ALPHA", "ION BETA"):
                rows[label] = [float(line[2 + 12 * i:14 + 12 * i].replace("D", "E")) for i in range(4)]
            if label == "END OF HEADER":
                break
    return {"gps": np.array([rows["ION ALPHA"], rows["ION BETA"]])}


def corrected(full, iono_params):
    """Per epoch: drop SVs below the mask, remove tropo + iono delay from corr_pr_m."""
    frames = []
    for _, _, frame in glp.loop_time(full, "gps_millis"):
        rx = np.array([[frame["x_rx_m"][0]], [frame["y_rx_m"][0]], [frame["z_rx_m"][0]]])
        sv = np.vstack([frame["x_sv_m"], frame["y_sv_m"], frame["z_sv_m"]])
        el = glp.ecef_to_el_az(rx, sv)[0]
        state = glp.NavData()
        for row, val in zip(["x_rx_m", "y_rx_m", "z_rx_m", "vx_rx_mps", "vy_rx_mps",
                             "vz_rx_mps", "b_rx_m", "b_dot_rx_mps"], [*rx.ravel(), 0, 0, 0, 0, 0]):
            state[row] = np.array([val])
        tropo, iono = glp.calculate_pseudorange_corr(frame["gps_millis"][0], state=state,
                                                     sv_posvel=frame, iono_params=iono_params)
        frame["corr_pr_m"] = frame["raw_pr_m"] + frame["b_sv_m"] - tropo - iono
        frames.append(frame.copy(cols=np.flatnonzero(el >= ELEV_MASK_DEG)))
    return glp.concat(*frames)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("obs", help="RINEX 3 observation file (glp parses 3.0x band codes like 1C)")
    ap.add_argument("--truth", required=True)
    ap.add_argument("--epoch", type=float, required=True)
    ap.add_argument("--start", required=True, help="GPS time (as in rnx2rtkp -ts), e.g. 2024-04-09T12:00:00")
    ap.add_argument("--minutes", type=float, default=60.0)
    ap.add_argument("--nav-header", default="data/brdc1000.24n.gz",
                    help="RINEX 2 nav file whose header carries ION ALPHA / ION BETA")
    args = ap.parse_args()

    approx = gr.rinexheader(args.obs).get("position")
    print(f"RINEX header APPROX POSITION XYZ: {approx}")

    t0 = datetime.fromisoformat(args.start).replace(tzinfo=timezone.utc)
    leap_ms = glp.get_leap_seconds(t0) * MS_PER_S
    # glp converts a UTC datetime; the start is GPS time, so take the leap seconds back off
    window = [glp.datetime_to_gps_millis(t0) - leap_ms,
              glp.datetime_to_gps_millis(t0 + timedelta(minutes=args.minutes)) - leap_ms]

    obs = glp.RinexObs(args.obs)
    obs["gps_millis"] = obs["gps_millis"] - leap_ms
    obs = obs.where("gps_millis", window, condition="between")
    obs = obs.where("gnss_id", "gps").where("signal_type", "l1")

    # Broadcast ephemeris: glp downloads the day's RINEX NAV into EPHEM_DIR if absent.
    full = sv_states(obs)
    # SV clock only; no iono/tropo model, so expect metre-level vertical bias.
    full["corr_pr_m"] = full["raw_pr_m"] + full["b_sv_m"]
    state = glp.solve_wls(full)
    print(f"pass 1 (SV states at receive time): {score(state, args)}")

    # pass 2: SV states at transmit time, using the pass-1 fix as receiver position
    rx_by_t = {t: (x, y, z) for t, x, y, z in zip(state["gps_millis"], state["x_rx_wls_m"],
                                                   state["y_rx_wls_m"], state["z_rx_wls_m"])}
    rx = np.array([rx_by_t[t] for t in obs["gps_millis"]])
    obs["x_rx_m"], obs["y_rx_m"], obs["z_rx_m"] = rx[:, 0], rx[:, 1], rx[:, 2]
    full = sv_states(obs)
    full["corr_pr_m"] = full["raw_pr_m"] + full["b_sv_m"]
    state = glp.solve_wls(full)
    print(f"pass 2 (SV states at transmit time): {score(state, args)}")

    full = corrected(full, klobuchar_params(args.nav_header))
    state = glp.solve_wls(full)
    print(f"pass 3 (+{ELEV_MASK_DEG:g} deg mask, tropo, Klobuchar): {score(state, args)}")


def score(state, args):
    xyz = np.vstack([state["x_rx_wls_m"], state["y_rx_wls_m"], state["z_rx_wls_m"]]).T
    truth = truth_at(args.truth, args.epoch)
    lat, lon, _ = ecef_to_geodetic(*truth)
    enu = np.array([ecef_delta_to_enu(row - np.array(truth), lat, lon) for row in xyz])
    enu = enu[~np.isnan(enu).any(axis=1)]
    rms = np.sqrt((enu**2).mean(axis=0))
    h95 = np.percentile(np.hypot(enu[:, 0], enu[:, 1]), 95)
    return (f"{len(enu)} epochs  E/N/U rms = {rms[0]:.2f} / {rms[1]:.2f} / {rms[2]:.2f} m"
            f"  H95 = {h95:.2f} m")


if __name__ == "__main__":
    main()
