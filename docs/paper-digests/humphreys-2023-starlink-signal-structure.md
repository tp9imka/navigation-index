# Starlink Ku-band signal structure - paper digest
<!-- about: res:humphreys-2023-starlink-signal-structure, repo:gitlab.com/radionavlab/public/ut-starlink-signal-simulator -->
**Signal Structure of the Starlink Ku-Band Downlink** - Humphreys, Iannucci, Komodromos, Graff (UT Austin Radionavigation Lab), IEEE Transactions on Aerospace and Electronic Systems vol. 59 no. 5, pp. 6016-6030, Oct. 2023 (arXiv v3 2023-08-30). [paper](https://arxiv.org/abs/2210.11578) ([DOI](https://doi.org/10.1109/TAES.2023.3268610)) | [code (simulator, companion work)](https://gitlab.com/radionavlab/public/ut-starlink-signal-simulator) | Read: full text via ar5iv HTML rendering of the arXiv paper.

## Problem
Starlink's Ku-band waveform is undisclosed. To use it for opportunistic PNT you need known, repeating parts of the signal (pilots, sync sequences) to correlate against and form pseudoranges. The paper blindly identifies the OFDM parameters and the synchronization sequences from raw captures.

## Method
- Extends blind OFDM identification (previously shown only on simulated signals) to real captures (Secs. III-V).
- Symbol length N from the cyclic autocorrelation over power-of-two candidates 2^9-2^12, with a 10 dB validation threshold; guard length Ng from the cyclic autocorrelation at that N.
- Doppler modeled as both frequency shift and time compression/dilation; the authors argue compression cannot be ignored at this bandwidth.
- Sample rate Fs inferred from N (rounded to integer MHz), frame period from the cyclic autocorrelation (assumed integer Hz frame rate).
- Joint search over sample offset and carrier frequency offset, scored by constellation clustering (k-means, empirical SNR); works for 4QAM and 16QAM.
- Sync sequences found by cross-correlating symbol intervals across frames; the PSS recovered by coherent stacking of wideband data.
- Channel center frequency from the frame-arrival-time polynomial and CFO.

## Data and sensors
- 90 cm steerable offset dish (~3 deg beam, ~40 dBi at 12.5 GHz), tracks one satellite at a time above 50 deg elevation.
- Dual-band LNB, 60 dB gain, 0.8 dB NF.
- Narrowband mode: ~60 MHz usable, 16-bit complex at 62.5 Msps, GPS-disciplined OCXO. Wideband mode: ~1 GHz, 12-bit real at 4096 Msps, 1 s segments, sample clock not shared with the LNB, worse SNR.
- A Starlink user terminal was not used (raw samples would need defeating its security; unknown clock).
- Satellites observed: Starlink versions 0.9, 1.0, 1.5. Captures not released. No dataset card in this hub.

## Headline results (as reported)
- Table II: channel bandwidth Fs = 240 MHz; N = 1024 subcarriers; cyclic prefix Ng = 32; subcarrier spacing 234,375 Hz; useful symbol 64/15 us; symbol duration 4.4 us; frame period 1/750 s (~1.333 ms); 302 symbols per frame (298 data); frame guard 68/15 us; channel spacing 250 MHz; guard band 10 MHz; Fc,i = 10.7 + F/2 + 0.25(i - 1/2) GHz.
- Eight channels in the band, two lowest vacant; 4-subcarrier gutter mid-channel (Secs. V, Figs. 5-6).
- PSS (symbol 0): eight repetitions of an N/8 subsequence, a DPSK encoding of a length-127 m-sequence from LFSR polynomial 1 + D^3 + D^7; seed given in hex. Identical across frames and satellites (Sec. V-G, Eqs. 36-42).
- SSS (symbol 1): 4QAM OFDM symbol on subcarriers 2..N-3, phase sequence given in hex; identical across satellites; not a known canonical sequence.
- Fig. 7: correlation against a local PSS replica gives sharp peaks at each frame start.
- Frame occupancy never below one frame per 40 ms in the intervals studied.
- Claimed: coherent combination of the sync sequences enables pseudorange and Doppler observables below -6 dB SNR. No positioning or timing accuracy is demonstrated in this paper.

## Limitations
- Stated by authors: one satellite at a time, no synoptic view; wideband mode limited; PSS and SSS identical across satellites, so they do not identify the satellite; CM1SS (symbol 300) and CSS (symbol 301) only partly characterized, full details deferred; header (symbols 2-5) and pilots inferred; Starlink v2.0 satellites not verified; Fs assumed an integer MHz multiple.
- Our read: the index summary is accurate, but note the paper stops at "observables are possible" - it gives no ranging or position numbers.
- Our read: SpaceX can change the waveform at any time; any receiver built on these constants should check them against fresh captures.
- Our read: a 90 cm tracked dish is a lab setup. A hackathon receiver with a flat or fixed antenna will see lower SNR and frequent beam handovers.

## Code, weights, license
- The paper ships no code. The index links the companion UT Starlink signal simulator on GitLab (`radionavlab/public/ut-starlink-signal-simulator`): MIT license (LICENSE file and GitLab API), copyright 2023 Zacharias Komodromos; last activity 2024-01-16; README says "still a work in progress".
- Simulator contents: MATLAB `utils/` (`genPss.m`, `genSss.m` + `sssVec.mat`, `genStrlkFrame.m`, `genStrlkOFDM.m`, `genStrlkStream.m`, `genDopHist.m`, `fftAcqStrlk.m`, `getEphSpaceTrackZip.m`, `ofdmSnrEstimator.m`), live-script playgrounds (`.mlx`), and unit tests. Its own citation is Komodromos, Qin, Humphreys, ION GNSS+ 2023.
- No weights (not an ML paper).

## Reproduction effort (estimate)
Estimate:
- Simulation path: MATLAB licence needed (.mlx playgrounds need MATLAB, not Octave). Generate a Starlink frame, run `fftAcqStrlk` against simulated Doppler; a few hours.
- Real-signal path: dish or Ku antenna + LNB + SDR with tens of MHz bandwidth and a GPSDO; the paper's narrowband capture was 62.5 Msps (~60 MHz of a 240 MHz channel), and the PSS itself was recovered from the 4096 Msps wideband captures. A day or more of RF work before the first correlation peak.
- Not reproducible: the original captures, the blind identification pipeline code, CM1SS/CSS details.

## What a hackathon team can take from it
- Table II and the PSS/SSS definitions are what you need to build a Starlink correlator; you do not need to redo the blind identification.
- PSS correlation peaks give frame timing at 750 Hz; with TLE orbits this yields pseudorange-like and Doppler observables for a [Psiaki-style](psiaki-transit-on-steroids-2021.md) or [cold-start SDP](leo-doppler-cold-start-2025.md) solver.
- Use the UT simulator to generate test vectors and unit-test your acquisition before touching RF hardware.
- Since PSS/SSS are identical across satellites, satellite identity must come from Doppler vs TLE prediction and antenna pointing - plan that association step.
- Contrast with the tone-tracking approach in [kassas-starlink-navigation](kassas-starlink-navigation.md): tones are easier, sync sequences give more precise observables.
