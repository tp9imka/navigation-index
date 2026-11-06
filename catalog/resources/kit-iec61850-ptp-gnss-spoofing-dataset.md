# IEC61850 SV and PTP traffic under GNSS time synchronization attacks

`res:kit-iec61850-ptp-gnss-spoofing-dataset` - dataset - <https://doi.org/10.35097/8k5cjmx5mqrq61qk>

**By:** Clemens Fruboese (KIT KASTEL) - **Year:** 2026 - **Level:** advanced - **Access:** open

Pseudonymised pcap captures of IEC 61850 Sampled Values and IEEE 1588 PTP traffic from the KIT KASTEL energy security lab while the substation's GNSS-fed time server is spoofed. About 592 GB tar on KIT RADAR, CC BY-NC 4.0. Companion of the jamming dataset; related publication 'Compromising Synchrophasor Data by Attacking Time Synchronization: A Hardware-Lab Study' (2026). The landing page does not list devices or derived offset series.

## Key takeaways

- Real PTP grandmaster behaviour while its GNSS input is attacked - announce/clockClass changes and timestamps are in the pcaps
- Very large: plan a partial download and a pcap-to-offset extraction step
- Non-commercial licence

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `ptp`, `iec-61850`, `pcap`, `gnss-spoofing`, `substation`, `kit`

## Related

- same_author: [IEC61850 SV and PTP traffic under GNSS jamming](../../catalog/resources/kit-iec61850-ptp-gnss-jamming-dataset.md)
- dataset_for: [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md)
- cites: [Evaluation of the vulnerability of phasor measurement units to GPS spoofing attacks](../../catalog/resources/shepard-humphreys-2012-pmu-spoofing.md)

## Referenced by

- [IEC61850 SV and PTP traffic under GNSS jamming](../../catalog/resources/kit-iec61850-ptp-gnss-jamming-dataset.md) (same_author)

_Indexed by lane(s): timing-network_
