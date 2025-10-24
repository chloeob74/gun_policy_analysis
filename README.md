# A State-Level Firearm Policy Analysis

A reproducible pipeline to combine CDC mortality data with the **RAND State Firearm Law Database** to engineer policy-strength features and analyze outcomes. Includes a Makefile-driven workflow and a Shiny App.

## Overview
- **Goal:** Quantify relationships between policy changes and firearm mortality.
- **Data:** CDC mortality (state-year) + RAND State Firearm Laws Database (event-level).
- **Outputs:** Panel with .....
- **Reproducibility:** Makefile pipeline; large files via Git LFS.

## Repository Structure

## Environment & Setup
- R >= 4.5.1; packages: 'tidyverse', 'readxl', janitor', 'lubridate', 'datasets', 'readr'
- Optional: 'renv' for dependency pinning

```bash
# Install make (Windows: choco/scoop; macOSl Xcode CLT; Linux: apt/yum)
--make --version

# (optional) Initialize renv
R -q -e "install.packages('renv'); renv::init()"
```

## Makefile Workflow
Common targets
```
.PHONY: all fetch clean process all

all: fetch clean

fetch:
		Rscript scripts/R/00_fetch.R \
		--mortality "data-table.csv" \
		--laws "TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"
		
clean process:
		Rscript scripts/R/02_clean_merge.R
```
### Quick start
```
make           # runs fetch + clean
make fetch     # copy inputs to data/raw/
make process   # build data/processed/firearm_data_cleaned.csv
```
### Customizing inputs
```
Rscript scripts/R/00_fetch.R \
  --mortality "path/to/data-table.csv" \
  --laws "path/to/TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"
```

## Data Sources
1. [CDC mortality](https://www.cdc.gov/nchs/state-stats/deaths/firearms.html):
   - *Description:*
   - *Key fields:* `STATE`, `YEAR`, `RATE`(per 100K), `DEATHS`
   - *File:* `data-table.csv`
2. [RAND State Firearm Database](https://www.rand.org/pubs/tools/TLA243-2-v3.html)
    - *Key fields:* `Law ID`, `State`, `Law Class`, `Effect`(Restrictive/Permissive), `Type of Change(Implement/Modify/Repeal)`, `Effective Date Year`
    - *File:* `TL-A243-2-v3 State Firearm Law Database 5.0.xlsx` (sheet: `Database`)
    
> Place source files anywhere and run `make fetch` to stage standardized copies into `data/raw/`.

## Feature Engineering Summary
- Score Rules:
  - +1: `Effect == Restrictive` & `Type of Change ∈ {Implement, Modify}`
  - −1: `Effect == Permissive` & `Type of Change ∈ {Implement, Modify}`
  - **Repeal** flips sign accordingly (repeal restrictive -> −1; repeal permissive -> +1)
- Annual roll-up:
Annual roll-up:
  - `law_strength_score` (sum of scores per state-year)
  - counts: `restrictive_laws`, `permissive_laws`, `total_law_changes`
  - per-class strength and counts (wide columns)
- Outcome helpers
  - `high_risk`: 1 if `rate >= 75th` percentile within year; else 0
  - `rate_change`, `law_strength_change` (year-over-year within state)
  - `restrictive_ratio`, `permissive_ratio` = proportion of changes within year
  
## Outputs
- `Data/processed/firearm_data_cleaned.csv`
- Schema .....

## Citation
...
