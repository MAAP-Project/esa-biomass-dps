#!/usr/bin/env bash
set -euo pipefail

echo "Starting ESA BIOMASS DPS job..."

basedir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
env_name="esa_biomass_dps"
output_path="${basedir}/output/biomass.tif"

mkdir -p "$(dirname "${output_path}")"

conda run --no-capture-output -n "${env_name}" \
  python "${basedir}/run.py" --output-path "${output_path}" "$@"

echo "Job completed."
echo "Output files:"
ls -lh "$(dirname "${output_path}")"
