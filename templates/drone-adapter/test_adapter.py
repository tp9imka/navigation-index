"""Smoke test: frame round-trips and example_loop on MockAdapter. Run: python3 -m unittest -v"""
import math
import unittest

from adapter import (Adapter, body_to_world, enu_to_ned, flu_to_frd, frd_to_flu, ned_to_enu,
                     world_to_body, yaw_enu_to_ned, yaw_ned_to_enu)
from example_loop import fly_to
from mock import MockAdapter

VECS = [(1.0, 2.0, 3.0), (-0.5, 0.0, 7.25), (0.0, -4.0, -1.0)]
YAWS = [0.0, 0.3, math.pi / 2, -2.5, 3.1]


class Frames(unittest.TestCase):
    def test_round_trips(self):
        for v in VECS:
            self.assertEqual(ned_to_enu(enu_to_ned(v)), v)
            self.assertEqual(frd_to_flu(flu_to_frd(v)), v)
            for yaw in YAWS:
                for a, b in zip(body_to_world(world_to_body(v, yaw), yaw), v):
                    self.assertAlmostEqual(a, b, places=12)
        for yaw in YAWS:
            self.assertAlmostEqual(math.remainder(yaw_ned_to_enu(yaw_enu_to_ned(yaw)) - yaw,
                                                  math.tau), 0.0, places=12)

    def test_known_values(self):
        self.assertEqual(enu_to_ned((1.0, 0.0, 0.0)), (0.0, 1.0, -0.0))  # east => NED y
        self.assertAlmostEqual(yaw_enu_to_ned(0.0), math.pi / 2)        # facing east
        self.assertAlmostEqual(yaw_enu_to_ned(math.pi / 2), 0.0)        # facing north
        f, l, _ = world_to_body((0.0, 1.0, 0.0), math.pi / 2)           # north while facing north
        self.assertAlmostEqual(f, 1.0)
        self.assertAlmostEqual(l, 0.0)


class Loop(unittest.TestCase):
    def test_mock_is_adapter(self):
        self.assertIsInstance(MockAdapter(), Adapter)

    def test_reaches_goal(self):
        mock = MockAdapter()
        self.assertLess(fly_to(mock, (5.0, 3.0, 1.0)), 0.15)
        self.assertFalse(mock.collided)

    def test_stops_before_wall(self):
        mock = MockAdapter()                   # wall x=4, y in [-1, 1]; goal behind it
        d = fly_to(mock, (6.0, 0.0, 1.0), timeout_s=20.0)
        self.assertFalse(mock.collided)
        self.assertGreater(d, 1.0)
        self.assertGreater(mock.min_wall_dist, mock.radius)


if __name__ == "__main__":
    unittest.main()
