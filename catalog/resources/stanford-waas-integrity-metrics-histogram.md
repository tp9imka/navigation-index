# Stanford WAAS Laboratory - system metrics (the integrity/availability histogram behind the 'Stanford plot')

`res:stanford-waas-integrity-metrics-histogram` - doc - <https://web.stanford.edu/group/scpnt/gpslab/www/metrics.html>

**By:** Stanford University GPS Laboratory - **Year:** None - **Level:** intermediate - **Access:** open

Stanford GPS Lab page that explains the 2D histogram of true position error against protection level from its real-time WAAS implementation on the National Satellite Test Bed. It defines the normal-operation, alarm (PL above alert limit) and integrity-failure regions and offers the MATLAB plotting scripts (hplstat.m, vplstat.m). Secondary sources credit the Stanford WAAS lab with this diagram; the page itself is undated.

## Key takeaways

- Axes: true error (x) vs protection level (y), log-scaled counts
- Points with error above PL are integrity failures
- Original MATLAB scripts for drawing the plot

**Concepts:** [GNSS positioning](../../catalog/concepts/gnss.md), [Assured / resilient PNT](../../catalog/concepts/assured-pnt.md)

**Tags:** `stanford-diagram`, `protection-level`, `waas`, `sbas`, `integrity`

## Related

- explains: [The Stanford - ESA Integrity Diagram: Focusing on SBAS Integrity](../../catalog/resources/tossaint-2006-stanford-esa-integrity-diagram.md)
- part_of: [Stanford GPS Laboratory](../../catalog/resources/stanford-gps-lab.md)

_Indexed by lane(s): backlog_
