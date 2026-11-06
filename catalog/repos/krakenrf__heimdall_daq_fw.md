# Heimdall DAQ firmware

`repo:krakenrf/heimdall_daq_fw` - <https://github.com/krakenrf/heimdall_daq_fw>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 100 | C | GPL-3.0 | 2026-01-05 | False | active-research | medium |

Coherent multichannel SDR acquisition chain (sync, calibration, decimation) underneath KrakenSDR DoA and passive radar apps.

**Why it matters:** Useful if you need raw coherent IQ for your own DF or interference-localization algorithm.

**Hackathon notes:** Installed as part of the KrakenSDR image; modify only if building custom DSP.

**Concepts:** [RF localization and direction finding](../concepts/rf-localization.md), [Sensor calibration](../concepts/calibration.md)

**Tags:** `sdr`, `coherent`, `daq`

**Domains:** multi

## Related

- same_org: [KrakenSDR DoA DSP](../repos/krakenrf__krakensdr_doa.md)

## Referenced by

- [KrakenSDR DoA DSP](../repos/krakenrf__krakensdr_doa.md) (depends_on)

_Indexed by lane(s): defense-context_

_GitHub metadata fetched 2026-11-06._
