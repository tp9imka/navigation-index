"""CoT output for an emitter fix: a point (unknown ground) plus a 95% ellipse drawing.

Point events come from ../mavlink-to-tak-cot/cot.py (imported, unchanged); the extra
detail elements are added to its XML here.
"""
import math
import os
import socket
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "mavlink-to-tak-cot"))
import cot  # noqa: E402
from triangulate import CHI2_2DOF_95  # noqa: E402

EMITTER_COT_TYPE = "a-u-G"       # unknown ground point; change to your unit's convention
ELLIPSE_COT_TYPE = "u-d-c-e"     # ATAK drawn ellipse (shape/ellipse major, minor, angle)
HOW_FUSED = "m-f"
STALE_S = 600
UNKNOWN_HEIGHT_HAE = 0.0
MESH_SA_GROUP, MESH_SA_PORT = "239.2.3.1", 6969
MULTICAST_TTL = 1
ELLIPSE_LINE_ABGR = "ff0000ff"   # KML colour aabbggrr: opaque red
ELLIPSE_FILL_ABGR = "400000ff"


def _retag(xml_bytes, how):
    ev = ET.fromstring(xml_bytes)
    ev.set("how", how)
    return ev


def emitter_events(uid, lat, lon, semi_major_95, semi_minor_95, angle_deg, sigma_major_1,
                   remarks, now=None):
    """Returns [point_event_bytes, ellipse_event_bytes]."""
    point = _retag(cot.build_event(uid, lat, lon, UNKNOWN_HEIGHT_HAE, callsign="GNSS-JAM est",
                                   ce=sigma_major_1, now=now, stale_s=STALE_S,
                                   cot_type=EMITTER_COT_TYPE), HOW_FUSED)
    ET.SubElement(point.find("detail"), "remarks").text = remarks

    ell = _retag(cot.build_event(uid + ".ellipse", lat, lon, UNKNOWN_HEIGHT_HAE,
                                 callsign="GNSS-JAM 95%", now=now, stale_s=STALE_S,
                                 cot_type=ELLIPSE_COT_TYPE), HOW_FUSED)
    shape = ET.SubElement(ell.find("detail"), "shape")
    ET.SubElement(shape, "ellipse", {"major": f"{semi_major_95:.1f}",
                                     "minor": f"{semi_minor_95:.1f}",
                                     "angle": f"{angle_deg:.1f}"})
    link = ET.SubElement(shape, "link", {"uid": uid + ".ellipse.Style", "type": "b-x-KmlStyle",
                                         "relation": "p-c"})
    style = ET.SubElement(link, "Style")
    ls = ET.SubElement(style, "LineStyle")
    ET.SubElement(ls, "color").text = ELLIPSE_LINE_ABGR
    ET.SubElement(ls, "width").text = "3.0"
    ET.SubElement(ET.SubElement(style, "PolyStyle"), "color").text = ELLIPSE_FILL_ABGR
    return [ET.tostring(point, encoding="utf-8"), ET.tostring(ell, encoding="utf-8")]


def events_from_fix(uid, lat, lon, ellipse95, remarks, now=None):
    """ellipse95 = (semi_major_m, semi_minor_m, major_axis_bearing_deg) at 95%.
    CoT ce gets the 1-sigma semi-major axis (conservative stand-in for a circular error)."""
    sigma_major_1 = ellipse95[0] / math.sqrt(CHI2_2DOF_95)
    return emitter_events(uid, lat, lon, *ellipse95, sigma_major_1, remarks, now=now)


def write_events(events, out_dir, stem):
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i, ev in enumerate(events):
        p = os.path.join(out_dir, f"{stem}-{i}.cot.xml")
        with open(p, "wb") as fh:
            fh.write(b'<?xml version="1.0" encoding="UTF-8"?>\n' + ev)
        paths.append(p)
    return paths


def send_udp(events, host=MESH_SA_GROUP, port=MESH_SA_PORT):
    """Mesh SA multicast (ATAK default input) or any UDP CoT input on a TAK server."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
        for ev in events:
            s.sendto(ev, (host, port))
