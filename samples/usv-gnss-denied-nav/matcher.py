"""Radar-to-chart matching: likelihood-field grid search, then point-to-line ICP (x, y, heading).

The fix is computed from the radar scan, the chart and a search window only; the prior position
picks the window but does not enter the estimate, so the fix stays independent of GNSS.
"""
import math
from dataclasses import dataclass

from chart import FIELD_RES_M
from geo import eig2, inv, wrap_pi

MIN_RETURNS = 25
MAX_POINTS = 160
COARSE_POINTS = 80
LF_SIGMA_M = 15.0
SEARCH_MIN_M, SEARCH_MAX_M = 40.0, 800.0
SEARCH_CELLS = 6                 # grid half-width in steps
HEADING_STEPS_DEG = (-2.0, 0.0, 2.0)
MIN_SCORE_FRAC = 0.2             # mean likelihood per return at the best cell
AMBIGUITY_RATIO = 0.9            # a distinct second peak this close to the best => ambiguous
AMBIGUITY_MAHAL2 = 16.0
ICP_ITERS = 12
ICP_GATE_START_M, ICP_GATE_END_M = 50.0, 25.0
HUBER_M = 10.0
MIN_INLIERS = 20
MIN_INLIER_FRAC = 0.25
MAX_FIX_SIGMA_M = 30.0           # marginal 1-sigma along the weakest direction; above => degenerate
CORRELATION_INFLATION = 10.0     # residuals of neighbouring azimuths are not independent
CHART_SIGMA_M = 5.0              # assumed OSM digitising error, not measured


@dataclass
class Fix:
    ok: bool
    reason: str
    x: float = 0.0
    y: float = 0.0
    psi: float = 0.0
    cov: list = None             # 3x3 over (x, y, psi)
    n_returns: int = 0
    n_inliers: int = 0
    inlier_frac: float = 0.0
    cond: float = 0.0            # sqrt of the translational covariance eigenvalue ratio
    sigma_major: float = 0.0
    degenerate: bool = False


def to_world(points, x, y, psi):
    return [(x + r * math.sin(psi + b), y + r * math.cos(psi + b)) for r, b in points]


def lf_score(chart, points, x, y, psi):
    k = -0.5 / (LF_SIGMA_M * LF_SIGMA_M)
    return sum(math.exp(k * chart.field(px, py) ** 2) for px, py in to_world(points, x, y, psi))


def grid_search(chart, points, x0, y0, psi0, radius):
    """Local maxima of the likelihood-field score over a translation grid (best heading per cell),
    best first. Translations snap to the field lattice so each cell is a pure table lookup per return."""
    res = FIELD_RES_M
    step_i = max(1, round(radius / SEARCH_CELLS / res))
    step = step_i * res
    n = int(math.ceil(radius / step))
    k = -0.5 / (LF_SIGMA_M * LF_SIGMA_M)
    lik = {}
    grid = {}
    i0, j0 = round(x0 / res), round(y0 / res)
    for dh in HEADING_STEPS_DEG:
        psi = psi0 + math.radians(dh)
        rel = [(round(r * math.sin(psi + b) / res), round(r * math.cos(psi + b) / res)) for r, b in points]
        for a in range(-n, n + 1):
            ci = i0 + a * step_i
            for c in range(-n, n + 1):
                cj = j0 + c * step_i
                sc = 0.0
                for di, dj in rel:
                    key = (ci + di, cj + dj)
                    v = lik.get(key)
                    if v is None:
                        v = lik[key] = math.exp(k * chart.field_key(*key) ** 2)
                    sc += v
                if sc > grid.get((a, c), (-1.0,))[0]:
                    grid[(a, c)] = (sc, ci * res, cj * res, psi)
    peaks = [v for (a, c), v in grid.items()
             if all(v[0] >= grid.get((a + da, c + dc), (-1.0,))[0]
                    for da in (-1, 0, 1) for dc in (-1, 0, 1))]
    peaks.sort(reverse=True)
    return peaks, step


