# OSNMAlib - integration card
<!-- about: repo:algafix/osnma -->
Python implementation of Galileo OSNMA (navigation message authentication): feed it Galileo I/NAV pages from a u-blox, Septentrio, GNSS-SDR or galmon stream and it tells you, per satellite and subframe, whether the ephemeris and clock data are cryptographically authentic. Basis for an "authenticated position" or anti-spoofing demo.

| | |
|---|---|
| Install | No PyPI package. `git clone https://github.com/Algafix/OSNMA && cd OSNMA && pip install -r requirements.txt` (bitstring<5, ecdsa, pycryptodome, protobuf, pyserial, reedsolo, ntplib, pandas, pytest...). Runner scripts add `..` to `sys.path`, so run them from their own folder. |
| Runs on | Python 3.10-3.12 per README; tested on Linux and Windows. No GPU. |
| Inputs | Galileo E1-B I/NAV pages with transmission WN/TOW: Septentrio SBF (`GALRawINAV`, file or IP port), u-blox UBX `RXM-SFRBX` (file, serial, socket; NAV-TIME* / TIM-TP used for time), GNSS-SDR over UDP, galmon live feed, Android GnssLogger files (post-process). Plus GSC-issued `OSNMA_MerkleTree.xml` and public key XML (shipped in the run folders). |
| Outputs | Verbose log and per-subframe JSON status log (schema in `osnma/utils/json_schema/status_log_schema.json`), saved KROOT / public key, TTFAF and TTFF figures. |
| Key API / entry points | `osnma.receiver.receiver.OSNMAReceiver(input_module, param_dict)`; `.start(start_at_gst=None)`; input iterators in `osnma/input_formats/`: `SBF(path)`, `UBX(path)`, `UBXLiveSerial(port)`, `UBXLiveSocket(host, port)`, plus galmon and GNSS-SDR modules. Config keys: `exec_path`, `merkle_name`, `pubk_name`, `kroot_name`, `TS`, `do_reed_solomon_recovery`, `do_dual_frequency`, `stop_at_faf`. Runners: `custom_run/run.py`, `ublox_run/run_file.py`, `ublox_run/run_serial.py`, `live_galmon_run/run.py`. |
| Time to first result | Estimate: 15 min to run `custom_run/run.py` on the bundled SBF recording; assumes Python 3.10-3.12 and pip access. Live u-blox adds receiver config time. |
| License | EUPL-1.2 (copyleft, compatible with GPL; check before embedding in closed code). |

## Minimal usage
Not run with a live receiver. From README and `ublox_run/run_serial.py` (file-mode runs on a recording are in Verified in this hub):

```sh
git clone https://github.com/Algafix/OSNMA && cd OSNMA
pip install -r requirements.txt
cd custom_run && python run.py            # bundled current_config.sbf, huge console output
cd ../ublox_run && python run_file.py     # bundled current_config.ubx
```

Live u-blox (edit the hard-coded port first):

```python
import sys; sys.path.insert(0, '..')
from osnma.receiver.receiver import OSNMAReceiver
from osnma.input_formats.input_ubx import UBXLiveSerial

cfg = {'exec_path': '.', 'pubk_name': 'OSNMA_PublicKey_2.xml',
       'merkle_name': 'OSNMA_MerkleTree.xml'}
OSNMAReceiver(UBXLiveSerial("/dev/ttyACM0"), cfg).start()
```

## Wiring it into a nav stack
- Receiver side: enable `RXM-SFRBX` (and Galileo E1) with [pyubx2](./semuconsulting__pyubx2.md) `config_set`, or record it with [pygnssutils](./semuconsulting__pygnssutils.md) `gnssstreamer`.
- Consume the JSON status log as a trust signal: only satellites with authenticated ADKD0/ADKD12 data feed your PVT, or raise an alarm when authentication drops while C/N0 stays high (a spoofing cue). Combine with the receiver-flag heuristics in [samples/gnss-interference-monitor](../../samples/gnss-interference-monitor/).
- SDR route: [GNSS-SDR](./gnss-sdr__gnss-sdr.md) can stream I/NAV pages over UDP into OSNMAlib (GNSS-SDR now also has OSNMA built in). For a fully synthetic test, the index lists [osnma-sdr-sim](../../catalog/repos/haiyang-wong__osnma-sdr-sim.md); keep generated signals in files or cabled setups.
- Authenticated position is still only as good as the time sync: OSNMA security assumes the receiver knows GST within `TS` (default 30 s); in live mode OSNMAlib can use NTP or the local clock.

