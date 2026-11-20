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

## 2026-11-19: Green in-game importer validation
- User provided screenshot of CapForge **New Game → Import** with both inputs green:
  - PLAYERS: `preview/players-2020-four-class-position-v3.json`, checkmark and **2293** rostered players.
  - TEAMS: `preview/teams-2020-roofs-v2.json`, checkmark and **32** teams.
  - STAFF: DEFAULT.
  - No warning or error panel visible, choose-your-path green and enabled.
- This confirms CapForge validation acceptance of these specific imports. It does **NOT** prove that the 2024 fourth class will appear after progression, nor that 2021–2026 classes are historically complete.
- Next test: User taps Choose Your Path, selects a disposable test franchise in Dynasty if available, confirms start season 2020 regular season, checks that 2021 is populated, and advances a throwaway save sufficiently to verify 2024 class appears (without inspecting hidden potentials).
- If user chooses to share screen captures, never ask to reveal individual player potential. Historical contracts and staff still provisional.
- Do not modify Project Ice, and do not advertise these previews as final.

## 2026-11-19: V4 corrects failed league construction (after clean V3 import)
- User's Choose Your Path screenshot: `Could not build the league: Bad state: new-league construction could not satisfy both hard invariants — over cap: {}, stuck (dead cap blocks relief): {}, short of required personnel: [all 32 teams]`. Mode shown: Arcade, no save constructed.
- Root cause grounded in 2020 Madden and 2035 real game export: original converter mapped **all Madden LE/RE to EDGE**, leaving **zero DE players on all 32 teams**. CapForge has separate 15 positions including DE and EDGE.
- Fixed builder: Madden LE/RE maps to DE; pass rushing LOLB/ROLB eligible for EDGE; team-wide balancing selectively reclassifies extra DEs to EDGE and heavy DE to DT where needed; OG to C if team has only one center. Each move recalibrates OVR to new position, preserving underlying target as closely as possible.
- CI run `44680479166` finished successfully. Spoiler-free report: 32 clubs, zero team with missing position, minimum 2 DE, 3 EDGE, 2 DT, no predicted OVR mismatch >2.
- V4 test Players: https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/players-2020-four-class-personnel-v4.json
- Teams remains https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/teams-2020-roofs-v2.json
- Strengthened `scripts/validate_capforge_roster.py` with 15-position presence + DE/EDGE/DT minimums.
- Still must validate actual game league construction and 2024 fourth-class persistence. Contracts provisional; hidden potentials remain private. Do not change Project Ice.

## 2026-11-19: V4 in-game league construction success + portrait V6
- User screenshot after previous V4 import shows **Kansas City Chiefs 2020 squad loaded and playable**, with Madden-based stars visible. V4 cleared the initial league-construction errors. User reports NFL players' generic cartoon faces don't resemble real people.
- Cause: V4 intentionally removed explicit portrait IDs to avoid invalid-position warnings; CapForge autogenerated generic faces instead.
- CapForge import supports built-in cartoon `portraitId` references, NOT verified real NFL image URLs. Other roster creator's 2018 (human matched to headshots) and 2026 (approximate) packs have per-player portrait IDs.
- Added `assign_reference_portraits` in `scripts/build_2020.py`: exact normalized name, exact current CapForge position, age adjusted by source year. Prefer 2018 reference for 2020 players, 2026 reference for later draftees; unmatched players preserve deterministic fallback. No ratings, contracts, potential, teams or developmental parameters changed.
- Network source downloader now retries 429/5xx. An initial V5 run accidentally matched 0 due overescaped regex; code corrected, and V6 workflow generated successfully.
- V6 initial report: 1,231 matches from 2018 reference, 1,277 from 2026 reference, 2,508 total; **1,431 of 2,293 2020 players** assigned, 862 initial roster unmatched; 741 future draft entries unmatched. Portrait matches are approximate, not verified true likeness.
- NEW user import test: `https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/players-2020-four-class-portraits-v6.json`
- Keep Teams link `https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/teams-2020-roofs-v2.json`, Staff default.
- Have user validate V6 and check any portrait incompatibility warnings. Starting a *new disposable save* required to test portraits in roster, not an existing save. Do NOT claim actual NFL headshots can be imported or exact likenesses obtained.
- Still need verify the fourth class truly survives after advancing to 2024; future draft completeness, contracts, and historical staffs remain unfinished. Project Ice unchanged.

