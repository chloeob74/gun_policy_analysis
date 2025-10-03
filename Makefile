.PHONY: all fetch clean process all

all: fetch clean

fetch:
		Rscript scripts/R/00_fetch.R \
		--mortality "data-table.csv" \
		--laws "TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"
		
clean process:
		Rscript scripts/R/02_clean_merge.R