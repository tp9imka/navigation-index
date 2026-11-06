# manif - integration card
<!-- about: repo:artivis/manif -->
Header-only C++ Lie group library (SO2/SE2/SO3/SE3/SE_2(3)/SGal(3)/Rn/Bundle) with analytic right Jacobians and Python bindings, so you can write an on-manifold ESKF or a Ceres factor in an afternoon without deriving Jacobians by hand.

| | |
|---|---|
| Install | C++ (header-only, needs Eigen3): `apt-get install libeigen3-dev`, then `git clone https://github.com/artivis/manif.git && cd manif && mkdir build && cd build && cmake .. && make install` (`docs/tutorial/cpp.md`). Python: `conda install -c conda-forge manifpy` (conda-forge 0.0.5, builds for linux-64, linux-aarch64, osx-64, osx-arm64, win-64), or from source `python3 -m pip install "pybind11[global]"` then `python3 -m pip install .` in the clone (`docs/tutorial/python.md`). **`manifpy` is not on PyPI** (pypi.org/pypi/manifpy/json returns 404), so `pip install manifpy` fails. Latest tag 0.0.5 (2024-08-11); `CMakeLists.txt` still says `project(manif VERSION 0.0.3)` (closed issue #312). |
| Runs on | Anything with a C++11 compiler and Eigen3. CMake warns on Eigen < 3.3.8 and on the buggy 3.3.6. No ROS dependency, no GPU. Python bindings via pybind11; MSVC `cl.exe` fails to compile them, `clang-cl` works (open issue #311). |
| Inputs | Group elements and tangent vectors as Eigen types (C++) or numpy arrays (Python). Tangent order matters: SE3 = (rho, theta), SE_2(3) = (rho, theta, nu), SGal(3) = (rho, nu, theta, s) (README "Tangent spaces"; note the SE_2(3)/SGal(3) order mismatch). |
| Outputs | Composed elements, tangent vectors, and optional Jacobians written into caller-supplied matrices (C++ `OptJacobianRef`, Python pass a numpy array to be filled). |
| Key API / entry points | Headers `#include <manif/manif.h>`, types `manif::SO3d`, `SE3d`, `SE3Tangentd`, `SE_2_3d`, `SGal3d`, `Bundle<...>`. Methods `X.inverse()`, `X.compose(Y)` / `X * Y`, `X.act(v)`, `X.log()`, `w.exp()`, `X.plus(w)` / `X + w` (right plus), `X.minus(Y)`, `X.between(Y)`, `X.adj()`, each with optional Jacobian args. Ceres glue in `include/manif/ceres/` (`manifold.h`, `objective.h`, `constraint.h`). Algorithms `include/manif/algorithms/` (`average.h`, `interpolation.h`, `bezier.h`, `decasteljau.h`). Python `from manifpy import SE3, SE3Tangent`. CMake `find_package(manif REQUIRED)`. |
| Time to first result | Estimate: 10 min with conda (run `examples/se3_localization.py`); 30 min for a C++ build with `-DBUILD_EXAMPLES=ON`. |
| License | MIT (`LICENSE`, Copyright 2018 Jeremie Deray). Bundles `external/tl/optional.hpp` (tl::optional, CC0 upstream). No weights or data. |

## Minimal usage
Not run. Condensed from `examples/se3_localization.py` (ESKF with beacon measurements, Jacobians from manif):

```python
import numpy as np
from manifpy import SE3, SE3Tangent

X = SE3.Identity(); P = np.zeros((SE3.DoF, SE3.DoF))
J_x = np.zeros((SE3.DoF, SE3.DoF)); J_u = np.zeros((SE3.DoF, SE3.DoF))
U = np.diag([0.1**2] * 6); R = np.diag([0.01**2] * 3)

u = SE3Tangent(np.array([0.1, 0, 0, 0, 0, 0.05]))   # body twist * dt
X = X.plus(u, J_x, J_u)                               # X * Exp(u), Jacobians filled in place
P = J_x @ P @ J_x.T + J_u @ U @ J_u.T

b = np.array([2.0, 0.0, 0.0])                         # beacon in world
J_xi_x = np.zeros((SE3.DoF, SE3.DoF)); J_e_xi = np.zeros((SE3.Dim, SE3.DoF))
e = X.inverse(J_xi_x).act(b, J_e_xi)                  # expected measurement
H = J_e_xi @ J_xi_x
Z = H @ P @ H.T + R
K = P @ H.T @ np.linalg.inv(Z)
X = X + SE3Tangent(K @ (y_measured - e))              # correction in tangent space at X
P = P - K @ Z @ K.T
```

Note the upstream example multiplies Jacobians with `*` in the propagation line (`J_x * P * J_x.transpose()`), which is element-wise on numpy arrays; use `@`.

## Wiring it into a nav stack
- Math layer under a hand-written ESKF/IEKF: SE_2(3) is the extended-pose group used by invariant EKFs (same idea as [DRIFT](./umich-curly__drift.md) and [AI-IMU](./mbrossar__ai-imu-dr.md)). Feed results into [robot_localization](./cra-ros-pkg__robot_localization.md) or MAVLink `ODOMETRY` yourself; manif has no I/O.
- Factor graphs: use `include/manif/ceres/` to put SE3 states into [Ceres](../../catalog/repos/ceres-solver__ceres-solver.md) problems (`docs/howto/ceres.md`). [GTSAM](./borglab__gtsam.md) has its own Lie types, so you do not need manif there.
- Python prototype then port: [navlie](./decargroup__navlie.md) gives the filter scaffolding in Python; manif gives the same groups in C++ when you move to onboard code.

## Gotchas
- Jacobians are right Jacobians w.r.t. a local tangent perturbation. Ceres autodiff expects Jacobians w.r.t. the raw parameter vector (quaternion), so use the provided `manifold.h` / local parameterization rather than mixing (README "Note", `docs/explanation/autodiff.md`).
- Tangent ordering is translation first (rho, theta), unlike some libraries (Sophus also uses translation first; GTSAM Pose3 uses rotation first). Covariances copied between libraries need permuting.
- Python bindings come from conda-forge or a source build only; no PyPI wheel.
- Open bug on `Bundle::element<Idx>()` (issue #342). No embedded/MCU port (issue #340).
- Quick-start links in README point at the devel branch (issue #333); docs site is the reliable reference.

## Alternatives
- [Sophus](../../catalog/repos/strasdat__sophus.md) - C++ Lie groups used by many VO/SLAM codebases; pick it if your SLAM code already depends on it.
- [liegroups](../../catalog/repos/utiasstars__liegroups.md) - pure Python/numpy (and PyTorch) Lie groups, no compiled build.
- [GTSAM](./borglab__gtsam.md) - if you want the solver and IMU preintegration too, not just the group math.

Sources: `README.md`, `LICENSE`, `CMakeLists.txt`, `setup.cfg`, `pyproject.toml`, `docs/tutorial/cpp.md`, `docs/tutorial/python.md`, `docs/howto/ceres.md`, `examples/se3_localization.py`, repo tree (`include/manif/`), release list, issues #311 #312 #333 #340 #342 (github.com/artivis/manif); pypi.org/pypi/manifpy/json (404); api.anaconda.org/package/conda-forge/manifpy.
