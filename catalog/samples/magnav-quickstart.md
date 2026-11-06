# Sample: MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight

`sample:magnav-quickstart` - code and walkthrough in [samples/magnav-quickstart](../../samples/magnav-quickstart/)

A Julia walkthrough with MagNav.jl that downloads the public SGL 2020 challenge flight and Ottawa anomaly maps, compensates the scalar magnetometer with Tolles-Lawson on a calibration box, and runs the MagNav EKF against the map, printing INS-only vs EKF error and the CRLB. The README explains why magnetic anomaly navigation resists jamming and spoofing, and where it breaks down (map coverage, altitude, aircraft noise, temporal variation).

**Verification:** Ran on 2026-11-06 in the julia:1.11 Docker image (Julia 1.11.9, linux/arm64) with MagNav.jl v1.3.5, CSV v1.3.0, DataFrames v1.8.2 and FFTA pinned to 0.2.1 (FFTA 0.3.2 breaks precompilation of GlobalSensitivity): EKF DRMS 31.2 m vs INS-only final error 218.8 m on line 1006.08 with map Eastern_395. Output in README. Artifacts downloaded: sgl_2020_train ~563 MB and ottawa_area_maps ~1.2 GB on disk, plus EMAG2 ~0.5 GB pulled during precompile.

## Deep dives

- [magnav-challenge-data](../../docs/dataset-cards/magnav-challenge-data.md) (dataset-cards)

**Concepts:** [Magnetic anomaly navigation](../../catalog/concepts/magnetic-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Sensor calibration](../../catalog/concepts/calibration.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `magnav`, `julia`, `tolles-lawson`, `ekf`, `anomaly-map`, `afrl`, `gnss-denied`, `airborne`

## Related

- uses: [MagNav.jl](../../catalog/repos/mit-ai-accelerator__magnav.jl.md)
- explains: [MagNavPy](../../catalog/repos/manasp21__magnav.py.md)
- explains: [MagNav deep-learning compensation](../../catalog/repos/naatyu__magnav.md)
- explains: [AFIT MagNav example data](../../catalog/repos/afit-eeng-magnav__example-data.md)
- explains: [DroneMagNav](../../catalog/repos/ajisrawi__dronemagnav.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): samples_
