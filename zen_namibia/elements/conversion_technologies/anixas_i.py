from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, ConversionTechnology

from zen_namibia.datasets.datasets.carrier.nampower import load_costs
from zen_namibia.datasets.datasets.technology.nampower import NamPowerCapacities
from zen_namibia.utils import capacity_existing_df

# MOCK DATA: assumed lifetime of 25 years.
# TODO: replace with a real lifetime assumption once available.
LIFETIME = 25
# Anixas full-load heat rate from Namibia's 2022 NIRP: 8.03 MJ/kWh_e,
# numerically equal to 8.03 GJ/MWh_e.
FULL_LOAD_HEAT_RATE_GJ_PER_MWH_E = 8.03
FUEL_INPUT_PER_ELECTRIC_OUTPUT = FULL_LOAD_HEAT_RATE_GJ_PER_MWH_E / 3.6
NET_CAPACITY_MW = 21.5


class AnixasI(ConversionTechnology):
    """Anixas I, represented with HFO fuel and plant-specific O&M costs."""

    name: str = "anixas_i"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """Set Anixas I's reference carrier to electricity."""
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """Use HFO as Anixas I's operating fuel."""
        return Attribute(name="input_carrier", default_value=["hfo"], element=self)

    def _set_output_carrier(self) -> Attribute:
        """Set Anixas I's output carrier to electricity."""
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

        Source: Namibia NIRP Review and Update (2022), Anixas parameters.
        """
        return Attribute(
            name="conversion_factor",
            default_value=[{"hfo": {"default_value": FUEL_INPUT_PER_ELECTRIC_OUTPUT, "unit": f"{self.power_unit}h/{self.power_unit}h"}}],
            element=self,
        )

    # ---------- Optional method for overriding a default attribute ----------

    def _set_capacity_existing(self) -> Attribute:
        """Set Anixas I's existing installed capacity."""
        reference_year = self.config.system.reference_year
        capacity = NamPowerCapacities(self.source_path).capacity_existing(
            "anixas_i_mw", reference_year
        )
        return Attribute(
            "capacity_existing",
            default_value=0.0,
            unit=self.power_unit,
            element=self,
            df=capacity_existing_df(capacity, reference_year),
        )

    def _set_opex_specific_fixed(self) -> Attribute:
        return Attribute(
            "opex_specific_fixed",
            default_value=load_costs(self.source_path).fixed_om("anixas_fixed_om_nirap"),
            unit="Euro/MW",
            element=self,
        )

    def _set_opex_specific_variable(self) -> Attribute:
        """Anixas I variable O&M per MWh of electricity (NIRP 2022 Table 7).

        The NIRP lists "3 x N$1.55/kWh", applied as N$4.65/kWh; it excludes fuel.
        """
        return Attribute(
            "opex_specific_variable",
            default_value=load_costs(self.source_path).variable_om("anixas_variable_om_nirap"),
            unit="Euro/MWh",
            element=self,
        )

    def _set_max_load(self) -> Attribute:
        """Cap net electricity output at Anixas I's NIRP value of 21.5 MW."""
        nameplate = NamPowerCapacities(self.source_path).capacity_existing(
            "anixas_i_mw", self.config.system.reference_year
        )
        if nameplate <= 0 or NET_CAPACITY_MW > nameplate:
            raise ValueError("Anixas I net capacity must be positive and no greater than nameplate")
        return Attribute(
            "max_load",
            default_value=NET_CAPACITY_MW / nameplate,
            unit="1",
            element=self,
        )
