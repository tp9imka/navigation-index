# MagNav challenge submission (lw-kong)

`repo:lw-kong/magnav` - <https://github.com/lw-kong/MagNav>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 23 | Julia | ? | 2022-07-26 | False | archived | medium |

A public submission repository for the JuliaCon 2020 MagNav signal-enhancement challenge, implementing a learned aircraft-field compensation.

**Why it matters:** One of the few open challenge entries - shows what a competing compensation pipeline looks like end to end.

**Build notes:** Inactive since 2022; useful as a template for a challenge-style submission on the MagNav data. Needs both Julia (Tolles-Lawson pre-filter) and MATLAB with the Deep Learning Toolbox (the learned filter in runs/main.m).

## Deep dives

- [magnav-challenge-data](../../docs/dataset-cards/magnav-challenge-data.md) (dataset-cards)
- [afrl-magnav-challenge-2020](../../docs/paper-digests/afrl-magnav-challenge-2020.md) (paper-digests)

**Concepts:** [Magnetic anomaly navigation](../../catalog/concepts/magnetic-nav.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `magnav-challenge`, `julia`, `machine-learning`

**Domains:** air

## Related

- depends_on: [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md)

## Referenced by

- [Competition playbook: navigation and PNT under GNSS denial](../../docs/competition-playbook.md) (mentions)
- [Dataset cards](../../docs/dataset-cards/README.md) (mentions)
- [The first three hours](../../docs/first-three-hours.md) (mentions)
- [Paper digests](../../docs/paper-digests/README.md) (mentions)
- [Brief decoder](../../docs/problem-statement-decoder.md) (mentions)
- [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md) (extends)
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../../catalog/resources/afrl-magnav-challenge-2020.md) (has_code)

_Indexed by lane(s): defense-context_

_GitHub metadata fetched 2026-11-09._
