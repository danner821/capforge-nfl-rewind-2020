# NFL Rebirth 2026 — fantasy dispersal draft (EXPERIMENTAL, NOT A VERIFIED RELEASE)

**Updated:** 2026-11-23  
**Status:** Static source construction done; in-game CapForge Draft Day behavior and progression remain **UNVERIFIED**. Do not overwrite original 2020 league saves, V34/V36/V39/V42/V43 rosters or Project Ice.

## Concept

All 32 NFL franchises are reinitialized with **46 fictional players each** (OVR 58–68, potential at most 71). No real NFL player begins on a team. In **2026 Draft Day**, the user and AI draft from a **480-person real-player class**, made from:

- 470 real 2026 NFL players selected from the independently published Madden 27 CapForge public roster, with position quotas and roughly 78% weight on original current OVR, 22% on original stated potential (or current OVR if none), and a small age-26-and-under modifier. Rating values themselves are **NOT** globally rescaled.
- 10 curated headlining 2027 prospects, accelerated one year earlier into 2026, from our archived V39 2027 prospect records. Their proposed potential/OVR values are subjective **alternate-history game balancing**, not scouting facts, and can be calibrated after actual gameplay.

After the draft there are **700 additional real 2026 NFL players** in the original free-agent pool to help clubs replace fictional depth. Unselected original public NFL players were intentionally *not* loaded; the game may generate more free agents on save initialization.

This is an **NFL dispersal draft using CapForge's normal NFL Draft Day**, not a true 40+ round snake fantasy draft. If the game uses 7 rounds and 32 teams (224 selections), **256 of the 480 prospects will not be drafted**, subject to the game's own behavior. Before using this as a permanent universe, we must verify what happens to undrafted real players, draft pick allocations/trades, FA signing and veteran rookie contract handling.

## Two import URLs

**PLAYERS** (do not use the existing 2020 historical Players file)

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/experiment/nfl-rebirth-2026-fantasy-draft/preview/players-2026-nfl-rebirth-480-fantasy-draft-TEST.json
```

**TEAMS** (pinned, unchanged copy of creator's public 2026 32-team file)

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/experiment/nfl-rebirth-2026-fantasy-draft/preview/teams-2026-nfl-rebirth-TEST.json
```

**STAFF:** leave blank/default for this pilot. It is not a source of real head coaches.

## First acceptance test — don't blindly Save Changes on 480 players

1. Create **NEW disposable game** -> IMPORT, paste Players & Teams URLs, leave Staff blank. Validate both.
2. **Season 2026; start date DRAFT DAY, not Regular Season; ARCADE mode; TALENT MARKET DEEP** for the initial control. For a tougher career use TIGHT later, after mechanics are verified.
3. Inspect 2026 draft board **before progressing**. Look for **480 prospects**, recognizable veterans (e.g. Josh Allen, Patrick Mahomes, Joe Burrow) and headliners (Jeremiah Smith, Arch Manning). CapForge might reject or suppress age-30+ draft entries; report exactly what appears.
4. Verify actual teams contain **fictional low-OVR players**, not preassigned 2026 NFL stars. Check draft pick counts and whether draft starts normally. Screenshot any unusual behavior.
5. Draft or simulate *just enough* to see at least one real NFL veteran and one accelerated 2027 prospect being selected. If the game skips the imported 2026 class, stops, auto-regenerates it, or fails to sign veteran draftees, **STOP and send the result**. Do not spend time saving editor cards.
6. Once draftees are on their new teams, check numerical **Future Growth** on one high-gap young draftee immediately. Use **Cancel/Back**, not Save. For a control test, start a second disposable save with identical settings and try a **single** no-change **Save Changes** on one draftee there. Do not edit/save the whole league.
7. Sim **three regular-season games**, then re-check the same player and export **Players JSON**. Note whether a no-op Save preserves potential, whether AI teams use fictional depth, and how undrafted players enter free agency.
8. If test succeeds, then calibrate distribution, remaining free agents, veteran rookie contracts, and future 2027–2029 classes (excluding the ten brought forward). Do not call this a finished fantasy-draft game yet.

