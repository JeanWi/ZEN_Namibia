from __future__ import annotations

from math import inf
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, Carrier
from zen_namibia.datasets.datasets.carrier.nampower import load_costs

class HFO(Carrier):
    """Heavy fuel oil used by Anixas I (price is a documented 2020 proxy)."""

    name: str = "hfo"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_availability_import(self) -> Attribute:
        return Attribute("availability_import", default_value=inf, unit=self.power_unit, element=self)

    def _set_price_import(self) -> Attribute:
        return Attribute(
            "price_import",
            default_value=load_costs(self.source_path).anixas_hfo_price(),
            unit=f"Euro/({self.power_unit}*h)",
            element=self,
        )

