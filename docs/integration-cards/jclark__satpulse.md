# SatPulse - integration card
<!-- about: repo:jclark/satpulse -->
Go daemon + tools that own a GNSS receiver's serial port and turn it into (a) a chrony/ntpd refclock, (b) a PHC-disciplining PTP grandmaster feeding `ptp4l`, (c) an Ntrip caster / client / server for RTK, and (d) a browser GUI (Workbench) to configure and monitor receivers from u-blox, Unicore, Septentrio, Quectel and others. Fastest way to get a cheap timing receiver into a GNSS-disciplined time + RTK base setup.

| | |
|---|---|
| Install | Linux packages from GitHub release v0.3 (2026-10-28): `satpulse_0.3_amd64.deb`, `_arm64.deb`, `_armhf.deb` (ARMv6, every Pi), `satpulse-0.3.x86_64.rpm`, `.aarch64.rpm`; install with `sudo dpkg -i satpulse_0.3_arm64.deb`. Windows: `satpulse_0.3_windows_amd64.zip` (no installer). macOS: Homebrew tap `jclark/homebrew-satpulse`. Source: Go toolchain (go.mod says `go 1.26.0`), `git clone https://github.com/jclark/satpulse.git && cd satpulse && make && sudo make install` on Linux (docs/setup/satpulse-install.md). |
| Runs on | Linux (full feature set: PHC, PTP, NTP SHM/SOCK, systemd), macOS (stratum 1 with chrony), Windows (mainly `satpulsewb.exe`; `satpulsed` runs only in a terminal, not as a service). amd64, arm64, 32-bit ARM. PHC/PTP needs a NIC or SoC with a PTP hardware clock and an SDP pin (Pi CM4/CM5, Intel NICs per README). |
| Inputs | GNSS receiver on a serial device (`-d /dev/ttyAMA0`, `[serial] speed`); PPS either on a PHC pin (`[phc] interface`, `pin`) or on a serial modem-control line (`[serial] pps.pin = "cts"|"dcd"|"dsr"|"ri"`, new in 0.3). Packet formats: NMEA, UBX, Unicore, SBF (Septentrio, new in 0.3), RTCM, SPARTN corrections from Ntrip/TCP. Fixed antenna position as `fixedPosECEF` (m) or `fixedPosLLH` (deg, deg, m). |
| Outputs | chrony SOCK samples (`[ntp] sock.path`), NTP SHM (`[ntp] shm.segment`), PHC discipline plus ptp4l metadata over its UDS (`[ptp] ptp4l.udsAddress`, `clockAccuracy`); RTCM via Ntrip caster (`[[ntrip.mountpoint]]`) or push (`[[stream.push]]`, also UDP); JSONL event / track / packet logs; Prometheus metrics and web dashboard (`[[http]] listen = ":2000"`); RINEX from SBF via `satpulsetool convobs`. |
| Key API / entry points | `satpulsed [-f satpulse.toml] [-d device] [-w] [-s]` (systemd template `satpulse@<tty>.service`, e.g. `sudo systemctl enable --now satpulse@ttyAMA0`); `satpulsetool gps` (configure receiver: `-g GPS,GAL`, `--survey --survey-time 3000 --survey-acc 1.5`, `-rtcm-out MSM4,ARP`, `--packet-log x.jsonl --capture 10`); `satpulsetool sdp`, `serial`, `syncsim`, `convobs`, `decode`, `scan`, `pack`, `annotate`; `satpulsewb` (Workbench, default port 15754). Config schema `configs/config-schema.json`, annotated sample `configs/satpulse.toml`. |
| Time to first result | Estimate: 15-30 min to see a u-blox receiver live in `satpulsewb`; 1-2 h for a chrony stratum 1 with serial PPS, assuming PPS is wired to a modem-control pin. |
| License | MIT (`LICENSE`, Copyright 2024 James Clark). No data or weights. |

## Minimal usage
Not run. From `docs/man/satpulsetool-gps.1.md`, `docs/man/satpulsewb.1.md`, `configs/satpulse.toml`, `configs/chrony.conf`.

