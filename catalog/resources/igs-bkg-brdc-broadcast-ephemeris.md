# IGS daily merged broadcast navigation files (BKG mirror)

`res:igs-bkg-brdc-broadcast-ephemeris` - dataset - <https://igs.bkg.bund.de/root_ftp/IGS/BRDC/>

**By:** International GNSS Service, BKG (German Federal Agency for Cartography and Geodesy) - **Year:** ? - **Level:** intermediate - **Access:** open

Daily multi-GNSS RINEX navigation files that merge the broadcast ephemerides collected across the IGS network, mirrored by BKG over HTTPS and organised by year and day of year. The standard way to get a real ephemeris for a past date when simulating GNSS signals or reprocessing recorded observations.

## Key takeaways

- Feed a past date's ephemeris to a signal simulator such as gps-sdr-sim or to an SPP solver
- No account needed on the BKG HTTPS mirror
- Broadcast orbits, not precise products; use IGS final orbits when centimetre accuracy matters

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [GNSS positioning](../../catalog/concepts/gnss.md), [Software-defined GNSS receivers](../../catalog/concepts/gnss-sdr.md)

**Tags:** `igs`, `bkg`, `rinex-nav`, `ephemeris`, `brdc`

## Related

- dataset_for: [File-based GNSS signal chain: gps-sdr-sim => GNSS-SDR => spoofing/jamming scorer](../../catalog/samples/gnss-signal-chain.md)
- has_code: [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md)
- same_author: [NTRIP: Networked Transport of RTCM via Internet Protocol (BKG)](../../catalog/resources/bkg-ntrip-about.md)

_Indexed by lane(s): datasets-used_