## 2026-11-19: Approved V6 portraits and repaired 2025 Madden rookies
- User checked multiple NFL franchises and likes the approximate CapForge cartoon portraits from V6; wants every player matched as closely as available, NOT true photo headshots. Keep V6 as working checkpoint; do not disturb player's existing save.
- Historical-prospect QA discovered 2025 Madden 26 data contains 340 rookie entries, but 39 2025 LBs labeled "Mike Backer", "Weak Backer", and "Sam Backer", plus 3 "Long Snapper" rows, were skipped by position normalizer. Repaired mapping to LB/C. Six-class preview now contains 2025: 340 prospects (previously 298).
- New six-class link: https://github.com/danner821/capforge-nfl-rewind-2020/blob/main/preview/players-2020-six-class-draftfix-v7.json
- Tests: GitHub Actions build and JSON checks succeeded; 4,153 total entries in V7 (2,293 2020 roster + 1,860 draft prospects 2021-26); at this point only 4-class V6 portrait version is user confirmed playable.
- Added scripts/audit_draft_classes.py and CI step to compare historic draft picks against https://github.com/7LayerLabs/nfldraft/blob/main/nfl-drafts-2017-2026.csv with known historical name aliases, no potentials revealed.
- Current audit: **all rounds 1-3 actual drafted players in 2021-26 covered**. Other drafted players still missing: 2021 23, 2022 4, 2023 3, 2024 2, 2025 19, 2026 23; audit source name aliases may explain some.
- Individual prospects' 2020-26 hidden potential/curves remain only in raw import JSON; NEVER print them in user-facing drafts.
- Next tests: user can try V7 disposable 2020 save and confirm 6 classes persist. Need real 2020 contracts and staff, exact Week 1 roster, late-round and undrafted draft completeness; avoid changes to Project Ice.

## 2026-11-19: V8 historical draft reconciliation, safe test checkpoint
- Prior timed-out development completed a new evidence-based V8 backfill: **27** sourced historical drafted prospects were added (20 in 2021, 1 in 2024, 6 in 2025), based on later Madden records or matched 2026 fan-player entries. Missing picks without reliable individual attributes were not invented.
- New output files are `preview/players-2020-four-class-history-v8.json` (3,532 records) and `preview/players-2020-six-class-history-v8.json` (4,180 records). Both preserve the 2,293-player 2020 starting roster; earlier V6 and V7 exports remain intact, frozen by build code.
- Source report `preview/build-report.json` lists V8 draft class sizes: 2021 286, 2022 318, 2023 346, 2024 289, 2025 346, 2026 302. Six-class years beyond three still require direct CapForge progression testing.
- The original `preview/draft-coverage-report.json` continued to audit V7; this branch updates the auditor to target **V8**, enforces early-round coverage and the V8 drafted-name baseline, validates both V8 exports structurally, and tests pull requests without publishing artifacts on the PR branch.
- Remaining drafted picks absent from the source-backed backfill include hard-to-source late selections and long snappers unsupported as their own CapForge position. Do not fabricate ratings just to force full coverage.
- **Next in-game test:** Import `preview/players-2020-four-class-history-v8.json` with `preview/teams-2020-roofs-v2.json`, default Staff, and start only a disposable 2020 game. Check build success and portrait warnings. Then separately import `preview/players-2020-six-class-history-v8.json` in a disposable 2020 save to test 2025–2026 class survival. In-game status of V8 remains unverified.
- **Do not replace a working save.** V6 portraits and the older playable version remain available, no hidden potential or future team destinations should be exposed, and Project Ice stays untouched.

