# Mid-Air

<!-- about: res:midair-synthetic-drone-dataset -->

Synthetic low-altitude quadcopter flights from the University of Liege (Fonder and Van Droogenbroeck, CVPR Workshops 2019). Each trajectory is rendered under several weather and season setups, with simulated IMU and GPS alongside dense vision ground truth. One of few public sets that pairs drone imagery with a (simulated) GPS stream.

| Field | Value |
|---|---|
| Platform | Simulated quadcopter, extremely low altitude |
| Environment | 3 environment maps; 4 weather setups and 3 seasons (site also says "7 climates") |
| Sensors and rates | 3 RGB cameras (left, right, down per the data layout) at 25 Hz, 90 degree FOV; accelerometer and gyroscope 100 Hz; GPS 1 Hz with GDOP/PDOP/HDOP/VDOP and satellite count (tech specs page) |
| Ground truth | Simulator: poses, depth, stereo disparity, surface normals, semantic segmentation |
| Size | Not stated; the download form shows a "volume selected" counter only. Not verified |
| License | CC BY-NC-SA 4.0; commercial use needs a separate license from the authors |
| Format | HDF5 sensor records + zipped image streams (JPEG RGB, 16-bit float PNG depth/disparity, PNG seg/normals) |
| Index | [Mid-Air](../../catalog/resources/midair-synthetic-drone-dataset.md) |

## What's in it

- 54 trajectories of equal length, rendered per climate => over 420,000 training frames, 79 minutes of distinct flight from more than 5 hours of flight records (homepage).
- A benchmark test set for robustness (size not stated).
- Initial accelerometer and gyroscope bias estimates per trajectory.

## Download

No public file URLs. The flow is: fill the form at https://midair.ulg.ac.be/download.html (select streams, trajectories, climates, test sets), give an email, receive `download_config.txt` by mail, then:

```bash
wget --content-disposition -x -nH -i download_config.txt
find . -name "*.zip" -execdir unzip -o {} \;   # unzip in place, per the page
```

Plan a day for the email round trip. Files downloaded before 6 Sep 2019 were patched and must be re-fetched.

## Loading and tooling

- Example scripts: https://github.com/montefiore-ai/midair-dataset (not in the index).
- HDF5 via `h5py`; images are referenced by path from the HDF5 tree.

```python
import h5py
f = h5py.File('<climate_setup>/sensor_records.hdf5', 'r')
traj = f[list(f.keys())[0]]                      # trajectory_<i>
gt = traj['groundtruth/position'][:]             # 100 Hz
acc, gyr = traj['imu/accelerometer'][:], traj['imu/gyroscope'][:]
gps = traj['gps/position'][:]                    # 1 Hz
left = traj['camera_data/color_left'][:]         # relative image paths, 25 Hz
```

Layout per the data organization page: one folder per climate setup with `color_left/`, `color_right/`, `color_down/`, `depth/`, ... `trajectory_<i>/<j>.jpg|png`, and `sensor_records.hdf5`. Not opened here.

## Hackathon fit

- Idea 18 (visual geolocalization fused with VO) and GNSS-outage demos: has synchronized GPS + IMU + down camera, so you can blank GPS and show VO/IMU holdover against perfect truth.
- Idea 5 (INS holdover budget): simulated IMU with bias, but noise model undocumented.
- Weather robustness of a learned depth or VPR model.

## Pitfalls

- Email-gated download with unknown size; request early.
- Simulated GPS and IMU noise models are not documented on the specs page.
- Non-commercial license.
- Synthetic imagery; sim-to-real gap.

## Sources

- https://midair.ulg.ac.be/ (scale, climates, license)
- https://midair.ulg.ac.be/tech_specs.html (25 Hz cameras, 100 Hz IMU, 1 Hz GPS, file formats)
- https://midair.ulg.ac.be/download.html (form + emailed config + wget command)
