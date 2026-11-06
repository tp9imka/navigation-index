"""Jammer localization from per-node jammer-power measurements (stdlib).

(a) weighted_centroid  - positions weighted by dB above the detection threshold
(b) rss_ls             - Levenberg-Marquardt on the log-distance model with unknown power
                         (and k=2 sources), censored nodes as one-sided residuals
(c) GridFilter         - grid likelihood over (x, y, P0) with Bayesian update over time,
                         censored likelihoods, optional DF bearing terms
Model: J_i = P0 - 10 n log10(d_i) + e_i, e_i ~ N(0, sigma_sh^2 + sigma_meas^2 + sigma_pos^2).
P0 absorbs every common-mode constant: EIRP, 1 m loss, Q, noise figure, antenna horizon gain.
"""
import math

import siblings  # noqa: F401
import jsn_model as M
import jsn_protocol as P
from triangulate import CHI2_2DOF_95, ellipse  # noqa: E402  (../interference-geolocation-to-tak)

LN10 = math.log(10.0)
LOG_FLOOR = math.log(1e-4)       # robust floor per term: one wild node cannot veto a cell
LM_ITERS = 60
LM_TOL = 1e-6
BIC_MARGIN = 10.0
MIN_SEPARATION_M = 150.0
TOP_NODES_FOR_STARTS = 6
START_GRID = 4
P0_STEP_DB = 2.5
P0_RANGE = (-60.0, 5.0)          # EIRP -24..+41 dBm minus the 1 m free-space loss
DF_SIGMA_FLOOR_DEG = 2.0
AREA_MARGIN = 0.1               # LS solutions outside the search area (+10%) are discarded


def detect_threshold():
    return P.J_UPPER_CN0


def weighted_centroid(meas, ple=M.PLE_DEFAULT):
    thr = detect_threshold()
    pts = [(m.x, m.y, m.j_dbm - thr) for m in meas if m.kind in ("val", "lower") and m.j_dbm > thr]
    if not pts:
        return None
    pts = [(x, y, 10 ** (w / (10 * ple))) for x, y, w in pts]   # ~ 1/distance
    w = sum(p[2] for p in pts)
    return sum(p[0] * p[2] for p in pts) / w, sum(p[1] * p[2] for p in pts) / w


def _sigma(m, d, ple, sigma_sh):
    pos = 10.0 * ple / LN10 * m.ps / max(d, M.D_MIN_M)
    return math.sqrt(sigma_sh ** 2 + m.sigma_db ** 2 + pos ** 2)


def _model(params, x, y, ple):
    """Received dBm at (x, y), gradient wrt params, distance to the nearest source."""
    k = len(params) // 3
    lins, grads, dmin = [], [], math.inf
    for s in range(k):
        sx, sy, p0 = params[3 * s:3 * s + 3]
        dx, dy = sx - x, sy - y
        d = math.hypot(dx, dy)
        dmin = min(dmin, d)
        if d < M.D_MIN_M:
            m, g = p0 - 10 * ple * math.log10(M.D_MIN_M), (0.0, 0.0, 1.0)
        else:
            c = -10 * ple / LN10 / (d * d)
            m, g = p0 - 10 * ple * math.log10(d), (c * dx, c * dy, 1.0)
        lins.append(m)
        grads.append(g)
    if k == 1:
        return lins[0], list(grads[0]), dmin
    top = max(lins)
    lins = [M.db2lin(v - top) for v in lins]
    tot = sum(lins)
    full = []
    for li, g in zip(lins, grads):
        full.extend(gi * li / tot for gi in g)
    return top + M.lin2db(tot), full, dmin


def _residuals(params, meas, ple, sigma_sh):
    rs, rows = [], []
    for m in meas:
        mu, g, d = _model(params, m.x, m.y, ple)
        s = _sigma(m, d, ple, sigma_sh)
        r = (m.j_dbm - mu) / s
        if (m.kind == "upper" and r >= 0) or (m.kind == "lower" and r <= 0):
            continue
        rs.append(r)
        rows.append([-gi / s for gi in g])
    return rs, rows


def solve(a, b):
    n = len(b)
    m = [row[:] + [b[i]] for i, row in enumerate(a)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(m[r][c]))
        if abs(m[piv][c]) < 1e-15:
            raise ValueError("singular")
        m[c], m[piv] = m[piv], m[c]
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                for k in range(c, n + 1):
                    m[r][k] -= f * m[c][k]
    return [m[i][n] / m[i][i] for i in range(n)]


