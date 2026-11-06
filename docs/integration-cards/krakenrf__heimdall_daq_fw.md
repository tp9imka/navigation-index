# Heimdall DAQ firmware - integration card
<!-- about: repo:krakenrf/heimdall_daq_fw -->
One-line: the C/Python acquisition chain that turns the 5 RTL-SDR tuners of a KrakenSDR (or 4-channel KerberosSDR) into sample- and phase-coherent IQ frames, served over shared memory or TCP; the layer under [KrakenSDR DoA](./krakenrf__krakensdr_doa.md), and the entry point if you want raw coherent IQ for your own DF or interference-localisation code.

| | |
|---|---|
| Install | Easiest: KrakenSDR Pi 4/5 / Orange Pi 5B images or install scripts (links in README, krakensdr_docs wiki). Manual (README): `apt install build-essential git cmake libusb-1.0-0-dev lsof libzmq3-dev`; build `krakenrf/librtlsdr` (blacklist `dvb_usb_rtl28xxu`, reboot); ARM: build `krakenrf/Ne10`; x86_64: build `krakenrf/kfr` with clang and copy libs/headers; Miniforge, `conda create -n kraken python=3.9.7`, `scipy==1.9.3`, `numba==0.56.4`, `configparser`, `pyzmq`, `scikit-rf`; clone into `~/krakensdr/heimdall_daq_fw`, copy `librtlsdr.a` and headers (and `libNE10.a` on ARM) into `Firmware/_daq_core`, `make`. No GitHub releases; tags `v3.0.0-a.1`, `v3.1.0-a.1`. |
| Runs on | 64-bit Linux, aarch64 or x86_64 (conda requirement). Tested on Raspberry Pi 4; README suggests at least 4 CPU cores on other systems. Needs root (real-time `chrt -f 99`, usbfs and sysctl tweaks). No GPU. |
| Inputs | KrakenSDR / KerberosSDR over USB via the KrakenRF librtlsdr fork. Config `Firmware/daq_chain_config.ini` (templates in `config_files/kraken_default`, `kerberos_default`, `kraken_development`, `unit_test_k4`): `[hw] num_ch=5`, `[daq] center_freq=700000000`, `sample_rate=2400000`, `daq_buffer_size=262144`, `gain`, `en_noise_source_ctr`; `[pre_processing] cpi_size=1048576`, `decimation_ratio`, FIR settings; `[calibration]` tolerances and tracking mode; `[data_interface] out_data_iface_type = shmem` or `eth`. Optional `Firmware/_calibration/cable_ch*.s1p`. Runtime tuning via the hardware-controller port. |
| Outputs | Coherent multichannel IQ frames: 1024-byte header (`iq_header.py`: sync word `0x2bf7b95a`, `frame_type` (0 data, 3 calibration per the synthesizer), `hardware_id`, `active_ant_chs`, `rf_center_freq`, `sampling_freq`, `cpi_length`, `time_stamp`, `daq_block_index`, `data_type`, `sample_bit_depth`, `adc_overdrive_flags`, `if_gains[32]`, `delay_sync_flag`, `iq_sync_flag`, `sync_state`, `noise_source_state`) + samples. `shmem`: shared-memory buffers named `delay_sync_iq` with control FIFOs in `Firmware/_data_control/`. `eth`: `iq_server.out` on TCP 5000, hardware controller on TCP 5001. Logs in `Firmware/_logs/`. |
| Key API / entry points | `Firmware/daq_start_sm.sh` (run from `Firmware/`, scripts use relative paths) starts `rtl_daq.out | rebuffer.out`, `decimate.out`, `delay_sync.py`, `hw_controller.py`, and `iq_server.out` when `eth`; `Firmware/daq_stop.sh`; `Firmware/daq_synthetic_start.sh` (no-hardware path, see Gotchas); `Firmware/unit_test.sh` (+ `_testing/unit_test/test_*.py`); Python helpers `_daq_core/iq_header.py` `IQHeader` (`decode_header`, `encode_header`), `_daq_core/shmemIface.py` `inShmemIface`, `_testing/iq_recorder.py`, `_testing/iq_analyzer.py`, `util/cfg_gen.py`, `Firmware/ini_checker.py`. Internal control: `hw_controller.py` talks to `rtl_daq` over ZMQ REQ `tcp://localhost:1130`. |
| Time to first result | Estimate: 30-60 min with a prebuilt KrakenSDR image (Heimdall starts with the DoA app). 2-4 h for a manual build on a fresh Pi or x86 box, mostly librtlsdr/Ne10 or KFR and conda. Without hardware: unknown, the synthetic path looks broken (see Gotchas). Assumes a KrakenSDR with antennas and a Linux host you can run as root. |
| License | GPL-3.0. |

## Minimal usage
Shared-memory mode as used by KrakenSDR DoA, from README and the start scripts. Not run.

