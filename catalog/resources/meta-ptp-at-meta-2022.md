# How Precision Time Protocol is being deployed at Meta

`res:meta-ptp-at-meta-2022` - blog - <https://engineering.fb.com/2022/11/21/production-engineering/precision-time-protocol-at-meta/>

**By:** O. Obleukhov, A. Byagowi - **Year:** 2022 - **Level:** intermediate - **Access:** open

Meta's PTP architecture: Time Appliance racks, unicast PTP through transparent clocks, and clients that report a window of uncertainty instead of a single time. When an appliance enters holdover its uncertainty grows with oscillator stability and clients are steered away by clock class.

## Key takeaways

- Publish an uncertainty bound with time, not just time
- Holdover is signalled to clients through clockClass

**Concepts:** [Timing and time transfer](../concepts/timing.md)

**Tags:** `ptp`, `meta`, `holdover`, `window-of-uncertainty`

## Related

- has_code: [Meta Time libraries](../repos/meta__time.md)
- uses: [OCP Time Card](../repos/time-appliances-project__time-card.md)

_Indexed by lane(s): timing_
