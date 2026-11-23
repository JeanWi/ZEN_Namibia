from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, ConversionTechnology

from zen_namibia.datasets.datasets.carrier.nampower import load_costs
from zen_namibia.datasets.dataset_collections.renewable_fleet import RenewableFleet
from zen_namibia.datasets.datasets.technology.expansion import (
    committed_projects,
    investment_costs,
)
from zen_namibia.utils import capacity_lower_limit_attribute, capacity_limit_attribute

# MOCK DATA: assumed lifetime of 25 years.
# TODO: replace with a real lifetime assumption once available.
LIFETIME = 25


class Photovoltaics(ConversionTechnology):
    """Class containing all data and assumptions for photovoltaics."""

    name: str = "photovoltaics"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """Set the reference carrier of photovoltaics to electricity."""
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        Photovoltaics has no input carrier, since it converts solar energy
        directly into electricity.
        """
        return Attribute(name="input_carrier", default_value=[], element=self)

    def _set_output_carrier(self) -> Attribute:
        """Set the output carrier of photovoltaics to electricity."""
        return Attribute(
            name="output_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        return Attribute(
            "lifetime", default_value=LIFETIME, unit="1", element=self
        )

    def _set_conversion_factor(self) -> Attribute:
        """Photovoltaics has no input carrier, so no conversion factor is needed."""
        attr = self.conversion_factor  # default value: []
        return attr

    # ---------- Optional methods for applying Renewable Ninja data ----------

    def _set_capacity_limit(self) -> Attribute:
        """2023 fleet in the reference year; unlimited new capacity in Namibia later."""
        existing = RenewableFleet(self.source_path).existing_capacity_mw(
            "solar", self.config.system.reference_year
        )
        return capacity_limit_attribute(self, existing, expandable=True)

    def _set_capacity_lower_limit(self) -> Attribute:
        """2023 fleet plus committed projects online by each later year."""
        existing = RenewableFleet(self.source_path).existing_capacity_mw(
            "solar", self.config.system.reference_year
        )
        projects = committed_projects(self.source_path)
        return capacity_lower_limit_attribute(
            self, existing, lambda year: projects.committed_by(self.name, year)
        )

    def _set_capex_specific_conversion(self) -> Attribute:
        """Capex per MW from NamPower's own project cost (investment_costs.csv)."""
        return Attribute(
            "capex_specific_conversion",
            default_value=investment_costs(self.source_path).capex_euro_per_mw(self.name),
            unit=f"Euro/{self.power_unit}", element=self,
        )

    def _set_max_load(self) -> Attribute:
        return RenewableFleet(self.source_path).get_max_load(self, "solar")

    def _set_capacity_existing(self) -> Attribute:
        return RenewableFleet(self.source_path).get_capacity_existing(self, "solar")

    def _set_opex_specific_fixed(self) -> Attribute:
        """Utility PV fixed O&M per MW per year (IRENA 2023 average, US$6.2).

        Variable O&M is taken as zero.
        """
        return Attribute(
            "opex_specific_fixed",
            default_value=load_costs(self.source_path).usd_fixed_om("pv_fixed_om_irena"),
            unit=f"Euro/{self.power_unit}",
            element=self,
        )
