from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml


@lru_cache(maxsize=None)
def _reference_year(source: Path) -> int:
    with (source / "config.yaml").open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}
    return int(config["system"]["reference_year"])


def read_reference_year(source_path: Path | str) -> int:
    """Return ``system.reference_year`` from ``<source_path>/config.yaml``."""
    return _reference_year(Path(source_path).resolve())


def capacities_path(source_path: Path | str, year: int) -> Path:
    """Prefer ``capacities_<year>.csv``; fall back to the full ``capacities.csv``."""
    source = Path(source_path)
    year_specific = source / f"capacities_{year}.csv"
    return year_specific if year_specific.exists() else source / "capacities.csv"


class NamibiaBaseline:
    """Load the split annual Namibia baseline source tables."""

    def __init__(self, source_path: Path | str):
        source = Path(source_path)
        self.reference_year = read_reference_year(source)

        # Prefer a year-isolated capacity table when one exists. Keep the full
        # historical table as the fallback for years without a dedicated file.
        self.capacities = pd.read_csv(capacities_path(source, self.reference_year))
        self.capacities["year"] = pd.to_numeric(
            self.capacities["year"], errors="raise"
        ).astype(int)

        tables = [
            pd.read_csv(source / "capacities.csv"),
            pd.read_csv(source / "imports.csv"),
            pd.read_csv(source / "demands.csv"),
        ]
        self.data = tables[0].merge(tables[1], on="year", validate="one_to_one").merge(
            tables[2], on="year", validate="one_to_one"
        )
        self.data["year"] = pd.to_numeric(self.data["year"], errors="raise").astype(int)

    def capacity_existing(self, column: str) -> float:
        rows = self.capacities.loc[self.capacities.year == self.reference_year, column]
        if rows.empty:
            raise ValueError(
                f"No capacity data found for reference year {self.reference_year} "
                f"in capacities_{self.reference_year}.csv or capacities.csv"
            )
        if len(rows) != 1:
            raise ValueError(
                f"Expected one capacity row for {self.reference_year}; found {len(rows)}"
            )
        return float(rows.iloc[0])


@lru_cache(maxsize=None)
def _load_baseline(source: Path) -> NamibiaBaseline:
    return NamibiaBaseline(source)


def load_baseline(source_path: Path | str) -> NamibiaBaseline:
    """Return a cached NamibiaBaseline so each build reads the CSVs only once.

    Callers must treat the returned tables as read-only.
    """
    return _load_baseline(Path(source_path).resolve())
