# IEZ (INS-EKF-ZUPT)

`repo:pajaraca/iez` - <https://github.com/pajaraca/IEZ>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 57 | Python | ? | 2022-08-15 | False | educational | high |

Python implementation (one 9-state script, plus ESP32 logger firmware) of a foot-mounted INS with EKF and zero-velocity updates for pedestrian dead reckoning, with sample datasets from two foot-mounted MPU6050 IMUs.

**Why it matters:** Compact reference for the standard ZUPT pedestrian tracker that underpins dismounted soldier navigation.

**Hackathon notes:** Runs offline on included data; reproduce with any cheap IMU strapped to a boot.

**Concepts:** [Indoor and pedestrian navigation](../concepts/indoor-pedestrian.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `zupt`, `foot-mounted`, `pdr`, `ekf`, `python`

**Domains:** dismounted

## Related

- alternative_to: [PyShoe](../repos/utiasstars__pyshoe.md)
- integrates_with: [OpenShoe: open source embedded foot-mounted INS](../resources/openshoe-foot-mounted-ins-2012.md)

## Referenced by

- [MPU6050 ZUPT](../repos/mtahakoroglu__mpu6050_zupt.md) (alternative_to)
- [OpenShoe: open source embedded foot-mounted INS](../resources/openshoe-foot-mounted-ins-2012.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
