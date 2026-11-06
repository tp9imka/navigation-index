# MPU6050 ZUPT

`repo:mtahakoroglu/mpu6050_zupt` - <https://github.com/mtahakoroglu/MPU6050_ZUPT>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | C++ | MIT | 2024-07-02 | False | research-prototype | medium |

Arduino library forked from MPU6050_tockn that reads and calibrates an MPU6050 and streams angles and time series to Python plotting scripts. The README says foot-mounted INS / ZUPT support is planned but the repo is under construction; no zero-velocity detector or INS code is in it yet.

**Why it matters:** Low-cost hardware path to a working foot-mounted INS demo.

**Hackathon notes:** Only the IMU reading and calibration part exists; you would write the ZUPT detector and INS yourself (see pajaraca/IEZ or OpenShoe for the algorithm). Needs an MPU6050 and an Arduino-class board; expect heading drift without magnetometer aiding.

**Concepts:** [Indoor and pedestrian navigation](../concepts/indoor-pedestrian.md), [Inertial navigation (INS/IMU)](../concepts/ins.md)

**Tags:** `zupt`, `mpu6050`, `arduino`, `foot-mounted`

**Domains:** dismounted

## Related

- alternative_to: [IEZ (INS-EKF-ZUPT)](../repos/pajaraca__iez.md)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
