## Setup
- Use zen-creator 2.1.0 or newer: `pip install --upgrade zen-creator`

## Current scope
Details and sources: `data/raw_data/README.md`.

- **Model:** hourly, cost-driven; 2023 (calibrated fleet, no new capacity) and 2030 (investment allowed), 8% discount rate.
- **Investment (2030):** PV, onshore wind, engines, biomass, batteries; capex from NamPower projects (`03-technology/expansion/`); committed projects (Anixas II, Rosh Pinah PV, Omburu BESS, Otjikoto biomass, Diaz wind, ...) fixed; coal, hydro, Anixas I and lines not expandable.
- **Green hydrogen (2030):** Hyphen Phase 1, 175 kt H2/yr (666 MW flat) from 2028; grid-connected electrolysers (69%, $1,350/kW) and compressed storage ($700/kg) sized by the model (`03-technology/hydrogen/`).
- **Wind:** Renewables.ninja profile scaled to a 34.8% capacity factor (NamPower Rosh Pinah P50).
- **Demand growth:** later years scale 2023 demand: NamPower actuals to 2025, then NIRP 2.7%/yr (4,938 GWh in 2030, 6,445 GWh in 2040). Set `optimized_years` / `interval_between_years` to use it.
- **Nodes:** Namibia (demand and plants); South Africa, Zambia, Zimbabwe (trade only).
- **Lines:** South Africa 575 MW, Zambia 300 MW, Kariba (Zambia–Zimbabwe) 428 MW.
- **Imports:** South Africa at the SAPP time-of-use price (monthly off-peak/standard/peak, Eskom hours, €20–229/MWh); ZESCO (180 MW) and ZPC (80 MW) contracts at €95/MWh.
- **Exports:** via South Africa only, hourly SAPP price capped at €95/MWh; after 2023 capped at 539 GWh/yr (NamPower 2025 exports).
- **Costs:** coal, estimated HFO price, NIRP and IRENA O&M, in 2023 euros.

## Current results
2023 + 2030 with hydrogen solved to optimum (objective €1.70 bn) but Gurobi ran out of memory before writing results: rerun with more free memory. Table below is the earlier 2023-only run (objective €197.88M).

| Item | Model (GWh) | NamPower (GWh) |
|---|---|---|
| Van Eck | 55.9 | 44.3 |
| Anixas I | 0 | 5–6 |
| Imports SA / Zambia / Zimbabwe | 1,578 / 459 / 143 | 676 / 1,478 / 330 |
| Exports | 11.6 | 198 |
| Ruacana hydro | 1,323 | 1,323 |
| PV / wind | 480.1 / 27.9 | not reported |

## Next steps
1. **Anixas I:** never runs (€400/MWh vs SAPP peak ≤ €229/MWh); it runs in real shortages, which the model lacks (SA imports unlimited up to the line). Also confirm SAPP's time-of-use hours (Eskom's assumed).
2. **Exports:** model exports only domestic surplus (11.6 GWh). NamPower's 198 GWh (FY2022/23) is mostly contract imports it could not use, resold to SAPP, which the model does not represent. For future years: revisit the €95/MWh export price cap and SAPP export limits.
3. **Zambia link:** confirm 300 MW (SAPP lists 180 MW).
4. **Costs:** actual HFO price; check NIRP O&M; ZESCO and ZPC contract prices; IPP contract prices for PV and wind.
5. **Demand growth:** check 2.7% in the NIRP 2022 itself (Ch. 3, App. A2).
6. **Hydrogen:** rerun and read results; check the no-imports-for-hydrogen rule (compare 2030 imports with a run without hydrogen, add an import cap if they rise); verify the 69% electrolyser efficiency (IEA); add ammonia synthesis and desalination electricity; existing PV/wind are charged capex in 2023 (+€15.5M).
7. **Later:** line losses; Angola and Botswana links.
