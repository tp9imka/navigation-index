# Integrity monitoring for navigation and alt-PNT

<!-- about: repo:stanford-gps-lab/maast_for_araim_2, repo:michaelbeechan/raim, res:ion-webinar-gipson -->

After this page you can explain what a protection level is and why it is different from an
accuracy number, run a solution-separation monitor over several alt-PNT sources, and show
judges a Stanford diagram that proves your navigator does not lie silently.

Working code: [samples/altpnt-integrity](../samples/altpnt-integrity/) (stdlib Python, run
and tested). Numbers quoted on this page from that sample are its observed output.

## 1. Why this is a differentiator

The [GNSS-denied navigation products landscape](landscape/gnss-denied-nav-products.md)
lists about ten vendors selling camera-to-map visual navigation. Most give no accuracy
numbers at all, and none of the sources found there publishes integrity or failure data:
how often the system is wrong without warning, how fast it warns, or what bound it
guarantees. Aviation GNSS has a 30-year vocabulary for exactly that
question. Porting it to visual, terrain and magnetic fixes is open work, and a hackathon
team that shows a protection level with a negative control is answering a question the
products do not.

## 2. Vocabulary

| Term | Meaning |
|---|---|
| Accuracy | statistics of the position error (PE), e.g. 95th percentile |
| Integrity | the ability to bound the error and to warn in time when the bound cannot be trusted |
| Continuity | probability that the service, once started, is not interrupted (by alerts, exclusions) |
| Availability | fraction of time the service meets all requirements, including PL < AL |
| Protection level (PL) | a bound the system computes on its own error, at a stated integrity risk; HPL horizontal, VPL vertical |
| Alert limit (AL) | the largest error the operation tolerates; set by the operation, not by the sensor |
| Time to alert (TTA) | time from the error exceeding AL (or the fault starting) to the alert reaching the user |
| Integrity risk | probability that PE > PL without an alert within TTA |
| P_FA, P_MD | false-alert and missed-detection probabilities that set detection thresholds |
| MI | misleading information: PE > PL while the system says it is available |
| HMI | hazardously misleading information: PE > AL while the system says it is available |

The core rule: a navigator may be inaccurate, but it must not be inaccurate *and* confident.
`PL >= AL` is not a failure; it is the system correctly saying "do not use me for this".
The failure is PE > PL without an alert.

The [GPS SPS Performance Standard](../catalog/resources/gps-sps-performance-standard-2020.md)
is the formal statement of these terms for civil GPS; [Navipedia](../catalog/resources/navipedia.md)
covers RAIM, SBAS and integrity terms. The [DHS Resilient PNT Conformance Framework](../catalog/resources/dhs-resilient-pnt-conformance-framework.md)
describes receiver behaviour under attack (prevent, respond, recover) but does not define
protection levels.

## 3. RAIM and ARAIM in one page

**Residual-based RAIM (chi-square).** With more measurements than unknowns, the
least-squares residual vector `r` has `r^T W r ~ chi2(n - m)` when fault-free. Exceeding the
threshold for `P_FA` means "some measurement is faulty". The PL is derived from how large a
single fault can be while still keeping the test statistic under the threshold
(the "slope" of each measurement). [MichaelBeechan/RAIM](../catalog/repos/michaelbeechan__raim.md)
is a MATLAB implementation of classic RAIM FDE.

**Solution separation (SS).** Compute the all-in-view solution `x0` and one sub-solution
`x_j` per fault hypothesis j (all measurements except subset j). Under no fault, the
separation `d_j = x0 - x_j` is zero-mean with covariance `P_j - P0` (for optimal
estimators). Test `|d_j| > T_j = K_fa * sigma_dj`. The PL covers both the fault-free case and
each hypothesis:

```
HPL = max( K_ff * sigma_0 ,  max_j ( T_j + K_md * sigma_j ) )
K_fa = Q^-1(P_FA / (2 N)),  K_md = Q^-1(P_MD),  K_ff = Q^-1(IR_ff / 2)
```

