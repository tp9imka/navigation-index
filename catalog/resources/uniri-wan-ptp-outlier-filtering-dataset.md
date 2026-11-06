# Data for "PTP over wide area networks with offset measurement outlier filtering"

`res:uniri-wan-ptp-outlier-filtering-dataset` - dataset - <https://zenodo.org/records/14231423>

**By:** Victor Vazquez, Carlos Megias, Carmen Velez, Hector Esteban, Javier Diaz - **Year:** 2024 - **Level:** advanced - **Access:** free-registration

University of Granada measurements of ptp4l and chrony time transfer over about 200 km of research network between ROA (Spanish UTC lab) and Granada, plus Calnex Paragon-X network emulation runs and free-running NIC stability against a passive hydrogen maser. CSVs give ptp4l offset_raw, offset_sw, delay, frequency adjustment and a hardware 1PPS time error from a frequency counter, and GNSS common-view one-way delays. Zenodo marks the files as restricted (access on request), CC BY 4.0.

## Key takeaways

- The only dataset found with both ptp4l's own offset estimate and an independent 1PPS truth - exactly what a replay needs
- One-way delays each direction give the real path asymmetry, not an assumed one
- Files are restricted on Zenodo: request access early, it is not a same-day download

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `ptp4l`, `chrony`, `wan`, `time-transfer`, `1pps`, `path-asymmetry`, `zenodo`

## Related

- evaluates: [linuxptp](../../catalog/repos/nwtime__linuxptp.md)
- evaluates: [chrony](../../catalog/repos/gitlab.com__chrony__chrony.md)
- dataset_for: [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md)
- uses: [allantools](../../catalog/repos/aewallin__allantools.md)

_Indexed by lane(s): timing-network_
