# SDR приемник GPS на микроконтроллере

`res:habr-mcu-gps-sdr-2024` - blog - <https://habr.com/ru/articles/789382/>

**By:** iliasam - **Year:** 2024 - **Level:** advanced - **Access:** open

English: 'SDR GPS receiver on a microcontroller'. Builds a real-time software GPS receiver on an STM32F4 (later ESP32) fed with 1-bit samples from a MAX2769 front end: XOR-based correlation, table bit-sums, four time-multiplexed channels with DLL/PLL, navigation decoding, RTCM 3 pseudorange output and on-chip RTKLIB positioning (author reports ~80 m indoors).

## Key takeaways

- A GPS receiver can run on a commodity MCU without FPGA
- Exposes the tracking loops that interference attacks
- Good hands-on companion to receiver-theory articles

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md), [GNSS positioning](../../catalog/concepts/gnss.md)

**Tags:** `lang:ru`, `habr`, `stm32`, `sdr`, `diy`

## Related

- uses: [RTKLIB](../../catalog/repos/tomojitakasu__rtklib.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-sources_
