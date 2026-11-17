from __future__ import annotations

from typing import TYPE_CHECKING
from math import inf

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, Carrier

from zen_namibia.datasets.dataset_collections.electricity_demand import (
    ElectricityDemand,
)
from zen_namibia.datasets.datasets.carrier.nampower import (
    NamPowerImportsExports,
    load_costs,
)


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

    def _yearly_trade_limit(self, name: str, column: str) -> Attribute:
        """Cap annual trade at the GWh reported in imports_exports.csv."""
        return Attribute(
            name, default_value=0.0, unit=f"{self.power_unit}*h", element=self,
            df=NamPowerImportsExports(self.source_path).yearly_mwh(column),
        )

    def _set_availability_import_yearly(self) -> Attribute:
        return self._yearly_trade_limit("availability_import_yearly", "imports_gwh")

    def _set_availability_export_yearly(self) -> Attribute:
        return self._yearly_trade_limit("availability_export_yearly", "exports_gwh")

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
