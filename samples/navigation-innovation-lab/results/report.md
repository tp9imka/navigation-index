# Navigation innovation POCs: measured synthetic evidence

100 paired evaluation seeds per scenario, disjoint from 16 tuning seeds. Descriptor-level / scalar stochastic simulations only. No camera inference, autopilot, aircraft dynamics, hardware, real flight, or formal safety guarantee.

Configuration, per-seed rows, code hashes and timing: [results.json](results.json). One evaluation seed per policy/scenario: [traces.json](traces.json).

## H1

Selected settings: `passive=0.12`, `texture=0.12`, `information=0.12`, `efficient=0`, `no_unknown=0`

| Scenario | Policy | success | false_accept | abstain | steps | distance |
|---|---|---:|---:|---:|---:|---:|
| nominal | passive | 1.0000 | 0.0000 | 0.0000 | 13.1100 | 13.1100 |
| nominal | texture | 1.0000 | 0.0000 | 0.0000 | 13.1100 | 13.1100 |
| nominal | information | 0.9900 | 0.0100 | 0.0000 | 3.1100 | 3.1100 |
| nominal | efficient | 0.9900 | 0.0100 | 0.0000 | 3.1100 | 3.1100 |
| nominal | no_unknown | 0.9900 | 0.0100 | 0.0000 | 3.0100 | 3.0100 |
| indistinguishable | passive | 0.0000 | 0.0000 | 1.0000 | 24.0000 | 24.0000 |
| indistinguishable | texture | 0.0000 | 0.0000 | 1.0000 | 24.0000 | 24.0000 |
| indistinguishable | information | 0.0000 | 0.0000 | 1.0000 | 24.0000 | 24.0000 |
| indistinguishable | efficient | 0.0000 | 0.0000 | 1.0000 | 24.0000 | 24.0000 |
| indistinguishable | no_unknown | 0.0000 | 0.0000 | 1.0000 | 24.0000 | 24.0000 |
| missing_truth | passive | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| missing_truth | texture | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| missing_truth | information | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| missing_truth | efficient | 0.0000 | 0.0000 | 1.0000 | 1.0000 | 1.0000 |
| missing_truth | no_unknown | 0.0000 | 1.0000 | 0.0000 | 1.0000 | 1.0000 |
| map_shift | passive | 0.6300 | 0.0000 | 0.3700 | 10.2200 | 10.2200 |
| map_shift | texture | 0.6300 | 0.0000 | 0.3700 | 10.2200 | 10.2200 |
| map_shift | information | 0.2200 | 0.7200 | 0.0600 | 3.7000 | 3.7000 |
| map_shift | efficient | 0.2200 | 0.7200 | 0.0600 | 3.7000 | 3.7000 |
| map_shift | no_unknown | 0.2800 | 0.7200 | 0.0000 | 2.9400 | 2.9400 |

### Paired differences

Candidate minus baseline; positive favors the candidate for success, negative for RMSE. 95% paired-bootstrap intervals describe this synthetic seed distribution only. Degenerate intervals at 0 or 1 do not establish a zero failure probability.

