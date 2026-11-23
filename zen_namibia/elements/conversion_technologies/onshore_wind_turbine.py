from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

from zen_creator import Attribute, ConversionTechnology

from zen_namibia.datasets.datasets.carrier.nampower import load_costs
from zen_namibia.datasets.dataset_collections.renewable_fleet import RenewableFleet
from zen_namibia.datasets.datasets.technology.expansion import (
    committed_projects,
    expansion_assumptions,
    investment_costs,
)
from zen_namibia.utils import capacity_lower_limit_attribute, capacity_limit_attribute

# MOCK DATA: assumed lifetime of 25 years.
# TODO: replace with a real lifetime assumption once available.
LIFETIME = 25


class OnshoreWindTurbine(ConversionTechnology):
    """Class containing all data and assumptions for onshore_wind_turbine."""

    name: str = "onshore_wind_turbine"
    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        """Set the reference carrier of onshore_wind_turbine to electricity."""
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    def _set_input_carrier(self) -> Attribute:
        """
        onshore_wind_turbine has no input carrier, since it converts wind energy
        directly into electricity.
        """
        return Attribute(name="input_carrier", default_value=[], element=self)

    def _set_output_carrier(self) -> Attribute:
        """Set the output carrier of onshore_wind_turbine to electricity."""
        return Attribute(
            name="output_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        return Attribute(
            "lifetime", default_value=LIFETIME, unit="1", element=self
        )

    def _set_conversion_factor(self) -> Attribute:
        """onshore_wind_turbine has no input carrier, so no conversion factor is needed."""
        attr = self.conversion_factor  # default value: []
        return attr

    # ---------- Optional methods for applying Renewable Ninja data ----------

    def _set_capacity_limit(self) -> Attribute:
        """2023 fleet in the reference year; unlimited new capacity in Namibia later."""
        existing = RenewableFleet(self.source_path).existing_capacity_mw(
            "wind", self.config.system.reference_year
        )
        return capacity_limit_attribute(self, existing, expandable=True)

    def _set_capacity_lower_limit(self) -> Attribute:
        """2023 fleet plus committed projects online by each later year."""
        existing = RenewableFleet(self.source_path).existing_capacity_mw(
            "wind", self.config.system.reference_year
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
        """Renewables.ninja profile scaled to a 34.8% annual capacity factor.

        The Ombepo (Luderitz) profile gives about 51%, while NamPower's P50
        yield for the cancelled 40 MW Rosh Pinah wind farm on the same coast
        was 34.8% (assumptions.csv)."""
        target = expansion_assumptions(self.source_path).value("wind_capacity_factor")
        return RenewableFleet(self.source_path).get_max_load(self, "wind", target)

    def _set_capacity_existing(self) -> Attribute:
        return RenewableFleet(self.source_path).get_capacity_existing(self, "wind")

    def _set_opex_specific_fixed(self) -> Attribute:
        """Onshore wind fixed O&M per MW per year (IRENA 2021 Africa, US$68, unscaled).

        Variable O&M is taken as zero.
        """
        return Attribute(
            "opex_specific_fixed",
            default_value=load_costs(self.source_path).usd_fixed_om("wind_fixed_om_irena"),
            unit=f"Euro/{self.power_unit}",
            element=self,
        )
