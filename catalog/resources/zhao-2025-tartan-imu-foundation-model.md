# Tartan IMU: A Light Foundation Model for Inertial Positioning in Robotics

`res:zhao-2025-tartan-imu-foundation-model` - paper - <https://openaccess.thecvf.com/content/CVPR2025/html/Zhao_Tartan_IMU_A_Light_Foundation_Model_for_Inertial_Positioning_in_CVPR_2025_paper.html>

**By:** Shibo Zhao, Sifan Zhou, Raphael Blanchard, Yuheng Qiu, Wenshan Wang, Sebastian Scherer - **Year:** 2025 - **Level:** advanced - **Access:** open

CVPR 2025. Pretrains one inertial model on more than 100 hours of data from four platform types, then adapts per platform with LoRA (1.1 M trainable parameters) and online test-time adaptation.

## Key takeaways

- Reported 36% ATE improvement over specialized models
- Online adaptation reported at 200 FPS
- Public release is the LSTM model; the Transformer core is not included per the README

**Concepts:** [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `imu-foundation-model`, `lora`, `cvpr-2025`

## Related

- has_code: [TartanIMU](../../catalog/repos/superxslam__tartanimu.md)

## Referenced by

- [Differentiators scan: what to bring besides satellite matching](../../docs/differentiators-scan.md) (mentions)

_Indexed by lane(s): nav-differentiators_
