from pathlib import Path

import yaml
from zen_garden import run

from global_vars import INPUT_DATA_PATH

PROJECT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = PROJECT_DIR / "config_dispatch_2023.yaml"

CONFIG = {
    "analysis": {
        "dataset": str(INPUT_DATA_PATH),
        "objective": "total_cost",
        "sense": "min",
        "folder_output": str(PROJECT_DIR / "outputs_dispatch_2023"),
    },
    "solver": {
        "name": "gurobi",
    },
}


def run_zen_garden():
    CONFIG_PATH.write_text(yaml.safe_dump(CONFIG, sort_keys=False), encoding="utf-8")
    run(config=CONFIG_PATH)


if __name__ == "__main__":
    run_zen_garden()
