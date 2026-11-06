"""Core math: heightmap features, CCOEFF template matching, clustered particle filter, TERCOM.

Conventions: a map is a 2D array indexed [row, col] with row 0 at the southern edge;
cell (i, j) sits at east = j * res, north = i * res metres in the local frame.
"""
import numpy as np
from scipy.cluster.vq import kmeans2
from scipy.ndimage import gaussian_filter, grey_opening
from scipy.signal import fftconvolve


def bilinear(grid, east, north, res, fill=np.nan):
    """Bilinear sample of grid at metric positions (arrays). Outside the grid => fill."""
    x = np.asarray(east, float) / res
    y = np.asarray(north, float) / res
    h, w = grid.shape
    inside = (x >= 0) & (y >= 0) & (x <= w - 1) & (y <= h - 1)
    xc = np.clip(x, 0, w - 1.000001)
    yc = np.clip(y, 0, h - 1.000001)
    j = np.floor(xc).astype(int)
    i = np.floor(yc).astype(int)
    fx = xc - j
    fy = yc - i
    v = (grid[i, j] * (1 - fx) * (1 - fy) + grid[i, j + 1] * fx * (1 - fy)
         + grid[i + 1, j] * (1 - fx) * fy + grid[i + 1, j + 1] * fx * fy)
    return np.where(inside, v, fill)


def height_above_ground(dsm, size_cells):
    """nDSM approximation: DSM minus a morphological opening (removes objects narrower than size)."""
    return dsm - grey_opening(dsm, size=(size_cells, size_cells))


def gradient_magnitude(h):
    """Height change per cell (m/cell), central differences."""
    gy, gx = np.gradient(h)
    return np.hypot(gx, gy)


def features(h, mode, thr=5.0):
    """'binary': |grad| > thr => 1 else 0 (paper, Sec. III-B). 'grad': continuous |grad|."""
    g = gradient_magnitude(h)
    if mode == "binary":
        return (g > thr).astype(np.float64)
    if mode == "grad":
        return g
    raise ValueError(mode)


def match_ccoeff(image, templ, mask=None):
    """Eq. (1): R(x,y) = sum (T - Tbar)(I(x+x', y+y') - Ibar_xy), 'valid' placements only.

    Because sum(T - Tbar) = 0, the Ibar term vanishes and R is a plain correlation of I with
    the zero-mean template (OpenCV TM_CCOEFF). With a validity mask the template mean is
    taken over valid cells and invalid cells contribute nothing.
    """
    t = np.asarray(templ, float)
    m = np.ones_like(t) if mask is None else mask.astype(float)
    n = m.sum()
    if n == 0:
        return np.zeros((image.shape[0] - t.shape[0] + 1, image.shape[1] - t.shape[1] + 1))
    tc = (t - (t * m).sum() / n) * m
    return fftconvolve(image, tc[::-1, ::-1], mode="valid")


def match_ccoeff_naive(image, templ, mask=None):
    """Direct loop over Eq. (1) including the patch-mean term, for tests."""
    th, tw = templ.shape
    m = np.ones_like(templ, float) if mask is None else mask.astype(float)
    n = m.sum()
    tbar = (templ * m).sum() / n
    out = np.zeros((image.shape[0] - th + 1, image.shape[1] - tw + 1))
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            patch = image[i:i + th, j:j + tw]
            ibar = (patch * m).sum() / n
            out[i, j] = (m * (templ - tbar) * (patch - ibar)).sum()
    return out


def blur_normalize(r, sigma_cells):
    """Gaussian blur against discretization artifacts, then min-max to [0, 1]."""
    b = gaussian_filter(r, sigma_cells) if sigma_cells > 0 else r
    lo, hi = b.min(), b.max()
    return np.zeros_like(b) if hi <= lo else (b - lo) / (hi - lo)


