# ZEN Namibia

ZEN-garden model of the Namibian electricity system, built with zen-creator.
The current setup is a fixed-fleet 2023 dispatch snapshot (one node, 8,760 hours,
no investment).

## Setup

- Install conda and create the `ZEN-garden` environment
- Install zen-creator 2.1 or newer and ZEN-garden 3.1 or newer into it
  (`pip install --upgrade zen-creator`; version 1.5 cannot read this code)
- Install Gurobi (an academic licence is available)

## Workflow

Run both scripts from this folder (`ZEN_Namibia/`):

1. `python create_model.py` — builds the ZEN-garden dataset into
   `./zen_namibia_dataset_dispatch_2023/`
2. `python run_zen_garden.py` — writes `config_dispatch_2023.yaml`, solves the
   dataset and writes results into `./outputs_dispatch_2023/`

The dataset and output folder names are set in `global_vars.py` and
`run_zen_garden.py`.

## Where to find what

- `data/zen_namibia_config.yaml` — zen-creator config: reference year, time
  steps, and which carriers/technologies are inserted
- `data/raw_data/` — raw inputs, one folder per source
  (`<category>/<source>/`, as in ZEN-europe); see `data/raw_data/README.md`
  for files, sources and assumptions
- `zen_namibia/elements/` — carrier, technology and energy-system definitions
  (edit these to change assumptions)
- `zen_namibia/datasets/datasets/` — one dataset class per source: `carrier/nampower.py` (NamPower demand),
  `carrier/nampower.py` also holds NamPower costs and annual imports/exports,
  `carrier/pypsa.py` (hourly demand shape), `technology/renewables_ninja.py`
  (wind/solar profiles, hydro weather), `technology/nampower.py` (NamPower
  capacities), `technology/manual_renewable_plants.py` (own list of
  wind/solar plants) and `technology/manual_dispatch_assumptions.py` (own
  coal, diesel and hydro operating assumptions).
- `zen_namibia/datasets/dataset_collections/` — combine several sources:
  `electricity_demand.py` (PyPSA shape scaled to NamPower totals) and
  `renewable_fleet.py` (plant list + Renewables.ninja profiles + NamPower's
  Omburu PV)
- `create_model.py` — builds and writes the dataset (existing-capacity
  vintages are set in the technology classes)
- `run_zen_garden.py` — solves the built dataset
- `global_vars.py` — shared paths used by both scripts

## Notes

- All year-dependent inputs follow `system.reference_year` in
  `data/zen_namibia_config.yaml`. The hourly demand profile in
  `hourly_demand_2023.csv` is only available for 2023; other years use a flat
  annual-average profile.
- Natural gas is not included until sourced 2023 capacity and fuel data are available.
- Import, export, coal and diesel prices are read from
  `data/raw_data/02-carrier/nampower/costs_2023.csv`. Plant operating costs and
  physical cross-border line limits are still needed for a stronger dispatch
  model.
- Hourly electricity trade and fuel supply are unbounded pending verified
  physical limits. Yearly imports and exports are capped at the reported values
  in `imports_exports.csv`, and yearly coal supply is capped so Van Eck
  generates at most its reported 44.3 GWh. Fuel and trade prices are nonzero
  and influence dispatch.
- Anixas (diesel) is available only in the 5% highest-demand hours and must run
  at least 5% of its capacity-hours, from
  `03-technology/manual_dispatch_assumptions/dispatch_assumptions_2023.csv`.
- Imports and exports are native electricity-carrier boundary flows at the
  single Namibia node. There is no export-link technology or neighboring
  country node in this configuration.

## Troubleshooting

- If Python exits with Windows exception `0xc06d007f` inside `numpy.linalg`, reinstall NumPy in the active `ZEN-garden` environment (`conda install --force-reinstall numpy`).
