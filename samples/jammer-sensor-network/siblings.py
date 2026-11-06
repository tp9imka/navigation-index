"""Put the sibling samples this one imports on sys.path (they are used unchanged):
../interference-geolocation-to-tak (geo, kraken, triangulate, tak_out) and
../mavlink-to-tak-cot (cot)."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.dirname(HERE)
for _d in ("interference-geolocation-to-tak", "mavlink-to-tak-cot"):
    _p = os.path.join(SAMPLES, _d)
    if _p not in sys.path:
        sys.path.append(_p)
