from __future__ import annotations

from typing import TYPE_CHECKING
from math import inf

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, Carrier

from zen_namibia.datasets.dataset_collections.electricity_demand import (
    ElectricityDemand,
)
from zen_namibia.datasets.datasets.carrier.nampower import load_costs


class Electricity(Carrier):
    """All data and assumptions for the electricity carrier."""

    name: str = "electricity"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_demand(self) -> Attribute:
        """Set the hourly electricity demand (PyPSA shape, NamPower totals)."""
        return ElectricityDemand(self.source_path).get_demand(self)

    def _set_availability_import(self) -> Attribute:
        """Leave hourly imports effectively unbounded. Todo: this should become line limit"""
        return Attribute(
            "availability_import", default_value=inf, unit=self.power_unit,
            element=self,
        )

    def _set_availability_export(self) -> Attribute:
        """Leave hourly exports effectively unbounded. Todo: this should become line limit"""
        return Attribute(
            "availability_export", default_value=inf, unit=self.power_unit,
            element=self,
        )

    def _set_availability_export_yearly(self) -> Attribute:
        """Leave annual exports unbounded (the zen-creator default of 0 blocks all exports)."""
        return Attribute(
            "availability_export_yearly", default_value=inf, unit=f"{self.power_unit}*h",
            element=self,
        )

    def _set_price_import(self) -> Attribute:
        return Attribute(
            "price_import",
            default_value=load_costs(self.source_path).electricity_price("import"),
            unit=f"Euro/({self.power_unit}*h)",
            element=self,
        )

    def _set_price_export(self) -> Attribute:
        return Attribute(
            "price_export",
            default_value=load_costs(self.source_path).electricity_price("export"),
            unit=f"Euro/({self.power_unit}*h)",
            element=self,
        )
