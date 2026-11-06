"""Mix gps-sdr-sim 16-bit IQ streams into one 8-bit IQ file for GNSS-SDR (file only, never RF).

authentic + thermal noise, optionally + a spoofer stream (power offset, sample delay, on-time)
and + a broadband noise burst (jamming). gps-sdr-sim output is noise-free and a satellite with
fixed gain 128 (-p) has complex amplitude 250 in 16-bit output (cosTable512 peak 250, gain/128),
so noise is set from that reference: N0 = 250^2 / 10^(cn0_ref/10).

Inputs may be files or FIFOs fed by `gps-sdr-sim -o -`, so the 16-bit streams never hit disk.
Writes a per-second in-band power log (CSV) as a stand-in for a receiver AGC indicator.
"""
import argparse
import math
import sys

import numpy as np

REF_AMPLITUDE = 250.0
RAMP_START_DB = -20.0
OUT_NOISE_STD_LSB = 12.0  # int8 headroom: thermal noise std per I/Q component after scaling


def read_block(f, n):
    """Read n complex int16 samples; works on pipes (gps-sdr-sim -o -), zero-pads at EOF."""
    buf = bytearray(4 * n)
    view, got = memoryview(buf), 0
    while got < len(buf):
        k = f.readinto(view[got:])
        if not k:
            break
        got += k
    raw = np.frombuffer(buf, dtype=np.int16)
    return raw[0::2].astype(np.float32) + 1j * raw[1::2].astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--authentic", required=True)
    ap.add_argument("--spoofer")
    ap.add_argument("--fs", type=float, required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--cn0-ref", type=float, default=47.0, help="dB-Hz of a 0 dB-gain satellite")
    ap.add_argument("--spoof-on", type=float, default=0.0, help="s")
    ap.add_argument("--spoof-gain-db", type=float, default=0.0, help="spoofer power vs its 16-bit level")
    ap.add_argument("--spoof-ramp-s", type=float, default=0.0,
                    help="ramp spoofer power from -20 dB to --spoof-gain-db over this many seconds")
    ap.add_argument("--spoof-delay-samples", type=int, default=0)
    ap.add_argument("--jam-on", type=float)
    ap.add_argument("--jam-off", type=float)
    ap.add_argument("--jam-jn-db", type=float, default=25.0, help="jammer power over thermal noise")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--power-log", required=True)
    a = ap.parse_args()

    fs = int(a.fs)
    n0 = REF_AMPLITUDE ** 2 / 10 ** (a.cn0_ref / 10.0)  # noise PSD, power per Hz
    sigma = math.sqrt(n0 * fs / 2.0)  # per-component std of thermal noise
    scale = OUT_NOISE_STD_LSB / sigma
    jam_sigma = sigma * 10 ** (a.jam_jn_db / 20.0)
    rng = np.random.default_rng(a.seed)

    fa = open(a.authentic, "rb")
    fsp = open(a.spoofer, "rb") if a.spoofer else None
    spoof_buf = np.zeros(a.spoof_delay_samples, dtype=np.complex64)
    clipped = 0
    with open(a.out, "wb") as fo, open(a.power_log, "w") as pl:
        pl.write("t_s,power_lsb2,clip_fraction\n")
        for sec in range(int(a.duration)):
            x = read_block(fa, fs)
            if fsp is not None:
                s = np.concatenate([spoof_buf, read_block(fsp, fs)])
                spoof_buf, s = s[fs:], s[:fs]
                if sec >= a.spoof_on:
                    gain_db = a.spoof_gain_db
                    if sec < a.spoof_on + a.spoof_ramp_s:
                        frac = (sec - a.spoof_on) / a.spoof_ramp_s
                        gain_db = RAMP_START_DB + frac * (a.spoof_gain_db - RAMP_START_DB)
                    x = x + 10 ** (gain_db / 20.0) * s
            x = x + sigma * (rng.standard_normal(fs) + 1j * rng.standard_normal(fs))
            if a.jam_on is not None and a.jam_on <= sec < a.jam_off:
                x = x + jam_sigma * (rng.standard_normal(fs) + 1j * rng.standard_normal(fs))
            x *= scale
            iq = np.empty(2 * fs, dtype=np.float32)
            iq[0::2], iq[1::2] = x.real, x.imag
            c = np.count_nonzero(np.abs(iq) > 127)
            clipped += c
            np.clip(np.rint(iq), -127, 127).astype(np.int8).tofile(fo)
            pl.write(f"{sec},{float(np.mean(iq.astype(np.float64) ** 2)):.2f},{c / iq.size:.5f}\n")
    print(f"wrote {a.out}: {int(a.duration)} s at {fs} sps, noise sigma {sigma:.1f} (16-bit units), "
          f"clipped {clipped} samples", file=sys.stderr)


if __name__ == "__main__":
    main()
