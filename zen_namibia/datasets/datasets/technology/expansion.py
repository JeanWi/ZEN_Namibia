from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from zen_creator import Dataset, MetaData

from zen_namibia.datasets.datasets.carrier.nampower import load_costs


def _folder(source_path: Path) -> Path:
    return Path(source_path) / "03-technology" / "expansion"


def _workbook_metadata(name: str, note: str) -> MetaData:
    return MetaData(
        name=name,
        title="Namibia Power Plants 2023 & Expansion Pipeline",
        author=["ZEN Namibia", "NamPower"],
        publication="Project workbook compiled from NamPower Integrated Annual Reports 2022-2025 and the ECB licence register",
        publication_year=2026,
        note=note,
    )


class InvestmentCosts(Dataset[pd.DataFrame]):
    """Capital costs of new plants from NamPower's own projects (N$, 2022-2025)."""

    name = "investment_costs"

    def _set_metadata(self) -> MetaData:
        return _workbook_metadata(
            self.name, "Project cost / capacity; nominal N$ converted at the 2023 N$/EUR rate"
        )

    def _set_path(self) -> Path:
        return _folder(self.source_path) / "investment_costs.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        required = {"technology", "capex_nad_per_kw", "capex_nad_per_kwh", "lifetime_years"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError("investment_costs.csv is missing columns: " + ", ".join(sorted(missing)))
        if data["technology"].duplicated().any():
            raise ValueError("investment_costs.csv has duplicate technologies")
        return data.set_index("technology")

    def _value(self, technology: str, column: str) -> float:
        value = float(self.data.loc[technology, column])
        if not value > 0:
            raise ValueError(f"investment_costs.csv needs a positive {column} for {technology}")
        return value

    def capex_euro_per_mw(self, technology: str) -> float:
        """Capex per MW of power, in euro."""
        return load_costs(self.source_path).to_euro(
            self._value(technology, "capex_nad_per_kw") * 1000.0
        )

    def capex_euro_per_mwh(self, technology: str) -> float:
        """Capex per MWh of storage energy, in euro."""
        return load_costs(self.source_path).to_euro(
            self._value(technology, "capex_nad_per_kwh") * 1000.0
        )

    def lifetime(self, technology: str) -> float:
        return self._value(technology, "lifetime_years")


class CommittedProjects(Dataset[pd.DataFrame]):
    """Projects built after 2023 or under construction, fixed in later years."""

    name = "committed_projects"

    def _set_metadata(self) -> MetaData:
        return _workbook_metadata(
            self.name, "Commissioned after 2023 or under construction (expansion pipeline sheet)"
        )

    def _set_path(self) -> Path:
        return _folder(self.source_path) / "committed_projects.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        required = {"project", "technology", "capacity_mw", "energy_mwh", "expected_cod"}
        missing = required.difference(data.columns)
        if missing:
            raise ValueError("committed_projects.csv is missing columns: " + ", ".join(sorted(missing)))
        for column in ["capacity_mw", "energy_mwh", "expected_cod"]:
            data[column] = pd.to_numeric(data[column], errors="raise")
        if (data["capacity_mw"] <= 0).any():
            raise ValueError("committed_projects.csv needs positive capacity_mw")
        return data

    def committed_by(self, technology: str, year: int, column: str = "capacity_mw") -> float:
        """Capacity (MW, or MWh for energy_mwh) of a technology online by a year."""
        rows = self.data.loc[(self.data["technology"] == technology) & (self.data["expected_cod"] <= year)]
        return float(rows[column].fillna(0.0).sum())


class ExpansionAssumptions(Dataset[pd.DataFrame]):
    """Discount rate and biomass and battery parameters."""

    name = "expansion_assumptions"

    def _set_metadata(self) -> MetaData:
        return _workbook_metadata(
            self.name, "Otjikoto fact sheet (May 2024), GIZ (2018) and flagged assumptions"
        )

    def _set_path(self) -> Path:
        return _folder(self.source_path) / "assumptions.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        if not {"item", "value"}.issubset(data.columns) or data["item"].duplicated().any():
            raise ValueError("assumptions.csv needs unique items with values")
        data["value"] = pd.to_numeric(data["value"], errors="raise")
        return data.set_index("item")

    def value(self, item: str) -> float:
        return float(self.data.loc[item, "value"])

    def biomass_fuel_price(self) -> float:
        """Wood-chip price in euro per MWh of fuel energy."""
        nad_per_mwh = self.value("biomass_fuel_price") / (self.value("biomass_energy_content") / 3.6)
        return load_costs(self.source_path).to_euro(nad_per_mwh)


@lru_cache(maxsize=None)
def investment_costs(source_path: Path | str) -> InvestmentCosts:
    return InvestmentCosts(source_path)


@lru_cache(maxsize=None)
def committed_projects(source_path: Path | str) -> CommittedProjects:
    return CommittedProjects(source_path)


@lru_cache(maxsize=None)
def expansion_assumptions(source_path: Path | str) -> ExpansionAssumptions:
    return ExpansionAssumptions(source_path)
