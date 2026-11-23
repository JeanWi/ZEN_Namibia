from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

import pandas as pd
from zen_creator import Attribute, EnergySystem

from zen_namibia.datasets.datasets.technology.expansion import expansion_assumptions
from zen_namibia.datasets.datasets.technology.sapp import SAPPTransferLimits

# Namibia plus the neighbouring systems it trades with. Namibia holds
# the demand and the domestic fleet; the neighbours only supply imports and
# take exports at the boundary prices, via the cross-border power lines.
# Zimbabwe (ZPC) has no direct line to Namibia and reaches it through Zambia;
# SAPP market trade reaches Namibia through South Africa and Zambia.
# Coordinates are the capital cities and are used only for line distances.
# Note: "NA" is avoided as a node name because pandas reads it as "missing data".
NODES = pd.DataFrame(
    {
        "lon": [17.0658, 28.1881, 28.2833, 31.0522],
        "lat": [-22.5609, -25.7461, -15.4167, -17.8292],
    },
    index=pd.Index(["NAM", "ZAF", "ZMB", "ZWE"], name="node"),
)
DOMESTIC_NODE = "NAM"
# Node where Namibia trades at the SAPP market price (SAPP market and Eskom).
SAPP_MARKET_NODE = "ZAF"


class EnergySystemNamibia(EnergySystem):
    """Energy system for Namibia with its South African, Zambian and Zimbabwean neighbours."""

    name: str = "energy_system_namibia"

    def __init__(self, model: Model):
        super().__init__(model=model)

    def _set_discount_rate(self) -> Attribute:
        """8% real (assumption; NamPower does not disclose its WACC)."""
        return Attribute(
            "discount_rate",
            default_value=expansion_assumptions(self.source_path).value("discount_rate"),
            unit="1", element=self,
        )

    def _set_set_nodes(self) -> Attribute:
        return Attribute("set_nodes", default_value=None, df=NODES, element=self)

    def _set_set_edges(self) -> Attribute:
        """One directed edge per interconnector direction in interconnectors.csv."""
        limits = SAPPTransferLimits(self.source_path)
        unknown = set(limits.nodes()).difference(NODES.index)
        if unknown:
            raise ValueError(f"interconnectors.csv uses nodes without coordinates: {sorted(unknown)}")
        edges = pd.DataFrame(
            [edge.split("-") for edge in limits.edge_capacities().index],
            columns=["node_from", "node_to"],
            index=limits.edge_capacities().index,
        )
        return Attribute("set_edges", default_value=None, df=edges, element=self)