def similarity_map(feat_map, feat_templ, mask, center_e, center_n, half_extent_m, res, blur_cells):
    """Similarity of the template placed with its centre at each map cell inside a search box.

    Returns (sim, origin_e, origin_n): sim[i, j] is the score for the template centre at
    east = origin_e + j*res, north = origin_n + i*res.
    """
    th, tw = feat_templ.shape
    assert th % 2 == 1 and tw % 2 == 1
    h, w = feat_map.shape
    ci, cj = int(round(center_n / res)), int(round(center_e / res))
    k = int(np.ceil(half_extent_m / res))
    i0 = max(0, ci - k - th // 2)
    i1 = min(h, ci + k + th // 2 + 1)
    j0 = max(0, cj - k - tw // 2)
    j1 = min(w, cj + k + tw // 2 + 1)
    sub = feat_map[i0:i1, j0:j1]
    if sub.shape[0] < th or sub.shape[1] < tw:
        return None
    r = match_ccoeff(sub, feat_templ, mask)
    sim = blur_normalize(r, blur_cells)
    return sim, (j0 + tw // 2) * res, (i0 + th // 2) * res


def systematic_resample(weights, rng):
    n = len(weights)
    c = np.cumsum(weights)
    c[-1] = 1.0
    u = (rng.random() + np.arange(n)) / n
    return np.searchsorted(c, u)


def largest_cluster_centroid(points, k, rng):
    """K-means on particles; centroid of the most populated cluster (paper, Sec. III-C)."""
    if k <= 1:
        return points.mean(0)
    seed = int(rng.integers(1 << 31))
    cent, lab = kmeans2(points, k, minit="++", seed=seed)
    counts = np.bincount(lab, minlength=k)
    return cent[int(np.argmax(counts))]


class HeightmapPF:
    """Translational particle filter driven by odometry and similarity maps."""

    def __init__(self, n, mean, sigma, rng, kmeans_k=4, weight_power=1.0):
        self.rng = rng
        self.p = np.asarray(mean, float) + rng.normal(0, sigma, (n, 2))
        self.k = kmeans_k
        self.power = weight_power

    def predict(self, delta):
        self.p += delta

    def update(self, sim, origin_e, origin_n, res, jitter_sigma):
        """Weight by normalized similarity at each particle, resample, perturb. Returns ESS."""
        w = bilinear(sim, self.p[:, 0] - origin_e, self.p[:, 1] - origin_n, res, fill=0.0)
        w = np.clip(w, 0, None) ** self.power
        s = w.sum()
        if s <= 0:
            return 0.0
        w /= s
        ess = 1.0 / np.sum(w ** 2)
        idx = systematic_resample(w, self.rng)
        self.p = self.p[idx] + self.rng.normal(0, jitter_sigma, self.p.shape)
        return ess

    def estimate(self):
        return largest_cluster_centroid(self.p, self.k, self.rng)

    def spread(self):
        return float(np.sqrt(np.trace(np.cov(self.p.T))))


def tercom_fix(dem, res, track_e, track_n, profile, radius_m, step_m):
    """Batch TERCOM: translation offset minimizing mean-removed MAD between profile and DEM.

    Returns (d_east, d_north, best_mad, second_mad), where second_mad is the best score at
    least 3 cells away from the winner (an ambiguity indicator), or None if all invalid.
    """
    offs = np.arange(-radius_m, radius_m + step_m / 2, step_m)
    de, dn = np.meshgrid(offs, offs)
    de = de.ravel()[:, None]
    dn = dn.ravel()[:, None]
    m = bilinear(dem, track_e[None, :] + de, track_n[None, :] + dn, res)
    p = profile - profile.mean()
    m = m - m.mean(axis=1, keepdims=True)
    mad = np.abs(m - p[None, :]).mean(axis=1)
    if np.all(np.isnan(mad)):
        return None
    mad = np.where(np.isnan(mad), np.inf, mad)
    b = int(np.argmin(mad))
    far = np.hypot(de[:, 0] - de[b, 0], dn[:, 0] - dn[b, 0]) > 3 * res
    second = mad[far].min() if far.any() else np.inf
    return float(de[b, 0]), float(dn[b, 0]), float(mad[b]), float(second)


# ---------------------------------------------------------------- v2: likelihood, information gate, heading state

def rotate_patch(h, mask, angle):
    """Undo a compass error `angle` (rad): out[u] = h[R(-angle) u], u in cells about the patch centre.

    The sensor patch is h[g] = world(pos + R(err) g), so angle = err gives a north-aligned patch.
    Cells whose source falls outside the patch or on an invalid cell become invalid.
    """
    from scipy.ndimage import map_coordinates
    n0, n1 = h.shape
    c0, c1 = (n0 - 1) / 2, (n1 - 1) / 2
    v, u = np.mgrid[0:n0, 0:n1].astype(float)
    u -= c1
    v -= c0
    ca, sa = np.cos(-angle), np.sin(-angle)
    src_col = ca * u - sa * v + c1
    src_row = sa * u + ca * v + c0
    hv = np.where(mask, h, 0.0)
    num = map_coordinates(hv, [src_row, src_col], order=1, cval=0.0)
    den = map_coordinates(mask.astype(float), [src_row, src_col], order=1, cval=0.0)
    m = den > 0.5
    return np.where(m, num / np.where(m, den, 1.0), 0.0), m


def ncc_map(image, templ, mask):
    """Masked normalized cross-correlation of template and each image window ('valid').

    rho = R / sqrt(sum m (T - Tbar)^2 * sum m (I - Ibar)^2), R the Eq. (1) correlation. Unlike
    Eq. (1) it is invariant to feature gain, which matters because gradient magnitude of a
    noisy patch is inflated (rectified noise) relative to the clean map. Windows with no
    variance get rho = 0. Returns (rho, n_valid, template energy).
    """
    m = mask.astype(float)
    n = m.sum()
    t = np.where(mask, templ, 0.0)
    tc = (t - t.sum() / n) * m
    et = (tc ** 2).sum()
    mf = m[::-1, ::-1]
    s1 = fftconvolve(image, mf, mode="valid")
    s2 = fftconvolve(image * image, mf, mode="valid")
    r = fftconvolve(image, tc[::-1, ::-1], mode="valid")
    var_i = s2 - s1 ** 2 / n
    ok = var_i > 1e-9 * max(var_i.max(), 1e-30)
    rho = np.where(ok, r / np.sqrt(np.where(ok, var_i, 1.0) * max(et, 1e-30)), 0.0)
    return np.clip(rho, -1, 1), n, et


def ncc_map_naive(image, templ, mask):
    th, tw = templ.shape
    m = mask.astype(bool)
    out = np.zeros((image.shape[0] - th + 1, image.shape[1] - tw + 1))
    a = templ[m] - templ[m].mean()
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            p = image[i:i + th, j:j + tw][m]
            p = p - p.mean()
            out[i, j] = (a * p).sum() / np.sqrt((a * a).sum() * (p * p).sum())
    return out


def ncc_loglik(rho_maps, n, kappa):
    """Gain-fitted Gaussian residual sum(T - a I)^2 = E_T (1 - rho+^2), a >= 0, with the noise
    variance self-calibrated from the best residual over all hypotheses (no truth, no tuning
    of sigma). Returns log-likelihood maps, 0 at the best cell. kappa = cells per independent
    residual.
    """
    res = [1 - np.clip(r, 0, None) ** 2 for r in rho_maps]
    best = max(min(x.min() for x in res), 1e-6)
    return [-(np.maximum(x, best) / best - 1) * n / (2 * kappa) for x in res]


def translation_crb(window, mask, sigma2, res):
    """Cramer-Rao bound of the template position from the reference features under the window.

    Gaussian model f_obs = f_map(x + d) + white noise sigma2 per cell gives Fisher information
    J = sum m grad f grad f^T / sigma2 (gradients per metre). Returns (worst-axis std in metres,
    J). Inf when J is singular (no texture or texture in one direction only).
    """
    gy, gx = np.gradient(window, res)
    m = mask.astype(float)
    J = np.array([[(m * gx * gx).sum(), (m * gx * gy).sum()],
                  [(m * gx * gy).sum(), (m * gy * gy).sum()]]) / max(sigma2, 1e-12)
    lmin = np.linalg.eigvalsh(J)[0]
    return (float(1 / np.sqrt(lmin)) if lmin > 1e-12 else float("inf")), J


def ncc_crb(window, mask, rho, kappa, res, rho_null=0.0):
    """CRB (metres, worst axis) of the match under the gain-fitted model T = a I(x) + e.

    With rho the best NCC, the per-cell signal-to-noise ratio is rho^2 / (1 - rho^2) in units of
    the window's own variance, so J = (n / kappa) SNR * sum m grad I grad I^T / E_I. rho is a
    maximum over many placements and is biased up, so only the part above rho_null (the
    maximum pure noise reaches) counts as signal: SNR = (rho^2 - rho_null^2) / (1 - rho^2).
    Needs no truth: the reference window at the current estimate and the NCC map only.
    """
    m = mask.astype(bool)
    n = m.sum()
    v = window[m]
    e_i = ((v - v.mean()) ** 2).sum()
    rho = float(np.clip(rho, 0, 0.999))
    snr = (rho ** 2 - rho_null ** 2) / (1 - rho ** 2)
    if n == 0 or e_i <= 0 or snr <= 0:
        return float("inf")
    w = (window - v.mean()) / np.sqrt(e_i / n)
    return translation_crb(w, mask, kappa / snr, res)[0]


def temper_to_ess(loglik, ess_floor):
    """Smallest flattening of the likelihood that keeps ESS >= ess_floor * N. Returns (w, beta)."""
    l = loglik - loglik.max()
    n = len(l)

    def w_of(b):
        w = np.exp(b * l)
        return w / w.sum()

    def ess(w):
        return 1.0 / np.sum(w ** 2) / n

    w = w_of(1.0)
    if ess(w) >= ess_floor:
        return w, 1.0
    lo, hi = 0.0, 1.0
    for _ in range(30):
        mid = (lo + hi) / 2
        if ess(w_of(mid)) >= ess_floor:
            lo = mid
        else:
            hi = mid
    return w_of(lo), lo


class HeadingPF:
    """Particle filter over (east, north, compass bias). Odometry is rotated per particle by -bias."""

    def __init__(self, n, mean, sigma, bias_sigma, bias_max, rng, kmeans_k=4):
        self.rng = rng
        self.p = np.empty((n, 3))
        self.p[:, :2] = np.asarray(mean, float) + rng.normal(0, sigma, (n, 2))
        b = rng.normal(0, bias_sigma, n)
        self.p[:, 2] = np.clip(b - b.mean(), -bias_max, bias_max)
        self.bias_max = bias_max
        self.k = kmeans_k

    def predict(self, d):
        c, s = np.cos(-self.p[:, 2]), np.sin(-self.p[:, 2])
        self.p[:, 0] += c * d[0] - s * d[1]
        self.p[:, 1] += s * d[0] + c * d[1]

    def diffuse(self, pos_sigma, bias_sigma):
        self.p[:, :2] += self.rng.normal(0, pos_sigma, (len(self.p), 2))
        self.p[:, 2] = np.clip(self.p[:, 2] + self.rng.normal(0, bias_sigma, len(self.p)), -self.bias_max, self.bias_max)

    def loglik_at(self, maps, angles, origin_e, origin_n, res):
        """Log-likelihood per particle: bilinear in position, linear between the two nearest angle maps."""
        a = np.asarray(angles, float)
        floor = min(m.min() for m in maps)
        v = np.stack([bilinear(m, self.p[:, 0] - origin_e, self.p[:, 1] - origin_n, res, fill=floor) for m in maps])
        if len(a) == 1:
            return v[0]
        x = np.clip((self.p[:, 2] - a[0]) / (a[1] - a[0]), 0, len(a) - 1)
        k0 = np.minimum(np.floor(x).astype(int), len(a) - 2)
        f = x - k0
        idx = np.arange(len(self.p))
        return (1 - f) * v[k0, idx] + f * v[k0 + 1, idx]

    def update(self, loglik, ess_floor):
        """Weight, resample. Returns (pre-resample ESS fraction, tempering beta)."""
        w, beta = temper_to_ess(loglik, ess_floor)
        ess = 1.0 / np.sum(w ** 2) / len(w)
        self.p = self.p[systematic_resample(w, self.rng)]
        return float(ess), float(beta)

    def estimate(self):
        return largest_cluster_centroid(self.p[:, :2], self.k, self.rng)

    def spread(self):
        return float(np.sqrt(np.trace(np.cov(self.p[:, :2].T))))
