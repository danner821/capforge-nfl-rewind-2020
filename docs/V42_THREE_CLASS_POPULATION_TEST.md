# V42 read-only population ablation: 2020 with three imported future classes

**Status: TEST ONLY — game behavior not verified.** This diagnostic isolates the user's 2026-11-22 hypothesis that loading 9 future draft classes can trigger a league-wide potential cap, talent redistribution, or player-development normalization issue.

Source 9-class file: `preview/players-2020-nine-class-no-personality-v39-TEST.json` at frozen Git blob `b69f4643932460e0369765e0d7d49f9e361420e4`. Latest failed V39 was confirmed in Arcade. The 2020 baseline source has 2,293 NFL players and 480 prospects for every year 2021–2029.

New 3-class diagnostic: `preview/players-2020-three-class-count-diagnostic-v42-TEST.json` at frozen Git blob `7f64c7ca3efd3558fe9a62016ce4bf28fb162927`. Built by **only omitting draft-class prospects for 2024–2029**. Retained 2,293 unchanged 2020 NFL players and all 1,440 unchanged 2021, 2022 and 2023 draft prospects. 3,733 total. All retained records (including potential, attributes, contracts, portraits, personality presence, college, and metadata) were verified exact JSON equals the V39 source; zero modified retained records. 2020 `meta.baseSeason` unchanged. The original V39 nine-class input, historical imports, team/staff, saved games and Project Ice were not changed.

## Disposable in-game A/B

**Nine-class control (V39):**
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-no-personality-v39-TEST.json

**Three-class diagnostic (V42 branch, pinned commit):**
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/7e2a2c7f29c51768e787205fc9c724f7a5b73a9c/preview/players-2020-three-class-count-diagnostic-v42-TEST.json

**Both use exactly same Teams V2 and Staff V25:**
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/staff-2020-head-coach-video-matched-v25.json

1. Create **two new disposable Arcade 2020 Regular Season saves** using the control versus diagnostic Players URLs, Teams V2 / Staff V25, and otherwise identical game settings (especially Talent Market); do not mutate a permanent save.
2. Verify all imports green, Bills NEW GAME preview Josh Allen QB development-tier badge. Start career, do NOT click Save Changes in player editor. If opening editor to read FUTURE GROWTH, exit Cancel/Back.
3. Compare Josh Allen's starting badge, actual OVR and editor future-growth projection immediately after league creation and again after **three simulated games** in both saves. In each save check two 2021–2023 prospects by ID/name to see whether their unchanged imported future potential was preserved or regenerated.
4. Outcomes:
    * 3-class **still fails** ⇒ future-class count alone is NOT a sufficient explanation; app-level importer-to-franchise normalization or other setting remains leading hypothesis. Do not rebuild or restart at 2023.
    * 3-class **passes** while 9-class **fails** ⇒ number of imported prospects or associated distribution/scouting code likely matters. Next controlled test would be 6 classes (2021–2026), followed by 9 classes with varied cohort/density only if evidence warrants, to discriminate class count, player count, and high-potential density.
    * BOTH **pass** ⇒ uncontrolled settings/seed/version or inconsistent symptom; repeat at identical settings before permanent launch.
    * BOTH **fail** ⇒ the original Josh Allen player hydration/editor-save bug is independent of imported class count.
5. Even a 3-class pass does not prove 2027–2029 can be injected mid-save. Do not promise incremental class imports absent an explicit supported CapForge import feature. A 2023 starting season would require genuine historical 2023 player/team/age/contract/staff rebaselining, not changing meta.baseSeason.

**No evidence yet of a documented fixed league-wide potential quota.** Official v1.8.3 app release notes describe TIGHT/BARE young-QB development and initial roster trimming over 53 active players, not global potential caps. V39 is a failed growth test, and the 2020 three-game export demonstrates large reductions while retaining all nine draft cohorts. See `docs/CAPFORGE_IMPORT_POTENTIAL_ENGINE_TRIAGE.md` and issue #41.

**Release gate:** no new player import may be recommended for a permanent franchise until the in-app development issue is corrected and a multi-year no-editor-save regression is successful.
