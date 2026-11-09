"""Vehicle and adapter with altitude, for the 3D arena (world_z.py).

VehicleZ is vehicle.Vehicle with hold_z=False: it integrates the commanded vz with the same
first-order lag (tau 0.15 s), |a_z| <= a_max and |vz| <= vz_max (1.0 m/s default). Horizontal
dynamics are unchanged.

SimAdapterZ is adapter.SimAdapter whose ranges() casts the horizontal fan at the vehicle's true
height, so a 2D lidar at 1 m sees through a window at 2 m. pose() already carries z and vz.
"""
from __future__ import annotations

try:
    from .adapter import SimAdapter
    from .vehicle import Vehicle
except ImportError:
    from adapter import SimAdapter
    from vehicle import Vehicle


class VehicleZ(Vehicle):
    def __init__(self, x: float = 0.0, y: float = 0.0, z0: float = 1.0, yaw: float = 0.0,
                 vz_max: float = 1.0, **kw):
        kw.pop("hold_z", None)
        super().__init__(x, y, z0, yaw, vz_max=vz_max, hold_z=False, **kw)


class SimAdapterZ(SimAdapter):
    """world must be a world_z.WorldZ (raycast takes a height)."""

    def ranges(self):
        v = self.vehicle
        return self.sensor.scan(self.world.at_height(float(v.p[2])), v.p[0], v.p[1], v.yaw, v.t)
