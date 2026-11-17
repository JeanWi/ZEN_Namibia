## Update to latest Zen creator version
- Update your environment to the newest Zen creator version (2.1.0 or newer):
  ```
  pip install --upgrade zen-creator
  pip show zen-creator
  ```
  
## Current scope
- The model is a fixed-fleet 2023 snapshot. Historical annual trade volumes are stored for reference but are not enforced as dispatch limits.
- Fuel and electricity trade prices are now included. Fuel imports and cross-border electricity trade remain unbounded until physical limits are sourced.
- Manual dispatch assumptions have been removed; dispatch is cost-driven. Plant operating costs remain incomplete.
- Existing renewable capacity is limited to the 2023 roster. The separate future-expansion list is not included in the active fleet.

## Next steps
1. Source plant operating costs for coal, Anixas fuel, hydro, PV, and wind where applicable.
2. Source physical import/export limits and schedules for Namibia's cross-border interconnectors, then represent neighboring systems and border flows.
3. Confirm the exchange rate and average trade/fuel prices in `costs_2023.csv`, especially the diesel-pump-price proxy for Anixas HFO.
4. Compare modeled calendar-year 2023 generation and trade against observed values; keep fiscal-year figures labeled as proxies.
5. Rebuild and solve after the remaining inputs are sourced, then review dispatch and energy balance.
