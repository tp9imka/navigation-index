# Demo script

Live demo inside a 3-minute pitch (adjust times to the event). One driver, one narrator. The
driver never types free text on stage: every step is a command already in shell history or a
button.

## Setup (T-30 min)

- [ ] Demo laptop on mains power, sleep and notifications off, screen mirrored and tested on the venue projector.
- [ ] `make test` green on the demo laptop. Paste the tail into the team chat.
- [ ] TAK client / web map open, zoomed to the AOI, old tracks cleared.
- [ ] GCS (QGC / MAVProxy) listening on the STATUSTEXT port, if used.
- [ ] Backup video open in a paused player on the same laptop AND on laptop 2.
- [ ] Results table and one plot open in a tab.
- [ ] Network: assume none. Everything runs from localhost.

## Script

| Time | Screen | Driver does | Narrator says |
|---|---|---|---|
| 0:00 | Map, vehicle on track | `make demo` (or start replay) | "This is a TODO platform navigating with GNSS + TODO. Uncertainty circle is our own 95% radius." |
| 0:20 | Map + status panel | nothing | "Health is trusted. Sources in use: dead reckoning + GNSS." |
| 0:30 | Attack starts | nothing (scripted at T+60 s sim time) | "Now a slow spoof drag-off starts, 1.5 m/s. A single-epoch check does not see it." |
| 0:45 | Alarm on map + GCS | point at the alert | "Our windowed test fires at TODO s. GNSS is excluded, we continue on TODO." |
| 1:00 | Side by side, baseline vs ours | open the plot | "Without the monitor the estimate follows the spoofer to TODO m. With it, TODO m." |
| 1:20 | Results table | scroll | "Measured over TODO runs, ground truth from TODO. Not measured: TODO." |
| 1:35 | Failure case | show it | "Here is where it breaks: TODO." |
| 1:45 | Back to slides | hand over | |

## Fallback plan

| Failure | Detect | Switch to | Max time lost |
|---|---|---|---|
| Live run errors / hangs | No CoT on the map 10 s after start | Backup video from 0:00, narrator keeps the same script | 10 s |
| Projector / laptop dies | Black screen | Laptop 2, same video | 30 s |
| Map client crashes | Window gone | Plot of `runs/demo.jsonl` + video | 10 s |
| Judges ask to see it live after the video | - | `make demo` at the judging table after the pitch | - |

Never debug on stage. Say "switching to the recording made at H+30", switch, continue.

## Recording the backup (H+30 to H+36)

- Record the full script once end to end, screen + narration, no cuts. Note the commit hash on the first frame.
- Second recording of just the attack and alarm, 30 s, for a slide.
- Copy both to laptop 2 and to a USB stick. Check they play offline.
- Upload to the submission location if the rules allow; link it from README.
