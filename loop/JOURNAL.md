# Loop journal

Append-only. One entry per wave or land, newest at the bottom. Format:

```
## <date> wave <n>
- launched: <item-id> => <job-id>
- landed: <item-id> => <commit sha> (<key result>)
- failed / retry / needs-human: <item-id> - <reason>
- claims checked: <held>/<checked>
- notes: <what changed the plan>
```

## 2026-11-09 setup
- Loop defined: [DRIVER.md](DRIVER.md), [BACKLOG.md](BACKLOG.md), [brief-template.md](brief-template.md).
- Base: origin/main at d7c068d. Close-area research round landed in dbafbff.
- Kiro 2.21.2 ok (engine v3, claude-opus-5.5). farmout scores kiro implement 55/99 ok => keep jobs small.

## 2026-11-09 wave 1
- launched: 01 => 20261109-114530-kiro-ff32, 02a => -114531-kiro-b178, 05 => -114531-kiro-9634, 07 => -114531-kiro-6c7a, 12 => -114531-kiro-286f, 13 and 18 queued (slots shared with other sessions).
- needs-human: 09, 15 - no sitl-docker images on this machine; building them pulls base images.
- notes: 09 swapped out of wave 1 for 18. Arena and adapter briefs carry the same published Pose/RangeScan/Setpoint interface.
- landed: 18 => d0dc4d8 (pitch story + demo script; claims checked 1/1: OpenVINS ATE 0.36 m matches relative-nav-benchmark)
- landed: 07 => 530ea69 (rows 31-33, decode_eval close-area n=8 hit@1 1.00; claims checked 2/2: decode_eval and decode top row re-run by driver)
- landed: 02a => af25b73 (mock loop reaches goal at 0.096 m; claims checked 2/2: interface matches the published one field for field, test and example re-run by driver)
- landed: 13 => d4180ee (headline as worded exists: Tan et al. IROS 2025, Zhang/Li/Clark TAC 2025; claim narrowed to the hover-on-ambiguity composition; claims checked 3/3: both arXiv titles and authors, tiiuae repo has no license)
- notes: kill test (06) must add FT-CBF residual dropping and Tan union-of-states arms.
- landed: 01 => 6d72ea1 (straight baseline reached 40 %, stuck 60 % on 20 random layouts; 0 % on traps; EDT 2M cells 183 ms; claims checked 3/3: driver re-ran run.py with identical table, smoke skips under plain python3, interface matches templates/drone-adapter)
- notes: sitl-docker evidence says the images were built on 2026-11-06 but none exist now (pruned?). 09 and 15 stay needs-human.
- landed: 05 => cf93eb1 (shipped PX4-CBF has no FoV constraint; MR-CBF and gatekeeper already take an error bound; claims checked 3/3: Belief-CBF DOI via crossref, PX4 fork cbf HEAD e7ef0c61 and commit 338fb51f via gh api)
- notes: kill test (06) arms now: none, CP-stop, PX4-CBF shipped, PX4-CBF with FoV QP, Belief-CBF (with covariance prediction), MR-CBF fixed bound, FT-CBF residual dropping, Tan union of states, ours. Record metadata fixes and upstream-findings items from job 9634 go to sweep 27.
- launched wave 2: 03, 04, 10, 11, 08a, 14, 16 (queued as slots free); 02b running.
- landed: 12 => 914e5e6 (top Day-1 shape: marked B in a small known arena; claims checked 1/1: LSY sensor_range 0.7 in level2.toml). Worker ignored an embedded 'Agent Instructions' block in the SUAS handbook.
- landed: 02b => 46a6e40 (4 driver stubs, unrun, lazy SDK imports; driver fix: Tello ranges() now an empty scan instead of 4 x inf that reads as clear; claims checked 2/2: each driver class has the 3 methods, smoke test passes)
- landed: 04 => 7616f5c (FAIL vs expectation: 0 % collisions under all faults for range-only planners; freest_beam reach 86 => 40 % under bias; claims checked 2/2: drift target matches relative-nav-benchmark, summary table matches results file)
- fix: tools/check_links.py cached listdir (took >10 min at load 90, now 4.5 s).
- landed: 03 => 7a55438 (known map 100 % all families; unknown map 80 % narrow_gap, loops not stops; claims checked 2/2: results table matches file, held-out seed 3 u_trap 10/10)
- landed: 11 => 881d7e1 (log scorer matches arena scorer; claims checked 1/1 re-run on hand log); 10 => bcd1b17 (APF+escape 92 % u_trap with 72 beams; 4-beam fan: VFH+ collides 72-98 %, APF 8-54 %; claims checked 2/2: table row matches results, smoke skips)
- landed: 08a => 226dd1f (make test 6/6, mock A=>B 0.194 m; driver re-ran both); 16 => 6e12000 (0.16 m tag >=90 % detection to 5 m frontal, approach 50/50 within 0.1 m; smoke re-run); 14 => 9501e7c (intake tree; stale gap notes: drivers and A* now exist - sweep fixes)

