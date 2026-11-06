"""Decode ArduPilot EKF_STATUS_REPORT (MAVLink id 193). Stdlib only.

Bit values come from the EKF_STATUS_FLAGS enum in mavlink ardupilotmega.xml.
"""
import sys

POS_HORIZ_REL = 8
POS_HORIZ_ABS = 16
CONST_POS_MODE = 128
UNINITIALIZED = 1024

EKF_FLAGS = {
    1: "ATTITUDE",
    2: "VELOCITY_HORIZ",
    4: "VELOCITY_VERT",
    8: "POS_HORIZ_REL",
    16: "POS_HORIZ_ABS",
    32: "POS_VERT_ABS",
    64: "POS_VERT_AGL",
    128: "CONST_POS_MODE",
    256: "PRED_POS_HORIZ_REL",
    512: "PRED_POS_HORIZ_ABS",
    1024: "UNINITIALIZED",
    32768: "GPS_GLITCHING",
}

# Thresholds from the comment on EKF_STATUS_REPORT.velocity_variance in ardupilotmega.xml;
# ArduPilot reports these variances as normalized test ratios.
VARIANCE_WARN = 0.5
VARIANCE_BAD = 0.8

VARIANCE_FIELDS = {
    "velocity_variance": "vel",
    "pos_horiz_variance": "pos_h",
    "pos_vert_variance": "pos_v",
    "compass_variance": "mag",
}


def decode(flags):
    return [name for bit, name in sorted(EKF_FLAGS.items()) if flags & bit]


def classify_variance(value):
    if value >= VARIANCE_BAD:
        return "bad"
    if value >= VARIANCE_WARN:
        return "warn"
    return "good"


def has_horizontal_position(flags):
    """True when the EKF claims a usable horizontal position (absolute or relative)."""
    if flags & (CONST_POS_MODE | UNINITIALIZED):
        return False
    return bool(flags & (POS_HORIZ_ABS | POS_HORIZ_REL))


def has_absolute_position(flags):
    return bool(flags & POS_HORIZ_ABS) and not flags & CONST_POS_MODE


def summarize(report):
    """report: mapping with 'flags' and the variance fields (e.g. msg.to_dict())."""
    flags = int(report["flags"])
    parts = [f"flags=0x{flags:04x}", "pos=" + ("abs" if has_absolute_position(flags)
                                               else "rel" if has_horizontal_position(flags)
                                               else "NONE")]
    for field, label in VARIANCE_FIELDS.items():
        v = float(report[field])
        parts.append(f"{label}={v:.2f}({classify_variance(v)})")
    return " ".join(parts)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        value = int(arg, 0)
        print(f"0x{value:04x}: {' | '.join(decode(value)) or '(none)'}")
