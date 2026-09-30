#!/usr/bin/env bash
set -euo pipefail
# Run from the repository root. Compile every top-level entrypoint, including
# the ML, Grafana, monitoring and recovery templates omitted by the old CI loop.
destination="${1:?A temporary output directory is required}"
mkdir -p "$destination"
for template in infra/*.bicep; do
  az bicep build --file "$template" --outfile "$destination/$(basename "$template" .bicep).json"
done
python infra/azure/check_ml_security.py "$destination/ml-workspace.json" --compiled-directory "$destination"
