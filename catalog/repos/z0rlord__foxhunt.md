# foxhunt

`repo:z0rlord/foxhunt` - <https://github.com/Z0rlord/foxhunt>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1 | Python | MIT | 2026-07-17 | False | research-prototype | high |

Receive-only GNSS interference detection with radio direction finding and triangulation on Raspberry Pi and RTL-SDR.

**Why it matters:** Low-cost jammer localization is a practical defensive EW capability.

**Hackathon notes:** Needs 3+ Raspberry Pi + RTL-SDR nodes with directional antennas; start with foxhunt-sim and --mock-sdr after uv sync. Receive-only, but a live test still needs an authorised interference source. Rotator GPIO driver and PPS wiring are still planned.

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [RF localization and direction finding](../../catalog/concepts/rf-localization.md)

**Tags:** `rtl-sdr`, `rdf`, `raspberry-pi`, `jammer-localization`

**Domains:** ground

## Referenced by

- [Low-cost GNSS jammer sensor network: u-blox telemetry => localization => TAK and dashboard](../../catalog/samples/jammer-sensor-network.md) (explains)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