## Gotchas
- Public key changed from ID 1 to ID 2 on 2025-12-10 10:00 UTC; data recorded before that needs `OSNMA_PublicKey_1.xml` (both keys ship in `custom_run/`, `ublox_run/`, `gnss_sdr_run/`; the live galmon and Septentrio runners ship only key 2). Data before 2023-08-03 needs the `OSNMA_Test_Phase_ICD` branch.
- `run_serial.py` hard-codes `"COM4"` and `UBXLiveSerial` hard-codes 115200 baud; change both for Linux/macOS or a receiver at 38400.
- u-blox SFRBX v1 has no signal id; the code assumes Galileo E1 (comment in `input_ubx.py`). Dual-frequency E5b optimisation needs an input that delivers E5b-I pages.
- Not packaged: no `pip install osnma`, imports rely on `sys.path.insert(0, '..')`.
- Merkle tree and public key must come from the GSC (gsc-europa.eu); a bundled copy can go stale after a key or tree renewal event.
- README research notice: do not reuse unpublished optimisation ideas without citing the papers.

## Verified in this hub
Measured by hub samples that ran this code on 2026-11-06, unless a bullet says otherwise. The linked sample README holds the commands and raw output.

- **Ran** unmodified OSNMAlib (commit 25aa61de, Python 3.12) on its bundled 76 min Septentrio recording: 56 KROOT, 962 TESLA keys, 4711 tags authenticated, 0 failures; first ADKD0 authentication 90 s after the first page (warm start). 20 min x 11 scenarios ~8 s wall on an M-series Mac. Runs one scenario per process (config and status logger are module singletons) - [osnma-authentication](../../samples/osnma-authentication/README.md).
- **Same-IOD forgery stays authenticated**: an ADKD0 block's authenticated bit stream is computed once (`ADKD0DataBlock.add_word` / `_compute_data_stream`); later words with the same IOD overwrite `words` but not that stream. Forged OMEGA_0 on E23 stayed "authenticated" for 10 min until an IOD change. Navigate on the authenticated copy, or compare decoded words against it - [osnma-authentication](../../samples/osnma-authentication/README.md).
- **File mode trusts the signal's GST**: an 11-month-old recording authenticated perfectly with no independent clock. With an independent clock: 3 s delay still authenticates; 60 s leaves only ADKD12; 1 h gives silence, not failures (`_filter_tag_by_TL`) - [osnma-authentication](../../samples/osnma-authentication/README.md).
- **Cold start**: with only the Merkle root no DSM-PKR appeared in 76 min, so no key and no authentication. Stripping OSNMA bits produces no failure, only absence - [osnma-authentication](../../samples/osnma-authentication/README.md).

## Alternatives
- [daniestevez/galileo-osnma](../../catalog/repos/daniestevez__galileo-osnma.md) - Rust, no_std, suited to embedded receivers.
- [nlsfi/fgi-osnma](../../catalog/repos/nlsfi__fgi-osnma.md) - another open implementation for cross-checking results.
- [axelbjork/osnma_ublox](../../catalog/repos/axelbjork__osnma_ublox.md) - u-blox focused alternative; GNSS-SDR's built-in OSNMA if you already run the SDR receiver.

Sources: `gh api repos/Algafix/OSNMA/readme`, `custom_run/run.py`, `ublox_run/run_serial.py`, `osnma/input_formats/input_ubx.py`, `osnma/receiver/receiver.py`, `requirements.txt`, issues (#16, #24, #57).
