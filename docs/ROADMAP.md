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
| 4 | 2028–2029 top prospect coverage | **IN DEVELOPMENT (V15)** | V12 covered 30 2028 early mocks and 3 2029 QBs; V15 checks broader 2028 big board/devy and 2026 freshman recruits for prospective 2029 | CI pass; user verify 2028 and 2029 boards after disposable import |
| 5 | 2028–2029 cartoon portraits | **BLOCKED ON GAME VISUAL TEST** | V15 audits explicit cartoon IDs vs game default; known IDs are retained, but JSON cannot prove appearance or likeness | Examine in-game top 2028/29 QB/WR/EDGE portraits; curate only position-compatible, game-known options using actual visual evidence |
| 6 | Nine-class long-horizon persistence | **BLOCKED ON GAME TEST** | Future year tabs and early board display ≠ surviving season progression | Advance multiple years in disposable save; inspect drafts/players from 2022 to 2029, persistence and any crashes |
| 7 | Authentic 2020 contracts and team salary caps (V14) | **IN DEVELOPMENT (research/audit done)** | V13 confirmed 2,293 placeholder contracts, all with flat salaries and zero bonuses; 32 nearly equal modeled payrolls around $285M | Match season-specific historical cap/contract data, model year-by-year schedules; new versioned export + game free-agency tests |
| 8 | Authentic 2020 coaches and staff | **IN DEVELOPMENT (schema reference located)** | Real 2020 HC/OC/DC/ST verification not done; a community 2018 staff shape exists but its contents are mostly fictional | Build separate sourced 2020 staff, verify all team IDs and 7 roles, clean disposable import |
| 9 | Accurate 2020 Week 1 depth, injuries and transactions | **NOT STARTED** | Madden 21-derived snapshot is not guaranteed exact Week 1 | Audit 32 rosters against contemporary 2020 team records, preserve cap legality |
| 10 | Season history, free agency, scouting, draft and contracts regression | **NOT STARTED** | CapForge franchise is not our codebase; only imports can be controlled | Simulate long-horizon save; measure draft quality, no generic top-ranked prospects, legal team personnel, rookie deals, free agency |
| 11 | Final freeze for permanent 2020 dynasty | **NOT READY** | Requires all essential game validations and history realism, not just green CI | Versioned stable players+teams+staff URLs; preserve old working exports and backups |

## Current user action
Test the newest *verified CI build* (currently V12, with V15 to be published once CI passes) in a disposable 2020 CapForge save with **Teams V2** and **Staff Default**. Check the warning panel and 2028/2029 boards. The user already approved the 2027 board and Arch Manning's portrait; do **not** ask them to reapprove it.

## Rules that remain locked
1. Never overwrite or delete the working V6–V12 exports or user's saves.
2. Preserve all 2020–2027 V12 records **byte-equivalent at record level** when testing V15.
3. Each imported year 2021–2029 has exactly 480 *real sourced identities*, with no guaranteed NFL destinations, draft selections, or career trajectories.
4. 2028/29 mock rankings and 2026 freshman-to-2029 cohort assignments are projections; explicitly label uncertainty.
5. Do not infer appearance from football position or assign unknown cartoon portrait IDs. A valid portrait ID is not visual confirmation.
6. Keep hidden development/potential and progression curves out of user-facing reports.
7. GitHub CI passing means structurally valid JSON, **not** that the game imported or simulated it without warnings.
8. Do not modify **Project Ice**.
