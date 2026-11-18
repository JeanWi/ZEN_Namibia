## Update to latest Zen creator version
- Update your environment to the newest Zen creator version (2.1.0 or newer):
  ```
  pip install --upgrade zen-creator
  pip show zen-creator
  ```
  
## Current scope

Details and sources are in `data/raw_data/README.md`.

- **Model:** fixed 2023 fleet, 8,760 hours, no investment; cost-driven dispatch, no manual dispatch rules or trade caps.
- **Nodes:** Namibia (all demand and plants) plus South Africa, Zambia and Zimbabwe (trade only; Zimbabwe via Zambia). Angola and Botswana are listed but not modeled.
- **Interconnectors:** SAPP transfer limits: 575 MW South Africa, 180 MW Zambia, 428 MW Kariba (Zambia–Zimbabwe); no line losses.
- **Trade prices:** South Africa at the 2023 monthly SAPP price (€38–192/MWh); Zambia and Zimbabwe at NamPower's average import price (€95/MWh). Exports earn the SAPP price, capped at €95/MWh.
- **Fuel and O&M:** coal N$2,227/t; HFO about N$306.5/GJ (2023 estimate). Thermal and Ruacana O&M from NIRP 2022, scaled to 2023 with CPI. PV (US$6.2/kW-yr, IRENA 2023) and wind (US$68/kW-yr, IRENA Africa) fixed O&M are not CPI-scaled, because these costs have fallen.
- **Exchange rates:** 19.9534 N$/EUR (2023) and 18.7695 N$/EUR (2020), Bank of Namibia.

## Current results (objective €202.78M)

| Item | Model | NamPower reported |
|---|---|---|
| Van Eck | 38.1 GWh (November) | 44.3 GWh |
| Anixas I | 0 GWh | 5–6 GWh |
| Imports via South Africa / Zambia / Zimbabwe | 1,809 / 388 / 0 GWh | Eskom + SAPP 676, ZESCO + ZPC 1,808 GWh |
| Exports | 11.6 GWh | 198 GWh |
| Ruacana hydro | 1,323 GWh | 1,323 GWh (FY2023; model calibrated to it) |
| PV / wind | 480.1 / 27.9 GWh | not reported by NamPower (mostly IPPs) |

The import split differs because SAPP is cheaper than the contract price in most months and contract volumes are not modeled.

## Next steps
1. Verify NIRP plant O&M assumptions against NamPower data; check whether NamPower's IPP contract prices for PV and wind are available, since NamPower pays those rather than the IRENA O&M benchmarks. The NIRP variable O&M excludes fuel, so fuel and O&M are modeled as separate costs.
2. Refine trade: source per-contract import prices for Eskom, ZESCO and ZPC (only NamPower's average is public) and contract volumes or take-or-pay terms, so the split of imports between the neighbours becomes meaningful (Zimbabwe currently supplies nothing); consider hourly SAPP prices instead of monthly averages; add Angola (400 kV Kunene–Cahama link, planned but not built) and Botswana (distribution-level links only; 0.4 GWh from BPC in 2023) if they become relevant; confirm the SAPP limits' date and the export-direction limits; add line losses. Note that 2023 imports via Zambia (ZESCO 1,478 GWh plus ZPC 330 GWh, about 206 MW on average) exceed what the 180 MW SAPP limit allows over a year (1,577 GWh), so check whether part of this energy is wheeled through South Africa or the Caprivi Link (300 MW HVDC) carries more.
3. Replace the estimated 2023 delivered HFO price with NamPower's actual procurement price if it becomes available, and check whether Anixas I burns HFO or VLSFO; confirm the trade-price inputs.
4. Compare modeled calendar-year 2023 generation and trade against observed values; keep fiscal-year figures labeled as proxies.
5. Rebuild and solve after the remaining inputs are sourced, then review dispatch and energy balance.
