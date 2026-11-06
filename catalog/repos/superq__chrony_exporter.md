# chrony_exporter

`repo:superq/chrony_exporter` - <https://github.com/SuperQ/chrony_exporter>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 114 | Go | Apache-2.0 | 2026-11-01 | False | production | high |

Prometheus exporter for chrony tracking, sources and server statistics.

**Why it matters:** Puts clock offset, frequency and source health on a dashboard: the monitoring half of a timing-resilience demo.

**Hackathon notes:** Run next to chronyd, scrape with Prometheus, chart in Grafana; enable the sources collector to see each reference.

**Concepts:** [Timing and time transfer](../concepts/timing.md)

**Tags:** `prometheus`, `monitoring`, `chrony`

**Domains:** multi

## Related

- integrates_with: [chrony](../repos/gitlab.com__chrony__chrony.md)

## Referenced by

- [chrony](../repos/gitlab.com__chrony__chrony.md) (integrates_with)

_Indexed by lane(s): timing_

_GitHub metadata fetched 2026-11-06._
