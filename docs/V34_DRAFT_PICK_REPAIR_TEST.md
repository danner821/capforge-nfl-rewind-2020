# V34 — test the 2020 rookie trade-value repair before restarting your permanent franchise

**Status: GitHub tests passed. Actual CapForge game test still required.** This is a separate, safe new **Players** import; it does not change the V30 version already in your save.

## Paste in CapForge → New Game → Import, start at 2020 Reg Season

### Players — V34 NEW test

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-draft-history-v34-TEST.json
```

### Teams — V2 UNCHANGED

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json
```

### Staff — V25 UNCHANGED

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/staff-2020-head-coach-video-matched-v25.json
```

### Five-minute game acceptance check

1. Start a **new disposable 2020 franchise** with all three green import checks.
2. **Without opening the editor first**, compare Joe Burrow's Trade Center trade value against the previous ~6; check Justin Jefferson too.
3. In player editor, verify real draft numbers: **Joe Burrow #1, Justin Jefferson #22, Tua Tagovailoa #5, Chase Young #2, CeeDee Lamb #17**.
4. Before making any edits, record Burrow's displayed potential tier. If it still reads **Impact**, save his editor card without changing development, then re-check whether it flips to **Franchise**. This distinguishes the imported draft-number bug from an independent game-editor refresh/serialization issue.
5. Verify the game starts normally, then spot-check early Pittsburgh/Baltimore/Jacksonville payrolls and the untouched 2021 draft class.

## What we know and what we do not

The old `build_2020.py` set `bio.draftNum=-1` for every rostered player. V34 repairs authentic NFL overall picks for **1,352 drafted starting players**, including **236 of the 2020 rookies**. Players whose source identity cannot be verified retain `-1` instead of receiving an invented selection. All 4,320 future class prospects remain pre-draft `-1` until CapForge drafts them. **Contracts, ratings, portraits, and hidden player development values are unchanged from V30.**

The game was not tested via GitHub Actions. The user's earlier editor experiment establishes a likely link between draftNum and trade value, but the **Impact→Franchise tier switch is still unverified as to cause**.

**Existing CapForge games do not pick up newly imported player files.** If the disposable V34 check passes, start a NEW actual Giants 2020 franchise with this V34 Players file. Keep original V30, V2 and V25 versioned files as backups.

Evidence: `preview/v34-historical-draft-history-audit.json` and `docs/LIVE_HANDOFF.md`.