```sh
# Look at the receiver in a browser (prints a tokenised URL)
satpulsewb -d /dev/ttyACM0 -s 9600

# Stratum 1 NTP: satpulsed => chrony over SOCK
sudo dpkg -i satpulse_0.3_arm64.deb
sudoedit /etc/satpulse.toml        # set [serial] speed, uncomment [ntp] sock.path = "/var/run/chrony.satpulse.sock"
echo 'refclock SOCK /var/run/chrony.satpulse.sock poll 2 filter 4 refid GNSS' | sudo tee -a /etc/chrony/chrony.conf
sudo systemctl restart chrony
sudo systemctl enable --now satpulse@ttyACM0.service
chronyc sources -v
```

Config file: `/etc/satpulse.toml` for a package install, `/usr/local/etc/satpulse.toml` for a source install (docs/setup/satpulsed.md). The unit also reads a per-device override `/etc/satpulse.d/<tty>.toml` (`configs/satpulse@.service`).

## Wiring it into a nav stack
- Time: => [chrony](./gitlab.com__chrony__chrony.md) (SOCK or SHM) and => [linuxptp](./nwtime__linuxptp.md) `ptp4l` grandmaster over its management socket. That gives sensor hosts one GNSS-disciplined timebase for LIO/VIO time sync.
- RTK: SatPulse as base (`rtcmOutput = true` + `[[ntrip.mountpoint]]`) => rover receivers or [RTKLIB](./rtklibexplorer__rtklib.md) `str2str`/`rtknavi` over Ntrip; or as rover (`[stream.pull]` from a caster).
- Logs: JSONL packet logs and `convobs` RINEX feed offline PPP/RTK in RTKLIB or [gnss_lib_py](./stanford-navlab__gnss_lib_py.md). The `[[stream.push]] udp.address` can mirror NMEA/UBX into [pygnssutils](./semuconsulting__pygnssutils.md) or a custom spoofing monitor.
- Monitoring: Prometheus metrics + correction reports for a ground-station dashboard.

## Gotchas
- Young project: 0.x versions, config keys keep growing each release (0.3 added `[ntrip]`, `[stream.pull]`, `[[stream.push]]`, `[ntp.shm]`, `pps.pin`); 128 open issues (2026-11), many receiver-specific (e.g. #526 signal config on AT372-F8P-36, #503 UBX NAV-SAT/NAV-SIG pairing).
- `satpulsewb` binds all interfaces by default, and the printed URL "grants control of the receiver until satpulsewb exits" (man page). Use `--listen 127.0.0.1:15754` on shared networks.
- GPS config written by `satpulsed` (`[gps] config = true`) is "not persistent across GPS reboots" (sample config comment); use `satpulsetool gps --save` for persistent changes where supported.
- Default assumes a stationary receiver; set `[gps] mobile = true` on a vehicle.
- Building from source needs a very recent Go (`go 1.26.0` in go.mod).
- PHC timing needs PPS physically on a PHC pin; serial `pps.pin` is the fallback for boards without a PHC and is less precise (NEWS 0.3).

## Alternatives
- [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) - the long-standing receiver daemon with chrony SOCK/SHM output and broad client support; prefer when other software already talks gpsd.
- [pygnssutils](./semuconsulting__pygnssutils.md) - Python receiver tooling and Ntrip client/caster, easier to script.
- [linuxptp](./nwtime__linuxptp.md) `ts2phc` - PPS + NMEA RMC => PHC without SatPulse, when you only need PTP timing.

Sources: `README.md`, `LICENSE`, `go.mod`, `docs/_includes/NEWS.md` (0.3), `docs/setup/satpulse-install.md`, `docs/setup/satpulsed.md`, `docs/man/satpulsed.8.md`, `docs/man/satpulsetool.1.md`, `docs/man/satpulsetool-gps.1.md`, `docs/man/satpulsewb.1.md`, `configs/satpulse.toml`, `configs/chrony.conf`, `configs/chrony.toml`, release v0.3 assets, open issues list (github.com/jclark/satpulse).
