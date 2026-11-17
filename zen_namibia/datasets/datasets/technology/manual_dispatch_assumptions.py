from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Attribute, Dataset, Element, MetaData
from zen_creator.utils.attribute import SourceInformation

ASSUMPTION_TYPES = {"capacity_fraction", "peak_hours_fraction"}


class ManualDispatchAssumptions(Dataset[pd.DataFrame]):
    """Own assumptions on how the dispatchable 2023 plants are operated.

    Each row gives one technology's annual minimum output as a fraction of its
    capacity-hours. ``peak_hours_fraction`` rows also limit the plant to that
    share of the highest-demand hours.
    """

    name = "manual_dispatch_assumptions"

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Namibia 2023 dispatch assumptions for coal, diesel and hydro",
            author=["ZEN Namibia"],
            publication="ZEN Namibia",
            publication_year=2026,
            note="modeling assumptions, not recorded plant dispatch",
        )

    def _set_path(self) -> Path:
        return (
            self.source_path / "03-technology" / "manual_dispatch_assumptions"
            / "dispatch_assumptions_2023.csv"
        )

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        required = ["technology", "assumption_type", "assumption_value"]
        missing = set(required).difference(data.columns)
        if missing:
            raise ValueError(
                "dispatch_assumptions_2023.csv is missing columns: "
                + ", ".join(sorted(missing))
            )
        if data[required].isna().any().any():
            raise ValueError("dispatch_assumptions_2023.csv contains blank values")
        if data["technology"].duplicated().any():
            raise ValueError("dispatch_assumptions_2023.csv has duplicate technologies")
        unknown = set(data["assumption_type"]).difference(ASSUMPTION_TYPES)
        if unknown:
            raise ValueError(f"Unknown assumption_type values: {', '.join(sorted(unknown))}")
        data["assumption_value"] = pd.to_numeric(data["assumption_value"], errors="raise")
        if not data["assumption_value"].between(0, 1).all():
            raise ValueError("Dispatch assumption values must be fractions from 0 to 1")
        return data.set_index("technology")

    def _row(self, technology: str) -> pd.Series:
        if technology not in self.data.index:
            raise ValueError(f"No dispatch assumption for {technology}")
        return self.data.loc[technology]

    def get_min_full_load_hours_fraction(self, element: Element) -> Attribute:
        """Return the annual minimum output as a fraction of capacity-hours."""
        row = self._row(element.name)
        return Attribute(
            "min_full_load_hours_fraction",
            default_value=float(row["assumption_value"]),
            unit="1",
            element=element,
            sources=[
                SourceInformation(
                    description=str(row.get("description", "")),
                    metadata=self.metadata,
                )
            ],
        )

    def peak_hours(self, technology: str, total_hours: int) -> int:
        """Return the number of highest-demand hours the plant may run in."""
        row = self._row(technology)
        if row["assumption_type"] != "peak_hours_fraction":
            raise ValueError(f"{technology} has no peak-hours dispatch assumption")
        if float(row["assumption_value"]) <= 0:
            raise ValueError(f"Peak-hours fraction for {technology} must be positive")
        return int(round(float(row["assumption_value"]) * total_hours))