| Scenario | Candidate | Baseline | Metric | Mean difference | 95% interval |
|---|---|---|---|---:|---|
| nominal | efficient | passive | success | -0.0100 | [-0.0300, 0.0000] |
| nominal | efficient | passive | distance | -10.0000 | [-10.2500, -9.7400] |
| nominal | efficient | passive | false_accept | 0.0100 | [0.0000, 0.0300] |
| nominal | efficient | texture | success | -0.0100 | [-0.0300, 0.0000] |
| nominal | efficient | texture | distance | -10.0000 | [-10.2500, -9.7400] |
| nominal | efficient | texture | false_accept | 0.0100 | [0.0000, 0.0300] |
| nominal | efficient | information | success | 0.0000 | [0.0000, 0.0000] |
| nominal | efficient | information | distance | 0.0000 | [0.0000, 0.0000] |
| nominal | efficient | information | false_accept | 0.0000 | [0.0000, 0.0000] |
| nominal | efficient | no_unknown | success | 0.0000 | [0.0000, 0.0000] |
| nominal | efficient | no_unknown | distance | 0.1000 | [0.0500, 0.1600] |
| nominal | efficient | no_unknown | false_accept | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | passive | success | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | passive | distance | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | passive | false_accept | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | texture | success | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | texture | distance | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | texture | false_accept | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | information | success | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | information | distance | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | information | false_accept | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | no_unknown | success | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | no_unknown | distance | 0.0000 | [0.0000, 0.0000] |
| indistinguishable | efficient | no_unknown | false_accept | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | passive | success | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | passive | distance | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | passive | false_accept | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | texture | success | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | texture | distance | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | texture | false_accept | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | information | success | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | information | distance | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | information | false_accept | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | no_unknown | success | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | no_unknown | distance | 0.0000 | [0.0000, 0.0000] |
| missing_truth | efficient | no_unknown | false_accept | -1.0000 | [-1.0000, -1.0000] |
| map_shift | efficient | passive | success | -0.4100 | [-0.5200, -0.2800] |
| map_shift | efficient | passive | distance | -6.5200 | [-7.4900, -5.4700] |
| map_shift | efficient | passive | false_accept | 0.7200 | [0.6300, 0.8000] |
| map_shift | efficient | texture | success | -0.4100 | [-0.5200, -0.2800] |
| map_shift | efficient | texture | distance | -6.5200 | [-7.4900, -5.4700] |
| map_shift | efficient | texture | false_accept | 0.7200 | [0.6300, 0.8000] |
| map_shift | efficient | information | success | 0.0000 | [0.0000, 0.0000] |
| map_shift | efficient | information | distance | 0.0000 | [0.0000, 0.0000] |
| map_shift | efficient | information | false_accept | 0.0000 | [0.0000, 0.0000] |
| map_shift | efficient | no_unknown | success | -0.0600 | [-0.1100, -0.0200] |
| map_shift | efficient | no_unknown | distance | 0.7600 | [0.4000, 1.1900] |
| map_shift | efficient | no_unknown | false_accept | 0.0000 | [0.0000, 0.0000] |

## H2

Selected settings: `periodic=14`, `threshold=0.8`, `opportunity=10`, `predictive=1`, `predictive_speed=1.3`, `no_latency=1`

| Scenario | Policy | success | violation_fraction | rmse | requests | duration |
|---|---|---:|---:|---:|---:|---:|
| nominal | periodic | 0.4000 | 0.0484 | 1.1738 | 4.0000 | 48.0000 |
| nominal | threshold | 0.5400 | 0.0200 | 0.9525 | 10.0000 | 48.0000 |
| nominal | opportunity | 0.6700 | 0.0197 | 0.9708 | 6.1800 | 48.0000 |
| nominal | predictive | 0.6400 | 0.0156 | 0.9308 | 6.9300 | 48.0000 |
| nominal | predictive_speed | 0.5500 | 0.0143 | 1.0615 | 9.9000 | 73.6200 |
| nominal | no_latency | 0.5700 | 0.0175 | 0.9684 | 6.5200 | 48.0000 |
| slow_compute | periodic | 0.3800 | 0.0539 | 1.2317 | 4.0000 | 48.0000 |
| slow_compute | threshold | 0.3700 | 0.0436 | 1.0966 | 8.9000 | 48.0000 |
| slow_compute | opportunity | 0.4500 | 0.0293 | 1.1220 | 5.0400 | 48.0000 |
| slow_compute | predictive | 0.4100 | 0.0310 | 1.0796 | 4.6100 | 48.0000 |
| slow_compute | predictive_speed | 0.4300 | 0.0244 | 1.1389 | 7.8400 | 74.4850 |
| slow_compute | no_latency | 0.3800 | 0.0375 | 1.0837 | 4.3800 | 48.0000 |
| unexpected_blackout | periodic | 0.3200 | 0.0731 | 1.3765 | 4.0000 | 48.0000 |
| unexpected_blackout | threshold | 0.3100 | 0.0723 | 1.4202 | 10.0000 | 48.0000 |
| unexpected_blackout | opportunity | 0.3200 | 0.0731 | 1.3814 | 6.1800 | 48.0000 |
| unexpected_blackout | predictive | 0.3500 | 0.0730 | 1.2951 | 7.0100 | 48.0000 |
| unexpected_blackout | predictive_speed | 0.2000 | 0.1148 | 1.7602 | 10.0000 | 75.2800 |
| unexpected_blackout | no_latency | 0.3700 | 0.0677 | 1.2884 | 6.8000 | 48.0000 |
| biased_odometry | periodic | 0.1300 | 0.1138 | 1.9484 | 4.0000 | 48.0000 |
| biased_odometry | threshold | 0.3300 | 0.0404 | 1.2508 | 10.0000 | 48.0000 |
| biased_odometry | opportunity | 0.4900 | 0.0368 | 1.3740 | 6.1800 | 48.0000 |
| biased_odometry | predictive | 0.4600 | 0.0321 | 1.2687 | 6.9300 | 48.0000 |
| biased_odometry | predictive_speed | 0.2800 | 0.0325 | 1.4714 | 9.9000 | 73.6200 |
| biased_odometry | no_latency | 0.4200 | 0.0355 | 1.2877 | 6.5200 | 48.0000 |

