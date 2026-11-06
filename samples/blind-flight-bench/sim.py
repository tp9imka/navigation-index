"""Blind-flight scenario generator: truth flight, world surface, radar altimeter, NMEA stream.

Frame: east/north metres in the DEM grid (row 0 = south, cell (i, j) at north=i*res, east=j*res).
Azimuth is degrees clockwise from north, so the unit direction is (sin az, cos az).
"""
from dataclasses import dataclass, field

import numpy as np
from scipy.ndimage import gaussian_filter

from ext import hpf_core

bilinear = hpf_core.bilinear

FLIGHT_MSL_M = 1500.0          # constant barometric flight level from the case statement
SAMPLE_HZ = 10.0               # case allows 1-10 Hz
FLIGHT_LEN_M = 20_500.0        # 20 km checkpoint plus a little slack
EDGE_MARGIN_M = 3_000.0        # keeps search windows and the beam footprint on the map
MIN_CLEARANCE_M = 200.0
SIM_DT = 0.1


@dataclass
class RadarModel:
    beam_full_deg: float = 40.0      # assumption: typical wide-beam radar altimeter, not a datasheet value
    noise_m: float = 0.5
    noise_frac: float = 0.005        # range-proportional noise, 0.5% => ~5 m at 1000 m AGL
    dropout_p: float = 0.02          # independent lost messages
    burst_p: float = 0.002           # per-sample chance a 1-5 s loss of lock starts
    burst_s: tuple = (1.0, 5.0)
    outlier_p: float = 0.005
    outlier_m: tuple = (30.0, 300.0)
    footprint: bool = True           # False => ideal nadir point measurement
    rings: int = 16
    spokes: int = 24


@dataclass
class AltRefModel:
    bias_sigma_m: float = 25.0       # QNH / temperature error of the 1500 m baro reference
    drift_sigma_mps: float = 0.03
    wander_sigma_m: float = 3.0      # altitude-hold wander, AR(1)
    wander_tau_s: float = 20.0


@dataclass
class WorldModel:
    dem_err_sigma_m: float = 3.0     # GLO-30 vs reality, spatially correlated
    dem_err_corr_m: float = 150.0
    forest_frac: float = 0.4         # share of the map where the radar sees partly through canopy
    penetration_m: tuple = (2.0, 8.0)  # assumption, see README


@dataclass
class Scenario:
    family: str = "straight"         # "straight" (organiser-style) or "turns"
    radar: RadarModel = field(default_factory=RadarModel)
    altref: AltRefModel = field(default_factory=AltRefModel)
    world: WorldModel = field(default_factory=WorldModel)
    start_sigma_m: float = 30.0      # last GNSS fix before the outage
    heading_hint_sigma_deg: float = 5.0
    speed_hint_sigma_mps: float = 2.0
    sample_hz: float = SAMPLE_HZ


def smooth_field(shape, sigma_cells, rng):
    f = gaussian_filter(rng.standard_normal(shape), sigma_cells)
    return f / (f.std() + 1e-12)


def world_surface(dem, res, wm, rng):
    """What the radar actually ranges to: DEM + correlated map error - canopy penetration."""
    err = wm.dem_err_sigma_m * smooth_field(dem.shape, wm.dem_err_corr_m / res, rng)
    f = smooth_field(dem.shape, 300.0 / res, rng)
    forest = f > np.quantile(f, 1 - wm.forest_frac)
    lo, hi = wm.penetration_m
    pen = lo + (hi - lo) * (0.5 + 0.5 * np.tanh(smooth_field(dem.shape, 100.0 / res, rng)))
    return dem + err - forest * pen


