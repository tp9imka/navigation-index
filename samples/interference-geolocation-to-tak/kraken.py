"""Adapter for krakensdr_doa outputs => Bearing records (true bearing, station position).

Formats read from krakenrf/krakensdr_doa @ 2e1c4e6 (2025-12-13):
- "Kraken Pro Local" JSON: SignalProcessor.wr_json() POSTs one dict per VFO to the node
  middleware (_nodejs/index.js /doapost), which re-broadcasts it on ws://KRAKEN_IP:8021.
  radioBearing is the raw DoA theta (array frame), gpsBearing is the station heading.
- "Kraken App" CSV: DOA_value.html (served on :8081), one line per VFO, second field is
  360 - theta.
Bearing convention from calculate_end_lat_lng(): true = (heading + 360 - theta) % 360.
"""
import json
import time
import urllib.request
from dataclasses import dataclass

CSV_MIN_FIELDS = 12
DEFAULT_POLL_S = 1.0
HTTP_TIMEOUT_S = 5.0


@dataclass(frozen=True)
class Bearing:
    t: float               # seconds (epoch or scenario time)
    station_id: str
    lat: float
    lon: float
    bearing_deg: float     # true bearing to emitter, clockwise from north
    conf: float = 0.0
    power_db: float = 0.0
    freq_hz: float = 0.0


def from_kraken_json(d):
    theta = float(d["radioBearing"])
    heading = float(d["gpsBearing"])
    return Bearing(
        t=float(d["tStamp"]) / 1000.0,
        station_id=str(d["station_id"]),
        lat=float(d["latitude"]),
        lon=float(d["longitude"]),
        bearing_deg=(heading + 360.0 - theta) % 360.0,
        conf=float(d.get("conf", 0.0)),
        power_db=float(d.get("power", 0.0)),
        freq_hz=float(d.get("freq", 0.0)),
    )


def to_kraken_json(t_ms, station_id, lat, lon, heading_deg, theta_deg, conf, power_db, freq_hz):
    """Inverse of from_kraken_json, field types as wr_json() writes them (mostly strings)."""
    return {
        "station_id": station_id, "tStamp": int(t_ms), "gps_timestamp": int(t_ms),
        "latitude": str(lat), "longitude": str(lon), "gpsBearing": str(heading_deg),
        "speed": "0", "radioBearing": f"{theta_deg}", "conf": f"{conf:.2f}",
        "power": f"{power_db:.1f}", "freq": int(freq_hz), "antType": "UCA",
        "latency": 100, "processing_time": 50, "doaArray": "", "adc_overdrive": False,
        "num_corr_sources": "1", "snr_db": 10.0,
    }


def from_kraken_csv_line(line):
    f = [x.strip() for x in line.split(",")]
    if len(f) < CSV_MIN_FIELDS:
        raise ValueError(f"expected >= {CSV_MIN_FIELDS} fields, got {len(f)}")
    doa_cw = float(f[1])  # already 360 - theta
    heading = float(f[10])
    return Bearing(
        t=float(f[0]) / 1000.0, station_id=f[7], lat=float(f[8]), lon=float(f[9]),
        bearing_deg=(heading + doa_cw) % 360.0, conf=float(f[2]), power_db=float(f[3]),
        freq_hz=float(f[4]),
    )


def read_jsonl(path):
    with open(path) as fh:
        return [from_kraken_json(json.loads(line)) for line in fh if line.strip()]


def poll_csv(url, period_s=DEFAULT_POLL_S, max_polls=None):
    """Poll http://KRAKEN_IP:8081/DOA_value.html; yields Bearing per VFO line."""
    n = 0
    while max_polls is None or n < max_polls:
        with urllib.request.urlopen(url, timeout=HTTP_TIMEOUT_S) as r:
            for line in r.read().decode().splitlines():
                if line.strip():
                    yield from_kraken_csv_line(line)
        n += 1
        if max_polls is None or n < max_polls:
            time.sleep(period_s)


async def listen_ws(url, on_bearing):
    """ws://KRAKEN_IP:8021 in "Kraken Pro Local" mode. Needs `pip install websockets`."""
    import websockets
    async with websockets.connect(url) as ws:
        async for msg in ws:
            d = json.loads(msg)
            if "radioBearing" in d:
                on_bearing(from_kraken_json(d))