### Paired differences

Candidate minus baseline; positive favors the candidate for success, negative for RMSE. 95% paired-bootstrap intervals describe this synthetic seed distribution only. Degenerate intervals at 0 or 1 do not establish a zero failure probability.

| Scenario | Candidate | Baseline | Metric | Mean difference | 95% interval |
|---|---|---|---|---:|---|
| nominal | predictive_speed | periodic | success | 0.1500 | [0.0300, 0.2700] |
| nominal | predictive_speed | threshold | success | 0.0100 | [-0.1200, 0.1500] |
| nominal | predictive_speed | opportunity | success | -0.1200 | [-0.2500, 0.0100] |
| nominal | predictive_speed | predictive | success | -0.0900 | [-0.2200, 0.0500] |
| nominal | predictive_speed | no_latency | success | -0.0200 | [-0.1400, 0.1100] |
| nominal | predictive | periodic | success | 0.2400 | [0.1300, 0.3400] |
| nominal | predictive | threshold | success | 0.1000 | [0.0200, 0.1900] |
| nominal | predictive | opportunity | success | -0.0300 | [-0.0900, 0.0300] |
| nominal | predictive | predictive_speed | success | 0.0900 | [-0.0400, 0.2200] |
| nominal | predictive | no_latency | success | 0.0700 | [0.0200, 0.1300] |
| slow_compute | predictive_speed | periodic | success | 0.0500 | [-0.0600, 0.1800] |
| slow_compute | predictive_speed | threshold | success | 0.0600 | [-0.0600, 0.1700] |
| slow_compute | predictive_speed | opportunity | success | -0.0200 | [-0.1500, 0.1000] |
| slow_compute | predictive_speed | predictive | success | 0.0200 | [-0.0900, 0.1400] |
| slow_compute | predictive_speed | no_latency | success | 0.0500 | [-0.0600, 0.1600] |
| slow_compute | predictive | periodic | success | 0.0300 | [-0.0500, 0.1100] |
| slow_compute | predictive | threshold | success | 0.0400 | [-0.0600, 0.1300] |
| slow_compute | predictive | opportunity | success | -0.0400 | [-0.1100, 0.0200] |
| slow_compute | predictive | predictive_speed | success | -0.0200 | [-0.1400, 0.0900] |
| slow_compute | predictive | no_latency | success | 0.0300 | [-0.0500, 0.1100] |
| unexpected_blackout | predictive_speed | periodic | success | -0.1200 | [-0.2200, -0.0200] |
| unexpected_blackout | predictive_speed | threshold | success | -0.1100 | [-0.2200, -0.0100] |
| unexpected_blackout | predictive_speed | opportunity | success | -0.1200 | [-0.2200, -0.0200] |
| unexpected_blackout | predictive_speed | predictive | success | -0.1500 | [-0.2400, -0.0500] |
| unexpected_blackout | predictive_speed | no_latency | success | -0.1700 | [-0.2700, -0.0800] |
| unexpected_blackout | predictive | periodic | success | 0.0300 | [-0.0500, 0.1100] |
| unexpected_blackout | predictive | threshold | success | 0.0400 | [-0.0400, 0.1300] |
| unexpected_blackout | predictive | opportunity | success | 0.0300 | [-0.0500, 0.1100] |
| unexpected_blackout | predictive | predictive_speed | success | 0.1500 | [0.0500, 0.2400] |
| unexpected_blackout | predictive | no_latency | success | -0.0200 | [-0.1100, 0.0700] |
| biased_odometry | predictive_speed | periodic | success | 0.1500 | [0.0400, 0.2600] |
| biased_odometry | predictive_speed | threshold | success | -0.0500 | [-0.1700, 0.0900] |
| biased_odometry | predictive_speed | opportunity | success | -0.2100 | [-0.3400, -0.0700] |
| biased_odometry | predictive_speed | predictive | success | -0.1800 | [-0.3100, -0.0400] |
| biased_odometry | predictive_speed | no_latency | success | -0.1400 | [-0.2700, 0.0000] |
| biased_odometry | predictive | periodic | success | 0.3300 | [0.2300, 0.4300] |
| biased_odometry | predictive | threshold | success | 0.1300 | [0.0400, 0.2400] |
| biased_odometry | predictive | opportunity | success | -0.0300 | [-0.1100, 0.0500] |
| biased_odometry | predictive | predictive_speed | success | 0.1800 | [0.0400, 0.3100] |
| biased_odometry | predictive | no_latency | success | 0.0400 | [-0.0200, 0.1100] |

