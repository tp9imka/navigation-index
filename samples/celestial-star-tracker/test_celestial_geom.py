import math
import os
import random
import unittest

import celestial_geom as cg

try:
    import numpy  # noqa: F401
    import skyfield  # noqa: F401
    HAVE_SKYFIELD = True
except ImportError:
    HAVE_SKYFIELD = False

HERE = os.path.dirname(os.path.abspath(__file__))
D = math.radians


def synthetic_stars(lat, lon, n=8, seed=0, h_min=30, h_max=80):
    """(GHA, dec) of stars spread in azimuth with elevations in [h_min, h_max] at (lat, lon)."""
    rng = random.Random(seed)
    up = cg.unit_from_lat_lon(lat, lon)
    east = cg.norm(cg.cross((0, 0, 1), up))
    north = cg.cross(up, east)
    stars = []
    for i in range(n):
        az = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        h = D(rng.uniform(h_min, h_max))
        v = tuple(math.cos(h) * math.sin(az) * east[k] + math.cos(h) * math.cos(az) * north[k]
                  + math.sin(h) * up[k] for k in range(3))
        dec, ra_east = cg.lat_lon_from_unit(v)
        stars.append((-ra_east, dec, v))   # Earth-fixed frame at t=0: GHA = -longitude
    return stars, up


def local_enu(lat, lon):
    up = cg.unit_from_lat_lon(lat, lon)
    east = cg.norm(cg.cross((0, 0, 1), up))
    north = cg.cross(up, east)
    return east, north, up


