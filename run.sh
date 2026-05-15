#!/bin/bash
set -euo pipefail

echo "Starting ESA BIOMASS DPS job..."

mkdir -p output

basedir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"

python "${basedir}/esa-biomass-dps.py" "$@"

echo "Job completed."
echo "Output files:"
ls -lh output/
