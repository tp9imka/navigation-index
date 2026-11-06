"""Monocular VO baseline: KLT tracks + essential matrix on keyframes, metric scale from an
external source (here: ground-truth step length, i.e. a scale oracle).

This is the classic "avisingh mono-vo" recipe, not a VIO. It exists to show what a vision-only
front end does without an IMU, next to OpenVINS on the same bag.
"""
import cv2
import numpy as np

MAX_FEATS = 400
MIN_FEATS = 120
KEYFRAME_PARALLAX_PX = 12.0
RANSAC_PROB = 0.999


class MonoVO:
    def __init__(self, K, D, fisheye=True):
        self.K, self.D, self.fisheye = K, D, fisheye
        self.f = 0.5 * (K[0, 0] + K[1, 1])
        self.kf_img = self.kf_pts = None
        self.prev_img = self.prev_pts = None
        self.kf_idx = None
        self.rejected = 0

    def _norm(self, pts):
        p = pts.reshape(-1, 1, 2).astype(np.float64)
        if self.fisheye:
            return cv2.fisheye.undistortPoints(p, self.K, self.D).reshape(-1, 2)
        return cv2.undistortPoints(p, self.K, self.D).reshape(-1, 2)

    def _detect(self, img):
        p = cv2.goodFeaturesToTrack(img, MAX_FEATS, 0.01, 12)
        return p.reshape(-1, 2) if p is not None else np.zeros((0, 2), np.float32)

    def _new_keyframe(self, img, idx):
        self.kf_img, self.kf_idx = img, idx
        self.kf_pts = self._detect(img)
        self.prev_img, self.prev_pts = img, self.kf_pts.copy()

    def step(self, img, idx):
        """Returns (kf_idx, idx, R, t_unit, inliers) when a new keyframe pair is solved, else None.

        R, t map points from the previous keyframe camera into the current camera (x2 = R x1 + t).
        """
        if self.kf_img is None:
            self._new_keyframe(img, idx)
            return None
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(self.prev_img, img, self.prev_pts.astype(np.float32), None,
                                              winSize=(21, 21), maxLevel=3)
        good = st.reshape(-1) == 1
        self.kf_pts, nxt = self.kf_pts[good], nxt.reshape(-1, 2)[good]
        self.prev_img, self.prev_pts = img, nxt
        if len(nxt) < 8:
            self.rejected += 1
            self._new_keyframe(img, idx)
            return None
        parallax = float(np.median(np.linalg.norm(nxt - self.kf_pts, axis=1)))
        if parallax < KEYFRAME_PARALLAX_PX and len(nxt) >= MIN_FEATS:
            return None
        a, b = self._norm(self.kf_pts), self._norm(nxt)
        E, mask = cv2.findEssentialMat(a, b, np.eye(3), cv2.RANSAC, RANSAC_PROB, 1.0 / self.f)
        out = None
        if E is not None and E.shape == (3, 3):
            n, R, t, mask2 = cv2.recoverPose(E, a, b, np.eye(3), mask=mask)
            if n >= 15:
                out = (self.kf_idx, idx, R, t.reshape(3), int(n))
            else:
                self.rejected += 1
        else:
            self.rejected += 1
        self._new_keyframe(img, idx)
        return out


def chain(T_w_c0, steps, scales):
    """Compose keyframe steps into camera poses in the world frame."""
    poses = [T_w_c0]
    for (R, t), s in zip(steps, scales):
        T = np.eye(4)
        T[:3, :3], T[:3, 3] = R, t * s
        poses.append(poses[-1] @ np.linalg.inv(T))
    return poses
