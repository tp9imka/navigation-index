# 09. Measuring OpenVINS covariance realism (NEES) in under 30 minutes

Loop-24, 2026-11-09. Question: what is the cheapest way to put one measured NEES number on a
mainstream VIO, indoor, on an Apple Silicon Mac, reusing
[relative-nav-benchmark](../../../samples/relative-nav-benchmark/README.md)?

Nothing here was run against a real covariance. No dataset was downloaded and no Docker image
was pulled. The scorer in section 5 was dry-run on the sample's committed TUM files with a
placeholder sigma, to check parsing and alignment only. No NEES value in this doc is a
hub measurement.

## 1. Bottom line

- **Cheapest path: rerun OpenVINS on the UZH-FPV bag the sample already uses, then score
  `ov_state_std.txt` with a stdlib script.** `vio/run_openvins.sh` already passes
  `_save_total_state:=true` and writes `ov_state_std.txt` next to `ov_state_est.txt`. The
  2026-11-06 run produced it, but `results/vio/openvins_raw/` is git-ignored, so it is not in
  this checkout. The committed GT (`results/vio/uzhfpv_indoor_forward_3_gt.tum`) can be reused
  as is.
- **Budget: fits, with little margin.** About 20 min image build + 0.5 to 1.5 min OpenVINS run +
  seconds of scoring = about 21 to 23 min of compute. Wall time is 22 to 29 min if the 1.61 GB
  bag downloads in parallel at the 1 to 2 MB/s seen on 2026-11-06. If the 2026-11-06 raw output
  still exists on the machine that made it, the whole job is the scoring step: seconds.
- **Blocker for this job: Docker.** The run needs the `ros:noetic-perception` base image (pull)
  plus a build. This job was not allowed to pull. The Docker daemon on this machine
  (`docker-desktop`, 16 vCPU, aarch64) has no `relnav-openvins:v2.7` image. A native macOS
  OpenVINS build would need brew packages (OpenCV, Ceres, Boost), also out of bounds.
- **No other set fits.** EuRoC is only available as 6 GB zips, and both hosts refused on
  2026-11-09. TUM-VI room1 as a bag is 2.97 GB.
