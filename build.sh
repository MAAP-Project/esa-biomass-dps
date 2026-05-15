#!/bin/bash
set -e

echo "Installing ESA BIOMASS DPS dependencies"

chmod +x /app/esa-biomass-dps/run.sh

pip install --no-cache-dir \
    requests \
    pystac-client \
    rasterio \
    odc-stac \
    odc-geo \
    rioxarray \
    xarray \
    boto3 \
    maap-py \
    bottleneck

echo "Build complete"
