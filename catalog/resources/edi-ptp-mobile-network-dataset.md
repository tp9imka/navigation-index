# Clock Synchronization Accuracy over Mobile Networks

`res:edi-ptp-mobile-network-dataset` - dataset - <https://zenodo.org/records/14230741>

**By:** Marcis Kalnins - **Year:** 2024 - **Level:** intermediate - **Access:** open

PTPv2 (PTPd) time synchronization between two hosts across mobile networks including a private 5G SA network, with the slave's PTPd 'offset from master' log values and an independent PPS-vs-PPS offset measured with an Analog Discovery 2 between the two NICs. Setup schematics included. Single zip, about 60 MB, open, CC BY 4.0. One folder is described in 'Clock Synchronization and Network Delay Evaluation over a Private 5G Standalone Network' (Kalnins, Rusins, Elsts).

## Key takeaways

- Real asymmetric, high-jitter packet path - a stress case for a PTP servo or for path-asymmetry detection
- PPS truth lets you compare what PTP thinks against what the clocks actually did
- PTPd, not ptp4l; the README warns the logged offset is the servo's view, not true offset

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `ptp`, `ptpd`, `5g`, `mobile-network`, `1pps`, `zenodo`

## Related

- evaluates: [PTPd](../../catalog/repos/ptpd__ptpd.md)
- dataset_for: [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md)

## Referenced by

- [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md) (uses)

_Indexed by lane(s): timing-network_
