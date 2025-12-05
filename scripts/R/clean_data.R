## ----setup, include=FALSE--------------------------------------------------------------------------
knitr::opts_chunk$set(echo = TRUE)
library(readxl)
TL_A243_2_v3_State_Firearm_Law_Database_5_0 <- read_excel("TL-A243-2-v3 State Firearm Law Database 5.0.xlsx", sheet = "Database")
data.table <- read.csv("data-table.csv")


## --------------------------------------------------------------------------------------------------
library(tidyverse)
library(skimr)
library(corrplot)
library(VIM)
library(plotly)
library(janitor)
library(lubridate)
library(recipes)
library(rsample)


## --------------------------------------------------------------------------------------------------
# Load the CSV file (contains firearm death rates)
mortality_data <- data.table

# Load Excel file (contains state firearm policies database)
law_data <- TL_A243_2_v3_State_Firearm_Law_Database_5_0


## --------------------------------------------------------------------------------------------------
# Standardize column names of law data
law_data <- law_data %>%
  janitor::clean_names()


## --------------------------------------------------------------------------------------------------
# Index subset of certain columns of law data
law_data2 <- law_data[, c("law_id", "state", "effective_date_year", 
                          "law_class_num", "law_class", "law_class_subtype", 
                          "effect", "type_of_change")]


## --------------------------------------------------------------------------------------------------
library(datasets)
# Add a new column to mortality_data with the full state name (mapped from abbreviations)
mortality_data$STATE_NAME <- datasets::state.name[match(toupper(mortality_data$STATE), datasets::state.abb)]
mortality_data$STATE_NAME[is.na(mortality_data$STATE_NAME)] <- "District of Columbia"


## --------------------------------------------------------------------------------------------------
# Convert "DEATHS" column to numeric type
mortality_data <- mortality_data %>%
  mutate(DEATHS = as.numeric(gsub("[^0-9.]", "", DEATHS)))


## --------------------------------------------------------------------------------------------------
# Clean law data
law_data2 <- law_data2 %>%
  # clean and standardize categorical variables
  mutate(
    law_class = str_trim(str_to_title(law_class)),
    law_class_subtype = str_trim(str_to_title(law_class_subtype)),
    effect = str_trim(str_to_title(effect)),
    type_of_change = str_trim(str_to_title(type_of_change))
  )


## --------------------------------------------------------------------------------------------------
# Create a complete grid of state-year combinations
state_year_grid <- mortality_data %>%
  distinct(STATE_NAME, YEAR) %>%
  rename(state = STATE_NAME, year = YEAR)


## --------------------------------------------------------------------------------------------------
# Create law strength scoring system
# Restrictive laws: +1 point (increase gun control)
# Permissive Laws = -1 point (decrease gun control)
# Handle repeals by reducing the score appropriately

law_scores <- law_data2 %>%
  mutate(
    law_score = case_when(
      effect == "Restrictive" & type_of_change %in% c("Implement", "Modify") ~ 1,
      effect == "Permissive" & type_of_change %in% c("Implement", "Modify") ~ -1,
      type_of_change == "Repeal" & effect == "Restrictive" ~ -1, # Repealing restrictive law = less control
      type_of_change == "Repeal" & effect == "Permissive" ~ 1, # Repealing permissive law = more control
      TRUE ~ 0 # Handle "see note" and other cases
    )
  ) %>%
  # Remove laws with zero score that cannot be categorized
  filter(law_score != 0)


## --------------------------------------------------------------------------------------------------
# For each state-year combination, calculate cumulative law strength
# A law affects all years from its effective year and onward

law_strength_by_year <- state_year_grid %>%
  left_join(
    law_scores %>% select(law_id, state, effective_date_year, law_class, law_class_subtype, effect, type_of_change, law_score),
    by = "state",
    relationship = "many-to-many"
  ) %>%
  # A law affects this year if its effective year is <= current year
  filter(effective_date_year <= year | is.na(effective_date_year)) %>%
  group_by(state, year) %>%
  summarise(
    # Overall law strength score (restrictive laws - permissive laws)
    law_strength_score = sum(law_score, na.rm = TRUE),
    # Count different type of laws
    restrictive_laws = sum(law_score == 1, na.rm = TRUE),
    permissive_laws = sum(law_score == -1, na.rm = TRUE),
    total_law_changes = sum(!is.na(law_score)),
    # unique law classes affected
    unique_law_classes = n_distinct(law_class, na.rm = TRUE),
    .groups = 'drop'
  )


## --------------------------------------------------------------------------------------------------
# Create law strength by law class
law_strength_by_class <- state_year_grid %>%
  left_join(
    law_scores %>% select(law_id, state, effective_date_year, law_class, law_score),
    by = "state",
    relationship = "many-to-many"
  ) %>%
  filter(effective_date_year <= year | is.na(effective_date_year)) %>%
  group_by(state, year, law_class) %>%
  summarise(
    class_strength = sum(law_score, na.rm = TRUE),
    .groups = 'drop'
  ) %>%
  # Pivot to wide format for each law class
 pivot_wider(
   names_from = law_class,
   values_from = class_strength,
   values_fill = 0,
   names_prefix = "strength_"
   ) %>%
  janitor::clean_names()



## --------------------------------------------------------------------------------------------------
# Combine all law strength measures
law_strength_final <- law_strength_by_year %>%
  left_join(law_strength_by_class, by = c("state", "year"))
  
## --------------------------------------------------------------------------------------------------
# Merge mortality data with law strength data

gun_data_final <- mortality_data %>%
  left_join(law_strength_final, by = c("STATE_NAME" = "state", "YEAR" = "year")) %>%
  janitor::clean_names()


gun_data_final2 <- gun_data_final %>%
  select(-url) %>%
  mutate(
    state = as.factor(state),
    year = as.integer(year)
  )


# year-over-year changes by state 
# changes in rate and change in law strength by time 

gun_data_final3 <- gun_data_final2 %>%
  arrange(state, year) %>%
  group_by(state) %>%
  mutate(
    rate_change = rate - lag(rate),
    law_strength_change = law_strength_score - lag(law_strength_score)
  ) %>%
  ungroup()

# Save the cleaned dataset

write_csv(gun_data_final4, "firearm_data_cleaned.csv")

