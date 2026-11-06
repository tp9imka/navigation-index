# Vision-based GNSS-Free Localization for UAVs in the Wild

`res:wildnav-gnss-free-uav-localization-2022` - paper - <https://arxiv.org/abs/2210.09727>

**By:** Marius-Mihail Gurgu, Jorge Peña Queralta, Tomi Westerlund - **Year:** 2022 - **Level:** intermediate - **Access:** open

Proposes matching drone camera frames to open satellite imagery with learned feature matching to get absolute position without GNSS, evaluated on flights over non-urban areas.

## Key takeaways

- Satellite tiles + learned matcher is a workable visual GPS baseline
- Failure cases cluster over low-texture and changed terrain

## Deep dives

- [wildnav-gnss-free-uav-localization-2022](../../docs/paper-digests/wildnav-gnss-free-uav-localization-2022.md) (paper-digests)

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Feature detection and matching](../../catalog/concepts/feature-matching.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `arxiv`, `uav`

## Related

- has_code: [WildNav](../../catalog/repos/tiers__wildnav.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Learning paths](../../docs/learning-paths.md) (mentions)
- [5. Absolute alternative PNT](../../docs/primer/05-absolute-alt-pnt.md) (mentions)

_Indexed by lane(s): alt-nav_
