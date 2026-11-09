# JointLoc: A Real-time Visual Localization Framework for Planetary UAVs Based on Joint Relative and Absolute Pose Estimation

`res:luo-2024-jointloc-planetary-uav` - paper - <https://arxiv.org/abs/2405.07429>

**By:** Xubo Luo, Xue Wan, Yixing Gao, Yaolin Tian, Wei Zhang, Leizheng Shu - **Year:** 2024 - **Level:** advanced - **Access:** open

IROS 2024 (per the repo README); arXiv 2405.07429 full text read through an HTML summary. Fuses satellite-map absolute 2-DoF pose with relative 6-DoF visual SLAM on Mars-like terrain. Notes that absolute localization on every frame costs too much compute, tests fixed intervals of 1, 10, 50 and 100 frames and picks 10; match confidence (SSIM x mean match degree) sets the next search radius. Desktop RTX 2080 Ti.

## Key takeaways

- A UAV paper that meets the fix-rate vs compute trade-off and answers it with a hand-tuned fixed interval
- Interval 50 gave too much error; 100 broke SLAM initialization
- Area prediction cut absolute localization from about 793 ms to 82 ms on one terrain

**Concepts:** [Visual geo-localization (image-to-map)](../../catalog/concepts/visual-geolocalization.md), [Visual SLAM](../../catalog/concepts/visual-slam.md), [Space and orbital navigation](../../catalog/concepts/space-nav.md)

**Tags:** `absolute-visual-localization`, `fix-rate`, `satellite-map`, `planetary-uav`

## Related

- has_code: [JointLoc](../../catalog/repos/luoxubo__jointloc.md)

_Indexed by lane(s): innovation-pa-scheduling_
