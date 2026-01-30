#!/usr/bin/env python3
"""
02_download_wdi.py

Download World Development Indicator electrification rates from World Bank API.
Indicator: EG.ELC.ACCS.ZS (Access to electricity, % of population)

Usage:
    python scripts/02_download_wdi.py
"""

import pandas as pd
from pathlib import Path

# Try wbgapi first, fall back to manual download
try:
    import wbgapi as wb
    USE_API = True
except ImportError:
    USE_API = False
    import requests

# Configuration
COUNTRIES = ['NGA', 'KEN', 'ETH', 'TZA', 'GHA', 'UGA',  # SSA
             'IND', 'BGD', 'NPL', 'PAK', 'MMR',          # South Asia
             'KHM']                                       # Southeast Asia

YEARS = range(2013, 2021)  # 2013-2020
INDICATOR = 'EG.ELC.ACCS.ZS'
OUTPUT_DIR = Path("data/external")


def download_via_api() -> pd.DataFrame:
    """Download WDI data using wbgapi package."""
    print("Downloading via World Bank API...")
    
    # Fetch data
    data = wb.data.DataFrame(
        INDICATOR,
        COUNTRIES,
        time=range(2013, 2021),
        labels=True
    )
    
    # Reshape to long format
    data = data.reset_index()
    data = data.melt(
        id_vars=['economy'],
        var_name='year',
        value_name='electrification_rate'
    )
    
    # Clean up
    data['year'] = data['year'].str.extract(r'(\d{4})').astype(int)
    data = data.rename(columns={'economy': 'country'})
    
    return data


def download_via_url() -> pd.DataFrame:
    """Download WDI data via direct URL (fallback)."""
    print("Downloading via direct URL...")
    
    records = []
    
    for iso3 in COUNTRIES:
        url = f"https://api.worldbank.org/v2/country/{iso3}/indicator/{INDICATOR}"
        params = {
            'format': 'json',
            'date': '2013:2020',
            'per_page': 100
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if len(data) > 1 and data[1]:
            for record in data[1]:
                records.append({
                    'iso3': iso3,
                    'country': record['country']['value'],
                    'year': int(record['date']),
                    'electrification_rate': record['value']
                })
    
    return pd.DataFrame(records)


def add_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Add region classification."""
    
    region_map = {
        'NGA': 'SSA', 'KEN': 'SSA', 'ETH': 'SSA',
        'TZA': 'SSA', 'GHA': 'SSA', 'UGA': 'SSA',
        'IND': 'South Asia', 'BGD': 'South Asia', 'NPL': 'South Asia',
        'PAK': 'South Asia', 'MMR': 'South Asia',
        'KHM': 'Southeast Asia'
    }
    
    country_names = {
        'NGA': 'Nigeria', 'KEN': 'Kenya', 'ETH': 'Ethiopia',
        'TZA': 'Tanzania', 'GHA': 'Ghana', 'UGA': 'Uganda',
        'IND': 'India', 'BGD': 'Bangladesh', 'NPL': 'Nepal',
        'PAK': 'Pakistan', 'MMR': 'Myanmar', 'KHM': 'Cambodia'
    }
    
    if 'iso3' not in df.columns:
        # Map country names to ISO3
        name_to_iso = {v: k for k, v in country_names.items()}
        df['iso3'] = df['country'].map(name_to_iso)
    
    df['region'] = df['iso3'].map(region_map)
    df['country_name'] = df['iso3'].map(country_names)
    
    return df


def main():
    print("=" * 60)
    print("WDI Electrification Data Download")
    print("=" * 60)
    print(f"\nIndicator: {INDICATOR}")
    print(f"Countries: {len(COUNTRIES)}")
    print(f"Years: 2013-2020")
    print("-" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download data
    if USE_API:
        df = download_via_api()
    else:
        df = download_via_url()
    
    # Add metadata
    df = add_metadata(df)
    
    # Sort and clean
    df = df.sort_values(['region', 'iso3', 'year'])
    
    # Save
    output_file = OUTPUT_DIR / "wdi_electrification_2013_2020.csv"
    df.to_csv(output_file, index=False)
    
    print(f"\n✓ Saved to: {output_file}")
    print(f"  Rows: {len(df)}")
    print(f"  Countries: {df['iso3'].nunique()}")
    
    # Preview
    print("\nPreview (2020 data):")
    print(df[df['year'] == 2020][['iso3', 'region', 'electrification_rate']].to_string(index=False))
    
    print("\n" + "=" * 60)
    print("Download complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