Brenner introduced SS for integrated GPS/inertial systems: a bank of sub-filters each
excluding one satellite, with the separation from the full filter as the test statistic
(Brenner 1996). Joerger, Chan and Pervan compare the two: SS can monitor better in principle because its
test statistics are tailored to each fault hypothesis and to the state of interest, but in
conventional implementations, for computational reasons, residual-based RAIM ends up with
tighter integrity-risk bounds (Joerger et al. 2014, abstract). The SS form transfers directly
to Kalman filters, which is why the sample uses it.

**ARAIM** generalises RAIM to multiple constellations and dual frequency: each fault mode
(single satellite, constellation-wide) has a prior probability from an Integrity Support
Message, hypotheses whose prior is below a threshold are not monitored, and the integrity
and continuity budgets are allocated across the monitored hypotheses with SS
(Blanch et al. 2012; Blanch et al. 2015). [MAAST for ARAIM](../catalog/repos/stanford-gps-lab__maast_for_araim_2.md)
is the Stanford GPS Lab MATLAB tool that evaluates ARAIM availability and PLs over service
areas.

Two ideas from ARAIM carry over to alt-PNT almost unchanged:

1. **Fault priors decide what you monitor.** You cannot protect against every fault
   combination. You list fault modes, give each a prior, and monitor the ones whose prior
   exceeds the integrity budget.
2. **Exclusion needs its own check.** After excluding j, the remaining solution must pass
   its own test, otherwise a wrong exclusion becomes undetected HMI.

## 4. Integrity in a Kalman filter

- **Innovation (NIS) gating.** For each measurement, `nu^T S^-1 nu ~ chi2(dim z)` under the
  filter's model. Rejecting above the 99.9 % quantile removes gross outliers. It is the
  first layer, not a monitor: a slow ramp is absorbed by the filter state, so the
  innovation stays small. The [gnss-ins-ekf-outage sample](../samples/gnss-ins-ekf-outage/)
  shows a gate missing spoofing walk-offs at 0.5 m/s and below.
- **Gate failure under uncertainty.** When the filter is uncertain (long outage), S is
  large and a 60 m outlier passes. When the filter is confidently wrong (it absorbed a bias),
  the gate rejects the *healthy* source. The altpnt-integrity sample shows the second case:
  after absorbing a map-misregistration bias during a GNSS outage, the gate-only filter
  rejected the returning, healthy GNSS for 61 consecutive epochs with 30-37 m error and a
  smaller PL.
- **Filter-based integrity risk.** Joerger and Pervan build a test statistic from current
  and past Kalman residuals and evaluate the integrity risk directly, rather than per-epoch
  gating (Joerger and Pervan 2013).
- **Multi-filter all-source navigation.** AFIT's work runs multiple filters and monitors
  sensor integrity to detect and isolate faulty or spoofed inputs
  ([ION webinar, Gipson](../catalog/resources/ion-webinar-gipson.md)). That is the same
  bank-of-filters structure as SS, applied to heterogeneous sensors.

## 5. Translating to non-GNSS fixes

The math does not care where an absolute fix comes from. The fault models do.

