from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from zen_creator import Dataset, MetaData

from zen_namibia.datasets.datasets.carrier.pypsa import STEPS_PER_YEAR

PRICE_COLUMNS = [
    "month",
    "mcp_usc_per_kwh",
    "off_peak_usc_per_kwh",
    "standard_usc_per_kwh",
    "peak_usc_per_kwh",
    "usd_per_eur",
]
TOU_COLUMNS = {
    "off_peak": "off_peak_usc_per_kwh",
    "standard": "standard_usc_per_kwh",
    "peak": "peak_usc_per_kwh",
}

# Time-of-use periods (assumption): SAPP reports DAM prices by off-peak,
# standard and peak but does not define the hours, so Eskom's Megaflex
# periods in force in 2023 are used. Hours are hour-beginning (7 = 07:00-08:00).
# Every hour not listed is off-peak; Sundays and public holidays are all off-peak.
HIGH_DEMAND_MONTHS = {6, 7, 8}  # June to August; low-demand season otherwise
WEEKDAY_PEAK = {
    "low": {7, 8, 9, 18, 19},
    "high": {6, 7, 8, 17, 18},
}
WEEKDAY_STANDARD = {
    "low": {6, *range(10, 18), 20, 21},
    "high": {*range(9, 17), 19, 20, 21},
}
SATURDAY_STANDARD = {7, 8, 9, 10, 11, 18, 19}


def tou_periods(hours: pd.DatetimeIndex) -> np.ndarray:
    """Eskom time-of-use period (off_peak, standard, peak) of each hour.

    Public holidays are treated as normal days.
    """
    periods = []
    for hour in hours:
        season = "high" if hour.month in HIGH_DEMAND_MONTHS else "low"
        if hour.dayofweek < 5:
            if hour.hour in WEEKDAY_PEAK[season]:
                periods.append("peak")
            elif hour.hour in WEEKDAY_STANDARD[season]:
                periods.append("standard")
            else:
                periods.append("off_peak")
        elif hour.dayofweek == 5 and hour.hour in SATURDAY_STANDARD:
            periods.append("standard")
        else:
            periods.append("off_peak")
    return np.array(periods)


class SAPPMarketPrices(Dataset[pd.DataFrame]):
    """SAPP day-ahead market (DAM) monthly prices 2023: average and by time of use."""

    name = "sapp_market_prices"

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="SAPP monthly market performance reports 2023",
            author=["Southern African Power Pool", "European Central Bank"],
            publication="SAPP Market Performance Reports; ECB euro reference rates",
            publication_year=2023,
            url="https://www.sapp.co.zw/market-reports",
            note=(
                "Monthly average DAM clearing price and monthly average off-peak, "
                "standard and peak prices (USc/kWh), converted with the ECB monthly "
                "USD/EUR rate; hours mapped to periods with Eskom's Megaflex definitions"
            ),
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
        for column in PRICE_COLUMNS[1:]:
            data[column] = pd.to_numeric(data[column], errors="raise")
        if data[PRICE_COLUMNS].isna().any().any() or (data[PRICE_COLUMNS[1:]] <= 0).any().any():
            raise ValueError("dam_prices_2023.csv contains blank or non-positive values")
        return data.set_index("month").sort_index()

    def _year(self, year: int) -> pd.DataFrame:
        data = self.data.loc[self.data.index.year == year]
        if len(data) != 12:
            raise ValueError(f"dam_prices_2023.csv needs 12 months for {year}; found {len(data)}")
        return data

    def monthly_euro_per_mwh(self, year: int, column: str = "mcp_usc_per_kwh") -> pd.Series:
        """Monthly price in Euro/MWh: USc/kWh x 10 = USD/MWh, divided by USD/EUR."""
        data = self._year(year)
        return data[column] * 10.0 / data["usd_per_eur"]

    def hourly_euro_per_mwh(self, year: int) -> np.ndarray:
        """Price for every hour of the year (8760 values): the month's
        off-peak, standard or peak price, by the hour's time-of-use period."""
        hours = pd.date_range(f"{year}-01-01", periods=STEPS_PER_YEAR, freq="h")
        months = hours.to_period("M")
        periods = tou_periods(hours)
        prices = np.empty(STEPS_PER_YEAR)
        for period, column in TOU_COLUMNS.items():
            monthly = self.monthly_euro_per_mwh(year, column)
            mask = periods == period
            prices[mask] = monthly.loc[months[mask]].to_numpy()
        return prices
