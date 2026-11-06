# RFC 8915: Network Time Security for the Network Time Protocol

`res:rfc8915-nts` - standard - <https://www.rfc-editor.org/rfc/rfc8915>

**By:** D. Franke, D. Sibold, K. Teichel, M. Dansarie, R. Sundblad - **Year:** 2020 - **Level:** advanced - **Access:** open

Specifies NTS: a TLS-based key exchange followed by authenticated NTP packets, protecting clients from on-path spoofing of time responses.

## Key takeaways

- Authenticates the server; does not stop delay attacks
- Supported by chrony, ntpd-rs and NTPsec

**Concepts:** [Timing and time transfer](../concepts/timing.md), [Standards and interface specs](../concepts/standards.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `nts`, `ntp`, `rfc`, `authentication`

## Related

- has_code: [ntpd-rs](../repos/pendulum-project__ntpd-rs.md)
- has_code: [chrony](../repos/gitlab.com__chrony__chrony.md)
- has_code: [cfnts](../repos/cloudflare__cfnts.md)

## Referenced by

- [NIST Authenticated NTP Service](../resources/nist-authenticated-ntp.md) (explains)
- [RFC 7384: Security Requirements of Time Protocols in Packet Switched Networks](../resources/rfc7384-time-protocol-security.md) (cites)

_Indexed by lane(s): timing_
