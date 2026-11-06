# TODO: project name

> One line: what it does, for which platform, under which threat.
> Example: "Detects GNSS spoofing on a small UAS within 10 s and keeps navigating on dead reckoning, shown live in TAK."

Status: hackathon prototype, TODO: event name and date. Not flight-tested. Not for operational use.

## Problem

- Threat in one sentence, with one public source (incident report, regulator bulletin).
- Who suffers it and on what platform (UAS, USV, UGV, dismounted, timing).
- What goes wrong today (e.g. hybrid GNSS/INS blend absorbs a slow spoof drag-off).

## Threat model

Short version here; full version in `docs/threat-model.md` (from the kit's `templates/threat-model.md`).

| Threat | In scope | How we handle it |
|---|---|---|
| GNSS jamming | yes / no | TODO |
| GNSS spoofing / meaconing | yes / no | TODO |
| Datalink EW | yes / no | TODO |
| Sensor spoofing (camera, mag, baro) | yes / no | TODO |
| Stale maps / reference data | yes / no | TODO |

Assumptions: TODO (e.g. first fix is trusted; IMU/odometry is not attacked; attacker has no access to the vehicle).

## Approach

```
PoseSource => NavFilter => IntegrityMonitor => Publisher (CoT to TAK, STATUSTEXT to GCS, JSONL log)
```

- Detect before fuse: fixes failing the integrity test never reach the filter.
- Map features to detect / respond / recover.
- Name the repos and papers you build on (hub ids help: `repo:...`, `res:...`).
- Decisions: `docs/adr/` (one file per decision, from `templates/adr.md`).

## Demo

- Video: TODO link (recorded before the live demo, saved on two machines).
- Live: `make demo` streams the spoof scenario as CoT to `127.0.0.1:6969` and STATUSTEXT to `127.0.0.1:14550`.
- Script: `docs/demo-script.md` (from `templates/demo-script.md`).

## Results

Produced by `make eval` (writes `runs/results.md`). Paste the table, do not retype it. A metric
the run cannot support reads `not measured`.

| Run | Data | Ground truth | ATE RMSE m | Time to detect s | False-alarm epochs | Availability % | Misleading % |
|---|---|---|---|---|---|---|---|
| baseline | TODO | TODO | not measured | not measured | not measured | not measured | not measured |
| ours | TODO | TODO | not measured | not measured | not measured | not measured | not measured |

Test conditions: TODO (synthetic / SITL / recorded dataset name / hardware). Alert limit: TODO m.

### What we did not verify

- TODO: e.g. "only synthetic and SITL data; no real receiver under a real spoofer".
- TODO: e.g. "thresholds tuned on the same seed we report".

### Known failure modes

- TODO: e.g. "a drag-off slower than X m/s is absorbed before detection".

## How to run

Needs Python 3.10+ only for the core. No network.

```sh
make test      # unit tests
make sim       # synthetic clean / jam / spoof, with and without integrity
make eval      # metrics table => runs/results.md
make demo      # stream to local TAK / GCS ports
```

Optional extras: `pip install -e '.[mavlink,tak]'` inside `.venv` (`make setup`).
Docker: `docker compose up app` (sim and TAK services are placeholders until you pin images).

## Compliance

- Public civil signals and published methods only. GNSS signal generation to file or cable only, never radiated.
- No targeting, no terminal guidance. Navigation, integrity and awareness only.
- Any AI component: logged decisions, confidence, off switch, safe fallback.
- Licence: TODO (see LICENSE). Third-party code and data licences: TODO list.

## Team

| Name | Role | Contact |
|---|---|---|
| TODO | Lead / integrator | |
| TODO | Nav / estimation | |
| TODO | Platform (SITL, hardware) | |
| TODO | Viz / C2 | |
| TODO | Pitch / evidence | |
