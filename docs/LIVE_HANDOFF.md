# CapForge NFL Rewind 2020 — Verified engineering checkpoint

Updated 2026-11-19 (America/Phoenix). This is the current state, not a declaration of game import success.

## Product decisions (locked)
- New independent CapForge save starts in **2020 regular season**. Original 2035 Seahawks save and Project Ice are not modified.
- Historical Madden NFL 21 (2020 season) ratings as base; attributes translated to CapForge. Rookie baseline may receive modest, **cohort-wide** upward adjustment, never inflated only because a future breakout is known.
- Include real 2021–2026 prospects; test >3 future classes (4 and 6) before committing to 2027–2029.
- Hidden potential based on career information through 2026 is **not discussed with the player**. Never reveal, rank, print, or quote player potential or hindsight rankings in user-facing analysis. Do not link the raw JSON as an invitation to inspect it for ratings.
- Real-world teams and draft eligibility, but draft destinations depend on the save; do not preassign future prospects to their eventual NFL clubs.

## Verified GitHub state
- Repository: danner821/capforge-nfl-rewind-2020, separate from danner821/The-Project-Ice.
- Access: GitHub connector can read and write.
- Latest successful build observed: workflow run **44677832563** (success). Build output committed on main.
- GitHub Action builds previews from external public sources and runs spoiler-free structural checks.
- Preview assets committed under preview/:
  - players-2020-three-class.json (2021–2023)
  - players-2020-four-class-test.json (2021–2024)
  - players-2020-extended-experimental.json (2021–2026)
  - teams-2020.json
  - build-report.json

## Counts from actual build-report.json
- Roster: 2,293 players across 32 teams.
- Draft player counts: 2021 266, 2022 318, 2023 346, 2024 288, 2025 298, 2026 302.
- Export players: 3-class 3,223; 4-class 3,511; 6-class 4,111.
- CI success means JSON generation and schema checks passed; **NOT** confirmation that CapForge accepts import or loads future classes.

## Known data gaps before release
1. **In-game import**: Test 3-class candidate; verify 2020 starting season, team identities, 2021 draft. Test isolated 4-class candidate to assess hard limit; only afterward test 6-class.
2. **Contracts**: 2020 player contracts are temporary approximations from Madden total salary, NOT historical cap hits. Replace using 2020 historical sources and balance against game salary cap.
3. **Week 1 rosters**: Madden 21 release roster is not independently matched against exact 2020 NFL Week 1 transaction/inactive lists; 2,293 players is larger than game-day 53-man counts. Decide practice squad/free agent policy.
4. **2025 data**: 2025 dataset source is a secondary Madden 26 export, not guaranteed launch-day.
5. **2026 data**: External fan-made Madden 27 conversion; audit rookie identities and completeness.
6. **Real draft picks**: Draft pick numbers for future prospects not reconstructed.
7. **480 prospects**: Only named Madden-record rookies are included per year. Need real prospect expansion/filler logic if the game requires 480.
8. **Staff**: Historical 2020 coaching staff still unbuilt.
9. **Accuracy**: Calibrate position-specific Madden-to-CapForge OVR/attributes, fix player heights/positions/names, and verify contract arrays.
10. **Hidden potential**: Actual game UI may show scouting ranges; use Dynasty if appropriate, but cannot guarantee spoiler-free if user opens GitHub JSON.

## Minimum user test
1. Open CapForge > New Game > Import.
2. Use preview/players-2020-four-class-test.json as Players, preview/teams-2020.json as Teams, leave Staff blank for default.
3. Click Validate for each. Report exact error/success; if validation fails, screenshot it.
4. Start a *disposable* 2020 regular-season test save only if validation passes; confirm rookies and 2021 draft appear.
5. For a class-count test, advance disposable save and verify 2024 class appears (a successful validation alone does not establish future class support).
6. Do not begin long-term career yet or open player JSON to inspect hidden potential.

## Engineering next action
Use game validation feedback to fix importer incompatibilities first. If the 4-class test succeeds, test 6-class. Then audit 2020 contracts, Week 1 team assignments, historical staff, draft completeness and rating quality in that order. Keep changes confined to CapForge repository.