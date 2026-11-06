# linuxptp - integration card
<!-- about: repo:nwtime/linuxptp -->
The standard Linux IEEE 1588 PTP stack: `ptp4l` (OC/BC/TC, gPTP, telecom profiles), `phc2sys` (PHC <=> system clock), `ts2phc` (GNSS 1PPS + NMEA => NIC hardware clock) and `pmc` (management). Use it to put every sensor computer on a vehicle onto one GNSS-disciplined timebase, or to keep sensor timestamps coherent when GNSS is lost.

| | |
|---|---|
| Install | Distro: `sudo apt install linuxptp` (Debian/Ubuntu package name). Source: `git clone https://github.com/nwtime/linuxptp && cd linuxptp && make && sudo make install` (installs to `/usr/local/sbin`; override `prefix`, `sbindir`, `mandir`, `man8dir`). Latest tag v4.4 (commit dated 2024-09-07); master still active (2026-08). README still points at SourceForge for downloads and patches go to `linuxptp-devel@lists.nwtime.org`, not GitHub PRs. |
| Runs on | Linux only, kernel 3.0+ (README). Hardware timestamping needs a NIC/MAC with a PHC (check `ethtool -T eth0`); software timestamping works anywhere with `ptp4l -S` or `time_stamping software`. Raspberry Pi CM4/CM5 and Intel i210/i225 class NICs have PHCs with SDP pins for PPS input. |
| Inputs | Network PTP messages (UDPv4, UDPv6, L2 Ethernet). `ts2phc`: 1PPS on a PHC pin (`ts2phc.pin_index`, `ts2phc.channel`, `ts2phc.extts_polarity`) plus time of day from NMEA RMC over serial (`ts2phc.nmea_serialport`, `ts2phc.nmea_baudrate`) or TCP (`ts2phc.nmea_remote_host/port`), or `generic` (PPS without ToD). |
| Outputs | Disciplined PHC (`/dev/ptpN`) and/or `CLOCK_REALTIME`; PTP grandmaster/slave messages on the wire; logs of offset/frequency/path delay to stdout or syslog. `phc2sys -E ntpshm` or `-E refclock_sock` hands samples to chrony or ntpd instead of steering the clock itself. |
| Key API / entry points | Binaries from `makefile` `PRG`: `ptp4l`, `phc2sys`, `ts2phc`, `pmc`, `phc_ctl`, `hwstamp_ctl`, `timemaster`, `nsm`, `tz2alt`. Typical: `ptp4l -i eth0 -m [-S] [-f configs/gPTP.cfg]`; `phc2sys -a -r -m` (follow running ptp4l); `phc2sys -s eth0 -c CLOCK_REALTIME -w`; `ts2phc -c eth0 -s nmea -f ts2phc.cfg -m`; `pmc -u -b 0 'GET CURRENT_DATA_SET'`. Example configs in `configs/`: `default.cfg`, `gPTP.cfg`, `automotive-master.cfg`/`automotive-slave.cfg`, `G.8275.1.cfg`, `UNICAST-MASTER.cfg`, `ts2phc-generic.cfg`, `ts2phc-TC.cfg`. |
| Time to first result | Estimate: 10 min for software-timestamped ptp4l between two Linux boxes; 1-3 h for GNSS PPS => PHC with `ts2phc` on a NIC with an SDP pin, including wiring and pin config. |
| License | GPL-2.0 (`COPYING`, README "GNU General Public License"). README note: when built with OpenSSL 3 (`make EXTRA_CFLAGS=-DUSE_OPENSSL`) for the Authentication TLV, the result is distributed under GPL-3. |

## Minimal usage
Not run. From README and man pages.

```sh
ethtool -T eth0                                  # hardware timestamping + "PTP Hardware Clock: N"?
sudo ptp4l -i eth0 -m                            # becomes GM or slave via BMCA
sudo phc2sys -a -r -m                            # keep system clock locked to the PHC ptp4l uses

# GNSS-disciplined grandmaster (receiver PPS on the NIC's SDP0, NMEA on /dev/ttyACM0)
cat > ts2phc.cfg <<'EOF'
[global]
ts2phc.nmea_serialport /dev/ttyACM0
ts2phc.nmea_baudrate 9600
ts2phc.pulsewidth 100000000
[eth0]
ts2phc.extts_polarity rising
ts2phc.pin_index 0
EOF
sudo ts2phc -c eth0 -s nmea -f ts2phc.cfg -m
```

## Wiring it into a nav stack
- GNSS receiver => [SatPulse](./jclark__satpulse.md) or `ts2phc` => PHC => `ptp4l` grandmaster => sensor PCs, cameras and LiDARs that speak PTP (many LiDARs sync to gPTP or 1588). This is what gives LIO/VIO pipelines such as [FAST-LIO2](./hku-mars__fast_lio.md) consistent timestamps across devices.
- System clock path: `phc2sys -E refclock_sock` => [chrony](./gitlab.com__chrony__chrony.md) `refclock SOCK`, so chrony arbitrates between PTP, NTP and holdover.
- Holdover: when GNSS drops, the PHC free-runs on the NIC oscillator; a GPSDO ([gpsdo catalog pages](../../catalog/repos/andrewbcn__lars-diy-gpsdo.md)) or Time Card ([time-card](../../catalog/repos/time-appliances-project__time-card.md)) extends holdover.
- Spoofing awareness: PTP trusts its grandmaster. Monitor the GM's GNSS with [chrony](./gitlab.com__chrony__chrony.md) `sources` against independent NTP/NTS servers to catch a time jump.

## Gotchas
- `ts2phc` NMEA mode uses only the RMC sentence for time of day (man page). Leap seconds come from the `leapfile` option (e.g. `/usr/share/zoneinfo/leap-seconds.list`) or else a table fixed at release time (man page), so set `leapfile` on long-lived systems.
- Some PHCs timestamp both edges of the PPS (`configs/ts2phc-generic.cfg` comment: Intel i210 "always time stamps both the rising and the falling edges"), so set `extts_polarity both` plus `ts2phc.pulsewidth` there.
- Software timestamping gives far worse sync than hardware; check `ethtool -T` first. If even `software-transmit` is missing, the MAC cannot be used at all (README).
- README still directs downloads to SourceForge and bug reports to `linuxptp-users@lists.nwtime.org`; the GitHub repo has issues enabled but only 2 open (2026-11), so search the mailing list archive, not GitHub, for known problems.
- PTP has no built-in security beyond the optional Authentication TLV (`configs/authentication.cfg`, `sa.cfg`), which needs both ends configured.

## Alternatives
- [statime](../../catalog/repos/pendulum-project__statime.md) - PTP in Rust; prefer if you want memory safety or a library.
- [ptpd](../../catalog/repos/ptpd__ptpd.md) - older PTP daemon, also runs on BSD; mostly superseded by linuxptp on Linux.
- [PPSi / White Rabbit](../../catalog/repos/gitlab.com__ohwr__project__ppsi.md) - sub-ns White Rabbit extension when you control the network hardware.

Sources: `README.org`, `COPYING`, `makefile`, `configs/` listing, `configs/ts2phc-generic.cfg`, `ts2phc.8`, `phc2sys.8`, tags and recent commits (github.com/nwtime/linuxptp).
