# Namibia energy model data

This folder holds the raw data and assumptions for the Namibia energy model for 2023.

## Input files

The folders follow ZEN-europe: `<category>/<source>/`. Source-specific dataset
classes in `zen_namibia/datasets/datasets/` read these inputs; dataset
collections combine the sources needed for demand and the renewable fleet.

| Folder | Files | Content |
| --- | --- | --- |
| `02-carrier/nampower/` | `demand.csv` | annual energy use, average and peak demand, sales |
| | `imports_exports.csv` | observed annual imports by origin and exports (GWh), retained for comparison |
| | `costs_2023.csv` | import/export prices, 2023 coal price, NIRP plant O&M and 2020 delivered HFO price, Bank of Namibia CPI (2020, 2023), INSEE HFO market prices (2020, 2023), and exchange rates |
| `02-carrier/pypsa/` | `hourly_demand_2023.csv` | hourly 2023 demand shape |
| `03-technology/nampower/` | `capacities.csv` | installed plant capacities per year (MW) |
| `03-technology/renewables_ninja/` | `pv_<site>.csv`, `wind_<site>.csv` | hourly 2023 output of each wind and solar site |
| | `weather_ruacana_2023.csv` | hourly 2023 weather near Ruacana, for hydro availability |
| `03-technology/manual_renewable_plants/` | `renewable_plants.csv` | active 2023 wind and solar roster, capacities, profiles, and project categories |
| | `renewable_plants_future_expansion.csv` | solar plants outside the 2023 roster; excluded from the active fleet |

## How the 2023 model is set up

The demand profile has 8,760 hourly values. The two missing year-end values were filled, then the profile was scaled to NamPower's 2023 figures: 4,055 GWh of energy use and a 632 MW peak.

The model uses the supplied 2023 roster: 347 MW hydro, 120 MW coal nameplate (96 MW available at Van Eck), 22.5 MW installed Anixas I (21.5 MW net output limit), 6.22 MW wind, and 193.339 MW solar including NamPower's 20 MW Omburu plant. The 23 rows in `renewable_plants.csv` are the active 2023 roster; project categories are retained where supplied. Solar plants outside that roster remain in `renewable_plants_future_expansion.csv` and are not included in the model. Wind and solar availability changes hourly using the supplied Renewables.ninja profiles. Profiles are normalized by their simulated capacity, scaled to listed plant capacity, and combined into technology-wide availability. The capacity factors in the roster are the means of the hourly profiles.

Hydro availability follows a seasonal profile based on precipitation near Ruacana. The weather point does not measure river flow. The profile is calibrated to a 1,323 GWh annual upper limit from NamPower's fiscal-year 2023 report, so treat it as an assumption for calendar 2023, not measured monthly generation.

## Important limitations

Van Eck is modeled with 120 MW nameplate and 96 MW available capacity. Its annual generation is not capped at the 44.3 GWh reported for FY2023/24 because that is not a calendar-2023 value. The 2023 baseline uses NamPower's FY2022/23 coal price of N$2,227/t; the FY2023/24 value of N$2,246/t is retained in `costs_2023.csv` for comparison and is not used for calendar 2023. Fuel and O&M are separate: coal consumption is represented by the 15.81 GJ/MWh heat rate (equivalent to about 0.58 t/MWh), while Van Eck variable and fixed O&M use the NIRP 2022 values, based on 2020–2021 data, of N$1.445/kWh (N$1,445/MWh) and N$1,692/kW-year (N$1,692,000/MW-year). The model scales these and the Anixas O&M values from 2020 to 2023 prices with the Bank of Namibia all-items CPI (167.3/140.6 = 1.1899; Quarterly Bulletin, March 2026, file `march 2026.indb`), giving N$1,719/MWh and N$2,013,312/MW-year for Van Eck, then converts them to euros at the 2023 average rate of 19.9534 N$/EUR, calculated from the twelve monthly period-average exchange rates published by the Bank of Namibia in its December 2024 Quarterly Bulletin, Table IV.J, page 147. At N$2,227/t, fuel is approximately N$1,292/MWh; adding 2023-price variable O&M gives approximately N$3,011/MWh before fixed O&M. Fixed O&M is a fleet-year cost and variable O&M is charged per generated MWh. These NIRP values reflect 2020–2021 data, not calendar 2023, and are not verified actual Van Eck expenditure.

Anixas I is represented separately as an HFO plant: the model retains NamPower's 22.5 MW installed capacity and caps net output at the NIRP's 21.5 MW. Its 8.03 GJ/MWh full-load heat rate is paired with an estimated 2023 delivered HFO price of about N$306.5/GJ. The NIRP 2020 delivered price (N$173.10/GJ) is split into the 2020 NW Europe HFO 380 cst FOB market price (EUR 188.89/t, INSEE series 010751333; N$87.32/GJ at 40.6 GJ/t and the Bank of Namibia 2020 average rate of 18.7695 N$/EUR, the mean of the 12 monthly averages) and a delivery cost of N$85.78/GJ. The 2023 price is the 2023 FOB price (EUR 416.05/t, N$204.47/GJ) plus the delivery cost scaled to 2023 with CPI (N$102.06/GJ). This is an estimate, not NamPower's actual 2023 procurement price. Anixas fixed O&M of N$1,517/kW-year (N$1,805,079/MW-year at 2023 prices) is included. Anixas variable O&M is the NIRP entry “3 x N$1.55/kWh”, applied as N$4.65/kWh (N$4,650/MWh; N$5,533/MWh at 2023 prices) per generated MWh; it excludes fuel. NamPower reports Anixas generation of 6.350 GWh in FY2022/23 and 5.237 GWh in FY2023/24; these fiscal-year totals are comparison points, not calendar-2023 dispatch. Combined fuel subsidies are not used as Anixas fuel costs. The hourly generation mix is a model result, not recorded plant dispatch.

## Sources

Demand, capacities, imports, exports, and Anixas generation are based on the baseline workbook, PyPSA demand data, and NamPower reports and statistics for 2019–2025. Van Eck and Anixas technical and O&M values (based on 2020–2021 data) and the 2020 delivered HFO price are from the [Namibia NIRP Review and Update (2022)](https://www.mme.gov.na/files/publications/611_NIRP_2022for_theElectricitySupplyIndustry_NamibiaSigned.pdf). HFO market prices are from INSEE series 010751333 (heavy fuel oil NW Europe 380 cst FOB). The 2020 and 2023 N$/EUR rates (means of monthly averages) are from the Bank of Namibia (bon.com.na; 2023 from the December 2024 Quarterly Bulletin, Table IV.J, page 147). The CPI used to scale NIRP costs to 2023 is from the Bank of Namibia Quarterly Bulletin, March 2026 (file `march 2026.indb`). Anixas FY2022/23 and FY2023/24 sent-out energy is reported in NamPower's Integrated Annual Report 2024 (the earlier nampower.com.na link to the PDF no longer works). Wind and solar profiles are from Renewables.ninja under the CC BY 4.0 license; files were renamed to `pv_<site>.csv` and `wind_<site>.csv`, retaining their original attribution headers. Hydro weather is from Renewables.ninja. The source PDFs are not stored in this repository.
