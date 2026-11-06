# Iridium PNT (Satellite Time and Location) and Iridium PNT ASIC

`res:iridium-pnt-stl-asic` - product - <https://www.gpsworld.com/iridium-pnt-asic-now-commercially-available-bringing-resilient-gnss-protection-to-devices-worldwide/>

**By:** Iridium - **Year:** 2026 - **Level:** intermediate - **Access:** open

Iridium broadcasts a high-power LEO timing and location signal (STL, from the Satelles acquisition) usable as a GNSS backup and cross-check. A dedicated PNT ASIC was unveiled in October 2025 and announced commercially available in July 2026; integrators include Solace and Skyband, and VectorNav/NAL Research announced STL-aided INS work in 2025.

## Key takeaways

- Positioning is coarse compared to GNSS; main value is timing and an independent plausibility check
- Vendor claim on ASIC size: 8 x 8 mm, under 0.2 g (press)
- Open LEO Doppler code in the index can use Iridium signals of opportunity without a subscription

## Deep dives

- [README](../../docs/landscape/README.md) (landscape)
- [gnss-denied-nav-products](../../docs/landscape/gnss-denied-nav-products.md) (landscape)
- [trends-2025-2026](../../docs/landscape/trends-2025-2026.md) (landscape)

**Concepts:** [Signals of opportunity](../concepts/signals-of-opportunity.md), [Timing and time transfer](../concepts/timing.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `landscape`, `iridium`, `stl`, `leo-pnt`, `vendor-claim`

## Related

- alternative_to: [Starlink LEO-PNT](../repos/przemyslawpiekarski__starlink-leo-pnt.md)
- alternative_to: [UT Starlink signal simulator](../repos/gitlab.com__radionavlab__public__ut-starlink-signal-simulator.md)
- alternative_to: [LEO SoOP positioning thesis (Voska)](../repos/voskavoj__dp.md)

## Referenced by

- [VectorNav - Iridium STL-aided INS collaboration with NAL Research](../resources/vectornav-stl-aided-ins.md) (uses)

_Indexed by lane(s): landscape_
