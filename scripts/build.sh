#!/usr/bin/env bash
# One-shot build: regenerate JSON from CSVs (if available), regenerate README,
# stage data into site/ for static deploy.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 1. (Optional) regenerate data from upstream CSVs if they exist locally.
#    In CI this step is skipped — programs.json is already committed.
if [ -d "/Users/pleasedodisturb/Projects/scratch/old-research/dev-funding/sheet-export" ]; then
  python3 scripts/csv_to_json.py
fi

# 2. Regenerate README from data/programs.json
python3 scripts/build_readme.py

# 3. Stage data for the static site (single deploy artifact = ./site/)
mkdir -p site/data
cp data/programs.json site/data/programs.json

echo "Build complete. Deploy artifact: ./site/"
