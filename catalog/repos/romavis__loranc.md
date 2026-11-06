# LoranC receiver

`repo:romavis/loranc` - <https://github.com/romavis/LoranC>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 7 | IDL | NOASSERTION | 2014-06-05 | False | archived | low |

Hobby project to build a DSP-based Loran-C receiver that can also lock onto the Russian Chayka chain. The published repo holds only KiCad hardware designs (loop antenna preamp, power supply, processing board, RF prototype); no DSP firmware or software.

**Why it matters:** One of very few open receivers for low-frequency hyperbolic navigation, the basis of eLoran.

**Hackathon notes:** Hardware reference only, last touched 2014: the loop-antenna preamp and RF front-end schematics are the useful part for an LF receiver build. No signal processing code to reuse.

**Concepts:** [Signals of opportunity](../concepts/signals-of-opportunity.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `loran-c`, `chayka`, `eloran`, `lf`, `dsp`

**Domains:** maritime, multi

## Related

- alternative_to: [Loran-C reference signal generator](../repos/cheolj__loran-c-reference-code.md)

## Referenced by

- [Loran-C reference signal generator](../repos/cheolj__loran-c-reference-code.md) (alternative_to)
- [The Global Loran / eLoran Infrastructure Evolution: A Robust and Resilient PNT Backup for GNSS](../resources/faa-eloran-iat-2014.md) (explains)

_Indexed by lane(s): gap-fill_

_GitHub metadata fetched 2026-11-06._
