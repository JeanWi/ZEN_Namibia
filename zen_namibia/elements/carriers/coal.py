from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, Carrier
from math import inf
from zen_namibia.datasets.datasets.carrier.nampower import load_costs
from zen_namibia.datasets.datasets.technology.nampower import NamPowerCapacities
from zen_namibia.elements.conversion_technologies.coal_steam_turbine import (
    FUEL_INPUT_PER_ELECTRIC_OUTPUT,
    FUEL_MWH_PER_TONNE,
)


class Coal(Carrier):
    """Coal fuel carrier; annual supply is capped by Van Eck's reported output."""

    name: str = "coal"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        return Attribute("availability_import", default_value=inf, unit=self.power_unit, element=self)

    def _set_availability_import_yearly(self) -> Attribute:
        """Cap annual coal supply so Van Eck generates at most its reported output.

        Van Eck is the only coal user, so limiting coal to sent-out GWh x fuel
        input per MWh_e caps its annual generation. ZEN-garden has no
        per-technology annual maximum to use instead. The 44.3 GWh is
        FY2023/24, so the cap is an assumption for calendar 2023.
        """
        sent_out_gwh = NamPowerCapacities(self.source_path).capacity_existing(
            "van_eck_sent_out_gwh", self.config.system.reference_year
        )
        return Attribute(
            "availability_import_yearly",
            default_value=sent_out_gwh * 1000 * FUEL_INPUT_PER_ELECTRIC_OUTPUT,
            unit=f"{self.power_unit}*h",
            element=self,
        )

    def _set_price_import(self) -> Attribute:
        """Van Eck coal cost per tonne, converted to Euro per MWh of coal."""
        return Attribute(
            "price_import",
            default_value=load_costs(self.source_path).coal_price(FUEL_MWH_PER_TONNE),
            unit=f"Euro/({self.power_unit}*h)",
            element=self,
        )
