# kiwiclient

`repo:jks-prv/kiwiclient` - <https://github.com/jks-prv/kiwiclient>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 98 | Python | ? | 2026-08-03 | False | production | medium |

Python clients for KiwiSDR receivers, including recorders that save IQ with GNSS timestamps from the receiver.

**Why it matters:** GNSS-timestamped IQ from a public network of receivers is the input for HF TDOA; it also shows what breaks when the receivers' GNSS time is denied.

**Hackathon notes:** Pure Python; record from public KiwiSDRs. Timestamps are only as good as each receiver's GNSS.

**Concepts:** [Timing and time transfer](../concepts/timing.md), [RF localization and direction finding](../concepts/rf-localization.md)

**Tags:** `kiwisdr`, `hf`, `iq`, `gnss-timestamps`, `tdoa`

**Domains:** multi

## Related

- integrates_with: [KiwiSDR](../repos/jks-prv__kiwisdr.md)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
