## DS 6021 Machine Learning Project
Barnes, Chloe;
Dallas, Ryan;
Luedtke, Terry;
Robinson, Shiraz;
Threat, Tiandre

## Data Sources
1. [CDC mortality](https://www.cdc.gov/nchs/state-stats/deaths/firearms.html):
    - *Description:*
    - *Key fields:* `STATE`, `YEAR`, `RATE (per 100K)`, `DEATHS`
    - *File:* `data-table.csv`
2. [RAND State Firearm Database](https://www.rand.org/pubs/tools/TLA243-2-v3.html)
    - *Key fields:* `Law ID`, `State`, `Law Class`, `Effect (Restrictive/Permissive)`, `Type of Change(Implement/Modify/Repeal)`, `Effective Date Year`
    - *File:* `TL-A243-2-v3 State Firearm Law Database 5.0.xlsx` (sheet: `Database`)

## Feature Engineering Summary
- Score Rules:
    - +1: `Effect == Restrictive` & `Type of Change in {Implement, Modify}`
    - -1: `Effect == Permissive` & `Type of Change in {Implement, Modify}`
    - **Repeal** flips sign accordingly (repeal restrictive -> -1; repeal permissive -> +1)
- Annual roll-up:
    - `law_strength_score` (sum of scores per state-year)
    - counts: `restrictive_laws`, `permissive_laws`, `total_law_changes`
    - per-class strength score (wide columns)
- Outcome helpers
    - `rate_change`, `law_strength_change` (year-over-year within state)
    - `restrictive_ratio`, `permissive_ratio` = proportion of changes within year