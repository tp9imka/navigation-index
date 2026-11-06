# Visual geo-localization (image-to-map)

`concept:visual-geolocalization`

Matching UAV/ground imagery to satellite orthophotos or maps for absolute position without GNSS.

## Samples (1)

- [Drone frame to orthophoto geolocalization with LightGlue](../samples/visual-geolocalization-lightglue.md) - Matches a nadir drone frame against a georeferenced satellite or orthophoto tile with SuperPoint + LightGlue, fits a MAGSAC homography with OpenCV, and maps the frame centre through the GeoTIFF geotransform to lat/lon.

## Repositories (37)

- [OpenDroneMap (ODM)](../repos/opendronemap__odm.md) - fit: high - Photogrammetry toolkit that turns aerial images into orthophotos, point clouds, 3D models and DEMs.
- [LightGlue-ONNX](../repos/fabio-sim__lightglue-onnx.md) - fit: high - ONNX export of SuperPoint/DISK + LightGlue feature matching with TensorRT and OpenVINO support.
- [AnyLoc](../repos/anyloc__anyloc.md) - fit: high - Universal visual place recognition using foundation-model (DINOv2) features with VLAD/GeM aggregation, working across aerial, underwater, indoor and outdoor domains without task-specific training.
- [UAV-VisLoc dataset](../repos/intellisensing__uav-visloc.md) - fit: high - Large-scale dataset of real UAV flight imagery with satellite reference maps for UAV visual localization across varied terrain.
- [WildNav](../repos/tiers__wildnav.md) - fit: high - Python pipeline that localizes a drone by matching its downward camera frames against georeferenced satellite map tiles with SuperGlue, then converts the best match into GPS coordinates.
- [AnyVisLoc benchmark](../repos/uav-avl__benchmark.md) - fit: high - Benchmark and code for UAV absolute visual localization under low-altitude, multi-view (oblique) observation, comparing retrieval and matching combinations against aerial and satellite reference maps.
- [pystac-client](../repos/stac-utils__pystac-client.md) - fit: high - Python client for searching STAC APIs (Earth Search, Planetary Computer and others) by area, time and properties.
- [VPR methods evaluation](../repos/gmberton__vpr-methods-evaluation.md) - fit: high - Wrapper exposing many state-of-the-art place recognition models behind one interface so you can switch models with one parameter.
- [visual_localization (GNSS-free UAV)](../repos/terbouchehacene__visual_localization.md) - fit: high - A cleaner reimplementation of the WildNav idea: match UAV images to satellite tiles with SuperPoint/SuperGlue-style matchers and estimate geographic position.
- [UAVLocalization (map retrieval + alignment)](../repos/hmf21__uavlocalization.md) - fit: high - Geo-localization system for aerial platforms that first retrieves the right satellite map region with a deep descriptor and then aligns the drone orthophoto to it to extract coordinates; evaluated on reorganized public A
- [Satellite-thermal geo-localization](../repos/arplaboratory__satellite-thermal-geo-localization.md) - fit: high - IROS 2023 code for long-range UAV thermal geo-localization against satellite RGB imagery, using domain adaptation to bridge thermal and visible imagery; comes with the Boson-nighttime dataset.
- [GeoAnchor](../repos/yusufgunel__geoanchor.md) - fit: high - Recent project fusing visual odometry with satellite-map matching in a particle filter for GNSS-denied UAV flight, with an explicit notion of when the map match should not be trusted; evaluated on UAV-VisLoc flights and 
- [sentinelhub-py](../repos/sentinel-hub__sentinelhub-py.md) - fit: medium - Python client for Sentinel Hub and Copernicus Data Space services to search, download and process Sentinel and other satellite imagery.
- [University-1652 baseline](../repos/layumi__university1652-baseline.md) - fit: medium - Dataset and baseline code for drone-based geo-localization across drone, satellite and ground views of university buildings worldwide.
- [CosPlace](../repos/gmberton__cosplace.md) - fit: medium - CVPR 2022 large-scale visual geo-localization treating place recognition as classification over geographic cells.
- [DenseUAV](../repos/dmmm1997__denseuav.md) - fit: medium - Dataset and baseline (TIP 2023) for UAV self-positioning in low-altitude urban environments using dense sampling of drone and satellite views.
- [Sample4Geo](../repos/skyy93__sample4geo.md) - fit: medium - Cross-view geo-localization training with hard negative sampling, reporting strong results on drone-satellite and street-satellite benchmarks with a simple contrastive setup.
- [Aerial Template Matching](../repos/m-hamza-mughal__aerial-template-matching.md) - fit: medium - Classical template-matching approach for locating an aerial image inside a larger reference image, built on OpenCV.
- [SUES-200 benchmark](../repos/reza-zhu__sues-200-benchmark.md) - fit: medium - Multi-height, multi-scene drone-satellite cross-view dataset and evaluation code, capturing drone imagery at several altitudes.
- [AerialVL](../repos/hmf21__aerialvl.md) - fit: medium - Visual geo-localization dataset and code designed for aerial vehicles.
- [STHN](../repos/arplaboratory__sthn.md) - fit: medium - Deep homography estimation for aligning UAV thermal images to satellite maps (RA-L 2024), refining coarse geo-localization into precise alignment.
- [GNSS-Denied UAV Geolocalization (terrain-weighted)](../repos/yfs90__gnss-denied-uav-geolocalization.md) - fit: medium - Code and demos for a UAV geolocalization system that combines image matching, visual odometry and a terrain-weighted constraint optimization, intended to work day and night.
- [VPAIR](../repos/aervisloc__vpair.md) - fit: medium - Repo for VPAIR, an aerial visual place recognition dataset matching low-altitude flight imagery to reference orthophotos.
- [UASTHN](../repos/arplaboratory__uasthn.md) - fit: medium - ICRA 2025 extension of STHN that adds uncertainty estimation to satellite-thermal homography, so the system can say when a fix is unreliable.
- [SCC-Loc](../repos/floralhercules__scc-loc.md) - fit: medium - Zero-shot UAV thermal geo-localization against satellite imagery without thermal-specific training.
- [UVDAR](../repos/ctu-mrs__uvdar_core.md) - fit: medium - Mutual relative localization for UAV swarms using blinking ultraviolet LEDs and UV-sensitive cameras, from CTU MRS.
- [U2S-CVGL (scale-aware UAV-to-satellite)](../repos/uav-avl__u2s-cvgl.md) - fit: medium - Scale-aware cross-view geo-localization method for matching UAV views to satellite imagery when the altitude-driven scale difference is unknown.
- [SatNav](../repos/eku127__satnav.md) - fit: medium - Scalable benchmark and platform for long-horizon UAV vision-language navigation built from satellite imagery (NeurIPS 2026 Datasets track).
- [UAVision](../repos/arborisers__uavision.md) - fit: medium - Map-matching-based visual localization software for UAVs in GNSS-denied settings, shipped with a GUI front end and demo.
- [TERCOM-python (TERCOM + DSMAC)](../repos/ayushmankumar7__tercom-python.md) - fit: medium - OpenCV-based demo of map-based navigation combining terrain contour matching with scene-matching area correlation.
- [Visual Locator](../repos/rtwotwo__visual-locator.md) - fit: medium - Absolute drone positioning by image retrieval (SelaVPR-style ViT features) over cropped satellite tiles followed by registration with SIFT+RANSAC or SuperPoint+SuperGlue.
- [KF-HomoVAL](../repos/lizhipro__kf-homoval.md) - fit: medium - 6-DoF absolute visual localization for UAVs built on deep homography estimation between the drone view and a reference map, smoothed with a Kalman filter.
- [CrossLoc](../repos/topo-epfl__crossloc.md) - fit: low - CVPR 2022 cross-modal visual representation learning for absolute camera localization of aerial imagery, trained largely on synthetic data rendered from geodata.
- [LPN (Local Pattern Network)](../repos/wtyhub__lpn.md) - fit: low - PyTorch implementation of a cross-view geo-localization method that pools features in rings around the image center to capture contextual local patterns.
- [JointLoc](../repos/luoxubo__jointloc.md) - fit: low - Real-time visual localization framework for planetary UAVs that jointly uses relative and absolute pose estimation against orbital maps.
- [Seasonally invariant transform (visual TRN)](../repos/connorlee77__seasonally-invariant-image-transform.md) - fit: low - Training code for a learned image transform that makes aerial imagery robust to seasonal appearance change for visual terrain-relative navigation.
- [CELL](../repos/panagiotisq__cell.md) - fit: low - Event camera localization in prior lidar maps with confidence weighting.

