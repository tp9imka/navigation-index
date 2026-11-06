"""Extract Open Drone ID payloads from pcap / pcapng captures (stdlib only).

Wi-Fi (radiotap, linktype 127): parses the 802.11 management header and walks
  - Beacon IEs for the ASD-STAN vendor IE (OUI FA:0B:BC, type 0x0D)
  - NAN Service Discovery action frames (Wi-Fi Alliance OUI, type 0x13) for the ODID service id
BLE (any linktype, e.g. 272 Nordic BLE sniffer): scans for an AD structure
  [len][0x16][0xFA 0xFF][0x0D][counter][message or pack] and checks that len is consistent.
  This is a signature scan, not a full link-layer parser. For the nRF Sniffer linktype (272)
  packets whose CRC-OK flag is clear are dropped: they decode to garbage (e.g. lon -214 deg).

  python3 capture.py odid_wifi_sample.pcap [--hex]
"""
import argparse
import json
import struct
import sys

import odid

LINKTYPE_IEEE802_11 = 105
LINKTYPE_RADIOTAP = 127
LINKTYPE_NORDIC_BLE = 272
NORDIC_FLAGS_OFFSET = 8       # board(1) + payload len(2) + proto ver(1) + counter(2) + id(1) + hdr len(1)
NORDIC_PROTO_VERSIONS = (2, 3)
NORDIC_FLAG_CRC_OK = 0x01

FC_TYPE_MGMT = 0
SUBTYPE_BEACON = 8
SUBTYPE_ACTION = 13
MGMT_HDR_LEN = 24
BEACON_FIXED_LEN = 12
IE_VENDOR = 221
NAN_ACTION_CATEGORY = 0x04  # public action
NAN_ACTION_CODE = 0x09      # vendor specific
NAN_SDF_HDR_LEN = 6         # category, action, OUI(3), OUI type
BLE_AD_SERVICE_DATA_16 = 0x16
BLE_ODID_SIG = bytes([BLE_AD_SERVICE_DATA_16, 0xFA, 0xFF, odid.ODID_APP_CODE])


