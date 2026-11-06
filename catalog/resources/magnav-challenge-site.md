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

## Deep dives

- [afit-magnav-example-data](../../docs/dataset-cards/afit-magnav-example-data.md) (dataset-cards)
- [magnav-challenge-data](../../docs/dataset-cards/magnav-challenge-data.md) (dataset-cards)
- [programs-and-challenges](../../docs/landscape/programs-and-challenges.md) (landscape)

**Concepts:** [Magnetic anomaly navigation](../concepts/magnetic-nav.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md)

**Tags:** `magnav`, `afrl`, `mit`, `airborne`, `challenge`

## Related

- has_code: [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md)
- part_of: [Signal Enhancement for Magnetic Navigation Challenge Problem](../resources/afrl-magnav-challenge-2020.md)

## Referenced by

- [Developing a Series of AI Challenges for the United States Department of the Air Force](../resources/daf-ai-challenges-arxiv.md) (explains)
- [DAF-MIT AI Accelerator MagNav real-time C-17 demonstration (2023)](../resources/daf-mit-magnav-c17-demo-2023.md) (cites)
- [Q-CTRL Ironstone Opal quantum-assured magnetic navigation](../resources/qctrl-ironstone-opal.md) (cites)
- [SandboxAQ AQNav geomagnetic navigation](../resources/sandboxaq-aqnav.md) (cites)

_Indexed by lane(s): docs-standards, sim-data_
