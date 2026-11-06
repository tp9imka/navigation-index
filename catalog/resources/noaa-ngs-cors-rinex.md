# NOAA NGS CORS network RINEX data archive

`res:noaa-ngs-cors-rinex` - dataset - <https://geodesy.noaa.gov/corsdata/>

**By:** NOAA National Geodetic Survey - **Year:** ? - **Level:** intermediate - **Access:** open

Public archive of RINEX observation and navigation files from the US Continuously Operating Reference Station network, organised by year and day of year. Station coordinates are precisely known and fixed, so any positioning error computed from these files is solution error, which makes them a clean test input for SPP, PPP and RTK pipelines. US government data, no login.

## Key takeaways

- Fixed, surveyed antennas give free truth for positioning-algorithm benchmarks
- Files are daily 30 s RINEX, often Hatanaka-compressed; pair with broadcast or precise orbits
- Pairs of nearby stations give a ready-made baseline for RTK tests

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [GNSS positioning](../../catalog/concepts/gnss.md), [RTK / PPP precise positioning](../../catalog/concepts/gnss-rtk-ppp.md), [Geodesy and coordinate frames](../../catalog/concepts/geodesy.md)

**Tags:** `cors`, `rinex`, `noaa`, `reference-stations`, `rtk`, `ppp`

## Related

- dataset_for: [Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py](../../catalog/samples/gnss-rinex-processing.md)
- has_code: [RTKLIB demo5 (rtklibexplorer)](../../catalog/repos/rtklibexplorer__rtklib.md)
- has_code: [georinex](../../catalog/repos/geospace-code__georinex.md)

_Indexed by lane(s): datasets-used_