def icp(chart, points, x, y, psi):
    """Gauss-Newton on point-to-line residuals with Huber weights. Returns (x, y, psi, H, resid, n_in)."""
    H = None
    for it in range(ICP_ITERS):
        gate = ICP_GATE_START_M + (ICP_GATE_END_M - ICP_GATE_START_M) * it / (ICP_ITERS - 1)
        H = [[0.0] * 3 for _ in range(3)]
        g = [0.0] * 3
        resid, n_in = [], 0
        for r, b in points:
            px, py = x + r * math.sin(psi + b), y + r * math.cos(psi + b)
            hit = chart.nearest(px, py, gate)
            if hit is None:
                continue
            d, cx, cy, _ = hit
            if d < 1e-6:
                ax, ay, bx, by = chart.segs[hit[3]][:4]
                L = math.hypot(bx - ax, by - ay) or 1.0
                nx, ny = -(by - ay) / L, (bx - ax) / L
            else:
                nx, ny = (px - cx) / d, (py - cy) / d
            e = nx * (px - cx) + ny * (py - cy)
            J = (nx, ny, nx * r * math.cos(psi + b) - ny * r * math.sin(psi + b))
            w = 1.0 if abs(e) <= HUBER_M else HUBER_M / abs(e)
            for a in range(3):
                g[a] += w * J[a] * e
                for c in range(3):
                    H[a][c] += w * J[a] * J[c]
            resid.append(e)
            n_in += 1
        if n_in < MIN_INLIERS:
            return x, y, psi, H, resid, n_in
        Hr = [[H[a][c] + (1e-3 if a == c else 0.0) for c in range(3)] for a in range(3)]
        Hr[2][2] += 1e4  # keep heading steps bounded when few far returns constrain it
        try:
            dx = [-sum(v * gg for v, gg in zip(row, g)) for row in inv(Hr)]
        except ZeroDivisionError:
            return x, y, psi, H, resid, n_in
        x, y, psi = x + dx[0], y + dx[1], wrap_pi(psi + dx[2])
        if math.hypot(dx[0], dx[1]) < 0.05 and abs(dx[2]) < 1e-5:
            break
    return x, y, psi, H, resid, n_in


def match(chart, returns, x0, y0, psi0, sigma_xy, sigma_range):
    pts = [(r, b) for r, b, *_ in returns]
    fix = Fix(False, "", n_returns=len(pts))
    if len(pts) < MIN_RETURNS:
        fix.reason = "few_returns"
        return fix
    if len(pts) > MAX_POINTS:
        pts = [pts[int(i * len(pts) / MAX_POINTS)] for i in range(MAX_POINTS)]
    radius = min(SEARCH_MAX_M, max(SEARCH_MIN_M, 3.0 * sigma_xy))
    coarse = pts[::max(1, len(pts) // COARSE_POINTS)]
    peaks, step = grid_search(chart, coarse, x0, y0, psi0, radius)
    best = peaks[0]
    if best[0] / len(coarse) < MIN_SCORE_FRAC:
        fix.reason = "no_chart_match"
        return fix
    x, y, psi, H, resid, n_in = icp(chart, pts, best[1], best[2], best[3])
    fix.n_inliers, fix.inlier_frac = n_in, n_in / len(pts)
    if n_in < MIN_INLIERS or fix.inlier_frac < MIN_INLIER_FRAC:
        fix.reason = "few_inliers"
        return fix
    s2 = max(sum(e * e for e in resid) / max(1, n_in - 3), sigma_range ** 2) * CORRELATION_INFLATION
    try:
        cov = [[s2 * v for v in row] for row in inv(H)]
    except ZeroDivisionError:
        fix.reason = "singular"
        return fix
    cov[0][0] += CHART_SIGMA_M ** 2
    cov[1][1] += CHART_SIGMA_M ** 2
    lo, hi, _ = eig2(cov[0][0], cov[0][1], cov[1][1])
    fix.cond = math.sqrt(hi / max(lo, 1e-9))
    fix.sigma_major = math.sqrt(hi)
    if fix.sigma_major > MAX_FIX_SIGMA_M:
        # Featureless or one-sided geometry. The full 3x3 covariance still couples position to
        # heading, and a filter with a tight heading prior would read that as a position fix.
        fix.degenerate = True
        fix.reason = "degenerate"
        return fix
    info = inv([[cov[0][0], cov[0][1]], [cov[1][0], cov[1][1]]])
    for sc, cx, cy, _ in peaks[1:]:
        if sc < AMBIGUITY_RATIO * best[0]:
            break
        dx, dy = cx - x, cy - y
        if math.hypot(dx, dy) > 2 * step and \
                dx * dx * info[0][0] + 2 * dx * dy * info[0][1] + dy * dy * info[1][1] > AMBIGUITY_MAHAL2:
            fix.reason = "ambiguous"
            return fix
    fix.ok, fix.reason = True, "ok"
    fix.x, fix.y, fix.psi, fix.cov = x, y, psi, cov
    return fix
