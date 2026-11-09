# VPAIR cached-observation scheduling replay

One real flight's derived observations, with artificial frame delays/covariance. No new flight, GPU run, timestamp latency measurement or independence claim.

Calibration: frames 0..9, 37 pairs. Evaluation: frames 10..198. Budget: 40 requests, one pending job. Settings fixed before this replay; all sensitivity cases retained.

| Stride | Q / frame | Delay frames | Policy | Requests | Accepted | RMSE m | Max m | Within 50 m |
|---:|---:|---:|---|---:|---:|---:|---:|---:|
| 1 | 4 | 0 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 4 | 0 | periodic | 38 | 13 | 106.59 | 202.22 | 0.434 |
| 1 | 4 | 0 | threshold | 40 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 4 | 0 | predictive | 40 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 4 | 2 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 4 | 2 | periodic | 38 | 13 | 106.81 | 202.22 | 0.429 |
| 1 | 4 | 2 | threshold | 40 | 1 | 127.68 | 217.63 | 0.106 |
| 1 | 4 | 2 | predictive | 40 | 2 | 121.77 | 217.19 | 0.148 |
| 1 | 4 | 5 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 4 | 5 | periodic | 38 | 13 | 107.25 | 202.22 | 0.429 |
| 1 | 4 | 5 | threshold | 33 | 1 | 131.55 | 218.50 | 0.106 |
| 1 | 4 | 5 | predictive | 33 | 6 | 113.28 | 204.53 | 0.222 |
| 1 | 16 | 0 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 16 | 0 | periodic | 38 | 20 | 72.47 | 172.16 | 0.603 |
| 1 | 16 | 0 | threshold | 40 | 21 | 79.03 | 171.47 | 0.540 |
| 1 | 16 | 0 | predictive | 40 | 27 | 111.84 | 211.62 | 0.402 |
| 1 | 16 | 2 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 16 | 2 | periodic | 38 | 20 | 73.14 | 172.16 | 0.577 |
| 1 | 16 | 2 | threshold | 40 | 24 | 61.86 | 147.48 | 0.582 |
| 1 | 16 | 2 | predictive | 40 | 32 | 108.02 | 205.75 | 0.423 |
| 1 | 16 | 5 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 1 | 16 | 5 | periodic | 38 | 20 | 74.41 | 172.16 | 0.545 |
| 1 | 16 | 5 | threshold | 37 | 20 | 74.41 | 172.16 | 0.545 |
| 1 | 16 | 5 | predictive | 38 | 20 | 74.41 | 172.16 | 0.545 |
| 8 | 4 | 0 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 4 | 0 | periodic | 38 | 7 | 128.61 | 232.28 | 0.222 |
| 8 | 4 | 0 | threshold | 40 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 4 | 0 | predictive | 40 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 4 | 2 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 4 | 2 | periodic | 38 | 7 | 128.74 | 232.28 | 0.222 |
| 8 | 4 | 2 | threshold | 40 | 1 | 146.60 | 249.90 | 0.106 |
| 8 | 4 | 2 | predictive | 40 | 3 | 136.09 | 248.32 | 0.201 |
| 8 | 4 | 5 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 4 | 5 | periodic | 38 | 7 | 129.00 | 232.28 | 0.222 |
| 8 | 4 | 5 | threshold | 35 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 4 | 5 | predictive | 36 | 1 | 146.96 | 260.94 | 0.127 |
| 8 | 16 | 0 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 16 | 0 | periodic | 38 | 10 | 123.22 | 229.12 | 0.423 |
| 8 | 16 | 0 | threshold | 40 | 11 | 107.61 | 201.20 | 0.434 |
| 8 | 16 | 0 | predictive | 40 | 15 | 116.41 | 212.90 | 0.402 |
| 8 | 16 | 2 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 16 | 2 | periodic | 38 | 10 | 123.28 | 229.12 | 0.434 |
| 8 | 16 | 2 | threshold | 40 | 14 | 83.03 | 175.77 | 0.487 |
| 8 | 16 | 2 | predictive | 40 | 20 | 106.16 | 202.75 | 0.439 |
| 8 | 16 | 5 | vo_only | 0 | 0 | 155.82 | 271.06 | 0.106 |
| 8 | 16 | 5 | periodic | 38 | 10 | 123.42 | 229.12 | 0.434 |
| 8 | 16 | 5 | threshold | 37 | 9 | 123.42 | 229.12 | 0.434 |
| 8 | 16 | 5 | predictive | 38 | 10 | 123.42 | 229.12 | 0.434 |

## Limitations

- One previously studied flight; not independent validation or parameter tuning/test separation.
- Frame indices are not sensor timestamps; delays in frames are artificial.
- VO includes an injected 2-degree heading error and calibration on this flight.
- Map renders and evaluation truth share a reference; error independence is not established.
- Affine image/map calibration omits changing attitude correction; not the sibling's full estimator.
- Cached matching is not rerun; historical runtime sums do not establish current hardware savings.
- Fixed recorded path cannot test speed or active-motion changes. Covariance is an uncalibrated proxy.

[Full receipt](results.json) · [Traces](traces.json)
