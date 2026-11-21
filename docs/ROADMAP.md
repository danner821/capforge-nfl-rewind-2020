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
| 7 | CapForge-style historical 2020 contracts (V19) | **CAPFORGE IMPORT GREEN; SEASON SIM PENDING** | User screenshot confirms V19 Players (2,293), Teams V2 (32), Staff V16 (672) all green; 1,570 annual source contracts + 723 game-scale approximations | Verify actual cap room, 2021 free agency, contract rollover; do not repeat import request |
| 8 | Accurate 2020 coach cartoons / V23 avatar catalog | **V22 IMPORT GREEN BUT LIKENESS FAILS; V23 VISUAL CATALOG IN CI** | User reports V22 Staff now green but many coaches still look wrong. We verified 73 accepted staff-only avatar IDs, but have no artwork-to-ID index; prior age-based selections didn't fix appearances | Run disposable V23 gallery once and capture labeled cartoon faces from Staff free-agent Head Coach market or edit portrait picker; then match actual 2020 coaches and release separate reviewed staff version |
| 9 | Accurate 2020 Week 1 depth, injuries and transactions | **NOT STARTED** | Madden 21-derived snapshot is not guaranteed exact Week 1 | Audit 32 rosters against contemporary 2020 team records, preserve cap legality |
| 10 | Season history, free agency, scouting, draft and contracts regression | **NOT STARTED** | CapForge franchise is not our codebase; only imports can be controlled | Simulate long-horizon save; measure draft quality, no generic top-ranked prospects, legal team personnel, rookie deals, free agency |
| 11 | Final freeze for permanent 2020 dynasty | **NOT READY** | Requires all essential game validations and history realism, not just green CI | Versioned stable players+teams+staff URLs; preserve old working exports and backups |

## Latest QA update: 2026-11-20
- User said the **2028/2029 V15 boards and visible cartoons look good**. Mark that narrow visual QA approved. Do not claim 960 unique portrait likenesses all inspected or full multi-season simulation passed.
- Staff V16 is separate and experimental, with all 128 lead coaching chair names from 2020 preseason public sources, 4 clearly labeled proxies where teams had no formal coordinator, and non-coaching roles retained as fictional placeholders. No player roster is changed.
- 2020 contract replacement remains open issue #8. Do not advance to final franchise freeze without sourced contracts and multi-season validation.

## Latest V19 publication — automated verification complete

- Main-branch GitHub Actions build **passed and published** [Nine-Class V19 Players](../preview/players-2020-nine-class-contracts-v19.json) and [V19 spoiler-free contract audit](../preview/v19-simplified-contracts-audit.json).
- 1,570/2,293 starting contracts use a plausible historical 2020 annual OTC source match (1,246 annual-and-team, 242 disambiguated, 82 team-level), 723 rely on explicitly labeled game-modeled fallback. The source-based numbers are **CapForge-scaled**, not exact 2020 NFL dollars.
- Remaining-years profile is 943 one-year, 521 two-year, 447 three-year, 358 four-year, 24 five-year. Prior V15 placeholder had 1,983 one-year deals.
- Simulated 2020 salary+bonus charges across all clubs range **$186.855M–$279.159M** under the modeled $300M cap, rather than artificially matching at $285M. Future existing-roster contract obligations through 2024 were validated under the cap before rookies/free-agent additions.
- Every non-contract 2020 player field, all 4,320 original 2021–2029 prospects, their portraits, ratings and hidden development are identical to approved V15. Teams V2 and V16 Staff untouched. Both V19 and historical regression builds passed in CI.
- **Not yet approved in CapForge app**: V19 Players needs a separate disposable new-save validation, plus 2021 free agency and later-year progression. Never overwrite the user's verified V15 save.
- Recommended trial: **Players V19** + **Teams V2** + **Staff V16**. Use Reg Season 2020. Existing Staff V16 is already green in-game; do not spend any work on scouts or doctors.

## V20 publication verification

- [Optional V20 staff import](../preview/staff-2020-coaches-age-qa-v20.json) and [portrait-age QA report](../preview/v20-staff-portrait-qa-report.json) have been generated and published from successful main-branch GitHub Actions. The independent V20 CI and historical roster CI passed.
- All **32 historical 2020 head-coach ages** now match public DOBs as of September 10, 2020; **31 age fields actually changed**, one already matched by coincidence.
- **Zero custom coach portrait IDs were assigned** because CapForge's portrait picker/catalog images cannot be established from JSON alone. No claim that coach face inaccuracies are fixed; they remain unresolved awaiting evidence. Current importer-approved **V16** remains default for existing saves and is safer than swapping solely for appearance.
- V20 retains the original 672 staff identities, team assignments, staff skills, coordinators, 96 fictional scout/doctor positions and 448 free-agent staff entries. It changes only those 31 head-coach age fields. The V19 Players and V2 Teams files are unchanged and green in the user's app.
- The user should supply screenshots of *specific inaccurate coach cards* and ideally the *in-game portrait selection screen* with any displayed IDs. Then assign only screenshot-approved portraits in a separate version; do not guess by name/age/demographics.

