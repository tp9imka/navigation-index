# Airborne Magnetic Anomaly Navigation with Neural-Network-Augmented Online Calibration

`res:hager-2026-magnav-nn-online-calibration` - paper - <https://arxiv.org/abs/2603.08265>

**By:** Antonia Hager, Sven Nebendahl, Alexej Klushyn, Jasper Krauser, Torleiv H. Bryne, Tor Arne Johansen - **Year:** 2026 - **Level:** advanced - **Access:** open

Published in the Journal of Guidance, Control, and Dynamics (2026). A 'cold-start' MagNav EKF that estimates kinematic states, Tolles-Lawson coefficients and the weights of a residual neural network in flight, so no calibration flight or pre-training is needed. Validated on the MagNav Challenge dataset.

## Key takeaways

- No prior calibration flight
- EKF update equivalent to online natural-gradient training
- Physics model first, NN only for residuals

**Concepts:** [Magnetic anomaly navigation](../../catalog/concepts/magnetic-nav.md), [Sensor calibration](../../catalog/concepts/calibration.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `magnav`, `online-calibration`, `neural-network`, `ekf`

## Related

- uses: [MagNav Challenge flight dataset (Zenodo)](../../catalog/resources/magnav-zenodo-dataset.md)

_Indexed by lane(s): backlog_
