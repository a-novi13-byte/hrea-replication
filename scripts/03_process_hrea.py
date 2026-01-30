#!/usr/bin/env python3
"""
03_process_hrea.py

Process downloaded HREA GeoTIFF tiles into summary statistics.
Computes country-level metrics from settlement-level lightscore data.

Usage:
    python scripts/03_process_hrea.py
"""

import numpy as np
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import warnings

# Try to import rasterio, provide helpful error if missing
try:
    import rasterio
except ImportError:
    print("Error: rasterio not installed. Install with: pip install rasterio")
    exit(1)

# Configuration
COUNTRIES = {
    'NGA': ('Nigeria', 'SSA'),
    'KEN': ('Kenya', 'SSA'),
    'ETH': ('Ethiopia', 'SSA'),
    'TZA': ('Tanzania', 'SSA'),
    'GHA': ('Ghana', 'SSA'),
    'UGA': ('Uganda', 'SSA'),
    'IND': ('India', 'South Asia'),
    'BGD': ('Bangladesh', 'South Asia'),
    'NPL': ('Nepal', 'South Asia'),
    'PAK': ('Pakistan', 'South Asia'),
    'MMR': ('Myanmar', 'South Asia'),
    'KHM': ('Cambodia', 'Southeast Asia')
}

YEARS = [2013, 2016, 2020]  # Key years for analysis
INPUT_DIR = Path("data/raw/hrea")
OUTPUT_DIR = Path("data/processed")

# HREA variable names in GeoTIFFs
VARIABLES = {
    'set_lightscore': 'Probability of electrification (0-1)',
    'set_zscore': 'Brightness z-score relative to background',
    'set_prplit': 'Proportion of nights statistically lit',
    'rade9lnmu': 'Mean nightlight radiance'
}


def find_tiles(country_dir: Path, year: int, variable: str = 'set_lightscore') -> list:
    """Find all HREA tiles for a country/year/variable combination."""
    
    # HREA naming convention: {ISO3}_{variable}_{year}_*.tif
    pattern = f"*{variable}*{year}*.tif"
    
    tiles = list(country_dir.rglob(pattern))
    
    # Also check for COG format
    if not tiles:
        pattern = f"*{variable}*{year}*.tiff"
        tiles = list(country_dir.rglob(pattern))
    
    return tiles


def process_tile(tile_path: Path) -> dict:
    """Extract statistics from a single HREA tile."""
    
    with rasterio.open(tile_path) as src:
        data = src.read(1)  # Read first band
        
        # HREA uses nodata value, typically -9999 or nan
        nodata = src.nodata
        if nodata is not None:
            mask = data != nodata
        else:
            mask = ~np.isnan(data)
        
        valid_data = data[mask]
        
        if len(valid_data) == 0:
            return None
        
        # Compute statistics
        stats = {
            'n_pixels': len(valid_data),
            'mean': float(np.mean(valid_data)),
            'std': float(np.std(valid_data)),
            'min': float(np.min(valid_data)),
            'max': float(np.max(valid_data)),
            'p5': float(np.percentile(valid_data, 5)),
            'p10': float(np.percentile(valid_data, 10)),
            'p25': float(np.percentile(valid_data, 25)),
            'p50': float(np.percentile(valid_data, 50)),
            'p75': float(np.percentile(valid_data, 75)),
            'p90': float(np.percentile(valid_data, 90)),
            'p95': float(np.percentile(valid_data, 95)),
            'pct_gt_0.5': float(np.mean(valid_data > 0.5) * 100),
            'pct_gt_0.8': float(np.mean(valid_data > 0.8) * 100),
        }
        
        return stats


