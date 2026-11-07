# Three selective offline starter bundles

Pick a bundle before downloading the broad [offline kit](../templates/offline-kit/README.md).
The runner is stdlib Python. It selects existing `prep.py` items plus explicit additions in
[`bundles.json`](../templates/offline-kit/bundles.json); all downloads use the existing cache and
fetchers. Copy the navigation-index checkout too: samples import their siblings and templates.
Do not copy a sample directory on its own.

| Bundle | What it runs | Cache and runtime requirements | Expected fresh output |
|---|---|---|---|
| `receiver-log` | [real-attack-replay](../samples/real-attack-replay/README.md), variant D: public recorded receiver logs; no transmissions | Stdlib Python; seven pinned VAARA `.ubx.xz` files, unpacked logs; no weights, Docker, pyubx2 or RTKLIB required | `replay.json` with all seven files and positive epoch counts, plus per-epoch CSV recordings |
| `vehicle-sim` | [golden-demo](../samples/golden-demo/README.md) v2: baseline and monitor flights in ArduPilot SITL, replayed visual matches | Docker engine; `nav-sitl-ardupilot:copter-4.6.3` built/saved for the host architecture; pymavlink 2.4.50 venv/wheels; committed `data/vgeo_table.json` | `navdash/summary.json`, `manifest.json`, and recorded truth/GNSS/fused/visual tracks |
| `vision` | [e2e-visual-nav-vpair](../samples/e2e-visual-nav-vpair/README.md): actual retrieval/matching twice, then fusion | VPAIR sample zip (861,249,439 bytes) and extracted renders/depth/query poses/images; pinned wheels and LightGlue source/wheel; **three checkpoints and DINOv2 source**; sample venv | New `frontend.json`, `frontend_yaw2.json`, fusion result/CSV/SVG and navdash tracks |

VAARA is pinned to source revision `51b5f9cca4af6894d264803cf0a070f6107272f8`.
It states no data license: fetch directly and retain provenance; this repository distributes no raw
VAARA recordings. VPAIR's README restricts its dataset to academic use, despite the broader Zenodo
tag. Read the existing [dataset card](dataset-cards/vpair.md) and
[weight licenses](model-weights-licenses.md) before sharing assets.

The vehicle selection uses a replay table of real matching on synthetic images and an oracle VIO
with noise. It is a simulation demonstration. The vision selection uses one short real flight,
recorded attitude, and a reference map tied to the same GNSS/INS truth. Its fault-free protection
level is not a general integrity guarantee. Keep these limits alongside any result.

## Prepare while online

From the checkout root:

```sh
python3 templates/offline-kit/bundle.py list
python3 templates/offline-kit/bundle.py plan receiver-log
python3 templates/offline-kit/bundle.py plan vehicle-sim
python3 templates/offline-kit/bundle.py plan vision
```

`plan` lists only the selected items, prerequisites, commands, known download bytes and items with
unknown sizes. Wheel, image and checkpoint sizes are unknown until downloaded; do not mistake
the known-byte subtotal for a total budget.

The receiver bundle needs no installation:

```sh
python3 templates/offline-kit/bundle.py prepare receiver-log --cache /Volumes/USB/navkit
python3 templates/offline-kit/bundle.py verify receiver-log --cache /Volumes/USB/navkit
python3 templates/offline-kit/bundle.py rehearse receiver-log --cache /Volumes/USB/navkit
```

For the heavy bundles, first create a venv using the interpreter you intend to use at the venue.
The vision sample's published environment was Python 3.12.14/macOS arm64, torch 2.15.0/MPS;
other platforms require their own rehearsal. Docker must be running for the vehicle bundle.

```sh
python3.12 -m venv .venv-vehicle
python3.12 -m venv .venv-vision
python3 templates/offline-kit/bundle.py prepare vehicle-sim --cache /Volumes/USB/navkit \
  --python "$PWD/.venv-vehicle/bin/python"
python3 templates/offline-kit/bundle.py prepare vision --cache /Volumes/USB/navkit \
  --python "$PWD/.venv-vision/bin/python"
```

