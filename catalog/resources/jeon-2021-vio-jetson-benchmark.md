# Run Your Visual-Inertial Odometry on NVIDIA Jetson: Benchmark Tests on a Micro Aerial Vehicle

`res:jeon-2021-vio-jetson-benchmark` - paper - <https://arxiv.org/abs/2103.01655>

**By:** Jinwoo Jeon, Sungwook Jung, Eungchang Lee, Duckyu Choi, Hyun Myung - **Year:** 2021 - **Level:** intermediate - **Access:** open

Runs seven VO/VIO systems (VINS-Mono, VINS-Fusion, Kimera, ALVIO, Stereo-MSCKF, ORB-SLAM2 stereo, ROVIO) on Jetson TX2, Xavier NX and AGX Xavier with a D435i at 30 Hz and a Pixhawk 4 mini IMU at 100 Hz, and reports accuracy, CPU and memory. Releases the KAIST VIO dataset.

## Key takeaways

- ROVIO had the lowest CPU use on every Jetson; all others used more than one core
- Kimera had markedly higher memory use, most visible on TX2
- VINS-Fusion CPU build did not run on TX2; the GPU variant was used
- CPU/memory values are only in a figure, not in tables; read them from Fig. 3

**Concepts:** [Visual(-inertial) odometry](../../catalog/concepts/vio.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md), [Datasets and benchmarks](../../catalog/concepts/datasets-benchmarks.md)

**Tags:** `jetson`, `vio`, `benchmark`, `uav`, `kaist`

## Related

- evaluates: [ROVIO](../../catalog/repos/ethz-asl__rovio.md)
- evaluates: [Kimera-VIO](../../catalog/repos/mit-spark__kimera-vio.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_