## 2026-11-09 wave 3
- launched: 06a, 27 (sweep), 20, 21; docs track: 29 (audit, read job), 30 (showcase); research 23, 24.
- Ivan asked for a docs/navigation update for agents plus a showcase UI => items 29-31.
- gate slip: pushed fc04bfc..b3b8fe3 with 4 broken links in an INTEGRATION.md; fixed in 27a85cf. Briefs now require check_links broken 0.
- landed: 24 => 4c0dca7 (plan: OpenVINS stereo NEES on UZH-FPV in ~25 min, needs Docker; claims checked 2/2: Lisus arXiv title, no cached ov_state_std.txt on this machine). 25 => needs-human.
- failed: 30 showcase attempt 1 (Kiro opened a >8000 px full-page screenshot, API 400); relaunched as 'showcase retry2' with a viewport-only rule.
- landed: 23 => 04e147c (4 x 27 deg beams cover 30 % of the circle; glass invisible; claims checked 1/1: BatDeck arXiv title). New item 32: arena sensor realism. Doc 08 README row => WP E.
- landed: 27 => 42e9fe1 (decoder rows 31-33 start-from now links real samples; evidence-matrix rows; kill-test arms list in doc 04; record and upstream-findings fixes; driver re-ran full gate: all green, no unlinked-sample warnings)
- landed: 06a => 1d1fd4a. KEY: all-visible => F1 and F2 at 0 % collisions in every fault case (doc 04 fail condition holds there). Map-only obstacles => F2 3-11 %, every hit on an unsensed obstacle. Headline survives only for obstacles the sensor cannot see. Claims checked 2/2: summary table matches results file; smoke passes in venv, skips without.
- landed: 30 => 1ea1d6c (showcase: hero counters, canvas replay of 4 arena runs, 50-card gallery with honest status/input badges; driver rendered it in headless Chrome: replay and gallery draw correctly; ?run= query does not preselect a run - minor)
- landed: 31C => 1cd8926 (AGENTS.md reaches every close-area target in 1 hop, was none; Q1 5 => 2-3 hops, Q2 4-6 => 2; driver removed the stale decoder note since sweep 27 fixed rows 31-33). MCP note in AGENTS.md waits for WP B.
- landed: 31F => c8d9878 (8/8 template READMEs have a trigger line; templates/README reaches every close-area asset in 1 hop; driver updated stale 'not run / does not exist' lines in pitch and demo script with kill test part a)
- landed: 31B => 5403b74 (search 'drone adapter send_setpoint' => drone-adapter README rank 1; MCP read opens templates/**/*.md and samples/<name>/*.md with .md-only, hidden/results dirs refused, resolve() containment kept - driver reviewed; decode low/none => up to 3 guides; full gate incl. node site tests green). Known cost: search recall@10 0.671 => 0.663; licences question lost model-weights-licenses from top 3.
- landed: 20 => 98f1e86 (A* 100 % at every gap 0.4-1.2 m; RRT* 1000: 28 % at 0.4 m, 5000: 86 % at 8x A* time; arena flights both 100 % but RRT* clearance 0.27 vs 0.64 m; side finding: 0.15 m fallback paths can graze; claims checked 2/2: sweep table matches, smoke skips)
- landed: 21 => 8f39a8e (MPC and carrot both 100 % reached, 0 % collisions; corridor rarely binds; 0.22 ms median solve; claims checked 2/2: osqp licence from wheel metadata, smoke skips)
- landed: 31G => 95a8417 (arena readiness: cpu, macos-arm64, offline verified, 16.5 s setup; README 'which planner' table; CONTRACT reference pose source/A*/log format; test_readiness passes)
- landed: 22 => ac5a899 (relocalization: single-hypothesis + scan-map consistency check 100 % reached under dropout and jump vs 64 / 36 % estimator only; multi-hypothesis never commits wrong but hovers forever: 80 / 93 %; symmetric corridor: multi hovers 20/20. Claims checked 2/2: table matches file, smoke skips). Backup headline is now measured.
- landed: 31I => 3b25e5c (5 index READMEs get trigger lines and the standard table; SPRIN-D digest indexed; close-area-nav 1 hop from landscape/primer/paper-digests). Follow-ups for a tooling job: md_plain mangles 'A=>B'; GUIDE_GLOBS skip paper-digests and dataset-cards READMEs; card_index.py trigger line.
- landed: 31E => e7f45ae (docs/research/README.md index; driver replaced stale 'kill test not in checkout' status with part a results; linked from docs/README). Doc 04 still has abstract-only labels outside 3.1 => follow-up.
- landed: 31D => d705042 (close-area-a-to-b cheat sheet; Challenge 2 section 4.1 close-area working set; Day-0 runbook close-area branch; worker re-ran 4 first commands, identical numbers). AGENTS.md now links the sheet directly.

