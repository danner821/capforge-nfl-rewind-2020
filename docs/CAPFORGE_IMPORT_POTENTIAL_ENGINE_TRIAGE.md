# CapForge imported player growth: 2020 preview vs actual career mismatch

**Status (2026-11-21): UNRESOLVED, permanent game release blocked.** This is a read-only investigation and developer reproduction, not a new Players version.

## Proven inputs

2020 historical import:
- **Players V36:** https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-editor-compatible-growth-v36-TEST.json
- **Teams V2:** https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json
- **Staff V25:** https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/staff-2020-head-coach-video-matched-v25.json

The exact published V36 Players blob is `c0bfebadba5116312449b33076eee0eeecab2a27`. Josh Allen, QB, BUF, born/college Wyoming, historical draft 2018 pick 7, has the deliberately simple:

```json
"development": {"ovr": 77, "potential": 99}
```

No `progressionCurve`. The V36 file retains **6,613 players**, including **2,293** starting roster and **4,320** future draft prospects. V34's validated draft pick correction remains intact; all contracts, talents, potential numbers and portraits match V34.

## User's repeated controlled outcomes

| Observation | Untouched V34/V36 new career | New career + no-change editor Save |
|---|---|---|
| Before choosing team | Bills Josh Allen preview: Franchise | Bills Josh Allen preview: Franchise |
| After actual career launches | Josh Allen card: Starter or Impact | Josh Allen card: Franchise |
| Imported Josh Allen development | OVR 77 / future 99 | OVR 77 / future 99 |
| Midyear and year-end future-growth read | **Drops to ~86** | **Remains 99** |
| Growth behavior | Below desired path | Desired development reported |

The user repeated both arms in a second V36 investigation after V34 originally displayed the same issue. The V36 hypothesis that 31-entry custom progression curves caused the initialization problem **did not hold**; removing them did not resolve runtime difference.

**Important caveat:** User has not yet identified whether the controlled runs were started with **Arcade or Dynasty**, the READ PACE, or TALENT MARKET setting. Their "future growth" screen may be an interpreted projection rather than persistent true potential. Avoid claiming that the engine has definitely overwritten underlying potential without a mode-controlled comparison.

## Relevant external documentation

CapForge official App Store page:
https://apps.apple.com/us/app/capforge-football-gm-2026/id6791601497

- **Version 1.5.1 (Oct 10):** NEW GAME → VIEW TEAM is view-only.
- **Version 1.5.2 (Oct 14):** Arcade shows true ratings; Dynasty displays staff reads of player OVR that improve with playing time; `OUR READ` and `READ PACE` distinguish these.
- **Latest version notes (1.8.3):** On `TIGHT` and `BARE` talent markets, young quarterbacks develop more slowly. This can affect actual in-game OVR trajectory and is a separate variable from imported `potential`.

These notes support alternative explanations for badge and short-term growth differences, but do not prove that a numeric 99→86 editor future ceiling is expected or cosmetic. Do not infer behavior beyond the stated notes.

## Decisive next test (one extra game; avoid full seasons if an early mismatch appears)

Create a **new disposable ARCADE** 2020 game with exactly the same V36/V2/V25 imported URLs. Do not touch player editor Save:

1. Read Josh Allen's **Franchise** badge in NEW GAME → VIEW TEAM Bills preview.
2. After Week 1 initialization, compare card label and numeric editor future ceiling; exit editor via Cancel/Back.
3. Sim to the midpoint of 2020. Examine same card, future ceiling and actual OVR growth. Compare to the prior V36 unsaved new game (Starter/Impact, ~86 by midyear).
4. If ARCADE stays 99, investigate Dynasty **staff reads** and Talent Market/READ PACE; explicitly ask developer whether TRUE potential is in fact preserved under Dynasty despite a changing future-growth projection.
5. If ARCADE itself drops 99→86 or the editor no-op Save changes actual true ceiling even with READ effects disabled, treat as likely **CapForge custom roster new-game normalization/importer bug**. The app developer needs to ensure imported development state survives new-game creation the same way an editor Save applies it.

No user should ever have to open/save **2,293 roster + 4,320 draft player cards** manually. The roster-only GitHub project cannot call an app-internal bulk Save. There is no proof that adding guessed JSON fields or modifying source potential would fix this.

## Developer-ready bug report / questions

**Subject:** Imported custom roster potential differs between NEW GAME preview and active franchise; editor no-op Save makes 99 ceiling persist

> Custom 2020 CapForge roster. Imported Josh Allen (BUF QB) `development: {ovr:77,potential:99}` (no progressionCurve) displays Franchise in NEW GAME → VIEW TEAM. Upon starting the career, card instead shows Starter or Impact. When we don't save the player editor, by midseason the editor's Future Growth drops from 99 to ~86 and he underdevelops. In an otherwise identical fresh save, opening Josh Allen's editor and clicking Save Changes without editing anything causes card Franchise and Future Growth 99 even after a season. Reproduced with both V34 (custom curves) and V36 (no custom curves). The import file is https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-editor-compatible-growth-v36-TEST.json .
>
> Can you clarify whether `development.potential` is honored as true persistent potential after NEW GAME, whether Dynasty's staff read/READ PACE might alter the observed values, and what the no-op editor Save normalizes? Is there a supported import schema or one-time whole-league player initialization pass so all 6,613 imported players maintain their intended potential without manual editor saves?

No message to external developer has been sent by this repo; this is a ready-to-paste report. Issue: https://github.com/danner821/capforge-nfl-rewind-2020/issues/41 .

## Keep frozen

**V34** remains the user-confirmed trade-value fix and **V36** remains a failed experimental-growth comparator; no player, coach, team, rating, portrait, salary, hidden potential, draft-class, existing save or Project Ice change is warranted without further evidence.
