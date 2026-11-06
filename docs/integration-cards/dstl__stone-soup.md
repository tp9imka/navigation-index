# Stone Soup - integration card
<!-- about: repo:dstl/stone-soup -->
One-line: Dstl's modular Python framework for tracking and state estimation (Kalman/EKF/UKF/particle filters, data association, track management, metrics); use it to turn ADS-B, Remote ID or DF bearing detections into tracks on one air picture, with bearing-only and range-bearing measurement models ready to use.

| | |
|---|---|
| Install | `pip install stonesoup` (latest release seen v1.9.1, 2026-06-24). `requires-python >= 3.11` in `pyproject.toml`. |
| Runs on | Any OS with Python 3.11+ (numpy/scipy stack). Tutorials and demos run in Jupyter. |
| Inputs | `Detection` objects carrying a `measurement_model`; readers for CSV (`CSVDetectionReader`, `CSVGroundTruthReader`, `CSVTrackReader` in `stonesoup/reader/generic.py`), dicts, pandas, YAML, HDF5, Kafka, video/images, OpenSky Network API (`reader/opensky.py`), AISHub (`reader/aishub.py`). Units are whatever your state vector uses; angle models use radians. |
| Outputs | `Track` objects (state sequences with covariances), metrics (OSPA, SIAP, PCRB), plots (`stonesoup.plotter`), YAML serialisation of whole tracker configs. |
| Key API / entry points | Models: `stonesoup.models.transition.linear.CombinedLinearGaussianTransitionModel`, `ConstantVelocity`; `stonesoup.models.measurement.nonlinear.Cartesian2DToBearing`, `CartesianToBearingRange`, `CartesianToElevationBearing`, `CartesianToBearingRangeRate`, `CartesianToElevationBearingRange`. Filters: `predictor.kalman.ExtendedKalmanPredictor`, `updater.kalman.ExtendedKalmanUpdater` (also Unscented, particle). Association: `hypothesiser.distance.DistanceHypothesiser` + `measures.Mahalanobis`, `dataassociator.neighbour.NearestNeighbour`, `GlobalNearestNeighbour`, `GNNWith2DAssignment`. Trackers: `tracker.simple.SingleTargetTracker`, `MultiTargetTracker`, `MultiTargetMixtureTracker`. Track management: `initiator.simple.*`, `deleter.time.UpdateTimeStepsDeleter`. |
| Time to first result | Estimate: 30 min to run the bearing-only example or a tutorial notebook; half a day to wire a live detection feed into a `MultiTargetTracker`. Assumes Python 3.11 env. |
| License | MIT. |

## Minimal usage
Imports and structure follow `docs/examples/filters/bearing_only_example.py`; tracker assembly is the standard tutorial pattern. Not run.

```python
import numpy as np
from datetime import datetime, timedelta
from stonesoup.models.transition.linear import CombinedLinearGaussianTransitionModel, ConstantVelocity
from stonesoup.models.measurement.nonlinear import Cartesian2DToBearing
from stonesoup.predictor.kalman import ExtendedKalmanPredictor
from stonesoup.updater.kalman import ExtendedKalmanUpdater
from stonesoup.types.detection import Detection
from stonesoup.types.state import GaussianState
from stonesoup.types.track import Track
from stonesoup.types.hypothesis import SingleHypothesis

tm = CombinedLinearGaussianTransitionModel([ConstantVelocity(0.5), ConstantVelocity(0.5)])
pred, upd = ExtendedKalmanPredictor(tm), ExtendedKalmanUpdater(measurement_model=None)

def bearing_detection(bearing_rad, sensor_xy, t):     # one DF station, local ENU metres
    mm = Cartesian2DToBearing(ndim_state=4, mapping=(0, 2),
                              noise_covar=np.array([[np.radians(5) ** 2]]),
                              translation_offset=np.array([[sensor_xy[0]], [sensor_xy[1]]]))
    return Detection(np.array([[bearing_rad]]), timestamp=t, measurement_model=mm)

track = Track([GaussianState([[1000], [0], [1000], [0]], np.diag([500, 10, 500, 10]) ** 2,
                             timestamp=datetime.now())])
# for each detection d from any station: p = pred.predict(track[-1], timestamp=d.timestamp)
#                                        track.append(upd.update(SingleHypothesis(p, d)))
```
Two or more stations with separated baselines make the target observable; one station needs own motion (the example's `MovingPlatform`).

## Wiring it into a nav stack
- DF: [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) JSON/XML (`radioBearing`, station lat/lon, heading) => convert to a local ENU frame with [pymap3d](./geospace-code__pymap3d.md) => `Cartesian2DToBearing` detections per station.
- ADS-B / Remote ID: positions from [readsb](./wiedehopf__readsb.md) or [receiver-android](./opendroneid__receiver-android.md) as linear position detections; the `docs/demos/OpenSky_Demo.py` and `AIS_Solent_Tracker.py` demos show real-data pipelines.
- Output tracks to TAK via [PyTAK](./snstac__pytak.md) (put the covariance into CoT `ce`) or to a web map with [milsymbol](./spatialillusions__milsymbol.md).
- For own-vehicle navigation filtering, a lighter option is [FilterPy](./rlabbe__filterpy.md) or [GTSAM](./borglab__gtsam.md); Stone Soup's strength is multi-target association and track management.
- Catalog: [Stone Soup page](../../catalog/repos/dstl__stone-soup.md).

## Gotchas
- Python 3.11+ only on current releases; older environments need an older Stone Soup.
- Angle handling: measurement types use `Bearing`/`Elevation` wrapped angle types; feeding raw degrees or unwrapped values breaks innovations near +/-pi. Open issue #316 discusses consistency of angular measurements and rotations.
- Bearing-only from a single static sensor is unobservable; the EKF will diverge quietly. Use two stations or a moving platform.
- Open #1314 (`is_clutter_detectable` vs `is_detectable` semantics) and #1269 (PCRB metric with multiple locations/models) affect simulation and metrics, not basic tracking.
- Keep it to air-picture awareness; the index scope excludes fire-control use.

## Alternatives
- [PyMHT](../../catalog/repos/erikliland__pymht.md): track-oriented MHT for maritime radar.
- [VIMMJIPDA](../../catalog/repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md): IMM-JIPDA multi-target tracker from NTNU.
- [FilterPy](./rlabbe__filterpy.md) when you only need a single-target filter.

Sources: `README.md`, `pyproject.toml`, `stonesoup/models/measurement/nonlinear.py`, `stonesoup/tracker/simple.py`, `stonesoup/dataassociator/neighbour.py`, `stonesoup/reader/` listing and `generic.py`, `docs/examples/filters/bearing_only_example.py` imports, `docs/demos/` listing, releases API, issue search (#316, #1314, #1269).
