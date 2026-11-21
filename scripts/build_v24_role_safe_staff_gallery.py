#!/usr/bin/env python3
"""V24: role-safe disposable CapForge staff portrait gallery.

Fix V23: changing offScout/defScout/teamDoctor/free-agent roles to headCoach
left role-specific sparse fields in place, resulting in 150 in-game errors.
Keep each selected free agent's ORIGINAL role, data and skill fields. Change
ONLY first name, surname, and portraitId for 73 fictional free agents.
Use 64 existing headCoach slots + 9 existing offCoordinator slots.
All 224 employed real 2020 staff are EXACTLY unchanged.

This is a TEST-ONLY visual catalog. Never use in a permanent franchise save.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
V16=PREVIEW/"staff-2020-coaching-v16.json"
BASE=PREVIEW/"staff-2020-valid-coach-portraits-v22.json"
OUTPUT=PREVIEW/"staff-portrait-gallery-role-safe-v24-TEST-ONLY.json"
REPORT=PREVIEW/"v24-staff-portrait-gallery-map.json"
PRIORITY=("portrait-0675","portrait-0689","portrait-0670",
          "portrait-0296","portrait-0677","portrait-0699","portrait-0660")

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Partial V24 catalog present; refusing overwrite")
        print("V24 frozen catalog already present")
        return
    green=read(V16)
    original=read(BASE)
    assert len(green)==len(original)==672
    assert len({x["iden"] for x in original})==672
    known=sorted({s["bio"]["portraitId"] for s in green if s["bio"].get("portraitId")})
    assert len(known)==73
    assert all(re.fullmatch(r"portrait-\d{4}",p) for p in known)
    assert len(set(PRIORITY))==7 and set(PRIORITY).issubset(known)
    # Prioritize on-screen inspectability of the seven V22 selections.
    ids=list(PRIORITY)+[p for p in known if p not in PRIORITY]
    out=copy.deepcopy(original)
    free_hc=sorted((s for s in out if s["pool"]=="freeAgent" and s["role"]=="headCoach"),key=lambda s:s["iden"])
    free_oc=sorted((s for s in out if s["pool"]=="freeAgent" and s["role"]=="offCoordinator"),key=lambda s:s["iden"])
    assert len(free_hc)==len(free_oc)==64
    slots=free_hc+free_oc[:9]
    assert len(slots)==len(ids)==73
    assigned_ids=set()
    mapping={}
    before_by_id={x["iden"]:x for x in original}
    for portrait,slot in zip(ids,slots):
        code=portrait[-4:]
        assert slot["iden"] not in assigned_ids
        assigned_ids.add(slot["iden"])
        old=before_by_id[slot["iden"]]
        assert slot["role"]==old["role"],"Staff role changed before assigning portrait"
        # Only three scalar fields differ. Never adjust skills, development,
        # team, role, age, contract, or source role-specific fields.
        slot["forename"]="Avatar"
        slot["surname"]="Pic"+code
        slot["bio"]["portraitId"]=portrait
        mapping[portrait]={
            "displayName":"Avatar Pic"+code,
            "role":old["role"],
            "pool":"freeAgent",
            "visualReview":"PENDING_IN_GAME",
        }
    changed=0
    by_role=Counter()
    for row in out:
        old=before_by_id[row["iden"]]
        if row["iden"] not in assigned_ids:
            assert row==old,"Unselected employed or free-agent staff changed"
        else:
            assert row["pool"]==old["pool"]=="freeAgent"
            assert row["role"]==old["role"],"Role may never change"
            assert row["skills"]==old["skills"]
            assert row["development"]==old["development"]
            assert row["contract"]==old["contract"]
            assert {k:v for k,v in row.items() if k not in ("forename","surname","bio")}=={
                k:v for k,v in old.items() if k not in ("forename","surname","bio")}
            assert {k:v for k,v in row["bio"].items() if k!="portraitId"}=={
                k:v for k,v in old["bio"].items() if k!="portraitId"}
            changed+=1
            by_role[row["role"]]+=1
    assert changed==73 and by_role==Counter({"headCoach":64,"offCoordinator":9})
    assert sum(r["pool"]=="staff" for r in out)==224
    assert sum(r["pool"]=="freeAgent" for r in out)==448
    OUTPUT.write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf-8")
    report={
        "status":"V24_ROLE_SAFE_STAFF_GALLERY_CI_PASS_GAME_IMPORT_PENDING_TEST_ONLY",
        "purpose":"Expose 73 accepted CapForge staff avatar IDs as labeled temporary free agents without violating per-role sparse fields",
        "failedPreviousVersion":"staff-portrait-reference-gallery-v23-TEST-ONLY.json",
        "fixedIssue":"V23 changed free-agent scouts and team doctors into headCoach roles but left incompatible role-specific fields, causing 150 importer errors",
        "baseStaffFile":BASE.name,
        "testOnlyStaffFile":OUTPUT.name,
        "sourcePreviouslyAcceptedStaff":V16.name,
        "totalStaff":672,
        "employedStaffUnchanged":224,
        "unchangedFictionalFreeAgents":375,
        "labeledDiagnosticFreeAgents":73,
        "roleDistribution":dict(by_role),
        "portraitToMarketLabel":mapping,
        "priorityPortraitsFirstInHeadCoachRole":list(PRIORITY),
        "preservation":{
            "allEmployed2020CoachesAndTeamPersonnel":True,
            "allStaffRoles":True,
            "allSkillsStylesDevelopmentContracts":True,
            "onlyThreeFieldsEditedInDiagnostics":["forename","surname","bio.portraitId"],
            "V19PlayersAndV2Teams":True,
            "existingUserSaves":True,
        },
        "instructions":[
            "Use a NEW throwaway 2020 game; V19 Players + V2 Teams + V24 TEST-ONLY Staff.",
            "Check Staff shows 672 with zero errors before starting.",
            "Open Staff free-agent market. Start in Head Coach and look for Avatar Pic#### (64 entries).",
            "Switch to Offensive Coordinator for the remaining 9 Avatar Pic#### entries.",
            "Send screenshots or a slow recording with avatar faces and their Pic#### names visible.",
            "Do not use this staff file in a real long-term franchise save. Switch back to playable V22."
        ],
        "limitations":[
            "V24 is schema-preserving under the known-good V22 rows, but actual CapForge import has NOT yet been verified.",
            "V24 changes 73 fictional free agents only to expose visual IDs; it fixes no actual coach likeness.",
            "A complete face-to-ID visual reference is still required before curation.",
            "Market layout/sorting and display of all diagnostic free agents requires in-game confirmation."
        ]
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"diagnostic":changed,
      "byRole":dict(by_role),"realStaffUntouched":224,
      "sha256":hashlib.sha256(BASE.read_bytes()).hexdigest()},indent=2))

if __name__=="__main__":
    main()
