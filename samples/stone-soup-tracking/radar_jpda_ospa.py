"""Two small UAVs seen by one ground radar: EKF + JPDA tracking and OSPA scoring with Stone Soup.

Requires: pip install -r requirements.txt (stonesoup, numpy, scipy). Run with stonesoup 1.9.1.
"""
from datetime import datetime, timedelta

import numpy as np

from stonesoup.dataassociator.probability import JPDA
from stonesoup.functions import gm_reduce_single
from stonesoup.hypothesiser.probability import PDAHypothesiser
from stonesoup.measures import Euclidean
from stonesoup.metricgenerator.manager import MultiManager
from stonesoup.metricgenerator.ospametric import OSPAMetric
from stonesoup.models.measurement.nonlinear import CartesianToBearingRange
from stonesoup.models.transition.linear import CombinedLinearGaussianTransitionModel, ConstantVelocity
from stonesoup.predictor.kalman import ExtendedKalmanPredictor
from stonesoup.types.angle import Bearing
from stonesoup.types.array import StateVector, StateVectors
from stonesoup.types.detection import Clutter, TrueDetection
from stonesoup.types.groundtruth import GroundTruthPath, GroundTruthState
from stonesoup.types.state import GaussianState
from stonesoup.types.track import Track
from stonesoup.types.update import GaussianStateUpdate
from stonesoup.updater.kalman import ExtendedKalmanUpdater

SEED = 2026
STEPS = 60
DT = timedelta(seconds=1)
PROCESS_NOISE = 0.5          # m^2/s^3 per axis, small agile UAV
BEARING_SIGMA_DEG = 1.0
RANGE_SIGMA_M = 10.0
MAX_RANGE_M = 3000.0
PROB_DETECT = 0.9
CLUTTER_RATE = 3             # mean false alarms per scan
OSPA_CUTOFF_M = 100.0
OSPA_ORDER = 1
RADAR_XY = np.array([[0.0], [0.0]])

# state = [x, vx, y, vy]; two UAVs on crossing paths ~1.5 km out
INITIAL_STATES = ([-1500, 15, 500, 0], [-1500, 15, 900, -8])
PRIOR_COVAR = np.diag([50.0 ** 2, 5.0 ** 2, 50.0 ** 2, 5.0 ** 2])

np.random.seed(SEED)
start = datetime.now().replace(microsecond=0)
times = [start + k * DT for k in range(STEPS)]

transition_model = CombinedLinearGaussianTransitionModel(
    [ConstantVelocity(PROCESS_NOISE), ConstantVelocity(PROCESS_NOISE)])
measurement_model = CartesianToBearingRange(
    ndim_state=4,
    mapping=(0, 2),
    noise_covar=np.diag([np.radians(BEARING_SIGMA_DEG) ** 2, RANGE_SIGMA_M ** 2]),
    translation_offset=RADAR_XY,
)

# Lists, not sets: set order follows random uuids, which would reorder the noise draws per run.
truths = []
for init in INITIAL_STATES:
    truth = GroundTruthPath([GroundTruthState(init, timestamp=times[0])])
    for t in times[1:]:
        truth.append(GroundTruthState(
            transition_model.function(truth[-1], noise=True, time_interval=DT), timestamp=t))
    truths.append(truth)

scans = []
for k, t in enumerate(times):
    detections = set()
    for truth in truths:
        if np.random.rand() <= PROB_DETECT:
            detections.add(TrueDetection(
                state_vector=measurement_model.function(truth[k], noise=True),
                timestamp=t, measurement_model=measurement_model, groundtruth_path=truth))
    for _ in range(np.random.poisson(CLUTTER_RATE)):
        detections.add(Clutter(
            StateVector([Bearing(np.random.uniform(-np.pi, np.pi)),
                         np.random.uniform(0, MAX_RANGE_M)]),
            timestamp=t, measurement_model=measurement_model))
    scans.append((t, detections))

predictor = ExtendedKalmanPredictor(transition_model)
updater = ExtendedKalmanUpdater(measurement_model)
# clutter density = expected false alarms / measurement-space volume (bearing span * range span)
hypothesiser = PDAHypothesiser(predictor=predictor, updater=updater,
                               clutter_spatial_density=CLUTTER_RATE / (2 * np.pi * MAX_RANGE_M),
                               prob_detect=PROB_DETECT)
data_associator = JPDA(hypothesiser=hypothesiser)

# Known priors keep the sketch short; swap in an initiator for real pop-up targets.
tracks = [Track([GaussianState(np.array(init, dtype=float).reshape(-1, 1), PRIOR_COVAR,
                               timestamp=times[0])]) for init in INITIAL_STATES]

for t, detections in scans[1:]:
    hypotheses = data_associator.associate(set(tracks), detections, t)
    for track in tracks:
        track_hypotheses = hypotheses[track]
        states, weights = [], []
        for hypothesis in track_hypotheses:
            states.append(updater.update(hypothesis) if hypothesis else hypothesis.prediction)
            weights.append(hypothesis.probability)
        mean, covar = gm_reduce_single(
            StateVectors([s.state_vector for s in states]),
            np.stack([s.covar for s in states], axis=2),
            np.asarray(weights, dtype=float))
        track.append(GaussianStateUpdate(mean, covar, track_hypotheses, t))

ospa = OSPAMetric(c=OSPA_CUTOFF_M, p=OSPA_ORDER, measure=Euclidean((0, 2)),
                  generator_name="ospa", tracks_key="tracks", truths_key="truths")
manager = MultiManager([ospa])
manager.add_data({"tracks": set(tracks), "truths": set(truths)})
metrics = manager.generate_metrics()

per_step = metrics["ospa"]["OSPA distances"].value
values = [float(m.value) for m in per_step]
print(f"scans={len(scans)} tracks={len(tracks)} truths={len(truths)}")
print(f"OSPA (c={OSPA_CUTOFF_M:g} m, p={OSPA_ORDER}): mean={np.mean(values):.1f} m "
      f"max={np.max(values):.1f} m final={values[-1]:.1f} m")
for i, track in enumerate(tracks):
    x, _, y, _ = track.state_vector.ravel()
    print(f"track {i} final position x={x:.0f} m y={y:.0f} m")
for i, truth in enumerate(truths):
    x, _, y, _ = truth.state_vector.ravel()
    print(f"truth {i} final position x={x:.0f} m y={y:.0f} m")
