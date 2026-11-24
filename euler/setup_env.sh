#!/bin/bash
# One-time setup on Euler: Python environment with ZEN-garden and zen-creator.
# Run from the repository root on a login node:  bash euler/setup_env.sh
set -euo pipefail

source "$(dirname "$0")/modules.sh"

ENV_DIR="$HOME/venvs/zen_namibia"
python -m venv "$ENV_DIR"
source "$ENV_DIR/bin/activate"
pip install --upgrade pip
# Same versions as the local Windows environment.
pip install "zen_garden==3.1.1" "zen_creator==2.1.0"
# gurobipy must not be newer than the Gurobi module's license server
# (see modules.sh); pip may have pulled a newer one with zen_garden.
pip install "gurobipy==${GUROBI_PY_VERSION}"

python -c "import zen_garden, zen_creator, gurobipy; print('gurobipy', gurobipy.gurobi.version())"
echo "Environment ready: $ENV_DIR"
