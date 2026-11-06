"""Feed live u-blox UBX telemetry into the heuristic scorer. Requires pyubx2 (and pyserial for a port).

Replay mode verified with pyubx2 1.4.1 on the synthetic capture from gen_synthetic_ubx.py.
Live-port mode (--port, --enable) is not verified: no receiver was attached.

Usage:
  python3 ubx_monitor.py --port /dev/ttyACM0 --baud 38400 --enable   # live receiver (M8/M9/M10/F9)
  python3 ubx_monitor.py --file capture.ubx                          # replay a recording
  python3 ubx_monitor.py --file fixtures/synthetic.ubx --changes-only
"""

from __future__ import annotations

import argparse

from pyubx2 import SET_LAYER_RAM, TXN_NONE, UBX_PROTOCOL, UBXMessage, UBXReader

from scorer import Epoch, InterferenceScorer

MSGOUT_KEYS = [  # CFG-VALSET keys, generation 9+ receivers (F9/M9/M10); M8 needs CFG-MSG instead
    "CFG_MSGOUT_UBX_NAV_PVT_USB",
    "CFG_MSGOUT_UBX_NAV_SAT_USB",
    "CFG_MSGOUT_UBX_NAV_STATUS_USB",
    "CFG_MSGOUT_UBX_NAV_CLOCK_USB",
    "CFG_MSGOUT_UBX_MON_RF_USB",
    "CFG_MSGOUT_UBX_SEC_SIG_USB",  # only on firmware that has UBX-SEC-SIG
]
GNSS_LETTER = {0: "G", 1: "S", 2: "E", 3: "C", 5: "J", 6: "R", 7: "I"}
MS_PER_S = 1000.0


def enable_messages(stream):
    msg = UBXMessage.config_set(SET_LAYER_RAM, TXN_NONE, [(k, 1) for k in MSGOUT_KEYS])
    stream.write(msg.serialize())


def fill(ep: Epoch, msg) -> None:
    """Copy the fields we use from one parsed UBX message into the current epoch."""
    ident = msg.identity
    if ident == "NAV-PVT":
        if msg.fixType >= 2:
            ep.lat, ep.lon = msg.lat, msg.lon  # pyubx2 applies the 1e-7 scaling
    elif ident == "NAV-SAT":
        for i in range(1, msg.numSvs + 1):
            cno = getattr(msg, f"cno_{i:02d}")
            if cno > 0:
                sv = f"{GNSS_LETTER.get(getattr(msg, f'gnssId_{i:02d}'), '?')}{getattr(msg, f'svId_{i:02d}'):02d}"
                ep.cn0[sv] = float(cno)
    elif ident == "NAV-STATUS":
        ep.spoof_det_state = msg.spoofDetState
    elif ident == "NAV-CLOCK":
        ep.clk_bias_ns, ep.clk_drift_ns_s = float(msg.clkB), float(msg.clkD)
    elif ident == "MON-RF":
        # block 1 = first RF path (L1 on dual-band receivers)
        ep.agc_cnt = float(msg.agcCnt_01)
        ep.jam_ind = float(msg.jamInd_01)
        ep.jamming_state = getattr(msg, "jammingState_01", None)  # absent in MON-RF-V0
    elif ident == "SEC-SIG":
        # V1 and V2 both expose jammingState / spoofingState as flat bit-field attributes
        ep.jamming_state = max(ep.jamming_state or 0, msg.jammingState)
        ep.spoof_det_state = max(ep.spoof_det_state or 0, msg.spoofingState)


def run(stream, changes_only=False):
    scorer = InterferenceScorer()
    reader = UBXReader(stream, protfilter=UBX_PROTOCOL)
    counts: dict[str, int] = {}
    last_verdict = None

    def emit(ep):
        nonlocal last_verdict
        a = scorer.assess(ep)
        counts[a.verdict] = counts.get(a.verdict, 0) + 1
        if not changes_only or a.verdict != last_verdict:
            print(f"t={ep.t:10.1f} {a.verdict:<17} jam={a.jam_score:.2f} "
                  f"spoof={a.spoof_score:.2f} {'; '.join(a.reasons)}")
        last_verdict = a.verdict

    current_tow = None
    ep = None
    for _raw, msg in reader:
        if msg is None or not hasattr(msg, "identity"):
            continue
        # NAV-* messages of one epoch share iTOW; MON-RF / SEC-SIG carry none and are
        # attributed to the epoch whose NAV messages preceded them.
        tow = getattr(msg, "iTOW", None)
        if tow is not None and tow != current_tow:
            if ep is not None:
                emit(ep)
            current_tow = tow
            ep = Epoch(t=tow / MS_PER_S)
        if ep is not None:
            fill(ep, msg)
    if ep is not None:
        emit(ep)
    print("epochs per verdict: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--port")
    src.add_argument("--file")
    ap.add_argument("--baud", type=int, default=38400)
    ap.add_argument("--enable", action="store_true", help="send CFG-VALSET to enable messages")
    ap.add_argument("--changes-only", action="store_true", help="print only verdict changes")
    args = ap.parse_args()
    if args.file:
        with open(args.file, "rb") as fh:
            run(fh, args.changes_only)
        return
    from serial import Serial  # pyserial

    with Serial(args.port, args.baud, timeout=3) as stream:
        if args.enable:
            enable_messages(stream)
        run(stream, args.changes_only)


if __name__ == "__main__":
    main()
