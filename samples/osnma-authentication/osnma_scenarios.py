"""Run OSNMAlib on a real Galileo I/NAV recording, clean and with file-level spoofing manipulations.

Everything happens on recorded bits in memory. Nothing is generated as RF and nothing is transmitted.

Each scenario wraps OSNMAlib's SBF reader in a PageIterator that edits pages before the receiver sees
them. The receiver itself is unmodified OSNMAlib. Each scenario runs in its own process because
OSNMAlib keeps its configuration and status logger in module-level singletons.

Usage:
  python osnma_scenarios.py --osnmalib /path/to/OSNMA [--minutes 20] [--out results.json] [scenario ...]
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

# I/NAV page layout inside OSNMAlib's 240-bit DataFormat (even half + odd half, ICD 2.1 section 4.3.2).
WORD_TYPE = slice(2, 8)
OSNMA_FIELD = slice(138, 178)
MACK_PAGE_START = 146
MACK_BITS_PER_PAGE = 32
PAGES_PER_SUBFRAME = 15
PAGE_S = 2
SUBFRAME_S = 30
# Bit inside word type 2 that falls in OMEGA_0 (word data starts at page bit 8; IODnav 10 bits, then OMEGA_0).
FORGED_BIT = 8 + 10 + 5
# MACK layout for the MACLT in force in the bundled recording (MACLT 34: 6 tags of 40 bits, key 128 bits).
TAG_BITS = 40
TAG_SLOT_BITS = 56  # tag + 16-bit tag info (tag0 slot: tag0 + MACSEQ + COP)
TAGS_PER_MACK = 6
KEY_BITS = 128
KEY_START = TAG_SLOT_BITS * TAGS_PER_MACK

ADKD0_FRESH_S = 60  # nominal lag between subframe start and newest authenticated ADKD0 data is 30 s
ADKD12_FRESH_S = 360  # slow MAC: key disclosed ~10 subframes later

SCENARIOS = {
    "clean": "Recording as is, receiver trusts the signal's own time (OSNMAlib file default, TS = 30 s).",
    "replay_no_clock": "Same as clean, read as an attack: the recording is from 2025-12-12 and is replayed on a "
                       "later day. With no independent clock the receiver cannot tell.",
    "meacon_3s": "Replay / meaconing with 3 s delay, receiver has an independent clock (true time = page time + 3 s).",
    "replay_60s": "Replay delayed 60 s, independent clock. Exceeds the 30 s bound for ADKD0/ADKD4.",
    "replay_1h": "Replay of 1 h old signal, independent clock. Exceeds the 330 s bound for every ADKD.",
    "forge_nav": "From the first page, one ephemeris bit (OMEGA_0, word type 2) flipped on 3 SVs; OSNMA bits untouched "
                 "(spoofer present from cold start).",
    "forge_nav_late": "Same flip, but only from minute 10, after the genuine word was already authenticated "
                      "(same IOD).",
    "forge_keys": "From minute 10, all SVs: ephemeris bit flipped and every MACK tag and TESLA key replaced by random "
                  "bits (spoofer without the private chain).",
    "strip_osnma": "From minute 10 the 40 OSNMA bits are zeroed on every page (spoofer sends plain I/NAV).",
    "time_shift_120s": "From minute 10 every page is stamped 120 s earlier (spoofer pulls GST back 4 subframes).",
    "cold_start_merkle": "Clean recording, no public key given: the receiver must get it from a DSM-PKR in the "
                         "signal and verify it against the GSC Merkle root.",
}
FORGE_SVIDS = (19, 23, 27)
CLOCK_DELAYS = {"meacon_3s": 3, "replay_60s": 60, "replay_1h": 3600}  # true time minus signal time, s
ATTACK_START_S = 600


def _page_index(tow: int) -> int:
    return (tow % SUBFRAME_S) // PAGE_S


def _randomize_mack_bits(nav_bits, tow: int, rng: random.Random) -> None:
    """Overwrite tag and key bits of the MACK slice carried by this page."""
    first = _page_index(tow) * MACK_BITS_PER_PAGE
    for off in range(MACK_BITS_PER_PAGE):
        i = first + off
        in_tag = i < KEY_START and (i % TAG_SLOT_BITS) < TAG_BITS
        in_key = KEY_START <= i < KEY_START + KEY_BITS
        if in_tag or in_key:
            nav_bits[MACK_PAGE_START + off] = rng.getrandbits(1)


def make_iterator(scenario: str, sbf_path: str, minutes: float):
    from osnma.input_formats.base_classes import DataFormat, PageIterator
    from osnma.input_formats.input_sbf import SBF
    from osnma.cryptographic.gst_class import GST


    class ScenarioPages(PageIterator):
        def __init__(self):
            super().__init__()
            self.src = SBF(sbf_path)
            self.t0 = None
            self.rng = random.Random(7)
            self.delay = CLOCK_DELAYS.get(scenario)
            self.provides_independent_clock = self.delay is not None
            self.jumped = False

        def __next__(self) -> DataFormat:
            while True:
                p = next(self.src)
                t = p.gst_page.wn * 604800 + p.gst_page.tow
                if self.t0 is None:
                    self.t0 = t
                if t - self.t0 > minutes * 60:
                    raise StopIteration
                break
            attack = t - self.t0 >= ATTACK_START_S
            bits = p.nav_bits.copy()
            wn, tow = p.gst_page.wn, p.gst_page.tow
            forge_window = attack if scenario == "forge_nav_late" else True
            if scenario in ("forge_nav", "forge_nav_late") and forge_window and p.svid in FORGE_SVIDS and bits[WORD_TYPE].uint == 2:
                bits.invert(FORGED_BIT)
            elif scenario == "forge_keys" and attack:
                if bits[WORD_TYPE].uint == 2:
                    bits.invert(FORGED_BIT)
                if bits[OSNMA_FIELD].uint != 0:
                    _randomize_mack_bits(bits, tow, self.rng)
            elif scenario == "strip_osnma" and attack:
                bits.overwrite("0b" + "0" * 40, OSNMA_FIELD.start)
            elif scenario == "time_shift_120s" and attack:
                tow -= 120
            clock = GST(wn=wn, tow=tow + self.delay) if self.delay is not None else None
            return DataFormat(p.svid, wn, tow, bits, p.band, p.crc, independent_clock=clock)

    return ScenarioPages()


def summarize(status_log: list[dict], general_log: str) -> dict:
    timeline = []
    for e in status_log:
        sf = e["metadata"]["GST_subframe"]
        t = sf[0] * 604800 + sf[1]
        v = e.get("verified_OSNMA_material", {})
        auth = e.get("authenticated_nav_data", {})

        def fresh(adkd, lag):
            return sorted(int(s) for s, b in auth.get(adkd, {}).items()
                          if t - (b["last_gst"][0] * 604800 + b["last_gst"][1]) <= lag)

        timeline.append({
            "gst_sf": sf,
            "nmas": (e.get("OSNMA_status") or {}).get("nma_status", {}).get("nmas"),
            "osnma_svs": sorted(int(s) for s in e.get("OSNMA_material_received", {})),
            "nav_svs": sorted(int(s) for s in e.get("nav_data_received", {})),
            "tags_ok": sum(1 for x in v.get("tags", []) if x["verification"]),
            "tags_fail": sum(1 for x in v.get("tags", []) if not x["verification"]),
            "keys_ok": sum(1 for x in v.get("tesla_key", []) if x["verification"]),
            "keys_fail": sum(1 for x in v.get("tesla_key", []) if not x["verification"]),
            "adkd0_fresh": fresh("ADKD0", ADKD0_FRESH_S),
            "adkd12_fresh": fresh("ADKD12", ADKD12_FRESH_S),
        })
    counts = {
        "kroot_authenticated": len(re.findall(r"KROOT.*\n\tAUTHENTICATED", general_log)),
        "tesla_keys_authenticated": len(re.findall(r"Tesla key \d+ Authenticated", general_log)),
        "tesla_key_failures": len(re.findall(r"Failed authentication of TESLA key", general_log)),
        "tags_authenticated": len(re.findall(r"Tag AUTHENTICATED", general_log)),
        "tags_failed": len(re.findall(r"Tag FAILED", general_log)),
        "macseq_failed": len(re.findall(r"MACSEQ FAILED", general_log)),
        "data_authenticated": len(re.findall(r"AUTHENTICATED: ADKD", general_log)),
        "time_backwards": len(re.findall(r"Time is going backwards", general_log)),
        "pkr_verified": len(re.findall(r"PKR with NPKID \d+ verified", general_log)),
        "errors": len(re.findall(r"\| ERROR", general_log)),
    }
    t0 = timeline[0]["gst_sf"][0] * 604800 + timeline[0]["gst_sf"][1] if timeline else 0
    first = next((x for x in timeline if x["adkd0_fresh"] or x["adkd12_fresh"]), None)
    counts["first_auth_s"] = None if first is None else first["gst_sf"][0] * 604800 + first["gst_sf"][1] - t0
    return {"counts": counts, "timeline": timeline}


def words_differ_from_stream(rx) -> list[int]:
    """SVs whose latest ADKD0 words (as a PVT engine would read them) differ from the frozen stream OSNMAlib
    authenticates tags against. OSNMAlib computes that stream once, when the block first completes."""
    out = []
    for svid, mgr in rx.receiver_state.nav_data_structure.adkd0_data_managers.items():
        blocks = [b for b in mgr.adkd0_data_blocks if b.gst_completed]
        if not blocks:
            continue
        b = blocks[-1]
        latest = sum((b.words[i] for i in range(1, 6)), start=type(b.nav_data_stream)())
        if latest != b.nav_data_stream:
            out.append(int(svid))
    return sorted(out)


def run_one(scenario: str, osnmalib: Path, sbf: Path, pubkey: str, minutes: float) -> dict:
    """In-process run. Call through run_isolated() when running several scenarios."""
    sys.path.insert(0, str(osnmalib))
    from osnma.receiver.receiver import OSNMAReceiver

    work = Path(tempfile.mkdtemp(prefix=f"osnma_{scenario}_"))
    src_dir = sbf.parent
    if scenario == "cold_start_merkle":
        pubkey = ""
    for name in ("OSNMA_MerkleTree.xml", pubkey):
        if name:
            shutil.copy(src_dir / name, work / name)
    cfg = {
        "exec_path": str(work), "logs_path": str(work),
        "merkle_name": "OSNMA_MerkleTree.xml", "pubk_name": pubkey, "kroot_name": "",
        "TS": 30, "do_reed_solomon_recovery": False, "log_console": False,
    }
    rx = OSNMAReceiver(make_iterator(scenario, str(sbf), minutes), cfg)
    rx.start()
    logdir = next(work.glob("logs_*"))
    status = json.loads((logdir / "status_log.json").read_text())
    general = (logdir / "general_logs.log").read_text()
    shutil.rmtree(work, ignore_errors=True)
    out = summarize(status, general)
    out["counts"]["words_differ_from_authenticated_stream"] = words_differ_from_stream(rx)
    out["scenario"] = scenario
    out["independent_clock_offset_s"] = CLOCK_DELAYS.get(scenario)
    out["description"] = SCENARIOS[scenario]
    return out


def run_isolated(scenario: str, osnmalib: Path, sbf: Path, pubkey: str, minutes: float) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out_path = f.name
    cmd = [sys.executable, "-I", str(Path(__file__)), "--osnmalib", str(osnmalib), "--sbf", str(sbf),
           "--pubkey", pubkey, "--minutes", str(minutes), "--single", scenario, "--out", out_path]
    subprocess.run(cmd, check=True, cwd=str(HERE))
    res = json.loads(Path(out_path).read_text())
    os.unlink(out_path)
    return res


def _t(x) -> int:
    return x["gst_sf"][0] * 604800 + x["gst_sf"][1]


def table(results: list[dict]) -> str:
    rows = ["| scenario | first auth [s] | KROOT ok | keys ok / fail | tags ok / fail | ADKD0-auth SVs at min 9.5 / at end "
            "| ADKD12-auth SVs at end | pages rejected (time backwards) |",
            "|---|---|---|---|---|---|---|---|"]
    for r in results:
        c, tl = r["counts"], r["timeline"]
        if not tl:
            rows.append(f"| {r['scenario']} | no status log entries |")
            continue
        t0 = _t(tl[0])
        before = [x for x in tl if _t(x) - t0 < ATTACK_START_S]
        b = before[-1]["adkd0_fresh"] if before else []
        first = "none" if c["first_auth_s"] is None else c["first_auth_s"]
        rows.append(f"| {r['scenario']} | {first} | {c['kroot_authenticated']} | {c['tesla_keys_authenticated']} / "
                    f"{c['tesla_key_failures']} | {c['tags_authenticated']} / {c['tags_failed']} | "
                    f"{len(b)} / {len(tl[-1]['adkd0_fresh'])} | {len(tl[-1]['adkd12_fresh'])} | {c['time_backwards']} |")
    return "\n".join(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--osnmalib", required=True, type=Path, help="OSNMAlib checkout (github.com/Algafix/OSNMA)")
    ap.add_argument("--sbf", type=Path, help="SBF file with GALRawINAV; default: <osnmalib>/custom_run/current_config.sbf")
    ap.add_argument("--pubkey", default="OSNMA_PublicKey_2.xml")
    ap.add_argument("--minutes", type=float, default=20.0)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--single", help=argparse.SUPPRESS)
    ap.add_argument("scenarios", nargs="*", default=list(SCENARIOS))
    a = ap.parse_args(argv)
    osnmalib = a.osnmalib.resolve()
    sbf = (a.sbf or osnmalib / "custom_run" / "current_config.sbf").resolve()
    if a.single:
        res = run_one(a.single, osnmalib, sbf, a.pubkey, a.minutes)
        a.out.write_text(json.dumps(res))
        return
    results = []
    for s in a.scenarios:
        print(f"running {s} ...", file=sys.stderr)
        results.append(run_isolated(s, osnmalib, sbf, a.pubkey, a.minutes))
    print(table(results))
    if a.out:
        a.out.write_text(json.dumps(results, separators=(",", ":")))


if __name__ == "__main__":
    main()
