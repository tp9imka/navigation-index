# 2. GNSS and its threats

After this chapter you can explain how a receiver turns satellite signals into a
position, read raw receiver output, pick between SPP, RTK and PPP, and build a
jamming or spoofing detector that runs on recorded data.

Prev: [PNT fundamentals](01-pnt-fundamentals.md) | Next: [Inertial and fusion](03-inertial-and-fusion.md) | [Primer index](README.md)

## How GNSS works

Each satellite broadcasts a spreading code plus a navigation message (orbit and clock
parameters). The receiver correlates the incoming signal against local code replicas to
measure *when* the signal left the satellite, and so the apparent range:

```
pseudorange  rho_i = || r_sat_i - r_user || + c * (dt_user - dt_sat_i) + I_i + T_i + e_i
```

- `r_user` (3 unknowns) and `dt_user`, the receiver clock offset (1 unknown), are what you
  solve for. Four satellites is the minimum; more give redundancy for integrity checks.
- `dt_sat`, orbits: from the broadcast message (defined bit-for-bit in
  [IS-GPS-200](../../catalog/resources/gps-is-gps-200n.md) and the
  [Galileo OS SIS ICD](../../catalog/resources/galileo-os-sis-icd-2-1.md)).
- `I`, `T`: ionospheric and tropospheric delays, modelled or removed with dual frequency.
- `e`: noise and multipath.

Solve with iterative least squares (Gauss-Newton): linearise around a guess, solve for the
correction, repeat. The geometry of the satellites in view scales measurement error into
position error (DOP). A full derivation with labs is in
[ESA GNSS Data Processing Vol. I](../../catalog/resources/esa-gnss-data-processing-vol1.md).

