# PTPsec: Securing the Precision Time Protocol Against Time Delay Attacks Using Cyclic Path Asymmetry Analysis

`res:finkenzeller-2024-ptpsec` - paper - <https://arxiv.org/abs/2401.10664>

**By:** Andreas Finkenzeller, Oliver Butowski, Emanuel Regnath, Mohammad Hamad, Sebastian Steinhorst - **Year:** 2024 - **Level:** advanced - **Access:** open

Detects PTP time delay attacks by measuring round-trip times over redundant network paths and comparing their asymmetry, with a new measurement message on top of IEEE 1588-2019. Evaluated on a hardware testbed; code at tum-esi/ptpsec. Detection relies on at least one redundant path staying symmetric.

## Key takeaways

- A delay attack is a path asymmetry change - encryption and authentication alone do not stop it
- Cyclic path measurements catch static and incremental delay attacks if one path is clean
- Same idea as the cross-node consistency check in sample:timing-network-holdover

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Electronic warfare resilience](../../catalog/concepts/ew-resilience.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `ptp`, `delay-attack`, `path-asymmetry`, `tum`

## Related

- has_code: [PTPsec](../../catalog/repos/tum-esi__ptpsec.md)
- uses: [IEEE 1588-2019: IEEE Standard for a Precision Clock Synchronization Protocol for Networked Measurement and Control Systems](../../catalog/resources/ieee-1588-2019.md)
- same_author: [Securing the Precision Time Protocol with SDN-enabled Cyclic Path Asymmetry Analysis](../../catalog/resources/finkenzeller-2025-ptpsec-sdn.md)
- explains: [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md)

## Referenced by

- [Securing the Precision Time Protocol with SDN-enabled Cyclic Path Asymmetry Analysis](../../catalog/resources/finkenzeller-2025-ptpsec-sdn.md) (same_author)

_Indexed by lane(s): timing-network_
