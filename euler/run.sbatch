#!/bin/bash
# Build the dataset and solve the model on Euler.
# Submit from the repository root:  sbatch euler/run.sbatch
#SBATCH --job-name=zen_namibia
#SBATCH --time=24:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=8G
#SBATCH --output=euler/logs/%x_%j.out

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

source euler/modules.sh
source "$HOME/venvs/zen_namibia/bin/activate"

echo "Job $SLURM_JOB_ID on $(hostname), $SLURM_CPUS_PER_TASK cores, commit $(git rev-parse --short HEAD)"
python create_model.py
python run_zen_garden.py
echo "Done. Results in outputs_dispatch_2023/"
