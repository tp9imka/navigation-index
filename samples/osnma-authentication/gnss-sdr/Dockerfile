# GNSS-SDR 0.0.20 (Debian trixie package) + OSNMA-SDR-SIM built from a pinned commit.
# GCC 14 needs the forced <bitset> include (the sources rely on it being pulled in transitively).
# File output only: run_sim.sh forces usrp=1 (no transmission). Never set usrp=0.
FROM debian:trixie
ARG SIM_COMMIT=e0b80759e9343257efedb2ecdd3bca4f04001a5e
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
      gnss-sdr libuhd-dev g++ cmake make pkg-config libncurses-dev libcurl4-openssl-dev zlib1g-dev \
      libboost-dev libboost-thread-dev libboost-system-dev libboost-program-options-dev libglib2.0-dev \
      git ca-certificates python3 \
 && rm -rf /var/lib/apt/lists/*
RUN git clone https://github.com/Haiyang-Wong/OSNMA-SDR-SIM.git /sim && cd /sim && git checkout ${SIM_COMMIT} \
 && mkdir build && cd build \
 && cmake -DCMAKE_CXX_FLAGS="-include bitset" .. && make -j"$(nproc)"
WORKDIR /work
