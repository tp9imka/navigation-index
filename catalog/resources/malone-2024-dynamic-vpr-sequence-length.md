# Dynamically Modulating Visual Place Recognition Sequence Length For Minimum Acceptable Performance Scenarios

`res:malone-2024-dynamic-vpr-sequence-length` - paper - <https://arxiv.org/abs/2407.00863>

**By:** Connor Malone, Ankit Vora, Thierry Peynot, Michael Milford - **Year:** 2024 - **Level:** intermediate - **Access:** open

IROS 2024 (doi 10.1109/IROS58592.2024.10802570, per Crossref); arXiv 2407.00863 abstract read. An MLP fitted on a calibration set predicts, per map section, the shortest VPR sequence length that meets a target localization performance, from appearance variation in the region under a coarse position prior.

## Key takeaways

- Spends just enough compute where a place is hard, keyed on a position prior
- Per-place effort, not driven by a navigation deadline or delay
- Ground vehicle data

**Concepts:** [Place recognition and loop closure](../../catalog/concepts/place-recognition.md), [Onboard / edge AI perception](../../catalog/concepts/edge-ai.md)

**Tags:** `vpr`, `adaptive-compute`, `sequence-matching`, `position-prior`

_Indexed by lane(s): innovation-pa-scheduling_
