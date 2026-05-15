#!/bin/bash
set -euo pipefail

echo "Starting ESA BIOMASS DPS job..."

mkdir -p output

python /app/ESA_BIOMASS_DPS_JOB/esa-biomass-dps.py "$@"

echo "Job completed."
echo "Output files:"
ls -lh output/