```bash
cd ~/krakensdr/heimdall_daq_fw/Firmware
cp ../config_files/kraken_default/daq_chain_config.ini .
# edit center_freq / sample_rate / gain; set out_data_iface_type = eth to serve IQ on TCP 5000 instead
sudo ./daq_start_sm.sh
tail -f _logs/delay_sync.log   # wait for sample and IQ sync before trusting frames
sudo ./daq_stop.sh
```
To consume in `eth` mode from your own code: connect TCP to `<host>:5000`, read the 1024-byte header with `IQHeader().decode_header(...)`, then `cpi_length` x `active_ant_chs` complex samples per `data_type`/`sample_bit_depth`; mirror `krakensdr_doa`'s `_sdr/_receiver/kraken_sdr_receiver.py` `receive_iq_frame()` rather than guessing the handshake.

## Wiring it into a nav stack
- Standard path: Heimdall (`shmem`) => [KrakenSDR DoA](./krakenrf__krakensdr_doa.md). The DoA receiver hard-codes the DAQ location as a sibling folder: `<parent of krakensdr_doa>/heimdall_daq_fw/Firmware/_data_control/` and shmem name `delay_sync_iq`; keep both repos side by side in `~/krakensdr/`. `kraken_doa_start.sh` launches `daq_start_sm.sh` for you.
- Split deployment: `out_data_iface_type = eth` lets the DAQ run on the Pi at the antenna and DSP run elsewhere over Ethernet (TCP 5000 data, 5001 control), which is how the DoA app's remote mode connects.
- Your own algorithm: take coherent frames over TCP into NumPy and run your DF, TDOA or interference-localisation code, then push bearings/fixes via [PyTAK](./snstac__pytak.md) and track them in [Stone Soup](./dstl__stone-soup.md). Keep it receive-only.
- Catalog: [Heimdall DAQ page](../../catalog/repos/krakenrf__heimdall_daq_fw.md).

## Gotchas
- Synthetic / no-hardware mode exists on paper but looks stale: `daq_synthetic_start.sh` pipes `_testing/test_data_synthesizer.py` into the chain, but the synthesizer opens `_data_control/rec_control_fifo`, which no start script creates (closed #16 reports exactly this `FileNotFoundError`; maintainer says synthetic start is for development only). The synthesizer was last changed in 2021-10, while `hw_controller.py` now controls `rtl_daq` over ZMQ `tcp://localhost:1130`, which the synthesizer does not serve. It also imports `pyargus` and by default emits signal power `ps = -200` dB with all test cases off (noise only), so you would edit the script to inject a direction. Inference from source, not run.
- README says `cd ~/krakensdr/heimdall_daq_fw && sudo ./daq_start_sm.sh`, but the scripts live in `Firmware/` and use relative paths; run them from there.
- `daq_start_sm.sh` bypasses the INI checker, sets `kernel.sched_rt_runtime_us=-1`, zeroes `usbfs_memory_mb`, drops caches and loops calling `daq_stop.sh` until ports 5000/5001 are free. Do not run it on a shared laptop casually.
- Dependency pins (`python=3.9.7`, `numba==0.56.4`, `scipy==1.9.3`) are old; conda through `sudo` loses the env (closed #12). Open #34: KFR build errors on x86.
- Phase coherence relies on the built-in noise source calibration; open #32 reports phase difference varying with frequency. Re-check calibration after retuning far from the calibrated frequency.
- Only 64-bit OS with conda; the KerberosSDR switch board needs `PIGPIO` enabled in the Makefile.
- GPL-3.0: linking your DSP into these binaries makes it GPL; talking to them over TCP/shared memory is the usual way to keep your code separate (check with counsel).

## Alternatives
- [KrakenSDR DoA](./krakenrf__krakensdr_doa.md) if you only want bearings; it wraps Heimdall and gives CSV/XML/JSON outputs.
- [KiwiSDR](../../catalog/repos/jks-prv__kiwisdr.md) for single-channel wideband HF reception from networked receivers; no coherent multichannel IQ.
- [GNSS-SDR](./gnss-sdr__gnss-sdr.md) for GNSS-band signal processing (a separate receiver per antenna, not a coherent array).

Sources: `README.md`, repo tree, `Firmware/daq_start_sm.sh`, `Firmware/daq_synthetic_start.sh`, `Firmware/_testing/test_data_synthesizer.py`, `Firmware/_daq_core/Makefile`, `Firmware/_daq_core/iq_header.py`, `Firmware/_daq_core/hw_controller.py`, `Firmware/_daq_core/rtl_daq.c` (control FIFO define), `config_files/kraken_default/daq_chain_config.ini`, `krakenrf/krakensdr_doa` `_sdr/_receiver/kraken_sdr_receiver.py` (ports, shmem path), commit history of the synthesizer, repo metadata and tags API, issue search (#12, #16, #32, #34).
