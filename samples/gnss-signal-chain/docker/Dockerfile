# File-based GNSS signal chain: gps-sdr-sim (IQ generator) + GNSS-SDR (software receiver)
# + RTKLIB demo5 (rnx2rtkp for a clock/position cross-check). Builds natively on arm64 and amd64.
# docker build -t gnss-signal-chain docker/
FROM ubuntu:24.04
ARG DEBIAN_FRONTEND=noninteractive
# gnss-sdr 0.0.19 from Ubuntu noble/universe (arm64 + amd64 binaries, no source build needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
      gnss-sdr build-essential cmake git ca-certificates python3 python3-numpy \
    && rm -rf /var/lib/apt/lists/*
ARG GPS_SDR_SIM_REF=28ca29a6719475195e3aabd5930c4ed02d67190f
RUN git clone https://github.com/osqzss/gps-sdr-sim.git /opt/gps-sdr-sim \
    && cd /opt/gps-sdr-sim && git checkout "$GPS_SDR_SIM_REF" \
    && gcc gpssim.c -lm -O3 -o /usr/local/bin/gps-sdr-sim
RUN git clone --depth 1 --branch v2.5.1 https://github.com/rtklibexplorer/RTKLIB.git /opt/RTKLIB \
    && cmake -S /opt/RTKLIB -B /opt/RTKLIB/build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build /opt/RTKLIB/build --target rnx2rtkp -j"$(nproc)" \
    && ln -s /opt/RTKLIB/bin/rnx2rtkp /usr/local/bin/rnx2rtkp
WORKDIR /work
# h5py reads GNSS-SDR's MATLAB v7.3 (HDF5) PVT dump
RUN apt-get update && apt-get install -y --no-install-recommends python3-h5py \
    && rm -rf /var/lib/apt/lists/*
