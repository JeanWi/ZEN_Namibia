from __future__ import annotations

from typing import TYPE_CHECKING
from math import inf

if TYPE_CHECKING:
    from zen_creator import Model

import numpy as np
import pandas as pd
from zen_creator import Attribute, Carrier

from zen_namibia.datasets.dataset_collections.electricity_demand import (
    ElectricityDemand,
)
from zen_namibia.datasets.datasets.carrier.nampower import (
    NamPowerImportContracts,
    load_costs,
)
from zen_namibia.datasets.datasets.carrier.pypsa import STEPS_PER_YEAR
from zen_namibia.datasets.datasets.carrier.sapp import SAPPMarketPrices
from zen_namibia.elements.energy_systems.energy_system_namibia import (
    DOMESTIC_NODE,
    NODES,
    SAPP_MARKET_NODE,
)


class Electricity(Carrier):
    """All data and assumptions for the electricity carrier."""

    name: str = "electricity"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_demand(self) -> Attribute:
        """Set the hourly electricity demand (PyPSA shape, NamPower totals)."""
        return ElectricityDemand(self.source_path).get_demand(self)

    def _hourly_limits(self, name: str, limits_mw: dict[str, float]) -> Attribute:
        """Constant hourly limits per node; nodes not listed are unbounded."""
        return Attribute(
            name, default_value=inf, unit=self.power_unit, element=self,
            df=pd.DataFrame(
                {node: np.full(STEPS_PER_YEAR, mw) for node, mw in limits_mw.items()},
                index=pd.RangeIndex(STEPS_PER_YEAR, name="time"),
            ),
        )

    def _set_availability_import(self) -> Attribute:
        """No imports in Namibia itself; ZESCO (ZMB) and ZPC (ZWE) are capped at
        their contract size (import_contracts.csv). South Africa (Eskom and SAPP
        market) is limited only by the interconnector."""
        caps = NamPowerImportContracts(self.source_path).import_caps_mw().to_dict()
        if DOMESTIC_NODE in caps:
            raise ValueError("import_contracts.csv cannot cap imports at the domestic node")
        return self._hourly_limits("availability_import", {DOMESTIC_NODE: 0.0, **caps})

    def _set_availability_export(self) -> Attribute:
        """Exports are SAPP market sales, so only the SAPP node (ZAF) can export.

        Exporting at a contract node (ZMB, ZWE) would let the model buy and
        resell there at the same price when SAPP exceeds the contract price.
        """
        no_export = NODES.index.drop(SAPP_MARKET_NODE)
        return self._hourly_limits("availability_export", {node: 0.0 for node in no_export})

    def _set_availability_export_yearly(self) -> Attribute:
        """Leave annual exports unbounded (the zen-creator default of 0 blocks all exports)."""
        return Attribute(
            "availability_export_yearly", default_value=inf, unit=f"{self.power_unit}*h",
            element=self,
        )

    def _hourly_prices(self, name: str, default: float, by_node: dict[str, np.ndarray]) -> Attribute:
        return Attribute(
            name, default_value=default, unit=f"Euro/({self.power_unit}*h)",
            element=self,
            df=pd.DataFrame(by_node, index=pd.RangeIndex(STEPS_PER_YEAR, name="time")),
        )

    def _sapp_price(self) -> np.ndarray:
        """Monthly SAPP day-ahead market price for every hour of the year."""
        return SAPPMarketPrices(self.source_path).hourly_euro_per_mwh(
            self.config.system.reference_year
        )

    def _set_price_import(self) -> Attribute:
        """South Africa (SAPP market, Eskom) buys at the monthly SAPP price;
        Zambia and Zimbabwe (ZESCO, ZPC contracts) at NamPower's average import price."""
        contract = load_costs(self.source_path).electricity_price("import")
        return self._hourly_prices(
            "price_import", contract, {SAPP_MARKET_NODE: self._sapp_price()}
        )

    def _set_price_export(self) -> Attribute:
        """Exports are sold at the monthly SAPP price, capped at the contract import price.

        The cap stops the model from buying contract power from Zambia or
        Zimbabwe and reselling it into SAPP when the market is dearer
        (September to November 2023).
        """
        contract = load_costs(self.source_path).electricity_price("import")
        export = np.minimum(self._sapp_price(), contract)
        return self._hourly_prices("price_export", 0.0, {SAPP_MARKET_NODE: export})