def process_country_year(iso3: str, year: int, country_dir: Path) -> dict:
    """Process all tiles for a country-year combination."""
    
    tiles = find_tiles(country_dir, year)
    
    if not tiles:
        return None
    
    # Aggregate across tiles
    all_stats = []
    total_pixels = 0
    
    for tile in tiles:
        stats = process_tile(tile)
        if stats:
            all_stats.append(stats)
            total_pixels += stats['n_pixels']
    
    if not all_stats:
        return None
    
    # Weighted average across tiles
    weights = [s['n_pixels'] / total_pixels for s in all_stats]
    
    result = {
        'iso3': iso3,
        'year': year,
        'n_tiles': len(tiles),
        'n_pixels': total_pixels,
    }
    
    # Weighted statistics
    for key in ['mean', 'std', 'p5', 'p10', 'p25', 'p50', 'p75', 'p90', 'p95', 
                'pct_gt_0.5', 'pct_gt_0.8']:
        result[key] = sum(s[key] * w for s, w in zip(all_stats, weights))
    
    return result


def compute_electrification_rate(iso3: str, year: int, country_dir: Path,
                                  zscore_threshold: float = 1.28) -> dict:
    """
    Compute population-weighted electrification rate using z-score threshold.
    
    A settlement is considered "electrified" if zscore > threshold (default 1.28,
    corresponding to 90th percentile of background distribution).
    """
    
    # Find z-score tiles
    zscore_tiles = find_tiles(country_dir, year, 'set_zscore')
    
    if not zscore_tiles:
        return None
    
    total_settlements = 0
    electrified_settlements = 0
    
    for tile in zscore_tiles:
        with rasterio.open(tile) as src:
            data = src.read(1)
            nodata = src.nodata
            
            if nodata is not None:
                mask = data != nodata
            else:
                mask = ~np.isnan(data)
            
            valid_data = data[mask]
            
            total_settlements += len(valid_data)
            electrified_settlements += np.sum(valid_data > zscore_threshold)
    
    if total_settlements == 0:
        return None
    
    return {
        'iso3': iso3,
        'year': year,
        'total_settlements': total_settlements,
        'electrified_settlements': int(electrified_settlements),
        'electrification_rate': float(electrified_settlements / total_settlements * 100)
    }


def main():
    print("=" * 60)
    print("HREA Data Processing")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Process summary statistics
    print("\n1. Computing lightscore summary statistics...")
    summary_records = []
    
    for iso3, (country_name, region) in tqdm(COUNTRIES.items()):
        country_dir = INPUT_DIR / iso3
        
        if not country_dir.exists():
            print(f"  Warning: No data for {iso3}")
            continue
        
        for year in YEARS:
            result = process_country_year(iso3, year, country_dir)
            if result:
                result['country'] = country_name
                result['region'] = region
                summary_records.append(result)
    
    summary_df = pd.DataFrame(summary_records)
    summary_file = OUTPUT_DIR / "hrea_summary_statistics.csv"
    summary_df.to_csv(summary_file, index=False)
    print(f"  ✓ Saved: {summary_file}")
    
    # Process electrification rates
    print("\n2. Computing electrification rates (z-score > 1.28)...")
    elec_records = []
    
    for iso3, (country_name, region) in tqdm(COUNTRIES.items()):
        country_dir = INPUT_DIR / iso3
        
        if not country_dir.exists():
            continue
        
        for year in YEARS:
            result = compute_electrification_rate(iso3, year, country_dir)
            if result:
                result['country'] = country_name
                result['region'] = region
                elec_records.append(result)
    
    elec_df = pd.DataFrame(elec_records)
    elec_file = OUTPUT_DIR / "hrea_electrification_rates.csv"
    elec_df.to_csv(elec_file, index=False)
    print(f"  ✓ Saved: {elec_file}")
    
    # Create 2020 summary for paper
    print("\n3. Creating 2020 summary table...")
    df_2020 = summary_df[summary_df['year'] == 2020].copy()
    df_2020 = df_2020.sort_values(['region', 'iso3'])
    
    table3_file = OUTPUT_DIR / "table3_hrea_summary_2020.csv"
    df_2020.to_csv(table3_file, index=False)
    print(f"  ✓ Saved: {table3_file}")
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)
    
    # Preview
    print("\nPreview (2020 lightscore statistics):")
    cols = ['iso3', 'region', 'n_pixels', 'mean', 'p50', 'std']
    print(df_2020[cols].to_string(index=False))


if __name__ == "__main__":
    main()
