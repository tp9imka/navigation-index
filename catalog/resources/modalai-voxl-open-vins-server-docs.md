# VOXL OpenVINS server

`res:modalai-voxl-open-vins-server-docs` - doc - <https://docs.modalai.com/voxl-open-vins-server/>

**By:** ModalAI - **Year:** 2026 - **Level:** intermediate - **Access:** open

ModalAI docs for the OpenVINS-based VIO service on VOXL 2. Publishes full state with covariances, feature counts, a quality score with INITIAL / GOOD / BAD hysteresis, error codes and status, and forwards odometry to the autopilot. Auto-resets on excessive velocity, low feature count for a timeout, or spinning in place. Only one VIO source (qVIO or OpenVINS) may run at a time.

## Key takeaways

- A shipping example of the health signals a planner can consume: features, quality, resets
- Reset triggers document the real failure modes
- The old docs path voxl-qvio-server now redirects here

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `voxl`, `modalai`, `openvins`, `quality`, `reset`, `vendor-doc`

## Related

- uses: [OpenVINS](../../catalog/repos/rpng__open_vins.md)
- part_of: [PX4 docs: ModalAI VOXL 2](../../catalog/resources/px4-modalai-voxl-2-docs.md)

_Indexed by lane(s): close-area-localization_
