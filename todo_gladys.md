## Update to latest Zen creator version
- Update your environment to the newest Zen creator version (2.1.0 or newer):
  ```
  pip install --upgrade zen-creator
  pip show zen-creator
  ```
  
## Current scope
- The model is a fixed-fleet 2023 snapshot. Historical annual trade volumes are stored for reference but are not enforced as dispatch limits.
- Fuel and electricity trade prices are included. Van Eck's variable and fixed O&M and Anixas I fixed O&M are included as NIRP benchmarks. Anixas I uses the NIRP 2020 HFO price proxy; its NIRP variable O&M entry is recorded but not applied pending unit clarification. Fuel imports and cross-border electricity trade remain unbounded until physical limits are sourced.
- Manual dispatch assumptions have been removed; dispatch is cost-driven. Plant operating costs remain incomplete.
- Existing renewable capacity is limited to the 2023 roster. The separate future-expansion list is not included in the active fleet.

## Next steps
1. Verify NIRP plant O&M assumptions against NamPower data; source O&M for hydro, PV, and wind where applicable, and clarify Anixas's “3 x N$1.55/kWh” VO&M entry.
2. Source physical import/export limits and schedules for Namibia's cross-border interconnectors, then represent neighboring systems and border flows.
3. Replace the 2020 NIRP HFO-price proxy with an actual 2023 delivered HFO/VLSFO price if procurement data or a defensible market series becomes available; confirm the exchange rate and trade-price inputs.
4. Compare modeled calendar-year 2023 generation and trade against observed values; keep fiscal-year figures labeled as proxies.
5. Rebuild and solve after the remaining inputs are sourced, then review dispatch and energy balance.
