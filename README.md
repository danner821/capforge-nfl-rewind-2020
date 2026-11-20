# CapForge: NFL Rewind 2020

A fan-made experimental **2020 NFL historical roster** with Madden-style attributes and future real draft prospects. All files are separate from Project Ice.

## Status

**Experimental V9 draft-preview test.** V8 has successfully imported into a playable 2020 league and shown 2021 prospects, but the new complete V9 classes still require direct game import and future-season validation. The first imported candidate produced thousands of warnings; calibrated v2 is designed to address its portrait and OVR warnings, but must be revalidated in-game. Starting rosters use a Madden NFL 21 (2020) ratings snapshot and reconstructed 2020 team identities. Contracts are **temporary approximations**, not authenticated 2020 cap hits. Rookie class coverage and exact 2020 Week 1 lineups require further review.

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

## League construction: personnel fix (V4)

The first clean V3 import still failed after Choose Your Path with a CapForge **Bad state**: all 32 teams were "short of required personnel" (the game's error explicitly reported no teams over cap). Root cause: the source Madden LE/RE players were all originally converted into CapForge `EDGE`, leaving every NFL club with zero `DE`. CapForge requires separate DE and EDGE groups.

The **current test file** is [2020 Players + 2021–2024 — Personnel V4](preview/players-2020-four-class-personnel-v4.json). It restores DE/EDGE separation, preserves player-specific Madden OVR targets and keeps a defensive depth floor (2 DE, 3 EDGE, 2 DT) plus every required position on all 32 teams. The report verifies 32 teams with no missing positional groups; these floors are inferred, not claimed as CapForge's official minimums.

Use [2020 Teams roofs V2](preview/teams-2020-roofs-v2.json) and default staff. Revalidate in-game, then try a *disposable* league with the 2020 regular-season kickoff. Please report whether Choose Your Path builds the league. Do not start the permanent save until both construction and class persistence are verified.

## V6 portrait-matched test (2020 league confirmed to launch with V4)

The user confirmed in-game that V4 successfully starts a 2020 NFL league, but default-generated players' faces did not resemble the named NFL players. We cannot substitute actual headshots via the currently supported `portraitId` field; the game uses built-in cartoon portraits.

The **current experimental portrait test** is [Players V6](preview/players-2020-four-class-portraits-v6.json). It reuses exact-name, position-compatible, age-aligned `portraitId` values from the original creator's 2018 and 2026 roster packs. Unmatched players intentionally keep default portraits. It does not alter ratings, contracts, team assignments, draft classes, or hidden potentials.

The initial successful V6 generation reported **1,431/2,293 starting roster players** with matched community portrait assignments; **2,508 total assignments** including future draft classes through 2026. These are still approximate visual matches, not real NFL likenesses.

**Import test:** New Game → Import → use the V6 players file and [2020 Teams roofs V2](preview/teams-2020-roofs-v2.json); staff blank. Press Validate and inspect for any portrait warning. If accepted, start only a disposable save and examine recognizable players to see whether the choices are actually better. Bulk player imports do not replace players in an existing save. Do not start the permanent career yet; historical contracts and the fourth-class persistence test remain open.



## V9 real-first, complete draft-class test (next disposable in-game test)

**V9 fixes the 480-prospect filler problem observed on the 2021 big board in the successful 2020 V8 import.** V8 supplied only 286 named 2021 prospects; CapForge displayed 480 with high-ranked generic names. V9 imports **exactly 480 independently documented real-player identities in each 2021–2026 class**, from the existing historic Madden-based records, verified NFL draft picks, NFL.com undrafted signings, and published combine/pro-day records. All previously supplied 4,180 V8 player records (including portraits, ratings, contracts and private progression) are preserved unchanged.

- [Players V9 — 2021–2024, four draft years](preview/players-2020-four-class-authentic-v9.json): **4,213 players including 2020 starters**.
- [Players V9 — 2021–2026, six draft years](preview/players-2020-six-class-authentic-v9.json): **5,173 players including 2020 starters**.
- [Teams V2](preview/teams-2020-roofs-v2.json): same accepted 32 historical teams. Staff: default.
- [Prospect source coverage and limitations](preview/v9-draft-pool-report.json), [NFL drafted-name audit](preview/v9-draft-coverage-report.json): both spoiler-free.

**How to test:** In CapForge New Game → Import, use **six-class V9 Players** plus **Teams V2**; choose Sep Reg Season with default staff and create a new disposable 2020 save. Confirm 2,293 starting roster players and 32 teams are accepted; then Market → Draft → Board for 2021, inspect whether the old generated big-board names are gone. Menu → Edit Players shows year tabs 2021–2026; those tabs alone don't confirm future-year survival. Verify later years through a throwaway advance before committing to a permanent career.

**Ratings provenance:** All added identities are real and draft-year documented, but **additional prospect attributes are position-based, conservative models** inferred from available physical/scouting data and position-specific imported attributes. They are NOT historical Madden 2021–2026 attribute exports. No historical pick outcomes or teams are forced, and actual per-player potential remains private. The app may still apply its own scouting/projections, and clean GitHub CI does not imply CapForge in-game acceptance. Versioned V9 exports are frozen after publication; older V6/V7/V8 files and Project Ice stay intact.

## V8 draft-reconciled test (older in-game checkpoint)

A new **history V8** backfill repairs 27 historically drafted prospects using evidence from later Madden entries or verified matching 2026 community records. It contains the same 2,293-player starting roster and preserves the previously approved V6 cartoon portrait checkpoint. Other missing picks are not fabricated without reliable attribute data.

- [Players V8 — 2021–2024 drafts](preview/players-2020-four-class-history-v8.json): **3,532 records**. Test 2020 league construction and the fourth class in a disposable save.
- [Players V8 — 2021–2026 drafts](preview/players-2020-six-class-history-v8.json): **4,180 records**. Optional six-year disposable-save test; game acceptance and persistence of later classes remain unverified.
- [Teams V2](preview/teams-2020-roofs-v2.json): 2020 historical teams and importer-accepted roof values; use default Staff.
- [Spoiler-free draft coverage](preview/draft-coverage-report.json): V8 pick-name audit against independent 2021–2026 draft lists; no development potentials disclosed.

The V8 source-backed repair does **not** establish that all late-round players, the full 480 prospects per draft year, exact 2020 Week 1 contracts, or historical staff are complete. If V8 fails, continue with the user-approved V6 roster. Do not use any preview to overwrite a working long-term save, and do not open the raw player files to inspect hidden progression.

## V7 six-class preview and historical-draft coverage audit

User tested V6 portraits across multiple teams and reported that the cartoon portrait assignments look good. **Do not replace the working V6 file**; it remains the confirmed portrait version. The portrait database can be improved later using verified same-position matches. Do not invent portrait IDs or inject real-world images.

The new optional **2020 + all six historical draft years** test file is [Players V7](preview/players-2020-six-class-draftfix-v7.json). It retains the 2020 roster, player portrait-matching rules, team mapping and historical-style ratings. It corrects Madden 26 player position labels ("Mike Backer", "Weak Backer", "Sam Backer", "Long Snapper") so 2025 rookie-class entries are no longer accidentally skipped.

[Draft coverage report](preview/draft-coverage-report.json) checks the actual 2021-2026 NFL draft selection list against prospects by name, not their hidden potential. It verifies that **every player drafted in rounds 1-3** appears in the six-class import. Later-round selections are still under review and every class has fewer than 480 entries. The game may fill remaining prospects or require expansion; this has not been independently verified.

### Next CapForge test (disposable save only)
- Players: `https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/players-2020-six-class-draftfix-v7.json`
- Teams: `https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/teams-2020-roofs-v2.json`
- Staff: Default.
- Verify both import links; open a *test* 2020 league if valid. Confirm future draft classes appear as their years approach. A successful URL validation alone **does not establish the game can use year 4-6 classes**.
- Never expose player hidden potential/retrospective career rankings to the user. Do not use this preview for the permanent long-term 2020 save yet; contracts/FA/staff/history still need work.
