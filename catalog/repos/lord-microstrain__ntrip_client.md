# ROS NTRIP client

`repo:lord-microstrain/ntrip_client` - <https://github.com/LORD-MicroStrain/ntrip_client>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 119 | Python | NOASSERTION | 2026-04-21 | False | production | high |

ROS/ROS 2 node that connects to an NTRIP caster and publishes RTCM corrections, forwarding NMEA position back to the caster.

**Why it matters:** Standard glue to get RTK corrections into a ROS robot.

**Hackathon notes:** apt-installable ROS package; works with any receiver driver accepting RTCM topics.

## Deep dives

- [_index-round5-c2-gis](../../docs/integration-cards/_index-round5-c2-gis.md) (integration-cards)
- [lord-microstrain__ntrip_client](../../docs/integration-cards/lord-microstrain__ntrip_client.md) (integration-cards)

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md)

**Tags:** `ntrip`, `ros2`, `rtcm`

**Domains:** ground, air

## Related

- integrates_with: [ublox ROS driver](../../catalog/repos/kumarrobotics__ublox.md)

## Referenced by

- [ublox ROS driver](../../catalog/repos/kumarrobotics__ublox.md) (integrates_with)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
