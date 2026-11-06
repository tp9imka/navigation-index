# strapdown-rs

`repo:jbrodovsky/strapdown-rs` - <https://github.com/jbrodovsky/strapdown-rs>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 8 | Rust | MIT | 2026-10-20 | False | active-research | medium |

Rust library and CLI for strapdown INS research under GNSS denial: local-level mechanization, four loosely coupled filters (ESKF, EKF, UKF, Rao-Blackwellized particle filter) and a simulator that removes or corrupts GNSS in recorded or synthetic data from a scenario file.

**Why it matters:** Lesser-known, actively developed Rust INS; memory-safe option for embedded or simulation pipelines.

**Hackathon notes:** cargo build; library crate is strapdown-core (docs.rs) and the CLI is strapdown-sim. Loosely coupled only, no pseudorange or carrier-phase models.

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `rust`, `strapdown`

**Domains:** multi

## Related

- alternative_to: [pyins](../../catalog/repos/nmayorov__pyins.md)

_Indexed by lane(s): ins-fusion_

_GitHub metadata fetched 2026-11-06._
