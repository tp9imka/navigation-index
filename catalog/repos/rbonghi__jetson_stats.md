# jetson-stats (jtop)

`repo:rbonghi/jetson_stats` - <https://github.com/rbonghi/jetson_stats>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 2,638 | Python | AGPL-3.0 | 2026-11-15 | False | production | high |

Monitoring tool for NVIDIA Jetson: CPU/GPU load, clocks, temperatures, power rails and power mode, with a Python API for logging.

**Why it matters:** The easy way to put a measured watts number next to a latency number, which is what an onboard-compute slide needs.

**Build notes:** AGPL-3.0: fine as a dev tool on the bench, do not bundle it into a shipped image. `sudo pip3 install jetson-stats` on the Jetson itself (ask before installing).

**Concepts:** [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `jetson`, `power`, `monitoring`, `tegrastats`

**Domains:** multi

## Related

- integrates_with: [TensorRT (open-source components)](../../catalog/repos/nvidia__tensorrt.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-16._
