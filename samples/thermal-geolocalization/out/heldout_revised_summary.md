# heldout_revised

False fix = accepted with error > 20.0 m. Frames outside the map: 5 (_DJI_20260322173430_0264_T.JPG, _DJI_20260322193728_0001_T.JPG, _DJI_20260322194211_0060_T.JPG, _DJI_20260322194656_0118_T.JPG, _DJI_20260322195135_0175_T.JPG)

## Local features + LightGlue

| Config | Condition | Frames (on map) | Accepted | Correct | False fixes | Median / p90 err (correct) | Best fit within 20 m, ungated | Median t/frame |
|---|---|---|---|---|---|---|---|---|
| **aliked/clahe** | **ALL** | 60 (55) | 5 | 5 | 0 | 2.1 / 3.1 m | 18 | 0.10 s |
| aliked/clahe | city-night | 20 (16) | 1 | 1 | 0 | 1.2 / 1.2 m | 5 | 0.11 s |
| aliked/clahe | village-day | 20 (19) | 3 | 3 | 0 | 2.1 / 3.1 m | 9 | 0.11 s |
| aliked/clahe | village-night | 20 (20) | 1 | 1 | 0 | 2.7 / 2.7 m | 4 | 0.10 s |
| **aliked/grad** | **ALL** | 60 (55) | 8 | 8 | 0 | 2.3 / 5.1 m | 22 | 0.12 s |
| aliked/grad | city-night | 20 (16) | 0 | 0 | 0 | - | 5 | 0.12 s |
| aliked/grad | village-day | 20 (19) | 6 | 6 | 0 | 2.2 / 2.7 m | 10 | 0.12 s |
| aliked/grad | village-night | 20 (20) | 2 | 2 | 0 | 6.4 / 9.8 m | 7 | 0.13 s |
| **aliked/raw** | **ALL** | 60 (55) | 7 | 7 | 0 | 2.2 / 3.0 m | 20 | 0.11 s |
| aliked/raw | city-night | 20 (16) | 1 | 1 | 0 | 0.9 / 0.9 m | 6 | 0.14 s |
| aliked/raw | village-day | 20 (19) | 4 | 4 | 0 | 1.9 / 2.8 m | 9 | 0.11 s |
| aliked/raw | village-night | 20 (20) | 2 | 2 | 0 | 2.9 / 3.0 m | 5 | 0.11 s |
| **disk/clahe** | **ALL** | 60 (55) | 7 | 7 | 0 | 3.0 / 3.9 m | 21 | 0.20 s |
| disk/clahe | city-night | 20 (16) | 1 | 1 | 0 | 3.6 / 3.6 m | 6 | 0.20 s |
| disk/clahe | village-day | 20 (19) | 4 | 4 | 0 | 2.9 / 4.0 m | 9 | 0.21 s |
| disk/clahe | village-night | 20 (20) | 2 | 2 | 0 | 2.7 / 3.0 m | 6 | 0.20 s |
| **disk/grad** | **ALL** | 60 (55) | 4 | 4 | 0 | 5.1 / 8.3 m | 19 | 0.22 s |
| disk/grad | city-night | 20 (16) | 0 | 0 | 0 | - | 6 | 0.21 s |
| disk/grad | village-day | 20 (19) | 3 | 3 | 0 | 2.6 / 6.6 m | 8 | 0.22 s |
| disk/grad | village-night | 20 (20) | 1 | 1 | 0 | 8.7 / 8.7 m | 5 | 0.22 s |
| **disk/raw** | **ALL** | 60 (55) | 6 | 6 | 0 | 2.2 / 3.4 m | 25 | 0.22 s |
| disk/raw | city-night | 20 (16) | 0 | 0 | 0 | - | 8 | 0.30 s |
| disk/raw | village-day | 20 (19) | 4 | 4 | 0 | 2.2 / 3.4 m | 11 | 0.21 s |
| disk/raw | village-night | 20 (20) | 2 | 2 | 0 | 2.4 / 2.8 m | 6 | 0.22 s |
| **sift/clahe** | **ALL** | 60 (55) | 0 | 0 | 0 | - | 7 | 0.14 s |
| sift/clahe | city-night | 20 (16) | 0 | 0 | 0 | - | 2 | 0.12 s |
| sift/clahe | village-day | 20 (19) | 0 | 0 | 0 | - | 3 | 0.14 s |
| sift/clahe | village-night | 20 (20) | 0 | 0 | 0 | - | 2 | 0.14 s |
| **sift/grad** | **ALL** | 60 (55) | 0 | 0 | 0 | - | 1 | 0.15 s |
| sift/grad | city-night | 20 (16) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/grad | village-day | 20 (19) | 0 | 0 | 0 | - | 1 | 0.16 s |
| sift/grad | village-night | 20 (20) | 0 | 0 | 0 | - | 0 | 0.15 s |
| **sift/raw** | **ALL** | 60 (55) | 0 | 0 | 0 | - | 2 | 0.14 s |
| sift/raw | city-night | 20 (16) | 0 | 0 | 0 | - | 1 | 0.14 s |
| sift/raw | village-day | 20 (19) | 0 | 0 | 0 | - | 0 | 0.14 s |
| sift/raw | village-night | 20 (20) | 0 | 0 | 0 | - | 1 | 0.14 s |

## Inlier threshold sweep (all other gate checks kept, post-hoc)

| Config | >= 8 inliers | >= 12 inliers | >= 16 inliers | >= 20 inliers | >= 25 inliers | >= 30 inliers |
|---|---|---|---|---|---|---|
| aliked/clahe | 10 ok / 0 false | 7 ok / 0 false | 5 ok / 0 false | 5 ok / 0 false | 5 ok / 0 false | 2 ok / 0 false |
| aliked/grad | 14 ok / 0 false | 8 ok / 0 false | 8 ok / 0 false | 7 ok / 0 false | 6 ok / 0 false | 6 ok / 0 false |
| aliked/raw | 12 ok / 0 false | 7 ok / 0 false | 7 ok / 0 false | 4 ok / 0 false | 1 ok / 0 false | 1 ok / 0 false |
| disk/clahe | 14 ok / 0 false | 8 ok / 0 false | 5 ok / 0 false | 3 ok / 0 false | 3 ok / 0 false | 1 ok / 0 false |
| disk/grad | 9 ok / 0 false | 5 ok / 0 false | 3 ok / 0 false | 3 ok / 0 false | 2 ok / 0 false | 1 ok / 0 false |
| disk/raw | 12 ok / 0 false | 6 ok / 0 false | 6 ok / 0 false | 5 ok / 0 false | 3 ok / 0 false | 3 ok / 0 false |
| sift/clahe | 1 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
| sift/grad | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
| sift/raw | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
