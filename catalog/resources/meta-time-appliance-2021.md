# Open-sourcing a more precise time appliance

`res:meta-time-appliance-2021` - blog - <https://engineering.fb.com/2021/08/11/open-source/time-appliance/>

**By:** A. Byagowi, O. Obleukhov - **Year:** 2021 - **Level:** intro - **Access:** open

Introduces the Time Card (GNSS receiver, miniature atomic clock, FPGA time engine on PCIe) and the OCP Time Appliance Project. States a holdover target of within 1 microsecond over 24 hours and reports a 24-hour test with PPS drift within 300 ns.

## Key takeaways

- Atomic holdover target: 1 us per 24 h
- Time Card driver is in Linux 5.15+

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `time-card`, `ocp`, `holdover`, `atomic-clock`

## Related

- has_code: [OCP Time Card](../../catalog/repos/time-appliances-project__time-card.md)
- explains: [Open Time Server spec](../../catalog/repos/time-appliances-project__open-time-server.md)

## Referenced by

- [Timing resilience: the T in PNT](../../docs/timing-resilience.md) (mentions)

_Indexed by lane(s): timing_