## H3

Selected settings: `fixed=0.3`, `calibrate_once=0.3`, `always=0.3`, `selective=1`, `no_excitation_gate=0.3`, `no_reference_gate=1`

| Scenario | Policy | velocity_rmse | position_error | updates | k_error |
|---|---|---:|---:|---:|---:|
| nominal | fixed | 0.7345 | 40.5558 | 0.0000 | 0.2000 |
| nominal | calibrate_once | 0.3433 | 3.1763 | 1.0000 | 0.0042 |
| nominal | always | 0.6062 | 31.1405 | 230.9000 | 0.1493 |
| nominal | selective | 0.3579 | 8.4018 | 94.9500 | 0.0227 |
| nominal | no_excitation_gate | 0.3998 | 16.2988 | 150.9000 | 0.0590 |
| nominal | no_reference_gate | 0.3579 | 8.4125 | 94.9700 | 0.0227 |
| no_excitation | fixed | 0.7345 | 40.5558 | 0.0000 | 0.2000 |
| no_excitation | calibrate_once | 0.7060 | 22.9249 | 0.4600 | 0.2300 |
| no_excitation | always | 1.7254 | 94.2009 | 157.4200 | 0.2957 |
| no_excitation | selective | 0.7345 | 40.5558 | 0.0000 | 0.2000 |
| no_excitation | no_excitation_gate | 0.5164 | 20.5394 | 79.1700 | 0.4268 |
| no_excitation | no_reference_gate | 0.7345 | 40.5558 | 0.0000 | 0.2000 |
| reference_outage | fixed | 0.7345 | 40.5558 | 0.0000 | 0.2000 |
| reference_outage | calibrate_once | 0.3439 | 3.2684 | 1.0000 | 0.0058 |
| reference_outage | always | 0.6046 | 31.0910 | 233.0000 | 0.1491 |
| reference_outage | selective | 0.3437 | 3.2820 | 22.7800 | 0.0105 |
| reference_outage | no_excitation_gate | 0.4399 | 21.6188 | 41.0000 | 0.0839 |
| reference_outage | no_reference_gate | 0.3590 | 8.7257 | 96.7000 | 0.0237 |
| parameter_change | fixed | 4.1146 | 326.4417 | 0.0000 | 0.4500 |
| parameter_change | calibrate_once | 2.2660 | 179.2450 | 1.0000 | 0.2514 |
| parameter_change | always | 0.4067 | 20.7392 | 225.7600 | 0.1975 |
| parameter_change | selective | 0.2465 | 5.7941 | 94.9500 | 0.0228 |
| parameter_change | no_excitation_gate | 0.2737 | 11.1166 | 145.7600 | 0.0591 |
| parameter_change | no_reference_gate | 0.2465 | 5.7975 | 94.9600 | 0.0228 |
| nonlinear_drag | fixed | 2.3550 | 183.5871 | 0.0000 | 0.2000 |
| nonlinear_drag | calibrate_once | 0.2507 | 7.1515 | 1.0000 | 0.2484 |
| nonlinear_drag | always | 0.4305 | 21.6447 | 230.9200 | 0.1097 |
| nonlinear_drag | selective | 0.2390 | 3.9233 | 94.9500 | 0.2568 |
| nonlinear_drag | no_excitation_gate | 0.2687 | 9.9047 | 150.9200 | 0.2642 |
| nonlinear_drag | no_reference_gate | 0.2390 | 3.9301 | 94.9600 | 0.2569 |
| unobserved_change | fixed | 3.6329 | 254.8938 | 0.0000 | 0.4500 |
| unobserved_change | calibrate_once | 2.0080 | 133.5911 | 1.0000 | 0.2514 |
| unobserved_change | always | 3.0291 | 211.6424 | 230.9000 | 0.3622 |
| unobserved_change | selective | 2.1158 | 144.1937 | 94.9500 | 0.2465 |
| unobserved_change | no_excitation_gate | 2.2114 | 152.8438 | 150.9000 | 0.2410 |
| unobserved_change | no_reference_gate | 2.1158 | 144.1989 | 110.5600 | 0.2465 |