## 2026-11-09 re-plan 1 (fable, base a766e5e)
- added 34-45; dropped 17; parked 26; 06 part c folded into 37; 28 amended (tuned/held-out column) to run last.
- risk noted: do not write PASS for the headline before 37 (held-out seeds).
- launched wave 4: 35, 36, 38, 43.
- landed: 32 => 0a62876 (job hit timeout after writing results; crazyflie preset on glass family: 90 % / 100 % collisions; bright light 38 % collisions for A* unknown map on random; parity 50/50 with run.evaluate; claims checked 2/2: table and notes consistent, parity line present)
- gate slip 2: a timed-out job cannot be landed; the chain used ';' so the README section pushed (0a62876) before its files; fixed with git apply of the job patch in f25d9c3. Rule: land chains use '&&' only, and end with gate.sh.
- landed: 06b => fe3bb5f (job timed out after results; driver applied the patch and wrote README Part b from result files). KEY: MR-CBF fixed eps 0.2 m => 0-1 % collisions in all fault cases with unsensed obstacles at F2-level reach. Ours must beat that. Belief-CBF misses jumps (9 %). Claims checked 2/2: summary table matches json-derived md; smoke passes in venv.
- landed: 06c => 559d7d8 (timed out, applied by driver; PL breaches <= 1.3e-4 in all faults; median PL 0.41-0.59 m; maxsep wrong exclusions 9-19 runs). Item 34 unblocked.
- landed: 22b/33 => 5683770 (random layouts: info-gain move 99-100 % reached, 0 wrong commits vs single 100 % with 2-4; corridor 70-80 % vs single 100 % with 8 wrong commits; driver ran held-out seed 1: same picture). Item 39 (pivot kit) unblocked.

## 2026-11-09 wave 5 (Ivan: more arenas, more algorithms, a playground)
- added 46-50; recommendation: playground runs the real Python arena via Pyodide (one implementation), gated on the 48a timing spike.
- launched 46a, 48a, 49, 50.
