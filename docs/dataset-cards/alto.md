# ALTO

<!-- about: repo:metaslam/alto -->

Aerial-view, large-scale, terrain-oriented dataset for UAV visual place recognition: long
helicopter flights with nadir imagery and satellite references. Cisneros, Yin, Zhang,
Choset, Scherer (CMU), arXiv 2207.12317 (2022). Used for the ICRA 2022 General Place
Recognition (GPR) competition, visual terrain-relative navigation track.

| Field | Value |
|---|---|
| Platform | Helicopter, nadir high-resolution RGB camera |
| Environment | Two long trajectories (about 150 km and 260 km) over Ohio and Pennsylvania: urban/suburban, forest, rural, natural terrain |
| Sensors and rates | RGB camera (competition release: compressed to 500x500 at 20 fps), accelerometer, laser altimeter, GPS-INS (paper abstract, GPR README) |
| Ground truth | NovAtel SPAN GPS+INS, stated "submeter level accuracy" (GPR competition README) |
| Size | Not verified (Dropbox folders and Baidu; no size given) |
| License | Repo: BSD-3-Clause (applies to repo content; dataset terms not stated) |
| Format | Competition: query frames paired with reference satellite images, with relative GT per sequence |
| Index | [ALTO](../../catalog/repos/metaslam__alto.md) |

## What's in it

- Released so far: the GPR competition subsets (Round 1 and Round 2). The ALTO README still
  says "Full Dataset: Coming soon!" (checked 2026-11-06), so the full 150 + 260 km release
  with altimeter and accelerometer streams is not public via that repo.

## Download

```bash
# Round 1 (Dropbox shared folder; browser or dl=1 zip)
curl -L -o alto_round1.zip "https://www.dropbox.com/sh/q1w5dmghbkut553/AAAOCMaELmfHE4NN5cw06QBba?dl=1"
# Round 2
curl -L -o alto_round2.zip "https://www.dropbox.com/scl/fo/saejbf9qanbfq40k8jo18/h?dl=1&rlkey=l19kx1vzzahifv3n5lkg19n84"
# Baidu mirror (code qghd): https://pan.baidu.com/s/1M97bBnSoRhy-56NhAmpf7w
```

Not tested: Dropbox folder zips can fail above its folder-download limit; fall back to the
browser. Note the Round 1 Dropbox link is shared with the GPR lidar track folder.

## Loading and tooling

Evaluation scripts live in https://github.com/MetaSLAM/GPR_Competition (not indexed).
Retrieval: [VPR methods evaluation](../../catalog/repos/gmberton__vpr-methods-evaluation.md),
[AnyLoc](../../catalog/repos/anyloc__anyloc.md).

## Hackathon fit

- Idea 11 / 18 for fixed-wing or helicopter-altitude scenarios: long routes over rural and
  forested terrain, where UAV-VisLoc and DenseUAV are thin.
- Retrieval-only demo; little else is public.

## Pitfalls

- Only competition subsets are public; the paper's richer streams are not.
- Unknown size and Dropbox reliability; pre-download well ahead.
- 500x500 compressed frames limit fine matching.

## Sources

- https://github.com/MetaSLAM/ALTO README (links, full dataset "coming soon"), read 2026-11-06.
- https://github.com/MetaSLAM/GPR_Competition README (helicopter, 20 fps, 500x500, NovAtel SPAN, submeter).
- arXiv 2207.12317 abstract (150 km and 260 km, sensors).
