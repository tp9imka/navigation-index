"""Minimal CoT sink standing in for a TAK server input: prints each <event> it receives.

  python3 cot_sink.py --port 18087 --count 5          # TCP, like a TAK server's 8087 input
  python3 cot_sink.py --udp --port 16969 --count 5    # UDP datagrams
"""
import argparse
import socket
import xml.etree.ElementTree as ET


def describe(raw: bytes, n: int):
    ev = ET.fromstring(raw)
    pt, trk = ev.find("point"), ev.find("detail/track")
    if trk is None:  # PyTAK's own keepalive events carry no track
        print(f"other: uid={ev.get('uid')} type={ev.get('type')}")
        return False
    print(f"cot {n}: uid={ev.get('uid')} type={ev.get('type')} "
          f"lat={pt.get('lat')} lon={pt.get('lon')} hae={pt.get('hae')} "
          f"course={trk.get('course')} speed={trk.get('speed')} "
          f"time={ev.get('time')} stale={ev.get('stale')}")
    if n == 1:
        print(raw.decode())
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=18087)
    ap.add_argument("--count", type=int, default=5)
    ap.add_argument("--udp", action="store_true")
    args = ap.parse_args()
    if args.udp:
        conn = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        conn.bind((args.host, args.port))
        recv = lambda: conn.recvfrom(65536)[0]
    else:
        srv = socket.create_server((args.host, args.port))
        conn, _ = srv.accept()
        recv = lambda: conn.recv(65536)
    buf, seen = b"", 0
    with conn:
        while seen < args.count:
            chunk = recv()
            if not chunk:
                break
            buf += chunk
            while b"</event>" in buf and seen < args.count:
                raw, buf = buf.split(b"</event>", 1)
                raw = raw[raw.find(b"<event"):] + b"</event>"
                if describe(raw, seen + 1):
                    seen += 1
    print(f"sink: received {seen} track CoT events over {'udp' if args.udp else 'tcp'}")


if __name__ == "__main__":
    main()
