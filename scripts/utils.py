#!/usr/bin/env python3
"""
utils.py

Utility functions for HREA replication analysis.
"""

import numpy as np
import pandas as pd
from pathlib import Path


# Country metadata
COUNTRIES = {
    'NGA': {'name': 'Nigeria', 'region': 'SSA'},
    'KEN': {'name': 'Kenya', 'region': 'SSA'},
    'ETH': {'name': 'Ethiopia', 'region': 'SSA'},
    'TZA': {'name': 'Tanzania', 'region': 'SSA'},
    'GHA': {'name': 'Ghana', 'region': 'SSA'},
    'UGA': {'name': 'Uganda', 'region': 'SSA'},
    'IND': {'name': 'India', 'region': 'South Asia'},
    'BGD': {'name': 'Bangladesh', 'region': 'South Asia'},
    'NPL': {'name': 'Nepal', 'region': 'South Asia'},
    'PAK': {'name': 'Pakistan', 'region': 'South Asia'},
    'MMR': {'name': 'Myanmar', 'region': 'South Asia'},
    'KHM': {'name': 'Cambodia', 'region': 'Southeast Asia'}
}

REGION_ORDER = ['SSA', 'South Asia', 'Southeast Asia']


def get_country_name(iso3: str) -> str:
    """Get country name from ISO3 code."""
    return COUNTRIES.get(iso3, {}).get('name', iso3)


def get_region(iso3: str) -> str:
    """Get region from ISO3 code."""
    return COUNTRIES.get(iso3, {}).get('region', 'Unknown')


def format_pvalue(p: float) -> str:
    """Format p-value for display."""
    if p < 0.001:
        return "< 0.001"
    elif p < 0.01:
        return f"{p:.3f}"
    else:
        return f"{p:.2f}"


def weighted_mean(values: np.ndarray, weights: np.ndarray) -> float:
    """Compute weighted mean."""
    return np.average(values, weights=weights)


def weighted_std(values: np.ndarray, weights: np.ndarray) -> float:
    """Compute weighted standard deviation."""
    average = weighted_mean(values, weights)
    variance = np.average((values - average) ** 2, weights=weights)
    return np.sqrt(variance)


def compute_percentile(data: np.ndarray, percentile: float) -> float:
    """Compute percentile of data array."""
    return float(np.percentile(data[~np.isnan(data)], percentile))


def fisher_z_test(r1: float, n1: int, r2: float, n2: int) -> tuple:
    """
    Fisher's z-test for comparing two correlation coefficients.
    
    Returns:
        z-statistic, p-value
    """
    # Fisher's z transformation
    z1 = 0.5 * np.log((1 + r1) / (1 - r1))
    z2 = 0.5 * np.log((1 + r2) / (1 - r2))
    
    # Standard error
    se = np.sqrt(1/(n1 - 3) + 1/(n2 - 3))
    
    # Z-statistic
    z = (z1 - z2) / se
    
    # Two-tailed p-value
    from scipy import stats
    p = 2 * (1 - stats.norm.cdf(abs(z)))
    
    return z, p
