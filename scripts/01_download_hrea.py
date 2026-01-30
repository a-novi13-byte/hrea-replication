#!/usr/bin/env python3
"""
01_download_hrea.py

Download HREA (High Resolution Electricity Access) tiles from AWS S3.
Data source: s3://globalnightlight/HREA/

This script downloads settlement-level electrification estimates for 12 countries
across Sub-Saharan Africa and South/Southeast Asia.

Usage:
    python scripts/01_download_hrea.py

Note: Requires ~34 GB of disk space for all countries.
"""

import os
import subprocess
from pathlib import Path
from tqdm import tqdm

# Configuration
COUNTRIES = {
    # Sub-Saharan Africa
    'NGA': 'Nigeria',
    'KEN': 'Kenya', 
    'ETH': 'Ethiopia',
    'TZA': 'Tanzania',
    'GHA': 'Ghana',
    'UGA': 'Uganda',
    # South Asia
    'IND': 'India',
    'BGD': 'Bangladesh',
    'NPL': 'Nepal',
    'PAK': 'Pakistan',
    'MMR': 'Myanmar',
    # Southeast Asia
    'KHM': 'Cambodia'
}

YEARS = [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]

S3_BASE = "s3://globalnightlight/HREA"
OUTPUT_DIR = Path("data/raw/hrea")


def download_country(iso3: str, country_name: str) -> None:
    """Download all HREA tiles for a single country."""
    
    country_dir = OUTPUT_DIR / iso3
    country_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nDownloading {country_name} ({iso3})...")
    
    # HREA uses different folder structures for different countries
    # India has state-level subfolders, others are flat
    s3_path = f"{S3_BASE}/{iso3}/"
    
    # Use AWS CLI for efficient sync
    cmd = [
        "aws", "s3", "sync",
        s3_path,
        str(country_dir),
        "--no-sign-request",  # Public bucket, no credentials needed
        "--quiet"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"  ✓ {country_name} complete")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ {country_name} failed: {e}")
    except FileNotFoundError:
        print("  ✗ AWS CLI not found. Install with: pip install awscli")
        print("    Or download manually from: https://globalnightlight.s3.amazonaws.com/index.html")


def check_aws_cli() -> bool:
    """Check if AWS CLI is installed."""
    try:
        subprocess.run(["aws", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def main():
    print("=" * 60)
    print("HREA Data Download Script")
    print("=" * 60)
    print(f"\nTarget directory: {OUTPUT_DIR.absolute()}")
    print(f"Countries: {len(COUNTRIES)}")
    print(f"Years: {YEARS[0]}-{YEARS[-1]}")
    print("\nEstimated download size: ~34 GB")
    print("-" * 60)
    
    # Check AWS CLI
    if not check_aws_cli():
        print("\n⚠ AWS CLI not found!")
        print("Install with: pip install awscli")
        print("\nAlternatively, download manually from:")
        print("https://globalnightlight.s3.amazonaws.com/index.html#HREA/")
        return
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Download each country
    for iso3, country_name in COUNTRIES.items():
        download_country(iso3, country_name)
    
    print("\n" + "=" * 60)
    print("Download complete!")
    print(f"Data saved to: {OUTPUT_DIR.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
