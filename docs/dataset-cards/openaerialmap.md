# OpenAerialMap drone orthophotos (as used by the LightGlue geoloc sample)

<!-- about: sample:visual-geolocalization-lightglue -->

OpenAerialMap (OAM, run by HOT) is an open catalogue of user-contributed aerial and drone orthophotos, CC BY 4.0, stored as Cloud-Optimized GeoTIFFs on a public S3 bucket. Coverage is patchy (wherever someone uploaded a survey), but it gives real centimetre-level drone orthos outside the US with no login. No index id of its own; the marker names the sample that uses it.

| Field | Value |
|---|---|
| Platform | Varies per upload; the two scenes used here are consumer-drone surveys |
| Environment | Used here: "Tbilisi (GE) - Saburtalo" (SJRC F22s Pro, 2023-10-08) as the map, and a Batumi survey as the negative control |
| Sensors and rates | RGB orthomosaic. Tbilisi scene: 8447 x 8926 px at 0.1 m in EPSG:3857 units, about 0.075 m on the ground at 41.7 N (sample README) |
| Ground truth | None beyond the ortho's own georeference; the sample synthesizes frames from it with known truth |
| Size | HEAD Content-Length, 2026-11-06: Tbilisi COG 15,119,801 B; Batumi COG 12,707,364 B. The sample's cut map tile is about 9 MB |
| License | CC BY 4.0, "OpenAerialMap contributors" plus the uploader (per scene metadata, as recorded by the sample) |
| Format | COG GeoTIFF, EPSG:3857 |
| Index | [visual-geolocalization-lightglue sample](../../samples/visual-geolocalization-lightglue/) |

## Download

```bash
B=https://oin-hotosm-temp.s3.us-east-1.amazonaws.com
curl -O $B/6523b171ceb34f0001f3742f/0/6523b171ceb34f0001f37430.tif   # Tbilisi Saburtalo, 15 MB
curl -O $B/65056d734a35b70001c38d46/0/65056d734a35b70001c38d47.tif   # Batumi, 12.7 MB
# or let the sample read windows over HTTPS and cut a test pair
python3 samples/visual-geolocalization-lightglue/make_test_pair.py --out data/base
```

Find other scenes by browsing openaerialmap.org or its catalogue API; each scene page links its S3 COG.

## Used in this repo

[samples/visual-geolocalization-lightglue](../../samples/visual-geolocalization-lightglue/) (`make_test_pair.py`, `run_cases.sh`), run 2026-11-06:

- The map is the whole Tbilisi ortho at 1/4 resolution (2111 x 2231 px, 0.4 m units); the "drone frame" is a 1600 x 1200 window at 1/2 resolution, rotated, keystoned, blurred and noised. Internet needed once, about 70 s for the windowed reads.
- SuperPoint + LightGlue on 7 synthetic cases: 0.04-0.21 m error with 441-473 inliers on the yaw cases (full table in the sample). The Batumi frame against the Tbilisi map gives 5 inliers and "no reliable fix" (negative control).

## Hackathon fit

- Idea 18 (visual geolocalization): a quick, redistributable, non-US drone ortho for a demo map when NAIP does not cover the area.
- Synthetic-pair testing of a matcher before real flight data arrives.

## Pitfalls

- Synthetic frames cut from the same ortho as the map share date, sensor and lighting; numbers are a best case. Real flights against an older map drop sharply (see the NAIP card and the geoloc-license-clean sample).
- EPSG:3857 units are not ground metres (factor cos(latitude)); convert before quoting GSD.
- Coverage and quality vary per uploader; check the scene's date and resolution before building on it. Some scenes ship without a usable geotransform: check `src.crs` before trusting `src.transform`.
- Bucket name says "temp"; keep a local copy before the event.

## Sources

- HEAD on both COG URLs, 2026-11-06
- samples/visual-geolocalization-lightglue/README.md, `make_test_pair.py`, `run_cases.sh`
