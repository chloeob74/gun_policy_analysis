#!/usr/bin/env Rscript

# Usage:
#   Rscript scripts/R/00_fetch.R \
#     --mortality "data-table.csv" \
#     --laws "TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"

suppressPackageStartupMessages({
  library(optparse)
  library(fs)
})

option_list <- list(
  make_option("--mortality", type = "character", default = "data-table.csv",
              help = "Path to the mortality CSV (CDC) [default %default]"),
  make_option("--laws", type = "character", default = "TL-A243-2-v3 State Firearm Law Database 5.0.xlsx",
              help = "Path to the firearm law Excel workbook [default %default]")
)

args <- parse_args(OptionParser(option_list = option_list))

# Ensure folder structure
dir_create("Data")
dir_create("Data/raw")
dir_create("Data/interim")
dir_create("Data/processed")

# Copy/standardize names under Data/raw/

raw_mortality <- "Data/raw/data-table.csv"
raw_laws_xlsx <- "Data/raw/TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"

if (file_exists(args$mortality)) {
  file_copy(args$mortality, raw_mortality, overwrite = TRUE)
} else if (!file_exists(raw_mortality)) {
  stop("Could not find mortality CSV at '", args$mortality,
       "' and there is no existing '", raw_mortality, "'.")
}

if (file_exists(args$laws)) {
  file_copy(args$laws, raw_laws_xlsx, overwrite = TRUE)
} else if (!file_exists(raw_laws_xlsx)) {
  stop("Could not find law database at '", args$laws,
       "' and there is no existing '", raw_laws_xlsx, "'.")
}

cat("Fetch step complete:\n",
    " - ", raw_mortality, "\n",
    " - ", raw_laws_xlsx, "\n", sep = "")