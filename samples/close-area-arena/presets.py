"""Sensor presets for the arena range sensor.

Values and their basis come from docs/research/close-area-nav/08-crazyflie-sensing-limits.md
("doc 08"), sections 2 and 6. Each value is tagged in a comment:
  [doc08 x.y]  quoted from that section of doc 08 (which cites datasheet / docs / code / paper)
  [proposal]   picked for this arena, no published number behind it

"ideal" is the arena default fan (run.DEFAULTS["sensor"]) and is served by sensors.RangeFan
unchanged: one exact ray per beam, every material seen. The others are served by
sensors_cone.ConeRangeFan (cone beams, minimum range, range-dependent noise, materials).

make_sensor(name, rng) builds the sensor for one run.

Custom sensors and vehicles. make_sensor also takes a dict in the user-facing schema
  {"beams", "fov_deg", "max_range_m", "min_range_m", "noise_sigma_m"}  required
  {"cone_deg", "dropout"}                                            optional (0 deg, 0.02)
and vehicle_kwargs(spec) turns a vehicle name or dict {"radius_m", "v_max", "a_max", "tau"} into the
vehicle.Vehicle keyword arguments (run.DEFAULTS["vehicle"] shape). Unknown or missing keys raise
ValueError naming them. A sensor dict is served by sensors_cone.ConeRangeFan with constant noise
(noise_sigma_m), cone beams of cone_deg (0 = one exact ray per beam), the closest sub-ray as the beam
reading, glass and mirror invisible (doc 08 2.4, true for ToF, lidar and active stereo alike) and no
dark-surface cut. The named presets depth_cam_87 and lidar_2d are written in that schema, so a dict
with the same numbers flies the same sensor, readings included.
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

# ---- user-facing sensor schema ----
SENSOR_SPEC_REQUIRED = ("beams", "fov_deg", "max_range_m", "min_range_m", "noise_sigma_m")
SENSOR_SPEC_DEFAULTS = {"cone_deg": 0.0,   # 0 = one exact ray per beam
                        "dropout": 0.02}   # as ideal (CONTRACT.md)
FULL_CIRCLE_DEG = 360.0
SPEC_SUB_RAY_DEG = 1.5        # [proposal] sub-ray spacing inside a cone: n_sub = 1 + ceil(cone_deg / 1.5)
SPEC_MIN_FILL = 0.0           # [proposal] beam = closest sub-ray (a depth image row keeps its nearest pixel)
SPEC_INVISIBLE = ("glass", "mirror")   # [doc08 2.4] ToF; lidar and active IR stereo also see through glass

# Forward depth camera, Intel RealSense D435i class.
#   fov 87 deg horizontal: Intel D435i specifications page ("Depth Field of View H:87 V:58")
#   https://www.intel.com/content/www/us/en/products/sku/190004/intel-realsense-depth-camera-d435i/specifications.html
#   min 0.3 m: same page ("Operating Range ~.3m - 3m"). max 5 m: [proposal, from the task brief], beyond
#   Intel's ~3 m operating range, where the error grows (community answers: drift after 3-4 m).
#   noise 0.04 m: D400 datasheet depth accuracy "< 2% at 2 m" (0.04 m at 2 m), held constant over range
#   (ConeRangeFan has no d^2 stereo noise model) [proposal].
DEPTH_CAM_87_BEAMS = 30            # [proposal] one beam per 3 deg column band of the depth image
DEPTH_CAM_87_FOV_DEG = 87.0
DEPTH_CAM_87_MIN_RANGE_M = 0.3
DEPTH_CAM_87_MAX_RANGE_M = 5.0
DEPTH_CAM_87_NOISE_M = 0.04
DEPTH_CAM_87_CONE_DEG = DEPTH_CAM_87_FOV_DEG / (DEPTH_CAM_87_BEAMS - 1)   # 3 deg: cones tile the field of view
DEPTH_CAM_87_DROPOUT = 0.05        # [proposal] stereo holes on low-texture surfaces, no published rate

# 2D scanning lidar, Slamtec RPLIDAR A1 class (https://www.slamtec.com/en/lidar/a1spec):
#   360 deg, 0.15-12 m, angular resolution <= 1 deg, accuracy 1 % of range up to 3 m.
LIDAR_2D_BEAMS = 360               # 1 deg apart
LIDAR_2D_FOV_DEG = FULL_CIRCLE_DEG
LIDAR_2D_MIN_RANGE_M = 0.15
LIDAR_2D_MAX_RANGE_M = 12.0
LIDAR_2D_NOISE_M = 0.03            # 1 % at 3 m, held constant [proposal]
LIDAR_2D_CONE_DEG = 0.0            # laser spot: one exact ray per beam [proposal]
LIDAR_2D_DROPOUT = 0.02            # [proposal] as ideal

SENSOR_SPECS = {
    "depth_cam_87": {"beams": DEPTH_CAM_87_BEAMS, "fov_deg": DEPTH_CAM_87_FOV_DEG,
                     "max_range_m": DEPTH_CAM_87_MAX_RANGE_M, "min_range_m": DEPTH_CAM_87_MIN_RANGE_M,
                     "noise_sigma_m": DEPTH_CAM_87_NOISE_M, "cone_deg": DEPTH_CAM_87_CONE_DEG,
                     "dropout": DEPTH_CAM_87_DROPOUT},
    "lidar_2d": {"beams": LIDAR_2D_BEAMS, "fov_deg": LIDAR_2D_FOV_DEG,
                 "max_range_m": LIDAR_2D_MAX_RANGE_M, "min_range_m": LIDAR_2D_MIN_RANGE_M,
                 "noise_sigma_m": LIDAR_2D_NOISE_M, "cone_deg": LIDAR_2D_CONE_DEG,
                 "dropout": LIDAR_2D_DROPOUT},
}

# ---- user-facing vehicle schema ----
VEHICLE_SPEC_KEYS = ("radius_m", "v_max", "a_max", "tau")
VEHICLE_SPECS = {
    # = run.DEFAULTS["vehicle"]: radius world.RADIUS 0.15 m, v_max 2 m/s, a_max 3 m/s^2, tau 0.15 s
    "default": {"radius_m": 0.15, "v_max": 2.0, "a_max": 3.0, "tau": 0.15},
}


def check_keys(spec: dict, required, optional, what: str) -> None:
    if not isinstance(spec, dict):
        raise ValueError(f"{what} must be a name or a dict, got {type(spec).__name__}")
    unknown = sorted(set(spec) - set(required) - set(optional))
    if unknown:
        raise ValueError(f"unknown {what} keys: {', '.join(map(str, unknown))} "
                         f"(allowed: {', '.join(list(required) + list(optional))})")
    missing = [k for k in required if k not in spec]
    if missing:
        raise ValueError(f"missing {what} keys: {', '.join(missing)}")


def _num(spec: dict, key: str, what: str, lo: float, hi: float = math.inf, lo_open: bool = False) -> float:
    v = spec[key]
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError(f"{what} {key} must be a finite number, got {v!r}")
    if v < lo or v > hi or (lo_open and v == lo):
        raise ValueError(f"{what} {key} = {v} is outside {'(' if lo_open else '['}{lo}, {hi}]")
    return float(v)


def sensor_spec(spec) -> dict:
    """Validated team-facing sensor dict (defaults filled in). A str is a SENSOR_SPECS name."""
    if isinstance(spec, str):
        if spec not in SENSOR_SPECS:
            raise ValueError(f"no sensor spec named {spec!r} (have {', '.join(SENSOR_SPECS)})")
        spec = SENSOR_SPECS[spec]
    check_keys(spec, SENSOR_SPEC_REQUIRED, SENSOR_SPEC_DEFAULTS, "sensor")
    s = dict(SENSOR_SPEC_DEFAULTS, **spec)
    b = s["beams"]
    if isinstance(b, bool) or not isinstance(b, (int, float)) or b != int(b) or b < 1:
        raise ValueError(f"sensor beams must be a whole number >= 1, got {b!r}")
    out = {"beams": int(b),
           "fov_deg": _num(s, "fov_deg", "sensor", 0.0, FULL_CIRCLE_DEG, lo_open=True),
           "max_range_m": _num(s, "max_range_m", "sensor", 0.0, lo_open=True),
           "min_range_m": _num(s, "min_range_m", "sensor", 0.0),
           "noise_sigma_m": _num(s, "noise_sigma_m", "sensor", 0.0),
           "cone_deg": _num(s, "cone_deg", "sensor", 0.0, FULL_CIRCLE_DEG),
           "dropout": _num(s, "dropout", "sensor", 0.0, 1.0)}
    if out["min_range_m"] >= out["max_range_m"]:
        raise ValueError(f"sensor min_range_m {out['min_range_m']} must be below max_range_m {out['max_range_m']}")
    return out


def _cone_params(s: dict) -> dict:
    """ConeRangeFan arguments for a validated team-facing sensor dict."""
    n_sub = 1 if s["cone_deg"] <= 0 else 1 + math.ceil(s["cone_deg"] / SPEC_SUB_RAY_DEG - 1e-9)
    return {"n_beams": s["beams"], "fov": math.radians(s["fov_deg"]), "max_range": s["max_range_m"],
            "noise_std": s["noise_sigma_m"], "dropout": s["dropout"], "noise_model": "constant",
            "cone_deg": s["cone_deg"], "n_sub": n_sub, "min_fill": SPEC_MIN_FILL,
            "min_range": s["min_range_m"], "invisible": SPEC_INVISIBLE, "dark_max_range": None}


for _name, _spec in SENSOR_SPECS.items():
    SENSOR_PRESETS[_name] = dict(model="cone", **_cone_params(sensor_spec(_spec)))


def describe_sensor(name_or_spec) -> dict:
    """The sensor actually flown, in the team-facing schema (plus "name" and "model")."""
    if isinstance(name_or_spec, str):
        if name_or_spec in SENSOR_SPECS:
            return dict(name=name_or_spec, model="cone", **sensor_spec(name_or_spec))
        if name_or_spec not in SENSOR_PRESETS:
            raise ValueError(f"unknown sensor preset {name_or_spec!r} (have {', '.join(SENSOR_PRESETS)})")
        p = SENSOR_PRESETS[name_or_spec]
        return {"name": name_or_spec, "model": p["model"], "beams": p["n_beams"],
                "fov_deg": round(math.degrees(p["fov"]), 6), "max_range_m": p["max_range"],
                "min_range_m": p.get("min_range", 0.0), "noise_sigma_m": p["noise_std"],
                "cone_deg": p.get("cone_deg", 0.0), "dropout": p["dropout"]}
    return dict(name="custom", model="cone", **sensor_spec(name_or_spec))


def sensor_fov(name_or_spec) -> float:
    """Field of view in rad of a preset name or sensor dict."""
    if isinstance(name_or_spec, str) and name_or_spec not in SENSOR_SPECS:
        return SENSOR_PRESETS[name_or_spec]["fov"]
    return math.radians(sensor_spec(name_or_spec)["fov_deg"])


def make_sensor(name, rng):
    """name: a SENSOR_PRESETS key, or a team-facing sensor dict (see the module docstring)."""
    if isinstance(name, str):
        if name not in SENSOR_PRESETS:
            raise ValueError(f"unknown sensor preset {name!r} (have {', '.join(SENSOR_PRESETS)})")
        p = SENSOR_PRESETS[name]
    else:
        p = dict(model="cone", **_cone_params(sensor_spec(name)))
    if p["model"] == "ray":
        return RangeFan(rng=rng, **{k: p[k] for k in _RAY_KEYS})
    return ConeRangeFan(rng=rng, **{k: p[k] for k in _CONE_KEYS})


def vehicle_spec(spec) -> dict:
    """Validated team-facing vehicle dict. A str is a VEHICLE_SPECS name."""
    if isinstance(spec, str):
        if spec not in VEHICLE_SPECS:
            raise ValueError(f"no vehicle spec named {spec!r} (have {', '.join(VEHICLE_SPECS)})")
        spec = VEHICLE_SPECS[spec]
    check_keys(spec, VEHICLE_SPEC_KEYS, (), "vehicle")
    return {k: _num(spec, k, "vehicle", 0.0, lo_open=True) for k in VEHICLE_SPEC_KEYS}


def vehicle_kwargs(spec) -> dict:
    """vehicle.Vehicle keyword arguments (run.DEFAULTS["vehicle"] shape) for a name or dict."""
    v = vehicle_spec(spec)
    return {"tau": v["tau"], "a_max": v["a_max"], "v_max": v["v_max"], "radius": v["radius_m"]}
