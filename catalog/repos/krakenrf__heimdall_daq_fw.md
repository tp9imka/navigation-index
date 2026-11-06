# Heimdall DAQ firmware

`repo:krakenrf/heimdall_daq_fw` - <https://github.com/krakenrf/heimdall_daq_fw>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 100 | C | GPL-3.0 | 2026-01-05 | False | active-research | medium |

Coherent multichannel SDR acquisition chain (sync, calibration, decimation) underneath KrakenSDR DoA and passive radar apps.

**Why it matters:** Useful if you need raw coherent IQ for your own DF or interference-localization algorithm.

**Hackathon notes:** Installed as part of the KrakenSDR image; modify only if building custom DSP.

## Deep dives

- [_index-round3](../../docs/integration-cards/_index-round3.md) (integration-cards)
- [krakenrf__heimdall_daq_fw](../../docs/integration-cards/krakenrf__heimdall_daq_fw.md) (integration-cards)

**Concepts:** [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Sensor calibration](../../catalog/concepts/calibration.md)

**Tags:** `sdr`, `coherent`, `daq`

**Domains:** multi

## Related

- same_org: [KrakenSDR DoA DSP](../../catalog/repos/krakenrf__krakensdr_doa.md)

## Referenced by

- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [TDOA evaluation with RTL-SDRs](../../catalog/repos/dc9st__tdoa-evaluation-rtlsdr.md) (alternative_to)
- [KrakenSDR DoA DSP](../../catalog/repos/krakenrf__krakensdr_doa.md) (depends_on)
- [GNSS jammer geolocation from DF bearings to TAK](../../catalog/samples/interference-geolocation-to-tak.md) (explains)

_Indexed by lane(s): defense-context_

_GitHub metadata fetched 2026-11-06._
