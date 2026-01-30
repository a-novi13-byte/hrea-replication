# GitHub Setup Guide

This guide walks you through setting up a GitHub repository for your replication package. No prior Git experience required.

---

## Step 1: Create a GitHub Account (if needed)

1. Go to [github.com](https://github.com)
2. Click "Sign up" and follow the prompts
3. Verify your email address

---

## Step 2: Install Git

### On Mac:
```bash
# Option 1: Install via Homebrew (recommended)
brew install git

# Option 2: Install Xcode Command Line Tools
xcode-select --install
```

### On Windows:
1. Download from [git-scm.com](https://git-scm.com/download/win)
2. Run the installer (accept defaults)

### Verify installation:
```bash
git --version
# Should show something like: git version 2.39.0
```

---

## Step 3: Configure Git

Open Terminal (Mac) or Git Bash (Windows) and run:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Use the same email as your GitHub account.

---

## Step 4: Create the Repository on GitHub

1. Log into GitHub
2. Click the **+** icon (top right) → **New repository**
3. Fill in:
   - **Repository name:** `hrea-replication`
   - **Description:** `Replication package for "Reproducibility and Geographic Transfer of Satellite-Based Electrification Predictions"`
   - **Public** (for open science) or **Private** (until publication)
   - ☐ Do NOT initialize with README (we have one)
4. Click **Create repository**
5. Copy the repository URL (looks like `https://github.com/YOUR-USERNAME/hrea-replication.git`)

---

## Step 5: Upload the Replication Package

### Option A: Using Command Line (Recommended)

Navigate to your replication package folder:

```bash
cd /path/to/replication_package
```

Initialize Git and push:

```bash
# Initialize Git repository
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: HREA replication package"

# Connect to GitHub (replace URL with yours)
git remote add origin https://github.com/YOUR-USERNAME/hrea-replication.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option B: Using GitHub Desktop (Easier)

1. Download [GitHub Desktop](https://desktop.github.com/)
2. Sign in with your GitHub account
3. File → Add Local Repository → Select your replication_package folder
4. It will prompt to "Create a repository" — click it
5. Click "Publish repository"

---

## Step 6: Verify Upload

1. Go to `github.com/YOUR-USERNAME/hrea-replication`
2. You should see all files:
   ```
   ├── README.md
   ├── LICENSE
   ├── requirements.txt
   ├── scripts/
   │   ├── 01_download_hrea.py
   │   ├── 02_download_wdi.py
   │   ├── 03_process_hrea.py
   │   ├── 04_analysis.py
   │   ├── 05_figures.py
   │   └── utils.py
   └── ...
   ```

---

## Step 7: Add Processed Data (Optional)

If you want to include the processed CSV files (so others don't need to download 34GB of raw data):

```bash
# Create the processed data directory
mkdir -p data/processed

# Copy your CSV files there
cp /path/to/your/csvs/*.csv data/processed/

# Add and commit
git add data/processed/
git commit -m "Add processed data files"
git push
```

---

## Step 8: Create a Release (For Citation)

Once your paper is accepted:

1. Go to your repository on GitHub
2. Click "Releases" (right sidebar)
3. Click "Create a new release"
4. Tag version: `v1.0.0`
5. Title: `MeasureDev 2026 Release`
6. Description: Paper citation and brief description
7. Click "Publish release"

This creates a citable, permanent snapshot with a DOI (via Zenodo integration).

---

## Quick Reference: Common Git Commands

```bash
# Check status
git status

# Add changes
git add .

# Commit with message
git commit -m "Description of changes"

# Push to GitHub
git push

# Pull latest changes
git pull
```

---

## Troubleshooting

### "Permission denied" error
You may need to set up SSH keys or use a personal access token:
1. GitHub → Settings → Developer Settings → Personal Access Tokens
2. Generate new token with "repo" permissions
3. Use token as password when pushing

### "Repository not found" error
Check that:
- The repository exists on GitHub
- You've spelled the URL correctly
- You have permissions (if private repo)

### Large files error
Git doesn't handle large files well. The `.gitignore` excludes raw data files (*.tif). 
If you need to include large files, look into [Git LFS](https://git-lfs.github.com/).

---

## Your Repository URL

After setup, your replication code will be at:

```
https://github.com/YOUR-USERNAME/hrea-replication
```

Add this URL to:
- Your paper's Data Availability Statement
- Conference submission materials
- Abstract/keywords

---

## Need Help?

- GitHub Docs: [docs.github.com](https://docs.github.com)
- Git tutorial: [git-scm.com/book](https://git-scm.com/book/en/v2)
