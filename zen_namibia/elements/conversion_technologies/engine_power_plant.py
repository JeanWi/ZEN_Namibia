from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, ConversionTechnology

from zen_namibia.datasets.datasets.carrier.nampower import load_costs
from zen_namibia.datasets.datasets.technology.expansion import (
    committed_projects,
    investment_costs,
)
from zen_namibia.elements.conversion_technologies.anixas_i import (
    FUEL_INPUT_PER_ELECTRIC_OUTPUT,
)
from zen_namibia.utils import capacity_limit_attribute, capacity_lower_limit_attribute


class EnginePowerPlant(ConversionTechnology):
    """New fuel-oil engine plants like Anixas II (54 MW, commissioned 2024).

    Assumptions: the NIRP heat rate and O&M of Anixas I, and the estimated
    HFO price (Anixas II runs on VLSFO/diesel and is gas-ready).
    """

    name: str = "engine_power_plant"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(name="reference_carrier", default_value=["electricity"], element=self)

    def _set_input_carrier(self) -> Attribute:
        return Attribute(name="input_carrier", default_value=["hfo"], element=self)

    def _set_output_carrier(self) -> Attribute:
        return Attribute(name="output_carrier", default_value=["electricity"], element=self)

    def _set_lifetime(self) -> Attribute:
        return Attribute(
            "lifetime", default_value=investment_costs(self.source_path).lifetime(self.name),
            unit="1", element=self,
        )

    def _set_conversion_factor(self) -> Attribute:
        """Full-load heat rate of Anixas I (NIRP, 8.03 GJ/MWh) as a proxy."""
        return Attribute(
            name="conversion_factor",
            default_value=[{"hfo": {"default_value": FUEL_INPUT_PER_ELECTRIC_OUTPUT, "unit": f"{self.power_unit}h/{self.power_unit}h"}}],
            element=self,
        )

    def _set_capacity_limit(self) -> Attribute:
        return capacity_limit_attribute(self, 0.0, expandable=True)

    def _set_capacity_lower_limit(self) -> Attribute:
        projects = committed_projects(self.source_path)
        return capacity_lower_limit_attribute(self, 0.0, lambda y: projects.committed_by(self.name, y))

    def _set_capex_specific_conversion(self) -> Attribute:
        """Anixas II final cost N$1.325 bn / 54 MW."""
        return Attribute(
            "capex_specific_conversion",
            default_value=investment_costs(self.source_path).capex_euro_per_mw(self.name),
            unit=f"Euro/{self.power_unit}", element=self,
        )

    def _set_opex_specific_fixed(self) -> Attribute:
        return Attribute(
            "opex_specific_fixed",
            default_value=load_costs(self.source_path).fixed_om("anixas_fixed_om_nirap"),
            unit=f"Euro/{self.power_unit}", element=self,
        )

    def _set_opex_specific_variable(self) -> Attribute:
        return Attribute(
            "opex_specific_variable",
            default_value=load_costs(self.source_path).variable_om("anixas_variable_om_nirap"),
            unit="Euro/MWh", element=self,
        )
