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
