# Nonlinear Kalman filtering techniques for terrain-aided navigation

`res:hostetler-andreas-1983-sitan` - paper - <https://doi.org/10.1109/TAC.1983.1103232>

**By:** Larry D. Hostetler, Ronald D. Andreas - **Year:** 1983 - **Level:** advanced - **Access:** paywalled

IEEE TAC 28(3) paper from Sandia (the SITAN line of work) on updating an INS with radar terrain-clearance measurements. It compares an EKF using local terrain slopes, a stochastic linearization fitting a least-squares plane to the terrain, and a bank of parallel reduced-order filters for large initial position uncertainty.

## Key takeaways

- Sequential (Kalman) terrain aiding, unlike batch TERCOM
- Terrain linearization is the core difficulty
- Parallel filter bank for acquisition

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `sitan`, `terrain-aided-navigation`, `ekf`, `radar-altimeter`, `history`

_Indexed by lane(s): backlog_
