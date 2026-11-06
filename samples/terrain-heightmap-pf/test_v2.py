import inspect
import tempfile
import unittest
from pathlib import Path

try:
    import numpy as np
    import pytest
    from scipy.ndimage import gaussian_filter

    import core
    import nav2
    import sim
    HAVE_DEPS, MISSING = True, ""
except ImportError as e:  # plain python3 without the venv
    HAVE_DEPS, MISSING = False, str(e)


def smooth_field(shape, seed=0, sigma=3.0):
    rng = np.random.default_rng(seed)
    return gaussian_filter(rng.normal(0, 10, shape), sigma)


def test_ncc_matches_loop_and_is_gain_invariant():
    img = smooth_field((30, 30), 1)
    t = smooth_field((9, 9), 2)
    m = np.random.default_rng(3).random(t.shape) > 0.3
    rho, n, _ = core.ncc_map(img, t, m)
    np.testing.assert_allclose(rho, core.ncc_map_naive(img, t, m), atol=1e-9)
    np.testing.assert_allclose(core.ncc_map(img, 4 * t + 100, m)[0], rho, atol=1e-9)
    assert n == m.sum()


def test_ncc_loglik_is_zero_at_best_and_negative_elsewhere():
    img = smooth_field((60, 60), 4)
    t = img[20:35, 10:25]
    rho, n, _ = core.ncc_map(img, t, np.ones_like(t, bool))
    ll = core.ncc_loglik([rho], n, 9.0)[0]
    assert np.unravel_index(np.argmax(ll), ll.shape) == (20, 10)
    assert ll.max() == pytest.approx(0.0) and (ll <= 1e-12).all()


def test_rotate_patch_undoes_compass_rotation():
    res = 30.0
    world = smooth_field((200, 200), 5, sigma=4.0)
    c = np.array([100 * res, 100 * res])
    g = (np.arange(41) - 20) * res
    gu, gv = np.meshgrid(g, g)
    err = np.deg2rad(12.0)
    R = sim.rot(err)
    patch = core.bilinear(world, c[0] + R[0, 0] * gu + R[0, 1] * gv, c[1] + R[1, 0] * gu + R[1, 1] * gv, res)
    north = core.bilinear(world, c[0] + gu, c[1] + gv, res)
    mask = np.ones_like(patch, bool)
    good, m = core.rotate_patch(patch, mask, err)
    bad, mb = core.rotate_patch(patch, mask, -err)
    e_good = np.abs(good - north)[m].mean()
    e_bad = np.abs(bad - north)[mb].mean()
    assert e_good < 0.1 * e_bad
    assert m.sum() > 0.7 * m.size and not m[0, 0]


def test_crb_singular_for_ridge_and_flat_and_finite_for_texture():
    yy, xx = np.mgrid[0:21, 0:21].astype(float)
    m = np.ones((21, 21), bool)
    assert core.translation_crb(np.sin(xx / 3), m, 1.0, 30.0)[0] == float("inf")
    assert core.ncc_crb(np.zeros((21, 21)), m, 0.8, 9.0, 30.0) == float("inf")
    tex = smooth_field((21, 21), 6, sigma=1.5)
    hi = core.ncc_crb(tex, m, 0.9, 9.0, 30.0)
    lo = core.ncc_crb(tex, m, 0.3, 9.0, 30.0)
    assert np.isfinite(hi) and hi < lo
    # J is linear in 1/kappa, so the CRB scales with sqrt(kappa)
    assert core.ncc_crb(tex, m, 0.9, 36.0, 30.0) == pytest.approx(2 * hi)


def test_temper_keeps_ess_floor():
    ll = np.r_[0.0, -np.full(999, 50.0)]
    w, beta = core.temper_to_ess(ll, 0.1)
    assert 1 / np.sum(w ** 2) / len(w) >= 0.1 - 1e-6 and 0 < beta < 1
    w2, b2 = core.temper_to_ess(np.zeros(100), 0.1)
    assert b2 == 1.0 and np.allclose(w2, 0.01)


def test_heading_pf_predict_rotates_by_minus_bias():
    rng = np.random.default_rng(0)
    pf = core.HeadingPF(3, [0, 0], 0.0, 0.0, 1.0, rng)
    pf.p[:, 2] = [0.0, 0.2, -0.2]
    true_step = np.array([10.0, 0.0])
    pf.predict(sim.rot(0.2) @ true_step)
    np.testing.assert_allclose(pf.p[1, :2], true_step, atol=1e-9)
    assert np.linalg.norm(pf.p[0, :2] - true_step) > 1.5


def synthetic(rough):
    rng = np.random.default_rng(7)
    base = gaussian_filter(rng.normal(0, 1, (560, 560)), 6)
    return 300 + (base / base.std()) * (15 if rough else 0.01), 30.0


CFG = sim.with_(sim.Config(), methods=("pf",), feature="grad", jitter_frac=0.1, n_particles=1000) if HAVE_DEPS else None


def test_v2_estimates_20_deg_compass_bias_on_textured_terrain():
    dem, res = synthetic(True)
    cfg = sim.with_(CFG, compass_bias_sigma_deg=0.0, compass_bias_fixed_deg=20.0)
    r = nav2.run_v2(dem, res, 1, cfg, nav2.V2(), sim.map_features(dem, cfg))
    assert r["err_odom"][-1] > 2000
    assert r["err_pf"][-1] < 60
    assert abs(np.rad2deg(r["rec_bias_est"][-1] - r["rec_bias_true"][-1])) < 2.0


def test_v2_gate_falls_back_to_odometry_on_flat_terrain():
    dem, res = synthetic(False)
    r = nav2.run_v2(dem, res, 2, CFG, nav2.V2(), sim.map_features(dem, CFG))
    assert not r["rec_applied"].any()
    assert np.abs(r["err_pf"] - r["err_odom"]).max() < 50
    # without the gate the filter follows noise on the same flight
    r2 = nav2.run_v2(dem, res, 2, CFG, nav2.V2(gate=False), sim.map_features(dem, CFG))
    assert r2["rec_applied"].all()
    assert np.abs(r2["err_pf"] - r2["err_odom"]).max() > 50


# `python3 -m unittest discover` (CI, plain interpreter) does not collect pytest-style functions.
# This class runs them under unittest and skips them without the sample venv; pytest ignores the
# class (__test__ = False) and runs the functions directly.
@unittest.skipUnless(HAVE_DEPS, f"needs the sample venv: {MISSING}")
class PytestFunctions(unittest.TestCase):
    __test__ = False


def _as_method(fn):
    def method(self):
        if "tmp_path" in inspect.signature(fn).parameters:
            with tempfile.TemporaryDirectory() as d:
                fn(Path(d))
        else:
            fn()
    method.__name__ = fn.__name__
    return method


for _name, _fn in list(globals().items()):
    if _name.startswith("test_") and inspect.isfunction(_fn):
        setattr(PytestFunctions, _name, _as_method(_fn))
