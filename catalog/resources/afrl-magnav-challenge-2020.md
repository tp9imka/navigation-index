# Signal Enhancement for Magnetic Navigation Challenge Problem

`res:afrl-magnav-challenge-2020` - paper - <https://arxiv.org/abs/2007.12158>

**By:** Albert R. Gnadt, Joseph Belarge, Aaron Canciani et al., et al. (MIT / USAF AI Accelerator), Gnadt, Belarge, et al. - **Year:** 2020 - **Level:** intermediate - **Access:** open

Defines the AFRL/MIT MagNav challenge: remove the aircraft's own magnetic field from airborne magnetometer data so the Earth's anomaly field can be used for navigation, with released flight data and a scientific-ML baseline.

## Key takeaways

- Aircraft magnetic compensation is the core difficulty
- Provides real survey-flight data and a baseline
- Problem is compensation, the hard step before map matching
- Physics (Tolles-Lawson) plus ML beat either alone
- Data and baseline code are open
- Tolles-Lawson is the classical baseline to beat
- Scalar magnetometer mixes Earth core, crustal anomaly and aircraft fields
- Dataset released on Zenodo

## Deep dives

- [magnav-challenge-data](../../docs/dataset-cards/magnav-challenge-data.md) (dataset-cards)
- [afrl-magnav-challenge-2020](../../docs/paper-digests/afrl-magnav-challenge-2020.md) (paper-digests)

**Concepts:** [Magnetic anomaly navigation](../../catalog/concepts/magnetic-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `arxiv`, `afrl`, `mit`, `challenge`, `magnav`, `tolles-lawson`, `ml`

## Related

- has_code: [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md)
- has_code: [MagNav challenge submission (lw-kong)](../../catalog/repos/lw-kong__magnav.md)
- dataset_for: [DAF-MIT AIA Open Flight Data for Magnetic Navigation Research](../../catalog/resources/magnav-sgs-flight-data.md)
- uses: [MagNav Challenge flight dataset (Zenodo)](../../catalog/resources/magnav-zenodo-dataset.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md) (evaluated_on)
- [Absolute Positioning Using the Earth's Magnetic Anomaly Field](../../catalog/resources/canciani-afit-magnetic-anomaly-dissertation-2016.md) (same_author)
- [DIU launches new emerging tech portfolio, solicits industry for quantum sensing capabilities](../../catalog/resources/diu-transition-quantum-sensing-2024.md) (cites)
- [Advanced Aeromagnetic Compensation Models for Airborne Magnetic Anomaly Navigation](../../catalog/resources/gnadt-2022-mit-phd-aeromagnetic-compensation.md) (same_author)
- [MagNav Challenge Problem (DAF-MIT AI Accelerator)](../../catalog/resources/magnav-challenge-site.md) (part_of)
- [DAF-MIT AIA Open Flight Data for Magnetic Navigation Research](../../catalog/resources/magnav-sgs-flight-data.md) (dataset_for)
- [MagNav Challenge flight dataset (Zenodo)](../../catalog/resources/magnav-zenodo-dataset.md) (dataset_for)

_Indexed by lane(s): alt-nav, defense-context, docs-standards_
