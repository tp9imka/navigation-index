# Matlab-LagrangianPMF

`repo:pesslovany/matlab-lagrangianpmf` - <https://github.com/pesslovany/Matlab-LagrangianPMF>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3 | MATLAB | AGPL-3.0 | 2026-10-30 | False | active-research | medium |

MATLAB implementation of Lagrangian grid-based (point-mass) filters for terrain-aided navigation, compared against other filters on real-world-based TAN models, with code for several related papers including the tensor-decomposition variant.

**Why it matters:** State-of-the-art grid filters for terrain-aided navigation that run in real time; a strong alternative to particle filters for radar-altimeter TRN.

**Hackathon notes:** Needs MATLAB; a mex file speeds the FFT time update and can be switched off. AGPL-3.0 licence matters if you ship derived code.

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md)

**Tags:** `point-mass-filter`, `terrain-aided-navigation`, `matlab`

**Domains:** air, underwater

## Related

- extends: [efficient-PMF](../../catalog/repos/idm-uwb__efficient-pmf.md)

## Referenced by

- [efficient-PMF](../../catalog/repos/idm-uwb__efficient-pmf.md) (alternative_to)
- [Tensor Decompositions for Online Grid-Based Terrain-Aided Navigation](../../catalog/resources/matousek-2026-tensor-decomposition-tan.md) (has_code)

_Indexed by lane(s): backlog_

_GitHub metadata fetched 2026-11-06._
