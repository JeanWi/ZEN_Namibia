from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from zen_creator import Dataset, MetaData

DEMAND_COLUMNS = [
    "year",
    "average_demand_mw",
    "energy_consumption_gwh",
    "peak_demand_mw",
]


def nampower_metadata(name: str) -> MetaData:
    """Return the citation shared by all NamPower datasets."""
    return MetaData(
        name=name,
        title="NamPower annual reports and statistics 2019-2025",
        author=["NamPower"],
        publication="NamPower Annual Reports",
        publication_year=2025,
        note="compiled in the ZEN Namibia baseline workbook",
    )


class NamPowerCosts(Dataset[pd.DataFrame]):
    """Source table of 2023 fuel and electricity trade price assumptions."""

    name = "nampower_costs"

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Namibia 2023 fuel and electricity trade price inputs",
            author=["NamPower", "Bank of Namibia", "ZEN Namibia"],
            publication="NamPower annual reports and Bank of Namibia bulletin",
            publication_year=2024,
            note="Published values and documented conversion assumptions",
        )

    def _set_path(self) -> Path:
        return self.source_path / "02-carrier" / "nampower" / "costs_2023.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        required = {"item", "value", "unit", "source"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(
                "costs_2023.csv is missing columns: " + ", ".join(sorted(missing))
            )
        if data["item"].duplicated().any():
            raise ValueError("costs_2023.csv has duplicate items")
        data["value"] = pd.to_numeric(data["value"], errors="raise")
        if data.isna().any().any() or (data["value"] <= 0).any():
            raise ValueError("costs_2023.csv contains blank or non-positive values")
        return data

    def value(self, item: str) -> float:
        rows = self.data.loc[self.data.item == item, "value"]
        if len(rows) != 1:
            raise ValueError(f"Expected one costs_2023.csv row for {item}; found {len(rows)}")
        return float(rows.iloc[0])

    def to_euro(self, nad: float) -> float:
        return nad / self.value("exchange_rate")

    def electricity_price(self, direction: str) -> float:
        return self.to_euro(self.value(f"electricity_{direction}_price"))

    def coal_price(self) -> float:
        # Fuel MWh per tonne from the NIRP heat rate and coal use.
        fuel_mwh_per_tonne = (15.81 / 3.6) / (580.0 / 1000.0)
        return self.to_euro(self.value("coal_price") / fuel_mwh_per_tonne)

    def anixas_hfo_price(self) -> float:
        """Convert the NIRP 2020 HFO benchmark to Euro/MWh of fuel."""
        return self.to_euro(self.value("anixas_hfo_price_2020") * 3.6)

    def nirp_to_2023(self) -> float:
        """CPI factor from the NIRP's 2020 price basis to 2023 prices."""
        return self.value("cpi_2023") / self.value("cpi_2020")

    def variable_om(self, item: str) -> float:
        """Convert NIRP N$/kWh (2020 prices) to 2023 Euro/MWh of electricity."""
        return self.to_euro(self.value(item) * 1000.0 * self.nirp_to_2023())

    def fixed_om(self, item: str) -> float:
        """Convert NIRP N$/kW/year (2020 prices) to 2023 Euro/MW/year."""
        return self.to_euro(self.value(item) * 1000.0 * self.nirp_to_2023())

@lru_cache(maxsize=None)
def load_costs(source_path: Path | str) -> NamPowerCosts:
    """Load and cache the NamPower 2023 cost inputs for a source folder."""
    return NamPowerCosts(source_path)


class NamPowerDemand(Dataset[pd.DataFrame]):
    """NamPower annual electricity demand 2019-2025.

    The files are in ``02-carrier/nampower/``. ``imports_exports.csv`` is kept
    there as well but is not used by the model at the moment.
    """

    name = "nampower_demand"

    def _set_metadata(self) -> MetaData:
        return nampower_metadata(self.name)

    def _set_path(self) -> Path:
        return self.source_path / "02-carrier" / "nampower" / "demand.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        missing = set(DEMAND_COLUMNS).difference(data.columns)
        if missing:
            raise ValueError(
                "demand.csv must include year, average_demand_mw, "
                "energy_consumption_gwh, and peak_demand_mw; "
                f"missing: {', '.join(sorted(missing))}"
            )
        data = data[DEMAND_COLUMNS].copy()
        data["node"] = "NAM"
        data = data.rename(columns={"average_demand_mw": "demand_mw"})
        data["year"] = pd.to_numeric(data["year"], errors="raise").astype(int)
        for column in ["demand_mw", "energy_consumption_gwh", "peak_demand_mw"]:
            data[column] = pd.to_numeric(data[column], errors="raise")
        if data.isna().any().any():
            raise ValueError("demand.csv contains blank values")
        if data.duplicated(["year", "node"]).any():
            raise ValueError("demand.csv has duplicate year,node rows")
        if (data["demand_mw"] < 0).any():
            raise ValueError("demand_mw values must be non-negative")
        return data

    def demand_in(self, year: int) -> pd.Series:
        """Return the row of demand.csv for one year."""
        rows = self.data.loc[self.data.year == year]
        if rows.empty:
            raise ValueError(f"No demand data for {year} in demand.csv")
        return rows.iloc[0]
