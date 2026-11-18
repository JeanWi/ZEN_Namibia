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
- **Interconnectors:** 575 MW South Africa and 428 MW Kariba (Zambia–Zimbabwe) from SAPP; 300 MW Zambia (Caprivi Link rating, above SAPP's 180 MW); no line losses.
- **Import contracts:** hourly caps at ZESCO 180 MW (Zambia) and ZPC 80 MW (Zimbabwe); Eskom (100 MW firm) and SAPP share South Africa. No take-or-pay volumes.
- **Trade prices:** South Africa at the 2023 monthly SAPP price (€38–192/MWh); Zambia and Zimbabwe at NamPower's average import price (€95/MWh). Exports only via South Africa, at the SAPP price capped at €95/MWh.
- **Fuel and O&M:** coal N$2,227/t; HFO about N$306.5/GJ (2023 estimate). Thermal and Ruacana O&M from NIRP 2022, scaled to 2023 with CPI. PV (US$6.2/kW-yr, IRENA 2023) and wind (US$68/kW-yr, IRENA Africa) fixed O&M are not CPI-scaled, because these costs have fallen.
- **Exchange rates:** 19.9534 N$/EUR (2023) and 18.7695 N$/EUR (2020), Bank of Namibia.

## Current results (objective €196.27M)

| Item | Model | NamPower reported |
|---|---|---|
| Van Eck | 15.2 GWh (November) | 44.3 GWh |
| Anixas I | 0 GWh | 5–6 GWh |
| Imports via South Africa / Zambia / Zimbabwe | 1,684 / 388 / 148 GWh | Eskom + SAPP 676 / ZESCO 1,478 / ZPC 330 GWh |
| Exports | 11.6 GWh | 198 GWh |
| Ruacana hydro | 1,323 GWh | 1,323 GWh (FY2023; model calibrated to it) |
| PV / wind | 480.1 / 27.9 GWh | not reported by NamPower (mostly IPPs) |

Contracts are used only in September–November, when SAPP is dearer than €95/MWh; without take-or-pay volumes the model buys mostly from SAPP.

## Next steps
1. **Import contracts:** decide with Jan whether take-or-pay volumes belong in the model (ZESCO ran at 94% of contract in 2023); source per-contract prices.
2. **Hourly SAPP prices:** replace the monthly averages, so short price spikes can trigger Anixas I (0 GWh modeled, 5–6 GWh reported).
3. **Exports:** find why the model exports 11.6 GWh against 198 GWh reported (export price cap, contract resale, timing).
4. **Zambia link:** confirm the 300 MW used instead of SAPP's 180 MW (Caprivi Link rating), the date of the SAPP limits and the export-direction limits.
5. **Fuel and plant costs:** replace the estimated HFO price with NamPower's actual price (HFO or VLSFO?); verify the NIRP O&M with NamPower; look for IPP contract prices for PV and wind.
6. **Later:** line losses; Angola (Kunene–Cahama, planned) and Botswana links if they become relevant.
