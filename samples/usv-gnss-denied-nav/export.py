"""navdash/1 JSONL for templates/demo-dashboard, own-ship Cursor-on-Target, zones and summaries."""
import json
import math
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "mavlink-to-tak-cot"))
import cot  # noqa: E402

R95_K = 2.45
TRACK_DECIMATE_S = 5
GNSS_DECIMATE_S = 5
COT_PERIOD_S = 10
ALERT_LIMIT_M = 50.0          # illustrative harbour-approach limit, not from a standard
EPOCH = datetime(2026, 10, 20, 2, 0, 0, tzinfo=timezone.utc)  # start of the AIS window
COT_TYPE_USV = "a-f-S"        # friendly sea-surface track (dB-SPL/cot-types CoTtypes.xml)
COT_HOW_FUSED = "m-f"         # "fused" in the same file's <how> table
LABELS = {"monitor": ("Fused + monitor", "#4fc3f7"), "single": ("Single filter, gates only", "#ffb74d"),
          "gnss_dr": ("GNSS + DR, no monitor", "#81c784"), "radar_dr": ("Radar + DR (no GNSS)", "#ce93d8")}


def _ll(frame, x, y):
    lat, lon = frame.to_ll(x, y)
    return round(lat, 7), round(lon, 7)


def _write(path, header, lines):
    with open(path, "w") as f:
        f.write(json.dumps({"header": header}) + "\n")
        for ln in lines:
            f.write(json.dumps(ln) + "\n")


def write_all(d, name, frame, truth, dr, gnss, results, attack):
    d.mkdir(parents=True, exist_ok=True)
    files = []

    def track(fname, header, lines):
        _write(d / fname, {"schema": "navdash/1", **header}, lines)
        files.append(fname)

    track("truth.jsonl", {"track": "truth", "role": "truth", "label": "Truth"},
          [{"t": s.t, **dict(zip(("lat", "lon"), _ll(frame, s.x, s.y)))}
           for s in truth if int(s.t) % TRACK_DECIMATE_S == 0])
    dr_rows = results["dr"][0]
    track("ins.jsonl", {"track": "dr", "role": "ins", "label": "Compass + speed log DR"},
          [{"t": r["t"], **dict(zip(("lat", "lon"), _ll(frame, r["x"], r["y"]))), "r95_m": round(R95_K * r["sigma"], 1)}
           for r in dr_rows if int(r["t"]) % TRACK_DECIMATE_S == 0])
    track("gnss.jsonl", {"track": "gnss", "role": "gnss", "label": "GNSS fixes"},
          [{"t": s.t, **dict(zip(("lat", "lon"), _ll(frame, *g)))}
           for s, g in zip(truth, gnss) if g is not None and int(s.t) % GNSS_DECIMATE_S == 0])
    rows, fixes, events = results["monitor"]
    track("radar.jsonl", {"track": "radar-fix", "role": "altpnt", "label": "Radar-chart fixes"},
          [{"t": t, **dict(zip(("lat", "lon"), _ll(frame, fx.x, fx.y))),
            "r95_m": round(R95_K * math.sqrt(max(fx.cov[0][0], fx.cov[1][1])), 1),
            "health": fx.reason} for t, fx, _ in fixes if fx.ok])
    track("fused-radar-dr.jsonl", {"track": "fused-radar-dr", "role": "fused",
                                   "label": LABELS["radar_dr"][0], "color": LABELS["radar_dr"][1]},
          [{"t": r["t"], **dict(zip(("lat", "lon"), _ll(frame, r["sub"][0], r["sub"][1]))),
            "r95_m": round(R95_K * r["sub"][2], 1)} for r in rows if int(r["t"]) % TRACK_DECIMATE_S == 0])
    for mode in ("monitor", "single", "gnss_dr"):
        rows_m, fixes_m, ev_m = results[mode]
        lines = []
        prev_gnss = True
        for r, g in zip(rows_m, gnss):
            have = g is not None
            if have != prev_gnss:
                lines.append({"t": r["t"], "event": "gnss_restored" if have else "gnss_lost"})
                prev_gnss = have
            if int(r["t"]) % TRACK_DECIMATE_S:
                continue
            src = ["dr"] + (["gnss"] if have and not r["excluded"] else []) + (["radar"] if mode in ("single", "monitor") else [])
            lines.append({"t": r["t"], **dict(zip(("lat", "lon"), _ll(frame, r["x"], r["y"]))),
                          "r95_m": round(R95_K * r["sigma"], 1), "pl_m": round(r["pl"], 1),
                          "health": "excluded" if r["excluded"] else "trusted", "alarm": r["alarm"],
                          "sources": src})
        lines += [{"t": t, "event": ev, "text": tx} for t, ev, tx in ev_m]
        if mode == "monitor":
            lines += _radar_events(fixes_m)
            if attack.kind != "none":
                lines.append({"t": attack.t_start, "event": "attack_onset", "ground_truth": True,
                              "text": f"{attack.kind} starts (scenario label)"})
        label, color = LABELS[mode]
        hdr = {"track": f"fused-{mode}", "role": "fused", "label": label, "color": color,
               "alert_limit_m": ALERT_LIMIT_M, "pl_method": "4.80 x filter sigma_major, not certified",
               "r95_method": "2.45 x filter sigma_major"}
        if mode == "monitor":
            hdr["primary"] = True
        track(f"fused-{mode}.jsonl", hdr, lines)
    _write_zones(d / "zones.geojson", frame, truth, attack)
    (d / "manifest.json").write_text(json.dumps(
        {"title": f"USV Oresund transit - {name}", "tracks": files, "zones": "zones.geojson"}, indent=1))
    write_cot(d / "ownship_cot.xml", frame, rows)


