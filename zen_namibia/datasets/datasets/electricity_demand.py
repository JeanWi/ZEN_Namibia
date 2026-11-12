from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from zen_creator import Attribute, Dataset, Element, MetaData, SourceInformation
from zen_namibia.datasets.datasets.namibia_baseline import read_reference_year


class ElectricityDemand(Dataset[pd.DataFrame]):
    """Load annual demand and use the supplied 2023 hourly profile."""

    name = "electricity_demand"
    hourly_profile_year = 2023
    steps_per_year = 8760

    def __init__(self, source_path: Path | str | None = None):
        self.hourly_profile: pd.DataFrame | None = None
        super().__init__(source_path=source_path)

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Electricity demand for Namibia",
            author=["ZEN Namibia"],
            publication="ZEN Namibia",
            publication_year=2026,
        )

    def _set_path(self) -> Path:
        return self.source_path / "demands.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        required = {"year", "average_demand_mw", "energy_consumption_gwh", "peak_demand_mw"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(
                "demands.csv must include year, average_demand_mw, energy_consumption_gwh, and peak_demand_mw; "
                f"missing: {', '.join(sorted(missing))}"
            )
        data = data[["year", "average_demand_mw", "energy_consumption_gwh", "peak_demand_mw"]].copy()
        data["node"] = "NAM"
        data = data.rename(columns={"average_demand_mw": "demand_mw"})
        data["year"] = pd.to_numeric(data["year"], errors="raise").astype(int)
        data["demand_mw"] = pd.to_numeric(data["demand_mw"], errors="raise")
        data["energy_consumption_gwh"] = pd.to_numeric(
            data["energy_consumption_gwh"], errors="raise"
        )
        data["peak_demand_mw"] = pd.to_numeric(data["peak_demand_mw"], errors="raise")
        if data[["year", "node", "demand_mw", "energy_consumption_gwh", "peak_demand_mw"]].isna().any().any():
            raise ValueError("demands.csv contains blank values")
        if data.duplicated(["year", "node"]).any():
            raise ValueError("demands.csv has duplicate year,node rows")
        if (data["demand_mw"] < 0).any():
            raise ValueError("demand_mw values must be non-negative")

        hourly_path = self.source_path / "hourly_demand_2023.csv"
        hourly = pd.read_csv(hourly_path, parse_dates=["time"])
        if set(hourly.columns) != {"time", "demand_mw"}:
            raise ValueError("hourly_demand_2023.csv must contain time,demand_mw")
        hourly["demand_mw"] = pd.to_numeric(hourly["demand_mw"], errors="raise")
        expected_time = pd.date_range("2023-01-01 00:00:00", periods=self.steps_per_year, freq="h")
        if len(hourly) != self.steps_per_year or not hourly["time"].equals(pd.Series(expected_time)):
            raise ValueError("2023 hourly demand must contain every hour from Jan 1 00:00 through Dec 31 23:00 exactly once")
        if hourly["demand_mw"].isna().any() or not np.isfinite(hourly["demand_mw"]).all():
            raise ValueError("hourly_demand_2023.csv contains missing or non-finite demand")
        if (hourly["demand_mw"] < 0).any():
            raise ValueError("hourly demand values must be non-negative")
        self.hourly_profile = hourly[["demand_mw"]].copy()
        self.hourly_profile.index = pd.RangeIndex(self.steps_per_year, name="time")

        years_in_model = set(range(int(data.year.min()), int(data.year.max()) + 1))
        if self.hourly_profile_year not in years_in_model:
            raise ValueError("demands.csv must include year 2023 for the hourly profile")
        return data

    def _demand_by_year(self) -> pd.DataFrame:
        return self.data.pivot(index="year", columns="node", values="demand_mw")

    def _profile_for_year(
        self,
        year: int,
        average_demand_mw: float,
        energy_consumption_gwh: float,
        peak_demand_mw: float,
    ) -> pd.DataFrame:
        if year == self.hourly_profile_year:
            demand = self.hourly_profile["demand_mw"].astype(float).copy()
            # Fill the two known zero rows by interpolating across the year boundary.
            if demand.iloc[-2:].eq(0).all():
                last_valid, first = demand.iloc[-3], demand.iloc[0]
                demand.iloc[-2] = last_valid + (first - last_valid) / 3
                demand.iloc[-1] = last_valid + 2 * (first - last_valid) / 3
            source_mean = float(demand.mean())
            source_peak = float(demand.max())
            target_mean = energy_consumption_gwh * 1000 / self.steps_per_year
            if source_peak <= source_mean:
                raise ValueError("2023 hourly demand must have a peak above its annual mean")
            spread_scale = (peak_demand_mw - target_mean) / (source_peak - source_mean)
            demand = (demand - source_mean) * spread_scale + target_mean
            if (demand < 0).any():
                raise ValueError("Calibrating 2023 demand to NamPower energy and peak produced negative values")
            return pd.DataFrame(
                {"NAM": demand.to_numpy()},
                index=pd.RangeIndex(self.steps_per_year, name="time"),
            )
        return pd.DataFrame(
            {"NAM": np.full(self.steps_per_year, float(average_demand_mw))},
            index=pd.RangeIndex(self.steps_per_year, name="time"),
        )

    def get_demand(self, element: Element) -> Attribute:
        """Create the default 8760-hour profile for the configured reference year."""
        demand_by_year = self._demand_by_year()
        reference_year = read_reference_year(self.source_path)
        if reference_year not in demand_by_year.index:
            raise ValueError(
                f"demands.csv has no row for reference year {reference_year}"
            )
        average = float(demand_by_year.loc[reference_year, "NAM"])
        energy = float(
            self.data.loc[
                self.data.year == reference_year, "energy_consumption_gwh"
            ].iloc[0]
        )
        peak = float(
            self.data.loc[self.data.year == reference_year, "peak_demand_mw"].iloc[0]
        )
        attr = Attribute("demand", element=element)
        attr.set_data(
            default_value=0.0,
            unit=element.power_unit,
            df=self._profile_for_year(reference_year, average, energy, peak),
            source=SourceInformation(
                description=(
                    f"Hourly electricity demand profile for reference year {reference_year}; "
                    f"PyPSA hourly shape calibrated to NamPower annual energy and peak for {self.hourly_profile_year}, "
                    "flat annual average otherwise."
                ),
                metadata=self.metadata,
            ),
        )
        return attr

    def get_year_specific_demand(self) -> dict[int, pd.DataFrame]:
        """Return an 8760-step profile for each modeled year."""
        demand_by_year = self._demand_by_year()
        return {
            int(year): self._profile_for_year(
                int(year),
                float(values["NAM"]),
                float(
                    self.data.loc[
                        self.data.year == year, "energy_consumption_gwh"
                    ].iloc[0]
                ),
                float(
                    self.data.loc[self.data.year == year, "peak_demand_mw"].iloc[0]
                ),
            )
            for year, values in demand_by_year.iterrows()
        }
