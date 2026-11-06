import unittest

import ekf_flags

# A healthy GPS-aided copter in flight: attitude, velocities, rel+abs horizontal and
# abs vertical position, plus predicted horizontal positions.
HEALTHY_GPS = 0x033F
# Dead-reckoning hold: attitude only, constant position mode.
CONST_POS = 0x0081


class EkfFlagsTest(unittest.TestCase):
    def test_decode_healthy(self):
        self.assertEqual(ekf_flags.decode(HEALTHY_GPS), [
            "ATTITUDE", "VELOCITY_HORIZ", "VELOCITY_VERT", "POS_HORIZ_REL", "POS_HORIZ_ABS",
            "POS_VERT_ABS", "PRED_POS_HORIZ_REL", "PRED_POS_HORIZ_ABS"])

    def test_gps_glitch_bit(self):
        self.assertIn("GPS_GLITCHING", ekf_flags.decode(HEALTHY_GPS | 0x8000))

    def test_position_predicates(self):
        self.assertTrue(ekf_flags.has_absolute_position(HEALTHY_GPS))
        self.assertTrue(ekf_flags.has_horizontal_position(HEALTHY_GPS))
        self.assertFalse(ekf_flags.has_horizontal_position(CONST_POS))
        self.assertFalse(ekf_flags.has_absolute_position(CONST_POS))
        rel_only = ekf_flags.POS_HORIZ_REL | 1
        self.assertTrue(ekf_flags.has_horizontal_position(rel_only))
        self.assertFalse(ekf_flags.has_absolute_position(rel_only))

    def test_uninitialized_has_no_position(self):
        self.assertFalse(ekf_flags.has_horizontal_position(HEALTHY_GPS | ekf_flags.UNINITIALIZED))

    def test_variance_classes(self):
        self.assertEqual(ekf_flags.classify_variance(0.1), "good")
        self.assertEqual(ekf_flags.classify_variance(0.5), "warn")
        self.assertEqual(ekf_flags.classify_variance(0.79), "warn")
        self.assertEqual(ekf_flags.classify_variance(0.8), "bad")

    def test_summarize(self):
        line = ekf_flags.summarize({"flags": CONST_POS, "velocity_variance": 0.9,
                                    "pos_horiz_variance": 0.2, "pos_vert_variance": 0.6,
                                    "compass_variance": 0.0})
        self.assertEqual(line, "flags=0x0081 pos=NONE vel=0.90(bad) pos_h=0.20(good) "
                               "pos_v=0.60(warn) mag=0.00(good)")


if __name__ == "__main__":
    unittest.main()
