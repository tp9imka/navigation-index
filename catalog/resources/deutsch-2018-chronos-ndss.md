# Preventing (Network) Time Travel with Chronos

`res:deutsch-2018-chronos-ndss` - paper - <https://www.ndss-symposium.org/wp-content/uploads/2018/02/ndss2018_02A-2_Deutsch_paper.pdf>

**By:** O. Deutsch, N. Rozen Schiff, D. Dolev, M. Schapira - **Year:** 2018 - **Level:** advanced - **Access:** open

NDSS 2018 paper proposing Chronos, an NTP client that queries many servers and discards outliers to bound time-shifting by a man in the middle; basis of the later Khronos RFC.

## Key takeaways

- Many servers plus trimming bounds an attacker's shift

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `ntp`, `chronos`, `time-shifting`, `ndss`

## Related

- same_author: [RFC 9523: A Secure Selection and Filtering Mechanism for the Network Time Protocol with Khronos](../../catalog/resources/rfc9523-khronos.md)

## Referenced by

- [RFC 9523: A Secure Selection and Filtering Mechanism for the Network Time Protocol with Khronos](../../catalog/resources/rfc9523-khronos.md) (cites)

_Indexed by lane(s): timing_