| Source | Nominal error | Fault modes that matter for integrity | What breaks in the GNSS recipe |
|---|---|---|---|
| Visual map-matching / geolocalization ([concept page](../catalog/concepts/visual-geolocalization.md)) | metres to tens of metres, depends on altitude, map resolution, matcher | repetitive texture (fields, roofs, forests) => confident wrong match, often far away; map misregistration or stale imagery => consistent bias that passes gates; water, snow, featureless terrain, night => dropouts; seasonal change => degraded match | errors are multimodal and spatially correlated, not white Gaussian; a single-sigma overbound is either huge or wrong |
| Terrain-relative nav (TRN / TERCOM, [concept page](../catalog/concepts/terrain-nav.md)) | depends on terrain roughness; poor over flat terrain | flat or self-similar terrain => ambiguous, multimodal posterior; DEM errors and vegetation vs bare-earth mismatch => bias; radar altimeter over water or forest canopy | particle-filter posterior is not Gaussian; PL should come from the posterior mass, not a covariance |
| Magnetic anomaly nav ([concept page](../catalog/concepts/magnetic-nav.md)) | tens to hundreds of metres, depends on map resolution and anomaly gradient | platform magnetic interference not compensated; map resolution and age; weak gradient regions => ambiguity; diurnal and space-weather variation | errors correlated over long distances; independent of imagery, which makes it a good cross-check for vision |
| VIO / VO ([concept page](../catalog/concepts/vio.md)) | relative only, drift ~ distance flown | scale error, yaw drift, loss of tracking, dynamic scenes | gives no absolute check but gives the dead-reckoning reference every consistency test needs |

Research that does this for cameras:

- Zhu, Meurer and Günther review integrity for visual navigation, with a framework for
  feature-based methods and the open problems (feature error modelling, illumination)
  (Zhu et al. 2022).
- Gupta and Gao compute data-driven PLs for camera-to-3D-map localization with a
  Gaussian-mixture error model learned per candidate pose (Gupta and Gao 2021).
- Mohanty, Gupta and Gao extend particle-filter RAIM to GNSS + camera, use map-matching for
  a camera position distribution, and check consistency between the two sensors with a
  KL-divergence test (Mohanty et al. 2020).
- Bhamidipati and Gao run SLAM-based integrity monitoring with GPS and a fish-eye camera,
  detecting faults in both and computing PLs (Bhamidipati and Gao 2019).
- For satellite-thermal UAV geolocalization, [UASTHN](../catalog/resources/uasthn-uncertainty-thermal-2025.md)
  outputs an uncertainty with the homography, which is the input a PL needs.

## 6. FDE with several alt-PNT sources

How many independent absolute sources you have decides what the monitor can do. The
altpnt-integrity sample makes this concrete (20 seeds, AL 50 m, full monitor):

| Absolute sources active | Detect | Identify | What the sample shows |
|---|---|---|---|
| 1 (vgeo only, GNSS off) | only against dead reckoning | yes, if VIO is trusted | zero MI, but 5.0 % availability: the fault term of the PL is the INS + VIO drift |
| 2 (vgeo + GNSS, or vgeo + MagNav) | yes | no: each sub-filter keeps one suspect | alert, rewind, resolve by consistency with dead reckoning; spoof detected 15 s after onset, blamed 65 s after onset on seed 1 |
| 3 (vgeo + GNSS + MagNav) | yes | yes, by largest normalised separation | spoof excluded 28 s after onset on seed 1; 49.5 % availability vs 41.7 % without MagNav |

Rules worth taking away:

- **Two sources detect, three identify.** With two, do not guess. Alert, coast, and let
  dead reckoning arbitrate. In the sample, without GNSS and with only vgeo + MagNav, dead
  reckoning was too loose to tell a 35 m misregistration from MagNav noise within 45 s, and
  11 of the blames over 20 seeds hit the wrong source. Integrity held because the alert was
  up; continuity did not.
- **Independence is a property of the data, not the sensor.** Visual geolocalization and
  TRN that share an orthophoto and DEM from the same misregistered source share the fault.
  SS cannot see a common-mode bias. MagNav or a radio fix is a better third source for a
  vision system than a second vision matcher.
- **A wrong exclusion must still be bounded.** After excluding, the rebuilt bank starts at
  zero separation. The sample keeps the spread between the candidate branches in the PL for
  30 s; without that term one seed in the 3-source run produced 3 MI epochs after a wrong
  exclusion (observed during development, before the term was added).

## 7. Consistency between VIO drift and absolute fixes

VIO is the referee for absolute fixes when nothing else agrees, so its drift model is the
most important number in the monitor.

