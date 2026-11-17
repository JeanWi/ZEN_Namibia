# Namibia energy model data

This folder holds the raw data and assumptions for the Namibia energy model for 2023.

## Input files

The folders follow ZEN-europe: `<category>/<source>/`. Source-specific dataset
classes in `zen_namibia/datasets/datasets/` read these inputs; dataset
collections combine the sources needed for demand and the renewable fleet.

| Folder | Files | Content |
| --- | --- | --- |
| `02-carrier/nampower/` | `demand.csv` | annual energy use, average and peak demand, sales |
| | `imports_exports.csv` | observed annual imports by origin and exports (GWh); total imports and exports are imposed as yearly caps |
| | `costs_2023.csv` | average import/export prices and coal/diesel fuel-price assumptions |
| `02-carrier/pypsa/` | `hourly_demand_2023.csv` | hourly 2023 demand shape |
| `03-technology/nampower/` | `capacities.csv` | installed plant capacities per year (MW) |
| `03-technology/renewables_ninja/` | `pv_<site>.csv`, `wind_<site>.csv` | hourly 2023 output of each wind and solar site |
| | `weather_ruacana_2023.csv` | hourly 2023 weather near Ruacana, for hydro availability |
| `03-technology/manual_renewable_plants/` | `renewable_plants.csv` | active 2023 wind and solar roster, capacities, profiles, and project categories |
| | `renewable_plants_future_expansion.csv` | solar plants outside the 2023 roster; excluded from the active fleet |
| `03-technology/manual_dispatch_assumptions/` | `dispatch_assumptions_2023.csv` | own operating assumptions for coal, diesel and hydro: annual minimum output and the diesel peak-hours share |

## How the 2023 model is set up

The demand profile has 8,760 hourly values. The two missing year-end values were filled, then the profile was scaled to NamPower's 2023 figures: 4,055 GWh of energy use and a 632 MW peak.

The model uses the supplied 2023 roster: 347 MW hydro, 120 MW coal nameplate (96 MW available at Van Eck), 22.5 MW diesel, 6.22 MW wind, and 193.339 MW solar including NamPower's 20 MW Omburu plant. The 23 rows in `renewable_plants.csv` are the active 2023 roster; project categories are retained where supplied. Solar plants outside that roster remain in `renewable_plants_future_expansion.csv` and are not included in the model. Wind and solar availability changes hourly using the supplied Renewables.ninja profiles. Profiles are normalized by their simulated capacity, scaled to listed plant capacity, and combined into technology-wide availability. The capacity factors in the roster are the means of the hourly profiles.

Hydro availability follows a seasonal profile based on precipitation near Ruacana. The weather point does not measure river flow. The profile is calibrated to a 1,323 GWh annual upper limit from NamPower's fiscal-year 2023 report, so treat it as an assumption for calendar 2023, not measured monthly generation.

## Important limitations

Van Eck is modeled as emergency standby: its 120 MW nameplate capacity is derated to 96 MW available capacity (24 MW per unit across four units), giving a maximum-load fraction of 0.8 and no annual minimum generation. The reported 44.3 GWh sent out in FY2023/24 (`van_eck_sent_out_gwh` in `capacities.csv`) is imposed as an annual maximum, applied as a cap on yearly coal supply because ZEN-garden has no per-technology annual maximum. The reporting period differs from calendar 2023, so treat the cap as an assumption. Synchronous-condenser operation provides grid support but is not counted as active-power generation. The Anixas generator is available only during the 5% highest-demand hours (438 hours, ranked on the PyPSA demand shape) and must run at least 5% of its annual capacity-hours, as set in `dispatch_assumptions_2023.csv`. Hydro has no annual minimum.

Conversion efficiencies use the plants' full-load heat rates in Namibia's 2022 National Integrated Resource Plan: about 22.8% for Van Eck coal and 44.8% for Anixas. The Van Eck table's heat-rate unit appears inconsistent, so its value is interpreted as GJ/MWh, consistent with the report's coal-consumption figure. Anixas burns HFO in operation; diesel/LFO is used for starting and flashing, although the model's input carrier is still named `diesel`.

Costs are fuel, import and export prices only; plant operating costs are not included, and hydro, wind and solar run at zero marginal cost (IPP contracts are treated as take-or-pay). Electricity imports use one average price (N$1,895/MWh, all import contracts and SAPP), so the model does not see hourly import price differences and the timing of coal output within the year remains arbitrary. Coal is priced from N$2,236.5/t using the NIRP's 580 kg/MWh and 15.81 GJ/MWh (about 7.57 MWh per tonne). Anixas fuel is priced at the 2023 average Diesel 50ppm pump price (N$20.71/L at 38.6 MJ/L); this retail price includes taxes and is not the HFO price NamPower pays. The exchange rate of N$19.95/EUR is an approximate 2023 average to be checked against the Bank of Namibia.

Imports and exports are native electricity-carrier boundary flows at the single Namibia node. Their yearly totals are capped at the reported values in `imports_exports.csv` (2,484.4 GWh imports and 198 GWh exports for 2023, which match NamPower's FY2022/23 figures). Exports are sold at the average SAPP market price (N$859.25/MWh); the 198 GWh is an upper bound, not a forced target, because ZEN-garden has no minimum yearly export constraint, so modeled exports can be lower. Hourly trade and fuel supply are unbounded until physical interconnector ratings are sourced; neighboring-country nodes and contract schedules are not modeled. The hourly generation mix is a model result, not recorded plant dispatch.

## Sources

Demand, capacities, imports and sales are based on the baseline workbook, PyPSA demand data, and NamPower reports and statistics for 2019–2025. Import, export and coal costs are from NamPower's integrated annual reports (2023 note 26(a), 2024 note 26, key statistics), and diesel prices from the Bank of Namibia Quarterly Bulletin, June 2024, Table 2.3. Van Eck and Anixas heat rates are from the [Namibia NIRP Review and Update (2022)](https://www.mme.gov.na/files/publications/611_NIRP_2022for_theElectricitySupplyIndustry_NamibiaSigned.pdf). Wind and solar profiles are from Renewables.ninja under the CC BY 4.0 license; the files were renamed to `pv_<site>.csv` and `wind_<site>.csv`, and each keeps its original attribution header. Hydro weather is from Renewables.ninja. The PDFs remain in their original Downloads folder.
