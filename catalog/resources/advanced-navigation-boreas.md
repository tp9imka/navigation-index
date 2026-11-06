# Advanced Navigation Boreas FOG INS with LVS laser velocity sensor

`res:advanced-navigation-boreas` - product - <https://www.criticalcomms.com.au/content/transport/article/beating-the-jammers-australian-tech-gives-warfighters-precision-in-gps-blackouts-289326898>

**By:** Advanced Navigation - **Year:** 2026 - **Level:** intermediate - **Access:** open

Advanced Navigation's Boreas fibre-optic-gyro INS line, fused with its LVS laser velocity sensor or wheel odometry, is marketed for long GNSS-denied ground and maritime runs; reported trials include a US Army testbed and an underground mine.

## Key takeaways

- Vendor/press claims: 11.7 m error over 65 km with GNSS jammed (wheel-encoder config, US Army testbed, linked article); better than 0.1% of distance travelled in BHP's Callio mine trial (Advanced Navigation case study)
- Strategy is inertial-centric dead reckoning with velocity aiding, not vision

## Deep dives

- [gnss-denied-nav-products](../../docs/landscape/gnss-denied-nav-products.md) (landscape)

**Concepts:** [Inertial navigation (INS/IMU)](../concepts/ins.md), [Ground vehicle autonomy](../concepts/ground-vehicle-nav.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `landscape`, `advanced-navigation`, `fog`, `vendor-claim`

## Related

- alternative_to: [KF-GINS](../repos/i2nav-whu__kf-gins.md)
- alternative_to: [pyins](../repos/nmayorov__pyins.md)
- alternative_to: [gnss-ins-sim](../repos/aceinna__gnss-ins-sim.md)

_Indexed by lane(s): landscape_
