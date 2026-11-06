# Sample: Blind-flight bench: radar altimeter + Copernicus GLO-30 TRN, six navigators on one harness

`sample:blind-flight-bench` - code and walkthrough in [samples/blind-flight-bench](../../samples/blind-flight-bench/)

Benchmark harness that reproduces the 2026 'Polyot vslepuyu' (Blind flight) hackathon case on four real GLO-30 windows (Khibiny mountains, Middle Urals, Yenisei taiga, the flat Moscow-region map area): 20 km simulated flights at a constant 1500 m baro level, a leading-edge radar altimeter with a 40 deg beam footprint, range noise, dropouts, outliers, baro bias and drift, map error and canopy, delivered as checksummed $GPGGA lines. Scores dead reckoning on the hints, our TERCOM baseline (core.tercom_fix from terrain-heightmap-pf) and our particle filter, each also against a precomputed beam-aware reference map, plus clean-room re-implementations (from README text only) of the GORIZONT multi-hypothesis tracker and the Gagarin MAD/NCC gated pipeline. Leaderboard of median/p95 error at 5/10/20 km, divergence rate, CPU and worst-step latency, and a one-impairment-at-a-time ablation.

**Verification:** ran 2026-11-06 with CPython 3.13.15 + numpy 2.5.4 / scipy 1.18.1 / rasterio 1.5.2 on an Apple M2 Max: regions.py fetched the four GLO-30 windows over public HTTPS through terrain-heightmap-pf/fetch_dem.py; run_bench.py produced out/results.json and the leaderboard (80 flights x 10 navigators, 349 s wall) and --ablation produced out/ablation.md (144 flights x 6 navigators); two full runs gave identical error numbers for unchanged navigators. unittest: 10 passed in the venv; with plain python3 and no third-party packages 3 metric tests pass and 7 skip. Mutating error_at_distances (bisect_left => bisect_right) or the sign of the TERCOM correction makes a test fail. Flights, altimeter, baro error, map error and canopy are simulated with assumed parameters; the GORIZONT and Gagarin navigators are our re-implementations from their README text, not their code, and no team code was run.

## Deep dives

- [copernicus-glo30](../../docs/dataset-cards/copernicus-glo30.md) (dataset-cards)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md), [Sensor fusion and state estimation](../../catalog/concepts/sensor-fusion.md), [GIS, maps and geospatial data](../../catalog/concepts/gis-mapping.md), [Simulation and HIL/SITL](../../catalog/concepts/simulation.md)

**Tags:** `trn`, `tercom`, `radar-altimeter`, `particle-filter`, `benchmark`, `nmea-0183`, `copernicus-glo30`, `beam-footprint`, `hackathon`, `python`, `numpy`, `scipy`

## Related

- explains: [Хакатон: трек «Робототехника и сенсорика», кейс «Полёт вслепую»](../../catalog/resources/iqarium-polet-vslepuyu-hackathon-2026.md)
- explains: [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md)
- explains: [Gagarin - TERCOM for UAVs without GNSS](../../catalog/repos/danilka88__gag27062026.md)
- uses: [Copernicus DEM on AWS Open Data](../../catalog/resources/copernicus-dem-aws.md)
- uses: [Rasterio](../../catalog/repos/rasterio__rasterio.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Evidence matrix](../../docs/evidence-matrix.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Reference stacks: if you only have X, use Y](../../docs/reference-stacks.md) (mentions)

_Indexed by lane(s): samples_