- Model VIO error as a state (scale, yaw, or a velocity bias with a Gauss-Markov model)
  rather than white noise. White noise on velocity makes the filter believe position drift
  grows with sqrt(t) when it grows with t; the PL then underbounds during long gaps.
- Test an absolute source against a dead-reckoning branch that has not seen that source
  recently. In the sample, on a two-source alert the main filter is rewound 30 s and
  replayed on INS + VIO only, removing what the faulty source injected before detection.
  Without the rewind (observed during development), the filter's VIO-bias state had
  learned the spoofer's walk-off rate and the coasting solution kept drifting with the
  spoofer, from 13 m to 66 m error over 100 s.
- The race is spoof rate vs drift bound. A fix passes probation if its offset stays inside
  the dead-reckoning uncertainty for the probation window. A spoofer slower than the drift
  bound per window is indistinguishable from drift. Longer windows catch slower faults and
  cost continuity.
- A source that just came back from an outage is the easiest to spoof: the filter's
  covariance is large and the gate is wide. Probation before re-admission closes that hole.

## 8. Presenting it to judges

Judges see accuracy plots every round. Show the four things below instead.

1. **Stanford diagram.** PE on x, PL on y, both log scale; diagonal PE = PL; vertical and
   horizontal lines at AL. Regions: nominal (PE < PL < AL), unavailable (PL >= AL), MI
   (PL <= PE, PL < AL), HMI (PE >= AL, PL < AL). The form comes from the Stanford WAAS
   laboratory; the Stanford-ESA integrity diagram variant is documented on Navipedia
   (Tossaint et al. 2006). `python3 altpnt_integrity.py --svg stanford.svg` writes one.
2. **Negative control.** Same flight, monitor off. In the sample, seed 1 goes from 169 HMI
   epochs (monitor off, HPL median 4.8 m, error up to 263 m) to 0. Without the control a
   zero-MI claim says nothing.
3. **The availability cost, stated up front.** Availability vs AL for each configuration.
   Full-monitor availability on seed 1 is 45.8 % at AL 50 m and 91.7 % at 250 m. Showing
   it is what makes the zero-HMI claim credible.
4. **Monitor log on the timeline.** "330 s vgeo excluded (map misregistration), 435 s
   ambiguous alert (spoof), 485 s GNSS blamed." Judges remember events, not tables.

One sentence pitch: "Our navigator reports a protection level every epoch; in 12 000
simulated epochs with spoofing, outliers and map errors it was never wrong without saying
so, and here is the same flight with the monitor off."

## 9. Pitfalls

- A PL is a model output. If R and Q are optimistic, the PL is optimistic. Overbound
  noise, check MI on a fault-free Monte Carlo, then add faults.
- `P_j - P0` as the separation covariance assumes optimal filters fed the same data.
  Gating breaks that slightly; floor the separation sigma.
- AL, P_FA and P_MD in the sample are illustrative. No UAV alt-PNT integrity standard was
  used or is claimed.
- Integrity risk numbers like 1e-7 cannot be validated by simulation of a few thousand
  epochs. What a hackathon can show is zero MI over the runs you did plus a negative
  control that does produce MI.
- Multimodal sources (repetitive texture, TRN over flat terrain) need mixture or particle
  PLs; a single Gaussian either underbounds the tail or makes the PL useless.

## References

Verification notes: "abstract page fetched" means the paper's landing page was read on
2026-11-06; "bibliographic record" means title, venue and DOI were confirmed from an index
or publisher record but the text was not read.

- Brenner, M. "Integrated GPS/Inertial Fault Detection Availability." NAVIGATION 43(2),
  111-130, 1996. doi:10.1002/j.2161-4296.1996.tb01920.x. Bibliographic record.