def read_packets(path):
    """Yield (timestamp_s, linktype, frame_bytes) from a pcap or pcapng file."""
    data = open(path, "rb").read()
    magic = data[:4]
    if magic in (b"\xd4\xc3\xb2\xa1", b"\xa1\xb2\xc3\xd4", b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d"):
        e = "<" if magic[0] in (0xD4, 0x4D) else ">"
        nano = magic in (b"\x4d\x3c\xb2\xa1", b"\xa1\xb2\x3c\x4d")
        linktype = struct.unpack_from(e + "I", data, 20)[0]
        off = 24
        while off + 16 <= len(data):
            sec, frac, incl, _ = struct.unpack_from(e + "IIII", data, off)
            off += 16
            yield sec + frac / (1e9 if nano else 1e6), linktype, data[off:off + incl]
            off += incl
    elif magic == b"\x0a\x0d\x0d\x0a":
        e = "<" if data[8:12] == b"\x4d\x3c\x2b\x1a" else ">"
        linktypes, off = [], 0
        while off + 12 <= len(data):
            btype, blen = struct.unpack_from(e + "II", data, off)
            if blen < 12:
                break
            body = data[off + 8: off + blen - 4]
            if btype == 1:  # Interface Description Block
                linktypes.append(struct.unpack_from(e + "H", body, 0)[0])
            elif btype == 6:  # Enhanced Packet Block, assumes default microsecond resolution
                iface, ts_hi, ts_lo, cap = struct.unpack_from(e + "IIII", body, 0)
                yield ((ts_hi << 32) | ts_lo) / 1e6, linktypes[iface], body[20:20 + cap]
            off += blen
    else:
        raise ValueError(f"{path}: not a pcap/pcapng file")


def _strip_radiotap(frame):
    if len(frame) < 4:
        return None
    rt_len = struct.unpack_from("<H", frame, 2)[0]
    return frame[rt_len:]


def _wifi_payloads(frame):
    """Yield (transport, src_mac, counter, pack_bytes) from one 802.11 frame."""
    if len(frame) < MGMT_HDR_LEN:
        return
    fc = struct.unpack_from("<H", frame, 0)[0]
    ftype, subtype = (fc >> 2) & 3, (fc >> 4) & 0xF
    if ftype != FC_TYPE_MGMT:
        return
    src = frame[10:16].hex(":")
    if subtype == SUBTYPE_BEACON:
        off = MGMT_HDR_LEN + BEACON_FIXED_LEN
        while off + 2 <= len(frame):
            eid, elen = frame[off], frame[off + 1]
            body = frame[off + 2: off + 2 + elen]
            if eid == IE_VENDOR:
                r = odid.from_beacon_vendor_ie(body)
                if r:
                    yield "wifi-beacon", src, r[0], r[1]
            off += 2 + elen
    elif subtype == SUBTYPE_ACTION:
        off = MGMT_HDR_LEN
        hdr = frame[off: off + NAN_SDF_HDR_LEN]
        if len(hdr) < NAN_SDF_HDR_LEN or hdr[0] != NAN_ACTION_CATEGORY or hdr[1] != NAN_ACTION_CODE \
                or hdr[2:5] != odid.WIFI_ALLIANCE_OUI or hdr[5] != odid.NAN_OUI_TYPE:
            return
        off += NAN_SDF_HDR_LEN
        while off + 3 <= len(frame):
            alen = struct.unpack_from("<H", frame, off + 1)[0]
            attr = frame[off: off + 3 + alen]
            r = odid.from_nan_sda(attr)
            if r:
                yield "wifi-nan", src, r[0], r[1]
            off += 3 + alen


def _nordic_crc_ok(frame):
    """nRF Sniffer pseudo-header: drop packets the sniffer flagged with a bad CRC."""
    if len(frame) <= NORDIC_FLAGS_OFFSET or frame[3] not in NORDIC_PROTO_VERSIONS:
        return True  # unknown header version: cannot tell, keep
    return bool(frame[NORDIC_FLAGS_OFFSET] & NORDIC_FLAG_CRC_OK)


def _ble_payloads(frame):
    i = 0
    while True:
        i = frame.find(BLE_ODID_SIG, i)
        if i < 1:
            return
        ad_len = frame[i - 1]
        sd = frame[i + 3: i + ad_len]  # service data after the UUID
        if ad_len >= 4 + odid.MESSAGE_SIZE and len(sd) == ad_len - 3:
            r = odid.from_ble_service_data(sd)
            if r:
                yield "ble", None, r[0], r[1]
        i += 1


def extract(path):
    """Yield dicts {t, transport, mac, counter, payload} for every ODID payload in a capture."""
    for t, linktype, frame in read_packets(path):
        if linktype == LINKTYPE_RADIOTAP:
            frame = _strip_radiotap(frame)
            gen = _wifi_payloads(frame) if frame else ()
        elif linktype == LINKTYPE_IEEE802_11:
            gen = _wifi_payloads(frame)
        elif linktype == LINKTYPE_NORDIC_BLE and not _nordic_crc_ok(frame):
            continue
        else:
            gen = _ble_payloads(frame)
        for transport, mac, counter, payload in gen:
            yield {"t": t, "transport": transport, "mac": mac, "counter": counter, "payload": payload}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("capture")
    ap.add_argument("--hex", action="store_true", help="print payload hex only (for the core-c harness)")
    args = ap.parse_args()
    for rec in extract(args.capture):
        if args.hex:
            print(rec["payload"].hex())
            continue
        mtype, uas = odid.decode(rec["payload"])
        print(json.dumps({"t": round(rec["t"], 6), "transport": rec["transport"], "mac": rec["mac"],
                          "counter": rec["counter"], "type": mtype, **odid.summarize(uas)}))


if __name__ == "__main__":
    sys.exit(main())
