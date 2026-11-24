#!/bin/bash
# Euler modules used by setup_env.sh and run.sbatch.
# Check the available versions with:  module avail python  /  module avail gurobi
# and adjust the three lines below if these are not listed.
module load stack/2024-06 python/3.12.8 gurobi/12.0.0
GUROBI_PY_VERSION="12.0.0"
