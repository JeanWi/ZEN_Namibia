from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from zen_creator import Attribute, Dataset, Element, MetaData, SourceInformation
from zen_namibia.datasets.datasets.namibia_baseline import load_baseline


class RenewablePlants(Dataset[pd.DataFrame]):
    """Plant capacities and hourly 2023 profiles for wind and solar resources."""

    name = "renewable_plants"
    steps_per_year = 8760

    def _set_metadata(self) -> MetaData:
        return MetaData(
            name=self.name,
            title="Namibia renewable plant capacities and capacity factors",
            author=["Renewable Ninja", "ZEN Namibia"],
            publication="Renewable Ninja plant",
            publication_year=2023,
        )

    def _set_path(self) -> Path:
        return self.source_path / "renewable_plants.csv"

    def _set_data(self) -> pd.DataFrame:
        data = pd.read_csv(self.path)
        required = {
            "technology", "plant", "capacity_limit_mw",
            "capacity_factor_2023_percent", "profile_file",
        }
        missing = required.difference(data.columns)
        if missing:
            raise ValueError(f"renewable_plants.csv is missing columns: {', '.join(sorted(missing))}")
        data = data[[
            "technology", "plant", "capacity_limit_mw",
            "capacity_factor_2023_percent", "profile_file",
        ]].copy()
        data["capacity_limit_mw"] = pd.to_numeric(data["capacity_limit_mw"], errors="raise")
        data["capacity_factor_2023_percent"] = pd.to_numeric(data["capacity_factor_2023_percent"], errors="raise")
        if data.isna().any().any() or data["plant"].duplicated().any():
            raise ValueError("renewable_plants.csv has blank values or duplicate plant names")
        profile_folder = self.source_path / "renewable_ninja_profiles_2023"
        missing_profiles = [
            filename for filename in data["profile_file"]
            if not (profile_folder / filename).is_file()
        ]
        if missing_profiles:
            raise FileNotFoundError(
                "Missing plant-level Renewable Ninja profiles: "
                + ", ".join(missing_profiles)
            )
        if (data["capacity_limit_mw"] < 0).any() or not data["capacity_factor_2023_percent"].between(0, 100).all():
            raise ValueError("Plant capacity limits must be non-negative and capacity factors must be percentages from 0 to 100")
        if not set(data["technology"]).issubset({"wind", "solar"}):
            raise ValueError("technology must be wind or solar")
        return data

    def capacity_mw(self, technology: str) -> float:
        """Sum the plant capacities listed in renewable_plants.csv."""
        rows = self.data.loc[self.data.technology == technology]
        return float(rows["capacity_limit_mw"].sum())

    def _omburu_reference_year(self) -> pd.Series | None:
        """Return the separate Omburu PV row for the configured reference year, if present."""
        baseline = load_baseline(self.source_path)
        year = baseline.reference_year
        rows = baseline.capacities.loc[baseline.capacities.year == year]
        if len(rows) > 1:
            raise ValueError(f"Expected at most one {year} Omburu capacity row")
        return None if rows.empty else rows.iloc[0]

    def existing_capacity_mw(self, technology: str) -> float:
        """Return the reference-year existing fleet capacity for a renewable technology.

        The separate Omburu PV entry (capacities_<reference_year>.csv, or
        capacities.csv as fallback) is added to the solar portfolio. It is not duplicated in renewable_plants.csv.
        """
        capacity = self.capacity_mw(technology)
        if technology == "solar":
            omburu = self._omburu_reference_year()
            if omburu is not None:
                capacity += float(omburu["omburu_pv_mw"])
        return capacity

    def get_capacity_limit(self, element: Element, technology: str) -> Attribute:
        """Cap total renewable capacity at the listed 2023 portfolio size."""
        return Attribute(
            "capacity_limit", default_value=self.existing_capacity_mw(technology),
            unit=element.power_unit, element=element,
            sources=[SourceInformation(
                description=f"Total installed 2023 {technology} capacity from renewable_plants.csv plus the Omburu PV row in capacities_<reference_year>.csv where applicable.",
                metadata=self.metadata,
            )],
        )

    def get_capacity_existing(self, element: Element, technology: str) -> Attribute:
        """Return the listed renewable portfolio as existing 2023 capacity."""
        return Attribute(
            "capacity_existing", default_value=self.existing_capacity_mw(technology),
            unit=element.power_unit, element=element,
            sources=[SourceInformation(
                description=f"Existing 2023 {technology} fleet capacity from renewable_plants.csv plus the Omburu PV row in capacities_<reference_year>.csv where applicable.",
                metadata=self.metadata,
            )],
        )

    def get_max_load(self, element: Element, technology: str) -> Attribute:
        """Capacity-weight hourly plant profiles into the technology's max_load."""
        rows = self.data.loc[self.data.technology == technology]
        if rows.empty:
            raise ValueError(f"No 2023 plants are listed for technology {technology}")

        plant_capacities = rows["capacity_limit_mw"].astype(float).tolist()
        plant_profiles = [
            _load_hourly_profile(
                self.source_path / "renewable_ninja_profiles_2023" / str(filename)
            )
            for filename in rows["profile_file"]
        ]

        # Omburu PV's separate 20 MW unit is stored in capacities_<year>.csv.
        if technology == "solar":
            omburu = self._omburu_reference_year()
            if omburu is not None and float(omburu["omburu_pv_mw"]) > 0:
                profile_file = str(omburu["omburu_pv_profile_file"])
                plant_capacities.append(float(omburu["omburu_pv_mw"]))
                plant_profiles.append(
                    _load_hourly_profile(
                        self.source_path / "renewable_ninja_profiles_2023" / profile_file
                    )
                )

        total_capacity = sum(plant_capacities)
        if total_capacity <= 0:
            raise ValueError(f"Installed capacity for {technology} must be positive")
        weighted_profile = sum(
            capacity * profile
            for capacity, profile in zip(plant_capacities, plant_profiles)
        ) / total_capacity
        if len(weighted_profile) != self.steps_per_year:
            raise ValueError(f"{technology} profile must contain 8,760 hourly values")
        profile = pd.DataFrame(
            {"NAM": weighted_profile.to_numpy()},
            index=pd.RangeIndex(self.steps_per_year, name="time"),
        )
        average_factor = float(weighted_profile.mean())
        return Attribute(
            "max_load", default_value=average_factor, unit="1", element=element, df=profile,
            sources=[SourceInformation(
                description=(
                    f"Hourly 2023 Renewables.ninja power profiles for the {technology} plants, "
                    "normalized by each profile's simulated capacity and weighted by installed capacity."
                ),
                metadata=self.metadata,
            )],
        )


