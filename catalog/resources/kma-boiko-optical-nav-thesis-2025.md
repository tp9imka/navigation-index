# Алгоритм оптичної навігації дрона

`res:kma-boiko-optical-nav-thesis-2025` - report - <https://ekmair.ukma.edu.ua/handle/123456789/36635>

**By:** Khrystyna Boiko, Andrii Hlybovets (advisor), NaUKMA - **Year:** 2025 - **Level:** intermediate - **Access:** open

English: 'Drone optical navigation algorithm'. Master's defense slides (Kyiv-Mohyla Academy): a GeoTIFF map is cut into field-of-view tiles with precomputed keypoints; each drone frame is matched (ORB vs SuperPoint+SuperGlue) against tiles near the current estimate, a homography gives position, and fallback strategies handle lost or repeating fixes. Reported on 930 tiles: SuperPoint+SuperGlue reached the goal in fewer steps with more matches but ~631 s run time vs ~26 s for ORB; goal reached in 30/30 runs.

## Key takeaways

- Tile pre-indexing plus local search around the last fix is the practical VPS structure
- Learned matchers win on match count but cost ~25x run time in this setup
- Explicit fallback behaviours (repeat detection, default heading) matter as much as the matcher
- Motivation cites both EW and fiber-optic range limits

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Feature detection and matching](../concepts/feature-matching.md)

**Tags:** `lang:uk`, `thesis`, `superpoint`, `superglue`, `orb`, `geotiff`

## Related

- uses: [SuperGlue (pretrained)](../repos/magicleap__supergluepretrainednetwork.md)

_Indexed by lane(s): ua-ru-sources_
