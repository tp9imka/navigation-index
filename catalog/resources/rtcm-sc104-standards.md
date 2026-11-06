# RTCM 10403.x Differential GNSS (DGNSS) Services - Version 3

`res:rtcm-sc104-standards` - standard - <https://www.rtcm.org/>

**By:** RTCM Special Committee 104 - **Year:** 2023 - **Level:** advanced - **Access:** paywalled

The paid-access RTCM v3 standard that defines the binary messages used to stream GNSS corrections and observations (legacy RTK 1001-1012, MSM 1-7 per constellation, ephemerides, SSR). Practically every NTRIP caster and RTK base station speaks it.

## Key takeaways

- MSM messages replaced legacy observation messages and align with RINEX 3
- MSM4/MSM7 are the common choices for RTK
- Standard itself is purchased; open parsers document much of it

**Concepts:** [RTK / PPP precise positioning](../concepts/gnss-rtk-ppp.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `rtcm3`, `msm`, `ntrip`, `rtk`

## Related

- has_code: [RTKLIB](../repos/tomojitakasu__rtklib.md)
- has_code: [RTKLIB demo5 (rtklibexplorer)](../repos/rtklibexplorer__rtklib.md)
- has_code: [pyrtcm](../repos/semuconsulting__pyrtcm.md)

## Referenced by

- [Navipedia: RTK Standards](../resources/navipedia-rtk-standards.md) (explains)

_Indexed by lane(s): docs-standards_
