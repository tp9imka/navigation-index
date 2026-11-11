# Lighthouse Positioning System: Dataset, Accuracy, and Precision for UAV Research

`res:taffanel-2021-lighthouse-positioning-accuracy` - paper - <https://arxiv.org/abs/2104.11523>

**By:** Arnaud Taffanel, Barbara Rousselot, Jonas Danielsson, Kimberly McGuire, Kristoffer Richardsson, Marcus Eliasson, Tobias Antonsson, Wolfgang Honig - **Year:** 2021 - **Level:** intermediate - **Access:** open

Workshop paper (ICRA 2021 Robot Swarms in the Real World). Measures the Crazyflie Lighthouse system against Qualisys mocap. Mean and median error about 2-4 cm, flight outliers about 5 cm, stationary jitter 0.3-3.9 mm depending on base-station version and method. Crossing-beam needs two base stations in view; the EKF works with one.

## Key takeaways

- Real accuracy is cm-level, the docs say 'mm'
- Needs line of sight; glass and mirrors break it
- About an order of magnitude cheaper than mocap

**Concepts:** [RF localization and direction finding](../../catalog/concepts/rf-localization.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `lighthouse`, `crazyflie`, `indoor`, `accuracy`, `workshop`

## Related

- has_code: [Bitcraze positioning_dataset](../../catalog/repos/bitcraze__positioning_dataset.md)
- evaluates: [Crazyflie firmware](../../catalog/repos/bitcraze__crazyflie-firmware.md)

## Referenced by

- [First-day intake: close-area A=>B, answers => stack](../../docs/first-day-intake.md) (mentions)
- [Positioning Systems Overview](../../catalog/resources/bitcraze-positioning-systems-overview.md) (cites)

_Indexed by lane(s): close-area-localization_
