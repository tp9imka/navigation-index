# Offline kit

<!-- about: concept:datasets-benchmarks, repo:protomaps/pmtiles -->

Venue Wi-Fi will not carry datasets, Docker images or a `pip install torch`. This kit fills one
cache directory (a USB disk is fine) with everything a team may need, before the event:

| Type | What | Built from |
|---|---|---|
| `dataset` | 26 items covering the 23-row core shortlist, plus 8 optional items (about 55 + 53 GB) | [dataset cards](../../docs/dataset-cards/README.md) shortlist |
| `script` | sample data that a sample's own script fetches | `samples/gnss-rinex-processing/fetch_data.sh` |
| `pip` | wheel caches for linux/amd64, linux/arm64, macOS arm64 (Python 3.12) | every `samples/*/requirements.txt` (12 today), plus card Install rows |
| `docker` / `docker-build` | `docker save` tarballs per platform; locally built sample images | Dockerfile `FROM` lines, compose `image:` lines, card `docker run` lines |
| `git` | `git clone --mirror` => `git bundle` for the 40 most-linked carded repos (83 in `full`) | integration cards ranked by inbound links in `index/records.jsonl` |
| `js` | maplibre-gl, milsymbol, pmtiles for the demo dashboard | `templates/demo-dashboard/fetch-vendor.sh` |
| `tool` / `tiles` | `pmtiles` CLI (4 platforms) and a regional vector basemap extract | `protomaps__pmtiles` card, Protomaps daily build |

Files: `prep.py` (fetcher, stdlib only), `build_manifest.py` (regenerates `manifest.json` from the
repo), `manifest.json`, `test_manifest.py`.

## Profiles

| Profile | Contents | Size |
|---|---|---|
| `minimal` | small datasets (UZH-FPV one sequence, NCLT one session, AFIT MagNav, S7AM1NA, Pohang nav, Remote ID captures), light pip sets, `python` base images, top 10 repos, JS, pmtiles CLI | about 1.4 GB datasets + about 2.1 GB repos (ArduPilot and PX4 are 0.7 and 0.6 GB) + images and wheels |
| `standard` (default) | the full core dataset shortlist, every sample pip set, base images, sample image builds, 40 repos, basemap | about 55 GB datasets + about 5.7 GB repos + images and wheels |
| `full` | plus the optional datasets, the card pip names, card images (GDAL, MagNav.jl, goatak), all 83 carded repos | about 109 GB datasets + 9.5 GB repos + images and wheels |

Repo and dataset numbers come from `--dry-run --probe --profile full` on 2026-11-06 (GitHub API repo
size, HEAD, Zenodo / Mendeley / S3 / LFS listings). Wheel and Docker sizes are not estimated:
the dry run reports them as unknown instead of guessing.

## The week before

```bash
cd templates/offline-kit
python3 prep.py --dry-run --profile standard              # sizes, licenses, nothing downloaded
python3 prep.py --dry-run --probe --profile standard      # ask hosts for missing sizes (needs network)
export GITHUB_TOKEN=$(gh auth token)                      # optional: GitHub API rate limit for --probe and tool:pmtiles
python3 prep.py --out /Volumes/USB/navkit --types tool    # pmtiles CLI first (tiles need it)
python3 prep.py --out /Volumes/USB/navkit --profile standard --bbox <minlon,minlat,maxlon,maxlat>
```

- Every item prints its license before it downloads, and the run writes `LICENSES.txt`. Read it.
  TEXBAT, MagNav (Air Force use agreement) and AnyVisLoc forbid redistribution; most sets are non-commercial.
- Interrupt any time. Files download to `*.part` and resume with HTTP Range; finished items are
  recorded in `.prep-state.json` and skipped next run (`--force` refetches).
- Checksums: Zenodo md5, Mendeley sha256, S3 ETag md5, Git LFS pointer sha256, TUM-VI `.md5` file
  and GitHub release digests are checked when the host publishes them. Everything else gets a sha256
  computed after download, so the cache can be verified later even if the source cannot.
- EuRoC rate-limits (HTTP 429): the fetcher backs off and honours `Retry-After`. Downloads are sequential.
- Google Drive items (UAV-VisLoc, MassMIND, Anti-UAV300, SUES-200) go through
  `drive.usercontent.google.com` with `confirm=t`. When Drive answers with an HTML quota page the item
  fails with that message; rerun later or use `gdown` in the project venv.
- `docker-build` items build `samples/sitl-docker` (ArduPilot, PX4, client), `rtklib-demo5` and
  `gnss-signal-chain`. The Dockerfiles clone and compile at build time, so build them here, not at the
  venue. Builds are saved for the host platform only.
- Manual items (`magnav-ottawa-maps`, `tartanair-one-env`) print instructions instead of downloading,
  because their URLs are not in this repo. The Ottawa maps arrive when you run
  [magnav-quickstart](../../samples/magnav-quickstart/README.md) once online.
- Pick the map area once the venue or problem region is known: `--bbox` and `--maxzoom` (default 14).
  The default bbox is the project-repo compose `ORIGIN` (59.0, 10.0). `--dry-run --probe` asks
  `pmtiles extract --dry-run` for the archive size; the default bbox at z14 estimated 6.6 MB.
