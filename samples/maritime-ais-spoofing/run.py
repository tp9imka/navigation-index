"""Run the detectors on real DMA AIS, then on the same data with injected spoofing episodes.

  python dma.py --date 2026-11-03 --mb 100 --out-dir data
  python run.py --csv data/aisdk-2026-11-03.head100mb.csv --hours 4 --seeds 1 2 3
"""
import argparse
import json
import time
from collections import Counter

import detectors as D
import evaluate
import export
import inject
import land


def detect(tracks, shp, cfg):
    masks = land.masks_for_tracks(tracks, shp) if shp else None
    flags = D.run_all(tracks, masks, cfg)
    return flags, D.aggregate(flags, cfg)


def describe_real(tracks, flags, alerts):
    by = {t.mmsi: t for t in tracks}
    static = Counter(f.kind for f in flags if f.kind in D.MMSI_STATIC_KINDS)
    lines = [f"tracks {len(tracks)} ({Counter(t.mobile for t in tracks).most_common()})",
             f"fixes {sum(len(t.fixes) for t in tracks)}",
             f"flags by kind {Counter(f.kind for f in flags).most_common()}",
             f"static MMSI anomalies {static.most_common()}",
             f"alerts {len(alerts)} on {len({a.mmsi for a in alerts})} vessels",
             "alerts by strongest kind " + str(Counter(
                 next((k for k in ('cluster', 'on_land', 'mmsi_shared', 'jump') if k in a.kinds), 'weak-only')
                 for a in alerts).most_common()),
             "alerting vessels by ship type " + str(Counter(by[m].ship_type for m in {a.mmsi for a in alerts}).most_common(8))]
    return "\n".join(lines)


def nmea_roundtrip(tracks, eps, shp, cfg, out):
    import nmea_io
    path = f"{out}/injected_vessels.nmea"
    with open(path, "w") as fh:
        for t in tracks:
            fh.write("\n".join(nmea_io.track_to_nmea(t)) + "\n")
    back = nmea_io.rows_to_tracks(nmea_io.read_nmea(path)[0])
    static = {t.mmsi: t for t in tracks}
    for t in back:
        t.ship_type, t.length_m, t.name = static[t.mmsi].ship_type, static[t.mmsi].length_m, static[t.mmsi].name
    _, al = detect(back, shp, cfg)
    rows, totals = evaluate.score(al, eps)
    print(f"\n== NMEA round trip: {sum(len(t.fixes) for t in back)} fixes via pyais ==\n"
          + evaluate.summarize(rows, totals))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--hours", type=float, default=None)
    ap.add_argument("--land", default="data/ne_10m_land.shp", help="'' to skip on-land check")
    ap.add_argument("--seeds", type=int, nargs="*", default=[1])
    ap.add_argument("--out", default="example_output")
    ap.add_argument("--nmea-roundtrip", action="store_true",
                    help="last seed: encode injected vessels to AIVDM with pyais, decode, re-detect")
    a = ap.parse_args()
    cfg = D.Config()
    import dma
    t0 = time.time()
    tracks, stats = dma.frame_to_tracks(dma.load_frame(a.csv, a.hours))
    print(f"loaded {stats} in {time.time() - t0:.0f} s")
    shp = a.land and (a.land if a.land.endswith(".shp") else land.fetch_land(a.land))
    t0 = time.time()
    flags, alerts = detect(tracks, shp, cfg)
    print(f"\n== unaltered real data ({time.time() - t0:.0f} s) ==\n" + describe_real(tracks, flags, alerts))
    by = {t.mmsi: t for t in tracks}
    export.write_outputs(alerts, by, a.out, "real_alerts")
    with open(f"{a.out}/real_alerts.txt", "w") as fh:
        for al in sorted(alerts, key=lambda x: -sum(x.kinds.values())):
            t = by[al.mmsi]
            fh.write(f"{al.mmsi}\t{t.name}\t{t.ship_type}\t{t.mobile}\t{len(t.fixes)}\t"
                     f"{al.start:.0f}-{al.end:.0f}\t{dict(al.kinds)}\t{al.flags[0].detail}\n")
    exclude = {al.mmsi for al in alerts}
    results = []
    for seed in a.seeds:
        t0 = time.time()
        inj, eps = inject.inject(tracks, seed=seed, exclude=exclude)
        _, al2 = detect(inj, shp, cfg)
        rows, totals = evaluate.score(al2, eps)
        print(f"\n== injected, seed {seed}: {len(eps)} episodes on {len({e.mmsi for e in eps})} vessels "
              f"({time.time() - t0:.0f} s) ==\n" + evaluate.summarize(rows, totals))
        results.append({"seed": seed, "totals": totals,
                        "episodes": [{**r["ep"]._asdict(), "detected": r["detected"], "ttd_s": r["ttd_s"],
                                      "kinds": dict(r["kinds"])} for r in rows]})
        if seed == a.seeds[-1]:
            inj_by = {t.mmsi: t for t in inj}
            injected = {e.mmsi for e in eps}
            export.write_outputs([x for x in al2 if x.mmsi in injected], inj_by, a.out, "injected_alerts")
            if a.nmea_roundtrip:
                nmea_roundtrip([inj_by[m] for m in injected], eps, shp, cfg, a.out)
    with open(f"{a.out}/injection_results.json", "w") as fh:
        json.dump(results, fh, indent=1)


if __name__ == "__main__":
    main()
