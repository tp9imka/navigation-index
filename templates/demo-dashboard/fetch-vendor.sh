#!/bin/sh
# Copies the pinned CDN libraries into vendor/ so the page works with no internet.
# index.html loads the CDN copy first and falls back to vendor/ when it fails.
set -eu
cd "$(dirname "$0")"
mkdir -p vendor
for f in \
  "maplibre-gl@4.7.1/dist/maplibre-gl.js maplibre-gl.js" \
  "maplibre-gl@4.7.1/dist/maplibre-gl.css maplibre-gl.css" \
  "milsymbol@3.0.4/dist/milsymbol.js milsymbol.js" \
  "pmtiles@4.4.1/dist/pmtiles.js pmtiles.js"; do
  set -- $f
  curl -fsSL "https://unpkg.com/$1" -o "vendor/$2"
  echo "vendor/$2"
done
