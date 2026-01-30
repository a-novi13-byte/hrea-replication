#!/usr/bin/env python3
"""
05_figures.py

Generate all figures for the HREA replication paper.

Figures:
1. Lightscore Distributions by Region
2. HREA vs WDI Scatter (Replication)
3. Regional Validation (HREA Mean vs WDI)
4. Calibration Plot
5. Temporal Stability (3-panel)
6. HREA-WDI Gap by Electrification Level

Usage:
    python scripts/05_figures.py
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pathlib import Path

# Configuration
DATA_DIR = Path("data/processed")
TABLE_DIR = Path("outputs/tables")
FIG_DIR = Path("outputs/figures")

# Style settings
plt.style.use('seaborn-v0_8-whitegrid')
COLORS = {
    'SSA': '#E64B35',
    'South Asia': '#4DBBD5', 
    'Southeast Asia': '#00A087'
}

REGION_ORDER = ['SSA', 'South Asia', 'Southeast Asia']


def setup_style():
    """Set up matplotlib style for publication."""
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.size': 10,
        'axes.titlesize': 12,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 9,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight'
    })


def load_data():
    """Load all required data."""
    
    # Summary statistics
    summary = pd.read_csv(DATA_DIR / "hrea_summary_statistics.csv")
    
    # Electrification rates
    elec = pd.read_csv(DATA_DIR / "hrea_electrification_rates.csv")
    
    # Merged HREA-WDI
    merged = pd.read_csv(TABLE_DIR / "merged_hrea_wdi_2020.csv")
    
    # WDI full
    wdi = pd.read_csv(Path("data/external") / "wdi_electrification_2013_2020.csv")
    
    return summary, elec, merged, wdi


def figure1_distributions(summary: pd.DataFrame):
    """Figure 1: Lightscore distributions by region (box plots)."""
    
    df = summary[summary['year'] == 2020].copy()
    
    # Sort by region, then by median within region
    df['region_order'] = df['region'].map({r: i for i, r in enumerate(REGION_ORDER)})
    df = df.sort_values(['region_order', 'p50'])
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Create box plot data manually from percentiles
    positions = range(len(df))
    
    for i, (_, row) in enumerate(df.iterrows()):
        color = COLORS[row['region']]
        
        # Box from p25 to p75
        box = plt.Rectangle((i - 0.3, row['p25']), 0.6, row['p75'] - row['p25'],
                            fill=True, facecolor=color, edgecolor='black', alpha=0.7)
        ax.add_patch(box)
        
        # Median line
        ax.plot([i - 0.3, i + 0.3], [row['p50'], row['p50']], 'k-', linewidth=2)
        
        # Whiskers (p5 to p95)
        ax.plot([i, i], [row['p5'], row['p25']], 'k-', linewidth=1)
        ax.plot([i, i], [row['p75'], row['p95']], 'k-', linewidth=1)
        ax.plot([i - 0.15, i + 0.15], [row['p5'], row['p5']], 'k-', linewidth=1)
        ax.plot([i - 0.15, i + 0.15], [row['p95'], row['p95']], 'k-', linewidth=1)
    
    # Labels
    ax.set_xticks(positions)
    ax.set_xticklabels(df['iso3'], rotation=45, ha='right')
    ax.set_ylabel('HREA Lightscore')
    ax.set_ylim(0, 1.05)
    ax.set_xlim(-0.5, len(df) - 0.5)
    
    # Add region separators
    ssa_count = len(df[df['region'] == 'SSA'])
    sa_count = len(df[df['region'] == 'South Asia'])
    ax.axvline(ssa_count - 0.5, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(ssa_count + sa_count - 0.5, color='gray', linestyle='--', alpha=0.5)
    
    # Region labels
    ax.text(ssa_count/2 - 0.5, 1.02, 'Sub-Saharan Africa', ha='center', fontsize=10)
    ax.text(ssa_count + sa_count/2 - 0.5, 1.02, 'South Asia', ha='center', fontsize=10)
    ax.text(ssa_count + sa_count + 0.5, 1.02, 'SEA', ha='center', fontsize=10)
    
    # Legend
    handles = [plt.Rectangle((0, 0), 1, 1, facecolor=COLORS[r], edgecolor='black', alpha=0.7) 
               for r in REGION_ORDER]
    ax.legend(handles, REGION_ORDER, loc='lower right')
    
    ax.set_title('Figure 1: HREA Lightscore Distributions by Country (2020)')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'figure1_distributions.png')
    plt.savefig(FIG_DIR / 'figure1_distributions.pdf')
    plt.close()
    
    print("  ✓ Figure 1: Lightscore distributions")


def figure2_replication(elec: pd.DataFrame, wdi: pd.DataFrame):
    """Figure 2: HREA vs WDI scatter plot."""
    
    # Merge HREA electrification rates with WDI
    hrea_2020 = elec[elec['year'] == 2020][['iso3', 'region', 'electrification_rate']].copy()
    hrea_2020 = hrea_2020.rename(columns={'electrification_rate': 'hrea_pct'})
    
    wdi_2020 = wdi[wdi['year'] == 2020][['iso3', 'electrification_rate']].copy()
    wdi_2020 = wdi_2020.rename(columns={'electrification_rate': 'wdi_pct'})
    
    df = hrea_2020.merge(wdi_2020, on='iso3')
    
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 45-degree line
    ax.plot([0, 100], [0, 100], 'k--', alpha=0.5, label='Perfect agreement')
    
    # Scatter by region
    for region in REGION_ORDER:
        subset = df[df['region'] == region]
        ax.scatter(subset['wdi_pct'], subset['hrea_pct'], 
                  c=COLORS[region], s=80, label=region, alpha=0.8, edgecolor='white')
        
        # Add country labels
        for _, row in subset.iterrows():
            ax.annotate(row['iso3'], (row['wdi_pct'], row['hrea_pct']),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Regression line
    slope, intercept, r, p, se = stats.linregress(df['wdi_pct'], df['hrea_pct'])
    x_line = np.array([30, 100])
    ax.plot(x_line, intercept + slope * x_line, 'r-', alpha=0.7, label=f'OLS fit (r={r:.2f})')
    
    # RMSE
    rmse = np.sqrt(np.mean((df['hrea_pct'] - df['wdi_pct'])**2))
    
    ax.set_xlabel('WDI Official Electrification Rate (%)')
    ax.set_ylabel('HREA Replicated Electrification Rate (%)')
    ax.set_xlim(30, 105)
    ax.set_ylim(10, 105)
    ax.legend(loc='lower right')
    ax.set_title(f'Figure 2: HREA vs WDI Electrification (2020)\nRMSE = {rmse:.1f} pp')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'figure2_replication.png')
    plt.savefig(FIG_DIR / 'figure2_replication.pdf')
    plt.close()
    
    print(f"  ✓ Figure 2: Replication scatter (RMSE = {rmse:.1f} pp)")


def figure3_regional(merged: pd.DataFrame):
    """Figure 3: HREA mean lightscore vs WDI by region."""
    
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Scatter by region
    for region in REGION_ORDER:
        subset = merged[merged['region'] == region]
        ax.scatter(subset['hrea_mean'], subset['wdi_rate'], 
                  c=COLORS[region], s=100, label=region, alpha=0.8, edgecolor='white')
        
        # Add country labels
        for _, row in subset.iterrows():
            ax.annotate(row['iso3'], (row['hrea_mean'], row['wdi_rate']),
                       xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        # Regional regression line (if n >= 3)
        if len(subset) >= 3:
            slope, intercept, r, p, se = stats.linregress(subset['hrea_mean'], subset['wdi_rate'])
            x_line = np.linspace(subset['hrea_mean'].min() - 0.05, subset['hrea_mean'].max() + 0.05, 50)
            linestyle = '-' if p < 0.05 else '--'
            ax.plot(x_line, intercept + slope * x_line, c=COLORS[region], 
                   linestyle=linestyle, alpha=0.7)
    
    # Add correlation annotations
    ax.text(0.02, 0.98, 'Regional correlations:', transform=ax.transAxes, 
           fontsize=9, verticalalignment='top', fontweight='bold')
    
    ssa = merged[merged['region'] == 'SSA']
    sa = merged[merged['region'] == 'South Asia']
    
    r_ssa, p_ssa = stats.pearsonr(ssa['hrea_mean'], ssa['wdi_rate'])
    r_sa, p_sa = stats.pearsonr(sa['hrea_mean'], sa['wdi_rate'])
    
    ax.text(0.02, 0.91, f'SSA: r = {r_ssa:.2f} (p = {p_ssa:.3f})', 
           transform=ax.transAxes, fontsize=9, color=COLORS['SSA'])
    ax.text(0.02, 0.84, f'South Asia: r = {r_sa:.2f} (p = {p_sa:.2f})', 
           transform=ax.transAxes, fontsize=9, color=COLORS['South Asia'])
    
    ax.set_xlabel('HREA Mean Lightscore')
    ax.set_ylabel('WDI Electrification Rate (%)')
    ax.set_xlim(0.15, 0.95)
    ax.set_ylim(35, 100)
    ax.legend(loc='lower right')
    ax.set_title('Figure 3: Regional Validation — HREA Lightscore vs Official Statistics')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'figure3_regional.png')
    plt.savefig(FIG_DIR / 'figure3_regional.pdf')
    plt.close()
    
    print(f"  ✓ Figure 3: Regional validation (SSA r={r_ssa:.2f}, SA r={r_sa:.2f})")


def figure4_calibration(merged: pd.DataFrame):
    """Figure 4: Calibration plot."""
    
    fig, ax = plt.subplots(figsize=(5, 5))
    
    # Convert WDI to 0-1 scale
    df = merged.copy()
    df['wdi_frac'] = df['wdi_rate'] / 100
    
    # 45-degree line (perfect calibration)
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.5, label='Perfect calibration')
    
    # Scatter
    for region in REGION_ORDER:
        subset = df[df['region'] == region]
        ax.scatter(subset['hrea_mean'], subset['wdi_frac'],
                  c=COLORS[region], s=80, label=region, alpha=0.8, edgecolor='white')
    
    # OLS fit
    slope, intercept, r, p, se = stats.linregress(df['hrea_mean'], df['wdi_frac'])
    x_line = np.linspace(0.2, 0.95, 50)
    ax.plot(x_line, intercept + slope * x_line, 'r-', alpha=0.7, label='OLS fit')
    
    # Test slope ≠ 1
    t_stat = (slope - 1) / se
    p_ne_1 = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(df) - 2))
    
    # Annotation
    ax.text(0.05, 0.95, f'Slope = {slope:.2f} (SE = {se:.2f})\nIntercept = {intercept:.2f}\np(slope ≠ 1) = {p_ne_1:.3f}',
           transform=ax.transAxes, fontsize=9, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    ax.set_xlabel('HREA Mean Lightscore')
    ax.set_ylabel('WDI Electrification Rate (fraction)')
    ax.set_xlim(0.15, 0.95)
    ax.set_ylim(0.35, 1.0)
    ax.legend(loc='lower right')
    ax.set_title('Figure 4: Calibration Analysis')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'figure4_calibration.png')
    plt.savefig(FIG_DIR / 'figure4_calibration.pdf')
    plt.close()
    
    print(f"  ✓ Figure 4: Calibration (slope = {slope:.2f})")


def figure5_temporal(summary: pd.DataFrame, wdi: pd.DataFrame):
    """Figure 5: Temporal stability (3-panel)."""
    
    fig, axes = plt.subplots(1, 3, figsize=(12, 4), sharey=True)
    
    years = [2013, 2016, 2020]
    
    for ax, year in zip(axes, years):
        # Merge for this year
        hrea_year = summary[summary['year'] == year][['iso3', 'region', 'mean']].copy()
        wdi_year = wdi[wdi['year'] == year][['iso3', 'electrification_rate']].copy()
        df = hrea_year.merge(wdi_year, on='iso3')
        
        # Scatter
        for region in REGION_ORDER:
            subset = df[df['region'] == region]
            ax.scatter(subset['mean'], subset['electrification_rate'],
                      c=COLORS[region], s=60, alpha=0.8, edgecolor='white')
        
        # Correlation
        r, p = stats.pearsonr(df['mean'], df['electrification_rate'])
        
        # Regression line
        slope, intercept, _, _, _ = stats.linregress(df['mean'], df['electrification_rate'])
        x_line = np.linspace(0.2, 0.95, 50)
        ax.plot(x_line, intercept + slope * x_line, 'k-', alpha=0.5)
        
        ax.set_xlabel('HREA Mean Lightscore')
        ax.set_xlim(0.15, 0.95)
        ax.set_ylim(35, 100)
        ax.set_title(f'{year}\nr = {r:.2f}')
    
    axes[0].set_ylabel('WDI Electrification Rate (%)')
    
    # Legend
    handles = [plt.scatter([], [], c=COLORS[r], s=60, label=r) for r in REGION_ORDER]
    fig.legend(handles, REGION_ORDER, loc='center right', bbox_to_anchor=(1.02, 0.5))
    
    fig.suptitle('Figure 5: Temporal Stability of HREA-WDI Relationship', y=1.02)
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'figure5_temporal.png', bbox_inches='tight')
    plt.savefig(FIG_DIR / 'figure5_temporal.pdf', bbox_inches='tight')
    plt.close()
    
    print("  ✓ Figure 5: Temporal stability (3-panel)")


def figure6_gap(elec: pd.DataFrame, wdi: pd.DataFrame):
    """Figure 6: HREA-WDI gap by electrification level."""
    
    # Merge
    hrea_2020 = elec[elec['year'] == 2020][['iso3', 'region', 'electrification_rate']].copy()
    hrea_2020 = hrea_2020.rename(columns={'electrification_rate': 'hrea_pct'})
    
    wdi_2020 = wdi[wdi['year'] == 2020][['iso3', 'electrification_rate']].copy()
    wdi_2020 = wdi_2020.rename(columns={'electrification_rate': 'wdi_pct'})
    
    df = hrea_2020.merge(wdi_2020, on='iso3')
    df['gap'] = df['wdi_pct'] - df['hrea_pct']  # Positive = HREA underestimates
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Horizontal line at 0
    ax.axhline(0, color='black', linestyle='-', alpha=0.3)
    
    # Scatter
    for region in REGION_ORDER:
        subset = df[df['region'] == region]
        ax.scatter(subset['wdi_pct'], subset['gap'],
                  c=COLORS[region], s=80, label=region, alpha=0.8, edgecolor='white')
        
        for _, row in subset.iterrows():
            ax.annotate(row['iso3'], (row['wdi_pct'], row['gap']),
                       xytext=(5, 5), textcoords='offset points', fontsize=8)
    
    # Correlation
    r, p = stats.pearsonr(df['wdi_pct'], df['gap'])
    
    # Regression line
    slope, intercept, _, _, _ = stats.linregress(df['wdi_pct'], df['gap'])
    x_line = np.linspace(35, 100, 50)
    ax.plot(x_line, intercept + slope * x_line, 'k--', alpha=0.5)
    
    ax.text(0.05, 0.95, f'r = {r:.2f} (p = {p:.3f})',
           transform=ax.transAxes, fontsize=10, verticalalignment='top')
    
    ax.set_xlabel('WDI Electrification Rate (%)')
    ax.set_ylabel('HREA Underestimation (WDI − HREA, pp)')
    ax.set_xlim(35, 100)
    ax.legend(loc='upper left')
    ax.set_title('Figure 6: HREA-WDI Gap by Electrification Level')
    
    plt.tight_layout()
    plt.savefig(FIG_DIR / 'figure6_gap.png')
    plt.savefig(FIG_DIR / 'figure6_gap.pdf')
    plt.close()
    
    print(f"  ✓ Figure 6: Gap analysis (r = {r:.2f})")


def main():
    print("=" * 60)
    print("Generating Figures")
    print("=" * 60)
    
    # Setup
    setup_style()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load data
    print("\nLoading data...")
    summary, elec, merged, wdi = load_data()
    
    # Generate figures
    print("\nGenerating figures...")
    figure1_distributions(summary)
    figure2_replication(elec, wdi)
    figure3_regional(merged)
    figure4_calibration(merged)
    figure5_temporal(summary, wdi)
    figure6_gap(elec, wdi)
    
    print("\n" + "=" * 60)
    print(f"All figures saved to: {FIG_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
