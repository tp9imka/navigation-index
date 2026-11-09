"""Sensor presets for the arena range sensor.

Values and their basis come from docs/research/close-area-nav/08-crazyflie-sensing-limits.md
("doc 08"), sections 2 and 6. Each value is tagged in a comment:
  [doc08 x.y]  quoted from that section of doc 08 (which cites datasheet / docs / code / paper)
  [proposal]   picked for this arena, no published number behind it

"ideal" is the arena default fan (run.DEFAULTS["sensor"]) and is served by sensors.RangeFan
unchanged: one exact ray per beam, every material seen. The others are served by
sensors_cone.ConeRangeFan (cone beams, minimum range, range-dependent noise, materials).

make_sensor(name, rng) builds the sensor for one run.
"""
from __future__ import annotations

import math

try:
    from .sensors import RangeFan
    from .sensors_cone import ConeRangeFan
except ImportError:
    from sensors import RangeFan
    from sensors_cone import ConeRangeFan

SENSOR_PRESETS = {
    # Arena default: 72 ideal rays, 360 deg, 6 m, 0.02 m noise, 2 % dropout (CONTRACT.md).
    "ideal": {
        "model": "ray",
        "n_beams": 72, "fov": 2 * math.pi, "max_range": 6.0, "noise_std": 0.02, "dropout": 0.02,
    },
    # Crazyflie Multi-ranger, nominal indoor light. Horizontal beams front, left, back, right.
    "crazyflie": {
        "model": "cone",
        "n_beams": 4,                      # [doc08 2.1] 4 horizontal VL53L1x (up beam not in 2.5D)
        "fov": 2 * math.pi,                # [doc08 6] beams 90 deg apart => -180, -90, 0, 90 deg
        "max_range": 3.0,                  # [proposal, doc08 6] margin below 3.6 m long-mode dark
        "noise_std": 0.02,                 # [doc08 2.2] ST ranging error +-20-25 mm
        "noise_model": "zranger",          # [doc08 2.3] Bitcraze zranger2.c std(d), added in quadrature [proposal]
        "dropout": 0.05,                   # [proposal, doc08 6] no published dropout rate
        "cone_deg": 27.0,                  # [doc08 2.1] 27 deg full cone, all SPADs
        "n_sub": 11,                       # [proposal] sub-rays per cone (2.7 deg apart)
        "min_fill": 0.15,                  # [proposal] cone fraction a target must fill; doc08 2.4 says
                                           #   narrow objects are missed, no minimum diameter published
        "min_range": 0.04,                 # [doc08 2.1] 4 cm, closer is detected but not accurate
        "invisible": ("glass", "mirror"),  # [doc08 2.4] BatDeck: glass doors not detected
        "dark_max_range": 1.0,             # [proposal, doc08 6] dark surfaces => inf beyond 1.0 m
        "rate_hz": 10,                     # [doc08 2.1] multiranger.c 100 ms; arena plan_hz is 10
    },
    # Same deck in strong ambient light.
    "crazyflie_bright": {
        "model": "cone",
        "n_beams": 4, "fov": 2 * math.pi,  # [doc08 2.1, 6]
        "max_range": 0.73,                 # [doc08 2.2] long mode, strong ambient light, ST figure
        "noise_std": 0.02,                 # [doc08 2.2]
        "noise_model": "zranger",          # [doc08 2.3] + [proposal] quadrature
        "dropout": 0.10,                   # [proposal, doc08 6] "a guess"
        "cone_deg": 27.0,                  # [doc08 2.1]
        "n_sub": 11, "min_fill": 0.15,     # [proposal]
        "min_range": 0.04,                 # [doc08 2.1]
        "invisible": ("glass", "mirror"),  # [doc08 2.4]
        "dark_max_range": 0.5,             # [proposal, doc08 6]
        "rate_hz": 10,                     # [doc08 2.1]
    },
    # Dense multi-zone ToF / 2D lidar class sensor with real cones. Whole preset is a [proposal].
    "dense": {
        "model": "cone",
        "n_beams": 72, "fov": 2 * math.pi, "max_range": 6.0,   # [proposal] same layout as ideal
        "noise_std": 0.02, "noise_model": "zranger",          # [proposal] floor as ideal
        "dropout": 0.02,                                       # [proposal] as ideal
        "cone_deg": 5.0, "n_sub": 3, "min_fill": 0.34,         # [proposal] cones tile the circle
        "min_range": 0.04,                                     # [proposal] VL53-class, doc08 2.1
        "invisible": ("glass", "mirror"),                      # [doc08 2.4] same physics for any ToF
        "dark_max_range": 2.0,                                 # [proposal]
        "rate_hz": 10,
    },
}

_RAY_KEYS = ("n_beams", "fov", "max_range", "noise_std", "dropout")
_CONE_KEYS = _RAY_KEYS + ("noise_model", "cone_deg", "n_sub", "min_fill", "min_range",
                          "invisible", "dark_max_range")


def make_sensor(name: str, rng):
    p = SENSOR_PRESETS[name]
    if p["model"] == "ray":
        return RangeFan(rng=rng, **{k: p[k] for k in _RAY_KEYS})
    return ConeRangeFan(rng=rng, **{k: p[k] for k in _CONE_KEYS})
