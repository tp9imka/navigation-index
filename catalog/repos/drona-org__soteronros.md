# SOTER on ROS

`repo:drona-org/soteronros` - <https://github.com/Drona-Org/SOTERonROS>

| stars | language | license | last push | archived | maturity | quick-build fit |
|---|---|---|---|---|---|---|
| 1 | C# | ? | 2020-06-23 | False | archived | low |

Research framework that builds distributed mobile-robot software on ROS as runtime-assurance modules: an advanced controller, a safe controller and a decision module that switches between them. Written in the P language (generated C#) with C++ robot modules.

**Why it matters:** A worked ROS example of the simplex switch with a formal decision module. Useful as a pattern reference, not as a dependency.

**Build notes:** Last push 2020-06, ROS 1, no license file. Read for the architecture only; reimplement the switch in your own node.

**Concepts:** [ROS / ROS 2 robotics middleware](../../catalog/concepts/ros.md), [Standards and interface specs](../../catalog/concepts/standards.md)

**Tags:** `runtime-assurance`, `simplex`, `ros1`, `p-language`

**Domains:** air, ground

## Related

- alternative_to: [run-time-assurance (AFRL ACT3)](../../catalog/repos/act3-ace__run-time-assurance.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [run-time-assurance (AFRL ACT3)](../../catalog/repos/act3-ace__run-time-assurance.md) (alternative_to)

_Indexed by lane(s): flight-embedded_

_GitHub metadata fetched 2026-11-23._
