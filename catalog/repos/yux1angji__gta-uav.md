# Game4Loc / GTA-UAV

`repo:yux1angji/gta-uav` - <https://github.com/Yux1angJi/GTA-UAV>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 177 | Python | Apache-2.0 | 2025-10-20 | False | active-research | high |

Benchmark and code for UAV geo-localization trained on synthetic game imagery with partial-match drone-satellite pairs (AAAI 2025).

**Why it matters:** Synthetic data generation for geo-localization reduces the need for real flight data.

**Hackathon notes:** Code Apache-2.0; the HF dataset cards also say Apache-2.0, but the imagery is rendered from GTA V, so check the game's terms before non-research use. LR set 12.8 GB, HR 143.3 GB. Pretrained cross-area and same-area checkpoints on HF; fine-tune on your area's satellite tiles.

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `cross-view`, `synthetic`, `gta`, `aaai2025`

**Domains:** air

## Related

- alternative_to: [Sample4Geo](../../catalog/repos/skyy93__sample4geo.md)
- alternative_to: [University-1652 baseline](../../catalog/repos/layumi__university1652-baseline.md)

## Referenced by

- [Game4Loc: A UAV Geo-Localization Benchmark from Game Data](../../catalog/resources/game4loc-2024.md) (has_code)

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
