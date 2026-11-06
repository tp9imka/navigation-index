# VPAIR - Aerial Visual Place Recognition and Localization in Large-scale Outdoor Environments

`res:vpair-dataset-2022` - dataset - <https://arxiv.org/abs/2205.11567>

**By:** Michael Schleiss, Fahmi Rouatbi, Daniel Cremers - **Year:** 2022 - **Level:** intermediate - **Access:** open

ICRA 2022 aerial-robotics workshop paper introducing VPAIR: downward camera images from a light aircraft flying above 300 m, each paired with a reference render with depth and a 6-DoF pose, over 100+ km of urban, farmland and forest terrain. Licence: the README says academic use only, commercial use prohibited (the small Zenodo sample is tagged CC BY 4.0).

## Key takeaways

- Medium-altitude aerial VPR benchmark
- Reference renders with depth
- Academic use only

## Deep dives

- [vpair](../../docs/dataset-cards/vpair.md) (dataset-cards)

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `aerial-vpr`, `dataset`, `academic-only`

## Related

- has_code: [VPAIR](../../catalog/repos/aervisloc__vpair.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [End-to-end GNSS-denied visual navigation on one real flight: nadir VO + DINOv2 retrieval + LightGlue fixes + multi-frame voting + altpnt integrity (VPAIR)](../../catalog/samples/e2e-visual-nav-vpair.md) (uses)
- [Two independent absolute sources on one real flight: visual fixes + terrain-relative navigation with solution-separation integrity (VPAIR over NRW 1 m LiDAR)](../../catalog/samples/two-source-integrity-vpair.md) (uses)

_Indexed by lane(s): backlog_
