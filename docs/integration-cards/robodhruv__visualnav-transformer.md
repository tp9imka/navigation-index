# GNM / ViNT / NoMaD (visualnav-transformer) - integration card
<!-- about: repo:robodhruv/visualnav-transformer -->
Pretrained visual navigation policies that drive a ground robot from a single RGB camera along a recorded image "topological map" (no metric map, no GNSS), plus NoMaD undirected exploration; ROS 1 deployment and PyTorch training code.

| | |
|---|---|
| Install | No PyPI package. README (`deployment/`): ROS Noetic, `sudo apt-get install ros-noetic-usb-cam ros-noetic-joy`, `conda env create -f deployment/deployment_environment.yaml && conda activate vint_deployment`, `pip install -e train/` (installs package `vint_train` 0.1.0 from `train/setup.py`), then `git clone` real-stanford/diffusion_policy and `pip install -e diffusion_policy/`. Training: `train/train_environment.yml` per README. Only tag: `code_release` (2023-10-06). |
| Runs on | Tested on a LoCoBot with Ubuntu 20.04 and Jetson Orin Nano (README). NVIDIA GPU expected (conda env pins Python 3.8.5, `cudatoolkit`, `diffusers==0.11.1`). Others report Jackal, Tello, Unitree A1, TurtleBot2 and CARLA (README). |
| Inputs | Camera images on `/usb_cam/image_raw` (`deployment/src/topic_names.py`), resized per model config; a topomap = folder of images `deployment/topomaps/images/<dir>/0..N` created from a rosbag at `--dt 1` s spacing; model choice from `deployment/config/models.yaml` (`vint`, `late_fusion`, `gnm`, `nomad`). |
| Outputs | `/waypoint` (std_msgs/Float32MultiArray; 2 or 4 values: dx, dy and optionally heading as cos/sin, robot frame) and `/topoplan/reached_goal` (Bool) from `navigate.py`; `pd_controller.py` converts the waypoint to geometry_msgs/Twist on `vel_navi_topic` (default `/cmd_vel_mux/input/navi`), clipped to `max_v` 0.2 m/s and `max_w` 0.4 rad/s (`config/robot.yaml`). |
| Key API / entry points | Scripts in `deployment/src/`: `record_bag.sh <bag>`, `create_topomap.sh <name> <bag>` (`create_topomap.py --dt 1 --dir <dir>`), `navigate.sh "--model <m> --dir <topomap>"` (`navigate.py` flags `--model` default `nomad`, `--waypoint` 2, `--dir`, `--goal-node -1`, `--close-threshold 3`, `--radius 4`, `--num-samples 8`), `exploration.sh "--model nomad"` (`explore.py`), `pd_controller.py`, `joy_teleop.py`. Training: `python train.py -c config/<vint|gnm|nomad>.yaml` in `train/`; data prep `process_bags.py`, `process_recon.py`. |
| Time to first result | Estimate: 2-4 h to get the conda env, weights and a recorded topomap running on a ROS 1 robot or sim; inference-only on a laptop GPU against a bag is faster. |
| License | Code `LICENSE`: MIT. Weights: Google Drive folder linked from the README, no separate licence stated. Training data (RECON, TartanDrive, SCAND, GoStanford2, SACSoN/HuRoN, etc.) each carry their own terms; check before redistributing fine-tuned weights. |

## Minimal usage
Not run. From README, run inside `deployment/src/` with weights saved to `deployment/model_weights/` (`nomad.pth`, `vint.pth`, `gnm_large.pth` as named in `models.yaml`).

```sh
./record_bag.sh run1                       # teleop the route once, record /usb_cam/image_raw
./create_topomap.sh route1 run1.bag        # one node image per second of bag
./navigate.sh "--model nomad --dir route1" # follows the route, publishes /waypoint, pd_controller drives
./exploration.sh "--model nomad"           # undirected exploration (NoMaD only)
```

## Wiring it into a nav stack
- It is a learned local policy with image-goal localization along a route. For GNSS-denied route repeat it replaces the metric map; pair with a metric odometry source ([Isaac ROS Visual SLAM](./nvidia-isaac-ros__isaac_ros_visual_slam.md), [OpenVINS](./rpng__open_vins.md)) only for safety monitoring, the policy itself does not consume odometry.
- Swap `pd_controller.py` output topic in `config/robot.yaml` to `/cmd_vel` or to [MAVROS](./mavlink__mavros.md) `setpoint_velocity/cmd_vel_unstamped` for a rover in GUIDED/OFFBOARD.
- ROS 2: no port in this repo; bridge with ros1_bridge or rewrite the thin `rospy` nodes.
- For aerial or long-range absolute fixes use satellite-image matching instead (see [WildNav](./tiers__wildnav.md), [AnyLoc](./anyloc__anyloc.md)).

## Gotchas
- `navigate.py --model` help says "only nomad is supported", while the README shows `--model <model_name>` for any entry in `models.yaml`. Use `nomad` for `navigate.sh` and `exploration.sh`.
- `deployment_environment.yaml` has `cudatoolkit=11.` (truncated version string); conda may resolve oddly. Pin a concrete `cudatoolkit=11.x` that matches your driver.
- Diffusion policy dependency is a separate unpinned git clone; `diffusers==0.11.1` is old and will clash with newer torch.
- Issue #11 thread: users deploying NoMaD/ViNT on their own robots report frequent collisions even after fine-tuning; topomaps with few nodes made it worse. Budget time for tuning `--close-threshold`, `--radius` and speed limits.
- Issue #19: closest-node index jitters while the robot is stationary.
- No activity since 2024-09 (last push); ROS 1 only.
- Ground robots only in the shipped config; speeds are deliberately low (0.2 m/s).

## Alternatives
- [OMPL](./ompl__ompl.md) + a metric map - classical planning when you have a map and pose.
- [TARE](./caochao39__tare_planner.md) - geometric exploration with LiDAR rather than learned exploration from RGB.
- [GRID playground](../../catalog/repos/genrobo__grid-playground.md) - foundation-model perception in an AirSim-derived sim if you need to prototype without a robot.

Sources: `README.md`, `LICENSE`, `train/setup.py`, `deployment/deployment_environment.yaml`, `deployment/config/models.yaml`, `deployment/config/robot.yaml`, `deployment/src/topic_names.py`, `deployment/src/navigate.py`, `deployment/src/pd_controller.py`, tag `code_release`, issues #10 #11 #13 #19 #27 #36 #44 (github.com/robodhruv/visualnav-transformer).
