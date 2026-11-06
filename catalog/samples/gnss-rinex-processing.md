# Sample: Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py

`sample:gnss-rinex-processing` - code and walkthrough in [samples/gnss-rinex-processing](../../samples/gnss-rinex-processing/)

Downloads one day of public NOAA NGS CORS RINEX for a rover/base pair 30 km apart, runs RTKLIB demo5 rnx2rtkp in single-point and kinematic RTK modes with exact CLI flags, and scores both against the stations' published ITRF2020 coordinates (propagated for plate motion) in ENU. An optional gnss_lib_py weighted-least-squares SPP covers the same data in Python, after converting RINEX 2.11 to 3.

**Verification:** ran on 2026-11-06 on real NOAA NGS CORS data (P730 rover, P731 base, 2024-04-09 12:00-14:00 GPST, GPS only, 241 epochs): RTKLIB demo5 v2.5.1 built in Docker (docker/Dockerfile) gave SPP E/N/U rms 0.62/1.24/1.02 m and RTK 0.084/0.055/0.071 m with 97% fix, scored by compare_pos.py against the propagated ITRF2020 sheet; gnss_lib_py 1.1.0 WLS (glp_spp.py, after fixing a GPST-vs-UTC epoch tag, per-chunk ephemeris selection and transmit-time SV states) gave 0.65/1.28/1.10 m. compare_pos.py's 4 unit tests ran with python3.14.7. Not verified: other days/stations, multi-GNSS, PPP, antenna phase-centre models, a native (non-Docker) RTKLIB build.

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md), [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `rinex`, `rtklib`, `demo5`, `rnx2rtkp`, `convbin`, `spp`, `rtk`, `cors`, `ngs`, `gnss_lib_py`, `georinex`, `hatanaka`

## Related

- uses: [RTKLIB demo5 (rtklibexplorer)](../../catalog/repos/rtklibexplorer__rtklib.md)
- explains: [RTKLIB](../../catalog/repos/tomojitakasu__rtklib.md)
- uses: [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md)
- uses: [georinex](../../catalog/repos/geospace-code__georinex.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [NOAA NGS CORS network RINEX data archive](../../catalog/resources/noaa-ngs-cors-rinex.md) (dataset_for)
- [Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP](../../catalog/samples/real-attack-replay.md) (uses)

_Indexed by lane(s): samples_
