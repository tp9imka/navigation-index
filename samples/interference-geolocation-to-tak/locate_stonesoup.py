"""Stone Soup bearing-only emitter localisation: particle filter (heavy-tailed bearing
likelihood for multipath) and UKF (innovation gating). Static emitter, random-walk state."""
import math
from datetime import datetime, timezone

import numpy as np
from stonesoup.base import Property
from stonesoup.models.measurement.nonlinear import Cartesian2DToBearing
from stonesoup.models.transition.linear import CombinedLinearGaussianTransitionModel, RandomWalk
from stonesoup.predictor.kalman import UnscentedKalmanPredictor
from stonesoup.predictor.particle import ParticlePredictor
from stonesoup.regulariser.particle import MCMCRegulariser
from stonesoup.resampler.particle import ESSResampler
from stonesoup.types.angle import Bearing as SSBearing
from stonesoup.types.array import StateVector, StateVectors
from stonesoup.types.detection import Detection
from stonesoup.types.hypothesis import SingleHypothesis
from stonesoup.types.state import GaussianState, ParticleState
from stonesoup.updater.kalman import UnscentedKalmanUpdater
from stonesoup.updater.particle import ParticleUpdater

from geo import LocalFrame, bearing_in_frame

STATIC_Q_M2_PER_S = 1.0        # random-walk jitter for a (nearly) static emitter
PRIOR_HALF_WIDTH_M = 15000.0   # PF: uniform prior box around the station centroid
UKF_PRIOR_SIGMA_M = 5000.0
GATE_CHI2_1DOF = 9.0           # 3-sigma innovation gate for the UKF
DEFAULT_PARTICLES = 5000
DEFAULT_OUTLIER_P = 0.15


class RobustBearing(Cartesian2DToBearing):
    """Gaussian bearing likelihood mixed with a uniform floor, so a multipath bearing
    cannot drag the whole particle cloud onto its (wrong) line."""
    outlier_p: float = Property(default=DEFAULT_OUTLIER_P)

    def logpdf(self, state1, state2, **kwargs):
        g = super().logpdf(state1, state2, **kwargs)
        return np.logaddexp(np.log1p(-self.outlier_p) + g, np.log(self.outlier_p / (2 * np.pi)))


def _setup(bearings, sigma_deg, station_sigma, outlier_p):
    bearings = sorted(bearings, key=lambda b: b.t)
    frame = LocalFrame(sum(b.lat for b in bearings) / len(bearings),
                       sum(b.lon for b in bearings) / len(bearings))
    dets = []
    for b in bearings:
        e, n, _ = frame.to_enu(b.lat, b.lon)
        sig = math.radians((station_sigma or {}).get(b.station_id, sigma_deg))
        model = RobustBearing(ndim_state=2, mapping=(0, 1), noise_covar=np.array([[sig ** 2]]),
                              translation_offset=StateVector([e, n]), outlier_p=outlier_p)
        math_angle = math.radians(90.0 - bearing_in_frame(frame, b.lat, b.lon, b.bearing_deg))  # compass => atan2(north, east)
        dets.append(Detection(StateVector([SSBearing(math_angle)]),
                              timestamp=datetime.fromtimestamp(b.t, timezone.utc),
                              measurement_model=model))
    transition = CombinedLinearGaussianTransitionModel([RandomWalk(STATIC_Q_M2_PER_S)] * 2)
    return frame, dets, transition


def _result(frame, mean, cov, n_used, n_total):
    lat, lon, _ = frame.to_geodetic(float(mean[0]), float(mean[1]))
    return {"lat": lat, "lon": lon, "enu": (float(mean[0]), float(mean[1])), "frame": frame,
            "cov": [[float(cov[0, 0]), float(cov[0, 1])], [float(cov[1, 0]), float(cov[1, 1])]],
            "n_used": n_used, "n_total": n_total}


def locate_pf(bearings, sigma_deg, station_sigma=None, n_particles=DEFAULT_PARTICLES,
              outlier_p=DEFAULT_OUTLIER_P, seed=0):
    frame, dets, transition = _setup(bearings, sigma_deg, station_sigma, outlier_p)
    rng = np.random.default_rng(seed)
    pts = rng.uniform(-PRIOR_HALF_WIDTH_M, PRIOR_HALF_WIDTH_M, size=(2, n_particles))
    state = ParticleState(StateVectors(pts), log_weight=np.full(n_particles, -np.log(n_particles)),
                          timestamp=dets[0].timestamp)
    predictor = ParticlePredictor(transition)
    updater = ParticleUpdater(measurement_model=None, resampler=ESSResampler(),
                              regulariser=MCMCRegulariser(transition_model=transition))
    for det in dets:
        pred = predictor.predict(state, timestamp=det.timestamp)
        state = updater.update(SingleHypothesis(pred, det))
    return _result(frame, state.mean, state.covar, len(dets), len(dets))


def locate_ukf(bearings, sigma_deg, station_sigma=None, outlier_p=DEFAULT_OUTLIER_P):
    frame, dets, transition = _setup(bearings, sigma_deg, station_sigma, outlier_p)
    state = GaussianState(StateVector([0.0, 0.0]), np.diag([UKF_PRIOR_SIGMA_M ** 2] * 2),
                          timestamp=dets[0].timestamp)
    predictor = UnscentedKalmanPredictor(transition)
    updater = UnscentedKalmanUpdater(measurement_model=None)
    used = 0
    for det in dets:
        pred = predictor.predict(state, timestamp=det.timestamp)
        mp = updater.predict_measurement(pred, measurement_model=det.measurement_model)
        innov = float(SSBearing(det.state_vector[0, 0] - mp.state_vector[0, 0]))
        if innov ** 2 / float(mp.covar[0, 0]) > GATE_CHI2_1DOF:
            state = pred
            continue
        state = updater.update(SingleHypothesis(pred, det))
        used += 1
    return _result(frame, state.state_vector, state.covar, used, len(dets))
