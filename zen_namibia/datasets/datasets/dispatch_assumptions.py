from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from zen_creator import Attribute


class DispatchAssumptions:
    """Read documented minimum dispatch assumptions for the 2023 snapshot."""

    def __init__(self, source_path: Path | str):
        self.path = Path(source_path) / "dispatch_assumptions_2023.csv"
        self.data = pd.read_csv(self.path)
        required = {"technology", "assumption_type", "assumption_value"}
        missing = required.difference(self.data.columns)
        if missing:
            raise ValueError(
                "dispatch_assumptions_2023.csv is missing columns: "
                + ", ".join(sorted(missing))
            )
        if self.data["technology"].duplicated().any():
            raise ValueError("dispatch_assumptions_2023.csv has duplicate technologies")
        if self.data[list(required)].isna().any().any():
            raise ValueError("dispatch_assumptions_2023.csv contains blank values")

    def _row(self, technology: str) -> pd.Series:
        rows = self.data.loc[self.data.technology == technology]
        if len(rows) != 1:
            raise ValueError(
                f"Expected one dispatch assumption for {technology}; found {len(rows)}"
            )
        return rows.iloc[0]

    def minimum_full_load_hours_fraction(
        self, technology: str, available_capacity_factor: float | None = None
    ) -> float:
        """Return a ZEN-garden annual minimum full-load-hours fraction.

        ``capacity_fraction`` values are fractions of installed capacity-hours.
        ``available_output_share`` values are multiplied by the renewable
        capacity factor, so the minimum remains below the time-series max_load.
        """
        row = self._row(technology)
        value = float(row["assumption_value"])
        if not 0 <= value <= 1:
            raise ValueError(f"Dispatch assumption for {technology} must be in [0, 1]")

        assumption_type = str(row["assumption_type"])
        if assumption_type in {"capacity_fraction", "peak_hours_fraction"}:
            return value
        if assumption_type == "available_output_share":
            if available_capacity_factor is None:
                raise ValueError(
                    f"{technology} needs an available capacity factor for its dispatch assumption"
                )
            if not 0 <= available_capacity_factor <= 1:
                raise ValueError(
                    f"Available capacity factor for {technology} must be in [0, 1]"
                )
            return value * available_capacity_factor
        raise ValueError(
            f"Unknown assumption_type {assumption_type!r} for {technology}"
        )

    def minimum_dispatch_attribute(
        self,
        element,
        available_capacity_factor: float | None = None,
    ) -> Attribute:
        """Build the shared ZEN-garden attribute used by dispatchable plants."""
        fraction = self.minimum_full_load_hours_fraction(
            element.name, available_capacity_factor
        )
        return Attribute(
            "min_full_load_hours_fraction",
            default_value=fraction,
            unit="1",
            element=element,
        )

    def peak_hours(self, technology: str, total_hours: int = 8760) -> int:
        """Return the assumed number of peak-load dispatch hours."""
        row = self._row(technology)
        if str(row["assumption_type"]) != "peak_hours_fraction":
            raise ValueError(f"{technology} has no peak-hours dispatch assumption")
        fraction = float(row["assumption_value"])
        if not 0 < fraction <= 1:
            raise ValueError(f"Peak-hours fraction for {technology} must be in (0, 1]")
        return int(round(fraction * total_hours))


@lru_cache(maxsize=None)
def _load_dispatch_assumptions(source: Path) -> DispatchAssumptions:
    return DispatchAssumptions(source)


def load_dispatch_assumptions(source_path: Path | str) -> DispatchAssumptions:
    """Return cached dispatch assumptions (read-only) for this source folder."""
    return _load_dispatch_assumptions(Path(source_path).resolve())
