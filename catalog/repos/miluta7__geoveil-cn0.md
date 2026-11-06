# geoveil-cn0

`repo:miluta7/geoveil-cn0` - <https://github.com/miluta7/geoveil-cn0>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 5 | Rust | NOASSERTION | 2026-09-29 | False | research-prototype | medium |

Rust library with a Python API (pip install geoveil-cn0) that scores GNSS signal quality from RINEX observation files via C/N0 and flags jamming, spoofing and interference across six constellations.

**Why it matters:** Drop-in signal-quality monitor for a navigation stack.

**Hackathon notes:** Input is plain RINEX 2-4 files (decompress Hatanaka first); the spoofing check needs a broadcast nav file. Licence is PolyForm Noncommercial with an attribution term - no commercial use.

**Concepts:** [Jamming and spoofing](../concepts/gnss-interference.md), [GNSS positioning](../concepts/gnss.md)

**Tags:** `cn0`, `rust`, `python`, `monitoring`

**Domains:** multi

_Indexed by lane(s): round3-expansion_

_GitHub metadata fetched 2026-11-06._
