# ZEN Namibia

ZEN-garden model of the Namibian electricity system, built with zen-creator.
The current setup is a fixed-fleet 2023 dispatch snapshot (one node, 8,760 hours,
no investment).

## Setup

- Install conda and create the `ZEN-garden` environment
- Install zen-garden and zen-creator into it
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

- `source_data/config.yaml` — zen-creator config: reference year, time steps,
  and which carriers/technologies are inserted
- `source_data/*.csv` — raw inputs (capacities, demand, hourly demand, imports,
  renewable plants, dispatch assumptions); see `source_data/readme.md` for
  sources and assumptions
- `zen_namibia/elements/` — carrier, technology and energy-system definitions
  (edit these to change assumptions)
- `zen_namibia/datasets/datasets/` — loaders that turn `source_data/` CSVs into
  attributes. Use the cached helpers (`load_baseline`, `load_renewable_plants`,
  `load_dispatch_assumptions`, `read_reference_year`) so each CSV is read once
  per build
- `create_model.py` — builds and writes the dataset, then adds existing-capacity
  vintages and year-specific `demand_<year>.csv` files
- `run_zen_garden.py` — solves the built dataset
- `global_vars.py` — shared paths used by both scripts

## Notes

- All year-dependent inputs follow `system.reference_year` in
  `source_data/config.yaml`. The hourly demand profile in
  `hourly_demand_2023.csv` is only available for 2023; other years use a flat
  annual-average profile.
- Natural gas is not included until sourced 2023 capacity and fuel data are available.

## Troubleshooting

- If Python exits with Windows exception `0xc06d007f` inside `numpy.linalg`, reinstall NumPy in the active `ZEN-garden` environment (`conda install --force-reinstall numpy`).
