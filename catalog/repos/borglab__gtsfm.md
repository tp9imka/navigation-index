# GTSfM

`repo:borglab/gtsfm` - <https://github.com/borglab/gtsfm>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 528 | Jupyter Notebook | NOASSERTION | 2026-11-06 | False | active-research | medium |

End-to-end structure-from-motion pipeline built on GTSAM, with pluggable front-ends (classical and learned matchers) and distributed execution via Dask.

**Why it matters:** Builds georeferenceable 3D maps from drone or ground imagery, which can serve as prior maps for visual localization.

**Hackathon notes:** No compilation: `uv tool install .` (or `pip install .` in Python 3.12) from a recursive checkout, then `gtsfm run` opens a browser workspace with sample scenes; `gtsfm execute` is the CLI path for your own image folders. Expect long runtimes on large sets - downsample.

**Concepts:** [Visual SLAM](../concepts/visual-slam.md), [Feature detection and matching](../concepts/feature-matching.md), [GIS, maps and geospatial data](../concepts/gis-mapping.md)

**Tags:** `sfm`, `gtsam`, `dask`, `3d-reconstruction`

**Domains:** air, ground

## Related

- depends_on: [GTSAM](../repos/borglab__gtsam.md)

## Referenced by

- [GTSAM](../repos/borglab__gtsam.md) (same_org)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
