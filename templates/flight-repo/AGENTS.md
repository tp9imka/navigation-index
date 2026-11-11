# AGENTS.md

For coding agents working in this repo during the hackathon.

## Ground rules

- `make test && make sim` must pass after every change you hand back.
- Stdlib only in `flightloop/`. Optional deps (numpy, an SDK) go in a local `.venv`, never global.
- Keep the stages: Adapter => NavHealth => Planner => SafetyFilter => send_setpoint. New platform =>
  new driver with `pose()`, `ranges()`, `send_setpoint()`. New planner => class with
  `step(pose, scan, goal, grid, dt)`. New filter => `filter(setpoint, pose, scan, health)`.
  Planners never call the vehicle or a platform SDK.
- Do not rename fields in `flightloop/adapter.py`: they match the hub's drone-adapter and arena.
- Thresholds are named constants. Every number in README comes from a file in `results/` with
  its input type (real / SITL / synthetic). The mock is synthetic.
- The loop must never stop streaming setpoints while flying. Do not add blocking calls to it.

## Scope

The vehicle's own navigation: localization, planning, obstacle avoidance, nav integrity. No
targeting, homing, intercept or weapons guidance.

## Knowledge hub: navigation-index

Read these before searching the web or cloning repos (paths relative to the hub root):

- `docs/research/close-area-nav/README.md`: close-area A=>B synthesis, recommended direction,
  questions for the organisers. Lanes 01 (planning), 02 (sims), 03 (localization).
- `samples/close-area-arena/CONTRACT.md`: seeded arena and truth scorer; its planners plug into
  this loop (`python3 main.py --mock --planner arena:<name> --arena <hub>/samples/close-area-arena`).
- `templates/drone-adapter/frames.md`: ENU / NED, FLU / FRD and yaw conventions per platform.
- `docs/problem-statement-decoder.md#route-a-full-brief-to-rows-and-first-pages`: which hub rows and samples fit Challenge 2.

Lookups: MCP `navigation-index` (`search`, `decode`, `show`, `read`), or
`python3 <hub>/tools/query.py search "close area obstacle avoidance range sensor"`.
