# CapForge: NFL Rewind 2020

A fan-made experimental **2020 NFL historical roster** with Madden-style attributes and future real draft prospects. All files are separate from Project Ice.

## Status

**Preview only — not validated inside CapForge.** The first imported candidate produced thousands of warnings; calibrated v2 is designed to address its portrait and OVR warnings, but must be revalidated in-game. Starting rosters use a Madden NFL 21 (2020) ratings snapshot and reconstructed 2020 team identities. Contracts are **temporary approximations**, not authenticated 2020 cap hits. Rookie class coverage and exact 2020 Week 1 lineups require further review.

## Once the build workflow succeeds

| File | Purpose |
| --- | --- |
| [2020 Teams](preview/teams-2020.json) | 2020 NFL team names, colors, stadiums |
| [2020 Players + 2021–2023 Classes](preview/players-2020-three-class.json) | Conservative initial import test |
| [2020 Players + 2021–2024 Classes — Positional v3](preview/players-2020-four-class-position-v3.json) | **Recommended current test**: proper EDGE/LB mapping + OVR calibration |
| [2020 Teams — Valid roofs v2](preview/teams-2020-roofs-v2.json) | **Recommended current test**: accepted roof enum values |
| [2020 Players + 2021–2024 Classes — Calibrated v2](preview/players-2020-four-class-calibrated-v2.json) | Previous test: portraits removed, OVR recalibrated against CapForge model |\n| [Previous 4-class test](preview/players-2020-four-class-test.json) | Earlier candidate kept only for comparison; do not start a game with it |
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

## Import warnings / calibrated second test

A prior tester's screenshot showed 4,324+ warnings: random portrait identifiers were invalid for many positions and Madden's base OVR was incompatible with CapForge's formula (for instance, some 99 OVR stars were scored far lower from the individual attributes). **V2 removes explicit portraitId fields and recalibrates the underlying Madden-derived attributes** using approximate CapForge OVR coefficients inferred from a 2035 game-generated roster. The build report checks count of absent portraits and 2+ point estimated OVR mismatches; this is **not** equivalent to CapForge's actual validator.

Please use the newly versioned `preview/players-2020-four-class-calibrated-v2.json` URL (not the old URL) to avoid stale URL caching. Use **our** `preview/teams-2020.json` for 2020 identities, not the other roster creator's 2026 team file. Leave staff blank for testing. Observe and report the exact warning count, not just the green checkmark.

## Latest validation response (2026-11-19)

- Calibrated v2 showed only two warnings on 2,293 current players: positions 12 and 22 (Khalil Mack and Chandler Jones).
- Teams file was rejected with three roof errors: 'fixed' is invalid in CapForge. New teams v2 uses 'dome' for fixed roofs.
- V3 classifies pass-rush Madden outside linebackers as CapForge EDGE and recalibrates their attributes.
- Use both new, versioned links from the table above. Automated build succeeded, but the game still needs to validate these new links.
