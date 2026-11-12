# Namibia energy model data

This folder holds the source data and assumptions for the Namibia energy model for 2023.

## Input files

- `capacities.csv` and `capacities_2023.csv`: installed plant capacities.
- `demands.csv` and `imports.csv`: annual demand, sales, imports and exports.
- `hourly_demand_2023.csv`: 2023 demand shape from PyPSA.
- `renewable_plants.csv` and `renewable_ninja_profiles_2023/`: plant capacities and hourly wind and solar profiles from Renewables.ninja.
- `hydro_weather_2023.csv`: local weather used to estimate seasonal hydro availability.
- `dispatch_assumptions_2023.csv`: operating assumptions for coal, diesel and hydro.

## How the 2023 model is set up

The demand profile has 8,760 hourly values. The two missing year-end values were filled, then the profile was scaled to NamPower's 2023 figures: 4,055 GWh of energy use and a 632 MW peak.

The model uses existing capacity only: 347 MW hydro, 120 MW coal, 22.5 MW diesel, 5.22 MW wind and 292.9 MW solar. Wind and solar availability changes hour by hour using the supplied plant profiles. Each profile is normalized by its Renewables.ninja simulation capacity, scaled to the plant's installed capacity, and combined into a technology-wide availability profile. Solar availability is zero at night. The capacity factors in `renewable_plants.csv` are calculated from these profiles; they differ from earlier estimates for Miles 7, Gaib Solar and Rosh Pinah.

Hydro availability follows a seasonal profile based on precipitation near Ruacana. The weather point does not measure river flow. The profile is calibrated to a 1,323 GWh annual upper limit from NamPower's fiscal-year 2023 report, so treat it as an assumption for calendar 2023, not measured monthly generation.

## Important limitations

Several inputs are still estimates. Coal has an assumed annual minimum of 60% of its capacity-hours. The Anixas generator is made available during the 5% highest-demand hours. Conversion efficiencies use the plants' full-load heat rates in Namibia's 2022 National Integrated Resource Plan: about 22.8% for Van Eck coal and 44.8% for Anixas. The Van Eck table's heat-rate unit appears inconsistent, so its value is interpreted as GJ/MWh, consistent with the report's coal-consumption figure. Anixas burns HFO in operation; diesel/LFO is used for starting and flashing, although the model's input carrier is still named `diesel`. Fuel prices, plant operating costs and import prices are missing, so total cost is not meaningful. The hourly generation mix is a model result, not recorded plant dispatch.

## Sources

Demand, capacities, imports and sales are based on the baseline workbook, PyPSA demand data, and NamPower reports and statistics for 2019–2025. Van Eck and Anixas heat rates are from the [Namibia NIRP Review and Update (2022)](https://www.mme.gov.na/files/publications/611_NIRP_2022for_theElectricitySupplyIndustry_NamibiaSigned.pdf). Wind and solar profiles are from Renewables.ninja; the original files and attribution headers are retained under the CC BY 4.0 license. Hydro weather is from Renewables.ninja. The PDFs remain in their original Downloads folder.
