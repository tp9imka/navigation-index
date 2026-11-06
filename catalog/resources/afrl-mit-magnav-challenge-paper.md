# Signal Enhancement for Magnetic Navigation Challenge Problem

`res:afrl-mit-magnav-challenge-paper` - paper - <https://arxiv.org/abs/2007.12158>

**By:** Albert R. Gnadt, et al. (MIT / USAF AI Accelerator) - **Year:** 2020 - **Level:** advanced - **Access:** open

Defines the AFRL/MIT MagNav challenge: remove the aircraft's own magnetic field from airborne magnetometer data so the Earth's anomaly field can be used for navigation, with released flight data and a scientific-ML baseline.

## Key takeaways

- Problem is compensation, the hard step before map matching
- Physics (Tolles-Lawson) plus ML beat either alone
- Data and baseline code are open

**Concepts:** [Magnetic anomaly navigation](../concepts/magnetic-nav.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md)

**Tags:** `afrl`, `mit`, `magnav`, `challenge`

## Related

- has_code: [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md)
- has_code: [MagNav challenge submission (lw-kong)](../repos/lw-kong__magnav.md)
- dataset_for: [MagNav challenge flight data (Sander Geophysics, Zenodo)](../resources/magnav-sgs-flight-data.md)

## Referenced by

- [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md) (evaluated_on)
- [DIU solicitation: Transition of Quantum Sensing for navigation](../resources/diu-transition-quantum-sensing-2024.md) (cites)
- [MagNav challenge flight data (Sander Geophysics, Zenodo)](../resources/magnav-sgs-flight-data.md) (dataset_for)

_Indexed by lane(s): defense-context_
