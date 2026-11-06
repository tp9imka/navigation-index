# IEZ (INS-EKF-ZUPT)

`repo:pajaraca/iez` - <https://github.com/pajaraca/IEZ>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 57 | Python | ? | 2022-08-15 | False | educational | high |

Python implementation (one 9-state script, plus ESP32 logger firmware) of a foot-mounted INS with EKF and zero-velocity updates for pedestrian dead reckoning, with sample datasets from two foot-mounted MPU6050 IMUs.

**Why it matters:** Compact reference for the standard ZUPT pedestrian tracker that underpins dismounted soldier navigation.

**Hackathon notes:** Runs offline on included data; reproduce with any cheap IMU strapped to a boot.

**Concepts:** [Indoor and pedestrian navigation](../../catalog/concepts/indoor-pedestrian.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `zupt`, `foot-mounted`, `pdr`, `ekf`, `python`

**Domains:** dismounted

## Related

- alternative_to: [PyShoe](../../catalog/repos/utiasstars__pyshoe.md)
- integrates_with: [OpenShoe: open source embedded foot-mounted INS](../../catalog/resources/openshoe-foot-mounted-ins-2012.md)

## Referenced by

- [MPU6050 ZUPT](../../catalog/repos/mtahakoroglu__mpu6050_zupt.md) (alternative_to)
- [OpenShoe: open source embedded foot-mounted INS](../../catalog/resources/openshoe-foot-mounted-ins-2012.md) (explains)
- [Dismounted foot-mounted INS: stdlib 15-state ZUPT EKF on the real pyshoe hallway data, cross-checked against pyshoe, with corridor heading, UWB and TAK output](../../catalog/samples/dismounted-foot-ins.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
