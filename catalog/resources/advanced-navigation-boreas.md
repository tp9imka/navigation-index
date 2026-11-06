# Advanced Navigation Boreas FOG INS with LVS laser velocity sensor

`res:advanced-navigation-boreas` - product - <https://www.criticalcomms.com.au/content/transport/article/beating-the-jammers-australian-tech-gives-warfighters-precision-in-gps-blackouts-289326898>

**By:** Advanced Navigation - **Year:** 2026 - **Level:** intermediate - **Access:** open

Advanced Navigation's Boreas fibre-optic-gyro INS line, fused with its LVS laser velocity sensor or wheel odometry, is marketed for long GNSS-denied ground and maritime runs; reported trials include a US Army testbed and an underground mine.

## Key takeaways

- Vendor/press claims: 11.7 m error over 65 km with GNSS jammed (wheel-encoder config, US Army testbed, linked article); better than 0.1% of distance travelled in BHP's Callio mine trial (Advanced Navigation case study)
- Strategy is inertial-centric dead reckoning with velocity aiding, not vision

## Deep dives

- [gnss-denied-nav-products](../../docs/landscape/gnss-denied-nav-products.md) (landscape)

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Ground vehicle autonomy](../../catalog/concepts/ground-vehicle-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `landscape`, `advanced-navigation`, `fog`, `vendor-claim`

## Related

- alternative_to: [KF-GINS](../../catalog/repos/i2nav-whu__kf-gins.md)
- alternative_to: [pyins](../../catalog/repos/nmayorov__pyins.md)
- alternative_to: [gnss-ins-sim](../../catalog/repos/aceinna__gnss-ins-sim.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Integrity monitoring for navigation and alt-PNT](../../docs/integrity-monitoring.md) (mentions)
- [GNSS-denied navigation: products and companies](../../docs/landscape/gnss-denied-nav-products.md) (mentions)
- [Landscape: what judges already know](../../docs/landscape/README.md) (mentions)
- [Navigation trends 2025-2026](../../docs/landscape/trends-2025-2026.md) (mentions)

_Indexed by lane(s): landscape_
