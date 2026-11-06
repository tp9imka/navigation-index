# RTKLIB demo5 (rtklibexplorer v2.5.1) rnx2rtkp + convbin, plus crx2rnx from the `hatanaka` wheel.
# docker build -t rtklib-demo5 docker/
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential cmake git ca-certificates python3 python3-venv gzip \
    && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch v2.5.1 https://github.com/rtklibexplorer/RTKLIB.git /opt/RTKLIB \
    && cmake -S /opt/RTKLIB -B /opt/RTKLIB/build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /opt/RTKLIB/build --target rnx2rtkp convbin -j"$(nproc)"
RUN python3 -m venv /opt/py && /opt/py/bin/pip install --no-cache-dir hatanaka==2.8.0
RUN set -e; for b in rnx2rtkp convbin; do \
      f=$(find /opt/RTKLIB -type f -name "$b" -perm -u+x | head -1); ln -s "$f" /usr/local/bin/$b; done; \
    ln -s /opt/py/bin/crx2rnx /usr/local/bin/crx2rnx
WORKDIR /work
