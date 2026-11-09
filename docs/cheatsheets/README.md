# Cheat sheets: pick one in 30 seconds

One page per likely brief family, readable in 3 minutes on the day. Each sheet has: what judges
likely want, the demo with exact samples and first commands, a first-2-hours plan, 3 numbers
with their input type (real / SITL / synthetic), top traps, a stretch goal and links. They
condense the [decoder](../problem-statement-decoder.md), [samples/README.md](../../samples/README.md)
and the [evidence matrix](../evidence-matrix.md); when a sheet and those disagree, those win.
Snapshot 2026-11-06; close-area sheet added 2026-11-09.

EDGE hackathon Challenge 2 (autonomous flight navigation): start at
[challenge-2-autonomous-flight](../challenge-2-autonomous-flight.md), which picks among these.

| The brief says... | Sheet | Decoder rows |
|---|---|---|
| "without GPS / GNSS-denied", a distance or route, "bring it home", "drop-in for COTS autopilot", "how long after GNSS loss" | [gnss-denied-drone-nav](gnss-denied-drone-nav.md) | 1, 2, 20, 26 |
| "spoofing", "deception", "trust", "integrity", "assured PNT", "keep flying", "fixed-wing 20-30 km jammed and spoofed" | [spoofing-keep-flying](spoofing-keep-flying.md) | 4, 20, 27 |
| "detect / map / warn" + jamming, "low-cost sensor network", "find the jammer", "emitter", "COP under EW" | [jammer-ew-map](jammer-ew-map.md) | 3, 5, 12 |
| "timing", "synchronisation", "time server", "critical infrastructure", "time push", "authenticate" | [resilient-timing](resilient-timing.md) | 6, 19 |
| "ship", "USV", "port", "AIS", "maritime", "vessel", "coast"; "underwater / AUV" (no sample) | [maritime-ais](maritime-ais.md) | 7, 8, 17 |
| A person on foot: "soldier", "dismounted", "squad", "on foot", "first responder", "indoors on foot", "basement", "tunnel". An indoor drone goes to close-area below | [dismounted-indoor-tunnel](dismounted-indoor-tunnel.md) | 9, 14 |
| "swarm", "team", "cooperative", "relative", "task allocation" | [swarm-cooperative](swarm-cooperative.md) | 10, 11 |
| "drone detection", "counter-UAS", "airspace awareness", "Remote ID", "FOB", "TAK" | [counter-uas-remote-id](counter-uas-remote-id.md) | 12, 13 |
| "terrain", "TERCOM", "blind flight", "night", "thermal", "smoke", "stars", "magnetic", "no RF" | [terrain-night-celestial](terrain-night-celestial.md) | 15, 16, 18, 25, 27 |
| "AI", "LLM", "agent", "assistant", "incident analysis" | [llm-agent-ops](llm-agent-ops.md) | 21, 22 |
| "point A to B", "A to B", "obstacles", "close area", "arena", "indoor drone", "avoid", "VIO lost" | [close-area-a-to-b](close-area-a-to-b.md) (first commands, which planner first, platform notes, traps). Also: [day1-close-area-intake](../day1-close-area-intake.md), [close-area-arena](../../samples/close-area-arena/) (A* + ESDF, estimator faults, log scorer), [flight-repo](../../templates/flight-repo/) and the [close-area-nav synthesis](../research/close-area-nav/README.md). "no map", "Crazyflie", "Multi-ranger", "reactive", "potential field": [close-area-planner-reactive](../../samples/close-area-planner-reactive/) (APF + escape beats VFH+ in a U trap, VFH+ beats APF through a narrow gap, both collide often on 4 beams). "moving obstacles", "people", "dynamic obstacles": [close-area-moving-obstacles](../../samples/close-area-moving-obstacles/README.md) (A* replan alone collides with walking people in 14-36 % of runs; a PX4-CBF style range filter removes them at a 16 % stuck cost, synthetic). "VIO lost", "relocalize", "tracking loss": [close-area-relocalize](../../samples/close-area-relocalize/README.md) (the recommended headline after the safety-filter kill test failed) | 31, 33 |
| "marker", "land on the pad", "landing pad / helipad", "fly to the tag", "precision landing", "AprilTag / ArUco" | [close-area-a-to-b](close-area-a-to-b.md) section 3, then [fiducial-goal-apriltag](../../samples/fiducial-goal-apriltag/) for tag size vs detection range, then [close-area-arena](../../samples/close-area-arena/) for the path that brings the tag into view | 32, 31 |

No sheet (thin coverage, go straight to the [decoder](../problem-statement-decoder.md#the-table)
and its [gaps](../problem-statement-decoder.md#gaps-this-table-exposed)): UGV / rover / rail
through forest or urban canyon (row 14: no real-data ground loop), urban-canyon multipath and NLOS
(row 23: [gnss-rinex-processing](../../samples/gnss-rinex-processing/) baseline only), LEO signals
of opportunity (row 24: no sample).

Two families fit? Pick the one whose demo is a vehicle if the brief names a platform and a
distance; pick the awareness sheet (jammer, C-UAS) if it names an area or an operator. Then score
both with the [day-0 rubric](../day0-runbook.md#2-pick-the-idea-scoring-rubric).
