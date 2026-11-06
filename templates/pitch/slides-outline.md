# Slides outline

A 7-slide deck (6 if you merge slides 6 and 7) for a 3-5 minute pitch. One message per slide;
the slide title is the message. The 9-slide version mapped to judging criteria is
[pitch-deck-outline.md](../pitch-deck-outline.md); use that one when the slot is 5 minutes or
more and judges score per criterion.

Every figure path below was checked to exist in the hub on 2026-11-06. Hub figures are context;
your own screenshot replaces them as soon as you have one. Put the input label (`[real]`,
`[SITL]`, `[synthetic]`, `[mixed]`) in the corner of every figure.

## The deck

| # | Slide (message as title) | Content | Figure | Time (3 / 5 min) |
|---|---|---|---|---|
| 1 | "[Platform] keeps an honest position when GNSS is [jammed / spoofed]" | Team name, one-line hook from [story-bank.md](story-bank.md), scope line ("defensive PNT, no transmission") | Your dashboard screenshot; until then [templates/demo-dashboard/screenshots/spoof-t100.jpg](../demo-dashboard/screenshots/spoof-t100.jpg) (synthetic sample: fused track excluded GNSS, baseline follows the spoofed fixes north) | 0:15 / 0:20 |
| 2 | "Today the [autopilot / receiver] believes the attacker" | One hub number with label and source, one sentence of consequence for the user | Family A: [autopilot-spoof-response/plots/reset_sawtooth.png](../../samples/autopilot-spoof-response/plots/reset_sawtooth.png) `[SITL]`. Family B: [golden-demo-fixedwing/screenshots/fw-t1250.jpg](../../samples/golden-demo-fixedwing/screenshots/fw-t1250.jpg) `[SITL]` (no-monitor aircraft ~800 m west of where it thinks it is). Others: table below | 0:25 / 0:50 |
| 3 | "We check every source before we fuse it" | One diagram: sources => integrity check => filter => output (autopilot / TAK / GCS). Grey out stubs. Name the standard messages (`GPS_INPUT`, CoT, NMEA) | Draw it yourself; pipeline names from [project-repo](../project-repo/) (`PoseSource => NavFilter => IntegrityMonitor => Publisher`) | 0:20 / 0:30 |
| 4 | "Live: attack, alarm, keep navigating" | No text. Dashboard full screen | [demo-dashboard](../demo-dashboard/) live (`?manifest=...`); fallback below | 1:00 / 1:30 |
| 5 | "[Ours] vs [baseline]: [your number]" | Your results table: metric, ours, baseline, runs, label, ground truth. One row "not measured: ..." | Your plot. Shapes to copy: [e2e-visual-nav-vpair/results/error_vs_distance.svg](../../samples/e2e-visual-nav-vpair/results/error_vs_distance.svg) (error vs distance `[real]`), [two-source-integrity-vpair/results/pl_vs_frame.svg](../../samples/two-source-integrity-vpair/results/pl_vs_frame.svg) (PL and error per frame `[mixed]`) | 0:35 / 0:50 |
| 6 | "Where it breaks" | The failure case you ran, the SITL / synthetic gap, thresholds and the data they were set on | The failure frame from your run; hub example [e2e-visual-nav-vpair/results/screenshots/e2e-t198.jpg](../../samples/e2e-visual-nav-vpair/results/screenshots/e2e-t198.jpg) | 0:15 / 0:30 |
| 7 | "Next: [real data / hardware / longer runs]" | Three next steps, the ask, compliance line (public civil signals, file or cabled signals only, no targeting), team | None | 0:10 / 0:30 |

Six-slide version: merge 6 into 5 as a "not measured / breaks when" row.

## Figure per brief family (slide 2 or 5)

