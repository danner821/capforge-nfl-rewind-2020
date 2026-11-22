# V36: test imported potential/development without custom curves

**Status: separate experimental Players import, GitHub tests passed, CapForge season-simulation test not yet verified.**

This issue is **real gameplay behavior**, not just a wrong badge: In the V34 save, Josh Allen QB's future ceiling fell from 99 to 86 by midseason when left untouched; in a separate identical V34 save, no-change Editor Save made his initial card Franchise and preserved the 99 ceiling and intended growth through the season. This suggests imported development isn't initialized in the same way as an Editor Save.

The V34 import had a hand-authored 31-number `progressionCurve` on 6,311 players, including Josh Allen. Two established public CapForge imported rosters (2018, 2026) omit that field. V36 removes **only** this nonstandard property from the frozen V34 data. All numeric development potentials/current overalls, attributes, contracts, faces, corrected draft picks, and 4,320 future prospect identities remain unchanged.

## Copyable CapForge URLs for a **NEW disposable 2020 franchise**

**Players V36 — NEW TEST**
```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-editor-compatible-growth-v36-TEST.json
```

**Teams V2 — unchanged**
```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json
```

**Staff V25 — unchanged**
```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/staff-2020-head-coach-video-matched-v25.json
```

## Decisive test

1. Start at **2020 Reg Season**, ensure all imports green. Do not open or Save player editor for Josh Allen before the test.
2. At Week 1, note Josh Allen QB's badge, future growth ceiling, and current OVR. *Do not save changes in his editor; if you open it to read the ceiling, cancel/back out.*
3. Sim to **midseason**, then inspect future ceiling and OVR. Continue through the **end of 2020**, repeat. The unedited V34 control previously fell **99→86**, while editor-saved V34 stayed **99**.
4. Also check another high-ceiling imported player who has not received an editor Save. Spot-check Joe Burrow and Justin Jefferson Trade Center values to confirm V34 draft-number fix survived.
5. **Only if V36 growth holds without editor saves** should we consider it a viable permanent franchise input. Then check that the 2021 draft class is present and salary caps still look normal.

**If V36 fails:** Do not open and save every imported player manually; instead use the controlled V34/V36 evidence to report an app-side import-initialization defect to the CapForge developer. The roster repository cannot patch its proprietary simulation or retroactively edit saved games.

Read [V36 aggregate audit](../preview/v36-progression-import-compatibility-audit.json), [live handoff](LIVE_HANDOFF.md), or [blocker Issue #41](https://github.com/danner821/capforge-nfl-rewind-2020/issues/41). Preserve original V34 and V30 files.