Preparation downloads/builds only the selection, unpacks datasets, installs runtime packages from
cached wheels into the selected venv, and records actual installed versions. The LightGlue source
is pinned in the sample requirements; its wheel is built from the downloaded source with no
package index or isolated build downloads. The vision selection also caches pinned setuptools
and wheel packages so that this build can be repeated on the second laptop. Missing platform
wheels, partial preparation, missing tools, missing checkpoints or corrupt archives fail preparation.
The tool never installs sample packages into the global interpreter.

The vision bundle overrides the sample's headless OpenCV pin with `opencv-python==5.0.0.93`
and adds `matplotlib==3.11.2` to satisfy the pinned LightGlue package's dependency metadata.
It installs only the normal OpenCV distribution in the fresh vision venv; do not add
`opencv-python-headless` alongside it. This dependency-resolution correction has a metadata-only
offline resolver test; the heavy vision pipeline remains unverified in this change.

Choose a separate cache per Python minor version or target architecture. The wheel cache layout
is the existing `pip/<platform>/` layout, not a universal environment. Supported wheel targets are
`macos-arm64`, `linux-amd64` and `linux-arm64`; Docker builds are native to the preparing host.
Windows and cross-architecture Docker builds are not verified by these bundles.

The vision warm-up instantiates DINOv2 ViT-S/14, ALIKED `aliked-n16`, and the ALIKED LightGlue
matcher with `TORCH_HOME=<cache>/torch`. It requires:

- `torch/hub/checkpoints/dinov2_vits14_pretrain.pth`;
- `torch/hub/checkpoints/aliked-n16.pth`;
- `torch/hub/checkpoints/aliked_lightglue_v0-1_arxiv.pth`;
- DINOv2 source at revision `7764ea0f912e53c92e82eb78a2a1631e92725fc8`, including `hubconf.py`.

Installing torch or finding a `checkpoints` folder does not satisfy these prerequisites. The
bundle hashes the named checkpoints and cached Python source. Source URLs/licenses are listed
in its definition. ALIKED's upstream weight URL is mutable; retain the measured SHA256 from your
preparation receipt. The vehicle replay and receiver bundles need no model weights. Vehicle
`--live`, other vision models, and RTKLIB SPP are outside these selections.

## Rehearse with external networking disabled

Disconnect internet-facing Wi-Fi/Ethernet or block external access while retaining localhost
for the SITL connection. Then run `verify` and `rehearse` for each selected bundle:

```sh
python3 templates/offline-kit/bundle.py verify vision --cache /Volumes/USB/navkit \
  --python "$PWD/.venv-vision/bin/python"
python3 templates/offline-kit/bundle.py rehearse vision --cache /Volumes/USB/navkit \
  --python "$PWD/.venv-vision/bin/python" --network-disabled
# Substitute vehicle-sim and its venv for the two simulation flights.
# receiver-log uses python3 directly and does not need --python.
```

`--network-disabled` records your declaration that networking was actually disabled; it does not
configure a firewall. A run without that flag can succeed but always records `offline_ready: false`.
The runner sets the sample's Torch cache path, pip's no-index mode for rehearsals, and the common
Hugging Face offline flags. Those settings are not proof of isolation. A network-disconnected
run is still required. The simulation script uses an already loaded image; its preflight fails
if the image is absent, before the sample could attempt an online image build.

The runner writes latest `prepare.json`, `verify.json` and `rehearse.json` under
`<cache>/bundles/<bundle>/`. Each attempt also has a separate `run-*/receipt.json` and command logs.
Receipts include input hashes relative to the checkout/cache, definition/tool fingerprints,
Python/platform/package versions, exact commands, exit statuses, measured elapsed seconds,
output byte counts/hashes, errors and the declared network condition. Unknown prerequisites,
changed inputs, partial prep state, failed commands, missing/old outputs and a replay that
silently skips one log all fail with a nonzero exit. `verify` means inputs/runtime match; it does
not mean the sample ran. Only a successful full sample rehearsal with the network declaration can
set `offline_ready: true`. A synthetic fixture never sets it.
For the vehicle bundle, the runtime record also captures the Docker server version and loaded
SITL image ID; missing or changed tooling/image identity invalidates verification.

