# JPL DE421 planetary ephemeris (NAIF SPK kernel)

`res:jpl-de421-ephemeris` - dataset - <https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/planets/a_old_versions/>

**By:** NASA JPL Solar System Dynamics / NAIF - **Year:** ? - **Level:** intermediate - **Access:** open

The DE421 planetary and lunar ephemeris as a NAIF SPK binary kernel (de421.bsp, about 16 MB), an older but compact JPL Development Ephemeris commonly loaded with Skyfield. Celestial navigation code needs it to place the Sun, Moon and planets and to compute observer geometry.

## Key takeaways

- Small, offline ephemeris adequate for celestial fixes; newer DE files exist under the same NAIF tree
- Load with Skyfield; no account needed
- Kept under a_old_versions on the NAIF server

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Celestial and star-tracker navigation](../../catalog/concepts/celestial-nav.md), [Space and orbital navigation](../../catalog/concepts/space-nav.md)

**Tags:** `ephemeris`, `jpl`, `naif`, `spk`, `skyfield`

## Related

- dataset_for: [Celestial fix: cedar-solve plate solving on real star images, then position from star elevations above an IMU vertical](../../catalog/samples/celestial-star-tracker.md)
- has_code: [Skyfield](../../catalog/repos/skyfielders__python-skyfield.md)

_Indexed by lane(s): datasets-used_
