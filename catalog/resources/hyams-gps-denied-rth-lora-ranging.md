# GPS-denied RTH for MAVLink systems using LoRa radio ranging

`res:hyams-gps-denied-rth-lora-ranging` - blog - <https://discuss.ardupilot.org/t/sam-hyamss-gps-denied-rth-for-mavlink-systems-using-lora-radio-ranging/130709>

**By:** Sam Hyams - **Year:** 2025 - **Level:** intermediate - **Access:** open

Blog (shared on ArduPilot Discourse) on returning a plane home without GPS using range measurements from a LoRa radio to a ground beacon; discussion covers multilateration and EKF3 range fusion.

## Key takeaways

- Radio ranging as a cheap GNSS backup for RTH
- Needs multiple beacons for a full position fix

**Concepts:** [RF localization and direction finding](../concepts/rf-localization.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Electronic warfare resilience](../concepts/ew-resilience.md)

**Tags:** `lora`, `ranging`, `rth`

## Related

- uses: [ArduPilot](../repos/ardupilot__ardupilot.md)

_Indexed by lane(s): autopilots_
