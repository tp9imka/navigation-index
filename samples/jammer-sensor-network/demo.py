"""End to end: simulated nodes => jsn/1 messages => aggregator (in-process or over HTTP) =>
estimates => CoT files + navdash/1 dashboard files.

    python3 demo.py                       # static, moving, two jammers; writes out/<scenario>/
    python3 demo.py --scenario static --http --buildings
"""
import argparse
import itertools
import json
import math
import os
import random
import threading
import urllib.request

import siblings  # noqa: F401
import jsn_aggregator as A
import jsn_localize as L
import jsn_model as M
import jsn_outputs as O
import jsn_protocol as P
import jsn_scenarios as S
import tak_out  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SETTLE_S = 60.0                  # error statistics use estimates this long after jammer on


def _post(url, msgs):
    body = "\n".join(json.dumps(m) for m in msgs).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/x-ndjson"})
    with urllib.request.urlopen(req, timeout=10) as r:
        res = json.loads(r.read())
    if res["errors"]:
        raise RuntimeError(res["errors"])


def run(sc, http=False, out_dir=None, seed=7, quiet=False, dump=None):
    rng = random.Random(seed)
    agg = A.Aggregator(*S.ORIGIN, S.HALF_M, jammer_speed_mps=sc.jammer_speed_mps, sigma_sh=6.0)
    frame = agg.frame
    srv = None
    if http:
        srv = A.serve(agg, port=0)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        url = f"http://127.0.0.1:{srv.server_address[1]}/v1/msg"
    deliver = (lambda ms: _post(url, ms)) if http else (lambda ms: [agg.ingest(m) for m in ms])
    dump_fh = open(dump, "w") if dump else None

    def send(ms):
        if dump_fh:
            dump_fh.writelines(f"{P.topic(m)} {json.dumps(m, separators=(',', ':'))}\n" for m in ms)
        deliver(ms)

    metas = []
    for n in sc.nodes:
        lat, lon, _ = frame.to_geodetic(*n.path(0.0))
        metas.append(P.make_meta(n.id, lat, lon, n.static, hw="u-blox M8/M9/F9 class (simulated)", **n.meta()))
    send(metas)
    truth = {j.name: [] for j in sc.jammers}
    vehicles = {n.id: [] for n in sc.nodes if not n.static}
    t = 0.0
    while t <= sc.duration_s:
        msgs = []
        for n in sc.nodes:
            j = M.total_jammer_dbm(sc.env, n.path(t), sc.jammers, t)
            f, _ = n.observe(t, j)
            lat, lon, _ = frame.to_geodetic(*f["xy"])
            msgs.append(P.make_obs(n.id, lat, lon, f))
            if not n.static:
                vehicles[n.id].append((t, round(lat, 7), round(lon, 7), f["pf"]))
        send(msgs)
        for b in S.df_bearings(sc, t, frame, rng):
            agg.ingest_bearing(b)
        for jm in sc.jammers:
            if jm.active(t):
                la, lo, _ = frame.to_geodetic(*jm.path(t))
                truth[jm.name].append((t, round(la, 7), round(lo, 7)))
        t += 1.0
    agg.flush()
    if dump_fh:
        dump_fh.close()
    if srv:
        srv.shutdown()
        srv.server_close()
    summary = summarize(sc, agg)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        est = agg.latest()
        tak_out.write_events(O.cot_events(agg, est), out_dir, "jsn")
        O.write_navdash(out_dir, agg, truth, f"Jammer sensor network: {sc.name} ({len(sc.nodes)} nodes)",
                        vehicles)
        with open(os.path.join(out_dir, "summary.json"), "w") as fh:
            json.dump(summary, fh, indent=1)
        with open(os.path.join(out_dir, "estimate-last.json"), "w") as fh:
            json.dump(est, fh, indent=1)
    if not quiet:
        print_summary(summary)
    return agg, summary


def _truth_at(sc, t):
    return [j.path(t) for j in sc.jammers if j.active(t)]


def _err(sources, truths):
    """Mean error under the best assignment of estimated sources to true ones."""
    best = math.inf
    for perm in itertools.permutations(truths, min(len(sources), len(truths))):
        e = [math.hypot(s[0] - p[0], s[1] - p[1]) for s, p in zip(sources, perm)]
        best = min(best, sum(e) / len(e))
    return best


