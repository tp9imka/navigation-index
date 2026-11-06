# Sample: MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight

`sample:magnav-quickstart` - code and walkthrough in [samples/magnav-quickstart](../../samples/magnav-quickstart/)

A Julia walkthrough with MagNav.jl that downloads the public SGL 2020 challenge flight and Ottawa anomaly maps, compensates the scalar magnetometer with Tolles-Lawson on a calibration box, and runs the MagNav EKF against the map, printing INS-only vs EKF error and the CRLB. The README explains why magnetic anomaly navigation resists jamming and spoofing, and where it breaks down (map coverage, altitude, aircraft noise, temporal variation).

**Verification:** unverified sketch: never run, Julia not installed; function names and signatures checked against MagNav.jl v1.3.5 examples and src on 2026-11-06; requires Julia 1.10+, MagNav.jl, CSV.jl, DataFrames.jl and the package's data artifacts.

**Concepts:** [Magnetic anomaly navigation](../concepts/magnetic-nav.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Inertial navigation (INS/IMU)](../concepts/ins.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Sensor calibration](../concepts/calibration.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md)

**Tags:** `magnav`, `julia`, `tolles-lawson`, `ekf`, `anomaly-map`, `afrl`, `gnss-denied`, `airborne`

## Related

- uses: [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md)
- explains: [MagNavPy](../repos/manasp21__magnav.py.md)
- explains: [MagNav deep-learning compensation](../repos/naatyu__magnav.md)
- explains: [AFIT MagNav example data](../repos/afit-eeng-magnav__example-data.md)
- explains: [DroneMagNav](../repos/ajisrawi__dronemagnav.md)

_Indexed by lane(s): samples_
