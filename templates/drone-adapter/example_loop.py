"""Go-to-goal with stop-if-close at 20 Hz, written only against the Adapter protocol."""
from __future__ import annotations

import math
import time

try:                                    # works as a package or as a flat folder
    from .adapter import Adapter, Setpoint, world_to_body
except ImportError:
    from adapter import Adapter, Setpoint, world_to_body

RATE_HZ, V_MAX, K_P, STOP_DIST, GOAL_TOL, CONE = 20.0, 1.0, 0.8, 0.6, 0.10, math.radians(30)


def fly_to(ad: Adapter, goal: tuple[float, float, float], timeout_s: float = 60.0,
           realtime: bool = False) -> float:
    """Fly toward goal (ENU, metres). Returns the final 3D distance to goal."""
    for _ in range(int(timeout_s * RATE_HZ)):
        p, scan = ad.pose(), ad.ranges()
        err = (goal[0] - p.x, goal[1] - p.y, goal[2] - p.z)
        dist = math.sqrt(sum(e * e for e in err))
        if dist < GOAL_TOL:
            break
        v = [K_P * e for e in err]
        n = math.sqrt(sum(c * c for c in v))
        v = [c * V_MAX / n for c in v] if n > V_MAX else v
        bx, by, _ = world_to_body((v[0], v[1], 0.0), p.yaw)
        heading = math.atan2(by, bx)     # commanded direction in body frame
        blocked = any(d < STOP_DIST and abs(math.remainder(a - heading, math.tau)) < CONE
                      for a, d in zip(scan.angles, scan.distances))
        if blocked:                      # stop horizontally, keep altitude control
            v[0] = v[1] = 0.0
        ad.send_setpoint(Setpoint(v[0], v[1], v[2]))
        if realtime:
            time.sleep(1.0 / RATE_HZ)    # a real loop should use a monotonic scheduler
    ad.send_setpoint(Setpoint(0.0, 0.0, 0.0))
    p = ad.pose()
    return math.dist((p.x, p.y, p.z), goal)


if __name__ == "__main__":
    from mock import MockAdapter  # run as a script from this folder
    mock, goal = MockAdapter(), (5.0, 3.0, 1.0)
    d = fly_to(mock, goal)
    print(f"goal={goal} final_distance_m={d:.3f} t_s={mock.t:.2f} "
          f"collided={mock.collided} min_wall_dist_m={mock.min_wall_dist:.2f}")