def make_track(family, rng):
    """Truth path in a local frame starting at the origin, sampled every SIM_DT."""
    psi = rng.uniform(0, 360)
    v0 = rng.uniform(30, 55)
    t, e, n, s = 0.0, 0.0, 0.0, 0.0
    T, E, N, PSI, V, S = [0.0], [0.0], [0.0], [psi], [v0], [0.0]
    v = v0
    next_turn = rng.uniform(3000, 7000)
    turn_left = 0.0
    turn_rate = 3.0
    while s < FLIGHT_LEN_M:
        if family == "turns":
            if turn_left == 0.0 and s >= next_turn:
                turn_left = rng.uniform(30, 120) * rng.choice([-1, 1])
                next_turn = s + rng.uniform(3000, 7000)
            if turn_left != 0.0:
                d = np.sign(turn_left) * min(abs(turn_left), turn_rate * SIM_DT)
                psi += d
                turn_left -= d
                if abs(turn_left) < 1e-9:
                    turn_left = 0.0
            v += (v0 - v) * SIM_DT / 60.0 + 2.0 * np.sqrt(2 * SIM_DT / 60.0) * rng.standard_normal()
        a = np.radians(psi)
        e += v * np.sin(a) * SIM_DT
        n += v * np.cos(a) * SIM_DT
        s += v * SIM_DT
        t += SIM_DT
        T.append(t), E.append(e), N.append(n), PSI.append(psi), V.append(v), S.append(s)
    return {k: np.array(x) for k, x in zip(("t", "e", "n", "psi", "v", "s"), (T, E, N, PSI, V, S))}


def place_track(track, dem, res, rng, tries=200):
    h, w = dem.shape
    e_lo, e_hi = track["e"].min(), track["e"].max()
    n_lo, n_hi = track["n"].min(), track["n"].max()
    for _ in range(tries):
        e0 = rng.uniform(EDGE_MARGIN_M - e_lo, (w - 1) * res - EDGE_MARGIN_M - e_hi)
        n0 = rng.uniform(EDGE_MARGIN_M - n_lo, (h - 1) * res - EDGE_MARGIN_M - n_hi)
        if not (np.isfinite(e0) and np.isfinite(n0)):
            return None
        ground = bilinear(dem, track["e"] + e0, track["n"] + n0, res)
        if np.nanmax(ground) < FLIGHT_MSL_M - MIN_CLEARANCE_M:
            out = dict(track)
            out["e"] = track["e"] + e0
            out["n"] = track["n"] + n0
            return out
    return None


def altitude_truth(t, am, rng, dt):
    bias = am.bias_sigma_m * rng.standard_normal()
    drift = am.drift_sigma_mps * rng.standard_normal()
    a = np.exp(-dt / am.wander_tau_s)
    w = np.zeros_like(t)
    w[0] = am.wander_sigma_m * rng.standard_normal()
    q = am.wander_sigma_m * np.sqrt(1 - a * a)
    for k in range(1, len(t)):
        w[k] = a * w[k - 1] + q * rng.standard_normal()
    return FLIGHT_MSL_M + bias + drift * t + w, bias


def radar_range(surface, res, e, n, alt, rm):
    """Leading-edge range: nearest surface point inside the beam cone (flat attitude)."""
    nadir = alt - bilinear(surface, e, n, res)
    if not rm.footprint:
        return nadir
    half = np.radians(rm.beam_full_deg / 2)
    rmax = np.maximum(nadir, 1.0) * np.tan(half) * 1.15
    rr = np.linspace(0, 1, rm.rings + 1)[1:]
    th = np.linspace(0, 2 * np.pi, rm.spokes, endpoint=False)
    off_r = (rr[:, None] * np.ones_like(th)[None, :]).ravel()
    off_c, off_s = np.cos(np.tile(th, rm.rings)), np.sin(np.tile(th, rm.rings))
    r = rmax[:, None] * off_r[None, :]
    pe = e[:, None] + r * off_s[None, :]
    pn = n[:, None] + r * off_c[None, :]
    dz = alt[:, None] - bilinear(surface, pe, pn, res)
    slant = np.hypot(r, dz)
    inside = np.arctan2(r, np.maximum(dz, 1e-6)) <= half
    slant = np.where(inside & np.isfinite(slant), slant, np.inf)
    return np.minimum(nadir, slant.min(axis=1))


