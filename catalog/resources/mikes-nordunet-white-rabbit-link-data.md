# MIKES NorduNET NTS White Rabbit link data (UTC(MIKE) - WR(RISE))

`res:mikes-nordunet-white-rabbit-link-data` - dataset - <https://monitor.mikes.fi/ftp/NTS_data/readme.txt>

**By:** VTT MIKES - **Year:** 2026 - **Level:** intermediate - **Access:** open

Public HDF5 files from the White Rabbit link between RISE (Stockholm) and MIKES (Espoo): time-interval counter readings of UTC(MIKE) against the WR-delivered RISE time every 10 minutes (valid from about 2026-05-23), plus WR switch telemetry (round-trip time in ps for boundary clocks at SUNET, CSC and MIKES) via SNMP. Updated about daily per the readme; an example plotting script sits in the same folder.

## Key takeaways

- A real long-haul WR time-transfer series against a national UTC realisation - good for Allan deviation and drift plots
- RTT telemetry lets you look for path changes
- Live folder, no DOI or licence stated - cite the URL and date of download

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `white-rabbit`, `time-transfer`, `utc-k`, `hdf5`, `mikes`, `rise`

## Related

- uses: [White Rabbit (CERN project page)](../../catalog/resources/cern-white-rabbit.md)
- uses: [White Rabbit switch software](../../catalog/repos/gitlab.com__ohwr__project__wr-switch-sw.md)
- uses: [allantools](../../catalog/repos/aewallin__allantools.md)
- dataset_for: [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md)

_Indexed by lane(s): timing-network_
