## Update to latest Zen creator version
- Update your environment to the newest Zen creator version (2.1.0 or newer):
  ```
  pip install --upgrade zen-creator
  pip show zen-creator
  ```
  
## Current scope
- The model is a fixed-fleet 2023 snapshot. Historical annual trade volumes are stored for reference but are not enforced as dispatch limits.
- Fuel and electricity trade prices are included. Van Eck's variable and fixed O&M and Anixas I's fixed and variable O&M are taken from the NIRP 2022 report, whose values are based on 2020–2021 data; they are scaled from 2020 to 2023 prices with the Bank of Namibia CPI (167.3/140.6 = 1.1899). Anixas I uses an estimated 2023 delivered HFO price (N$306.5/GJ): the 2023 NW Europe FOB market price plus the NIRP 2020 delivery cost scaled with CPI; the 2020 exchange rate of 18.7695 N$/EUR is an assumption. Its NIRP variable O&M ("3 x N$1.55/kWh") is applied as N$4.65/kWh (N$4,650/MWh). Fuel imports and cross-border electricity trade remain unbounded hourly and yearly until physical limits are sourced; the yearly export limit is set explicitly to unbounded, because zen-creator's default of 0 blocks all exports.
- Manual dispatch assumptions have been removed; dispatch is cost-driven. Hydro, PV and wind O&M are not yet included.
- With these costs, both thermal plants run 0 GWh in calendar 2023: Van Eck costs about €151/MWh and Anixas I about €400/MWh, against a flat €95/MWh import price. NamPower reported about 44 GWh from Van Eck (FY2023/24) and 5-6 GWh from Anixas I (FY2022/23 and FY2023/24). With a single flat import price the model cannot reproduce this peak and emergency use.
- Existing renewable capacity is limited to the 2023 roster. The separate future-expansion list is not included in the active fleet.

## Next steps
1. Verify NIRP plant O&M assumptions against NamPower data; source O&M for hydro, PV, and wind where applicable. The NIRP variable O&M excludes fuel, so fuel and O&M are modeled as separate costs.
2. Source physical import/export limits and schedules for Namibia's cross-border interconnectors, then represent neighboring systems and border flows.
3. Replace the estimated 2023 delivered HFO price with NamPower's actual procurement price if it becomes available, and check whether Anixas I burns HFO or VLSFO; verify the 2020 exchange rate (18.7695 N$/EUR); confirm the exchange rate and trade-price inputs.
4. Compare modeled calendar-year 2023 generation and trade against observed values; keep fiscal-year figures labeled as proxies.
5. Rebuild and solve after the remaining inputs are sourced, then review dispatch and energy balance.
