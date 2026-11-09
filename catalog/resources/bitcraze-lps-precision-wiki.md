# Loco Positioning System precision investigation

`res:bitcraze-lps-precision-wiki` - doc - <https://wiki.bitcraze.io/misc:investigations:lps-precision>

**By:** Bitcraze - **Year:** 2017 - **Level:** intermediate - **Access:** open

Archived Bitcraze wiki page with static TWR measurements of the UWB Loco system using six anchors: per-axis jitter about 0.5-2 cm, one 3D point with about 0.24 m average error, raw ranges biased short by 0.2-0.4 m (antenna delay). The author says the numbers are not a specification.

## Key takeaways

- UWB jitter is cm, bias is dm: calibrate antenna delay and anchor positions
- Z is the weakest axis with anchors near one height

**Concepts:** [RF localization and direction finding](../../catalog/concepts/rf-localization.md)

**Tags:** `uwb`, `loco`, `twr`, `crazyflie`, `archived`

## Related

- part_of: [Loco Positioning System documentation](../../catalog/resources/bitcraze-loco-positioning.md)

## Referenced by

- [Day-1 intake: close-area A=>B, organiser answers => stack](../../docs/day1-close-area-intake.md) (mentions)

_Indexed by lane(s): close-area-localization_
