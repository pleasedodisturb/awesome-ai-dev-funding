#!/usr/bin/env python3
"""
Generate README.md from data/programs.json.

Rationale: the README is the canonical github.com landing page (drives "awesome-"
discovery via SEO). Per awesome-list convention: TOC + per-category tables.
Both this README and the static site read from the same JSON, so they cannot drift.
"""
from __future__ import annotations
import json
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "programs.json"
OUT  = REPO / "README.md"

SOLO_BADGE = {
    "yes":         "Yes",
    "conditional": "Conditional",
    "no":          "No",
    "unknown":     "?",
}
STATUS_BADGE = {
    "open":        "Open",
    "conditional": "Conditional",
    "closed":      "Closed",
    "unknown":     "?",
}

def md_escape(s: str) -> str:
    """Escape pipe characters that would break markdown tables."""
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()

def main():
    data = json.loads(DATA.read_text())
    programs = data["programs"]
    cats     = data["categories"]
    last     = data["last_verified"]

    by_cat: dict[str, list[dict]] = defaultdict(list)
    for p in programs:
        by_cat[p["category_id"]].append(p)

    out: list[str] = []
    out.append("# Awesome AI Dev Funding [![Awesome](https://awesome.re/badge.svg)](https://awesome.re)")
    out.append("")
    out.append(f"> Curated list of funding programs for AI developers — credits, grants, fellowships, accelerators, bounties, and revenue paths. **{len(programs)} programs across {len(cats)} categories**, last verified {last}.")
    out.append("")
    out.append("Built for **solo AI developers** without VC backing or institutional affiliation. Every program is annotated with whether it's actually accessible to a solo dev, the realistic award amount, and the current status.")
    out.append("")
    out.append("**Quick filters:**")
    yes_open = sum(1 for p in programs if p["solo_ok"] == "yes" and p["status"] == "open")
    out.append(f"- 🟢 **{yes_open} programs** are *open* and *truly solo-friendly* — start here")
    out.append(f"- Browse the [interactive filterable site →](#interactive-site) for sortable tables and search")
    out.append("")
    out.append("---")
    out.append("")

    # --- TOC ------------------------------------------------------------
    out.append("## Contents")
    out.append("")
    for cat in cats:
        n = len(by_cat[cat["id"]])
        anchor = cat["label"].lower().replace(" & ", "--").replace(" / ", "--").replace(" ", "-")
        out.append(f"- [{cat['label']}](#{anchor}) ({n})")
    out.append("- [Interactive site](#interactive-site)")
    out.append("- [Contributing](#contributing)")
    out.append("- [License](#license)")
    out.append("")

    # --- Per-category tables -------------------------------------------
    for cat in cats:
        items = by_cat[cat["id"]]
        if not items:
            continue
        # sort: open+yes first, then by amount desc
        items.sort(key=lambda p: (
            0 if p["status"] == "open" and p["solo_ok"] == "yes" else
            1 if p["status"] == "open" else
            2 if p["status"] == "conditional" else 3,
            -(p["amount_max_usd"] or 0),
        ))
        out.append(f"## {cat['label']}")
        out.append("")
        out.append(f"_{len(items)} programs_")
        out.append("")
        out.append("| Program | Amount | Solo OK | Status | Notes |")
        out.append("| --- | --- | --- | --- | --- |")
        for p in items:
            indicator = ""
            if p["status"] == "open" and p["solo_ok"] == "yes":
                indicator = "🟢 "
            elif p["status"] == "open" and p["solo_ok"] == "conditional":
                indicator = "🟡 "
            elif p["status"] == "open" and p["solo_ok"] == "no":
                indicator = "🟠 "
            elif p["status"] == "closed":
                indicator = "🔴 "
            elif p["status"] == "conditional":
                indicator = "🟡 "
            name_link = f"{indicator}[{md_escape(p['name'])}]({p['url']})"
            note = md_escape(p["notes"])
            if len(note) > 110:
                note = note[:107] + "..."
            out.append(f"| {name_link} | {md_escape(p['amount'])} | {SOLO_BADGE[p['solo_ok']]} | {STATUS_BADGE[p['status']]} | {note} |")
        out.append("")

    # --- Footer sections ------------------------------------------------
    out.append("## Interactive site")
    out.append("")
    out.append("This list is also available as a filterable, sortable, searchable static site:")
    out.append("")
    out.append("- **GitHub Pages**: https://pleasedodisturb.github.io/awesome-ai-dev-funding/")
    out.append("- **Vercel**: _connect at vercel.com/new_")
    out.append("- **Netlify**: _connect at app.netlify.com/start_")
    out.append("")
    out.append("Source data lives in [`data/programs.json`](./data/programs.json). The README and site both build from that single file.")
    out.append("")
    out.append("## Contributing")
    out.append("")
    out.append("PRs welcome. To add or update a program:")
    out.append("1. Edit [`data/programs.json`](./data/programs.json) (see existing entries for the schema)")
    out.append("2. Run `python3 scripts/build_readme.py` to regenerate this README")
    out.append("3. Open a PR with the source link verifying the program details")
    out.append("")
    out.append("See [CONTRIBUTING.md](./CONTRIBUTING.md) for full guidelines.")
    out.append("")
    out.append("## License")
    out.append("")
    out.append("[![CC0](https://mirrors.creativecommons.org/presskit/buttons/88x31/svg/cc-zero.svg)](https://creativecommons.org/publicdomain/zero/1.0/)")
    out.append("")
    out.append("Data + content: [CC0-1.0](./LICENSE) (public domain). Code in `/scripts/` and `/site/`: [MIT](./LICENSE-CODE).")
    out.append("")

    OUT.write_text("\n".join(out))
    print(f"Wrote {OUT} ({len(out)} lines)")

if __name__ == "__main__":
    main()
