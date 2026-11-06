"""Read single members out of a remote ZIP with HTTP range requests (stdlib only).

The Thermal-UAV bundle is one 19.9 GB ZIP. Its central directory sits at the end, so a
seekable file object backed by Range requests lets zipfile list and extract a few members
without downloading the archive.
"""
import io
import urllib.request

BLOCK = 1 << 20


class HttpRangeFile(io.RawIOBase):
    def __init__(self, url, block=BLOCK):
        self.url = url
        self.block = block
        self.pos = 0
        self.cache = {}
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req) as r:
            self.url = r.geturl()
            self.size = int(r.headers["Content-Length"])
        self.bytes_fetched = 0

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, off, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.pos = off
        elif whence == io.SEEK_CUR:
            self.pos += off
        else:
            self.pos = self.size + off
        return self.pos

    def _range(self, start, end):
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end - 1}"})
        with urllib.request.urlopen(req) as r:
            data = r.read()
        self.bytes_fetched += len(data)
        return data

    def read(self, n=-1):
        if n is None or n < 0:
            n = self.size - self.pos
        n = max(0, min(n, self.size - self.pos))
        if n == 0:
            return b""
        if n > 4 * self.block:
            data = self._range(self.pos, self.pos + n)
            self.pos += n
            return data
        out = bytearray()
        while n > 0:
            b = self.pos // self.block
            if b not in self.cache:
                if len(self.cache) > 64:
                    self.cache.clear()
                s = b * self.block
                self.cache[b] = self._range(s, min(s + self.block, self.size))
            chunk = self.cache[b]
            o = self.pos - b * self.block
            take = chunk[o:o + n]
            out += take
            self.pos += len(take)
            n -= len(take)
        return bytes(out)

    def readinto(self, buf):
        data = self.read(len(buf))
        buf[:len(data)] = data
        return len(data)
