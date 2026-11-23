# V42 — population-limit versus import-initialization diagnostic (TEST ONLY)

**Status:** Static files generated and validated; gameplay outcomes untested. Never use these for a permanent franchise. V30/V34/V36/V39, V2 Teams, V25 Staff, original saves and Project Ice are frozen.

## Source/control

All variants are **unmodified subsets** of the existing immutable `preview/players-2020-nine-class-no-personality-v39-TEST.json` Git blob `b69f4643932460e0369765e0d7d49f9e361420e4`. The V39 nine-class import **already failed** the user-observed Arcade import/editor-save growth test, providing control D. V39 intentionally has no custom `progressionCurve` or `personality`. We are NOT claiming those omissions resolve anything.

- [A — NFL only](../preview/players-2020-v42-A-nfl-only-TEST.json): 2,293 original 2020 roster players; **zero** imported future draft prospects.
- [B — 2021–2023 full](../preview/players-2020-v42-B-2021-2023-full-TEST.json): same 2,293 roster players + 480 each in 2021, 2022 and 2023; **3,733** total.
- [C — nine classes, 160 each](../preview/players-2020-v42-C-nine-class-160-TEST.json): same 2,293 roster players + 160 per year in 2021–2029; **3,733** total.
- [D — full V39 existing failed Arcade baseline](../preview/players-2020-nine-class-no-personality-v39-TEST.json): same roster + 480 per year in 2021–2029; **6,613** total.

**C selection:** Preserve all 203 future players originally rated 85+ potential (including all **76** future players rated 90+), plus Penei Sewell, Jeremiah Smith, Darian Mensah, Arch Manning, Tavien St Clair and Akili Smith Jr. Fill each year to 160 while preserving every available position by proportionate deterministic selection of lower-potential depth. Every player included is an **identical full record** from V39; no OVR, potential, attribute, contract, draft history, ID, portrait, staff, team, or salary values were modified. Draft classes are not relocated to different draft seasons. All original roster players are retained in all versions. Class C is **below 224 players / seven NFL rounds**, so the game might automatically generate supplemental draft prospects, truncate the draft, or reject it; C is diagnostic only, NOT a plausible final franchise file.

## Controlled in-game protocol

1. Create a **new disposable** Arcade 2020 Reg Season career **for each file**, separately, keeping exactly identical settings (especially Talent Market); use the SAME unchanged Team and Staff inputs below. Do not load this into an existing save.
2. At **NEW GAME → VIEW TEAM → Bills** log Josh Allen (77 OVR, imported 99 potential) badge in preview. Do not Save Changes in any player editor, ever, during the comparison.
3. Start actual new career. Before sim, record Josh Allen's card tier, OVR and numeric Editor "Future Growth" reading; leave editor using **Cancel/Back**, never Save. If accessible, record one draft prospect's numeric future growth (Penei Sewell in B/C/D; Arch Manning and Darian Mensah in C/D).
4. Sim **exactly three games** in each test, with no manual player-editor saves. Recheck Josh Allen's numeric Future Growth/OVR/card tier and each available test prospect. Export Players JSON; label the exports A, B, C, D.
5. Report import-validation result (green/errors), auto-generated prospects if visible, game mode, exact Talent Market setting and any unexpected college-class behavior. **Do not simulate six seasons** unless a test passes initial three-game check. If A itself fails, stop; distant draft classes are not a necessary cause.
6. If early checks pass, repeat through a full year before approving any roster, to rule out later-season normalization. Even success in three games doesn't prove long-term stability.

**Teams V2:** https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/teams-2020-roofs-v2.json

**Staff V25:** https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/staff-2020-head-coach-video-matched-v25.json

**Control D V39:** https://raw.githubusercontent.com/danner821/capforge-nfl-rewind-2020/main/preview/players-2020-nine-class-no-personality-v39-TEST.json

## Interpretation (not proof of a fixed cap)

- **A fails:** No future prospects are *required* to cause the observed symptom. It does not logically rule out additional capacity constraints, but favors general import initialization or other game mechanics.
- **A passes, B fails:** One or more future classes/volume/talent distribution may trigger a difference.
- **B passes, C fails:** Nine-year horizon, prospect distribution, or partial draft-class fill may be contributing. C's 160-player class is a confounder.
- **B and C pass, D fails:** Full player count may matter. Since C retains all 76 originally elite future prospects, C passing argues against a strict cap based only on high-potential future-prospect counts.
- **All pass:** Prior V39 failure may depend on additional conditions. Retry D with exact same settings, export at three games and midseason before drawing conclusions.
- **A/B/C show all imported potentials intact until later:** Progression-time bug rather than an immediate hard import rejection remains possible.

The proprietary CapForge engine is not in this repository. These tests cannot establish why Save Changes in its editor repairs imported development. Seek app developer diagnosis using [issue #41](https://github.com/danner821/capforge-nfl-rewind-2020/issues/41) if population reduction does not solve the problem. No public release or changes to permanent game saves are authorized by these fixtures.
