# Roughtime (Cloudflare)

`repo:cloudflare/roughtime` - <https://github.com/cloudflare/roughtime>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 178 | Go | Apache-2.0 | 2026-04-28 | False | active-research | medium |

Go implementation of Roughtime, a protocol that returns signed coarse timestamps so a client can prove a server lied and can combine several servers.

**Why it matters:** Gives a cryptographically checkable, coarse sanity bound on time, useful to catch large GNSS or NTP time shifts at boot.

**Hackathon notes:** Query several public Roughtime servers at startup; reject GNSS time if it is outside their bound. Accuracy is seconds-level by design, not a fine timing source.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `roughtime`, `authenticated-time`, `go`

**Domains:** multi

## Related

- same_org: [cfnts](../repos/cloudflare__cfnts.md)

## Referenced by

- [Roughtime (draft-ietf-ntp-roughtime)](../resources/ietf-roughtime-draft.md) (has_code)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
