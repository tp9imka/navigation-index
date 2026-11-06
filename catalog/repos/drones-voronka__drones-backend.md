# Полёт вслепую - GCS with terrain-referenced navigation

`repo:drones-voronka/drones-backend` - <https://github.com/drones-voronka/drones-backend>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 0 | Python | ? | 2026-06-28 | False | research-prototype | medium |

Another team's take on the 2026 'Полёт вслепую' case, built as a ground control station for a UAV swarm: a Go telemetry ingestion gateway feeds RabbitMQ, a Python worker runs a particle-filter terrain-referenced navigation core on a DEM (rasterio) with Qdrant used for relocalisation, and MAVSDK-Python bridges to MAVLink vehicles. Full Docker Compose stack with PostgreSQL, Redis, Prometheus/Grafana/Loki.

**Why it matters:** An architecture reference for putting a TRN estimator behind a real telemetry pipeline and operator panel rather than in a notebook.

**Hackathon notes:** docker compose up brings the whole stack; heavy for a 24-48h build. Useful mainly for the particle-filter TRN module and the MAVSDK bridge pattern. Docs in docs/ (domain.md covers TRN).

## Deep dives

- [blind-flight-teardown](../../docs/landscape/blind-flight-teardown.md) (landscape)
- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Terrain-relative navigation](../../catalog/concepts/terrain-nav.md), [MAVLink, ground control and C2 links](../../catalog/concepts/mavlink-gcs.md), [Swarms and multi-agent navigation](../../catalog/concepts/multi-agent.md), [Situational awareness and C2 interop](../../catalog/concepts/situational-awareness.md)

**Tags:** `lang:ru`, `trn`, `particle-filter`, `mavsdk`, `fastapi`, `go`, `docker`, `hackathon`

**Domains:** air

## Related

- alternative_to: [Hackathon-Blind-Flight (team GORIZONT)](../../catalog/repos/t1gr20an06-k__hackathon-blind-flight.md)
- alternative_to: [FlyingBlind_Hakaton](../../catalog/repos/solarwarlock__flyingblind_hakaton.md)
- alternative_to: [KROT (Где мы, Бариста?) - terrain correlation from radar altimeter](../../catalog/repos/rub1kub__where-are-we-barista.md)
- depends_on: [MAVSDK-Python](../../catalog/repos/mavlink__mavsdk-python.md)

## Referenced by

- [Day-0 runbook: the first 3 hours](../../docs/day0-runbook.md) (mentions)
- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- ["Polyot vslepuyu" (Blind flight) 2026: problem teardown and seven public solutions](../../docs/landscape/blind-flight-teardown.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)
- [Docs map](../../docs/README.md) (mentions)
- [KROT (Где мы, Бариста?) - terrain correlation from radar altimeter](../../catalog/repos/rub1kub__where-are-we-barista.md) (alternative_to)
- [Хакатон: трек «Робототехника и сенсорика», кейс «Полёт вслепую»](../../catalog/resources/iqarium-polet-vslepuyu-hackathon-2026.md) (has_code)

_Indexed by lane(s): ua-ru-round2_

_GitHub metadata fetched 2026-11-06._
