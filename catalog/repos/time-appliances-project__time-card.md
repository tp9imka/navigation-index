# OCP Time Card

`repo:time-appliances-project/time-card` - <https://github.com/Time-Appliances-Project/Time-Card>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 1,491 | C | NOASSERTION | 2026-10-27 | False | production | low |

Open Compute Project Time Appliance Project hardware: a PCIe card with a GNSS receiver and an atomic or OCXO holdover oscillator that turns a server into a PTP grandmaster, plus specs and drivers.

**Why it matters:** An open reference design for exactly the GNSS + holdover-oscillator architecture resilient timing guidance recommends.

**Hackathon notes:** Hardware, not a 48 h build; read the architecture and holdover sections for design ideas.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `gpsdo`, `grandmaster`, `ocp`, `pcie`, `holdover`, `atomic-clock`

**Domains:** multi

## Related

- same_org: [Open Time Server spec](../../catalog/repos/time-appliances-project__open-time-server.md)
- integrates_with: [Meta Time libraries](../../catalog/repos/meta__time.md)
- integrates_with: [oscillatord](../../catalog/repos/orolia2s__oscillatord.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [Meta Time libraries](../../catalog/repos/meta__time.md) (integrates_with)
- [oscillatord](../../catalog/repos/orolia2s__oscillatord.md) (integrates_with)
- [Open Time Server spec](../../catalog/repos/time-appliances-project__open-time-server.md) (same_org)
- [How Precision Time Protocol is being deployed at Meta](../../catalog/resources/meta-ptp-at-meta-2022.md) (uses)
- [Open-sourcing a more precise time appliance](../../catalog/resources/meta-time-appliance-2021.md) (has_code)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
