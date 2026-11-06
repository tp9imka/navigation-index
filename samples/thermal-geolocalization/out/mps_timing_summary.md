# mps_timing

False fix = accepted with error > 20.0 m. Frames outside the map: 2 (_DJI_20260206192521_0068_T.JPG, _DJI_20260206193337_0199_T.JPG)

## Local features + LightGlue

| Config | Condition | Frames (on map) | Accepted | Correct | False fixes | Median / p90 err (correct) | Best fit within 20 m, ungated | Median t/frame |
|---|---|---|---|---|---|---|---|---|
| **aliked/grad** | **ALL** | 24 (22) | 4 | 4 | 0 | 3.4 / 8.1 m | 10 | 0.21 s |
| aliked/grad | city-day | 4 (4) | 1 | 1 | 0 | 3.8 / 3.8 m | 2 | 0.20 s |
| aliked/grad | city-night | 4 (4) | 0 | 0 | 0 | - | 2 | 0.22 s |
| aliked/grad | village-day | 4 (4) | 1 | 1 | 0 | 2.0 / 2.0 m | 2 | 0.25 s |
| aliked/grad | village-day-fog | 4 (4) | 1 | 1 | 0 | 9.9 / 9.9 m | 1 | 0.21 s |
| aliked/grad | village-night | 4 (4) | 1 | 1 | 0 | 3.0 / 3.0 m | 3 | 0.21 s |
| aliked/grad | village-night-fog | 4 (2) | 0 | 0 | 0 | - | 0 | 0.22 s |
| **aliked/raw** | **ALL** | 24 (22) | 5 | 5 | 0 | 4.4 / 6.3 m | 12 | 0.13 s |
| aliked/raw | city-day | 4 (4) | 2 | 2 | 0 | 5.3 / 6.2 m | 4 | 0.13 s |
| aliked/raw | city-night | 4 (4) | 2 | 2 | 0 | 5.2 / 6.0 m | 3 | 0.13 s |
| aliked/raw | village-day | 4 (4) | 1 | 1 | 0 | 1.8 / 1.8 m | 3 | 0.12 s |
| aliked/raw | village-day-fog | 4 (4) | 0 | 0 | 0 | - | 1 | 0.15 s |
| aliked/raw | village-night | 4 (4) | 0 | 0 | 0 | - | 1 | 0.11 s |
| aliked/raw | village-night-fog | 4 (2) | 0 | 0 | 0 | - | 0 | 0.20 s |
| **disk/grad** | **ALL** | 24 (22) | 5 | 5 | 0 | 2.8 / 6.0 m | 7 | 0.29 s |
| disk/grad | city-day | 4 (4) | 1 | 1 | 0 | 7.2 / 7.2 m | 2 | 0.31 s |
| disk/grad | city-night | 4 (4) | 1 | 1 | 0 | 4.2 / 4.2 m | 1 | 0.30 s |
| disk/grad | village-day | 4 (4) | 1 | 1 | 0 | 2.6 / 2.6 m | 1 | 0.28 s |
| disk/grad | village-day-fog | 4 (4) | 0 | 0 | 0 | - | 0 | 0.26 s |
| disk/grad | village-night | 4 (4) | 2 | 2 | 0 | 2.6 / 2.8 m | 3 | 0.30 s |
| disk/grad | village-night-fog | 4 (2) | 0 | 0 | 0 | - | 0 | 0.30 s |
| **disk/raw** | **ALL** | 24 (22) | 2 | 2 | 0 | 3.0 / 3.7 m | 10 | 0.31 s |
| disk/raw | city-day | 4 (4) | 0 | 0 | 0 | - | 3 | 0.37 s |
| disk/raw | city-night | 4 (4) | 1 | 1 | 0 | 3.9 / 3.9 m | 3 | 0.29 s |
| disk/raw | village-day | 4 (4) | 1 | 1 | 0 | 2.2 / 2.2 m | 3 | 0.28 s |
| disk/raw | village-day-fog | 4 (4) | 0 | 0 | 0 | - | 1 | 0.41 s |
| disk/raw | village-night | 4 (4) | 0 | 0 | 0 | - | 0 | 0.31 s |
| disk/raw | village-night-fog | 4 (2) | 0 | 0 | 0 | - | 0 | 0.42 s |
| **sift/grad** | **ALL** | 24 (22) | 0 | 0 | 0 | - | 0 | 0.32 s |
| sift/grad | city-day | 4 (4) | 0 | 0 | 0 | - | 0 | 0.32 s |
| sift/grad | city-night | 4 (4) | 0 | 0 | 0 | - | 0 | 0.37 s |
| sift/grad | village-day | 4 (4) | 0 | 0 | 0 | - | 0 | 0.31 s |
| sift/grad | village-day-fog | 4 (4) | 0 | 0 | 0 | - | 0 | 0.38 s |
| sift/grad | village-night | 4 (4) | 0 | 0 | 0 | - | 0 | 0.30 s |
| sift/grad | village-night-fog | 4 (2) | 0 | 0 | 0 | - | 0 | 0.42 s |
| **sift/raw** | **ALL** | 24 (22) | 0 | 0 | 0 | - | 0 | 0.26 s |
| sift/raw | city-day | 4 (4) | 0 | 0 | 0 | - | 0 | 0.24 s |
| sift/raw | city-night | 4 (4) | 0 | 0 | 0 | - | 0 | 0.25 s |
| sift/raw | village-day | 4 (4) | 0 | 0 | 0 | - | 0 | 0.31 s |
| sift/raw | village-day-fog | 4 (4) | 0 | 0 | 0 | - | 0 | 0.25 s |
| sift/raw | village-night | 4 (4) | 0 | 0 | 0 | - | 0 | 0.29 s |
| sift/raw | village-night-fog | 4 (2) | 0 | 0 | 0 | - | 0 | 0.26 s |

## Inlier threshold sweep (all other gate checks kept, post-hoc)

| Config | >= 8 inliers | >= 12 inliers | >= 16 inliers | >= 20 inliers | >= 25 inliers | >= 30 inliers |
|---|---|---|---|---|---|---|
| aliked/grad | 6 ok / 0 false | 5 ok / 0 false | 4 ok / 0 false | 2 ok / 0 false | 2 ok / 0 false | 0 ok / 0 false |
| aliked/raw | 7 ok / 0 false | 6 ok / 0 false | 5 ok / 0 false | 4 ok / 0 false | 4 ok / 0 false | 4 ok / 0 false |
| disk/grad | 5 ok / 0 false | 5 ok / 0 false | 5 ok / 0 false | 4 ok / 0 false | 3 ok / 0 false | 1 ok / 0 false |
| disk/raw | 8 ok / 0 false | 6 ok / 0 false | 1 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
| sift/grad | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
| sift/raw | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
