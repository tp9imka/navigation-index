# GPS-SDR-SIM - integration card
<!-- about: repo:osqzss/gps-sdr-sim -->
Generates GPS L1 C/A baseband IQ sample files for a chosen static position or trajectory and time. In a hackathon use it only to produce **files** that a software receiver ([GNSS-SDR](./gnss-sdr__gnss-sdr.md)) processes offline: repeatable test vectors for receiver, integrity and spoofing-detector development with no RF involved.

> **Legal boundary.** Radiating GNSS signals over the air without authorization is illegal in practically every jurisdiction (in the US under FCC rules and federal law; in the EU/UK under national radio law) and endangers aviation and other users. This card covers file generation and offline processing only. Any hardware test must be cabled into the receiver under test through attenuation, or done in a certified shielded enclosure under the relevant authorization. Read [docs/export-control-and-ethics.md](../export-control-and-ethics.md) first. The repo README includes SDR playback commands; they are deliberately not reproduced here.

| | |
|---|---|
| Install | No release tags. `git clone https://github.com/osqzss/gps-sdr-sim && cd gps-sdr-sim && gcc gpssim.c -lm -O3 -o gps-sdr-sim` (README). For trajectories longer than the default: `make USER_MOTION_SIZE=4000` or `-DUSER_MOTION_SIZE=4000`. Windows: Visual Studio project with `gpssim.c` + `getopt.c`. |
| Runs on | Any OS with a C compiler (single C file, libm). No GPU. Repo archived (read-only) since 2025; last push 2025-01-26. |
| Inputs | GPS broadcast ephemeris RINEX nav file (`-e`, required); parser keys on RINEX 2 header labels (`ION ALPHA`, `END OF HEADER` in `readRinexNavAll`), so use RINEX 2 `brdcDDD0.YYn` (e.g. NOAA CORS `brdc` files, no login; NASA CDDIS needs a free Earthdata account). Position: static `-l lat,lon,hgt` or `-c x,y,z` (ECEF m); dynamic 10 Hz trajectory as ECEF CSV (`-u`), LLH CSV (`-x`) or NMEA GGA (`-g`). Start time `-t YYYY/MM/DD,hh:mm:ss`. |
| Outputs | Interleaved I/Q samples, baseband (zero IF), default file `gpssim.bin` (`-o -` for stdout). Formats `-b 16` signed int16 (default), `-b 8` signed int8, `-b 1` packed 1-bit. Default rate 2.6 MS/s (`-s`). `-v` prints simulated channels (PRN, az/el, range). |
| Key API / entry points | Single CLI `gps-sdr-sim` with flags `-e -u -x -g -c -l -t -T -d -o -s -b -i -p -v -L` (from README usage block). Internals in `gpssim.c`: `readRinexNavAll()`, `readUserMotion()`, channel generation loop in `main()`. Durations: dynamic max 300 s, static max 86400 s (README). |
| Time to first result | Estimate: 10 min to compile and generate a 60 s static file (assumes gcc and a RINEX 2 brdc file); file size at default settings is about 2.6e6 samples/s x 4 bytes = ~10 MB per second of signal (derived from the format, not measured). Add the GNSS-SDR setup time for a fix. |
| License | MIT. |

## Minimal usage
Not run. File generation only:

```bash
gcc gpssim.c -lm -O3 -o gps-sdr-sim
# 60 s static scenario, int16 I/Q, 2.6 MS/s baseband
./gps-sdr-sim -e brdc0010.22n -l 30.286502,120.032669,100 -d 60 -o static.bin
# 10 Hz trajectory from the bundled example (brdc0010.22n, circle.csv, rocket.csv ship in the repo)
./gps-sdr-sim -e brdc0010.22n -u circle.csv -d 120 -o circle.bin
```

Then process `static.bin` with GNSS-SDR using `SignalSource.item_type=ishort` and `sampling_frequency=2600000` (see [GNSS-SDR card](./gnss-sdr__gnss-sdr.md)). For a spoofing-detector dataset, generate a truth file at the real position and a second file along a diverging trajectory, then compare what the receiver outputs; both stay files.

## Wiring it into a nav stack
- Offline loop: trajectory CSV (from a planned route or a [gnss-ins-sim](./aceinna__gnss-ins-sim.md) run, converted to 10 Hz ECEF) => IQ file => [GNSS-SDR](./gnss-sdr__gnss-sdr.md) => RINEX/NMEA/UDP monitor => your integrity check or GNSS/INS filter. You get IQ-level realism where gnss-ins-sim only gives position-level GNSS.
- Detector development: GNSS-SDR's `gnss_synchro` monitor gives C/N0 and tracking flags per channel; the [gnss-interference-monitor sample](../../samples/gnss-interference-monitor/README.md) shows a scoring approach.
- Mixing a "spoofer" file with an "authentic" file at different power levels is possible in numpy (add int16 arrays with scaling) to emulate a takeover in post-processing. Not tested here.
- Do not use it to test OSNMA: GPS L1 C/A only, no Galileo. See [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md) for Galileo test vectors.

## Gotchas
- **Archived repo**: no fixes will land. Derivatives such as multi-sdr-gps-sim continue development.
- RINEX 3 nav files: open issue #288 "Rinex version"; the parser targets RINEX 2 GPS nav. Convert or download RINEX 2.
- Start time must be inside the ephemeris validity; otherwise it falls back to the first TOC in the file. `-T` overwrites TOC/TOE to the scenario time (useful for "today" scenarios with old ephemeris, but the receiver will then decode a fake ephemeris).
- GNSS-SDR acquisition problems with sim files are a recurring issue topic (#309 "No PRN acquired after feeding the bin file to GNSS SDR"); usual cause is item type or sample-rate mismatch in the receiver config.
- `-p` disables path loss (constant power); default includes a free-space path loss model, which matters if you study C/N0-based detectors.
- No multipath, no antenna pattern, no receiver clock model beyond the trajectory: signals are cleaner than reality, so thresholds tuned on sim data are optimistic.

## Alternatives
- [multi-sdr-gps-sim](../../catalog/repos/mictronics__multi-sdr-gps-sim.md) - maintained derivative with more SDR backends; same legal boundary applies.
- [OSNMA-SDR-SIM](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md) - Galileo E1 with OSNMA, for authentication testing.
- [gnss-ins-sim](./aceinna__gnss-ins-sim.md) - when you only need position/IMU level synthetic data, not IQ; much faster.

Sources: https://github.com/osqzss/gps-sdr-sim README.md (raw), `gpssim.c` (`readRinexNavAll`, usage text), repo metadata (MIT, archived, pushed 2025-01-26), issues #288 #212 #309, gnss-sdr/gnss-sdr issue #499.
