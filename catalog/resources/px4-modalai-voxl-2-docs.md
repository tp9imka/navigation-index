# PX4 docs: ModalAI VOXL 2

`res:px4-modalai-voxl-2-docs` - doc - <https://docs.px4.io/main/en/flight_controller/modalai_voxl_2.html>

**By:** PX4 / Dronecode, ModalAI - **Year:** 2026 - **Level:** intro - **Access:** open

VOXL 2 combines a Qualcomm QRB5165 companion computer and PX4 on the DSP in one 16 g, 70 x 36 mm board, with a 15 TOPS NPU claim and six camera ports. ModalAI ships VIO (QVIO, OpenVINS server) as part of its SDK.

## Key takeaways

- Flight controller and companion on one SoC: shortest camera-to-EKF path
- 15 TOPS NPU, 8 cores up to 3.091 GHz, 8 GB LPDDR5 (vendor)
- No public third-party VIO latency numbers found for it

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Visual(-inertial) odometry](../../catalog/concepts/vio.md)

**Tags:** `voxl2`, `modalai`, `qrb5165`, `companion`, `vendor-claim`

## Related

- uses: [PX4 Autopilot](../../catalog/repos/px4__px4-autopilot.md)
- uses: [OpenVINS](../../catalog/repos/rpng__open_vins.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
