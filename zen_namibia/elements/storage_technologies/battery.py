from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, StorageTechnology

from zen_namibia.datasets.datasets.technology.expansion import (
    committed_projects,
    expansion_assumptions,
    investment_costs,
)
from zen_namibia.utils import capacity_limit_attribute, capacity_lower_limit_attribute


class Battery(StorageTechnology):
    """Lithium-ion batteries like the Omburu BESS (51 MW / 51 MWh, 2026).

    The whole Omburu cost is put on storage energy with a fixed one-hour
    duration, because only one cost figure is published.
    """

    name: str = "battery"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _assumption(self, item: str) -> float:
        return expansion_assumptions(self.source_path).value(item)

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(name="reference_carrier", default_value=["electricity"], element=self)

    def _set_lifetime(self) -> Attribute:
        return Attribute(
            "lifetime", default_value=investment_costs(self.source_path).lifetime(self.name),
            unit="1", element=self,
        )

    def _set_efficiency_charge(self) -> Attribute:
        """Half of the round-trip losses on charging (assumption: 90% round trip)."""
        return Attribute(
            "efficiency_charge",
            default_value=self._assumption("battery_round_trip_efficiency") ** 0.5,
            unit="1", element=self,
        )

    def _set_efficiency_discharge(self) -> Attribute:
        return Attribute(
            "efficiency_discharge",
            default_value=self._assumption("battery_round_trip_efficiency") ** 0.5,
            unit="1", element=self,
        )

    def _set_energy_to_power_ratio_min(self) -> Attribute:
        return Attribute(
            "energy_to_power_ratio_min", default_value=self._assumption("battery_duration"),
            unit="h", element=self,
        )

    def _set_energy_to_power_ratio_max(self) -> Attribute:
        return Attribute(
            "energy_to_power_ratio_max", default_value=self._assumption("battery_duration"),
            unit="h", element=self,
        )

    def _set_capacity_limit(self) -> Attribute:
        return capacity_limit_attribute(self, 0.0, expandable=True)

    def _set_capacity_limit_energy(self) -> Attribute:
        return capacity_limit_attribute(
            self, 0.0, expandable=True, name="capacity_limit_energy",
            unit=f"{self.power_unit}*h",
        )

    def _set_capacity_lower_limit(self) -> Attribute:
        projects = committed_projects(self.source_path)
        return capacity_lower_limit_attribute(self, 0.0, lambda y: projects.committed_by(self.name, y))

    def _set_capacity_lower_limit_energy(self) -> Attribute:
        projects = committed_projects(self.source_path)
        return capacity_lower_limit_attribute(
            self, 0.0, lambda y: projects.committed_by(self.name, y, "energy_mwh"),
            name="capacity_lower_limit_energy", unit=f"{self.power_unit}*h",
        )

    def _set_capex_specific_storage_energy(self) -> Attribute:
        """Omburu BESS N$500 m / 51 MWh, all on storage energy."""
        return Attribute(
            "capex_specific_storage_energy",
            default_value=investment_costs(self.source_path).capex_euro_per_mwh(self.name),
            unit=f"Euro/({self.power_unit}*h)", element=self,
        )

    def _set_opex_specific_fixed_energy(self) -> Attribute:
        """Assumption: a fixed share of capex per year (assumptions.csv)."""
        return Attribute(
            "opex_specific_fixed_energy",
            default_value=self._assumption("battery_fixed_om_share")
            * investment_costs(self.source_path).capex_euro_per_mwh(self.name),
            unit=f"Euro/({self.power_unit}*h)", element=self,
        )