### Expected imported values (before game normalization)

| Player | Type | OVR | Explicit potential |
| --- | --- | ---: | ---: |
| Josh Allen (QB) | 2026 draft | 99 | 99 |
| Patrick Mahomes (QB) | 2026 draft | 93 | 93 |
| Fernando Mendoza (QB) | 2026 draft | 73 | 90 |
| Ashton Jeanty (RB) | 2026 draft | 85 | 94 |
| Jeremiah Smith (WR) | accelerated 2027 | 81 | 97 |
| Arch Manning (QB) | accelerated 2027 | 77 | 96 |

The key controls are **Mendoza, Jeanty, Jeremiah Smith and Arch Manning**, since their imported potentials exceed their OVR. An unrelated display badge change is not proof; compare numeric potential in exported JSON, and observe the difference between new-game preview and playable save. Imported future potential is still subject to the unresolved engine issue documented in issue #41.

## Curated ten accelerated 2027 candidates

1. Jeremiah Smith — WR, Ohio State; 81/97
2. Arch Manning — QB, Texas; 77/96
3. Drew Mestemaker — QB, Oklahoma State; 76/89
4. Dante Moore — QB, Oregon; 76/91
5. CJ Carr — QB, Notre Dame; 75/90
6. Colin Simmons — EDGE, Texas; 79/96
7. Dylan Stewart — EDGE, South Carolina; 78/95
8. Leonard Moore — CB, Notre Dame; 79/94
9. Charlie Becker — WR, Indiana; 76/87
10. Jordan Seaton — OT, LSU; 78/92

These are **curated alternate-history headliners** rather than a definitive top-ten industry ranking. 2027 game data were sourced from the already frozen historical 2020 project, not scraped from a current mock. Current scouting discussions can inform later revisions; no source ranking directly determines assigned OVR/potential.

## Composition & reproducibility

- **2,652** imported players in the source file.
- **1,472 fictional roster players** (46 × 32). Each club has the same positional structure: 2 QB, 3 RB, 6 WR, 3 TE, 4 OT, 4 OG, 2 C, 3 DE, 3 DT, 3 EDGE, 4 LB, 4 CB, 3 S, 1 K, 1 P.
- **480 draftClass** players — exactly 470 from public 2026 source, plus 10 shifted 2027.
- **700 freeAgent** real 2026 NFL players, none duplicated in the draft class.
- No 2026 dead-cap inherited; fictional contracts are inexpensive 1–2 year deals.
- Original public 2026 Players Git blob: `9c35138d93b5065b577cfe07521da49503a1e456` from `jmansfield96/capforge-custom-rosters`.
- 2027 historical V39 Players Git blob: `b69f4643932460e0369765e0d7d49f9e361420e4`.
- 2026 NFL teams copied from published blob `955f82d554133d24644a15082256fd187a584fb1`.
- Exact selected 2026 player IDs and 2027 headliners are frozen in `preview/nfl-rebirth-2026-draft-manifest.json`.
- Static integrity script: `python scripts/validate_2026_nfl_rebirth.py`.

**Known unknowns:** Whether CapForge Draft Day honors imported 2026 draftClass records; whether it requires exactly 480 class rows or generates replacements; whether older NFL veterans can be drafted/contracted as first-time rookies; draft pick fairness; whether undrafted players enter the open FA market; how Player Editor no-op Save affects `development.potential` for drafted prospects; whether intended starting-roster OVRs are recalculated from attributes; and whether 2027/2028 future classes need an additional mechanism. Only a disposable in-game start and exported save can answer these.

## Separation from historical project

This experiment lives solely in `experiment/nfl-rebirth-2026-fantasy-draft` and a **draft pull request**. Existing `main`, user franchises, historical 2020 roster work, Issue #41 and Project Ice are not modified. Never merge into main until verified.
