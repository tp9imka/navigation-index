# ITU-T G.8275.2: Precision time protocol telecom profile for phase/time synchronization with partial timing support from the network

`res:itu-t-g8275-2-ptp-partial-support` - standard - <https://www.itu.int/rec/T-REC-G.8275.2>

**By:** ITU-T SG15 - **Year:** 2026 - **Level:** advanced - **Access:** open

Telecom PTP profile for networks where some nodes do not support PTP (partial timing support), carried over IPv4/IPv6 unicast. Intended for assisted partial timing support, e.g. a local GNSS receiver with PTP as backup during GNSS outage. In-force edition 02/2026 plus Amendment 1 (08/2026) per the ITU page.

## Key takeaways

- Unicast PTP over IP through non-PTP-aware routers: asymmetry and packet delay variation are not removed hop by hop
- The APTS case (GNSS primary, PTP as holdover aid) is the closest standard to a GNSS-denied timing fallback
- linuxptp ships configs/G.8275.2.cfg

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `itu-t`, `ptp`, `telecom-profile`, `partial-timing-support`, `apts`, `unicast`

## Related

- same_author: [ITU-T G.8275.1: Precision time protocol telecom profile for phase/time synchronization with full timing support from the network](../../catalog/resources/itu-t-g8275-1-ptp-full-support.md)
- part_of: [ITU-T G.8271: Time and phase synchronization aspects of telecommunication networks](../../catalog/resources/itu-t-g8271.md)
- has_code: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)
- explains: [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md)

_Indexed by lane(s): timing-network_
