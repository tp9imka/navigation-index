# NASA SkyView virtual observatory

`res:nasa-skyview-virtual-observatory` - dataset - <https://skyview.gsfc.nasa.gov/current/cgi/titlepage.pl>

**By:** NASA Goddard Space Flight Center - **Year:** ? - **Level:** intermediate - **Access:** open

A NASA service that cuts FITS images with a reference WCS from many all-sky surveys at any position, scale and projection. The celestial star-tracker sample pulls cutouts of the Mellinger optical all-sky mosaic to score plate-solving accuracy against a known attitude.

## Key takeaways

- Free reference star fields with known pointing for testing lost-in-space star trackers
- Under load it can answer with an HTML 'Too Many Processes' page instead of FITS; retry and validate
- Survey mosaics are not camera frames: no lens distortion, noise or stray light of a real sensor

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Celestial and star-tracker navigation](../../catalog/concepts/celestial-nav.md)

**Tags:** `skyview`, `fits`, `star-field`, `plate-solving`, `mellinger`

## Related

- dataset_for: [Celestial fix: cedar-solve plate solving on real star images, then position from star elevations above an IMU vertical](../../catalog/samples/celestial-star-tracker.md)
- uses: [cedar-solve](../../catalog/repos/smroid__cedar-solve.md)

_Indexed by lane(s): datasets-used_
