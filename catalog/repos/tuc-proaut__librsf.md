# libRSF

`repo:tuc-proaut/librsf` - <https://github.com/TUC-ProAut/libRSF>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 340 | C++ | GPL-3.0 | 2026-04-06 | False | active-research | medium |

Ceres-based robust sensor fusion library: factor graph formulation, sliding-window filter with marginalization, and robust error models including self-tuning Gaussian mixtures for non-Gaussian, outlier-heavy measurements.

**Why it matters:** The open reference for robust error models in navigation factor graphs; its GNSS datasets are reused by later integrity work (ION ITM 2026).

**Hackathon notes:** GPL-3.0; Ubuntu 22.04/24.04 install script. Use its datasets and ideas; for a product prototype prefer GTSAM robust kernels.

**Concepts:** [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GNSS positioning](../../catalog/concepts/gnss.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `factor-graph`, `robust-estimation`, `gaussian-mixture`, `ceres`

**Domains:** ground, multi

## Related

- depends_on: [Ceres Solver](../../catalog/repos/ceres-solver__ceres-solver.md)
- alternative_to: [GTSAM](../../catalog/repos/borglab__gtsam.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)
- [FGO_gnss_integrity](../../catalog/repos/cntaylor__fgo_gnss_integrity.md) (evaluated_on)

_Indexed by lane(s): nav-differentiators_

_GitHub metadata fetched 2026-11-09._
