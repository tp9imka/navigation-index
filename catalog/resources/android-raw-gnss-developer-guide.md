# Raw GNSS Measurements

`res:android-raw-gnss-developer-guide` - doc - <https://developer.android.com/develop/sensors-and-location/sensors/gnss>

**By:** Google - **Year:** 2024 - **Level:** intro - **Access:** open

Android documentation on the GnssMeasurement API: which phones expose pseudorange, carrier phase and AGC, and how to log them.

## Key takeaways

- AGC and C/N0 fields support jamming detection on phones
- Duty cycling must be disabled for continuous carrier phase

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Jamming and spoofing](../../catalog/concepts/gnss-interference.md)

**Tags:** `android`, `api`

## Related

- explains: [GPS Measurement Tools (incl. GnssLogger)](../../catalog/repos/google__gps-measurement-tools.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [2. GNSS and its threats](../../docs/primer/02-gnss-and-threats.md) (mentions)

_Indexed by lane(s): gnss_
