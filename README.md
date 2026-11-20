# CapForge: NFL Rewind 2020

A fan-made experimental **2020 NFL historical roster** with Madden-style attributes and future real draft prospects. All files are separate from Project Ice.

## Status

**Preview only — not validated inside CapForge.** Starting rosters use a Madden NFL 21 (2020) ratings snapshot and reconstructed 2020 team identities. Contracts are **temporary approximations**, not authenticated 2020 cap hits. Rookie class coverage and exact 2020 Week 1 lineups require further review.

## Once the build workflow succeeds

| File | Purpose |
| --- | --- |
| [2020 Teams](preview/teams-2020.json) | 2020 NFL team names, colors, stadiums |
| [2020 Players + 2021–2023 Classes](preview/players-2020-three-class.json) | Conservative initial import test |
| [2020 Players + 2021–2024 Classes](preview/players-2020-four-class-test.json) | Isolated test for a fourth historical draft class |
| [2020 Players + 2021–2026 Classes](preview/players-2020-extended-experimental.json) | Experimental six-class test; additional future years **not verified** |
| [Spoiler-free Build Report](preview/build-report.json) | Team and draft-class counts, known limitations |

These links will work only after GitHub Actions generates the files. [Build workflow](.github/workflows/build-roster.yml).

## Initial test plan

1. In CapForge select **New Game → Import**.
2. Paste the GitHub **Players** link and optional **Teams** link. Do not use the raw JSON page to inspect potentials.
3. Press **Validate**, then choose **Reg Season** (2020's rookies are already on teams).
4. Confirm all teams appear and that 2021 prospects are visible in-game.
5. Separately test the extended six-class candidate and check whether years 2024–2026 survive import and season progression.

**Do not replace a working long-term save with this preview.** Import validity, salary balance and advancement still require testing.

## Hidden progression: no spoilers

Player potential and curves are stored in the JSON because the importer requires them. No output report lists individual potentials, future career outcomes, or hindsight-ranked draft steals. Starting rookie ratings receive only a mild **cohort-wide** uplift; later real-world career performance is used to estimate hidden progression ceilings.

If you want to play blind, **don't open the players JSON on GitHub**.

## Source provenance

- [2020–2024 historical Madden ratings](https://github.com/theedgepredictor/nfl-madden-data).
- [Madden NFL 26 data for 2025](https://github.com/thompgt/madden-analysis). This may not be launch-day data.
- [2026 Madden-derived roster and 2018 team schema](https://github.com/jmansfield96/capforge-custom-rosters).
- The user's 2035 CapForge export informs schema validation only.

These are independent community data sources, not official historical league exports. Fan project; no affiliation with EA SPORTS, the NFL, or CapForge.

## Developer workflow

```sh
python scripts/build_2020.py
python scripts/validate_capforge_roster.py preview/players-2020-three-class.json preview/players-2020-extended-experimental.json
```
