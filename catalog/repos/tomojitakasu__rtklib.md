# RTKLIB

`repo:tomojitakasu/rtklib` - <https://github.com/tomojitakasu/RTKLIB>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 3,165 | C | ? | 2024-05-28 | False | production | high |

The original open-source GNSS positioning package by T. Takasu: SPP, DGNSS, RTK, PPK and PPP engines in portable C, plus CLI tools (rnx2rtkp, rtkrcv, str2str, convbin) and Windows GUIs.

**Why it matters:** The reference implementation most GNSS research and low-cost RTK work is built on; reading its rtkpos.c is the fastest way to understand RTK.

**Hackathon notes:** Use str2str to relay NTRIP/serial streams and rnx2rtkp for post-processing. Upstream is quiet since 2024; prefer the demo5 fork for current receivers.

**Concepts:** [GNSS positioning](../concepts/gnss.md), [RTK / PPP precise positioning](../concepts/gnss-rtk-ppp.md)

**Tags:** `rtk`, `ppk`, `ppp`, `rinex`, `rtcm`, `c`

**Domains:** multi

## Related

- alternative_to: [RTKLIB demo5 (rtklibexplorer)](../repos/rtklibexplorer__rtklib.md)
- alternative_to: [rtklib-py](../repos/rtklibexplorer__rtklib-py.md)

## Referenced by

- [GICI-LIB](../repos/chichengcn__gici-open.md) (extends)
- [ntripcaster (BKG standard caster)](../repos/nunojpg__ntripcaster.md) (integrates_with)
- [RTKLIB demo5 (rtklibexplorer)](../repos/rtklibexplorer__rtklib.md) (fork_of)
- [MatRTKLIB](../repos/taroz__matrtklib.md) (depends_on)
- [PocketSDR](../repos/tomojitakasu__pocketsdr.md) (same_org)
- [GraphGNSSLib](../repos/weisongwen__graphgnsslib.md) (depends_on)
- [BeiDou Navigation Satellite System Signal-In-Space ICDs (B1I, B3I, B1C, B2a, B2b)](../resources/beidou-icd-library.md) (has_code)
- [GNSS Data Processing, Vol. I: Fundamentals and Algorithms (ESA TM-23)](../resources/esa-gnss-data-processing-vol1.md) (has_code)
- [GNSS Data Processing, Vol. II: Laboratory Exercises (ESA TM-23)](../resources/esa-gnss-data-processing-vol2.md) (has_code)
- [Galileo High Accuracy Service Signal-In-Space ICD (HAS SIS ICD) Issue 1.0](../resources/galileo-has-sis-icd.md) (has_code)
- [Galileo Open Service Signal-In-Space Interface Control Document (OS SIS ICD) Issue 2.1](../resources/galileo-os-sis-icd-2-1.md) (has_code)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../resources/gps-is-gps-200n.md) (has_code)
- [SDR приемник GPS на микроконтроллере](../resources/habr-mcu-gps-sdr-2024.md) (uses)
- [RTKLib - Сантиметровая точность GPS/ГЛОНАСС в пост-обработке](../resources/habr-rtklib-postprocessing-2014.md) (uses)
- [Real-World Spoofing Detection (ION ITM 2025)](../resources/kreizis-ion-itm-2025-spoofing.md) (has_code)
- [Navipedia: RTK Standards](../resources/navipedia-rtk-standards.md) (has_code)
- [QZSS Performance Standards and Interface Specifications (IS-QZSS)](../resources/qzss-is-qzss.md) (has_code)
- [RTCM 10403.x Differential GNSS (DGNSS) Services - Version 3](../resources/rtcm-sc104-standards.md) (has_code)
- [rtklibexplorer blog](../resources/rtklibexplorer-blog.md) (uses)
- [Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py](../samples/gnss-rinex-processing.md) (explains)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
