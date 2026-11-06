# Real-World Spoofing Detection with Low-Cost Receivers - paper digest
<!-- about: res:kreizis-ion-itm-2025-spoofing -->
**Real-World Spoofing Detection and Characterization Using Low-Cost Receivers** - Kriezis, Chen, Akos, Lo, Walter (Stanford GPS Lab, CU Boulder), ION ITM 2025. [paper](https://web.stanford.edu/group/scpnt/gpslab/pubs/papers/Kriezis_ION_ITM_2025_Real_World_Spoofing_Detection.pdf) | code: none | Read: full text, Stanford-hosted PDF (11 pages)

Note: the first author's name is spelled "Kriezis" in the paper. The index id and the PDF filename use "Kriezis".

## Problem
Most spoofing-detection work is tuned on lab or test-range data, where the spoofing technique is known. This paper takes a real, uncontrolled spoofing event recorded on commodity receivers. It asks which standard detection metrics actually fire, and what the data reveals about the spoofer.

## Method
- Two u-blox F9P receivers on a ship heading to Haifa, southeast Mediterranean, summer 2024: one L1/L2 model and one L1/L5 model (Sec. II).
- L5 / Galileo E5a saw no jamming or spoofing during the event, so the authors use them as reference truth (Sec. II).
- Detection metrics are grouped into four classes (Sec. III): position solution, signal power (AGC, C/N0), signal information (ephemeris, IODE, update timing), and signal consistency (Doppler, pseudorange residual, clock drift).
- Each metric is graded "useful / not useful / N/A" in two cases (Table 1):
  - cold start: the receiver switches on during spoofing;
  - over time: the receiver is already tracking when spoofing begins.
- The RFI detector from the DFMC SBAS MOPS (EUROCAE ED-259) is run on the ship data (Sec. IV). It uses C/N0 against a 27 dB-Hz availability threshold and a "fewer than five satellites" trigger.
- Characterization (Sec. V): the pseudorange equation is split into spoofed and true terms. The shared receiver clock is solved from the unspoofed L5 channel, then used to isolate the spoofer-to-user range plus delay term (Eq. 5).

## Data and sensors
- Sensors: low-cost dual-frequency receivers only (u-blox F9P L1/L2 and L1/L5). The paper works from receiver outputs (PVT, C/N0, AGC, Doppler, pseudorange, navigation files), not raw IQ.
- Data: the authors' own ship recording, not released (no data availability statement found).
- Public alternatives for similar real or field spoofing:
  - [Jammertest data](../dataset-cards/jammertest-data.md): authority-run live spoofing with u-blox and phone logs;
  - [S7AM1NA phone spoofing set](../dataset-cards/gnss-spoofing-s7am1na.md);
  - [TEXBAT](../dataset-cards/texbat.md): signal-level lab recordings.

## Headline results (as reported)
- Sec. II, Fig. 2: spoofing first appeared about 10 km from the Israeli coast, with the position jumping to Beirut airport. Jamming saturated the AGC before spoofing began.
- Sec. III-3: ephemeris and IODE matched the true values. Most ephemeris updates came "within 18 seconds of the real signal". The authors conclude the spoofer had a real-time GNSS feed, so ephemeris checks were N/A.
- Fig. 8: at onset, the SV 27 pseudorange jumped by 2267 km within seconds on both L1 and L5. Fig. 9: the L5-derived receiver clock bias jumped by the equivalent of about 2400 km. In other words, the spoofed L1 corrupted the clock shared with the clean band.
- Sec. III-2, Fig. 5: after onset, L1 C/N0 split from L2 and stopped following elevation (flat). On the L1/L5 receiver, L1 C/N0 values under heavy jamming were too high to be real.
- Table 1:
  - C/N0 was useful at both cold start and over time.
  - Position, pseudorange residual and clock drift were useful only over time.
  - AGC and Doppler were not useful (Doppler matched L5 in shape, Fig. 7).
  - The ephemeris check was N/A.
- Sec. IV: the MOPS algorithm scored 94% accuracy with 4% false positives on the L1/L5 receiver. The authors call this "coincidental": that receiver rejected L1 signals inconsistent with L5, which tripped the satellite-count trigger. On the L1/L2 receiver, accuracy was "under 13%".

## Limitations
- Stated by authors:
  - Single event, single route.
  - The spoofer-geometry characterization (Eq. 5) showed no clear trend, attributed to a moving spoofer, unstable delay or mixed solutions. Those results were not included.
  - Most over-time metrics rely on catching the onset.
  - A spoofer that targets its power could defeat the C/N0 cue.
- Our read:
  - No ROC, thresholds or timing-to-detect are given for the individual metrics. "Useful" is a qualitative grade.
  - The L5-as-truth approach only works while L5 is clean. Multi-band spoofing would remove the reference.
  - The index links RTKLIB as this paper's code. The paper does not mention RTKLIB or any tool, so that link is an index inference, not the authors' code.

## Code, weights, license
No code, data or weights released. A paper PDF is hosted by the Stanford GPS Lab, and ION holds the proceedings copyright.

## Reproduction effort (estimate)
Estimate: the paper's event itself cannot be reproduced (the data is private). The metric set can be rebuilt in about 1 day:
- Hardware: none for replay. A u-blox F9P (L1/L5 variant if possible) for a live demo.
- Data: Jammertest VAARA u-blox logs (about 1.6 GB, plain git) give real spoofing with test-plan labels.
- Tooling: [pyubx2](../integration-cards/semuconsulting__pyubx2.md) for NAV-SAT C/N0, MON-RF AGC and NAV-CLOCK; [gnss_lib_py](../integration-cards/stanford-navlab__gnss_lib_py.md) or [RTKLIB](../integration-cards/rtklibexplorer__rtklib.md) for residuals from RINEX.
- Not reproducible: the Sec. V characterization numbers (none published) and the exact MOPS implementation details.

## What a hackathon team can take from it
- **The best cue in this event was cross-band C/N0 consistency:** L1 versus L2/L5 C/N0 divergence, and L1 C/N0 that stays flat and ignores elevation. It costs nothing on any dual-band u-blox. The hub's `samples/gnss-interference-monitor` scorer is the natural place to add it.
- **Use the clean band as a reference.** Run a separate L5/E5a-only solution and compare it to the L1 fix. Also watch the shared receiver clock: Fig. 9 shows a spoofed L1 channel corrupting the clock used by L5.
- **Evaluate both modes.** Grade your detector at cold start and over time, as Table 1 does. Most cheap metrics fail at cold start.
- **Ephemeris and IODE checks are not enough.** The real-world spoofer updated ephemeris in real time, so pair those checks with power and clock checks. Navigation message authentication ([OSNMA](galileo-osnma.md)) covers that gap for Galileo data.
- **For a GNSS-denied stack:** a detected spoof should de-weight GNSS in the EKF and hand over to INS/VIO. Do not wait for a satellite-count or RAIM alarm, which can stay silent (MOPS under 13% on L1/L2).
