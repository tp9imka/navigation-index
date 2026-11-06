# Water Linked DVL Python

`repo:waterlinked/dvl-python` - <https://github.com/waterlinked/dvl-python>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 9 | Python | ? | 2024-02-21 | False | archived | medium |

Example Python code for talking to Water Linked DVLs over their serial and TCP/JSON protocols, parsing velocity and dead-reckoning reports.

**Why it matters:** DVL velocity is the core GNSS-free aid for underwater dead reckoning; this is the shortest route to real DVL data.

**Hackathon notes:** Archived by Water Linked and no longer maintained, but the serial (wldvl) and TCP parsers still work as examples. Needs a DVL or recorded JSON; protocol is simple JSON over TCP so a replay mock is easy. No LICENSE file, so all rights reserved by default.

**Concepts:** [Underwater navigation](../../catalog/concepts/underwater-nav.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `dvl`, `waterlinked`, `a50`, `driver`

**Domains:** underwater

## Related

- same_org: [Water Linked DVL A50 ROS driver](../../catalog/repos/waterlinked__dvl-a50-ros-driver.md)
- integrates_with: [AuvEstimator](../../catalog/repos/alliwong__auvestimator.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [AuvEstimator](../../catalog/repos/alliwong__auvestimator.md) (integrates_with)
- [Water Linked DVL A50 ROS driver](../../catalog/repos/waterlinked__dvl-a50-ros-driver.md) (same_org)
- [Water Linked documentation (DVL and Underwater GPS)](../../catalog/resources/waterlinked-docs.md) (explains)

_Indexed by lane(s): domains-swarm_

_GitHub metadata fetched 2026-11-06._
