# MagNavPy

`repo:manasp21/magnav.py` - <https://github.com/manasp21/magnav.py>

| stars | language | license | last push | archived | maturity | hackathon fit |
|---|---|---|---|---|---|---|
| 9 | Python | ? | 2026-01-15 | False | research-prototype | high |

Community Python port of MIT's MagNav.jl: loads flight, INS and magnetometer data and magnetic anomaly maps (with upward continuation), runs Tolles-Lawson and neural-network aircraft compensation, and provides an EKF / MagNav filter with CRLB analysis and plotting.

**Why it matters:** Lowers the language barrier to the MagNav data and algorithms for Python-heavy teams.

**Hackathon notes:** Community port; install from the repo (despite the README badge, magnavpy is not on PyPI) and sort out GDAL first. Verify outputs against MagNav.jl examples.

**Concepts:** [Magnetic anomaly navigation](../concepts/magnetic-nav.md), [Assured / resilient PNT](../concepts/assured-pnt.md)

**Tags:** `python`, `port`, `magnav`

**Domains:** air

## Related

- alternative_to: [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md)
- fork_of: [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md)

## Referenced by

- [MagNav.jl](../repos/mit-ai-accelerator__magnav.jl.md) (alternative_to)
- [Q-CTRL Ironstone Opal quantum-assured magnetic navigation](../resources/qctrl-ironstone-opal.md) (alternative_to)
- [SandboxAQ AQNav geomagnetic navigation](../resources/sandboxaq-aqnav.md) (alternative_to)
- [MagNav.jl quickstart: Tolles-Lawson and EKF on the SGL 2020 flight](../samples/magnav-quickstart.md) (explains)

_Indexed by lane(s): alt-nav, defense-context_

_GitHub metadata fetched 2026-11-06._
