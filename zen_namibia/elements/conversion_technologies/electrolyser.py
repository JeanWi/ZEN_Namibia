from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, ConversionTechnology

from zen_namibia.datasets.datasets.technology.hydrogen import hydrogen_assumptions
from zen_namibia.utils import capacity_limit_attribute


class Electrolyser(ConversionTechnology):
    """Grid-connected electrolysers in Namibia (Hyphen Phase 1 plans 1.5 GW).

    Capacity is measured in MW of electricity input, so it can be compared
    with Hyphen's electrolyser size. The size is optimized, not imposed.
    """

    name: str = "electrolyser"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _h2(self, item: str) -> float:
        return hydrogen_assumptions(self.source_path).value(item)

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(name="reference_carrier", default_value=["electricity"], element=self)

    def _set_input_carrier(self) -> Attribute:
        return Attribute(name="input_carrier", default_value=["electricity"], element=self)

    def _set_output_carrier(self) -> Attribute:
        return Attribute(name="output_carrier", default_value=["hydrogen"], element=self)

    def _set_lifetime(self) -> Attribute:
        return Attribute("lifetime", default_value=self._h2("electrolyser_lifetime"), unit="1", element=self)

    def _set_conversion_factor(self) -> Attribute:
        """Hydrogen out (LHV) per MWh of electricity in."""
        return Attribute(
            name="conversion_factor",
            default_value=[{"hydrogen": {"default_value": self._h2("electrolyser_efficiency"), "unit": f"{self.power_unit}h/{self.power_unit}h"}}],
            element=self,
        )

    def _set_capacity_limit(self) -> Attribute:
        return capacity_limit_attribute(self, 0.0, expandable=True)

    def _set_capex_specific_conversion(self) -> Attribute:
        """IEA Global Hydrogen Review 2024, 2030 installed cost (hydrogen.csv)."""
        return Attribute(
            "capex_specific_conversion",
            default_value=hydrogen_assumptions(self.source_path).electrolyser_capex_euro_per_mw(),
            unit=f"Euro/{self.power_unit}", element=self,
        )

    def _set_opex_specific_fixed(self) -> Attribute:
        return Attribute(
            "opex_specific_fixed",
            default_value=self._h2("electrolyser_fixed_om_share")
            * hydrogen_assumptions(self.source_path).electrolyser_capex_euro_per_mw(),
            unit=f"Euro/{self.power_unit}", element=self,
        )
