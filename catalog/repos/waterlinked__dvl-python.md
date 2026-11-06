# Water Linked DVL Python

`repo:waterlinked/dvl-python` - <https://github.com/waterlinked/dvl-python>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 9 | Python | ? | 2024-02-21 | False | production | medium |

Example Python code for talking to Water Linked DVLs over their serial and TCP/JSON protocols, parsing velocity and dead-reckoning reports.

**Why it matters:** DVL velocity is the core GNSS-free aid for underwater dead reckoning; this is the shortest route to real DVL data.

**Hackathon notes:** Needs a DVL or recorded JSON; protocol is simple JSON over TCP so a replay mock is easy.

**Concepts:** [Underwater navigation](../concepts/underwater-nav.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `dvl`, `waterlinked`, `a50`, `driver`

**Domains:** underwater

## Related

- same_org: [Water Linked DVL A50 ROS driver](../repos/waterlinked__dvl-a50-ros-driver.md)
- integrates_with: [AuvEstimator](../repos/alliwong__auvestimator.md)

## Referenced by

- [AuvEstimator](../repos/alliwong__auvestimator.md) (integrates_with)
- [Water Linked DVL A50 ROS driver](../repos/waterlinked__dvl-a50-ros-driver.md) (same_org)
- [Water Linked documentation (DVL and Underwater GPS)](../resources/waterlinked-docs.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