def nmea_checksum(body):
    c = 0
    for ch in body:
        c ^= ord(ch)
    return f"{c:02X}"


def to_nmea(times, agl):
    """$GPGGA lines with only time and altitude, as in the case statement example."""
    out = []
    for t, a in zip(times, agl):
        hh, rem = divmod(t + 12 * 3600.0, 3600.0)
        mm, ss = divmod(rem, 60.0)
        body = f"GPGGA,{int(hh):02d}{int(mm):02d}{ss:06.3f},,,,,,,,{a:.1f},M,0.0,M,,"
        out.append(f"${body}*{nmea_checksum(body)}")
    return out


def parse_nmea(lines):
    ts, alts = [], []
    for ln in lines:
        ln = ln.strip()
        if not ln.startswith("$GPGGA") or "*" not in ln:
            continue
        body, cs = ln[1:].split("*", 1)
        if nmea_checksum(body) != cs[:2].upper():
            continue
        f = body.split(",")
        try:
            hhmmss = f[1]
            t = int(hhmmss[0:2]) * 3600 + int(hhmmss[2:4]) * 60 + float(hhmmss[4:]) - 12 * 3600.0
            ts.append(t)
            alts.append(float(f[9]))
        except (ValueError, IndexError):
            continue
    return np.array(ts), np.array(alts)


def generate(dem, res, sc, seed):
    """One run. Returns truth at the measurement epochs, the NMEA-derived stream and the prior."""
    rng = np.random.default_rng(seed)
    track = None
    while track is None:
        track = place_track(make_track(sc.family, rng), dem, res, rng)
    surface = world_surface(dem, res, sc.world, rng)

    step = int(round(1.0 / (sc.sample_hz * SIM_DT)))
    idx = np.arange(0, len(track["t"]), step)
    t = track["t"][idx]
    e, n = track["e"][idx], track["n"][idx]
    alt, bias = altitude_truth(t, sc.altref, rng, 1.0 / sc.sample_hz)
    rm = sc.radar
    rng_m = radar_range(surface, res, e, n, alt, rm)
    agl = rng_m + rng.standard_normal(len(t)) * (rm.noise_m + rm.noise_frac * rng_m)

    out_mask = rng.random(len(t)) < rm.outlier_p
    agl[out_mask] += rng.uniform(*rm.outlier_m, out_mask.sum()) * rng.choice([-1, 1], out_mask.sum())
    keep = rng.random(len(t)) >= rm.dropout_p
    k = 0
    while k < len(t):
        if rng.random() < rm.burst_p:
            nb = int(rng.uniform(*rm.burst_s) * sc.sample_hz)
            keep[k:k + nb] = False
            k += nb
        k += 1
    keep[0] = True

    tt, agl_meas = parse_nmea(to_nmea(t[keep], np.maximum(agl[keep], 0.0)))
    prior = {
        "e0": e[0] + sc.start_sigma_m * rng.standard_normal(),
        "n0": n[0] + sc.start_sigma_m * rng.standard_normal(),
        "pos_sigma_m": max(sc.start_sigma_m, 1.0),
        "heading_deg": float(track["psi"][0] + sc.heading_hint_sigma_deg * rng.standard_normal()) % 360,
        "speed_mps": float(track["v"][0] + sc.speed_hint_sigma_mps * rng.standard_normal()),
        "flight_msl_m": FLIGHT_MSL_M,
        "t0": float(tt[0]),
    }
    s = track["s"][idx][keep]
    return {
        "t": tt, "agl": agl_meas, "terrain_meas": FLIGHT_MSL_M - agl_meas,
        "e": e[keep], "n": n[keep], "s": s, "psi": track["psi"][idx][keep], "v": track["v"][idx][keep],
        "true_ground": bilinear(dem, e[keep], n[keep], res),
        "alt_bias_m": bias, "prior": prior, "n_epochs": len(t), "n_kept": int(keep.sum()),
    }