| Family ([story bank](story-bank.md#families)) | Figure | Label | What it shows |
|---|---|---|---|
| A. Spoofing on a small UAS | [autopilot-spoof-response/plots/sweep_coherent.png](../../samples/autopilot-spoof-response/plots/sweep_coherent.png) | SITL | Every config believed 96-110 % of a coherent drag |
| A. | [golden-demo/screenshots/golden-t100.jpg](../../samples/golden-demo/screenshots/golden-t100.jpg), [golden-demo-px4/screenshots/px4-t100.jpg](../../samples/golden-demo-px4/screenshots/px4-t100.jpg) | SITL | Monitor vs no-monitor tracks on the dashboard |
| B. Long-range denied nav | [golden-demo-fixedwing/data/xte_vs_distance.svg](../../samples/golden-demo-fixedwing/data/xte_vs_distance.svg) | SITL | Cross-track vs distance after onset, per response |
| B. | [terrain-heightmap-pf/out/v2_errors.png](../../samples/terrain-heightmap-pf/out/v2_errors.png) | synthetic over real GLO-30 | TRN error vs distance by terrain |
| B. | [relative-nav-benchmark/results/screenshots/vpair.jpg](../../samples/relative-nav-benchmark/results/screenshots/vpair.jpg) | real | Nadir VO drift on VPAIR |
| C. Integrity | [two-source-integrity-vpair/results/pl_vs_frame.svg](../../samples/two-source-integrity-vpair/results/pl_vs_frame.svg), [two-source-integrity-vpair/results/screenshots/two-source-t130.jpg](../../samples/two-source-integrity-vpair/results/screenshots/two-source-t130.jpg) | mixed | PL vs error per frame; dashboard with PL ring |
| D. Interference awareness | [osint-jamming-map/out/map.png](../../samples/osint-jamming-map/out/map.png) | real | ADS-B hexes (left), Sentinel-1 RFI (right) |
| D. | [templates/demo-dashboard/screenshots/jam-t90.jpg](../demo-dashboard/screenshots/jam-t90.jpg) | synthetic | Jamming zone on the dashboard |
| E. Timing | none in the hub | - | Plot your own TE vs time; do not borrow a figure from another family |
| F. Maritime | [usv-gnss-denied-nav/example_output/spoof-coastal.png](../../samples/usv-gnss-denied-nav/example_output/spoof-coastal.png), [usv-gnss-denied-nav/example_output/dashboard-spoof-coastal-t1700.jpg](../../samples/usv-gnss-denied-nav/example_output/dashboard-spoof-coastal-t1700.jpg) | synthetic | Coastal spoof, monitor vs baseline |
| F. Dismounted / swarm | none in the hub | - | Screenshot your own run |

## Demo failed live: fallback plan

No recorded video or GIF ships in the hub (checked 2026-11-06: no `.mp4`, `.webm`, `.mov` or
`.gif` anywhere). You record your own. Full procedure: [demo-script.md](../demo-script.md#fallback-plan).

| Layer | What | Where it lives | Made when |
|---|---|---|---|
| 1. Live | `make demo` + dashboard on localhost, no network | Demo laptop | Rehearsed at H+36 |
| 2. Recorded video | Full demo, screen + narration, commit hash on the first frame; second 30 s clip of attack + alarm only | Demo laptop, laptop 2, USB stick; plays offline | H+30 to H+36 ([demo-script.md](../demo-script.md#recording-the-backup-h30-to-h36)) |
| 3. GIF in the deck | The 30 s clip as a GIF embedded in slide 4, so the deck itself carries the demo | Deck file | H+36. Convert with whatever is already on the laptop (e.g. `ffmpeg` if installed); do not install tools on demo day |
| 4. Screenshots | Three stills: before attack, alarm, end state. The dashboard's S key saves `navdash-t<time>.png` with a metrics box ([dashboard controls](../demo-dashboard/README.md#controls)); samples with a `screenshot.sh` (golden-demo, golden-demo-px4, golden-demo-fixedwing, e2e-visual-nav-vpair, two-source-integrity-vpair) show how to capture headless | `slides/fallback/` in your repo | H+30 |
| 5. Hub stills | Last resort, labelled "reference run, not ours": [demo-dashboard/screenshots/spoof-t100.jpg](../demo-dashboard/screenshots/spoof-t100.jpg), [golden-demo/screenshots/golden-t36.jpg](../../samples/golden-demo/screenshots/golden-t36.jpg) (just after detection), [golden-demo/screenshots/golden-t100.jpg](../../samples/golden-demo/screenshots/golden-t100.jpg) | Hub | Already there |

Switch rule: no output on the map 10 s after start => say "switching to the recording made at
H+30" and play layer 2. Never debug on stage. Offer the live run at the judging table afterwards.
