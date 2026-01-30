#!/usr/bin/env python3
"""
04_analysis.py

Main analysis script for HREA replication study.
Computes correlations, generates tables for the paper.

Usage:
    python scripts/04_analysis.py
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
from tabulate import tabulate

# Configuration
DATA_DIR = Path("data/processed")
EXTERNAL_DIR = Path("data/external")
OUTPUT_DIR = Path("outputs/tables")


def load_data() -> tuple:
    """Load processed HREA and WDI data."""
    
    # HREA summary statistics
    hrea_summary = pd.read_csv(DATA_DIR / "hrea_summary_statistics.csv")
    
    # HREA electrification rates
    hrea_elec = pd.read_csv(DATA_DIR / "hrea_electrification_rates.csv")
    
    # WDI electrification
    wdi = pd.read_csv(EXTERNAL_DIR / "wdi_electrification_2013_2020.csv")
    
    return hrea_summary, hrea_elec, wdi


def compute_correlations(hrea: pd.DataFrame, wdi: pd.DataFrame, year: int = 2020) -> dict:
    """Compute Pearson correlations between HREA and WDI."""
    
    # Merge datasets
    hrea_year = hrea[hrea['year'] == year][['iso3', 'region', 'mean']].copy()
    hrea_year = hrea_year.rename(columns={'mean': 'hrea_mean'})
    
    wdi_year = wdi[wdi['year'] == year][['iso3', 'electrification_rate']].copy()
    wdi_year = wdi_year.rename(columns={'electrification_rate': 'wdi_rate'})
    
    merged = hrea_year.merge(wdi_year, on='iso3')
    
    results = {}
    
    # Overall correlation
    r, p = stats.pearsonr(merged['hrea_mean'], merged['wdi_rate'])
    results['overall'] = {'n': len(merged), 'r': r, 'p': p}
    
    # By region
    for region in merged['region'].unique():
        subset = merged[merged['region'] == region]
        if len(subset) >= 3:
            r, p = stats.pearsonr(subset['hrea_mean'], subset['wdi_rate'])
            results[region] = {'n': len(subset), 'r': r, 'p': p}
        else:
            results[region] = {'n': len(subset), 'r': np.nan, 'p': np.nan}
    
    return results, merged


def create_table4(hrea_elec: pd.DataFrame, wdi: pd.DataFrame, year: int = 2020) -> pd.DataFrame:
    """
    Table 4: Replication Results
    HREA-derived electrification rate vs WDI official rate.
    """
    
    # Get HREA electrification rates
    hrea_year = hrea_elec[hrea_elec['year'] == year][['iso3', 'country', 'region', 'electrification_rate']].copy()
    hrea_year = hrea_year.rename(columns={'electrification_rate': 'hrea_pct'})
    
    # Get WDI rates
    wdi_year = wdi[wdi['year'] == year][['iso3', 'electrification_rate']].copy()
    wdi_year = wdi_year.rename(columns={'electrification_rate': 'wdi_pct'})
    
    # Merge
    table4 = hrea_year.merge(wdi_year, on='iso3')
    
    # Compute difference
    table4['difference'] = table4['hrea_pct'] - table4['wdi_pct']
    
    # Sort by region, then country
    table4 = table4.sort_values(['region', 'iso3'])
    
    return table4


def create_table5(correlations: dict) -> pd.DataFrame:
    """
    Table 5: Regional Correlations
    HREA-WDI correlation by region.
    """
    
    records = []
    
    # Overall first
    overall = correlations['overall']
    records.append({
        'Scope': 'Overall',
        'Region': 'All',
        'N': overall['n'],
        'Pearson r': f"{overall['r']:.3f}",
        'p-value': f"{overall['p']:.4f}" if overall['p'] >= 0.0001 else "< 0.001"
    })
    
    # By region
    for region in ['SSA', 'South Asia', 'Southeast Asia']:
        if region in correlations:
            data = correlations[region]
            if np.isnan(data['r']):
                records.append({
                    'Scope': 'Region',
                    'Region': region,
                    'N': data['n'],
                    'Pearson r': '—',
                    'p-value': '—'
                })
            else:
                records.append({
                    'Scope': 'Region',
                    'Region': region,
                    'N': data['n'],
                    'Pearson r': f"{data['r']:.3f}",
                    'p-value': f"{data['p']:.3f}"
                })
    
    return pd.DataFrame(records)


def create_table6(hrea: pd.DataFrame, wdi: pd.DataFrame) -> pd.DataFrame:
    """
    Table 6: Temporal Stability
    Correlations for 2013, 2016, 2020.
    """
    
    records = []
    
    for year in [2013, 2016, 2020]:
        corr, _ = compute_correlations(hrea, wdi, year)
        overall = corr['overall']
        records.append({
            'Year': year,
            'N': overall['n'],
            'Pearson r': f"{overall['r']:.3f}",
            'p-value': f"{overall['p']:.4f}" if overall['p'] >= 0.0001 else "< 0.001"
        })
    
    return pd.DataFrame(records)


def compute_calibration(merged: pd.DataFrame) -> dict:
    """
    Compute calibration regression: WDI = a + b * HREA
    Test whether slope = 1 and intercept = 0.
    """
    
    x = merged['hrea_mean'].values
    y = merged['wdi_rate'].values / 100  # Convert to 0-1 scale
    
    slope, intercept, r, p, se = stats.linregress(x, y)
    
    # Test if slope differs from 1
    t_stat = (slope - 1) / se
    p_slope_ne_1 = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(x) - 2))
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r ** 2,
        'slope_se': se,
        'p_slope_ne_1': p_slope_ne_1
    }


def main():
    print("=" * 60)
    print("HREA Replication Analysis")
    print("=" * 60)
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\nLoading data...")
    hrea_summary, hrea_elec, wdi = load_data()
    print(f"  HREA summary: {len(hrea_summary)} rows")
    print(f"  HREA elec rates: {len(hrea_elec)} rows")
    print(f"  WDI: {len(wdi)} rows")
    
    # Compute correlations
    print("\n1. Computing correlations...")
    correlations, merged = compute_correlations(hrea_summary, wdi, 2020)
    
    print("\n  Results:")
    print(f"    Overall: r = {correlations['overall']['r']:.3f}, p = {correlations['overall']['p']:.4f}")
    for region in ['SSA', 'South Asia', 'Southeast Asia']:
        if region in correlations and not np.isnan(correlations[region]['r']):
            print(f"    {region}: r = {correlations[region]['r']:.3f}, p = {correlations[region]['p']:.3f}")
    
    # Create Table 4
    print("\n2. Creating Table 4 (Replication Results)...")
    table4 = create_table4(hrea_elec, wdi, 2020)
    table4.to_csv(OUTPUT_DIR / "table4_replication_results.csv", index=False)
    print(f"  ✓ Saved: table4_replication_results.csv")
    
    # Summary statistics
    mean_gap = table4['difference'].mean()
    mean_abs_gap = table4['difference'].abs().mean()
    print(f"  Mean difference (HREA - WDI): {mean_gap:.1f} pp")
    print(f"  Mean absolute difference: {mean_abs_gap:.1f} pp")
    
    # Create Table 5
    print("\n3. Creating Table 5 (Regional Correlations)...")
    table5 = create_table5(correlations)
    table5.to_csv(OUTPUT_DIR / "table5_regional_correlations.csv", index=False)
    print(f"  ✓ Saved: table5_regional_correlations.csv")
    print("\n" + tabulate(table5, headers='keys', tablefmt='simple', showindex=False))
    
    # Create Table 6
    print("\n4. Creating Table 6 (Temporal Stability)...")
    table6 = create_table6(hrea_summary, wdi)
    table6.to_csv(OUTPUT_DIR / "table6_temporal_stability.csv", index=False)
    print(f"  ✓ Saved: table6_temporal_stability.csv")
    print("\n" + tabulate(table6, headers='keys', tablefmt='simple', showindex=False))
    
    # Calibration analysis
    print("\n5. Calibration analysis...")
    calibration = compute_calibration(merged)
    print(f"  Slope: {calibration['slope']:.3f} (SE: {calibration['slope_se']:.3f})")
    print(f"  Intercept: {calibration['intercept']:.3f}")
    print(f"  R²: {calibration['r_squared']:.3f}")
    print(f"  Test slope ≠ 1: p = {calibration['p_slope_ne_1']:.3f}")
    
    # Save calibration results
    calib_df = pd.DataFrame([calibration])
    calib_df.to_csv(OUTPUT_DIR / "calibration_results.csv", index=False)
    
    # Create merged dataset for figures
    print("\n6. Saving merged dataset for figures...")
    merged.to_csv(OUTPUT_DIR / "merged_hrea_wdi_2020.csv", index=False)
    print(f"  ✓ Saved: merged_hrea_wdi_2020.csv")
    
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print(f"All tables saved to: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
