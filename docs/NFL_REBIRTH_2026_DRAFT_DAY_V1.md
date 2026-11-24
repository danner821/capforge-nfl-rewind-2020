# NFL Rebirth 2026 — fantasy-draft-inspired reset (V1, TEST ONLY)

**NOT a proven in-game import. Do not start a permanent franchise yet.** GitHub branch: `feature/nfl-rebirth-2026-draft-day-v1`. Original 2020 NFL Rewind files and Project Ice are untouched.

## Concept

This is a new independent alternate-history **2026 Draft Day** start in CapForge: all 32 NFL franchises begin with complete rosters consisting exclusively of fictional low-rated players. The 2026 prospect pool is a talent dispersal of famous contemporary NFL players plus ten accelerated 2027 college stars.

### Imported players

| Category | Count | Construction |
|---|---:|---|
| Fictional 2026 active rosters | 1,696 | 53 per team, 32 clubs, 58–68 OVR, potential ≤70; all 15 positions, plausible low-tier ratings and generic fictional names |
| 2026 draft class | 480 | 470 top OVR NFL players from independent public 2026 roster, plus 10 named players from frozen 2027 class |
| Real 2026 free agents | 700 | Next 700 players from the public 2026 roster, in overall-first ordering |
| **Total** | **2,876** | Each player ID unique; drafted/free-agent players not preassigned to a club |

The fictional roster records are mechanically calibrated by *using the numerical ratings, physical positions and portraits of independently published low-OVR players as anonymous templates*, assigning **new fictional names and UUIDs**, and allocating one low-rated player into each position slot of the public source's existing, complete 53-man NFL rosters. This avoids guessed per-position ratings that CapForge would reject as inaccurate OVR. These players are **not** intended as historical people, and their one-year contracts are modeled.

The top 470 NFL names are sorted by 2026 source `development.ovr` descending, then source potential/age as tie-breakers; this is not a bespoke scouting ranking. All real stars retain source ratings/portrait IDs/actual ages. A simulated league reset requires setting `bio.draftSeason:2026` and `pool:draftClass` on draft entrants even if they were actually drafted years ago: **do not interpret 2026 as their real first NFL draft**. Imported veteran contracts are zeroed to permit the game's rookie-draft-contract generation; whether that works for older players is UNTESTED.

**Ten accelerated 2027 players (all pulled directly from the frozen V39 2027 class):**
Jeremiah Smith (WR), Arch Manning (QB), Drew Mestemaker (QB), Dante Moore (QB), CJ Carr (QB), Colin Simmons (EDGE), Dylan Stewart (EDGE), Leonard Moore (CB), Charlie Becker (WR), Jordan Seaton (OT). Each now has the 2026 draft season and is NOT also in a separate 2027 class in this V1 file.

Every 2026 draft/FA prospect has explicit `development.potential` equal to or greater than overall; for records where public 2026 omitted potential, V1 defaults to that player's current overall. V1 does not invent new superstar future-potential ceilings or custom progression curves. The prior potential-initialization bug may still occur.

## Direct imports

- **PLAYERS** (V1 prototype): `https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/feature/nfl-rebirth-2026-draft-day-v1/preview/nfl-rebirth-2026-fantasy-draft-v1-TEST.json`
- **TEAMS** (unchanged public NFL clubs): `https://raw.githubusercontent.com/jmansfield96/capforge-custom-rosters/main/teams-files/nfl-teams.json`
- **STAFF:** Leave blank / CapForge DEFAULT.

Use the *new* dedicated TEST Players link, not the earlier 2020 Players or the untouched public 2026 Players import. If the CapForge importer cannot fetch this branch URL or reports an import warning/error, **do not assume success or change other imports**: capture the exact error first.

## In-game acceptance test (do not skip)

1. Create a **brand-new disposable 2026 save** in New Game → IMPORT, add Players link, add Teams link, leave Staff blank. Validate.
2. Pick **2026 DRAFT DAY**, **ARCADE**, **DEEP** for an apples-to-apples development baseline. Do **not** pick Reg Season (we want to draft first). Choose any team, e.g. Raiders.
3. Before draft, inspect the team's fictional roster: no established real NFL stars, all rated at most 68 OVR by import. Verify 53 active roster players and all positions. Note any game-side cuts/autofills.
4. Inspect the 2026 draft board: real 2026 NFL players such as Josh Allen/Patrick Mahomes/Ja'Marr Chase and newly promoted Arch Manning/Jeremiah Smith appear as 2026 prospects (not on existing teams). Count any truncation or missing 2027 names.
5. Check a top real prospect's potential badge and editor numeric future growth **without saving**; cancel. If the draft-class editor is unavailable before the draft, note that and continue.
6. Make at least one real-player pick. Verify he arrives on the roster. Sim/finish the remaining draft. Verify contracts are created and only 224 total selections occur under the normal seven-round rules; undrafted players should enter free agency if the game follows its stated standard behavior.
7. **Do not manually Save Changes on 480 players yet.** On your drafted player's editor, first verify the reported potential issue exists for imported 2026 draft-class players. If it does, run a *single-player* no-change Save for one player, leave another imported rookie untouched as control, then sim exactly 3 regular-season games. Export Players and compare true potentials. Avoid any edits in a real save.
8. Return results/screenshot of the validated importer, first draft board, any construction error, draft contracts and exported Players JSON. Do not play multiple seasons before the first gate passes.

## Important gameplay limitations

- **Seven-round 224-pick draft:** This is a `dispersal draft`, **not a complete 40+ round snake fantasy draft**. Forty-five or more original fictional placeholders can remain per team after seven picks and automatic roster pruning; real FAs allow additional signings. Do not imply 480 draft prospects all get selected.
- **CapForge private engine:** Neither GitHub checks nor our external importer can alter the app's draft order, add draft rounds, bypass hidden draft eligibility rules, or apply no-op editor saves in bulk. Draft Day might reject veterans/prospects or reroll potential; these remain live tests.
- **Roster limit:** 53 active fictional players/team before the 2026 draft avoids missing-position league initialization; post-draft auto-trimming may be necessary.
- **Salary:** Fictional rosters deliberately use modeled one-year $2.5–3.75M contracts; draft entrants have $0 pre-draft contracts to be assigned by the engine. Cap feasibility and rookie reserves need in-game verification.
- **Future classes:** No imported 2027–2029 classes yet; after confirming 2026 mechanics, future real classes should be added, excluding the ten 2027 players promoted here.
- **Source provenance:** Real 2026 player attributes and cartoon IDs derive from `jmansfield96/capforge-custom-rosters/player-files/madden-27-players.json`, frozen Git blob `9c35138d93b5065b577cfe07521da49503a1e456`. Fictional club positional templates and team IDs derive from the same data and `teams-files/nfl-teams.json`. Ten accelerated players derive from our frozen V39 2027 prospect pool, blob `b69f4643932460e0369765e0d7d49f9e361420e4`. Original source import files are never overwritten.

## Static checks

Run `python scripts/validate_nfl_rebirth_2026.py` on this branch to verify counts, positions, unique IDs, team assignment, OVR range, draft class season, original ten promoted identities, and contract states. **Even a green static CI is not proof the CapForge app can create and progress a save.**
