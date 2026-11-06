# Assessing the Spoofing Threat - paper digest
<!-- about: res:humphreys-2008-assessing-spoofing-threat -->
**Assessing the Spoofing Threat: Development of a Portable GPS Civilian Spoofer** - Humphreys, Ledvina, Psiaki, O'Hanlon, Kintner (UT Austin, Virginia Tech, Cornell), ION GNSS 2008 (preprint). [paper](https://rnl.ae.utexas.edu/images/stories/files/papers/ion2008r01_for_distributionW.pdf) | code: none | Read: full text, author-hosted preprint PDF (12 pages)

## Problem
In 2008 civil GPS receivers had no spoofing countermeasures, and manufacturers doubted the threat was real. Published countermeasure lists (Volpe report, Homeland Security Institute) were either hardware-heavy or easy to defeat. The authors built a research receiver-spoofer to find which attacks are easy, which are hard, and which defenses are worth adding first.

## Method
- Threat continuum (Sec. II, Fig. 1). Three classes: simplistic (an unsynchronised signal simulator), intermediate (a portable receiver-spoofer that tracks live signals and aligns its output with them), sophisticated (several phase-locked receiver-spoofers, one per victim antenna).
- For each class, the paper asks which user-equipment defenses still work. Section II summaries:
  - Simulator: easy to detect. It forces loss of lock or a time jump. "The victim receiver could flag jumps of more than, say, 100 ns" (Sec. II-A).
  - Single receiver-spoofer: defeats most user-equipment defenses. The only one the authors call completely effective is angle-of-arrival discrimination with 2+ antennas, against a single transmit antenna (Sec. II-B).
  - Coordinated multi-spoofer: "The only known defense against such an attack is cryptographic authentication" (Sec. II-C).
- Research platform (Sec. III-IV): the spoofer is a software module added to the Cornell GRID software receiver on a DSP. Demonstration (Sec. V): recorded live data was spoofed in a bit-stream combiner. Nothing was radiated over the air, to stay legal.
- Two new user-equipment defenses (Sec. VI):
  - Data bit latency defense: watch for data-bit sign changes off the expected bit boundaries. They show up when a spoofer relays bits instead of predicting them.
  - Vestigial signal defense: cancel the tracked signal from a buffered copy of the front-end samples, then re-acquire the same PRN. A remaining "vestige" of the authentic signal reveals the takeover.

## Data and sensors
- Single-antenna GPS L1 C/A only. A Zarlink GP2015 front end feeds a TI TMS320C6455 DSP (Sec. III-A).
- Demo input: recorded L1 C/A samples at 5.7 MHz with 6 satellites in view (Sec. V). There is no public dataset.
- For a public signal-level benchmark of the same attack family, see [TEXBAT](../dataset-cards/texbat.md). UT built it later. Our read: the ds3/ds4 matched-power push scenarios correspond to the "intermediate" class described here.

## Headline results (as reported)
- Sec. II-A (2008 context): commercial signal simulators cost up to "$400 k" or rent for "less than $1 k per week". The authors judge a simulator attack the most likely near-term threat but also easy to detect.
- Sec. I: four receiver manufacturers surveyed informally knew of the vulnerability but had added no countermeasures.
- Sec. IV: the platform tracks 12 L1 C/A signals and generates 12 spoofing signals at the same time on a 1.2 GHz TMS320C6455. Marginal cost per channel is 1.2% (tracking) and 4% (spoofing) of the DSP.
- Sec. IV: building the spoofer module took "approximately three developer-weeks". Off-the-shelf hardware cost "approximately $1500".
- Sec. V, Fig. 11: single-channel capture and drag-off of the victim's tracking points took "approximately 30 seconds". It was watched through 81 correlator taps at 0.2-chip spacing.
- Sec. VI-A: the data bit latency defense "has been implemented and validated on a modified Cornell GRID receiver". No detection-rate numbers are given.
- Sec. VI-B: suppressing the authentic signal (which would defeat the vestigial defense) needs about 1/8 cycle carrier-phase knowledge at the victim antenna, which implies cm-level relative geometry. The vestigial defense itself has no measured performance.
- Sec. VII conclusion: "nothing short of cryptographic authentication can guard against a sophisticated spoofing attack."

## Limitations
- Stated by authors:
  - No over-the-air tests.
  - The spoofer did not align carrier phase with the authentic signals (Sec. III-B.1, V).
  - The control module was partly under development.
  - Neither proposed defense is "spoof-proof" (Sec. VI).
  - A third, cryptographic defense was deferred to a later paper.
- Our read:
  - A threat-assessment paper, not an evaluation. The defenses get no ROC curves, false-alarm rates or field data.
  - GPS L1 C/A only. The authors note that multi-signal, multi-constellation receivers raise attacker cost (Sec. VII), so threat numbers do not carry over directly to modern multi-band receivers.
  - The 2008 cost and effort figures are now historical.

## Code, weights, license
No code or data released. Paper copyright is held by the authors (preprint notice). Not applicable for weights.

## Reproduction effort (estimate)
Estimate: not reproducible as a system, and reproducing the attack side is out of scope for this hub. The defensive ideas can be tried in about a day on recorded data:
- Data bit latency check: needs a software receiver with access to 1 ms prompt correlator outputs, e.g. [GNSS-SDR](../integration-cards/gnss-sdr__gnss-sdr.md) on [TEXBAT](../dataset-cards/texbat.md) IQ files (43 GB per scenario).
- Vestigial signal search: needs raw IQ and a custom acquisition pass. Expect 2-3 days to get a first detection plot.

## What a hackathon team can take from it
- **A threat-tier vocabulary for judges:** simplistic, intermediate, sophisticated, with the defense that still works at each tier. Use it to state honestly what your detector does and does not cover.
- **A cheap software check:** flag receiver clock or time jumps beyond a bound (the paper's example is 100 ns, Sec. II-A). Pair it with your platform's clock-drift model.
- **The vestigial-signal idea:** after tracking, search for a second peak of the same PRN. This is the ancestor of the "continuous re-acquisition" defense in [Psiaki and Humphreys 2016](psiaki-humphreys-2016-gnss-spoofing-detection.md), and it works on TEXBAT ds3/ds4 IQ.
- **The detection window is the drag-off:** capture took about 30 s in the demo (Fig. 11). Monitors that only look at PVT output miss it, so log correlator-level data if the stack exposes it.
- **Design takeaway for a GNSS-denied nav stack:** treat single-antenna, unauthenticated GNSS as untrusted against a capable adversary. Cross-check it against inertial/visual odometry and, where available, Galileo [OSNMA](galileo-osnma.md).
