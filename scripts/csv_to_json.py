#!/usr/bin/env python3
"""
Migrate per-category CSVs into a single canonical data/programs.json.

Source CSVs live in ../../research/dev-funding/sheet-export/ (the research workspace).
Output: data/programs.json — the single source of truth for README + static site.
"""
from __future__ import annotations
import csv
import json
import re
import sys
from pathlib import Path

REPO     = Path(__file__).resolve().parent.parent
SRC_DIR  = Path("/Users/pleasedodisturb/Projects/scratch/old-research/dev-funding/sheet-export")
OUT_FILE = REPO / "data" / "programs.json"

CATEGORIES = {
    "01-ai-lab-credits.csv":            ("ai-lab-credits",          "AI Lab Credits"),
    "02-oss-framework-grants.csv":      ("oss-framework-grants",    "OSS Framework Grants"),
    "03-cloud-compute-credits.csv":     ("cloud-compute-credits",   "Cloud Compute Credits"),
    "04-accelerators-fellowships.csv":  ("accelerators-fellowships","Accelerators & Fellowships"),
    "05-government-foundation-grants.csv": ("gov-foundation-grants","Government & Foundation Grants"),
    "06-crypto-web3-grants.csv":        ("crypto-web3-grants",      "Crypto / Web3 Grants"),
    "07-production-revenue-paths.csv":  ("production-revenue",      "Production & Revenue Paths"),
}

def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-")[:80]

def parse_amount_max_usd(amount: str) -> int | None:
    """Best-effort numeric extraction for sorting. Returns None for unbounded/varies."""
    if not amount:
        return None
    s = amount.replace(",", "")
    # try '$X-$Y' or 'Up to $Z' patterns
    nums = re.findall(r"\$?\s*(\d+(?:\.\d+)?)\s*([KkMmBb])?", s)
    if not nums:
        return None
    def to_int(n: str, suf: str) -> int:
        v = float(n)
        suf = suf.lower() if suf else ""
        return int(v * {"": 1, "k": 1_000, "m": 1_000_000, "b": 1_000_000_000}[suf])
    # Take MAX of any numbers found (for ranges, picks the upper bound)
    return max(to_int(n, suf) for n, suf in nums)

def normalize_solo(s: str) -> str:
    """Map free-text Solo OK column to: yes | conditional | no | unknown."""
    if not s:
        return "unknown"
    low = s.lower().strip()
    if low.startswith("yes"):  return "yes"
    if low.startswith("no"):   return "no"
    if low.startswith("conditional"): return "conditional"
    return "unknown"

def normalize_status(s: str) -> str:
    """Map Status to: open | conditional | closed | unknown."""
    if not s:
        return "unknown"
    low = s.lower().strip()
    if low == "open": return "open"
    if low == "closed": return "closed"
    if low == "conditional": return "conditional"
    return "unknown"

def main():
    if not SRC_DIR.exists():
        sys.exit(f"Source CSV dir not found: {SRC_DIR}")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    programs: list[dict] = []
    for csv_name, (cat_id, cat_label) in CATEGORIES.items():
        path = SRC_DIR / csv_name
        if not path.exists():
            print(f"!! missing {path}", file=sys.stderr)
            continue
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                program = {
                    "id":          slugify(f"{cat_id}-{row['Program']}"),
                    "name":        row["Program"].strip(),
                    "category_id": cat_id,
                    "category":    cat_label,
                    "amount":      row["Amount"].strip(),
                    "amount_max_usd": parse_amount_max_usd(row["Amount"]),
                    "type":        row["Type"].strip(),
                    "solo_ok":     normalize_solo(row["Solo OK"]),
                    "solo_ok_raw": row["Solo OK"].strip(),
                    "entity":      row["Entity"].strip(),
                    "geography":   row["Geography"].strip(),
                    "url":         row["URL"].strip(),
                    "status":      normalize_status(row["Status"]),
                    "notes":       row["Notes"].strip(),
                }
                programs.append(program)

    out = {
        "schema_version": 1,
        "last_verified":  "2026-05-08",
        "total":          len(programs),
        "categories":     [{"id": cid, "label": lbl} for (cid, lbl) in CATEGORIES.values()],
        "programs":       programs,
    }
    OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(f"Wrote {len(programs)} programs to {OUT_FILE}")
    # Quick sanity stats
    from collections import Counter
    print(f"  by status:  {dict(Counter(p['status'] for p in programs))}")
    print(f"  by solo_ok: {dict(Counter(p['solo_ok'] for p in programs))}")
    print(f"  by category:")
    for cid, lbl in CATEGORIES.values():
        n = sum(1 for p in programs if p['category_id'] == cid)
        print(f"    {n:3d}  {lbl}")

if __name__ == "__main__":
    main()
