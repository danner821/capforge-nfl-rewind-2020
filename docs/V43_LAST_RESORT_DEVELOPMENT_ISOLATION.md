# V43 — last-resort imported-potential isolation (TEST ONLY)

**Status:** Candidate imports generated; **NO CapForge gameplay result yet**. Nothing in this branch is approved for a permanent career. Original V30/V34/V36/V39, V42 A/B/C/D, Teams V2, Staff V25, and Project Ice are unchanged.

## Evidence before V43

- V39 in **Arcade** mode still showed Josh Allen's imported Franchise / 99-potential player dropping to Starter/Impact during active career; no-change Player Editor Save repaired him.
- V42 **A** excludes ALL imported future drafts, yet the user's Test A CapForge export still reduced Bills QB Josh Allen from 77/99 to **77/78** and Joe Burrow from 76/99 to **75/77**. At that export point the game had generated its own 2021–24 classes (480 each).
- Thus nine imported draft classes are **not necessary** to trigger the symptom. Test A does not conclusively rule out engine-wide talent-balancing/normalization, because CapForge may also create replacement future classes.

## Two precise 2020 NFL-only experiments

Both begin from the **same immutable source** as V42 A: Git blob `74aecc7993d9cf6c045483c11e2bdafc60662376`, 2,293 original 2020 roster records, no imported draft classes. All original identities, ages, ratings, OVR, team placements, contracts, portraits, draft history and schema are preserved. Neither contains authored personality or progressionCurve.

1. [V43-B — ONLY Josh has growth; potential key remains explicit](../preview/players-2020-v43-B-only-josh-has-growth-TEST.json).
   - **Josh Allen, BUF QB** retains `development: {ovr:77,potential:99}`.
   - Every other 2,292 NFL player retains original OVR but has `potential=ovr`.
   - If Josh 99 is lost here, a population of other *imported high-potential ceilings* is not required. This is not a realistic roster.
2. [V43-A — ONLY Josh has explicit potential](../preview/players-2020-v43-A-josh-only-explicit-TEST.json).
   - **Josh Allen, BUF QB** retains `development: {ovr:77,potential:99}`.
   - Every other NFL player's `development.potential` **key is absent** (their other fields are unchanged).
   - Public CapForge roster samples already omit potential on many ordinary players, so this is a valid source-format experiment, but game behavior may differ. This isolates how the new-game initializer handles missing-versus-explicit potential.

**Use B first, then A if B fails.** These files are **NOT final franchises**: thousands of other player ceilings are intentionally absent or lowered for isolation.

## In-game test protocol

- Start a **new disposable 2020 REG SEASON ARCADE** career for EACH Players file; do not import into an old save.
- Import **Teams V2** and **Staff V25** unchanged. Use the **exact same Talent Market settings** as failed V42 Test A. Do not manually change any player.
- Before starting, inspect NEW GAME → VIEW TEAM → Bills → Josh Allen, note his card tier.
- On entering the playable career, **before simulating games**, inspect Josh Allen card (tier/current OVR) and Player Editor Future Growth; EXIT editor via Cancel/Back — **NEVER Save Changes**.
- Sim **three games**, inspect Josh again and export Players JSON; name that result V43-B or V43-A. If the error is immediately visible, record it and stop early.
- Note any game import warning and whether future draft classes were automatically generated.
- If a candidate preserves Josh's 99 after three games, test **one full season** before using it as evidence of stability. This still would not establish it can handle nine imported classes.

## Interpretation

| Outcome | What it supports |
|---|---|
| B fails, A fails | Even with one imported high-growth player, failure survives. Strongly favors import-hydration/app-side progression over elite population or nine-class count. Escalate to CapForge developer. |
| B fails, A passes | Differences between explicit potential for everyone and selective/missing potential may contribute. Investigate proper optional-field behavior; DO NOT assume entire nine-class roster works. |
| B passes, A passes | Other imported player potentials/talent distribution may influence initial growth; graduate to a more realistic balanced nine-class subset. |
| B passes, A fails | Explicit potential may be required for valid initialization, or omitted values trigger different fallback. Investigate builder/default behavior. |

All outcomes require careful control for the same Talent Market and whether CapForge generates new draft classes. **No game outcomes claimed in this document.**

## Frozen external inputs

- Teams V2: https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json
- Staff V25: https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/staff-2020-head-coach-video-matched-v25.json
- Failed baseline V42 A: https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-v42-A-nfl-only-TEST.json
- Existing engine bug: https://github.com/danner821/capforge-nfl-rewind-2020/issues/41

No proprietary CapForge code is in this repository; GitHub JSON validation cannot certify in-game development. No edits to permanent imports, saves, releases or Project Ice are authorized by these files.
