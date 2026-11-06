# chrony - integration card
<!-- about: repo:gitlab.com/chrony/chrony -->
NTP client/server (`chronyd` + `chronyc`) that disciplines the system clock from NTP/NTS servers, GNSS refclocks (PPS, gpsd SOCK/SHM, PTP hardware clocks, RTC) and manual input, with explicit source-selection safeguards (`minsources`, `maxchange`). In a hackathon it is the glue that gives every box a correct, monitored clock and lets you see when one time source (e.g. a spoofed GNSS) disagrees with the others.

| | |
|---|---|
| Install | Distro: `sudo apt install chrony` / `sudo dnf install chrony` (package name `chrony`; most distros ship it as the default time daemon). Source (doc/installation.adoc): download the release tarball from https://chrony-project.org/ or `git clone https://gitlab.com/chrony/chrony.git`, then `./configure && make && sudo make install`. Latest release 4.9 (tag dated 2026-08-27). |
| Runs on | Linux, FreeBSD, NetBSD, OpenBSD, macOS, illumos (README). Hardware timestamping and PHC refclocks are Linux features. Any CPU. |
| Inputs | NTP/NTS servers (`server`, `pool`); refclocks via `refclock <driver> <param>` with drivers `PPS` (`/dev/ppsN`, kernel PPS API), `SOCK` (Unix datagram socket fed by gpsd, SatPulse, phc2sys), `SHM` (NTP shared memory), `PHC` (`/dev/ptpN` or interface name, incl. `extpps` pin input), `RTC`, and `SENSOR` (OpenBSD only, new in 4.9). Units: offsets/delays in seconds. |
| Outputs | Disciplined `CLOCK_REALTIME` (slew/step), optional NTP/NTS server for other hosts, optional RTC trimming, logs (`log measurements statistics tracking refclocks`) and monitoring via `chronyc`. |
| Key API / entry points | Daemon `chronyd [-f /etc/chrony/chrony.conf] [-d] [-q]`. Monitor `chronyc tracking`, `chronyc sources -v`, `chronyc sourcestats -v`, `chronyc selectdata -v`, `chronyc makestep`. Config directives that matter for PNT: `refclock`, `minsources`, `maxchange`, `maxdistance`, `makestep`, `local` (holdover / isolated network), `hwtimestamp`, `ntsserverkey`/`nts` (authenticated NTP). |
| Time to first result | Estimate: 5 min with the distro package against public NTP; 30-60 min to add a GNSS receiver through gpsd SOCK + PPS, assuming PPS is already wired to a serial DCD or GPIO pin. |
| License | GPL-2.0 (`COPYING`, README "License"). No data files. |

## Minimal usage
Not run. Config lines are from `doc/chrony.conf.adoc` and `doc/faq.adoc`.

```conf
# /etc/chrony/chrony.conf - GNSS + network sources, with a sanity floor
pool pool.ntp.org iburst
server time.cloudflare.com iburst nts
refclock PPS /dev/pps0 lock NMEA refid GPS
refclock SOCK /var/run/chrony.clk.ttyS0.sock offset 0.5 delay 0.1 refid NMEA noselect
minsources 2          # do not update the clock on a single (possibly wrong) source
maxchange 1 3 0       # after 3 updates, refuse a >1 s jump and exit instead
makestep 1 3
```

```sh
sudo systemctl restart chrony   # service name varies: chrony (Debian) or chronyd (Fedora)
chronyc sources -v              # '*' selected, '+' combined, 'x' falseticker, '?' unusable
chronyc tracking                # current offset, frequency, root distance
```

## Wiring it into a nav stack
- GNSS receiver => [gpsd](../../catalog/repos/gitlab.com__gpsd__gpsd.md) => `refclock SOCK /var/run/chrony.<dev>.sock` (PPS) and `chrony.clk.<dev>.sock` (message timing). Start gpsd after chronyd so the sockets exist (FAQ).
- GNSS receiver => [SatPulse](./jclark__satpulse.md) `[ntp] sock.path` => `refclock SOCK /var/run/chrony.satpulse.sock poll 2 filter 4 refid GNSS` (from SatPulse `configs/chrony.conf`).
- PTP: [linuxptp](./nwtime__linuxptp.md) keeps the NIC PHC; chrony reads it with `refclock PHC /dev/ptp0`, or `phc2sys -E refclock_sock` feeds chrony over SOCK.
- Monitoring: [chrony_exporter](../../catalog/repos/superq__chrony_exporter.md) for Prometheus, or parse `chronyc -c tracking` (CSV mode) from a health node.
- Spoofing / jamming defence at the time layer: run GNSS together with at least two independent network sources and `minsources 2`; a GNSS time jump then shows up as a falseticker (`x`) in `chronyc sources` instead of moving the clock. `maxchange` caps what a single update can do.

## Gotchas
- PPS alone has no absolute time: needs `lock <refid>` to a coarse source or `local` (doc: "As PPS refclocks do not supply full time, another time source ... is needed").
- Prefer SOCK over SHM: the FAQ warns an untrusted process can create the SHM segment first and feed false measurements.
- gpsd's serial-timing SOCK source (`chrony.clk.*`) needs gpsd 3.25 or newer.
- 4.8 fixed `refclock extpps` on Linux 6.15+ (NEWS); use 4.8 or later with PHC PPS input on new kernels.
- `makestep <threshold> <limit>` only allows steps during the first `limit` updates; after that, offsets are slewed at most at `maxslewrate` ppm, so a large offset after a long outage takes a long time to remove. Plan for `chronyc makestep` or an explicit step policy on vehicles.
- Development lives on GitLab and the chrony-dev mailing list; the GitHub mirrors are not where issues are tracked.

## Alternatives
- [ntpd-rs](../../catalog/repos/pendulum-project__ntpd-rs.md) - Rust NTP/NTS daemon; prefer for memory safety, fewer refclock drivers.
- [NTPsec](../../catalog/repos/gitlab.com__ntpsec__ntpsec.md) or [ntp](../../catalog/repos/ntp-project__ntp.md) - classic ntpd lineage with a broader legacy refclock driver set.
- [linuxptp](./nwtime__linuxptp.md) - when you need sub-microsecond sync between sensor hosts rather than NTP-grade system time.

Sources: `README`, `COPYING`, `NEWS`, `doc/chrony.conf.adoc` (refclock drivers PPS/SOCK/SHM/PHC/RTC/SENSOR, minsources, maxchange, local, makestep), `doc/chronyc.adoc`, `doc/faq.adoc` (gpsd section), `doc/installation.adoc`, GitLab project API tags and tree (gitlab.com/chrony/chrony).
