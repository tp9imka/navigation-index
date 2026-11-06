# OSNMAlib bundled Galileo I/NAV recording (custom_run)

`res:osnmalib-galileo-inav-recording` - dataset - <https://github.com/Algafix/OSNMA/tree/master/custom_run>

**By:** Aleix Galan (OSNMAlib) - **Year:** ? - **Level:** advanced - **Access:** open

A real 76-minute Septentrio SBF GALRawINAV recording of live Galileo E1 I/NAV pages with OSNMA, shipped in the OSNMAlib repository alongside the matching GSC public key and Merkle tree, plus an older recording from the previous public-key period. About 2.6 MB: the smallest real OSNMA input available, no receiver or account needed. EUPL-1.2 as part of the repo.

## Key takeaways

- Runs OSNMA authentication offline in seconds; attacks can be injected by manipulating pages
- File mode trusts the signal's own GST, so a months-old replay still authenticates: replay demos need an independent clock
- No DSM-PKR in the recording, so cold start with only the Merkle tree cannot be shown
- The bundled key and tree go stale at the next GSC renewal

## Deep dives

- [osnmalib-recording](../../docs/dataset-cards/osnmalib-recording.md) (dataset-cards)

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [GNSS positioning](../../catalog/concepts/gnss.md)

**Tags:** `osnma`, `galileo`, `sbf`, `septentrio`, `authentication`, `replay`

## Related

- part_of: [OSNMAlib](../../catalog/repos/algafix__osnma.md)
- dataset_for: [Galileo OSNMA authentication as a spoofing defence: real recording, file-level attacks, scorer adapter](../../catalog/samples/osnma-authentication.md)
- uses: [Galileo Open Service Navigation Message Authentication (OSNMA) - service page](../../catalog/resources/galileo-osnma-service-page.md)

_Indexed by lane(s): datasets-used_