## 2026-11-19: V9 source-backed 480-player draft classes (experimental)
- User successfully imported V8 six-class 2020 roster; menu shows 2021–2026 prospect year filters, and 2021 Market Draft board has 480 prospects. User caught generated fictional prospects ranked near the top (e.g. Beckett Lewis, Christopher Walsh, Beau Pope, Drew Lagunas). V8 has just 286 named 2021 prospects; CapForge likely generates 194 filler. This is in-game evidence that source count and game board count differ.
- V9 solves this structurally via scripts/expand_v9_drafts.py and scripts/parse_nfl_undrafted.py. Pulls extra year-specific REAL names from array-carpenter 2007–2026 combine/pro day dataset, NFL.com's per-year 2021–2026 undrafted free agent lists, and historical NFL draft picks from 7LayerLabs; optionally consults ESPN prospect records. New player positions and physical measurements use sources where present, and all new rookie skill ratings/development are clearly **estimated** from lower-tier same-position templates; do not imply they're authentic Madden ratings.
- Import paths once GitHub Actions publishes:
  - preview/players-2020-four-class-authentic-v9.json (2020 roster + four 480-player classes; 4,213 records).
  - preview/players-2020-six-class-authentic-v9.json (2020 roster + six 480-player classes; 5,173 records).
  - preview/teams-2020-roofs-v2.json (unchanged).
- Validation: every V8 record preserved EXACTLY, including 2020 club assignments, approved portraits, contracts, ratings, and hidden development settings. Six classes of exactly 480, no duplicate IDs/names, no assigned future NFL teams, generated-player attributes are calibrated for CapForge, and NO fictional depth placeholders permitted.
- CI scripts/validate_v9_drafts.py and scripts/audit_v9_drafts.py test schema, original-data preservation, counts and NFL drafted-name coverage. Spoiler-free output: preview/v9-draft-pool-report.json and preview/v9-draft-coverage-report.json.
- V9 PDFs/images are not generated. No changes to Project Ice or any CapForge save. Old V6/V7/V8 output files must remain frozen. V9 output files themselves are immutable once first published.
- **Next independent user checkpoint:** A new disposable CapForge 2020 league using V9 six-class Players, V2 Teams and Default Staff, Sep Regular Season. Check that 2021 Market → Draft → Board no longer shows generated top-ranked names and that all future years appear through real season progression. Do not claim this has been achieved based only on CI. Preserve user's original long-term game save.

## 2026-11-20: V9 2021 board verified and V10 future-class expansion
- User supplied screenshot of playable **V9 2021 Market → Draft → Board**: believable top candidates Trevor Lawrence, Penei Sewell, Jaylen Waddle, Rashawn Slater, Zach Wilson, Christian Darrisaw, Jamie Newman, Justin Fields and Azeez Ojulari. The previously problematic fictional top-three names are gone. This confirms 2021 V9 board display, not 2022–2026 post-progression persistence.
- Existing V9 inputs contain 2,293 historical 2020 rostered players and 6 × 480 fully sourced 2021–2026 prospects. V9 historical rookie identity validation and 2021 in-game test are successful; the 2020 contracts, coach staff and seasons beyond 2021 require testing.
- User wants to expand into the future. New V10 branch projects three classes: 2027, 2028 and 2029, **480 real college-player identities per year** from sportsdataverse 2026 CollegeFootballData roster CSV, without pretending that their future NFL declarations/draft positions are known.
- V10 assigns 2026 college juniors/seniors as *candidate* 2027 NFL entrants, sophomores as candidate 2028 and freshmen as candidate 2029. They are provisional: early declarations, redshirting, eligibility differences, and college return decisions are unknown. The 2027 projected early-tier reflects public 2026 scouting boards without any hindsight; 2028/29 talents are less forecastable and their skill/development numbers are hypothetical.
- New exports, generated and validated in CI:
  - preview/players-2020-seven-class-projection-v10.json — 5,653 total (through 2027).
  - preview/players-2020-nine-class-projection-v10.json — 6,613 total (through 2029).
  - preview/v10-projection-report.json — aggregate report, no hidden player values.
- scripts/build_v10_future.py runs after immutable V9 assets; scripts/validate_v10_future.py checks identical preservation of **all 5,173 V9 original player records**, exactly 480 prospects in each 2021–2029 class, 1,440 new real college identities, no new fictional fillers, unique IDs/names, source college, supported CapForge positions, no future NFL team assignments, and estimated OVR consistency.
- **Test sequence**: 7-class V10 first, disposable 2020 league; verify import and 2027 tab. Then 9-class V10 in another disposable league; check 2028 and 2029 classes, and ideally progress throwaway save to future seasons to verify that imported classes aren't overridden. CI passing does not verify CapForge's app year limits. Current working V9 and Project Ice must never be modified.

