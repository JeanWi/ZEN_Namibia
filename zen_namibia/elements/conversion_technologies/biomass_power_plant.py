from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, ConversionTechnology

from zen_namibia.datasets.datasets.technology.expansion import (
    committed_projects,
    expansion_assumptions,
    investment_costs,
)
from zen_namibia.utils import capacity_limit_attribute, capacity_lower_limit_attribute


class BiomassPowerPlant(ConversionTechnology):
    """Encroacher-bush biomass steam plants like Otjikoto (40 MW, COD 2027)."""

    name: str = "biomass_power_plant"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(name="reference_carrier", default_value=["electricity"], element=self)

    def _set_input_carrier(self) -> Attribute:
        return Attribute(name="input_carrier", default_value=["biomass"], element=self)

    def _set_output_carrier(self) -> Attribute:
        return Attribute(name="output_carrier", default_value=["electricity"], element=self)

    def _set_lifetime(self) -> Attribute:
        return Attribute(
            "lifetime", default_value=investment_costs(self.source_path).lifetime(self.name),
            unit="1", element=self,
        )

    def _set_conversion_factor(self) -> Attribute:
        """Fuel per MWh of electricity: 1 / 30% (Otjikoto fact sheet)."""
        efficiency = expansion_assumptions(self.source_path).value("biomass_efficiency")
        return Attribute(
            name="conversion_factor",
            default_value=[{"biomass": {"default_value": 1.0 / efficiency, "unit": f"{self.power_unit}h/{self.power_unit}h"}}],
            element=self,
        )

    def _set_capacity_limit(self) -> Attribute:
        return capacity_limit_attribute(self, 0.0, expandable=True)

    def _set_capacity_lower_limit(self) -> Attribute:
        projects = committed_projects(self.source_path)
        return capacity_lower_limit_attribute(self, 0.0, lambda y: projects.committed_by(self.name, y))

    def _set_capex_specific_conversion(self) -> Attribute:
        """Otjikoto estimated cost N$2.641 bn / 40 MW."""
        return Attribute(
            "capex_specific_conversion",
            default_value=investment_costs(self.source_path).capex_euro_per_mw(self.name),
            unit=f"Euro/{self.power_unit}", element=self,
        )

    def _set_opex_specific_fixed(self) -> Attribute:
        """Assumption: a fixed share of capex per year (assumptions.csv)."""
        share = expansion_assumptions(self.source_path).value("biomass_fixed_om_share")
        return Attribute(
            "opex_specific_fixed",
            default_value=share * investment_costs(self.source_path).capex_euro_per_mw(self.name),
            unit=f"Euro/{self.power_unit}", element=self,
        )