def summarize(sc, agg):
    t_on = min(j.t_on for j in sc.jammers)
    rows = {}
    first_det = None
    for e in agg.estimates:
        tr = _truth_at(sc, e["t"])
        if not tr or not e["methods"]:
            continue
        if e["detected"] and first_det is None:
            first_det = e["t"]
        for name, v in e["methods"].items():
            srcs = v.get("sources", [v])
            pts = [(s["x"], s["y"]) for s in srcs]
            if name == "ls":
                name = f"ls(k={v['k']})"
            r = rows.setdefault(name, {"errors": [], "inside95": []})
            if e["t"] - t_on >= SETTLE_S:
                r["errors"].append(_err(pts, tr))
                if len(srcs) == 1 and len(tr) == 1 and "ellipse95" in srcs[0]:
                    cov = v.get("cov") or _cov_from_ellipse(srcs[0]["ellipse95"])
                    r["inside95"].append(L.inside_ellipse(tr[0][0] - pts[0][0], tr[0][1] - pts[0][1], cov))
    out = {"scenario": sc.name, "note": sc.note, "nodes": len(sc.nodes),
           "mobile_nodes": sum(not n.static for n in sc.nodes), "df_stations": len(sc.df),
           "jammers": [{"name": j.name, "eirp_dbm": j.eirp_dbm} for j in sc.jammers],
           "first_detection_s_after_on": None if first_det is None else first_det - t_on,
           "fuse_steps": len(agg.estimates), "methods": {}}
    last = agg.latest()
    out["last"] = {k: last["methods"][k] for k in last["methods"]} if last else None
    for name, r in sorted(rows.items()):
        es = sorted(r["errors"])
        if not es:
            continue
        out["methods"][name] = {"n": len(es), "median_m": round(es[len(es) // 2], 1),
                                "p90_m": round(es[int(0.9 * (len(es) - 1))], 1),
                                "inside95_frac": round(sum(r["inside95"]) / len(r["inside95"]), 2)
                                if r["inside95"] else None}
    return out


def _cov_from_ellipse(ell):
    a, b, ang = ell
    s1, s2 = (a ** 2) / L.CHI2_2DOF_95, (b ** 2) / L.CHI2_2DOF_95
    ue, un = math.sin(math.radians(ang)), math.cos(math.radians(ang))
    return [[s1 * ue * ue + s2 * un * un, (s1 - s2) * ue * un], [(s1 - s2) * ue * un, s1 * un * un + s2 * ue * ue]]


def print_summary(s):
    print(f"== {s['scenario']} {s['note']}: {s['nodes']} nodes ({s['mobile_nodes']} mobile), "
          f"{s['df_stations']} DF stations, jammers {[(j['name'], j['eirp_dbm']) for j in s['jammers']]} dBm EIRP")
    print(f"   first detection {s['first_detection_s_after_on']} s after jammer on, {s['fuse_steps']} fuse steps")
    print(f"   {'method':<10} {'n':>4} {'median m':>9} {'p90 m':>7} {'truth in 95%':>13}")
    for k, v in s["methods"].items():
        cov = "-" if v["inside95_frac"] is None else f"{v['inside95_frac']:.2f}"
        print(f"   {k:<10} {v['n']:>4} {v['median_m']:>9} {v['p90_m']:>7} {cov:>13}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", choices=["static", "moving", "two", "all"], default="all")
    ap.add_argument("--http", action="store_true", help="send messages through the HTTP aggregator")
    ap.add_argument("--buildings", action="store_true", help="add building blockage near the static jammer")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--mobile", type=int, default=2, help="number of vehicle nodes")
    ap.add_argument("--static-nodes", type=int, default=12)
    ap.add_argument("--out", default=os.path.join(HERE, "out"))
    ap.add_argument("--dump-msgs", help="also write every message as `topic payload` lines (mosquitto_sub -v format)")
    a = ap.parse_args()
    names = ["static", "moving", "two"] if a.scenario == "all" else [a.scenario]
    for name in names:
        sc = S.build(name, seed=a.seed, n_static=a.static_nodes, n_mobile=a.mobile, buildings=a.buildings)
        tag = name + ("-buildings" if a.buildings else "") + (f"-m{a.mobile}" if a.mobile != 2 else "")
        run(sc, http=a.http, out_dir=os.path.join(a.out, tag), dump=a.dump_msgs)
        print(f"   wrote {os.path.relpath(os.path.join(a.out, tag), HERE)}/ (CoT, navdash manifest, zones, summary)")


if __name__ == "__main__":
    main()