@lru_cache(maxsize=32)
def _load_hourly_profile(profile_path: Path) -> pd.Series:
    """Read and validate one 2023 Renewables.ninja hourly power profile."""
    metadata = None
    with profile_path.open(encoding="utf-8-sig") as profile_file:
        for line in profile_file:
            line = line.strip()
            if line.startswith("# {"):
                metadata = json.loads(line[2:])
                break
    if metadata is None:
        raise ValueError(f"No Renewables.ninja simulation metadata in {profile_path.name}")
    params = metadata.get("params", {})
    if params.get("date_from") != "2023-01-01" or params.get("date_to") != "2023-12-31":
        raise ValueError(f"{profile_path.name} must cover calendar year 2023")
    if params.get("local_time") not in {False, "false", "False", 0}:
        raise ValueError(f"{profile_path.name} must use UTC timestamps")
    if str(metadata.get("units", {}).get("electricity", "")).lower() != "kw":
        raise ValueError(f"{profile_path.name} electricity values must be in kW")
    simulated_capacity_kw = float(params.get("capacity", 0))
    if simulated_capacity_kw <= 0:
        raise ValueError(f"{profile_path.name} has invalid simulated capacity")

    data = pd.read_csv(profile_path, comment="#", parse_dates=["time"])
    if not {"time", "electricity"}.issubset(data.columns):
        raise ValueError(f"{profile_path.name} must include time and electricity columns")
    expected_time = pd.date_range("2023-01-01 00:00", periods=8760, freq="h")
    if len(data) != len(expected_time) or not pd.DatetimeIndex(data["time"]).equals(expected_time):
        raise ValueError(f"{profile_path.name} must contain consecutive hourly UTC data for 2023")
    power_kw = pd.to_numeric(data["electricity"], errors="raise")
    if power_kw.isna().any() or (power_kw < 0).any():
        raise ValueError(f"{profile_path.name} has missing or negative generation")
    availability = power_kw / simulated_capacity_kw
    if (availability > 1.001).any():
        raise ValueError(f"{profile_path.name} exceeds its simulated capacity")
    return availability.clip(lower=0.0, upper=1.0).reset_index(drop=True)


@lru_cache(maxsize=None)
def _load_renewable_plants(source: Path) -> RenewablePlants:
    return RenewablePlants(source_path=source)


def load_renewable_plants(source_path: Path | str) -> RenewablePlants:
    """Return a cached RenewablePlants dataset (read-only) for this source folder."""
    return _load_renewable_plants(Path(source_path).resolve())
