#!/usr/bin/env python3

"""
Usage:
    python scripts/python/00_fetch.py \
        --mortality "data-table.csv" \
        --laws "TL-A243-2-v3 State Firearm Law Database 5.0.xlsx"
"""

import argparse
import shutil
from pathlib import Path
import sys


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Fetch and organize raw data files'
    )
    parser.add_argument(
        '--mortality',
        type=str,
        default='data-table.csv',
        help='Path to the mortality CSV (CDC) [default: data-table.csv]'
    )
    parser.add_argument(
        '--laws',
        type=str,
        default='TL-A243-2-v3 State Firearm Law Database 5.0.xlsx',
        help='Path to the firearm law Excel workbook [default: TL-A243-2-v3 State Firearm Law Database 5.0.xlsx]'
    )
    
    args = parser.parse_args()
    
    # Ensure folder structure
    Path('Data/raw').mkdir(parents=True, exist_ok=True)
    Path('Data/interim').mkdir(parents=True, exist_ok=True)
    Path('Data/processed').mkdir(parents=True, exist_ok=True)
    
    # Define standardized raw data paths
    raw_mortality = Path('Data/raw/data-table.csv')
    raw_laws_xlsx = Path('Data/raw/TL-A243-2-v3 State Firearm Law Database 5.0.xlsx')
    
    # Copy/standardize mortality file
    mortality_source = Path(args.mortality)
    if mortality_source.exists():
        shutil.copy2(mortality_source, raw_mortality)
    elif not raw_mortality.exists():
        print(f"Error: Could not find mortality CSV at '{args.mortality}' "
              f"and there is no existing '{raw_mortality}'.", file=sys.stderr)
        sys.exit(1)
    
    # Copy/standardize laws file
    laws_source = Path(args.laws)
    if laws_source.exists():
        shutil.copy2(laws_source, raw_laws_xlsx)
    elif not raw_laws_xlsx.exists():
        print(f"Error: Could not find law database at '{args.laws}' "
              f"and there is no existing '{raw_laws_xlsx}'.", file=sys.stderr)
        sys.exit(1)
    
    print("Fetch step complete:")
    print(f" - {raw_mortality}")
    print(f" - {raw_laws_xlsx}")


if __name__ == '__main__':
    main()
