# CapForge NFL Rewind 2020 — Verified Roadmap

_Last reviewed: 2026-11-20. Single source of truth: current main branch, versioned exports, and actual in-game tester feedback. No silent changes to existing saves or Project Ice._

## Status key
- **APPROVED IN GAME:** user inspected the actual CapForge result; narrow claim only.
- **CI VERIFIED:** scripts and build checks passed, but not confirmed by the game.
- **IN DEVELOPMENT:** code/research underway, not yet verified.
- **BLOCKED ON GAME TEST:** player needs to test a disposable new save.
- **NOT STARTED:** no claim of completion.

| Order | Workstream | Status | Current evidence | Next acceptance gate |
|---|---|---|---|---|
| 1 | 2020 league shell, team identities, 2020 starter import | **APPROVED IN GAME (limited)** | User previously started 2020 test league; V4 personnel fix worked; 32 teams and 2,293 rostered players on V10 import | Audit authentic Week 1 depth charts separately |
| 2 | 2021–2026 draft classes | **CI VERIFIED + 2021 BOARD APPROVED IN GAME** | V9 created 480 documented identities/year; user checked realistic 2021 board | Simulate to 2022–26 in a disposable game |
| 3 | 2027 prospect board and Arch Manning portrait | **APPROVED IN GAME** | User 2026-11-20: 2027 board looks good and Arch's in-game cartoon portrait looks good | Preserve unchanged on V15 and later |
| 4 | 2028–2029 top prospect coverage | **APPROVED IN GAME (spotlight visual check V15)** | User confirmed V15 looked good; 54 sourced spotlight 2028 prospects, 46 provisional 2029 candidates, 480 per year in CI | Retain V15 unchanged; full-year survival still requires sim test |
| 5 | 2028–2029 cartoon portraits | **APPROVED IN GAME (user-inspected sample, not all 960)** | User confirmed V15 looks good; 960 game-generated default portraits, no individual manual likeness confirmation across entire class | Preserve approved visuals; refine only newly reported outliers from actual screenshots |
| 6 | Nine-class long-horizon persistence | **BLOCKED ON GAME TEST** | Future year tabs and early board display ≠ surviving season progression | Advance multiple years in disposable save; inspect drafts/players from 2022 to 2029, persistence and any crashes |
| 7 | Authentic 2020 contracts and team salary caps (V14) | **V18 PARQUET AUDIT IN PROGRESS; V14 NOT BUILT** | V13 placeholder 2020 payroll; V17 1,721 plausible candidate matches, 473 ambiguous and 99 missing; annual CSV histories empty | Inspect yearly Parquet source, verify 2020 salary/proration and unique identity matches; build separate contract import only after source checks |
| 8 | 2020 head coaches and coordinators (V16) | **CAPFORGE IMPORT CHECK PASSED; IN-GAME NAME REVIEW OPTIONAL** | User reports green Staff checkmark; 32 clubs × 4 sourced preseason leadership chairs, including 4 labeled functional proxies | Keep V16; optionally inspect a few coach/team assignments, not another entire staff rebuild |
| 9 | Accurate 2020 Week 1 depth, injuries and transactions | **NOT STARTED** | Madden 21-derived snapshot is not guaranteed exact Week 1 | Audit 32 rosters against contemporary 2020 team records, preserve cap legality |
| 10 | Season history, free agency, scouting, draft and contracts regression | **NOT STARTED** | CapForge franchise is not our codebase; only imports can be controlled | Simulate long-horizon save; measure draft quality, no generic top-ranked prospects, legal team personnel, rookie deals, free agency |
| 11 | Final freeze for permanent 2020 dynasty | **NOT READY** | Requires all essential game validations and history realism, not just green CI | Versioned stable players+teams+staff URLs; preserve old working exports and backups |

## Latest QA update: 2026-11-20
- User said the **2028/2029 V15 boards and visible cartoons look good**. Mark that narrow visual QA approved. Do not claim 960 unique portrait likenesses all inspected or full multi-season simulation passed.
- Staff V16 is separate and experimental, with all 128 lead coaching chair names from 2020 preseason public sources, 4 clearly labeled proxies where teams had no formal coordinator, and non-coaching roles retained as fictional placeholders. No player roster is changed.
- 2020 contract replacement remains open issue #8. Do not advance to final franchise freeze without sourced contracts and multi-season validation.

## Current acceptance checkpoint

**V16 Staff import now has the user's green CapForge checkmark.** Mark importer acceptance as passed; do not infer that every coach identity, modeled skill, or season-long behavior has been inspected. No additional scout, team-doctor, or free-agent staff customization is requested; leave the structural placeholders required by CapForge.

