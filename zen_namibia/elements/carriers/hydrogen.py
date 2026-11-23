from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from zen_creator import Model

import numpy as np
import pandas as pd
from zen_creator import Attribute, Carrier
from zen_creator.utils.attribute import SourceInformation

from zen_namibia.datasets.datasets.carrier.pypsa import STEPS_PER_YEAR
from zen_namibia.datasets.datasets.technology.hydrogen import hydrogen_assumptions
from zen_namibia.utils import model_years


class Hydrogen(Carrier):
    """Green hydrogen for export (as ammonia), produced in Namibia.

    Demand is Hyphen Phase 1 (175,000 t/yr), flat over the year, from its
    first production year. Hydrogen cannot be imported, so it must come from
    Namibian electrolysers. Measured in MW of hydrogen (lower heating value).
    """

    name: str = "hydrogen"

    def __init__(self, model: Model, power_unit: str = "MW"):
        super().__init__(model=model, power_unit=power_unit)

    def _set_demand(self) -> Attribute:
        data = hydrogen_assumptions(self.source_path)
        first_year = data.value("hydrogen_first_year")
        years = model_years(self)
        attr = Attribute("demand", element=self)
        attr.set_data(
            default_value=0.0,
            unit=self.power_unit,
            df=pd.DataFrame(
                {"NAM": np.full(STEPS_PER_YEAR, data.demand_mw())},
                index=pd.RangeIndex(STEPS_PER_YEAR, name="time"),
            ),
            yearly_variations_df=pd.DataFrame(
                {"NAM": [1.0 if year >= first_year else 0.0 for year in years]},
                index=pd.Index(years, name="year"),
            ),
            source=SourceInformation(
                description=(
                    "Hyphen Phase 1 green hydrogen output (175,000 t/yr at 33.33 MWh/t), "
                    "flat over the year at the Namibian node, from the first production year."
                ),
                metadata=data.metadata,
            ),
        )
        return attr
