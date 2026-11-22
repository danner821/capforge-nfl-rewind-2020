# CapForge NFL Rewind 2020 — recommended permanent franchise imports

**Status: Ready for actual franchise play, with user-reported testing and noted limitations.**

**Use this exact import stack**. The V30 Players file still ends in `-TEST.json` because this is the specific unchanged version the user tested successfully in CapForge; the name does not mean a new file is required.

## Players (V30)

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-contracts-v30-TEST.json
```

## Teams (V2)

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json
```

## Staff (V25)

```text
https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/staff-2020-head-coach-video-matched-v25.json
```

Start **New Game → 2020 season**, paste each direct raw URL in the corresponding import field, confirm all three green, then begin and save the real franchise. Keep disposable test save separate.

## Acceptance evidence

- All three imports green per user's report; actual 2020 Week-1 game launched.
- Actual 2020 PIT/BAL/JAX payroll screens reviewed with positive cap room.
- Actual 2021 Week-1 PIT/BAL/JAX payroll screens reviewed with positive cap room, demonstrating 2020→2021 progression and roster changes.
- User reported no issues progressing through 2024 and then stated everything looked good after requested later-year spot checks. Late-year draft screens are not independently inspected; no claim of exhaustive playthrough verification.
- Original V19 Players fallback, immutable V30 import, Teams V2 and Staff V25, all nine future draft classes, and Project Ice kept unchanged.

For provenance see `data/v33-final-franchise-import-manifest.json`, `preview/v30-contract-calibration-audit.json`, `preview/v31-v30-real-2021-cap-rollover-audit.json`, and `docs/LIVE_HANDOFF.md`.

**Release freeze:** Future tweaks must create new optional versioned files instead of overwriting these confirmed working imports.
