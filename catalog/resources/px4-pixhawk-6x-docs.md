# PX4 docs: Holybro Pixhawk 6X (FMUv6X)

`res:px4-pixhawk-6x-docs` - doc - <https://docs.px4.io/main/en/flight_controller/pixhawk6x.html>

**By:** PX4 / Dronecode - **Year:** 2026 - **Level:** intro - **Access:** open

Reference page for the Pixhawk 6X: STM32H753 Cortex-M7 at 480 MHz with 2 MB flash and 1 MB RAM, an STM32F100 IO processor, triple IMU (ICM-45686 on rev 8), built to the Pixhawk FMUv6X open standard (DS-012).

## Key takeaways

- The class of MCU that runs EKF2 at its default 100 Hz prediction rate
- No room for image processing: vision runs on a companion
- Open hardware standard means multiple vendors build compatible FMUs

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `pixhawk`, `fmu-v6x`, `stm32h7`, `flight-controller`

## Related

- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
