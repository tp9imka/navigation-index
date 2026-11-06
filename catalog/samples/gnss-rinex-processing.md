# Sample: Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py

`sample:gnss-rinex-processing` - code and walkthrough in [samples/gnss-rinex-processing](../../samples/gnss-rinex-processing/)

Downloads one day of public NOAA NGS CORS RINEX for a rover/base pair 30 km apart, runs RTKLIB demo5 rnx2rtkp in single-point and kinematic RTK modes with exact CLI flags, and scores both against the stations' published ITRF2020 coordinates (propagated for plate motion) in ENU. An optional gnss_lib_py weighted-least-squares SPP covers the same data in Python, after converting RINEX 2.11 to 3.

**Verification:** unverified sketch: syntax-checked only (bash -n, py_compile); requires RTKLIB demo5 rnx2rtkp/convbin, crx2rnx, and gnss-lib-py. rnx2rtkp/convbin flags were checked against demo5 v2.5.1 source help text and gnss_lib_py calls against v1.1.0 source on 2026-11-06. The stdlib scorer compare_pos.py and its 4 unit tests ran with python3.14.7 on 2026-11-06, and its coordinate parser ran on the real downloaded NGS sheets; the data URLs returned HTTP 200 and the P730 RINEX header was inspected. No RTKLIB or gnss_lib_py solution was computed.

**Concepts:** [GNSS positioning](../concepts/gnss.md), [RTK / PPP precise positioning](../concepts/gnss-rtk-ppp.md), [Geodesy and coordinate frames](../concepts/geodesy.md), [Datasets and benchmarks](../concepts/datasets-benchmarks.md)

**Tags:** `rinex`, `rtklib`, `demo5`, `rnx2rtkp`, `convbin`, `spp`, `rtk`, `cors`, `ngs`, `gnss_lib_py`, `georinex`, `hatanaka`

## Related

- uses: [RTKLIB demo5 (rtklibexplorer)](../repos/rtklibexplorer__rtklib.md)
- explains: [RTKLIB](../repos/tomojitakasu__rtklib.md)
- uses: [gnss_lib_py](../repos/stanford-navlab__gnss_lib_py.md)
- uses: [georinex](../repos/geospace-code__georinex.md)

_Indexed by lane(s): samples_
