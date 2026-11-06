"""Minimal stdlib reader for MATLAB v5 .mat files: real numeric 2-D arrays only."""
import struct
import zlib

HEADER_BYTES = 128
MI_MATRIX = 14
MI_COMPRESSED = 15
NUMERIC = {1: "b", 2: "B", 3: "h", 4: "H", 5: "i", 6: "I", 7: "f", 9: "d", 12: "q", 13: "Q"}


def _tag(buf, off, en):
    t, n = struct.unpack_from(en + "II", buf, off)
    if t >> 16:  # small data element: 2-byte size, 2-byte type, data in the next 4 bytes
        return t & 0xFFFF, t >> 16, off + 4, off + 8
    end = off + 8 + n
    return t, n, off + 8, end + (-end % 8)


def _matrix(buf, off, end, en):
    out = {}
    fields = []
    while off < end:
        t, n, start, off = _tag(buf, off, en)
        fields.append((t, buf[start:start + n]))
    flags, dims, name = fields[0][1], fields[1][1], fields[2][1]
    if len(fields) < 4 or fields[3][0] not in NUMERIC or struct.unpack_from(en + "I", flags)[0] & 0x800:
        return out  # struct, cell, char, sparse or complex: not needed here
    shape = struct.unpack(en + "%di" % (len(dims) // 4), dims)
    t, raw = fields[3]
    fmt = NUMERIC[t]
    vals = struct.unpack(en + "%d%s" % (len(raw) // struct.calcsize(fmt), fmt), raw)
    rows, cols = shape[0], (len(vals) // shape[0] if shape[0] else 0)
    out[name.decode()] = [[vals[c * rows + r] for c in range(cols)] for r in range(rows)]
    return out


def _elements(buf, off, en):
    out = {}
    while off + 8 <= len(buf):
        t, n, start, nxt = _tag(buf, off, en)
        if t == MI_COMPRESSED:
            out.update(_elements(zlib.decompress(buf[start:start + n]), 0, en))
        elif t == MI_MATRIX:
            out.update(_matrix(buf, start, start + n, en))
        off = nxt
    return out


def loadmat(path):
    """Return {name: list of rows} for every real numeric matrix in a v5 .mat file."""
    with open(path, "rb") as f:
        buf = f.read()
    en = "<" if buf[126:128] == b"IM" else ">"
    return _elements(buf, HEADER_BYTES, en)