- **Published real-data NEES exists, but not for OpenVINS stereo on these sets.** It already
  points to large overconfidence: average position NEES 131 to 363 against an expected 3 for a
  sliding-window VI filter on EuRoC machine hall
  ([Lisus et al. RA-L 2023](https://arxiv.org/abs/2212.06923)). The OpenVINS docs show 10.6 to 13.1
  in an example console output on EuRoC V1_01. See section 6.

## 2. Which VIO gives a usable covariance

| Estimator | Covariance with the pose? | Where | Checked how |
|---|---|---|---|
| OpenVINS v2.7 | Yes, full | ROS topic `poseimu` (PoseWithCovarianceStamped, 6x6 marginal of p then q) and `odomimu` (Odometry, pose and twist covariance). Text dump `ov_state_std.txt` (per-axis std only) | `gh api` on `ov_msckf/src/ros/ROS1Visualizer.cpp` and `ROSVisualizerHelper.cpp` at tag v2.7 |
| VINS-Fusion | No | `vins_estimator/src/utility/visualization.cpp` never fills `covariance`. The result CSV has time, position, quaternion and velocity only | grep of that file on master |
| ORB-SLAM3 | No | `System.cc` writes poses only (`SaveTrajectoryTUM`, `SaveTrajectoryEuRoC`, `SaveTrajectoryKITTI`, keyframe variants) | grep of `src/System.cc` on master |

OpenVINS detail that matters for scoring:

- `ov_state_std.txt` columns: `t`, std of the orientation error (3, OpenVINS JPL local error), std
  of `p_IinG` (3, global frame), then v, bg, ba and calibration std. Same timestamps as
  `ov_state_est.txt` (`t, q(4), p(3), v(3), ...`), written in the same call. Off-diagonal
  terms are not written.
- In ROS 1 serial mode, `visualize()` runs after every camera update, so it also publishes
  `poseimu`. Full 3x3 position covariance needs `rosbag record /ov_msckf/poseimu` inside the
  container. The publisher queue is 2 and serial mode runs faster than real time, so drops are
  possible. That was not tested. The text dump is deterministic, so it is the first choice.
- OpenVINS' own scorer `ov_eval error_singlerun` computes NEES, but it reads a 20-column file
  with covariance (`t, p, q, 6 orientation cov, 6 position cov`). The sample's slim Dockerfile
  builds only `ov_core ov_init ov_msckf`, so `ov_eval` is not in the image. A stdlib script
  (section 5) avoids a rebuild.
- Position NEES only. Orientation NEES would need the UZH-FPV GT orientation convention, which
  the sample README says was never checked.

## 3. Candidate sequences

| Sequence | Download | Ground truth | GT rate | OpenVINS v2.7 config | In the hub already | Fits 30 min |
|---|---|---|---|---|---|---|
| **UZH-FPV indoor_forward_3** (Snapdragon) | bag 1.61 GB (HEAD 2026-11-09: 1,608,934,832 B) | Leica MS60 laser tracker + offline vision reconstruction ([card](../../dataset-cards/uzh-fpv.md)); covers 49.5 s of the 92 s bag | 500 Hz in the bag (24,750 poses over 49.5 s in the committed GT TUM) | `uzhfpv_indoor` (used by the sample) | GT TUM and OpenVINS TUM committed in `samples/relative-nav-benchmark/results/vio/`. Bag and raw OpenVINS output are git-ignored | **Yes**, about 21 to 23 min compute |
| UZH-FPV indoor_45_2 (Snapdragon) | bag 1.24 GB (HEAD 2026-11-09: 1,244,666,706 B) | same type | not checked | `uzhfpv_indoor_45` | No | Probably, but the config was never run here |
| EuRoC V1_01 / V2_01 | only inside `vicon_room1.zip` 6.04 GB / `vicon_room2.zip` 6.01 GB ([card](../../dataset-cards/euroc-mav.md)). On 2026-11-09 the per-sequence `robotics.ethz.ch` URL did not answer and the Research Collection answered HTTP 429 | Vicon 6D | not checked | `euroc_mav` | No | **No**: 6 GB at 1 to 2 MB/s is 50 to 100 min |
| TUM-VI room1, 512 | calibrated bag 2.97 GB (HEAD 2026-11-09: 2,971,525,053 B). The EuRoC-format tar is 1.71 GB but `ros1_serial_msckf` needs a bag | mocap, full trajectory ([card](../../dataset-cards/tum-vi.md)) | 120 Hz (card) | `tum_vi` | No | **No**: 25 to 50 min download. GT topic inside the bag not checked |
| KAIST VIO (3.15 x 3.60 x 2.50 m arena, closest to a Day-1 close area) | Google Drive, size not checked | OptiTrack ([OpenVINS docs](https://docs.openvins.com/gs-datasets.html)) | 50 Hz (same source) | `kaist_vio` | No | Unknown |

UZH-FPV is the only one where the hub already has the pipeline, the config and the GT. It is
also a fast racing flight (indoor top speed 12.8 m/s per the OpenVINS docs). That is not the
slow close-area flight we expect on Day 1, so treat its factor as a prior, not as a tuning value.

## 4. What the number means, and what biases it

- **Error definition.** GT position is linearly interpolated to each OpenVINS timestamp (gap at
  most 20 ms), mapped into the OpenVINS global frame by a 4-DoF (x, y, z, yaw) fit, then
  `NEES_k = sum over axes of (e_i / sigma_i)^2`. Expected value 3, median 2.366, 95th percentile 7.815
  (chi-square, 3 dof).
- **Alignment uses the GT, so the measured NEES is a lower bound on overconfidence.**
  `--align posyaw` fits on the whole overlap (the `ov_eval` convention) and removes part of the
  drift. `--align first10` fits on the first 10 % only, like a known start pose, and lets
  the drift show. Report both.
- **Gauge mismatch.** OpenVINS starts at 4888.24 s, while GT starts at 4908.79 s (first rows of
  the committed TUM files). The filter has grown 20.6 s of covariance before the first GT epoch,
  but the alignment zeroes the error there. That also biases NEES low.
- **Diagonal only.** Cross terms between x, y and z are ignored. The result is not the
  textbook NEES. Per-axis means are reported so a single bad axis is visible.
- **GT error is counted as VIO error.** UZH-FPV does not state GT accuracy. If OpenVINS reports
  centimetre sigmas, a centimetre-level GT error would raise NEES. This cannot be separated
  with one run.
- **One run, strongly autocorrelated samples.** No chi-square acceptance interval on the time
  average applies. Use median, 95th percentile and coverage. Tsuei et al. found a single scalar
  inflation inadequate on TUM-VI (section 6), so the fitted factor is a first-order fix only.
- **Inherited assumptions** from `vio/eval_uzhfpv.py`: the GT pose and the OpenVINS IMU pose
  are compared directly (no lever arm), with no time offset.

**Proposed threshold.** PASS (covariance usable as-is for a safety margin) if at least 90 % of
epochs fall inside the 95 % ellipsoid (`coverage_95 >= 0.90`). Otherwise report FAIL and use
`sigma_inflation.from_p95` as the multiplier on reported sigma. Given section 6, FAIL is the
expected outcome.

## 5. Command sequence (not run)

Step 0 decides between the seconds path and the 25-minute path.

```sh
cd samples/relative-nav-benchmark
export RELNAV_DATA=$PWD/data          # git-ignored
# 0. Seconds path: on the machine that ran the sample on 2026-11-06, the raw files may survive.
ls -la results/vio/openvins_raw/ov_state_est.txt results/vio/openvins_raw/ov_state_std.txt && echo "skip to step 3"
# 1. Download the 1.61 GB bag (13-27 min at 1-2 MB/s) and build the image (~20 min) in parallel.
#    The build pulls ros:noetic-perception. Needs colima or Docker Desktop.
./fetch_data.sh vio &
docker image inspect relnav-openvins:v2.7 >/dev/null 2>&1 || \
  docker build -f vio/Dockerfile.openvins -t relnav-openvins:v2.7 vio
wait
# 2. OpenVINS only (28.7-81 s for the 92 s bag). Do not use ./run.sh vio: it would also rerun the
#    mono VO and rewrite the committed TUM / navdash files.
vio/run_openvins.sh "$RELNAV_DATA/uzhfpv/indoor_forward_3_snapdragon_with_gt.bag" results/vio/openvins_raw uzhfpv_indoor 2
# 3. Score (stdlib, seconds). Save the script below as vio/nees_openvins.py first.
for al in posyaw first10; do
  python3 vio/nees_openvins.py --gt results/vio/uzhfpv_indoor_forward_3_gt.tum \
    --est results/vio/openvins_raw/ov_state_est.txt --std results/vio/openvins_raw/ov_state_std.txt \
    --align $al --out results/vio/nees_uzhfpv_indoor_forward_3_$al
done
```

Outputs: `results/vio/nees_uzhfpv_indoor_forward_3_{posyaw,first10}.json` (mean, median, p95,
per-axis means, 95 % coverage, covariance and sigma inflation factors fitted from mean,
median and p95) and a `.csv` time series (`t, ex, ey, ez, sx, sy, sz, nees`). Input type: real
flight data with laser-tracker GT.

Expected runtime:

| Step | Time | Source |
|---|---|---|
| Image build | ~20 min (apt 145 s, catkin `-j2` 754 s, export 232 s) | sample README cost table, colima 4 vCPU. `-j2` is fixed in the Dockerfile, so 16 vCPU will not speed it up much |
| Bag download, in parallel | 13 to 27 min | 1.61 GB at the 1 to 2 MB/s in the sample README |
| OpenVINS run | 28.7 to 81 s | sample README, two runs, same ATE to 1 mm |
| Scoring | seconds | dry run below |

Scorer, stdlib only. The dry run fed it the committed OpenVINS TUM file reshaped into the raw
column order, with a constant placeholder sigma. With `posyaw`, the error RMS it implies matched
the sample's committed SE3 ATE (0.36 m). With `first10` it came out close to, slightly below, the
committed origin-anchored RMSE (0.67 m), as expected for a fit over a start window rather than
one pose. That confirms the parsing, the association (1332 matched poses
against evo's 1334) and the 4-DoF fit. It says nothing about OpenVINS' real sigmas.

```python
"""Position NEES of an OpenVINS run against ground truth. Stdlib only.

Inputs: GT as TUM (t x y z qx qy qz qw), OpenVINS ov_state_est.txt and ov_state_std.txt
(written by run_openvins.sh with save_total_state). Uses the per-axis position std
(diagonal only; save_total_state does not write cross terms).
"""
import argparse, bisect, json, math, statistics

CHI2_3_MEDIAN, CHI2_3_P95 = 2.366, 7.815


def rows(path):
    return [[float(x) for x in l.split()] for l in open(path) if l.strip() and not l.startswith("#")]


def interp(gt_t, gt_p, t, max_gap=0.02):
    i = bisect.bisect_left(gt_t, t)
    if i == 0 or i >= len(gt_t) or gt_t[i] - gt_t[i - 1] > max_gap:
        return None
    a = (t - gt_t[i - 1]) / (gt_t[i] - gt_t[i - 1])
    return [(1 - a) * p0 + a * p1 for p0, p1 in zip(gt_p[i - 1], gt_p[i])]


def posyaw(g, e):
    """4-DoF (x, y, z, yaw) least-squares map from GT frame to the estimate's frame."""
    n = len(g)
    gc = [sum(p[k] for p in g) / n for k in range(3)]
    ec = [sum(p[k] for p in e) / n for k in range(3)]
    s = c = 0.0
    for p, q in zip(g, e):
        gx, gy, ex, ey = p[0] - gc[0], p[1] - gc[1], q[0] - ec[0], q[1] - ec[1]
        s += gx * ey - gy * ex
        c += gx * ex + gy * ey
    th = math.atan2(s, c)
    cs, sn = math.cos(th), math.sin(th)
    rot = lambda p: [cs * p[0] - sn * p[1], sn * p[0] + cs * p[1], p[2]]
    t = [a - b for a, b in zip(ec, rot(gc))]
    return (lambda p: [a + b for a, b in zip(rot(p), t)]), th


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gt", required=True)
    ap.add_argument("--est", required=True, help="ov_state_est.txt: t qx qy qz qw px py pz ...")
    ap.add_argument("--std", required=True, help="ov_state_std.txt: t sq(3) sp(3) ...")
    ap.add_argument("--align", choices=["posyaw", "first10"], default="posyaw",
                    help="posyaw: fit on the whole overlap (ov_eval convention); first10: fit on the first 10 %% only")
    ap.add_argument("--out", help="write <out>.json summary and <out>.csv time series")
    a = ap.parse_args()

    gt = rows(a.gt)
    gt_t, gt_p = [r[0] for r in gt], [r[1:4] for r in gt]
    est, std = rows(a.est), rows(a.std)
    assert len(est) == len(std), "est and std files differ in length"
    t, e, s, g = [], [], [], []
    for re_, rs in zip(est, std):
        assert abs(re_[0] - rs[0]) < 1e-4, f"timestamp mismatch {re_[0]} vs {rs[0]}"
        gp = interp(gt_t, gt_p, re_[0])
        if gp is not None:
            t.append(re_[0]); e.append(re_[5:8]); s.append(rs[4:7]); g.append(gp)
    n_fit = len(g) if a.align == "posyaw" else max(10, len(g) // 10)
    to_est, yaw = posyaw(g[:n_fit], e[:n_fit])
    nees, axis, series = [], [[], [], []], []
    for ti, ei, si, gi in zip(t, e, s, g):
        d = [x - y for x, y in zip(to_est(gi), ei)]
        z = [(dk / sk) ** 2 for dk, sk in zip(d, si)]
        nees.append(sum(z))
        for k in range(3):
            axis[k].append(z[k])
        series.append([ti] + d + si + [sum(z)])
    srt = sorted(nees)
    p95 = srt[int(0.95 * (len(srt) - 1))]
    k_mean, k_med, k_95 = statistics.fmean(nees) / 3, statistics.median(nees) / CHI2_3_MEDIAN, p95 / CHI2_3_P95
    out = {
        "align": a.align, "fit_samples": n_fit, "matched": len(nees), "yaw_deg": math.degrees(yaw),
        "duration_s": t[-1] - t[0], "nees_mean": statistics.fmean(nees), "nees_median": statistics.median(nees),
        "nees_p95": p95, "expected": {"mean": 3, "median": CHI2_3_MEDIAN, "p95": CHI2_3_P95},
        "per_axis_mean": [statistics.fmean(x) for x in axis],
        "coverage_95": sum(v <= CHI2_3_P95 for v in nees) / len(nees),
        "cov_inflation": {"from_mean": k_mean, "from_median": k_med, "from_p95": k_95},
        "sigma_inflation": {"from_mean": math.sqrt(k_mean), "from_median": math.sqrt(k_med), "from_p95": math.sqrt(k_95)},
        "note": "diagonal position std only; single run, samples autocorrelated",
    }
    print(json.dumps(out, indent=1))
    if a.out:
        json.dump(out, open(a.out + ".json", "w"), indent=1)
        with open(a.out + ".csv", "w") as f:
            f.write("t,ex,ey,ez,sx,sy,sz,nees\n")
            for r in series:
                f.write(",".join(f"{v:.6f}" for v in r) + "\n")


if __name__ == "__main__":
    main()
```

Optional second scorer for a cross-check: [smfeval](../../../catalog/repos/svendbot__smfeval.md)
(NEES, coverage, proper scoring rules) or
[cnspy_trajectory_evaluation](../../../catalog/repos/aau-cns__cnspy_trajectory_evaluation.md)
(NEES from pose covariance). Neither was installed or checked for input format.

## 6. Published NEES and consistency numbers

| Source | Estimator, data | What it reports | Read |
|---|---|---|---|
| [Lisus et al., RA-L 8(6) 2023](https://arxiv.org/abs/2212.06923) | Sliding-window filter VI-SLAM with IMU preintegration, VINS-Fusion KLT front end. **Real** EuRoC MH_01 to MH_05 | Average position NEES (expected 3): 130.86 (MH_04, RI) to 362.78 (MH_01, separate). MH_02 RI 153.61. The other rows were cut off in the HTML extraction. Yaw NEES (expected 1) 4.55 to 77.1. The authors expected none of the real runs to be consistent | Full text, arXiv HTML v1 (RA-L version is v4) |
| [OpenVINS docs, ov_eval page](https://docs.openvins.com/eval-error.html) | OpenVINS mono, `error_dataset posyaw`. **Real** EuRoC V1_01_easy | Example console output. Position NEES 10.629 (`mono_ov_vio`) and 13.095 (`mono_ov_slam`). Orientation NEES 625.4 and 793.6. Expected 3 | Docs page. An example output, not a study. Run count and version not stated |
| [Tsuei et al., ICRA 2021](../../../catalog/resources/tsuei-2021-learned-uncertainty-calibration-vi.md) | XIVO (mono EKF). **Real** TUM-VI room1 to room6 | The 9-dof NEES histogram barely overlaps chi-square(9). A constant scalar inflation is inadequate. A learned map from the reported covariance fixes most of it | Full text, arXiv HTML v1. Table values garbled in extraction, none quoted |
| [Observability and consistency with anchored features, IROS 2026](https://arxiv.org/abs/2606.19307) | OpenVINS base, global vs anchored features, Std / FEJ / RI-EKF | NEES only in Monte-Carlo **simulation** (Table III). Real TUM-VI room runs are reported as ATE and RPE only | Full text, arXiv HTML |
| FEJ2, Chen et al. ICRA 2022 | OpenVINS-family FEJ2 | Abstract says simulation and real-world tests | PDF only. No PDF reader here, not read |

What it implies (derived from the rows above, not measured): position covariance too tight by
3.5x to 4.4x (sigma by 1.9x to 2.1x) in the OpenVINS docs example, and by 44x to 121x
(sigma by 6.6x to 11x) in Lisus et al. Either way the hub's "overconfident" claim holds for
VIO, with a spread too wide to set a margin from. No source found reports NEES for OpenVINS
stereo on UZH-FPV, EuRoC Vicon rooms or TUM-VI room. The UZH-FPV run in section 5 would be new.

## 7. Not verified

Reconciled 2026-11-09 (loop-28): the plan was not run since (it needs the Docker build), so every
bullet below is still open. The arena's "overconfident" fault case is a synthetic stand-in
(reported sigma x0.25), not a VIO NEES measurement.

- No OpenVINS covariance was produced or scored. Every NEES figure here is cited or derived from
  a citation.
- Docker build time on this host (`docker-desktop`, 16 vCPU) and the `ros:noetic-perception` pull
  time. The 20 min figure is from colima, 4 vCPU, on 2026-11-06.
- Whether `poseimu` can be recorded without drops in serial mode, and whether the 2026-11-06 raw
  output still exists anywhere.
- UZH-FPV GT accuracy and frame convention, and the GT topics inside the TUM-VI and KAIST VIO bags.
- Download speed on the day. At under 1 MB/s the 30 min wall budget breaks.
- Lisus et al. numbers come from the v1 HTML. The published v4 tables were not compared.
