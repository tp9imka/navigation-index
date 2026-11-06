import numpy as np
import pytest
from scipy.ndimage import gaussian_filter

import core


def smooth_field(shape, seed=0, sigma=3.0):
    rng = np.random.default_rng(seed)
    return gaussian_filter(rng.normal(0, 10, shape), sigma)


def test_ccoeff_fft_matches_eq1_loop():
    img = smooth_field((30, 28), 1)
    t = smooth_field((7, 9), 2)
    np.testing.assert_allclose(core.match_ccoeff(img, t), core.match_ccoeff_naive(img, t), atol=1e-8)


def test_ccoeff_with_mask_matches_eq1_loop():
    img = smooth_field((25, 25), 3)
    t = smooth_field((9, 9), 4)
    m = np.random.default_rng(5).random(t.shape) > 0.3
    np.testing.assert_allclose(core.match_ccoeff(img, t, m), core.match_ccoeff_naive(img, t, m), atol=1e-8)


def test_ccoeff_peak_at_true_location_and_offset_invariant():
    img = smooth_field((80, 80), 6)
    i, j = 31, 17
    t = img[i:i + 21, j:j + 21] + 123.0
    r = core.match_ccoeff(img, t)
    assert np.unravel_index(np.argmax(r), r.shape) == (i, j)


def test_gradient_of_plane():
    yy, xx = np.mgrid[0:20, 0:20].astype(float)
    g = core.gradient_magnitude(3 * xx + 4 * yy)
    np.testing.assert_allclose(g, 5.0)


def test_features_ignore_vertical_offset_and_threshold():
    h = smooth_field((40, 40), 7, sigma=1.5)
    np.testing.assert_array_equal(core.features(h, "binary", 2.0), core.features(h + 500, "binary", 2.0))
    b = core.features(h, "binary", 2.0)
    assert set(np.unique(b)) <= {0.0, 1.0}
    assert np.array_equal(b == 1, core.gradient_magnitude(h) > 2.0)
    with pytest.raises(ValueError):
        core.features(h, "nope")


def test_height_above_ground_removes_ground_keeps_block():
    yy, xx = np.mgrid[0:40, 0:40].astype(float)
    ground = 0.5 * xx
    dsm = ground.copy()
    dsm[18:21, 18:21] += 15
    hag = core.height_above_ground(dsm, 7)
    assert hag[19, 19] == pytest.approx(15, abs=2)
    assert np.abs(hag[5:12, 5:12]).max() < 1e-9


def test_bilinear_exact_on_plane_and_nan_outside():
    yy, xx = np.mgrid[0:10, 0:12].astype(float)
    grid = 2 * xx - yy + 7
    e = np.array([15.0, 33.0, 400.0])
    n = np.array([15.0, 42.0, 10.0])
    v = core.bilinear(grid, e, n, res=30.0)
    np.testing.assert_allclose(v[:2], 2 * e[:2] / 30 - n[:2] / 30 + 7)
    assert np.isnan(v[2])


def test_blur_normalize_range():
    s = core.blur_normalize(smooth_field((20, 20), 8), 1.0)
    assert s.min() == 0 and s.max() == 1


def test_systematic_resample_proportions():
    rng = np.random.default_rng(0)
    w = np.array([0.0, 0.25, 0.75, 0.0])
    idx = core.systematic_resample(w, rng)
    counts = np.bincount(idx, minlength=4)
    assert counts[0] == 0 and counts[3] == 0
    assert counts[1] == 1 and counts[2] == 3


def test_largest_cluster_centroid_picks_majority_mode():
    rng = np.random.default_rng(1)
    a = rng.normal([0, 0], 5, (700, 2))
    b = rng.normal([500, 500], 5, (300, 2))
    c = core.largest_cluster_centroid(np.vstack([a, b]), 2, rng)
    assert np.linalg.norm(c) < 5


def test_similarity_and_pf_update_concentrate_on_true_position():
    res = 30.0
    rng = np.random.default_rng(2)
    dem = smooth_field((150, 150), 9, sigma=2.0) * 5
    fmap = core.features(dem, "grad")
    ci, cj = 70, 80
    templ = fmap[ci - 10:ci + 11, cj - 10:cj + 11]
    valid = np.ones_like(templ, bool)
    truth = np.array([cj * res, ci * res])
    pf = core.HeightmapPF(3000, truth + [200, -150], 200, rng, kmeans_k=3, weight_power=3)
    for _ in range(5):
        c = pf.p.mean(0)
        sim, oe, on = core.similarity_map(fmap, templ, valid, c[0], c[1], 3 * pf.spread() + 150, res, 1.0)
        pf.update(sim, oe, on, res, 5.0)
    assert np.linalg.norm(pf.estimate() - truth) < 30


def test_similarity_map_origin_is_template_centre():
    res = 10.0
    pattern = smooth_field((11, 11), 10, sigma=1.0)
    pattern -= pattern.mean()
    fmap = np.zeros((60, 60))
    fmap[20:31, 30:41] = pattern
    templ = pattern
    sim, oe, on = core.similarity_map(fmap, templ, None, 350, 250, 150, res, 0.0)
    i, j = np.unravel_index(np.argmax(sim), sim.shape)
    assert (oe + j * res, on + i * res) == (350, 250)


def test_ccoeff_is_not_normalized_so_high_contrast_wins():
    # Eq. (1) has no variance normalization: a scaled copy of the pattern outscores the exact copy.
    pattern = smooth_field((9, 9), 12, sigma=1.0)
    img = np.zeros((40, 40))
    img[5:14, 5:14] = pattern
    img[25:34, 25:34] = 3 * pattern
    r = core.match_ccoeff(img, pattern)
    assert np.unravel_index(np.argmax(r), r.shape) == (25, 25)


def test_tercom_recovers_known_offset():
    res = 30.0
    dem = smooth_field((200, 200), 11, sigma=3.0) * 10
    s = np.linspace(0, 1, 80)
    true_e = 2000 + 2000 * s
    true_n = 2500 + 1500 * s
    profile = core.bilinear(dem, true_e, true_n, res) + 40.0
    de, dn, best, second = core.tercom_fix(dem, res, true_e - 120, true_n + 90, profile, 300, 15)
    assert (de, dn) == (120, -90)
    assert best < second