def _radar_events(fixes, persist=3):
    out, state, run, cand = [], True, 0, None
    for t, fx, _ in fixes:
        ok = fx.ok
        if ok != state:
            run += 1
            cand = cand if cand else (t, fx.reason)
            if run >= persist:
                out.append({"t": cand[0], "event": "source_switched" if ok else "radar_fix_lost",
                            "text": "radar-chart fixes back" if ok else f"radar-chart fixes lost ({cand[1]})"})
                state, run, cand = ok, 0, None
        else:
            run, cand = 0, None
    return out


def _write_zones(path, frame, truth, attack, pad_m=1500.0, n=24):
    feats = []
    if attack.kind != "none":
        s = min(truth, key=lambda s: abs(s.t - attack.t_start))
        ring = [list(reversed(_ll(frame, s.x + pad_m * math.cos(2 * math.pi * k / n),
                                  s.y + pad_m * math.sin(2 * math.pi * k / n)))) for k in range(n + 1)]
        feats.append({"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [ring]},
                      "properties": {"kind": "spoofing" if attack.kind == "spoof" else "jamming",
                                     "label": f"{attack.kind} onset area (synthetic, not an emitter footprint)",
                                     "t_start": attack.t_start, "t_end": min(attack.t_end, truth[-1].t)}})
    path.write_text(json.dumps({"type": "FeatureCollection", "features": feats}))


def write_cot(path, frame, rows):
    """One CoT event per line, own-ship from the primary (monitor) filter. Course and speed come
    from the estimated track, not from truth."""
    with open(path, "w") as f:
        prev = None
        for r in rows:
            if int(r["t"]) % COT_PERIOD_S:
                continue
            lat, lon = _ll(frame, r["x"], r["y"])
            course = speed = None
            if prev is not None and r["t"] > prev["t"]:
                dx, dy = r["x"] - prev["x"], r["y"] - prev["y"]
                course, speed = math.degrees(math.atan2(dx, dy)) % 360, math.hypot(dx, dy) / (r["t"] - prev["t"])
            prev = r
            xml = cot.build_event("usv-oresund-1", lat, lon, 0.0, course=course, speed=speed,
                                  callsign="USV-1", ce=r["sigma"], le=cot.UNKNOWN_ERROR_M,
                                  now=EPOCH + timedelta(seconds=r["t"]), cot_type=COT_TYPE_USV)
            ev = ET.fromstring(xml)
            ev.set("how", COT_HOW_FUSED)
            ET.SubElement(ev.find("detail"), "remarks").text = (
                "GNSS excluded by integrity monitor" if r["excluded"] else "GNSS + radar-chart + DR")
            f.write(ET.tostring(ev, encoding="unicode") + "\n")


def _fmt(v, nd=0):
    return "-" if v is None else f"{v:.{nd}f}"


def summary_line(sm):
    parts = [f"[{sm['scenario']}]"]
    for m, c in sm["configs"].items():
        a = c.get("during_attack", c["all"])
        parts.append(f"{m}: max {a['max']:.0f} m final {a['final']:.0f} m"
                     + (f" det {c['detection_s']:.0f} s" if c.get("detection_s") is not None else ""))
    return " | ".join(parts)


def summary_markdown(summaries):
    L = ["| seed | scenario | config | RMS m | p95 m | max m | final m | max during attack m | alarm s | exclusion s | offset at alarm m | false alarms / exclusions |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for sm in summaries:
        for m, c in sm["configs"].items():
            a, da = c["all"], c.get("during_attack", {})
            L.append(f"| {sm['seed']} | {sm['scenario']} | {m} | {a['rms']:.1f} | {a['p95']:.1f} | {a['max']:.1f} | "
                     f"{a['final']:.1f} | {_fmt(da.get('max'), 1)} | {_fmt(c.get('detection_s'))} | {_fmt(c.get('exclusion_s'))} | "
                     f"{_fmt(c.get('spoof_offset_at_detection_m'), 1)} | {c['false_alarms']} / {c['false_exclusions']} |")
    seen = set()
    for sm in summaries:
        key = json.dumps(sm.get("radar", "default"))
        if key in seen:
            continue
        seen.add(key)
        L += ["", f"Radar-chart matching by route leg, monitor run, radar {key}, seed {sm['seed']}, {sm['scenario']}:", "",
              "| leg | scans | outcomes | accepted-fix error median / p95 m |", "|---|---|---|---|"]
        L += _leg_rows(sm)
    return "\n".join(L) + "\n"


def _leg_rows(sm):
    L = []
    for row in sm["radar_by_leg"]:
        L.append(f"| {row['name']} | {row['scans']} | "
                 + ", ".join(f"{k} {v}" for k, v in sorted(row["reasons"].items())) + " | "
                 + f"{_fmt(row.get('fix_err_median_m'), 1)} / {_fmt(row.get('fix_err_p95_m'), 1)} |")
    return L
