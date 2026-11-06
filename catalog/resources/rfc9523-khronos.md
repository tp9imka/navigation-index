# RFC 9523: A Secure Selection and Filtering Mechanism for the Network Time Protocol with Khronos

`res:rfc9523-khronos` - standard - <https://www.rfc-editor.org/rfc/rfc9523>

**By:** N. Rozen-Schiff, D. Dolev, T. Mizrahi, M. Schapira - **Year:** 2024 - **Level:** advanced - **Access:** open

Informational RFC describing Khronos: an NTP client watchdog that samples many servers and uses trimming to bound how far a man-in-the-middle controlling some of them can shift time.

## Key takeaways

- Sample many servers, trim outliers, bound the shift
- Grew out of the Chronos NDSS 2018 work

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `ntp`, `khronos`, `rfc`, `time-shifting`

## Related

- cites: [Preventing (Network) Time Travel with Chronos](../../catalog/resources/deutsch-2018-chronos-ndss.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)
- [Preventing (Network) Time Travel with Chronos](../../catalog/resources/deutsch-2018-chronos-ndss.md) (same_author)

_Indexed by lane(s): timing_
