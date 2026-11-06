# OpenDroneMap Aukerman Park eBee image set

`res:odm-aukerman-ebee-dataset` - dataset - <https://github.com/OpenDroneMap/odm_data_aukerman>

**By:** OpenDroneMap - **Year:** ? - **Level:** intro - **Access:** open

A CC0 set of nadir photos from a senseFly eBee survey of Aukerman Park, Ohio, distributed by OpenDroneMap as a photogrammetry test dataset, with EXIF GPS in each frame. The geolocalization samples use these real drone frames as queries against NAIP orthophotos of the same park.

## Key takeaways

- Real fixed-wing drone frames with a public-domain licence and EXIF positions as approximate truth
- Overlaps several NAIP epochs, so map-age effects can be measured on real imagery
- EXIF GPS is a consumer-grade fix, not survey truth

**Concepts:** [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Place recognition and loop closure](../../catalog/concepts/place-recognition.md)

**Tags:** `ebee`, `drone-imagery`, `cc0`, `photogrammetry`, `opendronemap`

## Related

- dataset_for: [License-clean drone frame to orthophoto geolocalization (ALIKED / DISK / SIFT + LightGlue)](../../catalog/samples/geoloc-license-clean.md)
- dataset_for: [Large-area visual place recognition for lost-GNSS recovery (DINOv2 GeM / VLAD over a 49 km2 NAIP tile DB, chained to LightGlue fine matching)](../../catalog/samples/vpr-large-area.md)
- has_code: [OpenDroneMap (ODM)](../../catalog/repos/opendronemap__odm.md)
- uses: [NAIP aerial imagery on Microsoft Planetary Computer](../../catalog/resources/naip-planetary-computer.md)

_Indexed by lane(s): datasets-used_
