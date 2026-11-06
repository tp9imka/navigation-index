"""ENU/FLU (ROS convention) to NED/FRD (MAVLink convention) frame conversion.

Quaternions are (w, x, y, z), Hamilton, and rotate body vectors into the world
frame (q_world_body). Stdlib only.
"""
import math

SQRT_HALF = math.sqrt(0.5)

# 180 deg about (1,1,0)/sqrt(2): maps ENU coordinates onto NED.
Q_NED_FROM_ENU = (0.0, SQRT_HALF, SQRT_HALF, 0.0)
# 180 deg about x: maps FRD body coordinates onto FLU.
Q_FLU_FROM_FRD = (0.0, 1.0, 0.0, 0.0)

# Diagonal indices of a 6x6 symmetric matrix stored as its 21-element upper triangle
# (row-major), the layout MAVLink uses for pose covariance.
COV21_DIAGONAL = (0, 6, 11, 15, 18, 20)


def quat_mul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (
        aw * bw - ax * bx - ay * by - az * bz,
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
    )


def quat_conj(q):
    w, x, y, z = q
    return (w, -x, -y, -z)


def quat_normalize(q):
    n = math.sqrt(sum(c * c for c in q))
    if n == 0.0:
        raise ValueError("zero quaternion")
    w, x, y, z = (c / n for c in q)
    # Keep w >= 0 so equal rotations compare equal.
    return (w, x, y, z) if w >= 0.0 else (-w, -x, -y, -z)


def rotate(q, v):
    """Rotate vector v by unit quaternion q."""
    p = (0.0, v[0], v[1], v[2])
    _, x, y, z = quat_mul(quat_mul(q, p), quat_conj(q))
    return (x, y, z)


def enu_to_ned(v):
    e, n, u = v
    return (n, e, -u)


def quat_enu_flu_to_ned_frd(q_enu_flu):
    """Orientation of an FLU body in ENU => orientation of the FRD body in NED."""
    q = quat_mul(quat_mul(Q_NED_FROM_ENU, quat_normalize(q_enu_flu)), Q_FLU_FROM_FRD)
    return quat_normalize(q)


def quat_to_euler(q):
    """ZYX Euler angles (roll, pitch, yaw) in radians."""
    w, x, y, z = q
    roll = math.atan2(2.0 * (w * x + y * z), 1.0 - 2.0 * (x * x + y * y))
    pitch = math.asin(max(-1.0, min(1.0, 2.0 * (w * y - z * x))))
    yaw = math.atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
    return roll, pitch, yaw


def world_to_body(q_world_body, v_world):
    return rotate(quat_conj(q_world_body), v_world)


def diag_covariance(pos_var_m2, ang_var_rad2):
    """21-element upper-triangle covariance with only the diagonal filled."""
    cov = [0.0] * 21
    for i, idx in enumerate(COV21_DIAGONAL):
        cov[idx] = pos_var_m2 if i < 3 else ang_var_rad2
    return cov


def unknown_covariance():
    """MAVLink marks unknown covariance with NaN in the first element."""
    return [float("nan")] + [0.0] * 20


def convert_pose(pos_enu, q_enu_flu):
    """Returns (pos_ned, q_ned_frd)."""
    return enu_to_ned(pos_enu), quat_enu_flu_to_ned_frd(q_enu_flu)
