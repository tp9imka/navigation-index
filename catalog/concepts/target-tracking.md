# Tracking and data association

`concept:target-tracking`

Multi-target tracking, MHT/JPDA, track fusion (for nav-relevant awareness, not weapon guidance).

## Samples (1)

- [Stone Soup radar tracking of two UAVs with JPDA and OSPA](../samples/stone-soup-tracking.md) - Simulates two small UAVs observed by a noisy bearing/range radar with clutter and tracks them with Stone Soup's Extended Kalman filter and JPDA data association.

## Repositories (15)

- [Ultralytics YOLO](../repos/ultralytics__ultralytics.md) - fit: high - Widely used Python package for YOLO-family detection, segmentation and tracking with training, export to edge runtimes and built-in trackers.
- [BoxMOT](../repos/mikel-brostrom__boxmot.md) - fit: high - Pluggable collection of modern multi-object trackers (ByteTrack, BoT-SORT, OC-SORT, StrongSORT and others) for detector outputs, in Python and C++.
- [FilterPy](../repos/rlabbe__filterpy.md) - fit: high - Python library of Kalman filters (linear, extended, unscented, ensemble), smoothers, particle filtering helpers and related estimators.
- [Anti-UAV](../repos/zhaoj9014__anti-uav.md) - fit: high - Official repository of the Anti-UAV challenge and benchmark for detecting and tracking UAVs in RGB and thermal infrared video, with dataset links (Anti-UAV300/410/600) and baselines.
- [Stone Soup](../repos/dstl__stone-soup.md) - fit: high - Open-source Python framework from UK Dstl and partners for developing, running and evaluating tracking and state estimation algorithms: Kalman variants, particle filters, JPDA, MHT, GM-PHD, track management and metrics.
- [pyais](../repos/m0r13n__pyais.md) - fit: high - Python library for decoding and encoding AIS NMEA sentences (AIVDM/AIVDO), including multi-part messages and streaming from sockets or files.
- [ByteTrack](../repos/foundationvision__bytetrack.md) - fit: medium - ECCV 2022 multi-object tracker that associates both high- and low-confidence detections, improving tracking through occlusion.
- [motpy](../repos/wmuron__motpy.md) - fit: medium - Simple Python library for tracking-by-detection multi-object tracking with Kalman filters and IoU/feature association.
- [traffic](../repos/xoolive__traffic.md) - fit: medium - Toolbox for processing and analyzing air traffic trajectories: OpenSky access, filtering, resampling, airspace intersection and visualization.
- [ASTERIX decoder (Croatia Control)](../repos/croatiacontrolltd__asterix.md) - fit: medium - C/C++ and Python decoder for EUROCONTROL ASTERIX surveillance data from files, stdin or network, with XML category definitions and JSON/XML output.
- [UAV Detection and Tracking Benchmark](../repos/kostadinovshalon__uavdetectiontrackingbenchmark.md) - fit: medium - Code and configs for benchmarking drone detection and tracking across Anti-UAV, Drone-vs-Bird and MAV-VID datasets, including format converters.
- [OpenCPN radar_pi](../repos/opencpn-radar-pi__radar_pi.md) - fit: medium - OpenCPN plugin that connects to Navico and some Garmin and Raymarine marine radars and overlays radar imagery and ARPA-style targets on the chart.
- [VIMMJIPDA tracker interface](../repos/ntnu-itk-autonomous-ship-lab__vimmjipda.md) - fit: medium - Interface that runs the VIMMJIPDA multi-target tracker (visibility, interacting multiple models, JIPDA) inside the NTNU colav-simulator; open-sourced November 2025.
- [K-Radar](../repos/kaist-avelab__k-radar.md) - fit: low - 4D radar dataset and benchmark for object detection in diverse weather, with raw 4D tensors, lidar, cameras and GNSS.
- [pyMHT](../repos/erikliland__pymht.md) - fit: low - Track-oriented multi-hypothesis multi-target tracker in Python developed for maritime radar tracking research.

## Documents, talks, courses, datasets (8)

- [Anti-UAV Challenge](../resources/anti-uav-challenge-site.md) - competition - Site for the recurring Anti-UAV workshop and challenge with tracks for single and multiple UAV tracking in infrared video.
- [Anti-UAV: A Large Multi-Modal Benchmark for UAV Tracking](../resources/anti-uav-benchmark-paper.md) - paper - Introduces the Anti-UAV RGB and thermal infrared video benchmark for UAV tracking and an evaluation protocol.
- [Kalman and Bayesian Filters in Python](../resources/labbe-kalman-bayesian-filters-python.md) - book - Free interactive book as Jupyter notebooks: g-h filters, discrete Bayes, univariate and multivariate Kalman filters, EKF, UKF, particle filters and smoothers, all with runnable code built on the companion FilterPy librar
- [Kalman Filter Tutorial (kalmanfilter.net)](../resources/kalmanfilter-net-tutorial.md) - blog - Free web tutorial deriving the Kalman filter through worked numerical examples (alpha-beta filter, 1D and multidimensional KF, EKF, UKF), written for engineers who want the equations without heavy theory.
- [Multi-Object Tracking for Automotive Systems (edX)](../resources/chalmers-multi-object-tracking.md) - course - edX course on single- and multi-object tracking: data association, GNN/JPDA/MHT, random finite sets and PMBM filters, with Matlab assignments.
- [Stone Soup documentation and tutorials](../resources/stone-soup-docs.md) - doc - Official docs for the Stone Soup tracking framework with step-by-step tutorials from a single-target Kalman filter through data association (PDA, JPDA), multi-hypothesis tracking, GM-PHD, track initiation/deletion, senso
- [Stone Soup: No Longer Just an Appetiser](../resources/dstl-stone-soup-v1-fusion2023.md) - paper - FUSION 2023 paper announcing Stone Soup version 1.0, describing the framework's stable architecture and its use across the tracking community.
- [Understanding Sensor Fusion and Tracking (MATLAB Tech Talks)](../resources/mathworks-understanding-sensor-fusion-tracking.md) - video - Short video series on sensor fusion for autonomous systems: what sensor fusion is, IMU/magnetometer orientation estimation, fusing GPS and IMU for pose with an asynchronous EKF, single- and multi-object tracking, and tra

