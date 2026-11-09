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
