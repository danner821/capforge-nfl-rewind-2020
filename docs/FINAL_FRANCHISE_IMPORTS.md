# CapForge NFL Rewind 2020 — historical V33 stack (temporary trade-value issue)

**STATUS UPDATE 2026-11-21: V33 launch recommendation temporarily suspended.** A critical issue was found: the 2020 source import assigns `draftNum: -1` even to historically drafted rookies and veterans, producing artificially low trade values. See `docs/LIVE_HANDOFF.md` V34. A separately versioned, draft-history-only V34 Players candidate is being developed and must pass an actual in-game trade-value and potential-badge check before new permanent games. The three URLs below remain the historical V33 stack and are retained for rollback, **not recommended for a new permanent start**.

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


## V34 follow-up — new trade-value test candidate (NOT YET game approved)

See [V34 draft-pick repair test](V34_DRAFT_PICK_REPAIR_TEST.md). The old V33 final recommendation remains suspended until the new V34 file is checked for rookie trade values and the potential badge. Do not replace the V30 file in place or assume an existing save updates automatically.


## V36 growth blocker follow-up (NOT YET APPROVED)

The old V33/V34 launch guidance is **on hold** because actual V34 imported player potential declined unless the editor was saved. See [the separate V36 one-season growth test](V36_GROWTH_IMPORT_TEST.md). Do not launch a new permanent save until automatic player development works in the V36 test without editing player cards.


**2026-11-21 follow-up: V36 failed the in-game Josh Allen A/B too.** Do NOT start a permanent game using V36 pending a controlled Arcade-vs-Dynasty diagnosis and/or confirmation from the CapForge developer. See [runtime developer triage](CAPFORGE_IMPORT_POTENTIAL_ENGINE_TRIAGE.md). The current import stack is preserved, no new JSON version has been proposed.
