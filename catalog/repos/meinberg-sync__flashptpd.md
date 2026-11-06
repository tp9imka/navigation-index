# flashptpd

`repo:meinberg-sync/flashptpd` - <https://github.com/meinberg-sync/flashptpd>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 51 | C++ | MIT | 2024-07-02 | True | archived | low |

Experimental C++17 client/server style PTP from Meinberg: the client sends Sync with a request TLV and the server answers, so no BMCA or master announce is needed. Archived.

**Why it matters:** Shows a unicast request/response PTP variant close to NTP in shape; useful when thinking about how a client chooses among several servers.

**Hackathon notes:** Archived; read for the protocol idea, do not build on it.

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `ptp`, `client-server`, `meinberg`, `c++`

**Domains:** multi

## Related

- alternative_to: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)

_Indexed by lane(s): timing-network_

_GitHub metadata fetched 2026-11-06._
