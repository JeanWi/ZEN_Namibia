from __future__ import annotations

from pathlib import Path

import pandas as pd
from zen_creator import Dataset, MetaData


class NIRPDemandGrowth(Dataset[pd.DataFrame]):
    """Annual electricity demand growth rate from Namibia's draft NIRP 2022."""

    name = "nirp_demand_growth"

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="NIRP Review and Update 2022: load forecast",
            author=["Ministry of Mines and Energy, Namibia"],
            publication="National Integrated Resource Plan (NIRP) 2022, as cited in the TMP (2023) least-cost study for Namibia",
            publication_year=2022,
            url="https://www.internationalrivers.org/wp-content/uploads/sites/86/2023/07/TMP-report-Namibia-2023.pdf",
            note="2.7% per year average growth of electricity demand 2021-2040",
        )

    def _set_path(self) -> Path:
        return self.source_path / "02-carrier" / "nirp" / "demand_growth.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        if not {"item", "value"}.issubset(data.columns):
            raise ValueError("demand_growth.csv needs item and value columns")
        data["value"] = pd.to_numeric(data["value"], errors="raise")
        return data.set_index("item")

    def annual_growth_rate(self) -> float:
        rate = float(self.data.loc["annual_growth_rate", "value"])
        if not -0.5 < rate < 0.5:
            raise ValueError("demand_growth.csv annual_growth_rate must be a fraction, e.g. 0.027")
        return rate
