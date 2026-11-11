# run-time-assurance (AFRL ACT3)

`repo:act3-ace/run-time-assurance` - <https://github.com/act3-ace/run-time-assurance>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 11 | Jupyter Notebook | NOASSERTION | 2025-09-12 | False | research-prototype | medium |

Python library of runtime-assurance safety filters from the AFRL ACT3 team: generic explicit and implicit Simplex plus explicit and implicit ASIF (active set invariance filter), with a zoo of worked examples. Constraints and a state-transition model are all a new module needs.

**Why it matters:** One of very few public, code-level RTA implementations from a defense lab. It shows the switch logic and constraint style a reviewer will expect when you claim 'simplex architecture'.

**Build notes:** LICENSE says only 'This software is government owned'; the README carries an AFRL public-release case number. Fine to read and learn from; ask before shipping it. Examples target spacecraft docking, so adapt the constraint set to nav (position bound, innovation bound).

**Concepts:** [Standards and interface specs](../../catalog/concepts/standards.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `runtime-assurance`, `simplex`, `asif`, `safety-filter`, `afrl`, `python`

**Domains:** air, space

## Related

- alternative_to: [SOTER on ROS](../../catalog/repos/drona-org__soteronros.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [04. Close-area navigation: prior art for three innovation angles, plus a wider scan](../../docs/research/close-area-nav/04-innovation-prior-art.md) (mentions)
- [SOTER on ROS](../../catalog/repos/drona-org__soteronros.md) (alternative_to)
- [ASTM F3269-21: Standard Practice for Methods to Safely Bound Behavior of Aircraft Systems Containing Complex Functions Using Run-Time Assurance](../../catalog/resources/astm-f3269-21-rta.md) (has_code)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-09._
