"""Aggregator: ingests jsn/1 node messages (and optional DF bearings), fuses them every
FUSE_PERIOD_S into jammer estimates, serves them over HTTP (stdlib).

    python3 jsn_aggregator.py --origin 69.28,16.03 --area 4000 --port 8765
    curl -X POST --data-binary @msgs.jsonl localhost:8765/v1/msg
    curl localhost:8765/v1/estimate | localhost:8765/v1/cot | localhost:8765/v1/zones.geojson
    mosquitto_sub -v -t 'jsn/v1/#' | python3 jsn_aggregator.py --origin ... --stdin

Endpoints: POST /v1/msg (JSON object, JSON array or JSONL; `topic payload` lines too),
GET /v1/estimate, /v1/nodes, /v1/cot (CoT XML events, one per line), /v1/zones.geojson.
"""
import argparse
import json
import math
import sys
import threading
from collections import defaultdict, deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import siblings  # noqa: F401
import jsn_localize as L
import jsn_model as M
import jsn_protocol as P
from geo import LocalFrame  # noqa: E402  (../interference-geolocation-to-tak)
import triangulate  # noqa: E402

FUSE_PERIOD_S = 5.0
STATIC_WINDOW_S = 10.0
D_CORR_M = 100.0                 # new-evidence spacing: ~2x the 50 m shadowing correlation length
MIN_WINDOW_S = 3.0
MOBILE_MEMORY_S = 300.0
DF_WINDOW_S = 30.0
DF_MODE_DEG = 10.0
BUFFER_LEN = 600
MAX_BODY_BYTES = 4_000_000


def _circ_robust_mean(bearings):
    best = max(bearings, key=lambda b: sum(abs((x - b + 180) % 360 - 180) < DF_MODE_DEG for x in bearings))
    near = [x for x in bearings if abs((x - best + 180) % 360 - 180) < DF_MODE_DEG]
    s = sum(math.sin(math.radians(x)) for x in near)
    c = sum(math.cos(math.radians(x)) for x in near)
    return math.degrees(math.atan2(s, c)) % 360.0, len(near)


def _window_mean(ms):
    """Collapse a node's measurements over a window into one Meas (majority kind)."""
    by = defaultdict(list)
    for m in ms:
        by[m.kind].append(m)
    kind = max(by, key=lambda k: (len(by[k]), k == "val"))
    g = by[kind]
    n = len(g)
    agg = P.Meas(node=g[-1].node, t=g[-1].t, x=sum(m.x for m in g) / n, y=sum(m.y for m in g) / n,
                 ps=sum(m.ps for m in g) / n, kind=kind, j_dbm=sum(m.j_dbm for m in g) / n,
                 sigma_db=max(sum(m.sigma_db for m in g) / n / math.sqrt(n), 0.3), static=g[-1].static,
                 source=g[-1].source)
    if kind == "upper":
        agg.j_dbm = min(m.j_dbm for m in g)
    return agg


