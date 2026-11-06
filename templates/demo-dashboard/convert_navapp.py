#!/usr/bin/env python3
"""Convert templates/project-repo (navapp) JSONL runs into navdash/1 files for the dashboard.

    python3 convert_navapp.py runs/spoof.jsonl runs/spoof-baseline.jsonl --out sample/spoof

Writes truth.jsonl, fused-<run>.jsonl (one per input, first = primary), events inside each
fused file, zones.geojson and manifest.json. For synthetic runs it also re-runs navapp's
SyntheticSource with the seed in the run header to recover the raw GNSS fixes and an
INS-only (odometry dead reckoning) track, and refuses if the regenerated truth does not
match the logged truth. Stdlib only.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import math
import sys
from pathlib import Path

SCHEMA = "navdash/1"
DEFAULT_ALERT_LIMIT_M = 10.0
DEFAULT_INTEGRITY_RISK = 1e-5
SIGMA_TO_R95 = math.sqrt(-2.0 * math.log(0.05))
ZONE_PAD_M = 150.0
ZONE_VERTICES = 48
TRUTH_MATCH_TOL_M = 1e-3
COORD_DIGITS = 7

WGS84_A = 6378137.0
WGS84_E2 = 6.69437999014e-3

COLORS = {
    "truth": "#e8eaed",
    "ins": "#ffb74d",
    "gnss": "#ef5350",
    "altpnt": "#ba68c8",
    "fused": ["#4fc3f7", "#9ccc65", "#f06292", "#ffd54f"],
}
HERE = Path(__file__).resolve().parent
DEFAULT_NAVAPP_SRC = HERE.parent / "project-repo" / "src"


def enu_to_geodetic(east: float, north: float, lat0: float, lon0: float) -> tuple[float, float]:
    """Same flat-earth approximation as navapp/geo.py, so positions line up with CoT output."""
    s = math.sin(math.radians(lat0))
    w = math.sqrt(1.0 - WGS84_E2 * s * s)
    rm = WGS84_A * (1.0 - WGS84_E2) / w ** 3
    rn = WGS84_A / w
    return (lat0 + math.degrees(north / rm),
            lon0 + math.degrees(east / (rn * math.cos(math.radians(lat0)))))


def read_run(path: Path) -> tuple[dict, list[dict]]:
    meta, recs = {}, []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        obj = json.loads(line)
        if "meta" in obj:
            meta = obj["meta"]
        else:
            recs.append(obj)
    if not meta:
        raise SystemExit(f"{path}: no meta header line; is this a navapp run?")
    return meta, recs


def point(t, east, north, origin, **extra) -> dict:
    lat, lon = enu_to_geodetic(east, north, *origin)
    rec = {"t": t, "lat": round(lat, COORD_DIGITS), "lon": round(lon, COORD_DIGITS)}
    rec.update({k: v for k, v in extra.items() if v is not None})
    return rec


def header(track, role, label, color, **extra) -> dict:
    return {"header": {"schema": SCHEMA, "track": track, "role": role, "label": label,
                       "color": color, **extra}}


def write_jsonl(path: Path, lines: list[dict]) -> None:
    path.write_text("".join(json.dumps(x, separators=(",", ":")) + "\n" for x in lines))


def fused_events(recs: list[dict]) -> list[dict]:
    events, prev = [], None
    for r in recs:
        t = r["t"]
        if prev is not None:
            h0, h1 = prev["health"], r["health"]
            if h1 != h0:
                if h1 == "unavailable":
                    events.append({"t": t, "event": "gnss_lost", "text": "No absolute fix"})
                elif h0 == "unavailable":
                    events.append({"t": t, "event": "gnss_restored", "text": f"Absolute fix back ({h1})"})
                if h1 == "excluded":
                    events.append({"t": t, "event": "spoof_suspected",
                                   "text": "GNSS excluded: windowed innovation test over gate"})
                elif h0 == "excluded" and h1 != "unavailable":
                    events.append({"t": t, "event": "fix_readmitted", "text": f"GNSS readmitted ({h1})"})
            if r["alarm"] != prev["alarm"]:
                events.append({"t": t, "event": "alarm_raised" if r["alarm"] else "alarm_cleared",
                               "text": "Integrity alarm " + ("raised" if r["alarm"] else "cleared")})
            s0, s1 = "+".join(prev["sources"]) or "none", "+".join(r["sources"]) or "none"
            # the first predict after the trust-on-first-fix init is not a switch
            if s0 != s1 and prev is not recs[0] and "suspect" not in (r["health"], prev["health"]):
                events.append({"t": t, "event": "source_switched", "text": f"Sources {s0} => {s1}"})
        prev = r
    return events


def regenerate_sensors(meta: dict, navapp_src: Path):
    """Re-run the synthetic source; returns (gnss fixes, ins track, truth) in ENU or None."""
    if str(navapp_src) not in sys.path:
        sys.path.insert(0, str(navapp_src))
    try:
        from navapp.sim import Scenario, SyntheticSource
    except ImportError as e:
        print(f"navapp not importable from {navapp_src} ({e}); skipping GNSS/INS tracks", file=sys.stderr)
        return None
    fields = {f.name for f in dataclasses.fields(Scenario)}
    sc = Scenario(**{k: v for k, v in meta.items() if k in fields})
    fixes, ins, truth = [], [], []
    pos = None
    t_prev = None
    for ep in SyntheticSource(sc).epochs():
        truth.append((ep.t, ep.truth.east, ep.truth.north))
        if ep.absolute is not None:
            fixes.append((ep.t, ep.absolute.east, ep.absolute.north, ep.absolute_sigma))
        if pos is None:
            if ep.absolute is not None:
                pos = (ep.absolute.east, ep.absolute.north)
        elif ep.velocity is not None:
            dt = ep.t - t_prev
            pos = (pos[0] + ep.velocity.east * dt, pos[1] + ep.velocity.north * dt)
        t_prev = ep.t
        if pos is not None:
            ins.append((ep.t, pos[0], pos[1]))
    return fixes, ins, truth


def zone_polygon(points: list[tuple[float, float]], pad_m: float, origin) -> list[list[float]]:
    ce = sum(p[0] for p in points) / len(points)
    cn = sum(p[1] for p in points) / len(points)
    r = max(math.hypot(e - ce, n - cn) for e, n in points) + pad_m
    ring = []
    for i in range(ZONE_VERTICES + 1):
        a = 2 * math.pi * i / ZONE_VERTICES
        lat, lon = enu_to_geodetic(ce + r * math.cos(a), cn + r * math.sin(a), *origin)
        ring.append([round(lon, COORD_DIGITS), round(lat, COORD_DIGITS)])
    return ring


def convert(inputs: list[Path], out: Path, alert_limit: float, integrity_risk: float,
            navapp_src: Path, sensors: bool, zone_pad: float) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    pl_k = math.sqrt(-2.0 * math.log(integrity_risk))
    pl_method = (f"k * sigma_h with k = sqrt(-2 ln {integrity_risk:g}) = {pl_k:.2f} "
                 "(isotropic 2D Gaussian tail from the filter's own sigma; not a certified HPL)")
    runs = [(p, *read_run(p)) for p in inputs]
    meta0, recs0 = runs[0][1], runs[0][2]
    origin = tuple(meta0.get("origin", (0.0, 0.0)))
    kind = meta0.get("kind", "run")
    onset = meta0.get("attack_onset_s")
    files = []

    truth_lines = [header("truth", "truth", "Truth (simulator)", COLORS["truth"],
                          source=meta0.get("source", "unknown"), origin=list(origin))]
    truth_lines += [point(r["t"], r["truth_east"], r["truth_north"], origin)
                    for r in recs0 if r.get("truth_east") is not None]
    if onset is not None:
        truth_lines.append({"t": onset, "event": "attack_onset", "ground_truth": True,
                            "text": f"{kind} starts (scenario ground truth, not a detection)"})
    write_jsonl(out / "truth.jsonl", truth_lines)
    files.append("truth.jsonl")

    for i, (path, meta, recs) in enumerate(runs):
        stem = path.stem
        integ = meta.get("integrity")
        label = f"Fused {stem} ({'integrity on' if integ else 'no integrity monitor'})"
        lines = [header(f"fused-{stem}", "fused", label, COLORS["fused"][i % len(COLORS["fused"])],
                        primary=(i == 0), alert_limit_m=alert_limit, pl_method=pl_method,
                        r95_method="2.45 * sigma_h (filter 95% radius)", run_meta=meta)]
        for r in recs:
            if r.get("east") is None:
                continue
            sig = r.get("sigma_h")
            lines.append(point(r["t"], r["east"], r["north"], origin,
                               r95_m=round(SIGMA_TO_R95 * sig, 3) if sig is not None else None,
                               pl_m=round(pl_k * sig, 3) if sig is not None else None,
                               health=r.get("health"), alarm=r.get("alarm"),
                               sources=r.get("sources")))
        lines += fused_events(recs)
        name = f"fused-{stem}.jsonl"
        write_jsonl(out / name, lines)
        files.append(name)

    if sensors and meta0.get("source") == "synthetic":
        regen = regenerate_sensors(meta0, navapp_src)
        if regen:
            fixes, ins, truth = regen
            logged = {r["t"]: (r["truth_east"], r["truth_north"]) for r in recs0}
            worst = max(math.hypot(e - logged[t][0], n - logged[t][1]) for t, e, n in truth if t in logged)
            if worst > TRUTH_MATCH_TOL_M:
                raise SystemExit(f"regenerated truth differs from log by {worst:.3f} m; "
                                 "navapp sim changed since the run, re-run `make sim` or pass --no-sensors")
            write_jsonl(out / "gnss.jsonl",
                        [header("gnss", "gnss", "GNSS fixes (as received, incl. spoofed)", COLORS["gnss"],
                                regenerated_from_seed=meta0.get("seed"))]
                        + [point(t, e, n, origin, r95_m=round(SIGMA_TO_R95 * s, 3)) for t, e, n, s in fixes])
            write_jsonl(out / "ins.jsonl",
                        [header("ins", "ins", "INS-only (odometry dead reckoning)", COLORS["ins"],
                                regenerated_from_seed=meta0.get("seed"))]
                        + [point(t, e, n, origin) for t, e, n in ins])
            files += ["gnss.jsonl", "ins.jsonl"]

    manifest = {"schema": SCHEMA, "title": f"navapp {kind} (seed {meta0.get('seed')}, synthetic)",
                "tracks": files}
    if onset is not None and kind in ("jam", "spoof"):
        t_end = onset + meta0["jam_duration_s"] if kind == "jam" else recs0[-1]["t"]
        pts = [(r["truth_east"], r["truth_north"]) for r in recs0
               if r.get("truth_east") is not None and onset <= r["t"] <= t_end]
        zone_kind = "jamming" if kind == "jam" else "spoofing"
        fc = {"type": "FeatureCollection", "features": [{
            "type": "Feature",
            "properties": {"kind": zone_kind, "label": f"Synthetic {zone_kind} area",
                           "t_start": onset, "t_end": t_end,
                           "note": "drawn around the truth track during the attack window; "
                                   "not an emitter footprint"},
            "geometry": {"type": "Polygon", "coordinates": [zone_polygon(pts, zone_pad, origin)]}}]}
        (out / "zones.geojson").write_text(json.dumps(fc, separators=(",", ":")) + "\n")
        manifest["zones"] = "zones.geojson"
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("runs", nargs="+", type=Path, help="navapp JSONL runs; the first is the primary fused track")
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--alert-limit", type=float, default=DEFAULT_ALERT_LIMIT_M, help="horizontal alert limit, m")
    p.add_argument("--integrity-risk", type=float, default=DEFAULT_INTEGRITY_RISK,
                   help="per-epoch risk used for the k * sigma protection level")
    p.add_argument("--navapp-src", type=Path, default=DEFAULT_NAVAPP_SRC)
    p.add_argument("--no-sensors", action="store_true", help="skip regenerating GNSS / INS-only tracks")
    p.add_argument("--zone-pad", type=float, default=ZONE_PAD_M)
    a = p.parse_args(argv)
    m = convert(a.runs, a.out, a.alert_limit, a.integrity_risk, a.navapp_src, not a.no_sensors, a.zone_pad)
    print(f"{len(m['tracks'])} tracks{' + zones' if 'zones' in m else ''} => {a.out}/manifest.json",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
