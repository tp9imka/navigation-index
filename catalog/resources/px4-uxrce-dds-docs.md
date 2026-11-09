# PX4 uXRCE-DDS (PX4-ROS 2/DDS Bridge)

`res:px4-uxrce-dds-docs` - doc - <https://docs.px4.io/main/en/middleware/uxrce_dds.html>

**By:** PX4 / Dronecode - **Year:** 2026 - **Level:** intermediate - **Access:** open

How PX4 exposes uORB topics to ROS 2: a client in firmware, the Micro XRCE-DDS Agent on the companion, a dds_topics.yaml allow-list, serial or UDP transport, and built-in timestamp synchronisation.

## Key takeaways

- Only topics in dds_topics.yaml cross the bridge; default rate cap 100 Hz
- UXRCE_DDS_SYNCT keeps PX4 and ROS 2 timestamps aligned (on by default)
- DDS is unauthenticated: keep the link isolated
- px4_msgs must match the firmware's message definitions

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Timing and time transfer](../../catalog/concepts/timing.md)

**Tags:** `px4`, `ros2`, `uxrce-dds`, `uorb`, `time-sync`

## Related

- uses: [Micro XRCE-DDS Agent](../../catalog/repos/eprosima__micro-xrce-dds-agent.md)
- uses: [px4_msgs](../../catalog/repos/px4__px4_msgs.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
