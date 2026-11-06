# Система управління та навігації БПЛА

`res:kpi-spaskyi-uav-control-nav-under-ew-2025` - paper - <https://heraldts.khmnu.edu.ua/index.php/heraldts/article/download/1877/1819/6149>

**By:** Ya. Spaskyi, V. Bondarenko, N. Bondarenko, KPI (Igor Sikorsky) - **Year:** 2025 - **Level:** intermediate - **Access:** open

English: 'UAV control and navigation system'. KPI authors describe an ArduPilot-based control and navigation architecture intended to keep working under EW: protected GPS module, inertial navigation, backup channels, and ArduPilot code modifications including pseudo-random frequency reassignment for the link.

## Key takeaways

- Ukrainian practice modifies ArduPilot rather than writing autopilots from scratch
- Link resilience (frequency agility) is treated together with navigation resilience
- System-level description; limited quantitative evaluation

## Deep dives

- [ua-ru-sources-overview](../../docs/landscape/ua-ru-sources-overview.md) (landscape)

**Concepts:** [Autopilots and flight control](../../catalog/concepts/autopilot.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md), [Inertial navigation (INS/IMU)](../../catalog/concepts/ins.md)

**Tags:** `lang:uk`, `kpi`, `ardupilot`, `link-resilience`

## Related

- uses: [ArduPilot](../../catalog/repos/ardupilot__ardupilot.md)

## Referenced by

- [Hackathon playbook: navigation and PNT under GNSS denial](../../docs/hackathon-playbook.md) (mentions)
- [Ukrainian- and Russian-language sources: what they add](../../docs/landscape/ua-ru-sources-overview.md) (mentions)
- [Problem-statement decoder](../../docs/problem-statement-decoder.md) (mentions)

_Indexed by lane(s): ua-ru-sources_
