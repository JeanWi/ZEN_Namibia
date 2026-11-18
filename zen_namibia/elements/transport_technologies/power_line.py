from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

import numpy as np
import pandas as pd
from zen_creator import Attribute, TransportTechnology

from zen_namibia.datasets.datasets.technology.sapp import SAPPTransferLimits
from zen_namibia.elements.energy_systems.energy_system_namibia import NODES

# MOCK DATA: assumed lifetime of 40 years; irrelevant without investment.
# TODO: replace with a real lifetime assumption once available.
LIFETIME = 40
EARTH_RADIUS_KM = 6371.0
TIE_BREAK_EURO_PER_MWH = 0.01


def great_circle_km(node_from: str, node_to: str) -> float:
    """Straight-line distance between two node coordinates."""
    lon1, lat1, lon2, lat2 = np.radians(
        [NODES.lon[node_from], NODES.lat[node_from], NODES.lon[node_to], NODES.lat[node_to]]
    )
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return float(2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a)))


class PowerLine(TransportTechnology):
    """Cross-border power lines, one capacity per direction (SAPP transfer limits)."""

    name: str = "power_line"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    # ---------- Required methods that are called during object construction ----------

    def _set_reference_carrier(self) -> Attribute:
        return Attribute(
            name="reference_carrier", default_value=["electricity"], element=self
        )

    # ---------- Required methods that are called during object build ----------

    def _set_lifetime(self) -> Attribute:
        return Attribute("lifetime", default_value=LIFETIME, unit="1", element=self)

    # ---------- Optional methods for overriding default attributes ----------

    def _set_capacity_existing(self) -> Attribute:
        """Existing transfer capacity per directed edge from interconnectors.csv."""
        reference_year = self.config.system.reference_year
        capacities = SAPPTransferLimits(self.source_path).edge_capacities()
        df = pd.DataFrame(
            {"capacity_existing": capacities.to_numpy()},
            index=pd.MultiIndex.from_tuples(
                [(edge, reference_year) for edge in capacities.index],
                names=["edge", "year_construction"],
            ),
        )
        return Attribute(
            "capacity_existing", default_value=0.0, unit=self.power_unit,
            element=self, df=df,
        )

    def _set_opex_specific_variable(self) -> Attribute:
        """Tiny wheeling cost so the solver does not route power in loops.

        Without it, flows in both directions at once or wheeling through
        Namibia cost nothing, and the reported line flows are arbitrary.
        The value is a numerical tie-breaker, not a sourced tariff.
        """
        return Attribute(
            "opex_specific_variable", default_value=TIE_BREAK_EURO_PER_MWH,
            unit=f"Euro/({self.power_unit}*h)", element=self,
        )

    def _set_distance(self) -> Attribute:
        """Straight-line distance between the node coordinates.

        Only informative: transport losses and line costs are zero.
        """
        edges = SAPPTransferLimits(self.source_path).edge_capacities().index
        df = pd.DataFrame(
            {"distance": [great_circle_km(*edge.split("-")) for edge in edges]},
            index=edges,
        )
        return Attribute("distance", default_value=0.0, unit="km", element=self, df=df)
