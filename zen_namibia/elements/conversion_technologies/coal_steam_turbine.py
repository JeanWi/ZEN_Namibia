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
# Van Eck full-load heat rate from Namibia's 2022 NIRP: 15.81 GJ/MWh_e.
# The table labels this value MJ/MWh, which is not physically plausible;
# interpreting it as GJ/MWh is consistent with the report's ~580 kg coal/MWh.
FULL_LOAD_HEAT_RATE_GJ_PER_MWH_E = 15.81
FUEL_INPUT_PER_ELECTRIC_OUTPUT = FULL_LOAD_HEAT_RATE_GJ_PER_MWH_E / 3.6


class CoalSteamTurbine(ConversionTechnology):
    """Class containing all data and assumptions for coal steam turbine."""

    name: str = "coal_steam_turbine"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """Set the reference carrier of coal steam turbine to electricity."""
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """Use coal as the plant's fuel input carrier."""
        return Attribute(name="input_carrier", default_value=["coal"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """Set the output carrier of coal steam turbine to electricity."""
        return Attribute(
            name="output_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        return Attribute(
            "lifetime", default_value=LIFETIME, unit="1", element=self
        )

    def _set_conversion_factor(self) -> Attribute:
        """Use Van Eck's reported full-load heat rate (about 22.8% efficiency).

        ZEN-garden expects fuel input per unit of electricity output, so the
        factor is the heat rate in GJ/MWh_e divided by 3.6 GJ/MWh_fuel.
        The NIRP also reports a lower efficiency at minimum load; this scalar
        assumption represents full-load operation only.
        Source: Namibia NIRP Review and Update (2022), Van Eck parameters.
        """
        return Attribute(
            name="conversion_factor",
            default_value=[{"coal": {"default_value": FUEL_INPUT_PER_ELECTRIC_OUTPUT, "unit": f"{self.power_unit}h/{self.power_unit}h"}}],
            element=self,
        )

    # ---------- Optional method for overriding a default attribute ----------

    def _set_capacity_existing(self) -> Attribute:
        """Set the preinstalled (already existing) coal steam turbine  capacity."""
        return Attribute(
            "capacity_existing",
            default_value=load_baseline(self.source_path).capacity_existing("van_eck_thermal_mw"),
            unit=self.power_unit,
            element=self,
        )

    def _set_min_full_load_hours_fraction(self) -> Attribute:
        return load_dispatch_assumptions(self.source_path).minimum_dispatch_attribute(self)

    def _set_max_load(self) -> Attribute:
        """Allow coal output to vary hourly up to installed capacity."""
        profile = pd.DataFrame(
            {"NAM": np.ones(8760)},
            index=pd.RangeIndex(8760, name="time"),
        )
        return Attribute(
            "max_load", default_value=1.0, unit="1", element=self, df=profile
        )