class Geometry(unittest.TestCase):
    def test_alt_matches_vector_dot(self):
        lat, lon = D(48.2), D(16.4)
        stars, up = synthetic_stars(lat, lon)
        for gha, dec, v in stars:
            h, _ = cg.alt_az(lat, lon, gha, dec)
            self.assertAlmostEqual(h, cg.elevation(v, up), places=12)

    def test_azimuth_convention(self):
        lat, lon = D(40), D(0)
        east, north, up = local_enu(lat, lon)
        for az_deg in (0, 90, 180, 270, 33):
            az = D(az_deg)
            v = tuple(math.cos(D(45)) * (math.sin(az) * east[k] + math.cos(az) * north[k])
                      + math.sin(D(45)) * up[k] for k in range(3))
            dec, ra_east = cg.lat_lon_from_unit(v)
            h, a = cg.alt_az(lat, lon, -ra_east, dec)
            self.assertAlmostEqual(math.degrees(h), 45, places=9)
            self.assertAlmostEqual((math.degrees(a) - az_deg + 180) % 360 - 180, 0, places=9)

    def test_fix_recovers_truth_noise_free(self):
        lat, lon = D(-33.9), D(151.2)
        stars, up = synthetic_stars(lat, lon, n=6, seed=3)
        obs = [(g, d, cg.elevation(v, up)) for g, d, v in stars]
        sol = cg.solve_fix(obs, lat0=D(-30), lon0=D(145))
        self.assertTrue(sol["converged"])
        self.assertLess(cg.great_circle_m(lat, lon, sol["lat"], sol["lon"]), 0.01)

    def test_one_arcmin_level_error_is_one_nautical_mile(self):
        lat, lon = D(55.0), D(12.0)
        stars, up = synthetic_stars(lat, lon, n=12, seed=5)
        east, north, _ = local_enu(lat, lon)
        for direction in (0.0, 1.0, 2.5, 4.0):
            horiz = tuple(math.sin(direction) * east[k] + math.cos(direction) * north[k]
                          for k in range(3))
            axis = cg.norm(cg.cross(up, horiz))
            for arcmin in (0.5, 1.0, 5.0):
                up_imu = cg.rotate(up, axis, arcmin * cg.ARCMIN)
                obs = [(g, d, cg.elevation(v, up_imu)) for g, d, v in stars]
                sol = cg.solve_fix(obs, lat0=lat, lon0=lon)
                err = cg.great_circle_m(lat, lon, sol["lat"], sol["lon"])
                expected = cg.position_error_from_level_error(arcmin * cg.ARCMIN)
                self.assertAlmostEqual(err / expected, 1.0, places=6)
        self.assertAlmostEqual(cg.position_error_from_level_error(cg.ARCMIN), 1853.25, places=1)

    def test_level_error_moves_fix_toward_tilt_direction(self):
        lat, lon = D(10.0), D(-70.0)
        stars, up = synthetic_stars(lat, lon, n=10, seed=2)
        east, north, _ = local_enu(lat, lon)
        axis = cg.norm(cg.cross(up, north))
        up_imu = cg.rotate(up, axis, 2 * cg.ARCMIN)
        obs = [(g, d, cg.elevation(v, up_imu)) for g, d, v in stars]
        sol = cg.solve_fix(obs, lat0=lat, lon0=lon)
        self.assertAlmostEqual(math.degrees(sol["lat"] - lat) * 60, 2.0, places=6)
        self.assertAlmostEqual(math.degrees(sol["lon"] - lon) * 60, 0.0, places=6)

    def test_time_error_is_pure_east_west(self):
        lat, lon = D(60.0), D(25.0)
        stars, up = synthetic_stars(lat, lon, n=8, seed=9)
        obs_true = [(g, d, cg.elevation(v, up)) for g, d, v in stars]
        dt = 1.0
        # the navigator's clock is 1 s fast: it uses the sky of t+dt for elevations taken at t
        obs = [(g + cg.OMEGA_EARTH * dt, d, h) for g, d, h in obs_true]
        sol = cg.solve_fix(obs, lat0=lat, lon0=lon)
        self.assertAlmostEqual(sol["lat"], lat, places=10)
        east = cg.great_circle_m(lat, lon, sol["lat"], sol["lon"])
        self.assertAlmostEqual(east, cg.east_error_from_time_error(dt, lat), delta=0.01)
        self.assertAlmostEqual(cg.east_error_from_time_error(1.0, 0.0), 464.6, delta=0.1)
        self.assertLess(sol["lon"], lon)   # clock fast => fix too far west

    def test_single_azimuth_geometry_is_singular_or_flagged(self):
        lat, lon = D(30.0), D(30.0)
        east, north, up = local_enu(lat, lon)
        obs = []
        for h_deg in (30, 50, 70):
            v = tuple(math.cos(D(h_deg)) * north[k] + math.sin(D(h_deg)) * up[k]
                      for k in range(3))
            dec, ra_east = cg.lat_lon_from_unit(v)
            obs.append((-ra_east, dec, D(h_deg)))
        sol = cg.solve_fix(obs, lat0=lat, lon0=lon)
        self.assertTrue(sol["singular"] or sol["az_spread_deg"] < 1.0)

    def test_refraction_bennett(self):
        self.assertAlmostEqual(cg.refraction_bennett(D(45)) / cg.ARCMIN, 0.99, delta=0.02)
        self.assertAlmostEqual(cg.refraction_bennett(D(90)) / cg.ARCMIN, 0.0, delta=0.01)
        self.assertGreater(cg.refraction_bennett(D(10)), cg.refraction_bennett(D(30)))
        thin = cg.refraction_bennett(D(45), pressure_hpa=265, temp_c=-50)
        self.assertLess(thin, 0.35 * cg.refraction_bennett(D(45)))

    def test_accel_to_level_error(self):
        mg = 1e-3 * cg.G0
        self.assertAlmostEqual(cg.level_error_from_accel(mg) / cg.ARCMIN, 3.44, delta=0.01)

    def test_zenith_fix(self):
        lat, lon = D(-12.3), D(-45.6)
        la, lo = cg.zenith_fix(cg.unit_from_lat_lon(lat, lon))
        self.assertAlmostEqual(la, lat, places=12)
        self.assertAlmostEqual(lo, lon, places=12)


@unittest.skipIf(not HAVE_SKYFIELD, "numpy/skyfield not installed")
class SkyfieldPipeline(unittest.TestCase):
    def test_noise_free_skyfield_fix_under_50_m(self):
        if not os.path.exists(os.path.join(HERE, "data", "de421.bsp")):
            self.skipTest("run fetch_data.py first (de421.bsp)")
        import position_fix_sim as sim
        r = sim.run_once(sim.Scenario(level_err_arcmin=0.0, centroid_noise_arcsec=0.0,
                                      vib_sigma_deg=0.0), seed=0)
        self.assertLess(r["err_m"], 50.0)


if __name__ == "__main__":
    unittest.main()
