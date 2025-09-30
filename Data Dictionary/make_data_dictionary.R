# DS 6021 Final Project: Firearm Laws and Mortality Data Dictionary
# This script creates a comprehensive data dictionary for all datasets

library(tidyverse)
library(openxlsx)

# Create a comprehensive data dictionary
create_data_dictionary <- function() {
  
  # SHEET 1: Mortality Data Variables
  mortality_vars <- tibble(
    Variable_Name = c("YEAR", "STATE", "RATE", "DEATHS", "URL"),
    Data_Type = c("Integer", "Character", "Numeric", "Character/Numeric", "Character"),
    Description = c(
      "Year of the mortality data observation",
      "State name (standardized to title case)",
      "Firearm mortality rate per 100,000 population",
      "Total number of firearm deaths (may be numeric or contain ranges/notes)",
      "Source URL for the original data"
    ),
    Source = rep("Original mortality dataset (data-table.csv)", 5),
    Notes = c(
      "Time dimension for panel data analysis",
      "Used as key for merging with law data",
      "Primary dependent variable for analysis",
      "Raw count data, may need cleaning for numeric analysis",
      "Reference for data verification and citation"
    )
  )
  
  # SHEET 2: Original Law Data Variables
  law_vars <- tibble(
    Variable_Name = c("law_id", "state", "effective_date_year", "law_class", 
                      "law_class_subtype", "effect", "type_of_change"),
    Data_Type = c("Character", "Character", "Integer", "Character", 
                  "Character", "Character", "Character"),
    Description = c(
      "Unique identifier for specific firearm law",
      "State where the law was enacted (standardized to title case)",
      "Year when the law became effective",
      "Broad category of the firearm law (e.g., Background Check, Permit)",
      "More specific subcategory within the law class",
      "Whether the law is Restrictive (increases gun control) or Permissive (decreases gun control)",
      "Type of legislative action: Implemented, Modify, Repeal, or See Note"
    ),
    Source = rep("Original law database (TLA2432v3 State Firearm Law Database 5.0.xlsx)", 7),
    Notes = c(
      "Each row represents one law change in one state",
      "Used as key for merging with mortality data",
      "Laws remain effective in subsequent years unless repealed",
      "Used to group laws for category-specific analysis",
      "Provides granular detail within broader law classes",
      "Critical for determining direction of law strength impact",
      "Majority are 'Implemented' - new laws taking effect"
    )
  )
  
  # SHEET 3: Computed Law Strength Variables
  law_strength_vars <- tibble(
    Variable_Name = c(
      "law_strength_score", "restrictive_laws", "permissive_laws", "total_law_changes",
      "unique_law_classes", "strength_[law_class]", "class_count_[law_class]", 
      "class_restrictive_[law_class]", "class_permissive_[law_class]"
    ),
    Data_Type = c(
      "Integer", "Integer", "Integer", "Integer", 
      "Integer", "Integer", "Integer", "Integer", "Integer"
    ),
    Description = c(
      "Net law strength score: restrictive laws (+1) minus permissive laws (-1). Higher = more gun control",
      "Count of restrictive laws effective in this state-year",
      "Count of permissive laws effective in this state-year", 
      "Total number of law changes effective in this state-year",
      "Number of different law classes with effective laws",
      "Net strength score for specific law class (e.g., strength_background_check)",
      "Total count of laws in specific class (e.g., class_count_permit)",
      "Count of restrictive laws in specific class",
      "Count of permissive laws in specific class"
    ),
    Source = c(
      rep("Computed from law database", 5),
      rep("Computed by law class from original data", 4)
    ),
    Notes = c(
      "Primary predictor variable - measures overall law restrictiveness",
      "Used to separately analyze impact of gun control measures",
      "Used to separately analyze impact of gun rights measures",
      "Measures total legislative activity regardless of direction",
      "Measures diversity of law types - broader vs focused approaches",
      "Allows analysis of which types of laws are most effective",
      "Raw counts by law category for detailed analysis",
      "Category-specific restrictive law analysis",
      "Category-specific permissive law analysis"
    )
  )
  
  # SHEET 4: Combined Dataset Variables
  combined_vars <- tibble(
    Variable_Name = c(
      "STATE", "YEAR", "RATE", "DEATHS", "URL",
      "law_strength_score", "restrictive_laws", "permissive_laws",
      "All law class variables..."
    ),
    Data_Type = c(
      "Character", "Integer", "Numeric", "Character", "Character",
      "Integer", "Integer", "Integer", "Various"
    ),
    Description = c(
      "State name (from mortality data)",
      "Year (from mortality data)", 
      "Firearm mortality rate per 100,000 (dependent variable)",
      "Total firearm deaths (from mortality data)",
      "Source URL (from mortality data)",
      "Net law strength score (primary predictor)",
      "Count of restrictive laws effective",
      "Count of permissive laws effective", 
      "All law class strength and count variables as detailed above"
    ),
    Source = c(
      rep("Merged from mortality and law datasets", 5),
      rep("Computed from law data", 4)
    ),
    Notes = c(
      "Analysis-ready dataset combining all variables",
      "Panel data structure: multiple years per state",
      "Key dependent variable for all predictive models",
      "May contain missing values or text ranges",
      "For data source documentation",
      "Main predictor of interest for research questions",
      "Allows separate analysis of gun control effects",
      "Allows separate analysis of gun rights effects",
      "Enables detailed analysis by law and/or class type"
    )
  )
  
 
  # SHEET 5: Data Quality and Limitations
  data_quality <- tibble(
    Issue = c(
      "Missing Values", "State Name Matching", "Temporal Coverage", 
      "Law Effectiveness Timing", "Mortality Data Granularity", 
      "Confounding Variables", "Causality Interpretation", "Data Currency"
    ),
    Description = c(
      "Some state-year combinations may lack law data or mortality data",
      "Ensure consistent state naming between mortality and law datasets",
      "Law data and mortality data may cover different time periods",
      "Laws may take time to affect mortality rates (lagged effects)",
      "Mortality rates are annual aggregates, may mask seasonal patterns",
      "Demographics, economics, urbanization not included in current analysis",
      "Correlation does not imply causation - cannot prove laws cause mortality changes",
      "Data may not reflect most recent law changes or mortality statistics"
    ),
    Mitigation = c(
      "Use complete cases analysis; document missing data patterns",
      "Standardize all state names to title case; manual verification",
      "Focus analysis on overlapping time periods; document coverage",
      "Consider lagged variables (e.g., law_strength_score lagged 1-2 years)",
      "Annual data appropriate for policy analysis timescale",
      "Acknowledge limitations; suggest future work with additional covariates",
      "Use careful language: 'associated with' rather than 'causes'",
      "Document data vintage; acknowledge currency limitations"
    ),
    Impact_on_Analysis = c(
      "Reduces sample size; may introduce bias if missing not at random",
      "Failed merges lose observations; inaccurate merges introduce noise",
      "Limits time trend analysis; reduces statistical power",
      "May underestimate law effects if using concurrent measures",
      "Appropriate for research question scale",
      "Results may conflate law effects with other state characteristics",
      "Limits policy conclusions that can be drawn",
      "Findings may not reflect current policy landscape"
    )
  )
  
  # Create workbook and add sheets
  wb <- createWorkbook()
  
  addWorksheet(wb, "1_Mortality_Variables")
  addWorksheet(wb, "2_Law_Variables") 
  addWorksheet(wb, "3_Computed_Variables")
  addWorksheet(wb, "4_Combined_Dataset")
  addWorksheet(wb, "5_Data_Quality")
  
  # Write data to sheets
  writeData(wb, "1_Mortality_Variables", mortality_vars)
  writeData(wb, "2_Law_Variables", law_vars)
  writeData(wb, "3_Computed_Variables", law_strength_vars)
  writeData(wb, "4_Combined_Dataset", combined_vars)
  writeData(wb, "5_Data_Quality", data_quality)
  
  # Format headers
  sheets <- c("1_Mortality_Variables", "2_Law_Variables", "3_Computed_Variables", 
              "4_Combined_Dataset", "5_Data_Quality")
  
  for(sheet in sheets) {
    # Bold headers
    addStyle(wb, sheet, createStyle(textDecoration = "bold"), rows = 1, cols = 1:10)
    # Auto-width columns
    setColWidths(wb, sheet, cols = 1:10, widths = "auto")
    # Wrap text
    addStyle(wb, sheet, createStyle(wrapText = TRUE), rows = 1:1000, cols = 1:10, gridExpand = TRUE)
  }
  
  return(wb)
}

