# 3GPP TS 38.133 (ETSI TS 138 133): NR; Requirements for support of radio resource management - clause 7.4 Cell phase synchronization accuracy

`res:3gpp-ts-38-133-cell-phase-sync` - standard - <https://www.etsi.org/deliver/etsi_ts/138100_138199/138133/15.02.00_60/ts_138133v150200p.pdf>

**By:** 3GPP TSG RAN WG4, ETSI - **Year:** 2018 - **Level:** advanced - **Access:** open

Clause 7.4 defines cell phase synchronization accuracy for TDD as the maximum absolute deviation in frame start timing between any pair of same-frequency cells with overlapping coverage, and requires it to be better than 3 us at the BS antenna connectors (read in V15.2.0, 2018-07). Commonly translated into roughly +-1.5 us per cell against a common reference. The ETSI server lists releases up to V19.6.0; only V15.2.0 was read here.

## Key takeaways

- 5G TDD needs cells within 3 us of each other => roughly +-1.5 us to UTC per cell
- GNSS loss at a TDD site becomes a holdover problem measured against this number
- Linked PDF is the 2018 Release 15 edition; check the current release before quoting clause numbers

**Concepts:** [Timing and time transfer](../../catalog/concepts/timing.md), [Standards and interface specs](../../catalog/concepts/standards.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `3gpp`, `5g-nr`, `tdd`, `phase-sync`, `3-us`

## Related

- cites: [ITU-T G.8271: Time and phase synchronization aspects of telecommunication networks](../../catalog/resources/itu-t-g8271.md)
- explains: [Network of GNSS-disciplined clocks: holdover from peers, spoof isolation by cross-node consistency, ADEV-weighted ensemble](../../catalog/samples/timing-network-holdover.md)
- explains: [GNSS-disciplined clock holdover per oscillator grade, and a slow time-walk spoof](../../catalog/samples/timing-holdover.md)

_Indexed by lane(s): timing-network_