## V20 coach age / portrait fidelity — latest task

- User reports **V19 Players, V2 Teams, V16 Staff all green in CapForge**, and visible coaching portraits are sometimes inaccurate. This is import-level acceptance for all three, *not* evidence the faces resemble the coaches or that the 2020–2029 season simulation passed.
- V16 originally reset all 128 coach avatar IDs to CapForge defaults and reused the fictional 2018 template's bio.age values. Its portraits are therefore uncurated and a number of ages are historically wrong. Avoid claiming a game-rendered portrait is accurate without a visual source.
- V20 builds a **separate** staff-only import `preview/staff-2020-coaches-age-qa-v20.json` from V16, changing verified HC ages as of 2020-09-10 on 32 teams. Source birthdates: `data/coaches_2020_head_coach_birthdates.json` with an explicit public source URL. UUIDs, team slots, coaching skills, contracts, remaining 96 team scouts/doctors and 448 free agents are unchanged.
- `data/coaches_2020_portrait_overrides.json` is initially **empty by design**: all 128 coaching avatars require an app screenshot/validated `portrait-####` crosswalk before assigning an explicit override. Do not improvise IDs by guessed traits or random portrait IDs; that would repeat prior portrait mistakes.
- Run separate V20 CI build and validation, then test V20 only in a new disposable CapForge save. V16 stays the user-validated fallback. Coach-specific cartoon portrait matching remains **blocked on actual in-game portrait picker evidence**, not just CI.
- The next franchise milestone after coach QA is 2021 free agency/contracts and 2020–2029 multi-season progression. User explicitly excluded scout/doctor research.

## Verified V21 pilot publication — 2026-11-20

- PR #20 merged, both the V21 and historical preview pull-request builds passed, and the main-branch V21 publish completed successfully.
- [Staff-only V21 trial import](../preview/staff-2020-coach-portrait-proxies-v21.json) is published alongside [V21 report](../preview/v21-coach-portrait-proxy-report.json). Both are separate from V16 and V20; no user saves or approved player files changed.
- Seven **tentative** 2020 head-coach cartoon IDs copied from real V19 2020 player records: GB LaFleur / Jimmy Garoppolo (portrait-0798), LAR McVay / Baker Mayfield, ARI Kingsbury / Derek Carr, SF Shanahan / Kirk Cousins, CLE Stefanski / Ryan Tannehill, CIN Taylor / Jared Goff, NYG Judge / Joe Burrow. These are human-proposed approximations, not verified actual cartoon-face matches.
- The V21 import has not been checked in CapForge; the coach role may reject player portrait IDs or render unexpectedly. Do **not** assert likeness is fixed until green Staff and visible coach cards in a disposable game. V16 remains the prior green fallback.
- All V20 staff names, ages, UUIDs, teams, roles, skills and contracts preserved; 96 scout/doctor chairs + 448 fictional free-agent staff untouched, plus all player/teams/draft files unchanged.
- Next check: in a **new disposable** September 2020 game, V19 Players + V2 Teams + V21 Staff, validate 672 and inspect LaFleur's coach card first, then the other six. If approved, proceed with larger coach portrait curation (remaining 121). If not, revert to V16 and reconcile exact source/position ID semantics before expanding.

## Latest user evidence and V23 visual atlas plan

