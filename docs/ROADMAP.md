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
| 7 | Authentic 2020 contracts and team salary caps (V14) | **IN DEVELOPMENT (research/audit done)** | V13 confirmed 2,293 placeholder contracts, all with flat salaries and zero bonuses; 32 nearly equal modeled payrolls around $285M | Match season-specific historical cap/contract data, model year-by-year schedules; new versioned export + game free-agency tests |
| 8 | Authentic 2020 coaches and staff | **IN DEVELOPMENT (V16 source-backed core)** | Source-backed 2020 HC/OC/DC/ST for all 32 clubs with 4 labeled functional coordinator proxies; other scout/doctor/free-agent identities and all skills modeled | Pass V16 staff build and validator; import optional staff into a disposable 2020 game, test team assignments and warnings |
| 9 | Accurate 2020 Week 1 depth, injuries and transactions | **NOT STARTED** | Madden 21-derived snapshot is not guaranteed exact Week 1 | Audit 32 rosters against contemporary 2020 team records, preserve cap legality |
| 10 | Season history, free agency, scouting, draft and contracts regression | **NOT STARTED** | CapForge franchise is not our codebase; only imports can be controlled | Simulate long-horizon save; measure draft quality, no generic top-ranked prospects, legal team personnel, rookie deals, free agency |
| 11 | Final freeze for permanent 2020 dynasty | **NOT READY** | Requires all essential game validations and history realism, not just green CI | Versioned stable players+teams+staff URLs; preserve old working exports and backups |

## Latest QA update: 2026-11-20
- User said the **2028/2029 V15 boards and visible cartoons look good**. Mark that narrow visual QA approved. Do not claim 960 unique portrait likenesses all inspected or full multi-season simulation passed.
- Staff V16 is separate and experimental, with all 128 lead coaching chair names from 2020 preseason public sources, 4 clearly labeled proxies where teams had no formal coordinator, and non-coaching roles retained as fictional placeholders. No player roster is changed.
- 2020 contract replacement remains open issue #8. Do not advance to final franchise freeze without sourced contracts and multi-season validation.

## Current user action
The 2028/29 V15 visual checkpoint is approved. Next, test the optional **V16 staff file** once CI publishes it alongside the protected V15 nine-class player file `preview/players-2020-nine-class-scout-audit-v15.json` in a disposable 2020 CapForge save with **Teams V2** and **Staff Default**. V15 includes all 2020–2027 V12 records unchanged, including user-approved 2027 prospects and Arch's portrait. Check the warning panel and 2028/2029 boards. The user already approved the 2027 board and Arch Manning's portrait; do **not** ask them to reapprove it.

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