- Model weights are not in the manifest. LightGlue / SuperPoint and the other matchers download weights
  on first use into `~/.cache/torch/hub/checkpoints/`; run each sample once online and copy that folder
  into the cache by hand. See [model-weights-licenses](../../docs/model-weights-licenses.md).

Selective runs: `--types dataset,pip`, `--items 'dataset:nclt*' --items 'git:cvg/*'`,
`--pip-platforms linux-amd64`, `--docker-platforms linux/amd64`, `--python-version 3.11`.

## The night before

```bash
python3 prep.py --out /Volumes/USB/navkit --profile standard   # resumes; only failed / new items run
python3 prep.py --out /Volumes/USB/navkit --keep-mirrors --types git --force   # refresh bundles
python3 prep.py --verify --out /Volumes/USB/navkit             # recheck every file against SHA256SUMS
```

Then test offline with Wi-Fi off, on one laptop:

```bash
docker load -i navkit/docker/python_3.12-slim__linux-arm64.tar
python3 -m pip install --no-index --find-links navkit/pip/macos-arm64 -r samples/mavlink-to-tak-cot/requirements.txt
git clone navkit/git/bundles/cvg__lightglue.bundle lightglue
cp navkit/js/* templates/demo-dashboard/vendor/
cp navkit/tiles/basemap.pmtiles templates/demo-dashboard/
navkit/tools/pmtiles/darwin-arm64/pmtiles serve templates/demo-dashboard --port 8080 --cors='*'
# or: python3 prep.py --serve 8080 --out templates/demo-dashboard   (Range-capable)
# open http://localhost:8080/index.html?pmtiles=basemap.pmtiles
```

Packages listed as "no wheel" in the run log were saved as sdists in `pip/sdist/` and need a compiler
offline; the dependencies of such a package are not fetched for that platform.

## Sharing the cache with teammates

USB: copy the directory, then `python3 prep.py --verify --out <copy>`.

Local network (venue LAN or a travel router, no internet needed):

```bash
# on the laptop that holds the cache
python3 prep.py --serve 8000 --out /Volumes/USB/navkit
# on each teammate laptop
python3 prep.py --pull-from http://<host-ip>:8000 --out ~/navkit --items 'pip/linux-amd64/*' --items 'datasets/nclt*'
```

`--serve` is `http.server` plus byte ranges, so interrupted pulls resume. `--pull-from` reads the
host's `SHA256SUMS`, downloads what matches `--items` (all if omitted) and checks each file's sha256.
`wget -c -r -np http://<host-ip>:8000/` also works against it.

## Layout

```
navkit/
  datasets/<id>/...        docker/<image>__<os-arch>.tar     pip/<platform>/*.whl, pip/sdist/
  git/bundles/<owner>__<repo>.bundle  (git/mirrors/ with --keep-mirrors)
  js/   tools/pmtiles/<os-arch>/pmtiles   tiles/basemap.pmtiles (+ .source.txt: build URL and bbox)
  SHA256SUMS  LICENSES.txt  .prep-state.json
```

## Regenerating the manifest

```bash
python3 build_manifest.py          # after adding a sample, card or Dockerfile
python3 -m unittest test_manifest  # checks every dataset URL / id appears in its card, manifest is current
```

Dataset subsets are chosen in `build_manifest.py` (`DATASETS`); each entry carries `evidence`
strings that must appear verbatim in its card, so a URL cannot enter the manifest unless a card
documents it. Pip, Docker, repo, JS and tool items are parsed from the repo files listed above.
Two URLs are built by the fetcher rather than copied from a card: Google Drive downloads from the
card's Drive id, and Git LFS media URLs from the card's repo and path.

## Verification (2026-11-06, macOS arm64, Python 3.14, Docker 29.5)

Ran into a scratch directory, then deleted:

- `dataset:s7am1na-sample` (23.7 MB, size checked), resumed from a truncated `.part`, same sha256.
- S3 listing fetcher on Boreas `calib/` (5 files, ETag md5 checked); Google Drive fetcher on MassMIND
  `Segmentation_Masks.zip` (7.25 MB, valid zip).
- `docker:alpine:3.20` pulled and saved for linux/amd64 and linux/arm64 (3.7 and 4.2 MB); the arm64
  tar loaded back with `docker load`. Alpine is a test image only, not in the manifest.
- `pip:mavlink-to-tak-cot` and `pip:gnss-ins-ekf-outage` for all three platforms: wheels for every
  package, no sdist fallback needed.
- `git:snstac/pytak` mirrored, bundled, `git bundle verify` passed, cloned back from the bundle.
- `js:pmtiles.js`, `tool:pmtiles` (4 archives, GitHub sha256 digests matched).
- `tiles:basemap` with a 0.08 x 0.04 degree Oslo bbox at maxzoom 12: 1.7 MB extract from the
  2026-11-05 Protomaps build (`pmtiles extract`), read back with `pmtiles show`.
- `--serve` + `--pull-from`: pulled a dataset file and the tiles over localhost, resumed a partial
  file with a 206 response, sha256 verified.
- `--dry-run --probe --profile full`: all listing resolvers (Zenodo, Mendeley, S3, Apache index,
  Git LFS pointer, GitHub API) answered.

Not run: the full or standard profile end to end, the `docker-build` items, the torch-heavy pip sets,
the `httpdir` and `lfs` downloads themselves (only their listings), the `script` item (it writes into
the sample folder), Windows.
