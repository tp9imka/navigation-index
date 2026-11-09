# PX4 uORB message: AuxGlobalPosition

`res:px4-aux-global-position-msg` - doc - <https://docs.px4.io/main/en/msg_docs/AuxGlobalPosition.html>

**By:** PX4 / Dronecode - **Year:** 2026 - **Level:** intermediate - **Access:** open

uORB message for an external global position (lat, lon, alt, eph, epv) tagged with a source type: vision, terrain, magnetic, pseudolites, LEO and others. EKF2 fuses up to 4 instances (EKF2_AGP*_ params) and the DDS bridge accepts it on /fmu/in/aux_global_position.

## Key takeaways

- The cleanest PX4 entry point for a visual-geolocalisation or terrain-matching fix
- Dedicated message with a source enum is on PX4 main; v1.16 and v1.17 bridge the same topic as VehicleGlobalPosition
- Only horizontal position is fused; vertical bit is reserved (params file on main)

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md)

**Tags:** `px4`, `ekf2`, `aux-global-position`, `uorb`, `alt-pnt`

## Related

- has_code: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
