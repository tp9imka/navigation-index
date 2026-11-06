# Attacking the Network Time Protocol

`res:malhotra-2016-attacking-ntp` - paper - <https://www.ndss-symposium.org/wp-content/uploads/2017/09/attacking-network-time-protocol.pdf>

**By:** A. Malhotra, I. E. Cohen, E. Brakke, S. Goldberg - **Year:** 2016 - **Level:** advanced - **Access:** open

NDSS 2016 paper showing on-path time shifting of NTP clients, an off-path single-packet denial of service against NTP synchronization, and related attacks that exploit unauthenticated NTP.

## Key takeaways

- Unauthenticated NTP can be shifted by an on-path attacker
- Some attacks work off-path

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Electronic warfare resilience](../concepts/ew-resilience.md)

**Tags:** `ntp`, `security`, `time-shifting`, `ndss`

## Related

- evaluates: [NTP reference implementation (ntpd)](../repos/ntp-project__ntp.md)

_Indexed by lane(s): timing_
