# A Benchmark Comparison of Monocular Visual-Inertial Odometry Algorithms for Flying Robots

`res:delmerico-scaramuzza-2018-vio-benchmark-flying-robots` - paper - <https://rpg.ifi.uzh.ch/docs/ICRA18_Delmerico.pdf>

**By:** Jeffrey Delmerico, Davide Scaramuzza - **Year:** 2018 - **Level:** intermediate - **Access:** open

ICRA 2018. Runs MSCKF, OKVIS, ROVIO, VINS-Mono, SVO+MSF and SVO+GTSAM on EuRoC across a laptop, an Intel NUC, an UP Board and an ODROID, comparing accuracy, CPU and memory. Only the author slides were read here: SVO+MSF fastest but least accurate, OKVIS consistent across platforms, ROVIO could not run on the UP Board.

## Key takeaways

- Accuracy rankings change with the onboard computer
- Pick the VIO for the compute you will actually fly

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `vio-benchmark`, `euroc`, `embedded`, `icra`

## Related

- uses: [EuRoC MAV Dataset](../../catalog/resources/ethz-euroc-mav-dataset.md)
- evaluates: [ROVIO](../../catalog/repos/ethz-asl__rovio.md)
- evaluates: [MSCKF_VIO](../../catalog/repos/kumarrobotics__msckf_vio.md)

_Indexed by lane(s): close-area-localization_
