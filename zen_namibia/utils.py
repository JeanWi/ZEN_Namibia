from __future__ import annotations

import pandas as pd


def capacity_existing_df(capacity: float, reference_year: int) -> pd.DataFrame | None:
    """Return the existing fleet as one vintage built in the reference year.

    ZEN-garden needs a construction year for each existing-capacity row. For
    this one-year snapshot, the reference year is used as the vintage so the
    reported fleet remains available during the modeled year. Returns None
    when there is no capacity, so no vintage row is written.
    """
    if capacity <= 0:
        return None
    return pd.DataFrame(
        {"capacity_existing": [capacity]},
        index=pd.MultiIndex.from_tuples(
            [("NAM", reference_year)], names=["node", "year_construction"]
        ),
    )


def model_years(element) -> list[int]:
    """Optimized years: reference year plus interval steps."""
    system = element.config.system
    return [
        system.reference_year + i * system.interval_between_years
        for i in range(system.optimized_years)
    ]


def capacity_limit_attribute(
    element, existing: float, expandable: bool, name: str = "capacity_limit",
    unit: str | None = None, node: str = "NAM",
):
    """Capacity limit per year: only the existing capacity in the reference year
    (2023 stays the calibrated fleet), unlimited later if expandable, and zero
    at every other node."""
    from math import inf

    from zen_creator import Attribute

    reference_year = element.config.system.reference_year
    years = model_years(element)
    limits = [
        existing if (year == reference_year or not expandable) else inf
        for year in years
    ]
    df = pd.DataFrame(
        {name: limits},
        index=pd.MultiIndex.from_tuples([(node, y) for y in years], names=["node", "year"]),
    )
    return Attribute(name, default_value=0.0, unit=unit or element.power_unit, element=element, df=df)


def capacity_lower_limit_attribute(
    element, existing: float, committed_by_year, name: str = "capacity_lower_limit",
    unit: str | None = None, node: str = "NAM",
):
    """Minimum capacity per year: existing capacity plus committed projects
    online by that year (committed_by_year: year -> MW). The reference year
    has no lower limit beyond what exists."""
    from zen_creator import Attribute

    reference_year = element.config.system.reference_year
    later = [y for y in model_years(element) if y > reference_year]
    if not later:
        return Attribute(name, default_value=0.0, unit=unit or element.power_unit, element=element)
    df = pd.DataFrame(
        {name: [existing + committed_by_year(y) for y in later]},
        index=pd.MultiIndex.from_tuples([(node, y) for y in later], names=["node", "year"]),
    )
    return Attribute(name, default_value=0.0, unit=unit or element.power_unit, element=element, df=df)
