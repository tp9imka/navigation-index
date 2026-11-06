# Roughenough

`repo:int08h/roughenough` - <https://github.com/int08h/roughenough>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 149 | Rust | Apache-2.0 | 2026-11-02 | False | active-research | medium |

Rust Roughtime (RFC 10049) server and client with a batching UDP server, optional malfeasance reporting and several key-protection backends (KMS, PKCS#11, SSH agent).

**Why it matters:** Quickest way to stand up an authenticated rough-time source and a client that checks several servers against each other.

**Hackathon notes:** cargo build needs a recent Rust (README states MSRV 1.94.1). Run a local server plus public servers; show the client flagging a server whose time you skew.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `roughtime`, `rfc10049`, `rust`, `authenticated-time`

**Domains:** multi

## Related

- alternative_to: [Roughtime (Cloudflare)](../../catalog/repos/cloudflare__roughtime.md)
- alternative_to: [pyroughtime](../../catalog/repos/dansarie__pyroughtime.md)

## Referenced by

- [pyroughtime](../../catalog/repos/dansarie__pyroughtime.md) (alternative_to)
- [RFC 10049: Roughtime: A Protocol for Rough Time Synchronization](../../catalog/resources/rfc10049-roughtime.md) (has_code)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
