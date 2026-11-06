# TEXBAT - Texas Spoofing Test Battery

<!-- about: res:ut-texbat, repo:gnss-sdr/gnss-sdr -->

UT Austin Radionavigation Lab's recorded GPS L1 C/A spoofing scenarios (TEXBAT 1.0 in 2012, 1.1 in 2015 added ds7/ds8). The standard signal-level benchmark for spoofing detection and authentication work.

| Field | Value |
|---|---|
| Platform | Static and dynamic (moving) receiver recordings, as the file names say; the exact antenna/vehicle setup is in the 2012 paper (not re-read here) |
| Environment | Austin, Texas; spoofer signals mixed in at RF and recorded |
| Sensors and rates | Raw IQ at L1 (center 1575.42 MHz), IQ rate 25 MS/s, int16 interleaved I/Q (from `ds1.xml` header and `scott.m` reader). NI PXIe RF record/playback chain (page lists models) |
| Ground truth | Scenario definitions (spoofing start, time push or position push, power matched or overpowered). No separate truth trajectory file in the directory listing |
| Size | Directory listing (2026-11-06): ds1-ds4 43 GB each, ds5-ds6 39 GB, ds7-ds8 44 GB, cleanStatic 45 GB, cleanDynamic 41 GB, cleanStatic80 7.5 GB. HEAD: ds2.bin = 45,717,913,600 bytes; cleanStatic80.bin = 8,016,392,192 bytes. Total about 430 GB. Pre-processed observables in `processed/ds3/` total about 0.8 GB (listing) |
| License | Copyright UT; free use for research; "users are requested to refrain from distributing the data" (page) |
| Format | `.bin` raw int16 IQ, `.xml` NI LabVIEW header, `.md5`; `processed/` has MATLAB `.mat` (channel, navsol, iq) from UT's GRID/pprx receiver |
| Index | [TEXBAT](../../catalog/resources/ut-texbat.md), [GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) |

## What's in it

| File | Content (2012/2015 papers as summarised on the page and commonly cited) |
|---|---|
| cleanStatic, cleanDynamic | No spoofing, reference |
| ds1 | Static switch attack |
| ds2 | Static, overpowered time push |
| ds3 | Static, matched-power time push |
| ds4 | Static, matched-power position push |
| ds5 | Dynamic, overpowered time push |
| ds6 | Dynamic, matched-power position push |
| ds7 | Like ds3 but carrier-phase aligned (page) |
| ds8 | ds7 plus zero-delay security-code estimation and replay (SCER) (page) |

ds7/ds8 descriptions are from the page; ds1-ds6 labels are the standard TEXBAT 1.0 descriptions and were not re-read from the 2012 paper this session. Each full file is about 7.6 min of data (45.7e9 B / (25e6 S/s x 4 B)).

## Download

```bash
B=https://rnl-data.ae.utexas.edu/datastore/texbat
# smallest useful set: header + one attack, or the 7.5 GB clean file
curl -O $B/ds3.xml -O $B/ds3.md5 -O $B/scott.m -O $B/texbat_ds7_and_ds8.pdf
curl -C - -O $B/ds3.bin            # 43 GB, server supports byte ranges
# first N seconds only (int16 IQ, 4 bytes/sample, 25 MS/s): 60 s = 6.0 GB
curl -r 0-5999999999 -o ds3_first60s.bin $B/ds3.bin
# pre-processed observables (no SDR needed)
wget -r -np -nH --cut-dirs=3 $B/processed/ds3/
```

## Loading and tooling

```python
import numpy as np
fs = 25e6
x = np.fromfile("ds3_first60s.bin", dtype=np.int16, count=2*int(10*fs))  # 10 s
iq = x[0::2] + 1j*x[1::2]
```

[GNSS-SDR](../../catalog/repos/gnss-sdr__gnss-sdr.md) can process it with a File_Signal_Source set to `ishort`, 25e6 S/s, IF 0. `processed/readme.txt` says `.mat` arrays must be transposed after loading; formats described at `radionavlab.ae.utexas.edu/datastore/satNavCourse/`.

## Hackathon fit

- Idea 1 (interference monitor) and Idea 8 (authenticate-or-alarm): signal-level detectors - C/N0 jumps, correlator distortion (SQM), AGC/power, clock jumps - scored against known spoofing onset.
- Partial-range download lets a team run on 60-120 s windows on a laptop.

## Pitfalls

- Files are huge; venue Wi-Fi will not carry them. Pull byte ranges or the `processed/` observables in advance.
- GPS L1 C/A only, 2012-era; no Galileo/OSNMA, no multi-band.
- Redistribution is discouraged: do not mirror into a public repo.
- The `tbION_for_distribution` file in the listing is a PDF (the `.zip` name 404s).

## Sources

- https://radionavlab.ae.utexas.edu/texbat/ (description, ds7/ds8, copyright notice, NI hardware)
- https://rnl-data.ae.utexas.edu/datastore/texbat/ directory listing; HEAD on ds2.bin and cleanStatic80.bin; `ds1.xml` (IQ rate, center frequency); `scott.m` (int16 interleaved); `processed/readme.txt`
