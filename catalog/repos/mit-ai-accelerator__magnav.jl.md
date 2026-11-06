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

**Concepts:** [Magnetic anomaly navigation](../concepts/magnetic-nav.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md)

**Tags:** `julia`, `magnav`, `afrl`, `tolles-lawson`, `mit`

**Domains:** air

## Related

- alternative_to: [MAMMAL](../repos/powerbroker2__mammal.md)
- alternative_to: [MagNavPy](../repos/manasp21__magnav.py.md)
- integrates_with: [AFIT MagNav example data](../repos/afit-eeng-magnav__example-data.md)
- extends: [MagNav challenge submission (lw-kong)](../repos/lw-kong__magnav.md)
- extends: [MagNav deep-learning compensation](../repos/naatyu__magnav.md)
- evaluated_on: [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/afrl-magnav-challenge-2020.md)

## Referenced by

- [AFIT MagNav example data](../repos/afit-eeng-magnav__example-data.md) (integrates_with)
- [DroneMagNav](../repos/ajisrawi__dronemagnav.md) (alternative_to)
- [MagNav challenge submission (lw-kong)](../repos/lw-kong__magnav.md) (depends_on)
- [MagNavPy](../repos/manasp21__magnav.py.md) (alternative_to)
- [MagNavPy](../repos/manasp21__magnav.py.md) (fork_of)
- [MagNav deep-learning compensation](../repos/naatyu__magnav.md) (extends)
- [MagNav deep-learning compensation](../repos/naatyu__magnav.md) (integrates_with)
- [MAMMAL](../repos/powerbroker2__mammal.md) (alternative_to)
- [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/afrl-magnav-challenge-2020.md) (has_code)
- [Developing a Series of AI Challenges for the United States Department of the Air Force](../resources/daf-ai-challenges-arxiv.md) (has_code)
- [DAF-MIT AI Accelerator MagNav real-time C-17 demonstration (2023)](../resources/daf-mit-magnav-c17-demo-2023.md) (has_code)
- [MagNav Challenge Problem (DAF-MIT AI Accelerator)](../resources/magnav-challenge-site.md) (has_code)
- [MagNav.jl documentation](../resources/magnav-jl-docs.md) (explains)
- [MagNav Challenge flight dataset (Zenodo)](../resources/magnav-zenodo-dataset.md) (has_code)
- [MagNav - MIT CSAIL open-source technologies](../resources/mit-cap-magnav-page.md) (explains)
- [Q-CTRL Ironstone Opal quantum-assured magnetic navigation](../resources/qctrl-ironstone-opal.md) (alternative_to)
- [SandboxAQ AQNav geomagnetic navigation](../resources/sandboxaq-aqnav.md) (alternative_to)
- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../samples/magnav-quickstart.md) (uses)

_Indexed by lane(s): alt-nav, defense-context, sim-data_

_GitHub metadata fetched 2026-11-06._
