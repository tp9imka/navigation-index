"""GNSS-SDR outputs => 1 Hz epochs (JSON lines) for score_scenario.py.

Position and receiver clock offset come from the PVT dump (pvt.mat, MATLAB v7.3 = HDF5, needs
h5py); per-SV C/N0 comes from the S1C column of GNSS-SDR's RINEX 3 observation file.
t is seconds since the scenario start (GPS TOW minus --t0-tow).
"""
import argparse
import glob
import json
import os

import h5py

SCENARIO_T0_TOW = 518400.0  # 2022-01-01 00:00:00 GPST, first epoch of gps-sdr-sim's brdc0010.22n


def rinex3_cn0(path):
    """Return {tow_s: {sv: cn0}} from a RINEX 3 obs file (GPS only, S1C column)."""
    out, obs_types, cur = {}, [], None
    with open(path) as f:
        for line in f:
            if "SYS / # / OBS TYPES" in line and line[0] == "G":
                obs_types = line[7:58].split()
            if "END OF HEADER" in line:
                break
        s1c = obs_types.index("S1C")
        for line in f:
            if line.startswith(">"):
                hh, mm, ss = int(line[13:15]), int(line[16:18]), float(line[19:29])
                cur = out.setdefault(round(SCENARIO_T0_TOW + hh * 3600 + mm * 60 + ss), {})
            elif cur is not None and line[0] == "G":
                field = line[3 + 16 * s1c:3 + 16 * s1c + 14].strip()
                if field:
                    cur[line[:3]] = float(field)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rx_dir")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    obs = glob.glob(os.path.join(a.rx_dir, "*.[0-9][0-9]O"))
    cn0 = rinex3_cn0(obs[0]) if obs else {}
    f = h5py.File(os.path.join(a.rx_dir, "pvt.mat"), "r")
    col = {k: f[k][:].ravel() for k in ("RX_time", "latitude", "longitude", "height",
                                        "user_clk_offset", "valid_sats")}
    seen, n = set(), 0
    with open(a.out, "w") as fo:
        for i, rx in enumerate(col["RX_time"]):
            tow = round(rx)
            if tow in seen or abs(rx - tow) > 0.011 or col["valid_sats"][i] == 0:
                continue
            seen.add(tow)
            ep = {"t": tow - SCENARIO_T0_TOW,
                  "lat": float(col["latitude"][i]), "lon": float(col["longitude"][i]),
                  "h": float(col["height"][i]),
                  "clk_bias_ns": float(col["user_clk_offset"][i]) * 1e9,
                  "valid_sats": int(col["valid_sats"][i]),
                  "cn0": cn0.get(tow, {})}
            fo.write(json.dumps(ep) + "\n")
            n += 1
    print(f"{a.out}: {n} epochs, {len(cn0)} RINEX epochs with C/N0")


if __name__ == "__main__":
    main()
