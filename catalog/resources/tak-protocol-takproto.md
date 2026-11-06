# TAK Protocol (takproto) - protobuf encoding of CoT

`res:tak-protocol-takproto` - doc - <https://github.com/deptofdefense/AndroidTacticalAssaultKit-CIV/blob/main/takproto/README.md>

**By:** US DoD / TAK Product Center - **Year:** 2020 - **Level:** intermediate - **Access:** open

Documentation of the TAK protocol used by ATAK and TAK Server: how CoT events are framed and carried as protocol buffers over mesh (UDP multicast) and streaming (TCP/TLS) transports, alongside legacy XML.

## Key takeaways

- Explains version negotiation between XML and protobuf CoT
- Mesh vs streaming framing headers
- Essential to get a custom app talking to ATAK

**Concepts:** [Situational awareness and C2 interop](../concepts/situational-awareness.md), [Standards and interface specs](../concepts/standards.md)

**Tags:** `tak`, `cot`, `protobuf`, `atak`

## Related

- has_code: [ATAK-CIV (DoD release, archived)](../repos/deptofdefense__androidtacticalassaultkit-civ.md)
- has_code: [ATAK-CIV (TAK Product Center)](../repos/tak-product-center__atak-civ.md)
- has_code: [PyTAK](../repos/snstac__pytak.md)
- cites: [Cursor on Target (NDIA briefing)](../resources/cot-niessen-ndia-2008.md)

_Indexed by lane(s): docs-standards_
