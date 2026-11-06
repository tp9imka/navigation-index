# Shield AI Hivemind autonomy stack

`res:shield-ai-hivemind` - product - <https://insideunmannedsystems.com/the-hivemind-working-toward-resilient-intelligent-teams/>

**By:** Shield AI - **Year:** 2024 - **Level:** intermediate - **Access:** open

Hivemind is Shield AI's onboard autonomy software, flown on its V-BAT and on partner aircraft. In an interview the CTO describes a state-estimation framework fusing visual, EO/IR and inertial observations so the aircraft keeps operating without GNSS or comms.

## Key takeaways

- Vendor description: multi-sensor state estimation for GNSS-denied and comms-denied flight
- No published accuracy numbers found
- ViDAR (acquired with Sentient Vision, 2024) is an EO/IR detection product, not a navigation source

## Deep dives

- [gnss-denied-nav-products](../../docs/landscape/gnss-denied-nav-products.md) (landscape)

**Concepts:** [Visual(-inertial) odometry](../concepts/vio.md), [Sensor fusion and state estimation](../concepts/sensor-fusion.md), [Assured / resilient PNT](../concepts/assured-pnt.md), [Swarms and multi-agent navigation](../concepts/multi-agent.md)

**Tags:** `landscape`, `shield-ai`, `v-bat`, `vendor-claim`

## Related

- alternative_to: [OpenVINS](../repos/rpng__open_vins.md)
- alternative_to: [cuVSLAM](../repos/nvidia-isaac__cuvslam.md)
- alternative_to: [GTSAM](../repos/borglab__gtsam.md)

_Indexed by lane(s): landscape_
