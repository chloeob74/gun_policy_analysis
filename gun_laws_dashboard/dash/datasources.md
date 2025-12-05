## Law Scoring System

The core of the data engineering work is the construction of a law strength scoring system that translates many individual law changes into a single nuneric indicator (and related features) of the firearm policy environment for each state-year.

### Design Choices and rationale

The law database contains one row per law, with:
  - Whether the law is **Restrictive** (tightens guns regulations) or **Permissive** (loosens regulations) -- stored in `effect`.
  - What type of change occured -- `type_of_change` (e.g., `Implement`, `Modify`, or `Repeal`).

To turn this into a consistent, interpretable score, we used a simple symmetric scoring scheme:
  - Restrictive law implementation/modification -> +1
  - Permissive law implementation/modification -> -1
  - Repeal of a restrictive law -> -1
  - Repeal of a permissive law -> +1

Formally, for each law row we defined:

```r
law_scores <- law_data2 %>%
  mutate(
    law_score = case_when(
      effect == "Restrictive" & type_of_change %in% c("Implement", "Modify") ~ 1,
      effect == "Permissive" & type_of_change %in% c("Implement", "Modify") ~ -1,
      type_of_change == "Repeal" & effect == "Restrictive" ~ -1,
      type_of_change == "Repeal" & effect == "Permissive" ~ 1,
      TRUE ~ 0
    )
  ) %>%
  filter(law_score != 0)
```

Why this makes sense:
  - The sign captures the direction of the change:
      - Positive values indicate the law makes the environment more restrictive overall.
      - Negative values indicate the law makes the environment becomes more permissive overall.
  - The magnitude (fixed at 1) assumes each law change contributes equally to the net policy climate. This is a simplification but has two advantages:
      - It keeps the measure easy to interpret: the total is just the net count of "restrictive minus permissive" actions.
      - It avoids having to arbitrarily weight different law classes without strong prior justification.
  - Repeals are handled symmetrically:
      - Repealing a restrictive law undoes restrictive policy, so it moves the environment in a more permissive direction (-1).
      - Repealing a permissive law decreases permissiveness, effectively making the environnment more restrictive (+1).

Cases where the `effect` and `type_of_change` could not be clearly categorized (e.g. "See note") are assigned a score of 0 and then removed before aggregation:

```r
filter(law_score != 0)
```

This avoids forcing ambiguous entries into one direction or the other.

### Cumulative law strength by state and year
The key assumption is that once a law is implemented, its effect persists in all subsequent years until poentially offset by later changes. To reflect this, we:
1. Joined the scored laws (`law_score`) onto the full `state_year_grid` by `state`.
2. For each state-year, kept only laws with `effective_date_year <= year` (they are "in force" by that year)
3. Summed scores within each state-yar to get cumulative strength.

```r
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
```
Interpretation:
  - `law_strength_score` - new accumulated score:
    > (# restrictive implementations + # permissive repeals) = (# permissive implementations + # restrictive repeals)
    > Higher values -> more restrictive policy environment overall
  - `restrictive_laws` - count of positive-scored law changes in that state-year (laws making policy more restrictive).
  - `permissive_laws` - count of negative-scored law change in that state-year (laws making policy more permissive).
  - `total_law_changes` - total number of scored law changes that are in effect in that state-year
  - `unique_law_classes` - number of distinct policy classes (e.g. background checks, concealed carry) represented by those laws, giving a sense of breadth.

### Cumulative law strength by state and year
The key assumption is that once a law is implemented, its effect persists in all subsequent years until potentially offset by later changes. To reflect this, we:
  1. Joined the scored laws (`law_score`) onto the full `state_year_grid` by `state`.
  2. For each state-year, kept only laws with `effective_date_year <= year` (they are "in force" by that year)
  3. Summed scores within each state-year to get cumulative strength.

```r
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
```
Interpretation:
  - `law_strength_score` - new accumulated score:
    > (# restrictive implementations + # permissive repeals) = (# permissive implementations + # restrictive repeals)
    > Higher values -> more restrictive policy environment overall
  - `restrictive_laws` - count of positive-scored law changes in that state-year (laws making policy more restrictive).
  - `permissive_laws` - count of negative-scored law changes in that state-year (laws making policy more permissive).
  - `total_law_changes` - total number of scored law changes that are in effect in that state-year
  - `unique_law_classes` - number of distinct policy classes (e.g. background checks, concealed carry) represented by those laws, giving a sense of breadth.

### Law Strength by law class

```r
To see which policy areas are driving the overall score, we also computed class-specific cumulative scores:
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
 pivot_wider(
   names_from = law_class,
   values_from = class_strength,
   values_fill = 0,
   names_prefix = "strength_"
   ) %>%
  janitor::clean_names()
```

  - Each resulting column `strength_<law_class>` is the net score for that specific law class in a given state-year.
  - Conceptual Example: `strength_background_checks` is positive if, overtime, background-check laws in the state have become more restrictive than permissive, and megative is the reverse is true. 
  - Reason: this lets us disentangle overall law strength into policy subdomains and analyze whether certain types of laws (e.g. background checks, concealed carry, castle doctrine) are more strongly associated with mortality patterns. 

Finally, I combined the overall and class-specific measures:
```r
law_strength_final <- law_strength_by_year %>%
  left_join(law_strength_by_class, by = c("state", "year"))
```

### Year-over-year change variables

To capture how things change over time within a state, I computed differences:

```r
gun_data_final3 <- gun_data_final2 %>%
  arrange(state, year) %>%
  group_by(state) %>%
  mutate(
    rate_change = rate - lag(rate),
    law_strength_change = law_strength_score - lag(law_strength_score)
  ) %>%
  ungroup()
```

  - `rate_change` – change in firearm death rate from the previous year within the same state.
  - `law_strength_change` – change in the overall law strength score from the previous year within the same state.

These variables are useful for looking at within-state dynamics (e.g., whether increases in law strength tend to precede or follow changes in mortality rates).