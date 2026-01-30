# Replication Package: Satellite-Based Electrification Predictions

## Paper

**Title:** Reproducibility and Geographic Transfer of Satellite-Based Electrification Predictions: Testing High-Resolution Electricity Access Models Across Africa and Asia

**Author:** Alexei (Frank) Hoffman, Georgetown University

**Conference:** MeasureDev 2026, World Bank

---

## Overview

This repository contains all code and instructions needed to replicate the analysis in the paper. The study tests whether High Resolution Electricity Access (HREA) satellite-derived electrification estimates perform consistently across Sub-Saharan Africa and South/Southeast Asia.

### Key Findings
- HREA correlates strongly with official statistics in SSA (r = 0.92) but weakly in South Asia (r = 0.66, n.s.)
- Systematic underestimation: mean 18 percentage-point gap vs. WDI
- Regional patterns are temporally stable (2013-2020)

---

## Repository Structure

```
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── data/
│   ├── raw/                  # Downloaded HREA tiles (not included, see instructions)
│   ├── processed/            # Processed CSVs (included)
│   └── external/             # WDI data, GADM boundaries
├── scripts/
│   ├── 01_download_hrea.py   # Download HREA data from AWS
│   ├── 02_download_wdi.py    # Download WDI electrification rates
│   ├── 03_process_hrea.py    # Compute summary statistics from HREA tiles
│   ├── 04_analysis.py        # Main analysis (correlations, tables)
│   ├── 05_figures.py         # Generate all figures
│   └── utils.py              # Helper functions
├── outputs/
│   ├── tables/               # Generated tables (CSV and LaTeX)
│   └── figures/              # Generated figures (PNG and PDF)
└── paper/
    └── draft.md              # Paper draft (not included)
```

---

## Data Sources

| Data | Source | Access |
|------|--------|--------|
| HREA settlement estimates | Min et al. (2024) | `s3://globalnightlight/HREA/` |
| WDI electrification rates | World Bank | `https://data.worldbank.org/indicator/EG.ELC.ACCS.ZS` |
| Administrative boundaries | GADM v4.1 | `https://gadm.org/` |

**Note:** Raw HREA tiles (~34 GB for 12 countries) are not included in this repository. Run `01_download_hrea.py` to download them.

---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/[YOUR-USERNAME]/hrea-replication.git
cd hrea-replication
```

### 2. Create virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download data

```bash
# Download HREA tiles from AWS (requires ~34 GB disk space)
python scripts/01_download_hrea.py

# Download WDI data
python scripts/02_download_wdi.py
```

### 5. Run analysis

```bash
# Process HREA tiles into summary statistics
python scripts/03_process_hrea.py

# Run main analysis (generates tables)
python scripts/04_analysis.py

# Generate figures
python scripts/05_figures.py
```

---

## Country Sample

| Country | ISO3 | Region | WDI 2020 (%) |
|---------|------|--------|--------------|
| Nigeria | NGA | SSA | 55.4 |
| Kenya | KEN | SSA | 71.5 |
| Ethiopia | ETH | SSA | 51.1 |
| Tanzania | TZA | SSA | 39.9 |
| Ghana | GHA | SSA | 85.4 |
| Uganda | UGA | SSA | 42.1 |
| India | IND | South Asia | 96.5 |
| Bangladesh | BGD | South Asia | 96.2 |
| Nepal | NPL | South Asia | 89.9 |
| Pakistan | PAK | South Asia | 94.5 |
| Myanmar | MMR | South Asia | 70.4 |
| Cambodia | KHM | Southeast Asia | 86.4 |

---

## Outputs

### Tables
- **Table 3:** HREA Summary Statistics by Country (2020)
- **Table 4:** HREA Replication Results (2020)
- **Table 5:** HREA-WDI Correlation by Region
- **Table 6:** Temporal Stability of HREA-WDI Correlation
- **Table 7:** Transparency Checklist for Satellite Energy Tools

### Figures
- **Figure 1:** Lightscore Distributions by Region
- **Figure 2:** HREA vs WDI Scatter Plot
- **Figure 3:** Regional Validation (HREA Mean vs WDI by Region)
- **Figure 4:** Calibration Plot
- **Figure 5:** Temporal Stability (2013, 2016, 2020)
- **Figure 6:** HREA-WDI Gap by Electrification Level

---

## Requirements

- Python 3.9+
- ~34 GB disk space (for raw HREA tiles)
- Internet connection (for data download)

See `requirements.txt` for Python package dependencies.

---

## Citation

If you use this code, please cite:

```bibtex
@unpublished{hoffman2026hrea,
  author = {Hoffman, Alexei},
  title = {Reproducibility and Geographic Transfer of Satellite-Based Electrification Predictions: Testing High-Resolution Electricity Access Models Across Africa and Asia},
  year = {2026},
  note = {Presented at MeasureDev 2026, World Bank}
}
```

---

## License

MIT License. See LICENSE file.

---

## Contact

Alexei (Frank) Hoffman  
Georgetown University, Walsh School of Foregin Service  
fdh14(at)georgetown(dot)edu

---

## Acknowledgments

HREA data provided by Min et al. (2024) via the World Bank Light Every Night initiative. WDI data from the World Bank Open Data platform.