def inverse(a):
    n = len(a)
    cols = [solve(a, [1.0 if i == j else 0.0 for i in range(n)]) for j in range(n)]
    return [[cols[j][i] for j in range(n)] for i in range(n)]


def _normal(rs, rows, p):
    a = [[sum(r[i] * r[j] for r in rows) for j in range(p)] for i in range(p)]
    g = [sum(r[i] * e for r, e in zip(rows, rs)) for i in range(p)]
    return a, g


def _lm(params, meas, ple, sigma_sh):
    p = len(params)
    rs, rows = _residuals(params, meas, ple, sigma_sh)
    cost = sum(r * r for r in rs)
    lam = 1e-3
    for _ in range(LM_ITERS):
        a, g = _normal(rs, rows, p)
        try:
            delta = solve([[a[i][j] + (lam * a[i][i] + 1e-9 if i == j else 0.0) for j in range(p)]
                           for i in range(p)], [-gi for gi in g])
        except ValueError:
            break
        cand = [x + d for x, d in zip(params, delta)]
        rs2, rows2 = _residuals(cand, meas, ple, sigma_sh)
        cost2 = sum(r * r for r in rs2)
        if cost2 < cost:
            done = cost - cost2 < LM_TOL * max(cost, 1.0)
            params, rs, rows, cost, lam = cand, rs2, rows2, cost2, lam / 3
            if done:
                break
        else:
            lam *= 4
            if lam > 1e8:
                break
    return params, cost, rs, rows


def _p0_init(meas, x, y, ple):
    vals = [m.j_dbm + 10 * ple * math.log10(max(math.hypot(m.x - x, m.y - y), M.D_MIN_M))
            for m in meas if m.kind == "val"]
    return sum(vals) / len(vals)


def rss_ls(meas, area, ple=M.PLE_DEFAULT, sigma_sh=6.0, k=1):
    """Multistart LM. Returns None if under-determined, else dict with sources [(x, y, p0)],
    cov (full, scaled by chi2/dof when > 1), chi2, dof, n_active, ellipse95 per source."""
    vals = sorted((m for m in meas if m.kind == "val"), key=lambda m: -m.j_dbm)
    if len(vals) < 3 * k:
        return None
    xmin, ymin, xmax, ymax = area
    starts = []
    if k == 1:
        wc = weighted_centroid(meas)
        seeds = [wc] if wc else []
        seeds += [(m.x, m.y) for m in vals[:TOP_NODES_FOR_STARTS]]
        seeds += [(xmin + (i + 0.5) * (xmax - xmin) / START_GRID, ymin + (j + 0.5) * (ymax - ymin) / START_GRID)
                  for i in range(START_GRID) for j in range(START_GRID)]
        starts = [[x, y, _p0_init(meas, x, y, ple)] for x, y in seeds]
    else:
        top = [(m.x, m.y) for m in vals[:TOP_NODES_FOR_STARTS]]
        for i in range(len(top)):
            for j in range(i + 1, len(top)):
                (x1, y1), (x2, y2) = top[i], top[j]
                if math.hypot(x1 - x2, y1 - y2) < MIN_SEPARATION_M:
                    continue
                starts.append([x1, y1, _p0_init(meas, x1, y1, ple) - 3, x2, y2, _p0_init(meas, x2, y2, ple) - 3])
        if not starts:
            return None
    best = None
    mx, my = AREA_MARGIN * (xmax - xmin), AREA_MARGIN * (ymax - ymin)
    for s in starts:
        params, cost, rs, rows = _lm(s, meas, ple, sigma_sh)
        inside = all(xmin - mx <= params[3 * i] <= xmax + mx and ymin - my <= params[3 * i + 1] <= ymax + my
                     for i in range(k))
        if inside and (best is None or cost < best[1]):
            best = (params, cost, rs, rows)
    if best is None:
        return None
    params, cost, rs, rows = best
    p = len(params)
    dof = len(rs) - p
    try:
        cov = inverse(_normal(rs, rows, p)[0])
    except ValueError:
        return None
    scale = max(1.0, cost / dof) if dof > 0 else 1.0
    cov = [[c * scale for c in row] for row in cov]
    srcs = [tuple(params[3 * s:3 * s + 3]) for s in range(k)]
    ells = [ellipse([[cov[3 * s][3 * s], cov[3 * s][3 * s + 1]], [cov[3 * s + 1][3 * s], cov[3 * s + 1][3 * s + 1]]])
            for s in range(k)]
    return {"sources": srcs, "cov": cov, "chi2": cost, "dof": dof, "n_active": len(rs),
            "ellipse95": ells, "n_meas": len(meas)}