## Keep a fallback recording and report

Save a successful run folder, not just a screenshot. For receiver replay keep `replay.json`,
the `epochs/` CSV files and the command log. For vehicle simulation keep `navdash/` and, if useful,
the sample's `runs/v2-*.raw.jsonl`/SITL logs. For vision keep both front-end caches and `fusion/`,
including its navdash tracks, CSV and result JSON. Keep the receipt beside them and capture a
short screen recording before travel. Clearly label a fallback presentation **recorded replay**.

The committed sample reports and navdash recordings are available for a fallback talk even if a
new heavy run cannot finish. They show the earlier sample author's results, not a successful run
on your laptop. The vehicle's dashboard uses MapLibre resources; cache the optional dashboard JS,
styles, fonts and map tiles separately or use the saved screen recording/CSV report. These three
bundles verify the sample pipelines, not an internet-free browser basemap.

## Second-laptop checklist

1. Copy the full checkout and selected cache, including `.prep-state.json`, `SHA256SUMS`,
   `LICENSES.txt`, `pip/`, the relevant `datasets/`/`docker/`/`torch/` trees and `bundles/` receipts.
   Check dataset/weight sharing terms first. A git clone alone omits these cached assets.
2. Use the same target OS/architecture and Python minor version as the prepared wheel cache.
   Install Python/Docker before disconnecting. Do not copy a venv: create a new one for each heavy
   bundle on the second laptop.
3. With the copy mounted, run the following while external networking is already disabled:

   ```sh
   python3 templates/offline-kit/prep.py --verify --out /Volumes/USB/navkit
   python3.12 -m venv .venv-vision
   python3 templates/offline-kit/bundle.py prepare vision --cached-only \
     --cache /Volumes/USB/navkit --python "$PWD/.venv-vision/bin/python"
   python3 templates/offline-kit/bundle.py verify vision \
     --cache /Volumes/USB/navkit --python "$PWD/.venv-vision/bin/python"
   python3 templates/offline-kit/bundle.py rehearse vision --network-disabled \
     --cache /Volumes/USB/navkit --python "$PWD/.venv-vision/bin/python"
   ```

   Substitute `vehicle-sim` and its new venv; cached-only preparation loads its saved Docker image.
   Receiver replay needs no venv; use `prepare receiver-log --cached-only`, then verify/rehearse.
   Cached-only preparation checks the copied receipt/hashes before rebuilding the local runtime;
   it never runs a fetcher or online model warm-up. Missing assets fail instead of being fetched.
4. Open the fresh report, inspect command exit statuses and expected output counts, and test the
   fallback recording/report on that laptop. Preserve this laptop's receipt with the artifacts.
   Do not promote a cache check or first-laptop run into second-laptop offline evidence.

## What was exercised here

On 2026-11-07 local time (macOS arm64, Python 3.14.7), the tool prepared, verified and rehearsed
the synthetic receiver fixture and the seven pinned real VAARA logs. The fixture contained 750
epochs; the real replay contained 47,450 epochs across all seven files. The measured report is
[`rehearsal-report.json`](../templates/offline-kit/rehearsal-report.json). Networking remained
available, so both runs recorded `offline_ready: false`. Vehicle SITL, the vision model/data
download and pipeline, a network-disconnected run, and the second laptop were **not rehearsed**
in this change. Their prerequisites remain cache-required until your measured rehearsal succeeds.

For a fast tool check with no real data or optional packages:

```sh
python3 templates/offline-kit/bundle.py prepare receiver-log --fixture --cache /tmp/navkit-fixture
python3 templates/offline-kit/bundle.py rehearse receiver-log --fixture --cache /tmp/navkit-fixture
python3 -m unittest discover -s templates/offline-kit -p 'test_bundles.py'
```
