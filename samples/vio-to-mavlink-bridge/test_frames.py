import math
import random
import unittest

import frames

TOL = 1e-9
RANDOM_CASES = 200
RANDOM_SEED = 7


def yaw_quat(yaw):
    return (math.cos(yaw / 2), 0.0, 0.0, math.sin(yaw / 2))


def pitch_quat(pitch):
    return (math.cos(pitch / 2), 0.0, math.sin(pitch / 2), 0.0)


def flu_to_frd(v):
    return (v[0], -v[1], -v[2])


class FramesTest(unittest.TestCase):
    def assertVecAlmostEqual(self, a, b):
        for x, y in zip(a, b):
            self.assertAlmostEqual(x, y, delta=TOL)

    def test_position_enu_to_ned(self):
        self.assertEqual(frames.enu_to_ned((1.0, 2.0, 3.0)), (2.0, 1.0, -3.0))

    def test_identity_enu_means_facing_east(self):
        _, q = frames.convert_pose((0, 0, 0), (1.0, 0.0, 0.0, 0.0))
        roll, pitch, yaw = frames.quat_to_euler(q)
        self.assertAlmostEqual(roll, 0.0, delta=TOL)
        self.assertAlmostEqual(pitch, 0.0, delta=TOL)
        self.assertAlmostEqual(yaw, math.pi / 2, delta=TOL)

    def test_facing_north_is_identity_in_ned(self):
        _, q = frames.convert_pose((0, 0, 0), yaw_quat(math.pi / 2))
        self.assertVecAlmostEqual(q, (1.0, 0.0, 0.0, 0.0))

    def test_yaw_maps_to_ninety_minus_yaw(self):
        for yaw_enu_deg in (-170, -45, 0, 30, 120):
            yaw_enu = math.radians(yaw_enu_deg)
            _, q = frames.convert_pose((0, 0, 0), yaw_quat(yaw_enu))
            expected = math.atan2(math.sin(math.pi / 2 - yaw_enu), math.cos(math.pi / 2 - yaw_enu))
            self.assertAlmostEqual(frames.quat_to_euler(q)[2], expected, delta=TOL)

    def test_ros_positive_pitch_is_nose_down(self):
        # REP-103: +pitch about the left axis lowers the nose; MAVLink +pitch raises it.
        _, q = frames.convert_pose((0, 0, 0), pitch_quat(math.radians(10)))
        self.assertAlmostEqual(frames.quat_to_euler(q)[1], math.radians(-10), delta=TOL)

    def test_random_rotations_agree_on_body_vectors(self):
        rng = random.Random(RANDOM_SEED)
        for _ in range(RANDOM_CASES):
            q_enu = frames.quat_normalize(tuple(rng.gauss(0, 1) for _ in range(4)))
            body_flu = tuple(rng.uniform(-5, 5) for _ in range(3))
            via_enu = frames.enu_to_ned(frames.rotate(q_enu, body_flu))
            q_ned = frames.quat_enu_flu_to_ned_frd(q_enu)
            via_ned = frames.rotate(q_ned, flu_to_frd(body_flu))
            self.assertVecAlmostEqual(via_enu, via_ned)

    def test_world_velocity_to_body(self):
        _, q = frames.convert_pose((0, 0, 0), (1.0, 0.0, 0.0, 0.0))
        v_ned = frames.enu_to_ned((2.0, 0.0, 0.0))
        self.assertVecAlmostEqual(frames.world_to_body(q, v_ned), (2.0, 0.0, 0.0))

    def test_covariance_layout(self):
        cov = frames.diag_covariance(0.01, 0.001)
        self.assertEqual(len(cov), 21)
        self.assertEqual([cov[i] for i in frames.COV21_DIAGONAL], [0.01] * 3 + [0.001] * 3)
        self.assertAlmostEqual(sum(cov), 0.033, delta=TOL)
        self.assertTrue(math.isnan(frames.unknown_covariance()[0]))


if __name__ == "__main__":
    unittest.main()
