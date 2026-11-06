# Помехи в глобальных навигационных спутниковых системах

`res:habr-gnss-interference-klimenko-2016` - blog - <https://habr.com/ru/articles/389071/>

**By:** Mikhail Klimenko (NelSon29) - **Year:** 2016 - **Level:** intermediate - **Access:** open

English: 'Interference in global navigation satellite systems'. Habr article by a developer of interference-resistant receivers: why GNSS is below the noise floor, receiver structure (front end, 1-2 bit sampling, per-satellite correlator channels), narrowband vs wideband jamming and spoofing, and their effect on code/carrier tracking loops.

## Key takeaways

- Clear receiver-level explanation of how jamming breaks tracking loops
- Low-bit quantization trades SNR for simpler correlators, which matters under jamming
- Anti-jam methods were deferred to a part 2

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md)

**Tags:** `lang:ru`, `habr`, `receiver-internals`

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-sources_
