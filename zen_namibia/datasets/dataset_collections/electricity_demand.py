from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from zen_creator import Attribute, Dataset, DatasetCollection, Element
from zen_creator.utils.attribute import SourceInformation

from zen_namibia.datasets.datasets.carrier.nampower import NamPowerDemand
from zen_namibia.datasets.datasets.carrier.pypsa import STEPS_PER_YEAR, PyPSA


class ElectricityDemand(DatasetCollection):
    """Hourly demand: the PyPSA shape scaled to NamPower's annual energy and peak."""

    name = "electricity_demand"

    def __init__(self, source_path: Path | str):
        super().__init__(source_path=source_path)

    def _get_data(self) -> dict[str, Dataset[Any] | DatasetCollection]:
        return {
            "nampower_demand": NamPowerDemand(self.source_path),
            "pypsa": PyPSA(self.source_path),
        }

    def _profile_for_year(self, year: int) -> pd.DataFrame:
        """Scale the PyPSA data to NamPower's data."""
        row = self.data["nampower_demand"].demand_in(year)
        average_demand_mw = float(row["demand_mw"])
        energy_consumption_gwh = float(row["energy_consumption_gwh"])
        peak_demand_mw = float(row["peak_demand_mw"])

        pypsa = self.data["pypsa"]
        if year != pypsa.profile_year:
            return pd.DataFrame(
                {"NAM": np.full(STEPS_PER_YEAR, average_demand_mw)},
                index=pd.RangeIndex(STEPS_PER_YEAR, name="time"),
            )

        demand = pypsa.data["demand_mw"].astype(float).copy()
        # The source stores missing hours as 0 MW (22:00 and 23:00 on 31 Dec).
        # Fill each with the same hour on the previous day.
        missing = np.flatnonzero(demand.to_numpy() == 0)
        if (missing < 24).any():
            raise ValueError("Cannot fill zero demand in the first day of the year")
        for hour in missing:
            demand.iloc[hour] = demand.iloc[hour - 24]
        if demand.eq(0).any():
            raise ValueError(f"{year} hourly demand still contains zero hours after filling")
        source_mean = float(demand.mean())
        source_peak = float(demand.max())
        target_mean = energy_consumption_gwh * 1000 / STEPS_PER_YEAR
        if source_peak <= source_mean:
            raise ValueError(
                f"{year} hourly demand must have a peak above its annual mean"
            )
        spread_scale = (peak_demand_mw - target_mean) / (source_peak - source_mean)
        demand = (demand - source_mean) * spread_scale + target_mean
        if (demand < 0).any():
            raise ValueError(
                f"Calibrating {year} demand to NamPower energy and peak produced "
                "negative values"
            )
        return pd.DataFrame(
            {"NAM": demand.to_numpy()},
            index=pd.RangeIndex(STEPS_PER_YEAR, name="time"),
        )

    def get_demand(self, element: Element) -> Attribute:
        """Create the 8760-hour demand profile for the configured reference year."""
        reference_year = element.config.system.reference_year
        profile_year = self.data["pypsa"].profile_year
        attr = Attribute("demand", element=element)
        attr.set_data(
            default_value=0.0,
            unit=element.power_unit,
            df=self._profile_for_year(reference_year),
            source=SourceInformation(
                description=(
                    "Hourly electricity demand profile for reference year "
                    f"{reference_year}; PyPSA hourly shape calibrated to NamPower "
                    f"annual energy and peak for {profile_year}, flat annual "
                    "average otherwise."
                ),
                metadata=self.metadata,
            ),
        )
        return attr
