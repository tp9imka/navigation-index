# main_revised

False fix = accepted with error > 20.0 m. Frames outside the map: 9 (_DJI_20251217133044_0354_T.JPG, _DJI_20251221112203_0152_T.JPG, _DJI_20251221224424_0299_T.JPG, _DJI_20260206192521_0068_T.JPG, _DJI_20260206193337_0199_T.JPG, _DJI_20260206194156_0331_T.JPG, _DJI_20260206195417_0065_T.JPG, _DJI_20260206200237_0197_T.JPG, _DJI_20260206204711_0368_T.JPG)

## Local features + LightGlue

| Config | Condition | Frames (on map) | Accepted | Correct | False fixes | Median / p90 err (correct) | Best fit within 20 m, ungated | Median t/frame |
|---|---|---|---|---|---|---|---|---|
| **aliked/clahe** | **ALL** | 120 (111) | 13 | 13 | 0 | 3.7 / 5.8 m | 43 | 0.13 s |
| aliked/clahe | city-day | 20 (19) | 5 | 5 | 0 | 4.8 / 5.7 m | 15 | 0.13 s |
| aliked/clahe | city-night | 20 (19) | 3 | 3 | 0 | 4.1 / 4.4 m | 9 | 0.12 s |
| aliked/clahe | village-day | 20 (19) | 3 | 3 | 0 | 2.6 / 3.3 m | 10 | 0.13 s |
| aliked/clahe | village-day-fog | 20 (20) | 1 | 1 | 0 | 8.2 / 8.2 m | 2 | 0.12 s |
| aliked/clahe | village-night | 20 (20) | 1 | 1 | 0 | 3.1 / 3.1 m | 7 | 0.12 s |
| aliked/clahe | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.13 s |
| **aliked/grad** | **ALL** | 120 (111) | 18 | 18 | 0 | 2.6 / 4.2 m | 45 | 0.14 s |
| aliked/grad | city-day | 20 (19) | 4 | 4 | 0 | 3.7 / 4.1 m | 9 | 0.14 s |
| aliked/grad | city-night | 20 (19) | 0 | 0 | 0 | - | 7 | 0.14 s |
| aliked/grad | village-day | 20 (19) | 5 | 5 | 0 | 0.7 / 4.0 m | 10 | 0.14 s |
| aliked/grad | village-day-fog | 20 (20) | 0 | 0 | 0 | - | 2 | 0.14 s |
| aliked/grad | village-night | 20 (20) | 9 | 9 | 0 | 2.6 / 3.3 m | 17 | 0.14 s |
| aliked/grad | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.14 s |
| **aliked/raw** | **ALL** | 120 (111) | 16 | 16 | 0 | 3.3 / 5.7 m | 55 | 0.13 s |
| aliked/raw | city-day | 20 (19) | 7 | 7 | 0 | 4.1 / 5.5 m | 17 | 0.15 s |
| aliked/raw | city-night | 20 (19) | 2 | 2 | 0 | 5.1 / 6.0 m | 13 | 0.12 s |
| aliked/raw | village-day | 20 (19) | 6 | 6 | 0 | 1.3 / 3.8 m | 13 | 0.13 s |
| aliked/raw | village-day-fog | 20 (20) | 0 | 0 | 0 | - | 2 | 0.12 s |
| aliked/raw | village-night | 20 (20) | 1 | 1 | 0 | 1.6 / 1.6 m | 10 | 0.12 s |
| aliked/raw | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.14 s |
| **disk/clahe** | **ALL** | 120 (111) | 10 | 10 | 0 | 3.4 / 5.9 m | 36 | 0.26 s |
| disk/clahe | city-day | 20 (19) | 5 | 5 | 0 | 3.3 / 6.0 m | 12 | 0.26 s |
| disk/clahe | city-night | 20 (19) | 2 | 2 | 0 | 4.8 / 5.5 m | 7 | 0.26 s |
| disk/clahe | village-day | 20 (19) | 3 | 3 | 0 | 1.6 / 3.1 m | 10 | 0.27 s |
| disk/clahe | village-day-fog | 20 (20) | 0 | 0 | 0 | - | 1 | 0.26 s |
| disk/clahe | village-night | 20 (20) | 0 | 0 | 0 | - | 6 | 0.25 s |
| disk/clahe | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.28 s |
| **disk/grad** | **ALL** | 120 (111) | 15 | 15 | 0 | 3.2 / 4.8 m | 30 | 0.29 s |
| disk/grad | city-day | 20 (19) | 4 | 4 | 0 | 3.6 / 6.2 m | 6 | 0.29 s |
| disk/grad | city-night | 20 (19) | 2 | 2 | 0 | 4.5 / 4.8 m | 7 | 0.28 s |
| disk/grad | village-day | 20 (19) | 2 | 2 | 0 | 1.5 / 1.9 m | 5 | 0.29 s |
| disk/grad | village-day-fog | 20 (20) | 1 | 1 | 0 | 1.1 / 1.1 m | 1 | 0.30 s |
| disk/grad | village-night | 20 (20) | 6 | 6 | 0 | 2.9 / 4.5 m | 11 | 0.30 s |
| disk/grad | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.31 s |
| **disk/raw** | **ALL** | 120 (111) | 11 | 11 | 0 | 1.8 / 4.5 m | 45 | 0.26 s |
| disk/raw | city-day | 20 (19) | 5 | 5 | 0 | 3.4 / 4.1 m | 13 | 0.27 s |
| disk/raw | city-night | 20 (19) | 1 | 1 | 0 | 4.8 / 4.8 m | 12 | 0.25 s |
| disk/raw | village-day | 20 (19) | 3 | 3 | 0 | 1.5 / 1.7 m | 12 | 0.26 s |
| disk/raw | village-day-fog | 20 (20) | 1 | 1 | 0 | 0.6 / 0.6 m | 2 | 0.26 s |
| disk/raw | village-night | 20 (20) | 1 | 1 | 0 | 1.9 / 1.9 m | 6 | 0.24 s |
| disk/raw | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.40 s |
| **sift/clahe** | **ALL** | 120 (111) | 0 | 0 | 0 | - | 3 | 0.15 s |
| sift/clahe | city-day | 20 (19) | 0 | 0 | 0 | - | 1 | 0.15 s |
| sift/clahe | city-night | 20 (19) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/clahe | village-day | 20 (19) | 0 | 0 | 0 | - | 1 | 0.16 s |
| sift/clahe | village-day-fog | 20 (20) | 0 | 0 | 0 | - | 1 | 0.14 s |
| sift/clahe | village-night | 20 (20) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/clahe | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.15 s |
| **sift/grad** | **ALL** | 120 (111) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/grad | city-day | 20 (19) | 0 | 0 | 0 | - | 0 | 0.16 s |
| sift/grad | city-night | 20 (19) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/grad | village-day | 20 (19) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/grad | village-day-fog | 20 (20) | 0 | 0 | 0 | - | 0 | 0.16 s |
| sift/grad | village-night | 20 (20) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/grad | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.17 s |
| **sift/raw** | **ALL** | 120 (111) | 1 | 1 | 0 | 3.1 / 3.1 m | 4 | 0.14 s |
| sift/raw | city-day | 20 (19) | 0 | 0 | 0 | - | 2 | 0.14 s |
| sift/raw | city-night | 20 (19) | 0 | 0 | 0 | - | 0 | 0.15 s |
| sift/raw | village-day | 20 (19) | 1 | 1 | 0 | 3.1 / 3.1 m | 2 | 0.14 s |
| sift/raw | village-day-fog | 20 (20) | 0 | 0 | 0 | - | 0 | 0.14 s |
| sift/raw | village-night | 20 (20) | 0 | 0 | 0 | - | 0 | 0.14 s |
| sift/raw | village-night-fog | 20 (14) | 0 | 0 | 0 | - | 0 | 0.14 s |

