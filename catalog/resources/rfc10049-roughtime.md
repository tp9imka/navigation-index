# RFC 10049: Roughtime: A Protocol for Rough Time Synchronization

`res:rfc10049-roughtime` - standard - <https://www.rfc-editor.org/info/rfc10049>

**By:** IETF NTP WG - **Year:** 2026 - **Level:** intermediate - **Access:** open

The published RFC version of Roughtime: signed, rough (seconds-level) time from several servers, with a chained-nonce scheme so a client can prove a server lied. The hub already indexes the IETF draft; this is the final RFC that current implementations (roughenough, pyroughtime) cite.

## Key takeaways

- Authenticated time to bootstrap certificate checks or detect a grossly wrong clock, not to discipline an oscillator
- Querying several servers gives cryptographic evidence of misbehaviour

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `roughtime`, `ietf`, `rfc`, `authenticated-time`

## Related

- cites: [Roughtime (draft-ietf-ntp-roughtime)](../../catalog/resources/ietf-roughtime-draft.md)
- has_code: [Roughenough](../../catalog/repos/int08h__roughenough.md)
- has_code: [pyroughtime](../../catalog/repos/dansarie__pyroughtime.md)
- has_code: [Roughtime (Cloudflare)](../../catalog/repos/cloudflare__roughtime.md)

_Indexed by lane(s): timing-network_
