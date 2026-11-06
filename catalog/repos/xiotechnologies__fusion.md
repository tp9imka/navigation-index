# x-io Fusion

`repo:xiotechnologies/fusion` - <https://github.com/xioTechnologies/Fusion>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,767 | C | MIT | 2026-09-18 | False | production | high |

x-io Technologies' C AHRS library (revised Madgwick-style algorithm) with gyro offset correction, acceleration and magnetic disturbance rejection, and Python bindings.

**Why it matters:** Production-grade embedded attitude filter with disturbance rejection, from the Madgwick filter's originators.

**Hackathon notes:** Drop the C files into firmware or pip install imufusion for Python prototyping.

**Concepts:** [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Onboard / edge AI perception](../concepts/edge-ai.md)

**Tags:** `ahrs`, `madgwick`, `embedded`, `c`

**Domains:** multi

## Related

- alternative_to: [AHRS (Python)](../repos/mayitzin__ahrs.md)
- alternative_to: [MadgwickAHRS (Arduino)](../repos/arduino-libraries__madgwickahrs.md)

## Referenced by

- [MadgwickAHRS (Arduino)](../repos/arduino-libraries__madgwickahrs.md) (alternative_to)
- [AHRS (Python)](../repos/mayitzin__ahrs.md) (alternative_to)
- [An efficient orientation filter for inertial and inertial/magnetic sensor arrays](../resources/madgwick-orientation-filter-report.md) (has_code)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
