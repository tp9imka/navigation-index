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
