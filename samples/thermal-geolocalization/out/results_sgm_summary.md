# results_sgm

False fix = accepted with error > 20.0 m. Frames outside the map: 9 (_DJI_20251217133044_0354_T.JPG, _DJI_20251221112203_0152_T.JPG, _DJI_20251221224424_0299_T.JPG, _DJI_20260206192521_0068_T.JPG, _DJI_20260206193337_0199_T.JPG, _DJI_20260206194156_0331_T.JPG, _DJI_20260206195417_0065_T.JPG, _DJI_20260206200237_0197_T.JPG, _DJI_20260206204711_0368_T.JPG)


## SGM retrieval (no geometric check)

| Config | Condition | Frames (on map) | Accepted | Correct | False fixes | Median / p90 err (correct) | Best fit within 20 m, ungated | Median t/frame |
|---|---|---|---|---|---|---|---|---|
| **sgm/sgm110** | **ALL** | 120 (111) | 119 | 29 | 90 | 11.0 / 17.3 m | 29 | 0.52 s |
| sgm/sgm110 | city-day | 20 (19) | 20 | 8 | 12 | 10.0 / 12.0 m | 8 | 0.51 s |
| sgm/sgm110 | city-night | 20 (19) | 20 | 7 | 13 | 13.0 / 18.2 m | 7 | 0.49 s |
| sgm/sgm110 | village-day | 20 (19) | 20 | 7 | 13 | 4.9 / 10.3 m | 7 | 0.54 s |
| sgm/sgm110 | village-day-fog | 20 (20) | 20 | 3 | 17 | 14.5 / 17.5 m | 3 | 0.82 s |
| sgm/sgm110 | village-night | 20 (20) | 20 | 4 | 16 | 16.6 / 18.0 m | 4 | 0.79 s |
| sgm/sgm110 | village-night-fog | 20 (14) | 19 | 0 | 19 | - | 0 | 0.50 s |
| **sgm/sgm512** | **ALL** | 120 (111) | 119 | 27 | 92 | 7.5 / 14.3 m | 26 | 3.63 s |
| sgm/sgm512 | city-day | 20 (19) | 20 | 4 | 16 | 6.2 / 6.7 m | 4 | 3.34 s |
| sgm/sgm512 | city-night | 20 (19) | 20 | 3 | 17 | 11.6 / 12.7 m | 3 | 3.32 s |
| sgm/sgm512 | village-day | 20 (19) | 20 | 9 | 11 | 7.5 / 19.7 m | 8 | 3.87 s |
| sgm/sgm512 | village-day-fog | 20 (20) | 20 | 1 | 19 | 14.4 / 14.4 m | 1 | 3.73 s |
| sgm/sgm512 | village-night | 20 (20) | 20 | 9 | 11 | 8.2 / 14.0 m | 9 | 3.80 s |
| sgm/sgm512 | village-night-fog | 20 (14) | 19 | 1 | 18 | 10.1 / 10.1 m | 1 | 3.77 s |

### SGM distinctiveness margin (2nd-best distance outside 40 m / best)

| Config | Condition | Frames on map | Top-1 within 20 m | margin >= 1.0: ok / false | margin >= 1.1: ok / false | margin >= 1.2: ok / false | margin >= 1.3: ok / false |
|---|---|---|---|---|---|---|---|
| sgm/sgm110 | ALL | 111 | 29 | 29 / 82 | 7 / 14 | 3 / 3 | 2 / 0 |
| sgm/sgm110 | city-day | 19 | 8 | 8 / 11 | 3 / 1 | 2 / 0 | 1 / 0 |
| sgm/sgm110 | city-night | 19 | 7 | 7 / 12 | 1 / 2 | 0 / 0 | 0 / 0 |
| sgm/sgm110 | village-day | 19 | 7 | 7 / 12 | 1 / 1 | 0 / 0 | 0 / 0 |
| sgm/sgm110 | village-day-fog | 20 | 3 | 3 / 17 | 1 / 4 | 0 / 1 | 0 / 0 |
| sgm/sgm110 | village-night | 20 | 4 | 4 / 16 | 1 / 3 | 1 / 0 | 1 / 0 |
| sgm/sgm110 | village-night-fog | 14 | 0 | 0 / 14 | 0 / 3 | 0 / 2 | 0 / 0 |
| sgm/sgm512 | ALL | 111 | 26 | 26 / 85 | 11 / 1 | 1 / 0 | 0 / 0 |
| sgm/sgm512 | city-day | 19 | 4 | 4 / 15 | 3 / 0 | 1 / 0 | 0 / 0 |
| sgm/sgm512 | city-night | 19 | 3 | 3 / 16 | 1 / 0 | 0 / 0 | 0 / 0 |
| sgm/sgm512 | village-day | 19 | 8 | 8 / 11 | 3 / 0 | 0 / 0 | 0 / 0 |
| sgm/sgm512 | village-day-fog | 20 | 1 | 1 / 19 | 1 / 0 | 0 / 0 | 0 / 0 |
| sgm/sgm512 | village-night | 20 | 9 | 9 / 11 | 3 / 1 | 0 / 0 | 0 / 0 |
| sgm/sgm512 | village-night-fog | 14 | 1 | 1 / 13 | 0 / 0 | 0 / 0 | 0 / 0 |
