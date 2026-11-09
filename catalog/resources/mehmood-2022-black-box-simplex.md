# The Black-Box Simplex Architecture for Runtime Assurance of Autonomous CPS

`res:mehmood-2022-black-box-simplex` - paper - <https://arxiv.org/abs/2102.12981>

**By:** Usama Mehmood, Sanaz Sheikhi, Stanley Bak, Scott A. Smolka, Scott D. Stoller - **Year:** 2022 - **Level:** advanced - **Access:** open

Extends Simplex so that neither the advanced nor the backup controller needs static verification: runtime checks over a short horizon decide whether the backup can still recover. Case studies include neural-network collision avoidance for F-16 groups. Published at NASA Formal Methods 2022.

## Key takeaways

- Removes the need to verify the backup controller offline
- Fits learned or MPC-style controllers that are hard to verify
- Earlier arXiv title: 'Safe CPS from Unsafe Controllers'

**Concepts:** [Standards and interface specs](../../catalog/concepts/standards.md), [Autopilots and flight control](../../catalog/concepts/autopilot.md)

**Tags:** `simplex`, `runtime-assurance`, `neural-network`, `nfm`

## Related

- cites: [Using Simplicity to Control Complexity](../../catalog/resources/sha-2001-simplex.md)

## Referenced by

- [Path to product: from a nav algorithm to something that flies](../../docs/path-to-product.md) (mentions)
- [Using Simplicity to Control Complexity](../../catalog/resources/sha-2001-simplex.md) (cites)

_Indexed by lane(s): flight-embedded_
