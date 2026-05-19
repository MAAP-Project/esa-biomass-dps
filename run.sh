#!/usr/bin/env bash
set -euo pipefail

echo "Starting ESA BIOMASS DPS job..."

basedir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
env_name="esa_biomass_dps"
output_dir="${PWD}/output"
output_path="${output_dir}/biomass.tif"

mkdir -p "${output_dir}"

conda run --no-capture-output -n "${env_name}" \
  python "${basedir}/run.py" --output-path "${output_path}" "$@"

echo "Job completed."
echo "Output files:"
ls -lh "${output_dir}"
