# MagNav.jl

`repo:mit-ai-accelerator/magnav.jl` - <https://github.com/MIT-AI-Accelerator/MagNav.jl>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 184 | Julia | NOASSERTION | 2026-11-02 | False | active-research | high |

Julia package from the DAF-MIT AI Accelerator for airborne magnetic anomaly navigation: flight/INS data import or simulation, anomaly maps, aircraft magnetic compensation (Tolles-Lawson and neural models) and navigation filters.

**Why it matters:** Official code behind the AFRL/MIT MagNav challenge; magnetic navigation is a leading GNSS-independent, unjammable PNT approach in DIU and AFRL programs.

**Hackathon notes:** Install Julia, Pkg.add("MagNav") and run the documented examples on the challenge flight data; compensation + EKF in a day. The DAF-MIT project has concluded and the package now gets maintenance-only changes, so do not expect fixes for new issues.

## Deep dives

- [_index-perception-altnav](../../docs/integration-cards/_index-perception-altnav.md) (integration-cards)
- [mit-ai-accelerator__magnav.jl](../../docs/integration-cards/mit-ai-accelerator__magnav.jl.md) (integration-cards)
- [afit-magnav-example-data](../../docs/dataset-cards/afit-magnav-example-data.md) (dataset-cards)
- [magnav-challenge-data](../../docs/dataset-cards/magnav-challenge-data.md) (dataset-cards)
- [afrl-magnav-challenge-2020](../../docs/paper-digests/afrl-magnav-challenge-2020.md) (paper-digests)

**Concepts:** [Magnetic anomaly navigation](../../catalog/concepts/magnetic-nav.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `julia`, `magnav`, `afrl`, `tolles-lawson`, `mit`

**Domains:** air

## Related

- alternative_to: [MAMMAL](../../catalog/repos/powerbroker2__mammal.md)
- alternative_to: [MagNavPy](../../catalog/repos/manasp21__magnav.py.md)
- integrates_with: [AFIT MagNav example data](../../catalog/repos/afit-eeng-magnav__example-data.md)
- extends: [MagNav challenge submission (lw-kong)](../../catalog/repos/lw-kong__magnav.md)
- extends: [MagNav deep-learning compensation](../../catalog/repos/naatyu__magnav.md)
- evaluated_on: [Signal Enhancement for Magnetic Navigation Challenge Problem](../../catalog/resources/afrl-magnav-challenge-2020.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)
- [AFIT MagNav example data](../../catalog/repos/afit-eeng-magnav__example-data.md) (integrates_with)
- [DroneMagNav](../../catalog/repos/ajisrawi__dronemagnav.md) (alternative_to)
- [MagNav challenge submission (lw-kong)](../../catalog/repos/lw-kong__magnav.md) (depends_on)
- [MagNavPy](../../catalog/repos/manasp21__magnav.py.md) (alternative_to)
- [MagNavPy](../../catalog/repos/manasp21__magnav.py.md) (fork_of)
- [MagNav deep-learning compensation](../../catalog/repos/naatyu__magnav.md) (extends)
- [MagNav deep-learning compensation](../../catalog/repos/naatyu__magnav.md) (integrates_with)
- [MAMMAL](../../catalog/repos/powerbroker2__mammal.md) (alternative_to)
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../../catalog/resources/afrl-magnav-challenge-2020.md) (has_code)
- [Developing a Series of AI Challenges for the United States Department of the Air Force](../../catalog/resources/daf-ai-challenges-arxiv.md) (has_code)
- [DAF-MIT AI Accelerator MagNav real-time C-17 demonstration (2023)](../../catalog/resources/daf-mit-magnav-c17-demo-2023.md) (has_code)
- [Advanced Aeromagnetic Compensation Models for Airborne Magnetic Anomaly Navigation](../../catalog/resources/gnadt-2022-mit-phd-aeromagnetic-compensation.md) (has_code)
- [Derivation and Extensions of the Tolles-Lawson Model for Aeromagnetic Compensation](../../catalog/resources/gnadt-2022-tolles-lawson-derivation.md) (has_code)
- [MagNav Challenge Problem (DAF-MIT AI Accelerator)](../../catalog/resources/magnav-challenge-site.md) (has_code)
- [MagNav.jl documentation](../../catalog/resources/magnav-jl-docs.md) (explains)
- [MagNav Challenge flight dataset (Zenodo)](../../catalog/resources/magnav-zenodo-dataset.md) (has_code)
- [MagNav - MIT CSAIL open-source technologies](../../catalog/resources/mit-cap-magnav-page.md) (explains)
- [Q-CTRL Ironstone Opal quantum-assured magnetic navigation](../../catalog/resources/qctrl-ironstone-opal.md) (alternative_to)
- [SandboxAQ AQNav geomagnetic navigation](../../catalog/resources/sandboxaq-aqnav.md) (alternative_to)
- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../../catalog/samples/magnav-quickstart.md) (uses)

_Indexed by lane(s): alt-nav, defense-context, sim-data_

_GitHub metadata fetched 2026-11-06._
