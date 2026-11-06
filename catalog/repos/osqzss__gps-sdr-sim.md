# GPS-SDR-SIM

`repo:osqzss/gps-sdr-sim` - <https://github.com/osqzss/gps-sdr-sim>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3,474 | C | MIT | 2025-01-26 | True | archived | high |

Generates GPS L1 C/A baseband IQ sample files for a user-defined static or moving trajectory from a broadcast ephemeris file, for playback through an SDR.

**Why it matters:** The standard open test-signal generator for evaluating receiver behavior under simulated or spoofed conditions. Cabled or shielded-enclosure use only: radiating GNSS signals over the air is illegal in most jurisdictions.

**Hackathon notes:** Generate IQ files and feed GNSS-SDR directly (no RF needed) to test detectors. Repository archived in 2025 but still works. Cabled or shielded-enclosure use only: radiating GNSS signals over the air is illegal in most jurisdictions.

**Concepts:** [GNSS positioning](../concepts/gnss.md), [Jamming and spoofing](../concepts/gnss-interference.md), [Simulation and HIL/SITL](../concepts/simulation.md)

**Tags:** `simulator`, `iq`, `hackrf`, `gps-l1`

**Domains:** multi

## Related

- integrates_with: [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md)
- alternative_to: [multi-sdr-gps-sim](../repos/mictronics__multi-sdr-gps-sim.md)

## Referenced by

- [GNSS-SDR](../repos/gnss-sdr__gnss-sdr.md) (integrates_with)
- [multi-sdr-gps-sim](../repos/mictronics__multi-sdr-gps-sim.md) (fork_of)
- [bladeGPS](../repos/osqzss__bladegps.md) (extends)
- [LimeGPS](../repos/osqzss__limegps.md) (extends)
- [Low-cost GPS simulator: GPS spoofing by SDR (DEF CON 23)](../resources/defcon23-low-cost-gps-spoofing-sdr.md) (uses)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../resources/gps-is-gps-200n.md) (explains)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../resources/gps-is-gps-200n.md) (has_code)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
