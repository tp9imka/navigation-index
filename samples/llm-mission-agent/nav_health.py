"""Summarize ArduPilot navigation integrity from EKF_STATUS_REPORT + GPS_RAW_INT. Stdlib only.

EKF flag bits: EKF_STATUS_FLAGS in mavlink ardupilotmega.xml (same table as
samples/ardupilot-ekf3-source-switch/ekf_flags.py). Variances are normalized test
ratios; 0.5 / 0.8 thresholds come from the EKF_STATUS_REPORT field comments.
"""

EKF_FLAGS = {
    1: "ATTITUDE", 2: "VELOCITY_HORIZ", 4: "VELOCITY_VERT", 8: "POS_HORIZ_REL",
    16: "POS_HORIZ_ABS", 32: "POS_VERT_ABS", 64: "POS_VERT_AGL", 128: "CONST_POS_MODE",
    256: "PRED_POS_HORIZ_REL", 512: "PRED_POS_HORIZ_ABS", 1024: "UNINITIALIZED",
    32768: "GPS_GLITCHING",
}
POS_HORIZ_REL, POS_HORIZ_ABS, CONST_POS_MODE, UNINITIALIZED, GPS_GLITCHING = 8, 16, 128, 1024, 32768

GPS_FIX_TYPES = {0: "NO_GPS", 1: "NO_FIX", 2: "2D_FIX", 3: "3D_FIX", 4: "DGPS",
                 5: "RTK_FLOAT", 6: "RTK_FIXED", 7: "STATIC", 8: "PPP"}

VARIANCE_WARN = 0.5
VARIANCE_BAD = 0.8
MIN_GOOD_SATS = 6
MAX_GOOD_HDOP = 2.0
UINT16_UNKNOWN = 65535
VARIANCE_FIELDS = ("velocity_variance", "pos_horiz_variance", "pos_vert_variance",
                   "compass_variance", "terrain_alt_variance")


def decode_flags(flags):
    return [name for bit, name in sorted(EKF_FLAGS.items()) if flags & bit]


def classify_variance(v):
    return "bad" if v >= VARIANCE_BAD else "warn" if v >= VARIANCE_WARN else "good"


def horizontal_position(flags):
    """'abs', 'rel' or 'none' as the EKF claims it."""
    if flags & (CONST_POS_MODE | UNINITIALIZED):
        return "none"
    if flags & POS_HORIZ_ABS:
        return "abs"
    if flags & POS_HORIZ_REL:
        return "rel"
    return "none"


def gps_summary(gps):
    """gps: GPS_RAW_INT as dict, or None."""
    if gps is None:
        return {"available": False}
    eph = gps.get("eph", UINT16_UNKNOWN)
    return {"available": True,
            "fix_type": GPS_FIX_TYPES.get(gps.get("fix_type"), str(gps.get("fix_type"))),
            "satellites_visible": gps.get("satellites_visible"),
            "hdop": None if eph in (None, UINT16_UNKNOWN) else round(eph / 100.0, 2)}


def assess(ekf, gps):
    """ekf: EKF_STATUS_REPORT as dict or None; gps: GPS_RAW_INT as dict or None.

    Returns verdict 'nominal' | 'degraded' | 'lost' | 'unknown' with the reasons.
    'degraded' means the vehicle still has a horizontal position but an input is
    suspect; 'lost' means the EKF reports no usable horizontal position.
    """
    reasons = []
    g = gps_summary(gps)
    gnss_ok = (g["available"] and gps.get("fix_type", 0) >= 3
               and (g["satellites_visible"] or 0) >= MIN_GOOD_SATS
               and (g["hdop"] is None or g["hdop"] <= MAX_GOOD_HDOP))
    if not g["available"]:
        reasons.append("no GPS_RAW_INT received")
    elif not gnss_ok:
        reasons.append(f"GNSS weak: fix={g['fix_type']} sats={g['satellites_visible']} "
                       f"hdop={g['hdop']}")
    if ekf is None:
        return {"verdict": "unknown", "reasons": reasons + ["no EKF_STATUS_REPORT received"],
                "gnss_ok": gnss_ok, "gps": g}
    flags = int(ekf["flags"])
    pos = horizontal_position(flags)
    variances = {f: round(float(ekf.get(f, 0.0)), 3) for f in VARIANCE_FIELDS}
    levels = {f: classify_variance(v) for f, v in variances.items()}
    if flags & GPS_GLITCHING:
        reasons.append("EKF flags GPS_GLITCHING")
    for f, lvl in levels.items():
        if lvl != "good" and f != "terrain_alt_variance":
            reasons.append(f"{f}={variances[f]} ({lvl})")
    if pos == "rel":
        reasons.append("EKF has relative horizontal position only")
    if pos == "none":
        verdict = "lost"
        reasons.insert(0, "EKF reports no horizontal position (CONST_POS_MODE/uninitialized)")
    elif reasons:
        verdict = "degraded"
    else:
        verdict = "nominal"
    return {"verdict": verdict, "reasons": reasons, "gnss_ok": gnss_ok,
            "horizontal_position": pos, "ekf_flags": decode_flags(flags),
            "ekf_flags_raw": flags, "variances": variances, "variance_levels": levels, "gps": g}
