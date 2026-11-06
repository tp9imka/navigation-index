# MagNav challenge - paper digest
<!-- about: res:afrl-magnav-challenge-2020, repo:mit-ai-accelerator/magnav.jl, repo:lw-kong/magnav -->
**Signal Enhancement for Magnetic Navigation Challenge Problem** - Gnadt (MIT), Belarge, Canciani, Carl, Conger, Curro, Edelman, Morales, Nielsen, O'Keeffe, Rackauckas, Taylor, Wollaber (MIT, MIT Lincoln Lab, AFIT), arXiv 2020 (v2 2023). [paper](https://arxiv.org/abs/2007.12158) | [code](https://github.com/MIT-AI-Accelerator/MagNav.jl) | [challenge entry](https://github.com/lw-kong/MagNav) | Read: full text via ar5iv HTML rendering of v2 (the arXiv PDF could not be text-extracted here).

## Problem
A scalar magnetometer in an aircraft cabin measures the Earth core field ("25,000-65,000 nT"), the crustal anomaly field ("typically less than 1000 nT") and the aircraft's own interference field, all summed. MagNav needs the anomaly field alone to match against a map. The challenge asks for a model that removes the aircraft field from cabin magnetometers, where classical Tolles-Lawson (TL) compensation "does not produce a compensated signal with sufficiently accurate results".

## Method
This is a challenge-problem definition, not a method paper. What it fixes:
- Task: map uncompensated cabin scalar magnetometers plus auxiliary sensors => compensated anomaly signal.
- Truth: `mag_1_c`, the professionally compensated tail-stinger magnetometer. Chosen over an anomaly map to avoid position interpolation error and to share weather conditions with the cabin sensors.
- Metric: standard deviation of the error between model output and truth, per flight line.
- Hold-out: line 1003.10 of Flight 1003 is the evaluation line; the other lines are the build set.
- Allowed inputs: diurnal, IGRF, uncompensated magnetometers, fluxgates, INS, current/voltage sensors. Fields redundant with truth (compensated tail values) are banned.
- Submission: a Git repo that runs on any original HDF5 file without source edits and outputs line, time and compensated value; a ~5-page methodology note is recommended.
- Baseline: MagNav.jl `create_TL_coef` (TL fit) then `detrend`. The paper motivates "scientific ML" (physics model plus learned correction) as the intended direction.

## Data and sensors
- Cessna Grand Caravan flown by Sander Geophysics, summer 2020, near Ottawa (Renfrew, Eastern Ontario and a figure-of-merit area).
- 5 optically pumped cesium scalar magnetometers (Mag 1 on the tail stinger, Mags 2-5 in the cabin), 4 fluxgate vector magnetometers (Flux A-D), INS, GPS, current/voltage sensors.
- Public flights 1002-1007. Flight 1003: June 29, 2020, "approximately 5 hr and 42 min", 400 m and 800 m altitudes.
- Sample rate: not stated in the paper text (10 Hz per the dataset card).
- Dataset card: [magnav-challenge-data](../dataset-cards/magnav-challenge-data.md) (sizes, Zenodo records, the restrictive Air Force data agreement).

## Headline results (as reported)
- No quantitative results. The paper reports no RMSE, no standard deviation numbers and no navigation error.
- Fig. 2 (qualitative, Flight 1002): TL on Mag 1 "exactly matches" the SGL professional compensation; Mag 5 "performs fairly well"; Mags 3 and 4 "would not be suitable"; Mag 2 "not shown due to even worse performance".
- Our read: the index summary says "Physics (Tolles-Lawson) plus ML beat either alone". That is the paper's motivation, not a result in this paper.

