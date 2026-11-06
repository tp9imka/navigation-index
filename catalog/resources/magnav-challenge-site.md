# MagNav Challenge Problem (DAF-MIT AI Accelerator)

`res:magnav-challenge-site` - competition - <https://magnav.mit.edu/>

**By:** DAF-MIT AI Accelerator / AFRL, MIT, US Air Force - **Year:** 2021 - **Level:** intermediate - **Access:** open

Challenge site for airborne magnetic anomaly navigation: compensate the aircraft's own magnetic field out of magnetometer data so the remaining crustal anomaly can be map-matched for GPS-free navigation. Challenge is closed but data and code remain.

## Key takeaways

- Scored against a professionally compensated tail-stinger magnetometer
- Real flight data from survey aircraft
- Directly reusable as a hackathon benchmark
- Sensors: scalar and vector magnetometers, INS, GPS truth
- Domain: airborne
- Code: MagNav.jl
- Terms: Air Force data sharing agreement, non-profit research, education or US government use only, one-year licence

## Deep dives

- [afit-magnav-example-data](../../docs/dataset-cards/afit-magnav-example-data.md) (dataset-cards)
- [magnav-challenge-data](../../docs/dataset-cards/magnav-challenge-data.md) (dataset-cards)
- [programs-and-challenges](../../docs/landscape/programs-and-challenges.md) (landscape)

**Concepts:** [Magnetic anomaly navigation](../../catalog/concepts/magnetic-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `magnav`, `afrl`, `mit`, `airborne`, `challenge`

## Related

- has_code: [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md)
- part_of: [Signal Enhancement for Magnetic Navigation Challenge Problem](../../catalog/resources/afrl-magnav-challenge-2020.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Programs, challenges and hackathons (2023-2026)](../../docs/landscape/programs-and-challenges.md) (mentions)
- [Landscape: what judges already know](../../docs/landscape/README.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [9. Evaluation and datasets](../../docs/primer/09-evaluation-and-datasets.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Developing a Series of AI Challenges for the United States Department of the Air Force](../../catalog/resources/daf-ai-challenges-arxiv.md) (explains)
- [DAF-MIT AI Accelerator MagNav real-time C-17 demonstration (2023)](../../catalog/resources/daf-mit-magnav-c17-demo-2023.md) (cites)
- [Q-CTRL Ironstone Opal quantum-assured magnetic navigation](../../catalog/resources/qctrl-ironstone-opal.md) (cites)
- [SandboxAQ AQNav geomagnetic navigation](../../catalog/resources/sandboxaq-aqnav.md) (cites)

_Indexed by lane(s): docs-standards, sim-data_
