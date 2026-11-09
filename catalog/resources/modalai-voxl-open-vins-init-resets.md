# VOXL OpenVINS server: Initialization and Resets

`res:modalai-voxl-open-vins-init-resets` - doc - <https://docs.modalai.com/voxl-open-vins-init/>

**By:** ModalAI - **Year:** 2026 - **Level:** intermediate - **Access:** open

ModalAI docs page (read 2026-11-09). VIO starts from a static or a dynamic (about 2 s structure-from-motion) initialization. Two reset tiers: a soft reset rebuilds the filter state while keeping feature tracks; a hard reset destroys and recreates the estimator. A 30 Hz health monitor issues hard resets on estimator-health codes (bad covariance, sustained low quality, feature starvation, velocity-uncertainty breaches), never on transport warnings. The docs warn that dynamic init and soft reset can cause a jump discontinuity.

## Key takeaways

- Vendor VIO recovery restarts the estimator in a new frame; it does not relocalize against a prior map
- Reset jumps are expected downstream, so the autopilot side must handle reset_counter

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `modalai`, `voxl`, `openvins`, `vio-reset`, `docs`

## Related

- part_of: [VOXL OpenVINS server](../../catalog/resources/modalai-voxl-open-vins-server-docs.md)

_Indexed by lane(s): loop-57_
