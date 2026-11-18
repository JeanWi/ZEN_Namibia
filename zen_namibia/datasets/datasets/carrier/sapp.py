from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from zen_creator import Dataset, MetaData

from zen_namibia.datasets.datasets.carrier.pypsa import STEPS_PER_YEAR

PRICE_COLUMNS = ["month", "mcp_usc_per_kwh", "usd_per_eur"]


class SAPPMarketPrices(Dataset[pd.DataFrame]):
    """SAPP day-ahead market (DAM) monthly average clearing prices, 2023."""

    name = "sapp_market_prices"

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="SAPP monthly market performance reports 2023",
            author=["Southern African Power Pool", "European Central Bank"],
            publication="SAPP Market Performance Reports; ECB euro reference rates",
            publication_year=2023,
            url="https://www.sapp.co.zw/market-reports",
            note="Monthly average DAM clearing price (USc/kWh), converted with the ECB monthly USD/EUR rate",
        )

    def _set_path(self) -> Path:
        return self.source_path / "02-carrier" / "sapp" / "dam_prices_2023.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        missing = set(PRICE_COLUMNS).difference(data.columns)
        if missing:
            raise ValueError(
                "dam_prices_2023.csv is missing columns: " + ", ".join(sorted(missing))
            )
        data["month"] = pd.PeriodIndex(data["month"], freq="M")
        for column in ["mcp_usc_per_kwh", "usd_per_eur"]:
            data[column] = pd.to_numeric(data[column], errors="raise")
        if data[PRICE_COLUMNS].isna().any().any() or (data[PRICE_COLUMNS[1:]] <= 0).any().any():
            raise ValueError("dam_prices_2023.csv contains blank or non-positive values")
        return data.set_index("month").sort_index()

    def monthly_euro_per_mwh(self, year: int) -> pd.Series:
        """Monthly price in Euro/MWh: USc/kWh x 10 = USD/MWh, divided by USD/EUR."""
        data = self.data.loc[self.data.index.year == year]
        if len(data) != 12:
            raise ValueError(f"dam_prices_2023.csv needs 12 months for {year}; found {len(data)}")
        return data["mcp_usc_per_kwh"] * 10.0 / data["usd_per_eur"]

    def hourly_euro_per_mwh(self, year: int) -> np.ndarray:
        """The monthly price repeated for every hour of the year (8760 values)."""
        hours = pd.date_range(f"{year}-01-01", periods=STEPS_PER_YEAR, freq="h")
        monthly = self.monthly_euro_per_mwh(year)
        return monthly.loc[hours.to_period("M")].to_numpy()
