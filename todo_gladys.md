## Update to latest Zen creator version
- Update your environment to the newest Zen creator version (2.1.0 or newer):
  ```
  pip install --upgrade zen-creator
  pip show zen-creator
  ```
  
## Current scope
- **Model:** fixed-fleet 2023 dispatch snapshot (8,760 hours, no investment). Dispatch is cost-driven; manual dispatch assumptions have been removed. Historical annual trade volumes are stored for comparison but are not enforced as limits.
- **Nodes:** Namibia (NAM) holds all demand and plants. Its neighbours South Africa (ZAF), Zambia (ZMB) and Zimbabwe (ZWE) only trade electricity. Zimbabwe connects only through Zambia. Angola (400 kV Kunene–Cahama link, planned) and Botswana (distribution-level links) are listed in `interconnectors.csv` but not modeled.
- **Interconnectors:** the power_line transport technology, limited per direction to the SAPP transfer limits: 575 MW South Africa–Namibia, 180 MW Zambia–Namibia, 428 MW Zambia–Zimbabwe (Kariba). Export-direction limits are assumed equal. A €0.01/MWh wheeling cost only stops looped flows; line losses are not modeled.
- **Trade prices:** South Africa (SAPP market, Eskom) trades at the 2023 monthly SAPP day-ahead price (€38–192/MWh); Zambia and Zimbabwe (ZESCO, ZPC contracts) at NamPower's average import price (€95/MWh), because per-contract prices are not published. Exports earn the SAPP price capped at €95/MWh, so contract imports are not resold. Annual trade and fuel imports are unbounded; the yearly export limit is set explicitly to unbounded, because zen-creator's default of 0 blocks all exports.
- **Plant costs:** Van Eck and Anixas I fixed and variable O&M come from the NIRP 2022 report (2020–2021 data), scaled to 2023 prices with the Bank of Namibia CPI (167.3/140.6 = 1.1899); NIRP variable O&M excludes fuel. Anixas I variable O&M is "3 x N$1.55/kWh", applied as N$4.65/kWh. Van Eck coal costs N$2,227/t (NamPower FY2022/23). Anixas I uses an estimated 2023 delivered HFO price of N$306.5/GJ: the 2023 NW Europe FOB market price (INSEE) plus the NIRP 2020 delivery cost scaled with CPI. Exchange rates are Bank of Namibia annual averages: 19.9534 N$/EUR (2023) and 18.7695 N$/EUR (2020). Hydro, PV and wind O&M are not yet included.
- **Fleet:** existing renewable capacity is limited to the 2023 roster; the future-expansion list is not included.

## Current results (objective €180.18M)
- **Van Eck** (about €151/MWh) runs 38.1 GWh, all in November, when SAPP costs €192/MWh and the Zambia line is full; NamPower reported 44.3 GWh (FY2023/24).
- **Anixas I** (about €400/MWh) is never cheaper than imports and runs 0 GWh, against 5–6 GWh reported (FY2022/23 and FY2023/24); monthly prices are too smooth to capture its short emergency runs.
- **Imports:** 1,809 GWh via South Africa (peak 573 MW, below the 575 MW limit) and 388 GWh via Zambia (September–November only, at the 180 MW limit for 2,027 hours); Zimbabwe supplies nothing, because its route crosses two lines at the same price as Zambia. NamPower actually bought about 676 GWh from Eskom and SAPP and 1,808 GWh from ZESCO and ZPC: SAPP is cheaper than the contract price in most months, and contract volumes (take-or-pay) are not modeled.
- **Exports:** 11.6 GWh of renewable surplus, against 198 GWh reported (FY2022/23).
- **Domestic generation:** hydro 1,323 GWh, PV 480.1 GWh, wind 27.9 GWh.

## Next steps
1. Verify NIRP plant O&M assumptions against NamPower data; source O&M for hydro, PV, and wind where applicable. The NIRP variable O&M excludes fuel, so fuel and O&M are modeled as separate costs.
2. Refine trade: source per-contract import prices for Eskom, ZESCO and ZPC (only NamPower's average is public) and contract volumes or take-or-pay terms, so the split of imports between the neighbours becomes meaningful (Zimbabwe currently supplies nothing); consider hourly SAPP prices instead of monthly averages; add Angola (400 kV Kunene–Cahama link, planned but not built) and Botswana (distribution-level links only; 0.4 GWh from BPC in 2023) if they become relevant; confirm the SAPP limits' date and the export-direction limits; add line losses. Note that 2023 imports via Zambia (ZESCO 1,478 GWh plus ZPC 330 GWh, about 206 MW on average) exceed what the 180 MW SAPP limit allows over a year (1,577 GWh), so check whether part of this energy is wheeled through South Africa or the Caprivi Link (300 MW HVDC) carries more.
3. Replace the estimated 2023 delivered HFO price with NamPower's actual procurement price if it becomes available, and check whether Anixas I burns HFO or VLSFO; confirm the trade-price inputs.
4. Compare modeled calendar-year 2023 generation and trade against observed values; keep fiscal-year figures labeled as proxies.
5. Rebuild and solve after the remaining inputs are sourced, then review dispatch and energy balance.
