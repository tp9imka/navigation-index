# GNSS Timing Spoofing Detection: Methods and Analysis using Jammertest data

`res:safi-2025-timing-spoofing-jammertest-thesis` - report - <https://osuva.uwasa.fi/handle/10024/19442>

**By:** Muhammad Safi - **Year:** 2025 - **Level:** intermediate - **Access:** open

University of Vaasa master's thesis (supervised by Heidi Kuusniemi) analysing u-blox ZED-F9P data from a Jammertest 2024 timing-spoofing event. C/N0 monitoring was ineffective; pseudorange RMS and NMEA validity flags caught anomalies with false positives; an Isolation Forest model detected the spoofing with very few false alarms. Recommends validity flags as a trigger plus ML verification. The repository page sits behind a bot check.

## Key takeaways

- Uses real live-spoofing data, not simulation
- C/N0 alone does not reveal timing spoofing
- Cheap receiver-side detection recipe

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `timing-spoofing`, `jammertest`, `isolation-forest`, `u-blox`, `thesis`

## Related

- same_author: [Empirical Evaluation of GNSS Timing Spoofing and Detection Using Machine Learning](../../catalog/resources/safi-2025-ipin-timing-spoofing-ml.md)
- uses: [Jammertest - open GNSS jamming and spoofing test event (Andoya, Norway)](../../catalog/resources/jammertest-norway.md)

## Referenced by

- [Empirical Evaluation of GNSS Timing Spoofing and Detection Using Machine Learning](../../catalog/resources/safi-2025-ipin-timing-spoofing-ml.md) (same_author)
- [Real attack replay: Jammertest 2024 u-blox logs through the GNSS interference monitor, with RTKLIB SPP](../../catalog/samples/real-attack-replay.md) (explains)

_Indexed by lane(s): backlog_