## Follow-on compensation work (Gnadt)
- Gnadt, "Machine learning-enhanced magnetic calibration for airborne magnetic anomaly navigation", AIAA SciTech 2022 Forum, paper 2022-1760 ([DOI](https://doi.org/10.2514/6.2022-1760)). Not read: AIAA returned 403 and no arXiv preprint was found (arXiv author query for "Gnadt" lists only 2007.12158 and 2212.09899). A 2026 third-party preprint ([arXiv 2603.08265](https://arxiv.org/abs/2603.08265), not read beyond its search snippet) describes it as TL combined with a pre-trained NN, integrated into a Kalman filter.
- Open sibling: Gnadt, Wollaber, Nielsen, "Derivation and Extensions of the Tolles-Lawson Model for Aeromagnetic Compensation" ([arXiv 2212.09899](https://arxiv.org/abs/2212.09899)). Read: abstract only. Reference derivation of the 1950 TL model (permanent, induced, eddy-current terms), the calibration procedure, a second-order correction and a way to build the aircraft vector field.
- The code side of that line of work is in MagNav.jl `src/compensation.jl`: model types `:m1` ("standard feedforward neural network"), `:m2a`-`:m2d` (NN outputs the TL coefficients, or an additive correction to TL) and `:m3s`/`:m3v`/`:m3w`/`:m3tf` ("NN determines scalar/vector correction to TL", window NN, transformer) per the docstrings.

## Limitations
- Stated by authors: TL assumptions hold for a stinger magnetometer ~3 m aft, which "is impractical for operational aircraft"; stinger truth needs a stinger-equipped aircraft; flights have individual nuances (read the pilot comment files).
- Our read: the metric is compensation error only. A good std-dev score does not guarantee a good position fix; map error and filter tuning are outside the challenge.
- Our read: one aircraft, one region. Models fit to this Caravan's interference will not transfer to another airframe without retraining.
- Our read: Appendix B points Flight 1007 to "Flt1006_readme.txt", likely a typo.

## Code, weights, license
- MagNav.jl: GitHub license NOASSERTION; `LICENSE.md` says public domain (17 U.S.C. 105) plus MIT-style text. Latest release v1.3.5 (2026-10-05), last push 2026-11-02. README: "this specific project has concluded. Only minimal changes". Docker image `ghcr.io/mit-ai-accelerator/magnav.jl`.
- Data: separate Air Force Data Sharing Agreement in the README - non-profit research, education or government purposes only, one-year term. Not open data in the usual sense.
- No pretrained compensation weights published.
- lw-kong/MagNav: no license file (GitHub API null), last push 2022-07-26. Pipeline is Julia TL pre-filter (`runs/pre_TL.jl`) then MATLAB `runs/main.m` that needs the Deep Learning Toolbox; targets line 1003.10. Method is described only in an `Introduction.pdf`.

## Reproduction effort (estimate)
Estimate:
- CPU laptop is enough. Data: ~0.4-1.2 GB from Zenodo, or MagNav.jl lazy artifacts (train set ~183 MB, Ottawa maps ~711 MB).
- 2-4 h to a TL baseline on line 1003.10 natively (Julia install and precompile dominate); 1-2 h via Docker.
- No paper numbers to reproduce. The lw-kong entry needs a MATLAB licence with Deep Learning Toolbox.
- The official challenge leaderboard and hidden evaluation data are not public.

## What a hackathon team can take from it
- A ready benchmark: train on the build lines, report error std vs `mag_1_c` on 1003.10. Same protocol makes results comparable to MagNav.jl models.
- TL as the physics prior, then a small NN on residuals (MagNav.jl `:m2a`/`:m3s`) - the cheapest "physics plus ML" demo with real flight data.
- Use the compensated signal in MagNav.jl `run_filt(..., :ekf)` or `:mpf` to close the loop to a position fix; see the [MagNav.jl integration card](../integration-cards/mit-ai-accelerator__magnav.jl.md).
- Feed the fluxgate and current/voltage channels as NN inputs; they are permitted and carry the aircraft interference.
- Read the data agreement before shipping anything derived from the flights outside the team.