- Joerger, M., Chan, F.-C., Pervan, B. "Solution Separation Versus Residual-Based RAIM."
  NAVIGATION 61(4), 273-291, 2014. doi:10.1002/navi.71. Abstract fetched
  ([University of Arizona portal](https://experts.arizona.edu/en/publications/solution-separation-versus-residual-based-raim/)).
- Joerger, M., Pervan, B. "Kalman Filter-Based Integrity Monitoring Against Sensor Faults."
  Journal of Guidance, Control, and Dynamics 36(2), 349-361, 2013. doi:10.2514/1.59480.
  Bibliographic record.
- Blanch, J., Walter, T., Enge, P., Lee, Y., Pervan, B., Rippl, M., Spletter, A.
  "Advanced RAIM User Algorithm Description: Integrity Support Message Processing, Fault
  Detection, Exclusion, and Protection Level Calculation." ION GNSS 2012, Nashville.
  Listed on the [Stanford GPS Lab publications page](https://web.stanford.edu/group/scpnt/gpslab/www/pubs/index.htm);
  PDF located, not parsed.
- Blanch, J., Walter, T., Enge, P., et al. "Baseline Advanced RAIM User Algorithm and
  Possible Improvements." IEEE Transactions on Aerospace and Electronic Systems 51(1),
  713-732, 2015. Bibliographic record (dblp).
- Tossaint, M., Samson, J., Toran, F., Ventura-Traveset, J., Sanz, J., Hernandez-Pajares,
  M., Juan, J. M., Tadjine, A., Delgado, I. "The Stanford - ESA Integrity Diagram: Focusing
  on SBAS Integrity." 2006. [Navipedia article](https://gssc.esa.int/navipedia/index.php/The_Stanford_%E2%80%93_ESA_Integrity_Diagram:_Focusing_on_SBAS_Integrity)
  fetched (regions and axes as described above).
- Zhu, C., Meurer, M., Günther, C. "Integrity of Visual Navigation - Developments,
  Challenges, and Prospects." NAVIGATION 69(2), navi.518, 2022.
  [doi:10.33012/navi.518](https://doi.org/10.33012/navi.518). Abstract page fetched.
- Gupta, S., Gao, G. X. "Data-Driven Protection Levels for Camera and 3D Map-based Safe
  Urban Localization." 2021. [arXiv:2101.06379](https://arxiv.org/abs/2101.06379).
  Abstract page fetched.
- Mohanty, A., Gupta, S., Gao, G. X. "A Particle Filtering Framework for Integrity Risk of
  GNSS-Camera Sensor Fusion." ION GNSS+ 2020. [arXiv:2101.06044](https://arxiv.org/abs/2101.06044).
  Abstract page fetched.
- Bhamidipati, S., Gao, G. X. "SLAM-based Integrity Monitoring Using GPS and Fish-eye
  Camera." ION GNSS+ 2019. [arXiv:1910.02165](https://arxiv.org/abs/1910.02165).
  Abstract page fetched.

Indexed resources used on this page:
[MAAST for ARAIM](../catalog/repos/stanford-gps-lab__maast_for_araim_2.md),
[RAIM (MATLAB)](../catalog/repos/michaelbeechan__raim.md),
[ION webinar: multi-filter all-source navigation with assurance](../catalog/resources/ion-webinar-gipson.md),
[GPS SPS Performance Standard](../catalog/resources/gps-sps-performance-standard-2020.md),
[Navipedia](../catalog/resources/navipedia.md),
[DHS Resilient PNT Conformance Framework](../catalog/resources/dhs-resilient-pnt-conformance-framework.md),
[UASTHN paper](../catalog/resources/uasthn-uncertainty-thermal-2025.md),
[Groves, Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems](../catalog/resources/groves-pnt-book-2e.md),
[FilterPy](../catalog/repos/rlabbe__filterpy.md), [GTSAM](../catalog/repos/borglab__gtsam.md),
[assured-pnt concept](../catalog/concepts/assured-pnt.md),
[sensor-fusion concept](../catalog/concepts/sensor-fusion.md).
