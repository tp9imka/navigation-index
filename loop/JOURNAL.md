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