# GENERATE THE DATA DICTIONARY

cat("Creating comprehensive data dictionary...\n")
data_dict_wb <- create_data_dictionary()

# Save the workbook
saveWorkbook(data_dict_wb, "Firearm_Data_Dictionary.xlsx", overwrite = TRUE)

cat("Data dictionary saved as 'Firearm_Data_Dictionary.xlsx'\n")
cat("\nThe dictionary includes 5 sheets:\n")
cat("1. Mortality Variables - Original mortality data columns\n")
cat("2. Law Variables - Original law database columns\n") 
cat("3. Computed Variables - Derived law strength measures\n")
cat("4. Combined Dataset - Final analysis dataset structure\n")
cat("5. Data Quality - Limitations and considerations\n")


# CREATE SIMPLIFIED REFERENCE CARD
# Also create a quick reference as a CSV for easy viewing
quick_ref <- tibble(
  Variable = c(
    "RATE", "law_strength_score", "restrictive_laws", "permissive_laws",
    "unique_law_classes", "STATE", "YEAR"
  ),
  Type = c("Numeric", "Integer", "Integer", "Integer", "Integer", "Character", "Integer"),
  Role = c("Dependent Variable", "Main Predictor", "Predictor", "Predictor", "Predictor", "Grouping", "Time"),
  Description = c(
    "Firearm mortality per 100K (what we're trying to predict)",
    "Net law strength: restrictive (+) minus permissive (-) laws",
    "Count of restrictive (gun control) laws in effect",
    "Count of permissive (gun rights) laws in effect", 
    "Number of different law categories with active laws",
    "State name for grouping and geographic analysis",
    "Year for time trends and panel data structure"
  ),
  Use_In_Models = c(
    "y variable", "Primary x variable", "Additional predictor", "Additional predictor",
    "Diversity measure", "Grouping/clustering", "Time trend control"
  )
)

write_csv(quick_ref, "Key_Variables_Quick_Reference.csv")

cat("\nAlso created 'Key_Variables_Quick_Reference.csv' for the most important variables.\n")


# PRINT SUMMARY FOR USER
cat("\n=== DATA DICTIONARY SUMMARY ===\n")
cat("Your datasets contain several types of variables:\n\n")

cat("Original:\n")
cat("- Mortality: YEAR, STATE, RATE, DEATHS, URL\n")
cat("- Laws: law_id, state, effective_data_year, law_class, effect, type_of_change\n\n")

cat("Computed Measures:\n")
cat("- law_strength_score: Main predictor (restrictive - permissive laws)\n")
cat("- restrictive_laws & permissive_laws: Separate counts by direction\n")
cat("- Law class variables: Strength/counts by category (background check, permit, etc.)\n\n")

cat("Ffor Analysis:\n")
cat("- Dependent variable: RATE (firearm mortality per 100K)\n")
cat("- Main predictor: law_strength_score\n")
cat("- Panel structure: Multiple years per state\n")
cat("- Rich detail: Law categories, restrictive vs permissive effects\n\n")
