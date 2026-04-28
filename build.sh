#!/bin/bash
set -e

echo "Installing ESA BIOMASS DPS dependencies"

pip install --no-cache-dir \
    requests \
    pystac-client \
    rasterio \
    odc-stac \
    odc-geo \
    rioxarray \
    xarray \
    boto3

echo "Build complete"