The **next engineering focus is authentic 2020 player contracts**. V18 independently tests whether the OTC historical Parquet file exposes annual 2020 cap, base salary and bonuses. No source data gets written to the approved V15 Players import until reconciled with 2020 rules and CapForge constraints. A separate disposable game still needs multi-year class and free-agency simulation; do not ask for repeat board/Arch approval.

## Rules that remain locked
1. Never overwrite or delete the working V6–V12 exports or user's saves.
2. Preserve all 2020–2027 V12 records **byte-equivalent at record level** when testing V15.
3. Each imported year 2021–2029 has exactly 480 *real sourced identities*, with no guaranteed NFL destinations, draft selections, or career trajectories.
4. 2028/29 mock rankings and 2026 freshman-to-2029 cohort assignments are projections; explicitly label uncertainty.
5. Do not infer appearance from football position or assign unknown cartoon portrait IDs. A valid portrait ID is not visual confirmation.
6. Keep hidden development/potential and progression curves out of user-facing reports.
7. GitHub CI passing means structurally valid JSON, **not** that the game imported or simulated it without warnings.
8. Do not modify **Project Ice**.

## Latest verified build — V15
- PR #9 merged and main-branch publication CI passed; [V15 report](../preview/v15-2028-2029-scout-portrait-audit.json) is generated and spoiler-free.
- [Nine-class V15 Players](../preview/players-2020-nine-class-scout-audit-v15.json), [same V2 Teams](../preview/teams-2020-roofs-v2.json); **Staff Default**.
- Automated audit: 2028 featured 54; 2029 featured 46; added 16 + 33 new real prospects, two moved to 2028, four positional fixes and one school correction; 2029 remains a *2026 freshman projection*.
- **Portraits:** all 480 in 2028 and all 480 in 2029 use automatic game-generated cartoons. The game may display them, but accuracy is unverified until screenshot review. Do not claim all players' faces are accurate.
- 2028/2029 boards and later years surviving actual season simulation remain **unverified in game**.

## V17 contract-source evidence checkpoint
- Official 2020 NFL base cap **$198.2M**, not directly the simulator's estimated **$300M**; source: https://www.nfl.com/news/nfl-salary-cap-will-increase-to-198-2m-in-2020-0ap3000001106260.
- Historic OTC/nflverse source: https://github.com/nflverse/nflverse-data/releases/download/contracts/historical_contracts.csv.gz; dictionary: https://nflreadr.nflverse.com/articles/dictionary_contracts.html.
- New source-audit script `scripts/audit_v17_contract_source.py` checks 2020 name/contract-year/team candidate coverage and serialized annual-history availability. It must **not** rewrite V15 players or claim exact actual 2020 cap charges. Duplicate annual-history rows must be checked before any conversion.
- Separate historical salary import requires another version and in-game verification; V15 remains protected until then.

## V17 completed audit findings (main-branch CI passed)
- [Published V17 report](../preview/v17-contract-source-coverage-audit.json) contains **31,893** historic OTC contract rows.
- Of 2,293 2020 players: **1,721 unique plausible name + contract-term-overlap + team matches**, **473 ambiguous multiple candidate deals**, and **99 more** with no match, no 2020 term or team mismatch (32, 39 and 28 respectively). These are *plausible* not verified 2020 cap charges.
- All **31,893 CSV `season_history` values are empty**. The CSV is not suitable for reconstructing 2020 annual base salaries, bonus/proration, cap numbers or guarantees. Next use the Parquet asset's nested annual histories, and specifically audit duplicated years before any write.
- The assumed CapForge $300M / actual NFL 2020 $198.2M scale is about **1.513623×**, but actual implementation also requires legal payroll headroom and dead cap, not automatic blind scaling.
- No V15 player contracts or approved draft-class/portrait data were changed in V17. No import candidate is ready until this source limitation is solved.

## Current user scope decision — V16 Staff accepted (2026-11-20)
- User explicitly reports **Staff green checkmark** in CapForge. This proves the V16 Staff import was accepted by the game's validation UI; it does not independently prove all 128 coach/team assignments or coach abilities are correct.
- User explicitly says **skip scouts and doctors**. Do not attempt to research, rename, tune or replace the 96 modeled scout/doctor team positions, or the 448 free-agent staff entries; preserve them only to satisfy the current CapForge staff schema.
- Focus staff historical accuracy work only on 2020 HC/OC/DC/special teams if clear errors are reported. Treat staff importer milestone as complete, with optional future visual spot-check.
- New V18 contract source audit runs in its own workflow, not the roster importer build. It tests the richer nflverse historical Parquet `season_history` field and duplicate-year structure and publishes aggregates only. V15 Players and V16 Staff remain frozen.
