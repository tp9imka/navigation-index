# ITU-T G.8275.1: Precision time protocol telecom profile for phase/time synchronization with full timing support from the network

`res:itu-t-g8275-1-ptp-full-support` - standard - <https://www.itu.int/rec/T-REC-G.8275.1>

**By:** ITU-T SG15 - **Year:** 2026 - **Level:** advanced - **Access:** open

The telecom PTP profile for networks where every node is a boundary or transparent clock (full on-path support), using Ethernet transport. Current in-force edition per the ITU page is 02/2026 with Amendment 1 (08/2026); the first edition was 2014.

## Key takeaways

- The profile a 5G fronthaul / TDD backhaul uses to deliver phase from a PRTC
- Assumes every hop timestamps; pairs with G.8273.2 clock limits and the G.8271.1 network budget
- linuxptp ships configs/G.8275.1.cfg

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `itu-t`, `ptp`, `telecom-profile`, `full-timing-support`, `5g`

## Related

- part_of: [ITU-T G.8271: Time and phase synchronization aspects of telecommunication networks](../../catalog/resources/itu-t-g8271.md)
- uses: [ITU-T G.8273.2: Timing characteristics of telecom boundary clocks and telecom time synchronous clocks for use with full timing support from the network](../../catalog/resources/itu-t-g8273-2-tbc-tsc.md)
- uses: [IEEE 1588-2019: IEEE Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems](../../catalog/resources/ieee-1588-2019.md)
- has_code: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

## Referenced by

- [ITU-T G.8273.2: Timing characteristics of telecom boundary clocks and telecom time synchronous clocks for use with full timing support from the network](../../catalog/resources/itu-t-g8273-2-tbc-tsc.md) (part_of)
- [ITU-T G.8275.2: Precision time protocol telecom profile for phase/time synchronization with partial timing support from the network](../../catalog/resources/itu-t-g8275-2-ptp-partial-support.md) (same_author)

_Indexed by lane(s): timing-network_
