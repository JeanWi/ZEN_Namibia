from pathlib import Path

import pandas as pd
from zen_creator import Config, Model

# importing these registers the custom classes in zen_namibia/elements/ with
# zen_creator, so that Model.from_config() can find them by name
# (see source_data/config.yaml)
from zen_namibia.elements import carriers, conversion_technologies, energy_systems  # noqa: F401
from zen_namibia.datasets.datasets.electricity_demand import ElectricityDemand
from zen_namibia.datasets.datasets.namibia_baseline import load_baseline
from zen_namibia.datasets.datasets.renewable_plants import load_renewable_plants

from global_vars import INPUT_DATA_PATH

CONFIG_PATH = Path(__file__).resolve().parent / "source_data" / "config.yaml"


def create_model() -> Model:
    config = Config.load_from_yaml(CONFIG_PATH)
    if config.source_path is not None:
        source_path = Path(config.source_path)
        if not source_path.is_absolute():
            config.source_path = str(CONFIG_PATH.parent.parent / source_path)

    model = Model.from_config(config)

    # the built ZEN-garden dataset is written to INPUT_DATA_PATH
    model.name = INPUT_DATA_PATH.name
    model.output_folder = INPUT_DATA_PATH.parent

    model.build()
    model.validate()
    model.write()

    # ZEN-garden needs a construction-year vintage for each existing-capacity
    # row. For this one-year 2023 snapshot, use the reference year as the vintage
    # so the reported 2023 fleet remains available during the modeled year.
    baseline = load_baseline(config.source_path)
    renewables = load_renewable_plants(config.source_path)
    existing_capacities = {
        "coal_steam_turbine": baseline.capacity_existing("van_eck_thermal_mw"),
        "diesel_generator": baseline.capacity_existing("anixas_diesel_mw"),
        "hydro_turbine": baseline.capacity_existing("ruacana_hydro_mw"),
        "photovoltaics": renewables.existing_capacity_mw("solar"),
        "onshore_wind_turbine": renewables.existing_capacity_mw("wind"),
    }
    technology_folder = model.output_path / "set_technologies" / "set_conversion_technologies"
    for technology, capacity in existing_capacities.items():
        if capacity <= 0:
            continue
        folder = technology_folder / technology
        folder.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(
            [{
                "node": "NAM",
                "year_construction": baseline.reference_year,
                "capacity_existing": capacity,
            }]
        ).to_csv(folder / "capacity_existing.csv", index=False)

    # ZEN-garden reads annual time series from demand_<year>.csv files.
    # Write them from the source CSV so repeated node names never become
    # duplicate columns in the default demand.csv.
    demand_folder = model.output_path / "set_carriers" / "electricity"
    demand_folder.mkdir(parents=True, exist_ok=True)
    for path in demand_folder.glob("demand_[0-9][0-9][0-9][0-9].csv"):
        path.unlink()
    demand_data = ElectricityDemand(source_path=config.source_path)
    for year, table in demand_data.get_year_specific_demand().items():
        table.to_csv(demand_folder / f"demand_{year}.csv", index_label="time")

    # ZEN-garden expects these folders to exist even without storage/transport techs
    (model.output_path / "set_technologies" / "set_storage_technologies").mkdir(
        parents=True, exist_ok=True
    )
    (model.output_path / "set_technologies" / "set_transport_technologies").mkdir(
        parents=True, exist_ok=True
    )

    return model


if __name__ == "__main__":
    create_model()
