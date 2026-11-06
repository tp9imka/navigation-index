# Auterion Skynode S and Auterion Visual Navigation

`res:auterion-skynode-visual-navigation` - product - <https://thedefensepost.com/2024/07/01/auterion-drone-bypass-jamming/>

**By:** Auterion - **Year:** 2024 - **Level:** intermediate - **Access:** open

Auterion sells PX4-derived AuterionOS plus Skynode flight/mission computers. Skynode S (2024) is a small integrated autopilot/mission computer marketed for operation when GNSS and links are jammed; Auterion Visual Navigation is the company's camera-based position source, named in its 2025 DIU Artemis completion announcement.

## Key takeaways

- Vendor claim: AuterionOS detects GNSS jamming/spoofing and stops trusting GNSS (Jan 2024 announcement)
- Vendor/press claim: used in Ukraine; no public accuracy figures found
- Open-source base is PX4; the visual navigation layer is proprietary

## Deep dives

- [README](../../docs/landscape/README.md) (landscape)
- [gnss-denied-nav-products](../../docs/landscape/gnss-denied-nav-products.md) (landscape)

**Concepts:** [Visual geo-localization (image-to-map)](../concepts/visual-geolocalization.md), [Visual(-inertial) odometry](../concepts/vio.md), [Autopilots and flight control](../concepts/autopilot.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `landscape`, `auterion`, `px4`, `uav`, `vendor-claim`

## Related

- alternative_to: [WildNav](../repos/tiers__wildnav.md)
- alternative_to: [AnyVisLoc benchmark](../repos/uav-avl__benchmark.md)
- alternative_to: [AnyLoc](../repos/anyloc__anyloc.md)
- alternative_to: [PX4 Autopilot](../repos/px4__px4-autopilot.md)
- cites: [Visual Inertial Odometry (VIO) in PX4](../resources/px4-visual-inertial-odometry.md)

_Indexed by lane(s): landscape_