## Inlier threshold sweep (all other gate checks kept, post-hoc)

| Config | >= 8 inliers | >= 12 inliers | >= 16 inliers | >= 20 inliers | >= 25 inliers | >= 30 inliers |
|---|---|---|---|---|---|---|
| aliked/clahe | 28 ok / 0 false | 17 ok / 0 false | 12 ok / 0 false | 9 ok / 0 false | 6 ok / 0 false | 5 ok / 0 false |
| aliked/grad | 27 ok / 0 false | 22 ok / 0 false | 18 ok / 0 false | 14 ok / 0 false | 12 ok / 0 false | 7 ok / 0 false |
| aliked/raw | 36 ok / 0 false | 24 ok / 0 false | 15 ok / 0 false | 10 ok / 0 false | 8 ok / 0 false | 7 ok / 0 false |
| disk/clahe | 19 ok / 0 false | 12 ok / 0 false | 10 ok / 0 false | 8 ok / 0 false | 6 ok / 0 false | 4 ok / 0 false |
| disk/grad | 19 ok / 0 false | 17 ok / 0 false | 15 ok / 0 false | 12 ok / 0 false | 10 ok / 0 false | 8 ok / 0 false |
| disk/raw | 28 ok / 0 false | 18 ok / 0 false | 10 ok / 0 false | 9 ok / 0 false | 7 ok / 0 false | 4 ok / 0 false |
| sift/clahe | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
| sift/grad | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
| sift/raw | 1 ok / 0 false | 1 ok / 0 false | 1 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false | 0 ok / 0 false |
