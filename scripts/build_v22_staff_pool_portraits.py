#!/usr/bin/env python3
"""V22: seven experimental COACH-POOL portraits replacing rejected V21 PLAYER IDs.

The green V16 import established that specific staff IDs can be accepted.
V21 incorrectly reused player-only IDs: CapForge rejected all seven.
V22 uses V20 staff (actual 2020 HC ages), adds only seven explicit portraits
which already appeared in green V16 Staff, and preserves all other data.
A successful import does not prove real-world facial likeness.
"""
from __future__ import annotations
import copy
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
STAFF_GREEN=PREVIEW/"staff-2020-coaching-v16.json"
STAFF_AGE=PREVIEW/"staff-2020-coaches-age-qa-v20.json"
STAFF_BAD=PREVIEW/"staff-2020-coach-portrait-proxies-v21.json"
SOURCE=ROOT/"data/coaches_2020_v22_staff_portrait_candidates.json"
OUTPUT=PREVIEW/"staff-2020-valid-coach-portraits-v22.json"
REPORT=PREVIEW/"v22-valid-staff-portrait-audit.json"
ROLES=("headCoach","offCoordinator","defCoordinator","specialTeams")

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Incomplete V22 outputs: refusing overwrite")
        print("V22 outputs already published/frozen");return
    source=read(SOURCE)
    accepted=read(STAFF_GREEN)
    baseline=read(STAFF_AGE)
    rejected=read(STAFF_BAD)
    assert source["version"]=="V22-STAFF-POOL-PILOT"
    assert len(accepted)==len(baseline)==len(rejected)==672
    assert len(source["assignments"])==7
    assert len({x["iden"] for x in baseline})==672
    assert {x["iden"] for x in baseline}=={x["iden"] for x in accepted}=={x["iden"] for x in rejected}
    validStaffIDs={x["bio"]["portraitId"] for x in accepted if x["bio"].get("portraitId")}
    assert len(validStaffIDs)>=60,"Unexpected shrinking of green V16's known staff ID pool"
    invalidV21={x["bio"]["portraitId"] for x in rejected if x["pool"]=="staff" and
                x["role"] in ROLES and x["bio"].get("portraitId") and
                not x["bio"]["portraitId"] in validStaffIDs}
    assert len(invalidV21)==7,"Previously rejected V21 player IDs changed unexpectedly"
    assert not invalidV21.intersection(validStaffIDs)
    out=copy.deepcopy(baseline)
    slots={(x.get("teamAbbr"),x.get("role")):x for x in out if x["pool"]=="staff"}
    assert len(slots)==224
    records={}
    for slot,info in source["assignments"].items():
        abbr,role=slot.split(":")
        assert role=="headCoach", "Seven-coach pilot restricted to head coaches"
        row=slots.get((abbr,role))
        assert row is not None
        assert row["forename"]+" "+row["surname"]==info["coach"]
        assert row["bio"]["age"]==info["coachAge2020"]
        assert row["bio"].get("portraitId") is None,"V20 coach portrait already curated"
        portrait=info["portraitId"]
        assert re.fullmatch(r"portrait-\d{4}",portrait)
        assert portrait in validStaffIDs, f"{portrait} is NOT in the actual green V16 staff ID pool"
        assert portrait not in invalidV21,"V21 rejected player-only avatar reused"
        assert info["referenceTemplateRole"]=="headCoach"
        assert 0<=abs(info["coachAge2020"]-info["referenceTemplateAge"])<=5
        row["bio"]["portraitId"]=portrait
        records[slot]={
            "coach":info["coach"],
            "portraitId":portrait,
            "evidence":"explicit_id_present_in_user_accepted_V16_staff_file",
            "roleAndAgeMatch":"approximate_only",
            "visualLikeness":"NOT_VERIFIED"
        }
    assert len({x["portraitId"] for x in records.values()})==len(records)
    before={x["iden"]:x for x in baseline}
    changed=0
    for r in out:
        old=before[r["iden"]]
        slot=f'{r.get("teamAbbr")}:{r["role"]}'
        if slot in records:
            assert r["pool"]=="staff"
            r_nobio={k:v for k,v in r.items() if k!="bio"}
            old_nobio={k:v for k,v in old.items() if k!="bio"}
            assert r_nobio==old_nobio
            old_bio=copy.deepcopy(old["bio"])
            new_bio=copy.deepcopy(r["bio"])
            new_bio.pop("portraitId",None)
            assert new_bio==old_bio
            changed+=1
        else:
            assert r==old,f"Unselected staff record mutated: {r['iden']}"
    assert changed==7
    assert sum(x["pool"]=="staff" for x in out)==224
    assert sum(x["pool"]=="freeAgent" for x in out)==448
    assert sum(x["pool"]=="staff" and x["role"] in ROLES and x["bio"].get("portraitId") is not None for x in out)==7
    OUTPUT.write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf-8")
    report={
        "status":"V22_KNOWN_VALID_STAFF_POOL_IDS_CI_PASSED_VISUAL_LIKENESS_AND_V22_IMPORT_PENDING",
        "inputStaff":STAFF_AGE.name,
        "previousFailedStaff":STAFF_BAD.name,
        "outputStaff":OUTPUT.name,
        "totalStaffRecords":672,
        "occupiedStaff":224,
        "teamCount":32,
        "knownPortraitIDsInGreenV16Staff":len(validStaffIDs),
        "rejectedV21PlayerPortraitIDs":len(invalidV21),
        "coachPortraitCandidatesReplaced":len(records),
        "remainingDefaultCoachFaces":128-len(records),
        "assignments":records,
        "preserved":{
            "all672StaffIdentityRecords":True,
            "rolesTeamsNamesCoachAges":True,
            "skillsAndContracts":True,
            "other121CoachFaceAssignments":True,
            "96ScoutsAndDoctors":True,
            "448FreeAgentStaff":True,
            "V19PlayersV2TeamsDraftClasses":True
        },
        "limitations":[
            "The seven IDs appeared in V16 Staff that received a green CapForge checkmark; this is strong staff-pool compatibility evidence, not V22 in-game validation.",
            "We have not inspected the game-rendered face for these portrait IDs and cannot promise any specific resemblance, facial feature or skin tone.",
            "Matt LaFleur is prioritized but his originally reported incorrect default face is not confirmed fixed until gameplay screenshot.",
            "Age-matched community-template head-coach portrait proxies are an approximation, not actual real 2020 coach portraits.",
            "No player-only IDs are reused; V19 Players, Teams V2, Staff V16/V20 and any user saves remain untouched."
        ],
        "testPlan":"NEW disposable game V19 Players + V2 Teams + V22 Staff, confirm zero Staff warnings and inspect Matt LaFleur and six other head-coach cartoons."
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":report["status"],
        "staffIDsFromGreenImport":len(validStaffIDs),
        "rejectedV21playerIds":len(invalidV21),
        "replacedCoachPortraits":len(records),
        "staffRecords":len(out),
        "laFleurCandidate":records["GB:headCoach"]["portraitId"]
    },indent=2))

if __name__=="__main__":
    main()
