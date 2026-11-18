# ZEN Namibia

ZEN-garden model of the Namibian electricity system, built with zen-creator.
The current setup is a fixed-fleet 2023 dispatch snapshot (8,760 hours, no
investment) with four nodes: Namibia (`NAM`) and its neighbours South Africa
(`ZAF`), Zambia (`ZMB`) and Zimbabwe (`ZWE`), joined by cross-border power
lines. Zimbabwe connects to Namibia only through Zambia.

## Setup

- Install conda and create the `ZEN-garden` environment
- Install zen-creator 2.1 or newer and ZEN-garden 3.1 or newer into it
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
- `zen_namibia/datasets/datasets/` — one dataset class per source: `carrier/nampower.py` (NamPower demand and `costs_2023.csv`, including the CPI scaling of NIRP O&M and the 2023 HFO price estimate),
  `carrier/pypsa.py` (hourly demand shape), `carrier/sapp.py` (SAPP monthly
  time-of-use market prices), `technology/renewables_ninja.py`
  (wind/solar profiles, hydro weather), `technology/nampower.py` (NamPower
  capacities), `technology/sapp.py` (SAPP interconnector transfer limits) and `technology/manual_renewable_plants.py` (own list of
  wind/solar plants).
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
- Import/export prices, Van Eck coal price, and Anixas I estimated 2023 HFO price are
  read from `data/raw_data/02-carrier/nampower/costs_2023.csv`. Van Eck, Anixas I
  and Ruacana O&M come from the NIRP (2020–2021 values); NIRP values are scaled to
  2023 prices with CPI. PV and wind fixed O&M come from IRENA (PV 2023 survey,
  wind Africa 2021) and are not CPI-scaled, because these costs have fallen.
- Electricity is imported only at the `ZAF`, `ZMB` and `ZWE` nodes and
  exported only at `ZAF` (SAPP sales). It reaches Namibia through the
  `power_line` transport technology, limited per direction to 575 MW South
  Africa and 428 MW Zimbabwe–Zambia (Kariba) (SAPP transfer limits) and
  300 MW Zambia (Caprivi Link rating). Neighbour nodes have no demand or
  plants. Imports are capped per hour at the ZESCO (180 MW) and ZPC (80 MW)
  contract sizes in `import_contracts.csv`. South Africa (SAPP market and Eskom) trades at the 2023 SAPP
  day-ahead price by time of use (each month's off-peak, standard and peak
  price, mapped to hours with Eskom's Megaflex periods); Zambia and Zimbabwe (ZESCO, ZPC contracts) at
  NamPower's average import price. Exports earn the SAPP price, capped at the
  contract import price so contract imports cannot be resold. Fuel supply is
  unbounded. Historical annual trade values are used for comparison, not
  imposed as model caps.

## Troubleshooting

- If Python exits with Windows exception `0xc06d007f` inside `numpy.linalg`, reinstall NumPy in the active `ZEN-garden` environment (`conda install --force-reinstall numpy`).
