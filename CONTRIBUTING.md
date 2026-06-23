# Contributing

Thanks for considering a contribution. This list aims to be **curated, accurate, and solo-dev-honest** — every program annotated for what it actually delivers, with stale entries marked rather than silently kept.

## What to contribute

Top priorities, in order:

1. **New programs** that fit one of the seven existing categories
2. **Status updates** — programs that opened, closed, paused, or changed amount
3. **Solo-OK reality checks** — if a program nominally accepts solo applicants but in practice rejects them, change `solo_ok` to `conditional` and add a note
4. **URL fixes** when a program's official page moves
5. **Schema additions** — propose new fields via issue first

## How to add or update a program

1. Edit [`data/programs.json`](./data/programs.json) — that's the single source of truth.
2. Use this schema:
   ```json
   {
     "id":          "kebab-cased-unique-id",
     "name":        "Program Name",
     "category_id": "ai-lab-credits | oss-framework-grants | cloud-compute-credits | accelerators-fellowships | gov-foundation-grants | crypto-web3-grants | production-revenue",
     "category":    "Human-Readable Category Label",
     "amount":      "Free-text amount (e.g., '$25K-$100K')",
     "amount_max_usd": 100000,
     "type":        "Credits | Cash | Equity | Fellowship | etc.",
     "solo_ok":     "yes | conditional | no",
     "solo_ok_raw": "Free-text — captures nuance like 'Yes (academic)'",
     "entity":      "Who's eligible — e.g., 'Solo OSS maintainer'",
     "geography":   "US | EU | Global | etc.",
     "url":         "Canonical URL to apply or learn more",
     "status":      "open | conditional | closed",
     "notes":       "≤200 chars, blunt about reality (no marketing fluff)"
   }
   ```
3. Run the build:
   ```bash
   bash scripts/build.sh
   ```
   This regenerates `README.md` and stages the data file for the static site. Commit both `data/programs.json` and the regenerated `README.md`.
4. Open a PR. Include in the description:
   - Source URL(s) that verify the program details
   - When you last verified them (date)
   - If updating an existing entry, what changed and why

## Style guide for `notes`

Keep notes:
- **Short** (target ≤120 chars; hard cap 200)
- **Concrete** — deadlines, eligibility gotchas, pitfalls
- **Honest** — call out VC gating, hidden caveats, paused programs

Avoid:
- "Innovative", "ecosystem-leading", marketing adjectives
- Vague claims ("flexible amounts" — give a range)
- Duplication of obvious fields ("Status: OPEN" already in the table)

## Removing programs

If a program is genuinely defunct (not just paused), keep the entry with `status: "closed"` and a note explaining when/why it ended. Removing entirely loses signal for users searching for it.

## Reporting issues

Open a GitHub Issue with one of these templates:
- **Stale entry** — program details have changed
- **Missing program** — propose a new addition
- **Schema/site bug** — UI, build, or data structure issue

## License

Data + content contributions are released under [CC0-1.0](./LICENSE).
Code contributions (`/scripts/`, `/site/`) under [MIT](./LICENSE-CODE).
By submitting a PR, you confirm you can release your contribution under these terms.
