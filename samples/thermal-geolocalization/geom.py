"""Stdlib geometry and the integrity gate. No third-party imports, so tests run on plain python3."""
import math
from dataclasses import dataclass

EARTH_R_M = 6371008.8


def frame_gsd_m(rel_height_m, focal_mm, sensor_diag_mm, width_px, height_px):
    """Ground sample distance of a nadir frame from altitude above ground and camera intrinsics."""
    pitch_mm = sensor_diag_mm / math.hypot(width_px, height_px)
    return rel_height_m * pitch_mm / focal_mm


def haversine_m(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * EARTH_R_M * math.asin(math.sqrt(a))


def offset_latlon(lat, lon, dist_m, bearing_deg):
    """Point dist_m away along bearing (spherical, fine for a few hundred metres)."""
    br = math.radians(bearing_deg)
    dlat = dist_m * math.cos(br) / EARTH_R_M
    dlon = dist_m * math.sin(br) / (EARTH_R_M * math.cos(math.radians(lat)))
    return lat + math.degrees(dlat), lon + math.degrees(dlon)


def affine_scale_rot(h):
    """Scale and rotation (deg) of the linear part of a 3x3 homography given as nested lists.

    The query is already rotated north-up and resampled to map GSD from the priors, so a
    correct fix has scale near 1 and rotation near 0.
    """
    a, b = h[0][0] / h[2][2], h[0][1] / h[2][2]
    c, d = h[1][0] / h[2][2], h[1][1] / h[2][2]
    det = a * d - b * c
    scale = math.sqrt(abs(det))
    rot = math.degrees(math.atan2(c - b, a + d))
    return scale, rot, det


@dataclass
class Gate:
    min_inliers: int = 30
    min_inlier_ratio: float = 0.25
    max_scale_dev: float = 0.25
    max_rot_deg: float = 15.0
    max_persp_distortion: float = 0.15

    def check(self, n_inliers, n_matches, h, shift_m, search_radius_m, query_half_diag_px):
        """Return (accepted, reasons). h is the query=>reference homography (nested lists).

        The perspective row is judged as relative scale change across the query: a nadir frame
        should map to the ortho with almost none.
        """
        reasons = []
        if n_inliers < self.min_inliers:
            reasons.append(f"inliers {n_inliers} < {self.min_inliers}")
        ratio = n_inliers / n_matches if n_matches else 0.0
        if ratio < self.min_inlier_ratio:
            reasons.append(f"inlier ratio {ratio:.2f} < {self.min_inlier_ratio}")
        if h is None:
            reasons.append("no homography")
            return False, reasons
        scale, rot, det = affine_scale_rot(h)
        if det <= 0:
            reasons.append("mirrored homography")
        if abs(scale - 1.0) > self.max_scale_dev:
            reasons.append(f"scale {scale:.2f} outside 1 +- {self.max_scale_dev}")
        if abs(rot) > self.max_rot_deg:
            reasons.append(f"rotation {rot:.1f} deg > {self.max_rot_deg}")
        persp = math.hypot(h[2][0] / h[2][2], h[2][1] / h[2][2]) * query_half_diag_px
        if persp > self.max_persp_distortion:
            reasons.append(f"perspective distortion {persp:.2f} > {self.max_persp_distortion}")
        if shift_m > search_radius_m:
            reasons.append(f"fix {shift_m:.0f} m from prior > search radius {search_radius_m:.0f} m")
        return not reasons, reasons


# "apriori" was fixed before the first full run. "revised" was chosen after inspecting that run
# (correct fits showed a -4 to -10 deg heading bias and 15-30 inliers); it was then checked on
# held-out flights from the dataset's validation split. See README.
GATES = {
    "apriori": Gate(),
    "revised": Gate(min_inliers=15, min_inlier_ratio=0.15, max_rot_deg=30.0),
}


def summarize(errors_accepted, n_total, false_fix_m):
    """Fix rate, correct and false fixes, and error percentiles for one config."""
    acc = sorted(errors_accepted)
    n_acc = len(acc)
    good = [e for e in acc if e <= false_fix_m]

    def pct(xs, q):
        if not xs:
            return None
        k = (len(xs) - 1) * q
        lo, hi = math.floor(k), math.ceil(k)
        return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)

    return {
        "n": n_total,
        "accepted": n_acc,
        "fix_rate": n_acc / n_total if n_total else 0.0,
        "correct": len(good),
        "false_fixes": n_acc - len(good),
        "false_fix_rate": (n_acc - len(good)) / n_acc if n_acc else 0.0,
        "median_err_m": pct(good, 0.5),
        "p90_err_m": pct(good, 0.9),
    }
