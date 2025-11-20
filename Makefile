# Makefile for firearm mortality and law data processing
#
# Usage:
#	make all:			- Run complete pipeline (R version)
#	make all-python 	- Run complete pipeline (Python version)
#	make fetch			- Run R fetch script only
# 	make fetch-python	- Run Python fetch script only
#	make clean			- Run R clean/merge script only
#	make clean-python	- Run Python clean/merge script only
#
# You can also run specific parts by calling the target nam

.PHONY: all all-python fectch fetch-python clean clean-python process process-python help

# Default target: run R pipeline
all: fetch clean

# Run Python pipeline
all-python: fetch-python clean-python

# R fetch target
fetch:
		Rscript scripts/R/01_fetch.R \
		--mortality "data-table.csv" \
		--laws "TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"

# Python fetch target
fetch-python:
		python3 scripts/py/00_fetch.py \
		--mortality "data-table.csv" \
		--laws "TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"

# R clean/merge target
clean process:
		Rscript scripts/R/01_clean_merge.R

# Python clean/merge target
clean-python process-python:
		python3 scripts/py/01_clean_merge.py

# Help target to show available commands
help:
	@echo "Available Targets:"
	@echo "  make all           - Run complete R pipeline (fetch + clean)"
	@echo "  make all-python    - Run complete Python pipeline (fetch + clean)"
	@echo "  make fetch         - Run R fetch script only"
	@echo "  make fetch-python  - Run Python fetch script only"
	@echo "  make clean         - Run R clean/merge script only"
	@echo "  make clean-python  - Run Python clean/merge script only"
	@echo ""
	@echo "Example:"
	@echo "  make fetch-python  - Only fetch data using Python"
	@echo " make all-python     - Run full python pipeline"
