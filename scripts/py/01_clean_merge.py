#!/usr/bin/env python3

"""
Clean and merge mortality and firearm law data.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys


def main():
    # ---------- Inputs ----------
    raw_mortality = Path('Data/raw/data-table.csv')
    raw_laws_xlsx = Path('Data/raw/TL-A243-2-v3 State Firearm Law Database 5.0.xlsx')
    laws_sheet = 'Database'
    
    # ---------- Output ----------
    out_path = Path('Data/processed/firearm_data_cleaned_new_py.csv')
    
    # ---------- Load ----------
    if not raw_mortality.exists():
        print(f"Error: Missing input: {raw_mortality}", file=sys.stderr)
        sys.exit(1)
    if not raw_laws_xlsx.exists():
        print(f"Error: Missing input: {raw_laws_xlsx}", file=sys.stderr)
        sys.exit(1)
    
    print("Loading data...")
    mortality_data = pd.read_csv(raw_mortality)
    law_data = pd.read_excel(raw_laws_xlsx, sheet_name=laws_sheet)
    
    # ---------- Prep ----------
    # Clean column names (lowercase, replace spaces with underscores)
    law_data.columns = law_data.columns.str.lower().str.replace(' ', '_')
    
    # Keep specific columns
    law_data2 = law_data[[
        'law_id', 'state', 'effective_date_year',
        'law_class_num', 'law_class', 'law_class_subtype',
        'effect', 'type_of_change'
    ]].copy()
    
    # Map state abbreviations to full names
    # Create mapping dictionary from state abbreviations to full names
    state_abbrev_to_name = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
        'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
        'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
        'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
        'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
        'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
        'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
        'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
        'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
        'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
        'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
    }
    
    mortality_data['STATE_NAME'] = mortality_data['STATE'].str.upper().map(state_abbrev_to_name)
    # Fill DC if not already mapped
    mortality_data['STATE_NAME'] = mortality_data['STATE_NAME'].fillna('District of Columbia')
    
    # Convert "DEATHS" column to numeric (remove non-numeric characters)
    mortality_data['DEATHS'] = pd.to_numeric(
        mortality_data['DEATHS'].astype(str).str.replace(r'[^0-9.]', '', regex=True),
        errors='coerce'
    )
    
    # Clean and standardize categorical columns in laws
    for col in ['law_class', 'law_class_subtype', 'effect', 'type_of_change']:
        law_data2[col] = law_data2[col].astype(str).str.strip().str.title()
    
    # Create state-year grid based on mortality data
    state_year_grid = mortality_data[['STATE_NAME', 'YEAR']].drop_duplicates()
    state_year_grid = state_year_grid.rename(columns={'STATE_NAME': 'state', 'YEAR': 'year'})
    
    # ---------- Scoring ----------
    print("Calculating law strength scores...")
    
    # Create law strength scoring system
    def calculate_law_score(row):
        effect = row['effect']
        change_type = row['type_of_change']
        
        # Restrictive laws (implement/modify): +1 point (increase gun control)
        if effect == 'Restrictive' and change_type in ['Implement', 'Modify']:
            return 1
        # Permissive Laws (implement/modify): -1 point (decrease gun control)
        elif effect == 'Permissive' and change_type in ['Implement', 'Modify']:
            return -1
        # Repealing restrictive law = less control
        elif change_type == 'Repeal' and effect == 'Restrictive':
            return -1
        # Repealing permissive law = more control
        elif change_type == 'Repeal' and effect == 'Permissive':
            return 1
        else:
            return 0  # Handle "see note" and other cases
    
    law_scores = law_data2.copy()
    law_scores['law_score'] = law_scores.apply(calculate_law_score, axis=1)
    
    # Remove laws with zero score that cannot be categorized
    law_scores = law_scores[law_scores['law_score'] != 0]
    
    # For each state-year combination, calculate cumulative law strength
    # A law affects all years from its effective year and onward
    
    # Merge state_year_grid with law_scores (many-to-many)
    law_year_merged = state_year_grid.merge(
        law_scores[['law_id', 'state', 'effective_date_year', 'law_class', 
                   'law_class_subtype', 'effect', 'type_of_change', 'law_score']],
        on='state',
        how='left'
    )
    
    # A law affects this year if its effective year is <= current year
    law_year_merged = law_year_merged[
        (law_year_merged['effective_date_year'] <= law_year_merged['year']) |
        (law_year_merged['effective_date_year'].isna())
    ]
    
    # Calculate aggregated law strength by state and year
    law_strength_by_year = law_year_merged.groupby(['state', 'year']).agg(
        law_strength_score=('law_score', 'sum'),
        restrictive_laws=('law_score', lambda x: (x == 1).sum()),
        permissive_laws=('law_score', lambda x: (x == -1).sum()),
        total_law_changes=('law_score', 'count'),
        unique_law_classes=('law_class', 'nunique')
    ).reset_index()
    
    # Create law strength by law class (wide format)
    print("Creating law class features...")
    
    law_class_merged = state_year_grid.merge(
        law_scores[['law_id', 'state', 'effective_date_year', 'law_class', 'law_score']],
        on='state',
        how='left'
    )
    
    law_class_merged = law_class_merged[
        (law_class_merged['effective_date_year'] <= law_class_merged['year']) |
        (law_class_merged['effective_date_year'].isna())
    ]
    
    law_strength_by_class = law_class_merged.groupby(['state', 'year', 'law_class']).agg(
        class_strength=('law_score', 'sum')
    ).reset_index()
    
    # Pivot to wide format
    law_strength_by_class_wide = law_strength_by_class.pivot_table(
        index=['state', 'year'],
        columns='law_class',
        values='class_strength',
        fill_value=0
    ).reset_index()
    
    # Clean column names (add prefix and lowercase)
    law_strength_by_class_wide.columns = [
        col if col in ['state', 'year'] else f'strength_{col}'.lower().replace(' ', '_')
        for col in law_strength_by_class_wide.columns
    ]

    
    # Combine all law strength measures
    law_strength_final = law_strength_by_year.merge(
        law_strength_by_class_wide,
        on=['state', 'year'],
        how='left'
    )
    
    # ---------- Merge with mortality & features ----------
    print("Merging with mortality data...")
    
    gun_data_final = mortality_data.merge(
        law_strength_final,
        left_on=['STATE_NAME', 'YEAR'],
        right_on=['state', 'year'],
        how='left'
    )
    
    # Clean column names (lowercase, replace spaces)
    gun_data_final.columns = gun_data_final.columns.str.lower().str.replace(' ', '_')
    
    # Remove URL column if exists and convert types
    if 'url' in gun_data_final.columns:
        gun_data_final2 = gun_data_final.drop(columns=['url'])
    else:
        gun_data_final2 = gun_data_final.copy()
    
    gun_data_final2['state'] = gun_data_final2['state'].astype('category')
    gun_data_final2['year'] = gun_data_final2['year'].astype('int64')
    
    # Calculate year-over-year changes by state
    print("Calculating year-over-year changes...")
    
    gun_data_final3 = gun_data_final2.sort_values(['state', 'year']).copy()
    gun_data_final3['rate_change'] = gun_data_final3.groupby('state')['rate'].diff()
    gun_data_final3['law_strength_change'] = gun_data_final3.groupby('state')['law_strength_score'].diff()
    
    # ---------- Save ----------
    out_path.parent.mkdir(parents=True, exist_ok=True)
    gun_data_final3.to_csv(out_path, index=False)
    print(f"Wrote: {out_path}")


if __name__ == '__main__':
    main()