class Aggregator:
    def __init__(self, lat0, lon0, half_size_m, jammer_speed_mps=0.0, ple=M.PLE_DEFAULT, sigma_sh=6.0,
                 grid_n=41, df_sigma_deg=3.0, two_source=True):
        self.frame = LocalFrame(lat0, lon0)
        self.area = (-half_size_m, -half_size_m, half_size_m, half_size_m)
        self.v_jam, self.ple, self.sigma_sh = jammer_speed_mps, ple, sigma_sh
        self.df_sigma = df_sigma_deg
        self.two_source = two_source
        self.grid = L.GridFilter(self.area, n=grid_n, ple=ple, sigma_sh=sigma_sh)
        self.meta = {}
        self.last_obs = {}
        self.buf = defaultdict(lambda: deque(maxlen=BUFFER_LEN))
        self.pending = defaultdict(list)       # mobile: measurements since the last counted point
        self.last_count = {}                   # mobile: (x, y, t) of the last counted point
        self.mobile_points = deque()
        self.bearings = defaultdict(lambda: deque(maxlen=BUFFER_LEN))
        self.t_last_fuse = None
        self.t_now = None
        self.estimates = []
        self.rejected = 0
        self.lock = threading.Lock()

    # ingestion
    def ingest(self, msg):
        try:
            P.validate(msg)
        except ValueError:
            self.rejected += 1
            raise
        with self.lock:
            if msg["k"] == "meta":
                self.meta[msg["id"]] = msg
                return None
            meta = self.meta.get(msg["id"])
            e, n, _ = self.frame.to_enu(msg["lat"], msg["lon"])
            m = P.to_measurement(msg, meta, (e, n))
            self.last_obs[msg["id"]] = (msg, m)
            self.buf[msg["id"]].append(m)
            if not m.static:
                self.pending[msg["id"]].append(m)
            self.t_now = max(self.t_now or msg["t"], msg["t"])
            if self.t_last_fuse is None:
                self.t_last_fuse = msg["t"]
            if self.t_now - self.t_last_fuse >= FUSE_PERIOD_S:
                return self._fuse(self.t_now)
        return None

    def ingest_bearing(self, b):
        """b: kraken.Bearing from ../interference-geolocation-to-tak."""
        with self.lock:
            self.bearings[b.station_id].append(b)

    # fusion
    def _window(self, base_s):
        """Averaging window; shortened when the jammer may move D_CORR_M within it."""
        return base_s if self.v_jam <= 0 else min(base_s, max(MIN_WINDOW_S, D_CORR_M / self.v_jam))

    def _static_snapshot(self, t):
        out = []
        w = self._window(STATIC_WINDOW_S)
        for nid, ms in self.buf.items():
            if not (self.meta.get(nid) or {}).get("static"):
                continue
            win = [m for m in ms if t - m.t <= w]
            if win:
                out.append(_window_mean(win))
        return out

    def _count_mobile(self, t):
        new = []
        for nid, ms in self.pending.items():
            if not ms:
                continue
            last = self.last_count.get(nid)
            cur = ms[-1]
            moved = math.inf if last is None else math.hypot(cur.x - last[0], cur.y - last[1])
            waited = math.inf if last is None else t - last[2]
            due = moved >= D_CORR_M or (self.v_jam > 0 and waited * self.v_jam >= D_CORR_M)
            if due:
                pt = _window_mean(ms)
                new.append(pt)
                self.last_count[nid] = (cur.x, cur.y, t)
                self.pending[nid] = []
        return new

    def _df_snapshot(self, t):
        obs, raw = [], []
        w = self._window(DF_WINDOW_S)
        for sid, bs in self.bearings.items():
            win = [b for b in bs if t - b.t <= w]
            if len(win) < 3:
                continue
            raw.extend(win)
            mean, n = _circ_robust_mean([b.bearing_deg for b in win])
            sx, sy, _ = self.frame.to_enu(win[-1].lat, win[-1].lon)
            sig = max(self.df_sigma / math.sqrt(n), L.DF_SIGMA_FLOOR_DEG)
            obs.append((sx, sy, mean, sig))
        return obs, raw

    def _to_ll(self, x, y):
        lat, lon, _ = self.frame.to_geodetic(x, y)
        return round(lat, 7), round(lon, 7)

    def _fuse(self, t):
        dt = t - self.t_last_fuse
        self.t_last_fuse = t
        if self.v_jam > 0:
            self.grid.diffuse(self.v_jam * dt)
        new_mobile = self._count_mobile(t)
        self.grid.add_recursive(new_mobile)
        self.mobile_points.extend(new_mobile)
        memory = MOBILE_MEMORY_S if self.v_jam == 0 else D_CORR_M / self.v_jam * 2
        while self.mobile_points and t - self.mobile_points[0].t > memory:
            self.mobile_points.popleft()
        static = self._static_snapshot(t)
        self.grid.set_static(static)
        df_obs, df_raw = self._df_snapshot(t)
        self.grid.set_bearings(df_obs)
        snap = static + list(self.mobile_points)
        est = {"t": t, "n_nodes": len(self.last_obs),
               "n_detecting": len({m.node for m in snap if m.kind != "upper"}),
               "n_points": len(snap), "methods": {}}
        est["detected"] = est["n_detecting"] > 0
        if est["detected"] or df_obs:
            meth = est["methods"]
            wc = L.weighted_centroid(snap)
            if wc:
                meth["wc"] = {"x": wc[0], "y": wc[1]}
            ls = (L.select_sources(snap, self.area, self.ple, self.sigma_sh) if self.two_source
                  else L.rss_ls(snap, self.area, self.ple, self.sigma_sh))
            if ls:
                meth["ls"] = {"sources": [{"x": s[0], "y": s[1], "eirp_dbm_model": s[2] + M.FSPL_D0_DB,
                                           "ellipse95": e} for s, e in zip(ls["sources"], ls["ellipse95"])],
                              "chi2": ls["chi2"], "dof": ls["dof"], "k": len(ls["sources"]),
                              "k_test": ls.get("k_test")}
            for key, use_df in (("grid", False), ("grid+df", True)):
                if key == "grid" and not est["detected"]:
                    continue
                if key == "grid+df" and not df_obs:
                    continue
                g = self.grid.estimate(use_df)
                meth[key] = {"x": g["x"], "y": g["y"], "eirp_dbm_model": g["p0"] + M.FSPL_D0_DB,
                             "ellipse95": g["ellipse95"], "cov": g["cov"],
                             "denial_radius_m": L.denial_radius_m(g["p0"], self.ple),
                             "df_fused": use_df, "rss_used": est["detected"]}
            if len(df_raw) >= 2 and len(df_obs) >= 2:
                try:
                    f = triangulate.locate(df_raw, self.df_sigma)
                    x, y, _ = self.frame.to_enu(f["lat"], f["lon"])
                    meth["df"] = {"x": x, "y": y, "ellipse95": triangulate.ellipse(f["cov"]),
                                  "n_used": f["n_used"]}
                except (ValueError, ZeroDivisionError):
                    pass
            for v in meth.values():
                for s in v.get("sources", [v]):
                    s["lat"], s["lon"] = self._to_ll(s["x"], s["y"])
        self.estimates.append(est)
        return est

    def flush(self):
        with self.lock:
            if self.t_now is not None and self.t_now != self.t_last_fuse:
                return self._fuse(self.t_now)
        return None

    def latest(self):
        return self.estimates[-1] if self.estimates else None

    def nodes(self):
        out = []
        for nid, (msg, m) in sorted(self.last_obs.items()):
            out.append({"id": nid, "lat": msg["lat"], "lon": msg["lon"], "static": m.static, "fix": msg["fix"],
                        "jst": msg["jst"], "kind": m.kind, "j_dbm": round(m.j_dbm, 1), "source": m.source,
                        "t": msg["t"]})
        return out


