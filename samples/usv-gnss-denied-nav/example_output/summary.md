| seed | scenario | config | RMS m | p95 m | max m | final m | max during attack m | alarm s | exclusion s | offset at alarm m | false alarms / exclusions |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | clean | dr | 302.1 | 504.6 | 532.7 | 532.7 | - | - | - | - | 0 / 0 |
| 1 | clean | gnss_dr | 3.1 | 5.4 | 6.0 | 3.1 | - | - | - | - | 0 / 0 |
| 1 | clean | single | 3.0 | 5.2 | 6.0 | 3.0 | - | - | - | - | 0 / 0 |
| 1 | clean | monitor | 3.0 | 5.1 | 6.0 | 3.0 | - | - | - | - | 0 / 0 |
| 1 | spoof-coastal | dr | 302.1 | 504.6 | 532.7 | 532.7 | 532.7 | - | - | - | 0 / 0 |
| 1 | spoof-coastal | gnss_dr | 618.1 | 1277.3 | 1392.2 | 1392.2 | 1392.2 | - | - | - | 0 / 0 |
| 1 | spoof-coastal | single | 618.0 | 1277.2 | 1392.1 | 1392.1 | 1392.1 | - | - | - | 0 / 0 |
| 1 | spoof-coastal | monitor | 2.1 | 4.8 | 10.0 | 1.0 | 10.0 | 130 | 130 | 25.4 | 0 / 0 |
| 1 | spoof-open | dr | 302.1 | 504.6 | 532.7 | 532.7 | 532.7 | - | - | - | 0 / 0 |
| 1 | spoof-open | gnss_dr | 1276.4 | 2137.4 | 2259.7 | 2259.7 | 2259.7 | - | - | - | 0 / 0 |
| 1 | spoof-open | single | 1276.4 | 2137.4 | 2259.7 | 2259.7 | 2259.7 | - | - | - | 0 / 0 |
| 1 | spoof-open | monitor | 9.6 | 4.0 | 81.6 | 1.0 | 81.6 | 207 | 250 | 64.2 | 0 / 0 |
| 1 | jam | dr | 302.1 | 504.6 | 532.7 | 532.7 | 532.7 | - | - | - | 0 / 0 |
| 1 | jam | gnss_dr | 17.5 | 29.9 | 33.6 | 33.6 | 33.6 | - | - | - | 0 / 0 |
| 1 | jam | single | 2.1 | 4.6 | 5.9 | 1.0 | 3.6 | - | - | - | 0 / 0 |
| 1 | jam | monitor | 2.1 | 4.6 | 6.0 | 1.0 | 3.6 | - | - | - | 0 / 0 |
| 1 | spoof-coastal-1500m | dr | 302.1 | 504.6 | 532.7 | 532.7 | 532.7 | - | - | - | 0 / 0 |
| 1 | spoof-coastal-1500m | gnss_dr | 618.1 | 1277.3 | 1392.2 | 1392.2 | 1392.2 | - | - | - | 0 / 0 |
| 1 | spoof-coastal-1500m | single | 618.2 | 1277.4 | 1392.2 | 1392.2 | 1392.2 | - | - | - | 0 / 0 |
| 1 | spoof-coastal-1500m | monitor | 392.1 | 907.0 | 1023.6 | 134.0 | 1023.6 | 592 | 1810 | 295.2 | 0 / 0 |

Radar-chart matching by route leg, monitor run, radar "default", seed 1, clean:

| leg | scans | outcomes | accepted-fix error median / p95 m |
|---|---|---|---|
| open water by Lillgrund | 139 | degenerate 1, few_inliers 13, few_returns 42, no_chart_match 8, ok 75 | 3.7 / 8.6 |
| Drogden south | 240 | ambiguous 2, ok 238 | 1.8 / 4.8 |
| Drogden channel | 166 | ok 166 | 2.0 / 4.7 |
| off Kastrup | 164 | ok 164 | 1.7 / 3.6 |
| Kongedybet / Middelgrunden | 77 | ok 77 | 1.1 / 3.1 |

Radar-chart matching by route leg, monitor run, radar {"max_range": 1500.0}, seed 1, spoof-coastal-1500m:

| leg | scans | outcomes | accepted-fix error median / p95 m |
|---|---|---|---|
| open water by Lillgrund | 139 | few_returns 139 | - / - |
| Drogden south | 240 | degenerate 3, few_inliers 18, few_returns 172, no_chart_match 47 | - / - |
| Drogden channel | 166 | ambiguous 6, degenerate 37, few_inliers 8, few_returns 15, no_chart_match 49, ok 51 | 4.4 / 14.9 |
| off Kastrup | 164 | ambiguous 13, degenerate 12, few_inliers 4, few_returns 89, no_chart_match 7, ok 39 | 1.9 / 110.0 |
| Kongedybet / Middelgrunden | 77 | ambiguous 5, no_chart_match 56, ok 16 | 1.4 / 148.9 |
