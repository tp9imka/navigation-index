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
