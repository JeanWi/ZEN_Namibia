from pathlib import Path

# Note: "zen-namibia" (hyphen) is the built ZEN-garden dataset, not to be confused
# with the "zen_namibia" (underscore) python package that builds it.
PROJECT_DIR = Path(__file__).resolve().parent
INPUT_DATA_PATH = PROJECT_DIR / "zen_namibia_dataset_dispatch_2023"
