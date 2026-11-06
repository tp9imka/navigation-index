# Cheat sheets: pick one in 30 seconds

One page per likely brief family, readable in 3 minutes on the day. Each sheet has: what judges
likely want, the demo with exact samples and first commands, a first-2-hours plan, 3 numbers
with their input type (real / SITL / synthetic), top traps, a stretch goal and links. They
condense the [decoder](../problem-statement-decoder.md), [samples/README.md](../../samples/README.md)
and the [evidence matrix](../evidence-matrix.md); when a sheet and those disagree, those win.
Snapshot 2026-11-06.

| The brief says... | Sheet | Decoder rows |
|---|---|---|
| "without GPS / GNSS-denied", a distance or route, "bring it home", "drop-in for COTS autopilot", "how long after GNSS loss" | [gnss-denied-drone-nav](gnss-denied-drone-nav.md) | 1, 2, 20, 26 |
| "spoofing", "deception", "trust", "integrity", "assured PNT", "keep flying", "fixed-wing 20-30 km jammed and spoofed" | [spoofing-keep-flying](spoofing-keep-flying.md) | 4, 20, 27 |
| "detect / map / warn" + jamming, "low-cost sensor network", "find the jammer", "emitter", "COP under EW" | [jammer-ew-map](jammer-ew-map.md) | 3, 5, 12 |
| "timing", "synchronisation", "time server", "critical infrastructure", "time push", "authenticate" | [resilient-timing](resilient-timing.md) | 6, 19 |
| "ship", "USV", "port", "AIS", "maritime", "vessel", "coast"; "underwater / AUV" (no sample) | [maritime-ais](maritime-ais.md) | 7, 8, 17 |
| "soldier", "dismounted", "indoors", "squad", "on foot", "first responder", "basement", "tunnel" | [dismounted-indoor-tunnel](dismounted-indoor-tunnel.md) | 9, 14 |
| "swarm", "team", "cooperative", "relative", "task allocation" | [swarm-cooperative](swarm-cooperative.md) | 10, 11 |
| "drone detection", "counter-UAS", "airspace awareness", "Remote ID", "FOB", "TAK" | [counter-uas-remote-id](counter-uas-remote-id.md) | 12, 13 |
| "terrain", "TERCOM", "blind flight", "night", "thermal", "smoke", "stars", "magnetic", "no RF" | [terrain-night-celestial](terrain-night-celestial.md) | 15, 16, 18, 25, 27 |
| "AI", "LLM", "agent", "assistant", "incident analysis" | [llm-agent-ops](llm-agent-ops.md) | 21, 22 |

No sheet (thin coverage, go straight to the [decoder](../problem-statement-decoder.md#the-table)
and its [gaps](../problem-statement-decoder.md#gaps-this-table-exposed)): UGV / rover / rail
through forest or urban canyon (row 14: no real-data ground loop), urban-canyon multipath and NLOS
(row 23: [gnss-rinex-processing](../../samples/gnss-rinex-processing/) baseline only), LEO signals
of opportunity (row 24: no sample).

Two families fit? Pick the one whose demo is a vehicle if the brief names a platform and a
distance; pick the awareness sheet (jammer, C-UAS) if it names an area or an operator. Then score
both with the [day-0 rubric](../day0-runbook.md#2-pick-the-idea-scoring-rubric).
