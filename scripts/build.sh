#!/usr/bin/env bash
# One-shot build: regenerate README from data/programs.json, stage data into
# site/ for static deploy.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# 1. (Opt-in) re-import from the upstream CSV export.
#
#    data/programs.json is the source of truth. The CSVs under sheet-export/ are a
#    one-time May 2026 import that has NOT been maintained since; re-importing them
#    silently reverts every later curation. Measured 2026-07-21: a re-import reverted
#    18 fields, including the Goose grant URL (to a dead block.xyz link), the NSF
#    26-510 solicitation details, and the GitHub Secure OSS Fund amount correction.
#
#    This used to run automatically whenever the CSV directory happened to exist on
#    the machine, so a routine local build could undo curated data with no diff review.
#    It is now opt-in, and should only be used to re-seed from a *freshly exported* CSV.
if [ "${AADF_REGEN_FROM_CSV:-0}" = "1" ]; then
  echo "WARNING: re-importing data/programs.json from sheet-export CSVs."
  echo "         Review 'git diff data/programs.json' before committing."
  python3 scripts/csv_to_json.py
fi

# 2. Regenerate README from data/programs.json
python3 scripts/build_readme.py

# 3. Stage data for the static site (single deploy artifact = ./site/)
mkdir -p site/data
cp data/programs.json site/data/programs.json

echo "Build complete. Deploy artifact: ./site/"
