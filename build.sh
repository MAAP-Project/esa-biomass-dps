#!/usr/bin/env bash
set -euo pipefail

basedir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
env_name="esa_biomass_dps"

if command -v mamba >/dev/null 2>&1; then
  conda_cmd="mamba"
else
  conda_cmd="conda"
fi

echo "Installing ${env_name} from ${basedir}/environment.yml using ${conda_cmd}"

if conda env list | awk '{print $1}' | grep -qx "${env_name}"; then
  "${conda_cmd}" env update -n "${env_name}" -f "${basedir}/environment.yml" --prune -y
else
  "${conda_cmd}" env create -f "${basedir}/environment.yml" -y
fi

chmod +x "${basedir}/run.sh"

echo "Build complete"