## 2026-11-20: V10 real in-game nine-class validation + V11 2027 mock/portrait repair
- User tested **nine-class V10** in CapForge. Actual game New Game → Import shows 2,293 2020 rostered players, 32 teams, green Choose Your Path, and user reports future prospects appearing. Two specific warnings shown:
  - \`players[5179].ovr\`: Dylan Stewart, projected 2027, 79 imported, game says only 77 is attainable.
  - \`players[4772].weightOverrideLbs\`: Desmond Watson, 2024 draft prospect, 425 outside 140-400, automatically reset to 400. Duplicate warning shown under Teams due shared validation panel, NOT two different players.
- User also reported inaccurate generic portrait for 2027 quarterback Arch Manning and major 2027 names missing from nine-class projection, citing Charlie Becker, Drew Mestemaker, Darian Mensah, CJ Carr. GitHub direct data check confirmed Becker absent, Drew/CJ in 2028, Mensah already 2027. Additional missing high-profile players included Nick Marsh, Trey'Dez Green, Yhonzae Pierre, etc.
- V11 files created on branch \`feat/v11-future-prospects-portrait-ovr-fix\`:
  - \`preview/players-2020-nine-class-mockfix-v11.json\` 6,613 records, 2021–2029 exactly 480 prospects/year.
  - \`preview/players-2020-seven-class-mockfix-v11.json\` 5,653 records for a focused 2027 test.
  - \`preview/v11-draft-corrections-report.json\` spoiler-free, includes 32 watchlist names and provenance.
- 2027 32-name coverage comes from contemporary Nov 2026 first-round mock consensus: https://whynfl.com/2027-nfl-mock-draft-consensus-13-mocks-jeremiah-smith-drew-mestemaker-qb1-nine-arch-manning-november-2026/ ; corroborated on current PFF/Drafttek boards. 15 prospects were not in V10 at all and are sourced from 2026 real college roster data or manually verified contemporary mocks; 4 were incorrectly projected in later years and moved to 2027. All future year placements are still **projections, not declarations**. Newly modeled ratings are not authentic Madden ratings; don't guarantee historical NFL pick order or results.
- Replaced 2027 generic QB portraits for Arch Manning, CJ Carr and Drew Mestemaker with position-compatible *existing V9 built-in cartoon* portrait IDs from known 2020/2021 quarterback profiles; visual approximation only, not accurate headshots and not yet game checked.
- All 2020 teams, starting roster, and entire original 2021–2026 V9 records preserved EXACTLY except Desmond Watson 2024 weight value to 400. Dylan Stewart's requested OVR lowered to 77 and mapped to CapForge EDGE (no longer DE); corrected projected OT/S positions for other 2027 consensus names. 2028 departures replaced by real 2026 college-player identities to keep 480/year; no future NFL team assignments.
- GitHub PR #5 CI generated V11 and passed schema, 480-per-class, exact coverage, preserved V9 history, no new overweight players, no positional archetype incompatibility, no duplicate IDs, rating-estimator consistency. **In-app V11 import remains untested.**
- **Next request from user:** Use copy button for latest nine-class V11 player link with SAME \`preview/teams-2020-roofs-v2.json\` link; staff default. Start new disposable 2020 league, check warnings (should ideally be zero), 2027 draft board completeness and Arch Manning visual. Don't claim nine-class future season progression tested; source 2027 mock guesses won't perfectly match final real NFL outcome. Keep user's existing working save and Project Ice untouched. Future work also 2020 Week 1 contracts and historical staff audit.


## 2026-11-20: V12 expanded projected-cohort scouting after merged V11
- A separate timed-out workstream already merged V11 in PR #5: files `preview/players-2020-seven-class-mockfix-v11.json`, `preview/players-2020-nine-class-mockfix-v11.json`, `preview/v11-draft-corrections-report.json`. V11 corrects the two screenshot warnings (Desmond Watson 2024 425->400 pounds for CapForge max; Dylan Stewart 2027 79->reachable <=77 and EDGE position) and assigns existing valid QB cartoon portraits to Arch Manning, Drew Mestemaker and CJ Carr. V11 remains user-untested.
- User flagged more 2027–2029 names missing or misassigned. Independent current November 18, 2026 2027 consensus source: https://www.thedraftroom.app/2027-nfl-draft-big-board; thinner 2028 early projections: https://ultimatebigboard.com/nfl/2028/. Many underrepresented/misdated names despite V10 supporting nine years in edit-player tabs.
- V12 script `scripts/build_v12_future.py` uses frozen V11 nine-class input, independently crosschecks top 50 2027 scouting candidates, 30 early 2028 candidates and three tentative 2029 2026-freshman QBs, and matches actual 2026 college roster biographies where possible. 2027–29 declared entry years unknown; do not claim final picks or future pro potential. False same-name conflation avoided (2020 NFL OT Jonah Williams and distinct 2028 Texas defensive back).
- The V12 generator adds 31 sourced missing real-player names, moves two wrong-year candidates and refills from other documented real college players to maintain exactly 480 per draft year. Preview output paths: `preview/players-2020-seven-class-scoutfix-v12.json` and `preview/players-2020-nine-class-scoutfix-v12.json`; aggregate privacy-safe `preview/v12-scouting-coverage-audit.json`.
- PR #6 green GitHub Actions checks: source-backed consensus coverage, 480 prospects in each 2021–2029 class, 6,613 total players (nine-year), 5,653 (seven-year), all 5,173 V11 historical players through 2026 absolutely unchanged, no duplicated future prospect identity, original V11 three QB cartoon portraits retained, no loss of fixes to body weight or OVR. CI cannot establish that CapForge produces zero warnings or the classes persist when seasons progress.
- **Next user test**: copy V12 Nine-Class Players URL and original `preview/teams-2020-roofs-v2.json` (Staff default), import into NEW disposable 2020 game. Open expanded Players/Teams validation to confirm 0 warnings and 0 fixed values, view Arch Manning portrait, and search 2027 for Charlie Becker, Drew Mestemaker, Darian Mensah and CJ Carr. Verify 2028 and 2029 tabs. Later simulate a throwaway save to test long-horizon retention. Never modify previous working save or Project Ice.


## 2026-11-20: V13 contract/staff audit (audit-only next engineering checkpoint)
- V12 PR #6 was merged and its main-branch GitHub Actions generation completed successfully; published nine-class and seven-class V12 player JSON files and the V12 scouting coverage report exist. **No user-provided CapForge V12 import outcome yet.**
- Current V12 import links:
  - `https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-scoutfix-v12.json` (6,613 players; nine 480-player draft classes).
  - `https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json` (32 teams), Staff **Default**.
- Use a NEW temporary game, check warnings/fixed values, Arch Manning's game-rendered cartoon portrait, 2027 big board and 2028–2029 year filters. Future-year persistence still requires test sim. Protect all previous working imports and Project Ice.
- The next actual engineering task starts with a spoiler-free **V13 audit** (`scripts/audit_v13_contract_staff.py`), not an unsupported contract replacement. Existing `scripts/build_2020.py` converts Madden's total salary into a flat annual heuristic, sets 2020 as signed season, zeroes annual signing bonus and approximates guarantees at 25%: **these are not verified 2020 NFL terms**.
- The audit runs in CI over the published V12 player JSON and accepted Teams V2. It validates contracts' structural integrity, reports aggregate salary/guarantee/bonus patterns and per-team modeled totals, and documents the lack of a verified historical coaching-staff schema. It writes `preview/v13-2020-contract-staff-audit.json` on main after green CI.
- **No new player import is generated in V13**. V12 roster, hidden player development, all 2020–2029 prospects, portraits and previous versioned exports remain unchanged.
- Next before any historical salary or coaching staff rewrite: find credible historical 2020 contract/cap-hit data; identify a tested compatible staff JSON schema; independently audit real opening-week 2020 assignments. Make another versioned import file only after validation and avoid overwriting user's saves.