### Paired differences

Candidate minus baseline; positive favors the candidate for success, negative for RMSE. 95% paired-bootstrap intervals describe this synthetic seed distribution only. Degenerate intervals at 0 or 1 do not establish a zero failure probability.

| Scenario | Candidate | Baseline | Metric | Mean difference | 95% interval |
|---|---|---|---|---:|---|
| nominal | selective | fixed | velocity_rmse | -0.3766 | [-0.3816, -0.3715] |
| nominal | selective | calibrate_once | velocity_rmse | 0.0146 | [0.0101, 0.0193] |
| nominal | selective | always | velocity_rmse | -0.2483 | [-0.2737, -0.2228] |
| nominal | selective | no_excitation_gate | velocity_rmse | -0.0419 | [-0.0561, -0.0282] |
| nominal | selective | no_reference_gate | velocity_rmse | -0.0000 | [-0.0002, 0.0001] |
| no_excitation | selective | fixed | velocity_rmse | 0.0000 | [0.0000, 0.0000] |
| no_excitation | selective | calibrate_once | velocity_rmse | 0.0285 | [-0.0567, 0.1089] |
| no_excitation | selective | always | velocity_rmse | -0.9909 | [-1.2800, -0.7088] |
| no_excitation | selective | no_excitation_gate | velocity_rmse | 0.2180 | [0.1024, 0.3252] |
| no_excitation | selective | no_reference_gate | velocity_rmse | 0.0000 | [0.0000, 0.0000] |
| reference_outage | selective | fixed | velocity_rmse | -0.3907 | [-0.3938, -0.3878] |
| reference_outage | selective | calibrate_once | velocity_rmse | -0.0002 | [-0.0018, 0.0014] |
| reference_outage | selective | always | velocity_rmse | -0.2609 | [-0.2859, -0.2357] |
| reference_outage | selective | no_excitation_gate | velocity_rmse | -0.0962 | [-0.1151, -0.0763] |
| reference_outage | selective | no_reference_gate | velocity_rmse | -0.0153 | [-0.0202, -0.0106] |
| parameter_change | selective | fixed | velocity_rmse | -3.8681 | [-3.8724, -3.8638] |
| parameter_change | selective | calibrate_once | velocity_rmse | -2.0195 | [-2.0261, -2.0132] |
| parameter_change | selective | always | velocity_rmse | -0.1601 | [-0.1724, -0.1479] |
| parameter_change | selective | no_excitation_gate | velocity_rmse | -0.0271 | [-0.0346, -0.0196] |
| parameter_change | selective | no_reference_gate | velocity_rmse | 0.0000 | [0.0000, 0.0000] |
| nonlinear_drag | selective | fixed | velocity_rmse | -2.1160 | [-2.1206, -2.1112] |
| nonlinear_drag | selective | calibrate_once | velocity_rmse | -0.0118 | [-0.0150, -0.0085] |
| nonlinear_drag | selective | always | velocity_rmse | -0.1915 | [-0.2081, -0.1756] |
| nonlinear_drag | selective | no_excitation_gate | velocity_rmse | -0.0297 | [-0.0389, -0.0203] |
| nonlinear_drag | selective | no_reference_gate | velocity_rmse | 0.0000 | [0.0000, 0.0000] |
| unobserved_change | selective | fixed | velocity_rmse | -1.5171 | [-1.5397, -1.4947] |
| unobserved_change | selective | calibrate_once | velocity_rmse | 0.1078 | [0.0852, 0.1308] |
| unobserved_change | selective | always | velocity_rmse | -0.9133 | [-1.0339, -0.7905] |
| unobserved_change | selective | no_excitation_gate | velocity_rmse | -0.0956 | [-0.1476, -0.0427] |
| unobserved_change | selective | no_reference_gate | velocity_rmse | -0.0000 | [-0.0007, 0.0007] |