- Latest user feedback: **"Green check mark but many coaches are still off"** after importing V22. Mark **V22 Staff import accepted in CapForge**, but **portrait likeness QA failed**. Do not ask the user to recheck import or claim the seven age-selected faces are correct.
- No trustworthy public visual atlas of CapForge's staff-specific cartoon images was found. The accepted V16 staff file contains **73 unique known-supported staff-only portrait IDs**, but their ID numbers provide no reliable information about faces, hairstyles or skin tones. Do not repeat arbitrary age-based mappings.
- V23 is a **diagnostic-only gallery**, never to be used in a real franchise: starts from the accepted V22 Staff, preserves all 224 employed/2020 historical staff entries exactly, and relabels 73 fictional free agents as `Avatar PicXXXX`, one per supported portrait ID. Diagnostic entries have freeAgent Head Coach role and high grades for discoverability in the Staff market. All remaining 375 free agents unchanged. No customization of actual scouts/doctors, and no players/teams/saves changed.
- File to generate: `preview/staff-portrait-reference-gallery-v23-TEST-ONLY.json`, plus `preview/v23-staff-portrait-gallery-map.json`. User can import into a **NEW disposable 2020 game** alongside the same V19 Players and V2 Teams; open Staff > Market/Free Agents, filter Head Coach, find `Avatar PicXXXX` labels, and send a scrolling screen recording or several screenshots of portraits. If the native Staff portrait picker shows a complete gallery with ID numbers, that screenshot/recording is preferable and V23 is unnecessary.
- Once the actual visual mapping is known, assign matched staff-only IDs to real 2020 HC/OC/DC/ST names, preserving V20 ages, and test one final production staff-only import. No more speculative V24 before seeing the faces.
- Remaining separate franchise QA: 2021 free agency/contract rollover and nine-year season progression. User explicitly excluded actual scout/doctor curation.

## V22 verified publishing checkpoint

- [V22 Staff import](../preview/staff-2020-valid-coach-portraits-v22.json) and [V22 audit report](../preview/v22-valid-staff-portrait-audit.json) were successfully published after both PR and main-branch CI passed. PR #22 merged.
- Seven replacements are from V16 Staff's 73 distinct explicitly imported-and-green cartoon IDs, rather than the rejected V21 player-only IDs. Matt LaFleur now has tentative staff ID `portrait-0675`.
- This is **staff portrait schema compatibility evidence, not actual resemblance verification**. The remaining 121 coach faces still use CapForge defaults. No promise about LaFleur's face/skin tone without in-game visual inspection. All other staff data, V19 Players and V2 Teams unchanged.
- The next useful user test is a **new temporary game** with V19/V2/V22: inspect Staff warnings and LaFleur face. If still wrong, refine staff-only ID selection, not player portraits. Preserve user-approved V16 for existing game and do not revisit scouts/doctors.

## New blocker and fix after actual user V21 screenshot

- The user's screenshot shows **all seven V21 staff portrait IDs rejected**: `portrait-0753`, `portrait-0007`, `portrait-0520`, `portrait-0798`, `portrait-0826`, `portrait-0523`, `portrait-0765`. CapForge explicitly warned each "is not a staff portrait; a portrait is picked from the iden instead." It still recognized 672 staff. This proves the **player-only ID scheme does not transfer to Staff**, despite prior player validation.
- The original 2018 CapForge community staff example has **74 unique staff IDs**, **73 of which already appear in the user's green-check V16 staff import** (the remaining single ID `portrait-0482` excluded from the supported set). Those accepted IDs are the safe *compatibility* source.
- V22 build derives from V20 corrected-age Staff (not failed V21). Seven head-coach roles use **distinct, known green-V16 staff portrait IDs**, selected by same role and approximate age from community staff template. All other 665 staff records unchanged, including scouts, doctors and free-agent staff. Every proposed ID must be in the accepted V16 pool; a new CI regression expressly rejects V21's seven player-only IDs.
- **Do not claim actual likeness or corrected skin tone:** the game's visual atlas is unavailable. Matching by template age and role is provisional. Start a disposable game using **V19 Players, Teams V2 and V22 Staff**; verify no Staff warnings and check Matt LaFleur's actual cartoon before expanding. If it still doesn't resemble LaFleur, revise only the tested staff portrait mapping. Keep original V16 as proven green fallback.
- After staff avatar compatibility, continue scheduled 2021 free-agency and long-season progression tests. Do not spend work on scouts/doctors or repeat approved draft boards. Don't modify Project Ice or user saves.

## V21 coach portrait experiment — latest user direction

- User explicitly wants **closest possible CapForge avatars for real 2020 coaches, exactly like player cartoon matching**. Example: Matt LaFleur's default face is wrong. Do not accept generated defaults as evidence of likeness.
- Game source has separate coach/player avatar pools. V21 **pilot** tests copying seven specific, already accepted V19 player cartoon portrait IDs to their visually analogous 2020 head coaches (including Matt LaFleur from Jimmy Garoppolo). The analog judgments are provisional, not proof of resemblance to actual cartoon artwork; actual coach import/photo check is required. More coaches can be added once compatibility and visuals pass.
- New versioned test `preview/staff-2020-coach-portrait-proxies-v21.json` retains all V20 ages, all 672 staff identities, teams, skills, contracts and other staff exactly; V16 remains the current game-validated fallback, while V19 Players and V2 Teams remain unchanged.
- Never imply all 128 coach faces are curated; the initial pilot covers **seven**. Never auto-classify race or guess unknown portrait IDs. Use known V19 player portrait references only and verify staff acceptance separately.
- After this, remaining major milestone is multi-year free agency, contracts and 2020–2029 draft class progression. Scouts/doctors remain out of scope.