The receiver pipeline, which [Borre's book](../../catalog/resources/borre-software-defined-gps-galileo-receiver.md)
walks through in MATLAB and [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) implements in C++:

```
RF front end => acquisition (find code phase + Doppler) => tracking loops (DLL/PLL)
=> navigation message decoding => observables (pseudorange, carrier phase, Doppler, C/N0) => PVT
```

## Precision modes

| Mode | Idea | What the sources say | Hackathon cost |
|------|------|-----------------------|----------------|
| **SPP** (single point) | Broadcast orbits and clocks, one receiver | The baseline every phone does | Free |
| **DGNSS / RTK** | A nearby base station sends corrections; RTK also resolves carrier-phase integer ambiguities | Centimetre-level from low-cost u-blox receivers with RTKLIB demo5 ([rtklibexplorer](../../catalog/resources/rtklibexplorer-blog.md)) | Base station or NTRIP caster, RTCM parsing |
| **PPP** | Precise orbits and clocks from a global network, one receiver | Galileo HAS broadcasts free PPP corrections for decimetre-level PPP ([HAS ICD](../../catalog/resources/galileo-has-sis-icd.md)); IGS products are free ([IGS](../../catalog/resources/igs-products.md)) | Long convergence; post-processing is easier |

Corrections travel as RTCM 3 messages over NTRIP (HTTP streaming)
([Navipedia RTK standards](../../catalog/resources/navipedia-rtk-standards.md),
[BKG NTRIP](../../catalog/resources/bkg-ntrip-about.md)). Receiver output is usually NMEA
0183 text ([NMEA Revealed](../../catalog/resources/gpsd-nmea-revealed.md)) or a binary
vendor protocol such as u-blox UBX.

Phones are real GNSS sensors: Android exposes raw pseudoranges, carrier phase, C/N0 and AGC
([Android raw GNSS guide](../../catalog/resources/android-raw-gnss-developer-guide.md)).
Google's Smartphone Decimeter Challenge set decimeter-level smartphone positioning as its
target, and winning solutions used factor graphs and carrier phase
([GSDC 2023](../../catalog/resources/google-gsdc-2023.md)).

## Threats

### Jamming

A jammer adds power in the GNSS band until tracking loops lose lock. It is easy to
detect: C/N0 drops across all satellites at once and the front-end AGC changes. u-blox
receivers expose jamming indicators (MON-RF) that apps can read
([u-blox explainer](../../catalog/resources/ublox-looming-threat-jamming-spoofing.md)).
At the wide-area level, aircraft report degraded navigation integrity (NIC/NACp) in
ADS-B, which [GPSJam](../../catalog/resources/gpsjam-org.md) and the
[Flightradar24 map](../../catalog/resources/fr24-gps-jamming-map.md) aggregate. Both caution
that empty cells mean no data, not no jamming.

### Spoofing

A spoofer transmits counterfeit signals. A sophisticated one first aligns with the real
signals, then drags the victim's solution away smoothly
([Humphreys 2008](../../catalog/resources/humphreys-2008-assessing-spoofing-threat.md)).
The barrier to crude spoofing is low: open-source tools and cheap SDRs fooled phones and a
consumer drone ([DEF CON 23 talk](../../catalog/resources/defcon23-low-cost-gps-spoofing-sdr.md)).
In service, spoofing has hit airliners
([OPSGROUP](../../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md)), ships
([C4ADS](../../catalog/resources/c4ads-above-us-only-stars.md),
[Windward 2025](../../catalog/resources/windward-2025-maritime-stress-test.md)) and, through
defensive spoofing, civilian phones in Ukraine
([The Record](../../catalog/resources/therecord-ukraine-spoofing-civilian-phones.md)).

### Defenses, layered

The survey literature agrees that several weak tests combined beat any single test
([Psiaki and Humphreys 2016](../../catalog/resources/psiaki-humphreys-2016-gnss-spoofing-detection.md)):

| Layer | Check | Data you need |
|-------|-------|---------------|
| Receiver signal | C/N0 too uniform or too high, AGC jump, correlation peak distortion | Raw measurements, IQ for the last one |
| Measurement consistency | RAIM residuals, pseudorange vs Doppler vs carrier consistency, clock jumps | Raw observables |
| Multi-constellation / multi-band | Spoofing many signals consistently is harder | Multi-GNSS receiver ([u-blox](../../catalog/resources/ublox-looming-threat-jamming-spoofing.md)) |
| Cross-sensor | GNSS position vs INS/VIO prediction, innovation gating | A fusion filter (chapter 3) |
| Spatial | Angle-of-arrival: all spoofed signals arrive from one direction | Antenna array or motion ([Rothmaier webinar](../../catalog/resources/ion-webinar-rothmaier.md)), or several receivers ([Hendeby webinar](../../catalog/resources/ion-webinar-hendeby.md)) |
| Cryptographic | Galileo OSNMA authenticates navigation data | E1-B I/NAV bits, public key, loose time sync ([OSNMA ICD](../../catalog/resources/galileo-osnma-sis-icd.md)) |

OSNMA caveats you should state in a pitch: it authenticates the *navigation data*, not the
ranging signal, so it does not by itself stop replay or meaconing, and its security
depends on the receiver's time-sync assumption
([OSNMA receiver guidelines](../../catalog/resources/galileo-osnma-receiver-guidelines.md)).
Hardware defenses such as CRPA null-steering antennas
([NovAtel GAJT-410ML](../../catalog/resources/novatel-gajt-410ml-sheet.md)) and in-receiver
mitigation ([Septentrio AIM+](../../catalog/resources/septentrio-aim-plus.md)) exist; treat
vendor performance claims as claims.

## Failure modes under EW (summary)

- **Jammed:** no fix. Your system must notice quickly and switch to dead reckoning and
  alternative fixes (chapters 3 to 5).
- **Spoofed:** a fix that looks fine. Never let GNSS reset your filter without a
  consistency check; hybrid GNSS/INS can be dragged too
  ([FAA SAFO 24002](../../catalog/resources/faa-safo-24002.md)).
- **After the event:** some systems retain corrupted state after GNSS returns
  ([OPSGROUP](../../catalog/resources/opsgroup-gps-spoofing-final-report-2024.md)). Plan the
  re-acquisition path, not only the loss path.
- **Time:** spoofing can push time instead of position; anything downstream that trusts
  GNSS time inherits the error.

## Working safely with interference data

Do not transmit. Generate signals to **files** and feed them to a software receiver, or
use recorded datasets ([TEXBAT](../../catalog/resources/ut-texbat.md),
[Jammertest](../../catalog/resources/jammertest-norway.md) community recordings). The
legal reasons are in [Export control and ethics](../export-control-and-ethics.md#3-gnss-signal-simulation-and-rf-transmission).

## Learn it

1. [Stanford GPS MOOC](../../catalog/resources/stanford-gps-mooc-van-diggelen-enge.md) - pseudoranges and receiver basics.
2. [Navipedia](../../catalog/resources/navipedia.md) and [Navipedia OSNMA](../../catalog/resources/navipedia-osnma.md) - quick lookups.
3. [White paper: Protecting GNSS against intentional interference](../../catalog/resources/protecting-gnss-intentional-interference-arxiv.md) - threat and countermeasure taxonomy.
4. [ION webinar: Detecting jamming and spoofing on Android](../../catalog/resources/ion-webinar-akos.md) - phones as sensors.
5. [ESA GNSS Data Processing Vol. I](../../catalog/resources/esa-gnss-data-processing-vol1.md) then [Vol. II labs](../../catalog/resources/esa-gnss-data-processing-vol2.md) - SPP to PPP with gLAB.
6. [rtklibexplorer blog](../../catalog/resources/rtklibexplorer-blog.md) - practical RTK/PPK.
7. [Borre, Software-Defined GPS and Galileo Receiver](../../catalog/resources/borre-software-defined-gps-galileo-receiver.md) and [GNSS-SDR tutorials](../../catalog/resources/gnss-sdr-tutorials.md) - receiver internals.
8. [Recent advances on jamming and spoofing detection](../../catalog/resources/rados-2024-jamming-spoofing-detection-review.md) and [Lu 2024 anti-spoofing overview](../../catalog/resources/lu-2024-spoofing-antispoofing-overview.md).
9. [Psiaki and Humphreys, GNSS Spoofing and Detection](../../catalog/resources/psiaki-humphreys-2016-gnss-spoofing-detection.md) - the defense survey.
10. [Real-world spoofing detection (ION ITM 2025)](../../catalog/resources/kreizis-ion-itm-2025-spoofing.md) - which cues fire on live data.
11. Specs when you need bits: [IS-GPS-200N](../../catalog/resources/gps-is-gps-200n.md), [Galileo OS SIS ICD](../../catalog/resources/galileo-os-sis-icd-2-1.md), [OSNMA ICD](../../catalog/resources/galileo-osnma-sis-icd.md).

## Build with it

- [gnss_lib_py](../../catalog/repos/stanford-navlab__gnss_lib_py.md) - parse Android/RINEX logs, compute residuals; best 24h base for a detector.
- [GPS Measurement Tools / GnssLogger](../../catalog/repos/google__gps-measurement-tools.md) - log raw GNSS on Android.
- [pyubx2](../../catalog/repos/semuconsulting__pyubx2.md) and [PyGPSClient](../../catalog/repos/semuconsulting__pygpsclient.md) - u-blox jamming/spoofing flags live.
- [RTKLIB demo5](../../catalog/repos/rtklibexplorer__rtklib.md) / [RTKLIB](../../catalog/repos/tomojitakasu__rtklib.md) - SPP/RTK/PPK/PPP engines.
- [pygnssutils](../../catalog/repos/semuconsulting__pygnssutils.md) and [pyrtcm](../../catalog/repos/semuconsulting__pyrtcm.md) - NTRIP client and RTCM parsing.
- [georinex](../../catalog/repos/geospace-code__georinex.md) - RINEX into xarray.
- [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) - software receiver for IQ files.
- [GPS-SDR-SIM](../../catalog/repos/osqzss__gps-sdr-sim.md) - generate GPS L1 IQ **files** (archived but usable).
- [OSNMAlib](../../catalog/repos/algafix__osnma.md) and [galileo-osnma (Rust)](../../catalog/repos/daniestevez__galileo-osnma.md) - authenticate Galileo navigation data.
- [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md) - authenticate-or-alarm pipeline without RF.
- [readsb](../../catalog/repos/wiedehopf__readsb.md) - ADS-B decoding for NIC/NACp interference maps.
- [Multi-frequency GNSS spoofing dataset](../../catalog/repos/s7am1na__gnss-spoofing-dataset.md) - labelled phone logs (verify labels).
- [GPSSpy](../../catalog/repos/hoverflyhampton__gpsspy.md) - C/N0-based jamming detection to adapt.

Samples in this hub: [`samples/gnss-interference-monitor`](../../samples/gnss-interference-monitor/).

Related concepts: [GNSS](../../catalog/concepts/gnss.md), [RTK/PPP](../../catalog/concepts/gnss-rtk-ppp.md),
[GNSS SDR](../../catalog/concepts/gnss-sdr.md), [jamming and spoofing](../../catalog/concepts/gnss-interference.md).
