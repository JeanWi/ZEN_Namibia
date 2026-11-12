from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, ConversionTechnology
from zen_namibia.datasets.datasets.dispatch_assumptions import load_dispatch_assumptions
from zen_namibia.datasets.datasets.namibia_baseline import load_baseline

# MOCK DATA: assumed lifetime of 25 years.
# TODO: replace with a real lifetime assumption once available.
LIFETIME = 25
# Anixas full-load heat rate from Namibia's 2022 NIRP: 8.03 MJ/kWh_e,
# numerically equal to 8.03 GJ/MWh_e.
FULL_LOAD_HEAT_RATE_GJ_PER_MWH_E = 8.03
FUEL_INPUT_PER_ELECTRIC_OUTPUT = FULL_LOAD_HEAT_RATE_GJ_PER_MWH_E / 3.6


class DieselGenerator(ConversionTechnology):
    """Class containing all data and assumptions for diesel generator."""

    name: str = "diesel_generator"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """Set the reference carrier of diesel generator  to electricity."""
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """Use diesel as the plant's fuel input carrier."""
        return Attribute(name="input_carrier", default_value=["diesel"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """Set the output carrier of diesel generator to electricity."""
        return Attribute(
            name="output_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        return Attribute(
            "lifetime", default_value=LIFETIME, unit="1", element=self
        )

    def _set_conversion_factor(self) -> Attribute:
        """Use Anixas's reported full-load heat rate (about 44.8% efficiency).

        ZEN-garden expects fuel input per unit of electricity output. Anixas
        operates on HFO; diesel/LFO is used for starting/flashing, so this
        efficiency applies to HFO fuel energy despite the current carrier name.
        Source: Namibia NIRP Review and Update (2022), Anixas parameters.
        """
        return Attribute(
            name="conversion_factor",
            default_value=[{"diesel": {"default_value": FUEL_INPUT_PER_ELECTRIC_OUTPUT, "unit": f"{self.power_unit}h/{self.power_unit}h"}}],
            element=self,
        )

    # ---------- Optional method for overriding a default attribute ----------

    def _set_capacity_existing(self) -> Attribute:
        """Set the preinstalled (already existing) diesel generator capacity."""
        return Attribute(
            "capacity_existing",
            default_value=load_baseline(self.source_path).capacity_existing("anixas_diesel_mw"),
            unit=self.power_unit,
            element=self,
        )

    def _set_min_full_load_hours_fraction(self) -> Attribute:
        return load_dispatch_assumptions(self.source_path).minimum_dispatch_attribute(self)

    def _set_max_load(self) -> Attribute:
        """Make diesel available at full output only in the assumed peak hours."""
        demand = pd.read_csv(self.source_path / "hourly_demand_2023.csv")
        if len(demand) != 8760:
            raise ValueError("2023 demand must have 8760 rows for diesel peak dispatch")
        peak_hours = load_dispatch_assumptions(self.source_path).peak_hours(self.name)
        peak_indices = demand["demand_mw"].nlargest(peak_hours).index
        profile_values = np.zeros(8760, dtype=float)
        profile_values[peak_indices] = 1.0
        profile = pd.DataFrame(
            {"NAM": profile_values},
            index=pd.RangeIndex(8760, name="time"),
        )
        return Attribute(
            "max_load", default_value=1.0, unit="1", element=self, df=profile
        )