## Current acceptance checkpoint

**V16 Staff import now has the user's green CapForge checkmark.** Mark importer acceptance as passed; do not infer that every coach identity, modeled skill, or season-long behavior has been inspected. No additional scout, team-doctor, or free-agent staff customization is requested; leave the structural placeholders required by CapForge.

The **next user acceptance gate is the published V19 contract import** in a new disposable 2020 CapForge game (same Teams V2 and green V16 Staff). Validate players warnings, team cap headroom and 2021 free agency, then long-term draft class persistence. V15 remains the preserved working fallback. Do not require repeated board/Arch approval or scout/doctor changes.

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

## V18 completed Parquet source audit — 2026-11-20
- [V18 source report](../preview/v18-parquet-contract-history-audit.json), published from successful GitHub Actions, **does not modify the V15 player file or any contract**.
- Parquet has 53,885 historical contract rows; **53,841** have a nonempty annual `season_history`, unlike the prior CSV. Available fields include `base_salary`, `cap_number`, `prorated_bonus`, `roster_bonus`, `cash_paid`, and `guaranteed_salary`. **22,348** individual nested 2020 annual records were found across all historical contracts, not all current NFL players.
- Of the 2,293 modeled starting roster players: 1,710 had exactly one plausible name/2020-term/team contract candidate; only **1,574** of those also had a single explicit 2020 annual record; **136** did not. **469** had multiple potential contract records; 38 had team mismatches; 39 lacked matching 2020 term and 37 had no source-name match. This is an **initial matching heuristic**, not confirmed historical 2020 cap numbers.
- 5,587 source contract rows have nonempty annual history without a parseable year. No repeated year *within a single parsed contract* was observed; across-contract conflicts and multiple player ID candidates remain to be addressed.
- Next acceptance gates: 2020 active deal by club/contract, source-specific annual pay breakdown and proration, duplicate/conflicting assignments, CapForge salary schedule constraints, scaling from NFL $198.2M base cap to modeled 300M cap, club headroom and real dead money. Do not alter V15 until a new separately versioned candidate is independently checked.

## Current user decision: simpler CapForge-friendly contracts (2026-11-20)
- User requested **mold historical 2020 contracts to how simple CapForge is**, rather than imitating full NFL legal clauses. This supersedes any demand to reconstruct every cap clause before producing a trial import.
- V19 experimental builder `scripts/build_v19_simple_contracts.py` consumes the audited 2020 OTC Parquet source while retaining *all V15 ratings, teams, names, portraits, potentials and 2021–2029 classes*. Only **2020 roster contracts** may change.
- Source-aligned deals use actual 2020 cap number (separating known prorated bonus once), approximate guaranteed salary and **remaining** contract years (1–5). Prior modeled salaries and plausible rookie years explicitly fill ambiguous/absent 2020 records; not every value is historically exact.
- Normalize contract `signedSeason=2020`, `currentYearIndex=0` to a new-game 2020 start; importer years represent remaining years, *not the real signing date*. CapForge `salaryByYear`, `bonusByYear`, `guaranteeByYear` are modeled straightforwardly.
- Apply one common league scaling factor (based on 2020 NFL $198.2M vs CapForge ~$300M) adjusted to ensure **every club's starting salary+bonus <=$280M**, rather than giving each team the previous identical ~$285M artificial total. The salary model must demonstrate meaningful variation in team spending, preserve minimum year salaries and avoid duplicate bonus counting. This is **game balance**, not the true historical NFL cap.
- CI separately verifies unchanged V15 noncontract data, 480 prospects every year, shape, 32 cap totals, salary/guarantee validity, and privacy-safe aggregate reports. Publish separately as `preview/players-2020-nine-class-contracts-v19.json` only after a green build; V15 stays the verified fallback until the user imports V19 in a **disposable** new save and checks free agency.
- Source-matching and future annual values are approximate; some source histories include future restructures. Historical 2020 dead money remains unimplemented. V16 staff is green and **scouts/doctors are out of scope**; no further customization is needed.
