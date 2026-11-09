# ASTM F3269-21: Standard Practice for Methods to Safely Bound Behavior of Aircraft Systems Containing Complex Functions Using Run-Time Assurance

`res:astm-f3269-21-rta` - standard - <https://store.astm.org/f3269-21.html>

**By:** ASTM F38 Committee - **Year:** 2021 - **Level:** intermediate - **Access:** paywalled

Industry standard practice for run-time assurance: let a complex function (adaptive, ML, COTS) operate, monitor it against a safe boundary, and switch to a simpler assured recovery function when it would cross that boundary. Written for UAS and scalable to other aircraft.

## Key takeaways

- Named parts: input manager, safety monitor, recovery control function, RTA switch
- The complex function can stay at a lower assurance level if the monitor and switch are assured
- Not a one-size-fits-all strategy; HW/SW integration is out of scope
- Safety assessment still runs through ARP4754A / ARP4761 / ASTM F3178

**Concepts:** [Standards and interface specs](../../catalog/concepts/standards.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `runtime-assurance`, `rta`, `simplex`, `astm`, `uas`, `certification`

## Related

- explains: [ASTM F3269 - An Industry Standard on Run Time Assurance for Aircraft Systems](../../catalog/resources/nagarajan-2021-astm-f3269-scitech.md)
- has_code: [run-time-assurance (AFRL ACT3)](../../catalog/repos/act3-ace__run-time-assurance.md)
- has_code: [Ogma](../../catalog/repos/nasa__ogma.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [04. Close-area navigation: prior art for three innovation angles, plus a wider scan](../../docs/research/close-area-nav/04-innovation-prior-art.md) (mentions)
- [Close-area pitch scaffold: A to B through obstacles](../../templates/pitch/close-area-story.md) (mentions)
- [Runtime Assurance for Autonomous Aerospace Systems](../../catalog/resources/clark-2020-rta-autonomous-aerospace.md) (cites)
- [ASTM F3269 - An Industry Standard on Run Time Assurance for Aircraft Systems](../../catalog/resources/nagarajan-2021-astm-f3269-scitech.md) (explains)
- [Resilient Shield: Strengthening Hivemind for Safe, Real-World Flight](../../catalog/resources/shield-ai-2025-resilient-shield-mm-rta.md) (uses)

_Indexed by lane(s): flight-embedded_