## Documents, talks, courses, datasets (21)

- [A Review on Deep Learning for UAV Absolute Visual Localization](../resources/couturier-review-dl-uav-avl-2024.md) - paper - Survey of deep-learning approaches to UAV absolute visual localization against reference maps since 2019, in the journal Drones.
- [A Robust Approach to Vision-Based Terrain-Aided Localization](../resources/ion-webinar-navon.md) - talk - Vision-based terrain-aided localization for aircraft, matching onboard imagery against terrain/map references as a GNSS-independent position source.
- [AnyLoc: Towards Universal Visual Place Recognition](../resources/anyloc-universal-vpr-2023.md) - paper - Shows that unsupervised aggregation of foundation-model (DINOv2) features gives place recognition that generalizes across domains including aerial imagery, without VPR-specific training.
- [Exploring the best way for UAV visual localization under Low-altitude Multi-view Observation Condition: a Benchmark](../resources/anyvisloc-uav-localization-benchmark-2025.md) - paper - Builds a benchmark for low-altitude, oblique-view UAV absolute visual localization and systematically compares retrieval, matching and refinement choices.
- [Image Matching: Local Features & Beyond (CVPR workshop)](../resources/cvpr-image-matching-workshop.md) - talk - Recurring CVPR workshop and Kaggle challenge on feature matching and structure-from-motion, with invited talks and recordings, covering the matchers used in visual geolocalization and VIO.
- [Long-range UAV Thermal Geo-localization with Satellite Imagery](../resources/thermal-geolocalization-iros-2023.md) - paper - Matches night-time UAV thermal imagery to satellite RGB maps using domain adaptation to cope with scarce paired thermal-satellite data; releases code and a nighttime dataset.
- [Long-Term Visual Localization benchmark](../resources/visual-localization-benchmark.md) - competition - Benchmark and workshop series for 6-DoF visual localization under changing conditions (day/night, seasons), with standard datasets and an evaluation server.
- [Photogrammetry I & II](../resources/stachniss-photogrammetry-i-ii.md) - lecture-series - Recorded two-semester photogrammetry course (2015/16 playlist): camera models, direct linear transform, projective geometry, epipolar geometry, bundle adjustment, and image-based 3D reconstruction.
- [Sample4Geo: Hard Negative Sampling For Cross-View Geo-Localisation](../resources/sample4geo-2023.md) - paper - Shows that a simple contrastive setup with careful hard-negative sampling performs strongly on cross-view geo-localization benchmarks.
- [STHN: Deep Homography Estimation for UAV Thermal Geo-localization with Satellite Imagery](../resources/sthn-thermal-homography-2024.md) - paper - Refines thermal-to-satellite localization with learned homography estimation for precise alignment.
- [SUES-200: A Multi-height Multi-scene Cross-view Image Benchmark Across Drone and Satellite](../resources/sues-200-benchmark-2022.md) - paper - Drone-satellite benchmark with imagery at several flight heights across varied scenes.
- [The Zurich Urban Micro Aerial Vehicle Dataset](../resources/zurich-urban-mav-dataset.md) - dataset - Low-altitude urban MAV flight over streets with camera, IMU and GPS plus Google Street View imagery for appearance-based localization.
- [UASTHN: Uncertainty-Aware Deep Homography Estimation for UAV Satellite-Thermal Geo-localization](../resources/uasthn-uncertainty-thermal-2025.md) - paper - Adds uncertainty estimation to satellite-thermal homography so a navigation filter can weight or reject visual fixes.
- [UAV-VisLoc: A Large-scale Dataset for UAV Visual Localization](../resources/uav-visloc-dataset-2024.md) - paper - Introduces a dataset of real UAV flight images paired with satellite maps over varied terrain for evaluating UAV visual localization.
- [UAVs: ISR, Deterrence and War (IISS Strategic Dossier)](../resources/iiss-uavs-isr-deterrence-war-2026.md) - report - IISS dossier on military UAV use, noting that GNSS is often effectively unavailable near the front line in Ukraine and that visual scene-matching navigation is a growing response.
- [Ukraine's Autonomous Killer Drones Defeat Electronic Warfare](../resources/ieee-spectrum-ukraine-drones-ew-2025.md) - blog - Reporting on how Ukrainian drone developers respond to pervasive jamming of radio links and satellite navigation, including onboard optical navigation that keeps the drone flying after links are lost.
- [Ukraine's DefTech at the End of 2025: From Drone Mass to Systems Warfare](../resources/ngrn-ukraine-deftech-2025.md) - blog - Analysis of Ukraine's defence-tech ecosystem at the end of 2025, noting that GNSS-denied operation is now the norm and expecting broad adoption of radio-beacon, visual and fused alternative navigation in 2026.
- [Ukrainian Drones Use Vermeer Optical Navigation System](../resources/militarnyi-vermeer-optical-nav-2025.md) - blog - Ukrainian defense outlet reporting that a US company's optical (visual) navigation system is being integrated into Ukrainian reconnaissance and strike drones.
- [Ukrainian drones use Vermeer optical navigation system](../resources/militarnyi-vermeer-optical-navigation.md) - blog - Ukrainian defense outlet report on a visual positioning system integrated on drones used by Ukrainian forces for operation when GNSS is jammed.
- [University-1652: A Multi-view Multi-source Benchmark for Drone-based Geo-localization](../resources/university-1652-benchmark-2020.md) - paper - Introduces the drone/satellite/ground benchmark that most drone cross-view geo-localization work evaluates on.
- [Vision-based GNSS-Free Localization for UAVs in the Wild](../resources/wildnav-gnss-free-uav-localization-2022.md) - paper - Proposes matching drone camera frames to open satellite imagery with learned feature matching to get absolute position without GNSS, evaluated on flights over non-urban areas.

