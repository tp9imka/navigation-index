# IS-GPS-200N: NAVSTAR GPS Space Segment / Navigation User Segment Interfaces

`res:gps-is-gps-200n` - standard - <https://archive.gps.gov/technical/icwg/IS-GPS-200N.pdf>

**By:** US Space Force / GPS ICWG, US Space Force GPS Directorate - **Year:** 2022 - **Level:** advanced - **Access:** open

The master interface specification for the legacy GPS L1 C/A and L2C (and P(Y) at the public level) signals: code generation, signal structure, and the full LNAV/CNAV navigation message bit layouts. Every GPS receiver, simulator and spoofing detector ultimately decodes against this document.

## Key takeaways

- Defines LNAV subframe and CNAV message formats bit-for-bit
- Ephemeris, clock and ionosphere parameter algorithms live here
- Revisions are managed through the public ICWG process
- Authoritative source for ephemeris and clock equations
- Defines L1 C/A and L2C signal structure
- Needed to build or audit any navigation message decoder

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `icd`, `gps`, `l1-ca`, `l2c`, `navigation-message`, `l1`

## Related

- has_code: [RTKLIB](../../catalog/repos/tomojitakasu__rtklib.md)
- has_code: [RTKLIB demo5 (rtklibexplorer)](../../catalog/repos/rtklibexplorer__rtklib.md)
- has_code: [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md)
- has_code: [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md)
- explains: [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md)
- explains: [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md)

## Referenced by

- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)
- [GPS Interface Control Documents (ICWG index)](../../catalog/resources/gps-icwg-document-index.md) (part_of)

_Indexed by lane(s): docs-standards, gnss_
