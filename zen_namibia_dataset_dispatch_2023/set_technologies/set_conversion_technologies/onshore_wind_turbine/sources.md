onshore_wind_turbine
====================

capacity_existing
-----------------

Step 1
Existing 2023 wind fleet capacity from renewable_plants.csv plus the Omburu PV unit in NamPower's capacities.csv.

**Citations**

- **manual_renewable_plants**: ZEN Namibia (2026). Namibia wind and solar plants in operation in 2023. ZEN Namibia.. Note: 2023 operating-plant roster compiled from the project list; profile files are from Renewables.ninja
- **renewables_ninja**: Pfenninger, S., Staffell, I. (2016). Long-term patterns of European PV output using 30 years of validated hourly reanalysis and satellite data. Energy. https://doi.org/10.1016/j.energy.2016.08.060
- **nampower_capacities**: NamPower (2025). NamPower annual reports and statistics 2019-2025. NamPower Annual Reports.. Note: compiled in the ZEN Namibia baseline workbook

max_load
--------

Step 1
Hourly 2023 Renewables.ninja power profiles for the wind plants, normalized by each profile's simulated capacity and weighted by installed capacity, scaled to a 34.8% annual capacity factor.

**Citations**

- **manual_renewable_plants**: ZEN Namibia (2026). Namibia wind and solar plants in operation in 2023. ZEN Namibia.. Note: 2023 operating-plant roster compiled from the project list; profile files are from Renewables.ninja
- **renewables_ninja**: Pfenninger, S., Staffell, I. (2016). Long-term patterns of European PV output using 30 years of validated hourly reanalysis and satellite data. Energy. https://doi.org/10.1016/j.energy.2016.08.060
- **nampower_capacities**: NamPower (2025). NamPower annual reports and statistics 2019-2025. NamPower Annual Reports.. Note: compiled in the ZEN Namibia baseline workbook