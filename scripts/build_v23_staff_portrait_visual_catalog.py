#!/usr/bin/env python3
"""V23: temporary in-game staff portrait catalog, NOT a playable roster upgrade.

User confirms V22 staff imports green but many real coaches look wrong.
Before guessing further, show every explicitly known green V16 staff-only
portrait ID as a labeled free-agent HEAD COACH inside one throwaway CapForge
game. The player can screen-record the market list and we can reliably map
the printed ID -> rendered art. Production V22 employed coaches are unchanged.

V23 modifies 73 otherwise-fictional FREE AGENTS solely as visual probes:
name, role, known staff portrait and simple high market skills. It is a
diagnostic pack only and MUST NEVER be recommended for a permanent save.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
GREEN=PREVIEW/"staff-2020-coaching-v16.json"
BASE=PREVIEW/"staff-2020-valid-coach-portraits-v22.json"
OUTPUT=PREVIEW/"staff-portrait-reference-gallery-v23-TEST-ONLY.json"
REPORT=PREVIEW/"v23-staff-portrait-gallery-map.json"

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Partial V23 diagnostic outputs: refusing rewrite")
        print("V23 test-only catalog already generated; skipping")
        return
    accepted=read(GREEN)
    before=read(BASE)
    assert len(accepted)==len(before)==672
    assert len({x["iden"] for x in before})==672
    staff_portraits=sorted({
        x["bio"]["portraitId"] for x in accepted
        if x["bio"].get("portraitId")
    })
    assert len(staff_portraits)==73, "Previously accepted V16 staff portrait set changed"
    assert all(re.fullmatch(r"portrait-\d{4}",p) for p in staff_portraits)
    assert "portrait-0798" not in staff_portraits, "Rejected V21 player ID in catalog"

    out=copy.deepcopy(before)
    occupied=[x for x in out if x["pool"]=="staff"]
    free=[x for x in out if x["pool"]=="freeAgent"]
    assert len(occupied)==224 and len(free)==448
    # Deterministic candidate slots, role changed only in experimental FA staff.
    slots=sorted(free,key=lambda r:r["iden"])[:len(staff_portraits)]
    assert len(slots)==73
    selected_ids={x["iden"] for x in slots}
    gallery={}
    for portrait,staff in zip(staff_portraits,slots):
        code=portrait.split("-")[1]
        # Short searchable display name (typically Avatar Pic0675).
        staff["forename"]="Avatar"
        staff["surname"]="Pic"+code
        staff["role"]="headCoach"
        staff["bio"]["portraitId"]=portrait
        # Make visual references easy to find near the top of staff market;
        # NEVER copy these fictional diagnostic skills into actual rosters.
        staff["skills"]={k:95 for k in staff["skills"]}
        staff["development"]["ovr"]=95
        staff["development"]["potential"]=95
        gallery[portrait]={"displayName":"Avatar Pic"+code,
                           "role":"headCoach","pool":"freeAgent",
                           "photoStatus":"IN_GAME_VISUAL_REFERENCE_NOT_YET_SEEN"}
    original={s["iden"]:s for s in before}
    for row in out:
        if row["iden"] not in selected_ids:
            assert row==original[row["iden"]], "A production coach or other FA changed"
        else:
            old=original[row["iden"]]
            assert old["pool"]=="freeAgent"
            assert not row.get("teamAbbr") and not row.get("teamId")
            assert row["contract"]==old["contract"], "Test contract changed"
    assert len(out)==672 and len({s["iden"] for s in out})==672
    assert sum(s["pool"]=="staff" for s in out)==224
    assert sum(s["pool"]=="freeAgent" for s in out)==448
    assert all(r==original[r["iden"]] for r in occupied)

    OUTPUT.write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf-8")
    report={
        "status":"V23_DIAGNOSTIC_ONLY_NOT_FOR_PERMANENT_SAVES_GAME_VISUAL_CATALOG_PENDING",
        "purpose":"Identify true on-screen appearance of all supported staff-only cartoon portrait IDs before touching 2020 coach likenesses again",
        "baseStaff":BASE.name,
        "previouslyGreenStaff":GREEN.name,
        "testStaffFile":OUTPUT.name,
        "priorV22CoachFacesPreserved":True,
        "published2020PlayersAndTeamsUnchanged":True,
        "totalStaffRecords":672,
        "occupiedStaffUnmodified":224,
        "diagnosticFreeAgentLabels":73,
        "otherFreeAgentsUnmodified":375,
        "supportedPortraitIds":staff_portraits,
        "portraitToMarketLabel":gallery,
        "instructions":[
           "Start NEW throwaway September 2020 CapForge game: V19 Players + V2 Teams + V23 TEST-ONLY Staff",
           "Staff validation should be green 672; this is a disposable research game, not a production coaching import",
           "Go to Staff > Market/Free Agents and filter Head Coach; sort by grade or search Avatar",
           "Find entries labelled Avatar Pic0295, Avatar Pic0675, etc; screen-record scrolling or take several screenshots showing name next to cartoon",
           "If the Staff portrait picker itself displays a complete gallery with IDs, a single picker screen recording can replace the market probe",
           "Share the visual reference, then curate real 2020 HC/OC/DC/ST names using the exact known staff portrait IDs"
        ],
        "limitations":[
          "V23 deliberately changes 73 fictional free agents' names, roles and skills to label avatars; NEVER use it in a permanent franchise save.",
          "This does not claim any coach's visual appearance has been corrected.",
          "The game's Staff market might sort or paginate differently; a screenshot of EDIT STAFF portrait picker is an alternative.",
          "No visual asset catalog is publicly verified; age-only matching in V22 is insufficient for likeness.",
          "Original V22, V20, V16, V19 Players and V2 Teams files remain unmodified."
        ]
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "result":report["status"],
        "labeledStaffAvatarIDs":len(staff_portraits),
        "productionCoachesUnchanged":224,
        "alteredOnlyDiagnosticFreeAgents":73,
        "otherStaffUnchanged":375,
        "baselineSha256":hashlib.sha256(BASE.read_bytes()).hexdigest(),
    },indent=2))

if __name__=="__main__":
    main()
