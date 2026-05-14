#!/bin/bash
set -euo pipefail

echo "Starting ESA BIOMASS DPS job..."

mkdir -p output

python /app/ESA_BIOMASS_DPS_JOB/esa-biomass-dps.py \
  --bbox "${bbox}" \
  --datetime "${datetime}" \
  --resolution "${resolution}" \
#  --out_dir "./output" \
  --out_name "biomass.tiff"

echo "Job completed."
echo "Output files:"
ls -lh output/
