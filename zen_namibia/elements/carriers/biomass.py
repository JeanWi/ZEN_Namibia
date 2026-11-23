from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from math import inf

from zen_creator import Attribute, Carrier

from zen_namibia.datasets.datasets.technology.expansion import expansion_assumptions


class Biomass(Carrier):
    """Encroacher-bush wood chips, bought in Namibia without a volume limit."""

    name: str = "biomass"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        """Ample resource: NamPower estimates that only 13% of the harvestable
        bush near Otjikoto would be used over 25 years."""
        return Attribute("availability_import", default_value=inf, unit=self.power_unit, element=self)

    def _set_price_import(self) -> Attribute:
        """Wood-chip price per MWh of fuel (N$908/t at 14.7 GJ/t)."""
        return Attribute(
            "price_import",
            default_value=expansion_assumptions(self.source_path).biomass_fuel_price(),
            unit=f"Euro/({self.power_unit}*h)", element=self,
        )
