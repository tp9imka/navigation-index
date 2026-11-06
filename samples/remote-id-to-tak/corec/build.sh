#!/bin/sh
# Build the core-c reference harness. Usage: ./build.sh [path-to-opendroneid-core-c]
# Without an argument it shallow-clones upstream into ./opendroneid-core-c (git-ignored).
set -eu
cd "$(dirname "$0")"
SRC="${1:-opendroneid-core-c}"
if [ ! -d "$SRC" ]; then
  git clone --depth 1 https://github.com/opendroneid/opendroneid-core-c "$SRC"
fi
cc -std=c99 -O1 -Wall -I"$SRC/libopendroneid" "$SRC/libopendroneid/opendroneid.c" odid_vectors.c -lm -o odid_vectors
echo "built $(pwd)/odid_vectors against $(git -C "$SRC" rev-parse HEAD 2>/dev/null || echo "$SRC")"