def _iter_body(text):
    """Yield (message or None, error or None) per item, so one bad line does not drop the batch."""
    text = text.strip()
    if text.startswith("["):
        for m in json.loads(text):
            yield m, None
        return
    for line in text.splitlines():
        if line.strip():
            try:
                yield P.parse_line(line), None
            except (ValueError, json.JSONDecodeError) as e:
                yield None, str(e)


def make_handler(agg):
    import jsn_outputs as O

    class H(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype="application/json"):
            data = body if isinstance(body, bytes) else body.encode()
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            if self.path != "/v1/msg":
                return self._send(404, '{"error":"not found"}')
            n = int(self.headers.get("Content-Length", 0))
            if n > MAX_BODY_BYTES:
                return self._send(413, '{"error":"too large"}')
            accepted, errors = 0, []
            try:
                for msg, err in _iter_body(self.rfile.read(n).decode()):
                    if err is None:
                        try:
                            agg.ingest(msg)
                            accepted += 1
                            continue
                        except ValueError as e:
                            err = str(e)
                    errors.append(err)
            except (ValueError, json.JSONDecodeError) as e:
                return self._send(400, json.dumps({"error": str(e)}))
            self._send(200 if not errors else 207, json.dumps({"accepted": accepted, "errors": errors[:10]}))

        def do_GET(self):
            est = agg.latest()
            if self.path == "/v1/estimate":
                return self._send(200, json.dumps(est))
            if self.path == "/v1/nodes":
                return self._send(200, json.dumps(agg.nodes()))
            if self.path == "/v1/cot":
                evs = O.cot_events(agg, est) if est else []
                return self._send(200, b"\n".join(evs), "application/xml")
            if self.path == "/v1/zones.geojson":
                return self._send(200, json.dumps(O.zones(agg, [est] if est else [])), "application/geo+json")
            self._send(404, '{"error":"not found"}')

        def log_message(self, *a):
            pass

    return H


def serve(agg, host="127.0.0.1", port=8765):
    return ThreadingHTTPServer((host, port), make_handler(agg))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origin", required=True, help="lat,lon of the local frame / area centre")
    ap.add_argument("--area", type=float, default=4000.0, help="side of the square search area, m")
    ap.add_argument("--jammer-speed", type=float, default=0.0, help="max jammer speed assumed, m/s")
    ap.add_argument("--sigma", type=float, default=6.0, help="shadowing sigma assumed, dB")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--stdin", action="store_true", help="read messages from stdin, print estimates")
    a = ap.parse_args()
    lat0, lon0 = (float(v) for v in a.origin.split(","))
    agg = Aggregator(lat0, lon0, a.area / 2, a.jammer_speed, sigma_sh=a.sigma)
    if a.stdin:
        for line in sys.stdin:
            try:
                msg = P.parse_line(line)
            except (ValueError, json.JSONDecodeError) as e:
                print(f"rejected: {e}", file=sys.stderr)
                continue
            if msg and (est := agg.ingest(msg)):
                print(json.dumps({k: est[k] for k in ("t", "detected", "n_detecting")} |
                                 {"grid": [est["methods"].get("grid", {}).get(k) for k in ("lat", "lon")]}), flush=True)
        return
    srv = serve(agg, a.host, a.port)
    print(f"jsn aggregator on http://{a.host}:{a.port}/v1/ (POST /v1/msg)")
    srv.serve_forever()


if __name__ == "__main__":
    main()