def select_sources(meas, area, ple=M.PLE_DEFAULT, sigma_sh=6.0):
    """k=1 vs k=2 by BIC on the chi2 (sigma assumed known)."""
    one = rss_ls(meas, area, ple, sigma_sh, k=1)
    if one is None:
        return None
    two = rss_ls(meas, area, ple, sigma_sh, k=2)
    one["k_test"] = None
    if two is None:
        return one
    n = max(one["n_active"], 1)
    bic1 = one["chi2"] + 3 * math.log(n)
    bic2 = two["chi2"] + 6 * math.log(n)
    (x1, y1, _), (x2, y2, _) = two["sources"]
    one["k_test"] = {"bic1": round(bic1, 1), "bic2": round(bic2, 1)}
    if bic2 + BIC_MARGIN < bic1 and math.hypot(x1 - x2, y1 - y2) > MIN_SEPARATION_M:
        two["k_test"] = one["k_test"]
        return two
    return one


class GridFilter:
    """Posterior over (x, y, P0) on a regular grid, kept in log space.

    log post = R + S + D:
      R  recursive part: mobile-node terms, each counted once per new link geometry,
         diffused between updates when the jammer may move;
      S  static nodes, rebuilt every update from each node's latest window mean (their
         shadowing is a fixed bias, so repeating it would count the same evidence again);
      D  DF stations, likewise latest robust mean bearing per station.
    """

    def __init__(self, area, n=41, ple=M.PLE_DEFAULT, sigma_sh=6.0, p0_range=P0_RANGE, p0_step=P0_STEP_DB):
        xmin, ymin, xmax, ymax = area
        self.n, self.area, self.ple, self.sigma_sh = n, area, ple, sigma_sh
        self.dx, self.dy = (xmax - xmin) / n, (ymax - ymin) / n
        self.xs = [xmin + (i + 0.5) * self.dx for i in range(n)]
        self.ys = [ymin + (j + 0.5) * self.dy for j in range(n)]
        self.cells = [(x, y) for y in self.ys for x in self.xs]
        np_ = int(round((p0_range[1] - p0_range[0]) / p0_step)) + 1
        self.p0s = [p0_range[0] + i * p0_step for i in range(np_)]
        self.R = [[0.0] * len(self.cells) for _ in self.p0s]
        self.S = None
        self.D = None

    def _term(self, m):
        ple, sh = self.ple, self.sigma_sh
        lg, inv_s, log_s = [], [], []
        for cx, cy in self.cells:
            d = max(math.hypot(cx - m.x, cy - m.y), M.D_MIN_M)
            s = _sigma(m, d, ple, sh)
            lg.append(10 * ple * math.log10(d))
            inv_s.append(1.0 / s)
            log_s.append(math.log(s))
        out = []
        j, kind = m.j_dbm, m.kind
        erfc, log, rt2 = math.erfc, math.log, math.sqrt(2.0)
        for p0 in self.p0s:
            row = []
            if kind == "val":
                for g, iv, ls in zip(lg, inv_s, log_s):
                    z = (j - p0 + g) * iv
                    v = -0.5 * z * z - ls
                    row.append(v if v > LOG_FLOOR else LOG_FLOOR)
            else:
                sign = 1.0 if kind == "upper" else -1.0
                for g, iv in zip(lg, inv_s):
                    z = sign * (j - p0 + g) * iv
                    pr = 0.5 * erfc(-z / rt2)
                    row.append(log(pr) if pr > 1e-4 else LOG_FLOOR)
            out.append(row)
        return out

    @staticmethod
    def _add(acc, term, w=1.0):
        for a, t in zip(acc, term):
            for i, v in enumerate(t):
                a[i] += w * v

    def diffuse(self, sigma_m):
        """Gaussian blur of each P0 slice of R in probability space (jammer motion model)."""
        if sigma_m <= 0:
            return
        half = max(1, int(math.ceil(3 * sigma_m / min(self.dx, self.dy))))
        kx = [math.exp(-0.5 * (i * self.dx / sigma_m) ** 2) for i in range(-half, half + 1)]
        ky = [math.exp(-0.5 * (i * self.dy / sigma_m) ** 2) for i in range(-half, half + 1)]
        n = self.n
        mx = max(max(r) for r in self.R)
        for p, row in enumerate(self.R):
            pr = [math.exp(v - mx) for v in row]
            tmp = [0.0] * len(pr)
            for j in range(n):
                for i in range(n):
                    acc = 0.0
                    for o, w in enumerate(kx):
                        ii = i + o - half
                        if 0 <= ii < n:
                            acc += w * pr[j * n + ii]
                    tmp[j * n + i] = acc
            for j in range(n):
                for i in range(n):
                    acc = 0.0
                    for o, w in enumerate(ky):
                        jj = j + o - half
                        if 0 <= jj < n:
                            acc += w * tmp[jj * n + i]
                    pr[j * n + i] = acc
            self.R[p] = [math.log(v + 1e-12) for v in pr]

    def add_recursive(self, meas):
        for m in meas:
            self._add(self.R, self._term(m))

    def set_static(self, meas):
        self.S = [[0.0] * len(self.cells) for _ in self.p0s]
        for m in meas:
            self._add(self.S, self._term(m))

    def set_bearings(self, df_obs):
        """df_obs: [(x, y, bearing_deg, sigma_deg)] one robust mean per station."""
        if not df_obs:
            self.D = None
            return
        row = [0.0] * len(self.cells)
        for sx, sy, b, sig in df_obs:
            for i, (cx, cy) in enumerate(self.cells):
                pred = math.degrees(math.atan2(cx - sx, cy - sy))
                r = (b - pred + 180.0) % 360.0 - 180.0
                v = -0.5 * (r / sig) ** 2
                row[i] += v if v > LOG_FLOOR else LOG_FLOOR
        self.D = row

    def posterior(self, use_df=True):
        tot = []
        for p in range(len(self.p0s)):
            r = self.R[p][:]
            if self.S is not None:
                r = [a + b for a, b in zip(r, self.S[p])]
            if use_df and self.D is not None:
                r = [a + b for a, b in zip(r, self.D)]
            tot.append(r)
        mx = max(max(r) for r in tot)
        probs = [[math.exp(v - mx) for v in r] for r in tot]
        z = sum(sum(r) for r in probs)
        return [[v / z for v in r] for r in probs]

    def estimate(self, use_df=True):
        post = self.posterior(use_df)
        cell = [sum(post[p][i] for p in range(len(self.p0s))) for i in range(len(self.cells))]
        mx = sum(w * c[0] for w, c in zip(cell, self.cells))
        my = sum(w * c[1] for w, c in zip(cell, self.cells))
        sxx = sum(w * (c[0] - mx) ** 2 for w, c in zip(cell, self.cells)) + self.dx ** 2 / 12
        syy = sum(w * (c[1] - my) ** 2 for w, c in zip(cell, self.cells)) + self.dy ** 2 / 12
        sxy = sum(w * (c[0] - mx) * (c[1] - my) for w, c in zip(cell, self.cells))
        imap = max(range(len(cell)), key=cell.__getitem__)
        p0m = [sum(r) for r in post]
        p0 = sum(w * v for w, v in zip(p0m, self.p0s))
        cov = [[sxx, sxy], [sxy, syy]]
        return {"x": mx, "y": my, "map": self.cells[imap], "p0": p0, "cov": cov, "ellipse95": ellipse(cov),
                "cell_probs": cell}


def inside_ellipse(dx, dy, cov, chi2=CHI2_2DOF_95):
    a, b, d = cov[0][0], cov[0][1], cov[1][1]
    det = a * d - b * b
    if det <= 0:
        return False
    return (d * dx * dx - 2 * b * dx * dy + a * dy * dy) / det <= chi2


def denial_radius_m(p0, ple=M.PLE_DEFAULT, cn0_dbhz=43.5):
    """Model radius inside which a typical SV (cn0_dbhz clear) drops below tracking."""
    j = M.jammer_dbm_from_cn0_drop(cn0_dbhz - M.TRACK_LOSS_CN0_DBHZ)
    return max(M.D0_M * 10 ** ((p0 - j) / (10 * ple)), 0.0)
