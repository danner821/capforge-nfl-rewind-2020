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
## 2026-11-19: Calibrated import v2 after user screenshot
- User tested `preview/players-2020-four-class-test.json`. CapForge showed 2,293 rostered players, 0 free agents and **4,324+ warnings**. Examples: generated random `portraitId` invalid for player's position; displayed OVR 99 disagreed with OVR recomputed from game attributes (example 99 -> 81).
- The green check and 2,293 count mean roster file parsing succeeded; **do not interpret as proof that the fourth class persists or future seasons work**.
- Root cause: CapForge per-position OVR weights are not equal to Madden's, and builder assigned arbitrary portrait IDs. We inferred approximate OVR coefficients across 15 positions from user's genuine 2035 CapForge export (no hidden player data included in coefficient file).
- Changed `scripts/build_2020.py`: remove explicit player portraitIds, map defender/offensive-lineman vision to recognition instead of ball-carrier vision, fill DB secondary rating keys, calibrate imported 2020 and 2021–26 stats to the projected CapForge formula; retain Madden OVR target when reachable.
- New helper `scripts/capforge_ovr.py` and `scripts/ovr_calibration_coefficients.json`. Coefficients are estimates, not official game source.
- Latest verified automated roster build succeeded (workflow run `44679273858`). Report confirms **0 explicit portrait IDs and 0 estimated OVR mismatches greater than two**; game must confirm warning count.
- NEW LINK for next user validation: `https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/players-2020-four-class-calibrated-v2.json`. Use `preview/teams-2020.json` for teams; previous screenshot showed teams field pointed at other creator's link, possibly 2026 identities.
- Next immediate action: user pastes new versioned link and checks warnings. Do not start permanent save yet; still outstanding historical contracts, staff, exact Week 1 rosters, and verification of 4+ imported draft classes.
- Project Ice untouched.

## 2026-11-19: V3 import correction after user screenshot
- Calibrated v2 reduced Players import warnings to TWO, at players[12] and players[22]. Source-order mapping points to Khalil Mack and Chandler Jones; both were incorrectly modeled as coverage LB instead of pass-rush EDGE.
- User Teams import rejected with three roof enum errors. Valid values are open, dome, retractable (not fixed).
- scripts/build_2020.py now maps Madden 3-4 pass-rush LOLB/ROLB to CapForge EDGE using skill profiles, and converts fixed-roof stadiums to dome.
- Latest GitHub Actions run 44679699544 completed successfully; 32 valid teams, 0 estimated OVR mismatches >2, no explicit portrait IDs.
- Next Players link: https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/players-2020-four-class-position-v3.json
- Next Teams link: https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/teams-2020-roofs-v2.json
- Next step: user validates both V3/V2 files in CapForge, confirms error and warning count. Successful CI is NOT proof of in-game compatibility. Only then start disposable test save to test 4th class.
- Never disclose hidden player potential, never touch Project Ice.
