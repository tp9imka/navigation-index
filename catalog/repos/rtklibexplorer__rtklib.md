# RTKLIB demo5 (rtklibexplorer)

`repo:rtklibexplorer/rtklib` - <https://github.com/rtklibexplorer/RTKLIB>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 992 | C | NOASSERTION | 2026-11-05 | False | production | high |

Actively maintained RTKLIB fork tuned for low-cost receivers (especially u-blox), with many robustness fixes to ambiguity resolution, cycle-slip handling and receiver decoders.

**Why it matters:** The practical default for RTK/PPK with cheap F9P-class hardware; well documented through the rtklibexplorer blog.

**Hackathon notes:** Prebuilt Windows binaries and Linux builds are easy. Pair with a u-blox F9P and a free NTRIP caster for cm-level fixes in an afternoon.

## Deep dives

- [_index-gnss-fusion-gis](../../docs/integration-cards/_index-gnss-fusion-gis.md) (integration-cards)
- [rtklibexplorer__rtklib](../../docs/integration-cards/rtklibexplorer__rtklib.md) (integration-cards)

**Concepts:** [GNSS positioning](../concepts/gnss.md), [RTK / PPP precise positioning](../concepts/gnss-rtk-ppp.md)

**Tags:** `rtk`, `ppk`, `demo5`, `u-blox`, `rtklib-fork`

**Domains:** multi

## Related

- fork_of: [RTKLIB](../repos/tomojitakasu__rtklib.md)
- same_org: [rtklib-py](../repos/rtklibexplorer__rtklib-py.md)

## Referenced by

- [rtklib-py](../repos/rtklibexplorer__rtklib-py.md) (extends)
- [RTKLIB](../repos/tomojitakasu__rtklib.md) (alternative_to)
- [BeiDou Navigation Satellite System Signal-In-Space ICDs (B1I, B3I, B1C, B2a, B2b)](../resources/beidou-icd-library.md) (has_code)
- [GNSS Data Processing, Vol. I: Fundamentals and Algorithms (ESA TM-23)](../resources/esa-gnss-data-processing-vol1.md) (has_code)
- [GNSS Data Processing, Vol. II: Laboratory Exercises (ESA TM-23)](../resources/esa-gnss-data-processing-vol2.md) (has_code)
- [Galileo High Accuracy Service Signal-In-Space ICD (HAS SIS ICD) Issue 1.0](../resources/galileo-has-sis-icd.md) (has_code)
- [Galileo Open Service Signal-In-Space Interface Control Document (OS SIS ICD) Issue 2.1](../resources/galileo-os-sis-icd-2-1.md) (has_code)
- [IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces](../resources/gps-is-gps-200n.md) (has_code)
- [Real-World Spoofing Detection (ION ITM 2025)](../resources/kreizis-ion-itm-2025-spoofing.md) (has_code)
- [Navipedia: RTK Standards](../resources/navipedia-rtk-standards.md) (has_code)
- [QZSS Performance Standards and Interface Specifications (IS-QZSS)](../resources/qzss-is-qzss.md) (has_code)
- [RTCM 10403.x Differential GNSS (DGNSS) Services - Version 3](../resources/rtcm-sc104-standards.md) (has_code)
- [rtklibexplorer blog](../resources/rtklibexplorer-blog.md) (explains)
- [rtklibexplorer blog](../resources/rtklibexplorer-blog.md) (has_code)
- [Public CORS RINEX to SPP vs RTK with RTKLIB demo5 and gnss_lib_py](../samples/gnss-rinex-processing.md) (uses)
- [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../samples/gnss-signal-chain.md) (uses)

_Indexed by lane(s): gnss_

_GitHub metadata fetched 2026-11-06._
