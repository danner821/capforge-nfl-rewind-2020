#!/usr/bin/env python3
"""CI guard against reusing player-only portraits in CapForge staff imports."""
from __future__ import annotations
import json
from build_v22_staff_pool_portraits import (
    STAFF_GREEN,STAFF_AGE,STAFF_BAD,SOURCE,OUTPUT,REPORT,read,ROLES
)

def main():
    imported=read(STAFF_GREEN)
    baseline=read(STAFF_AGE)
    rejected=read(STAFF_BAD)
    output=read(OUTPUT)
    spec=read(SOURCE)
    audit=read(REPORT)
    assert len(imported)==len(baseline)==len(rejected)==len(output)==672
    assert audit["status"]=="V22_KNOWN_VALID_STAFF_POOL_IDS_CI_PASSED_VISUAL_LIKENESS_AND_V22_IMPORT_PENDING"
    validIds={s["bio"]["portraitId"] for s in imported if s["bio"].get("portraitId")}
    badIds={
        s["bio"]["portraitId"] for s in rejected
        if s["pool"]=="staff" and s["role"] in ROLES
        and s["bio"].get("portraitId") not in validIds
        and s["bio"].get("portraitId") is not None
    }
    assert len(badIds)==7 and validIds.isdisjoint(badIds)
    approved={s["iden"]:s for s in baseline}
    final={s["iden"]:s for s in output}
    assert set(approved)==set(final)
    changes=0
    for ident,old in approved.items():
        new=final[ident]
        key=f'{old.get("teamAbbr")}:{old["role"]}'
        if key in spec["assignments"]:
            change=spec["assignments"][key]
            assert old["pool"]=="staff" and old["role"]=="headCoach"
            assert new["forename"]+" "+new["surname"]==change["coach"]
            assert new["bio"]["age"]==change["coachAge2020"]
            assert new["bio"]["portraitId"]==change["portraitId"]
            assert new["bio"]["portraitId"] in validIds
            assert new["bio"]["portraitId"] not in badIds
            assert {k:v for k,v in new.items() if k!="bio"}=={k:v for k,v in old.items() if k!="bio"}
            assert {k:v for k,v in new["bio"].items() if k!="portraitId"}==old["bio"]
            changes+=1
        else:
            assert old==new,"Unselected personnel changed"
    assert changes==7
    assert audit["coachPortraitCandidatesReplaced"]==7
    assert audit["remainingDefaultCoachFaces"]==121
    assert audit["rejectedV21PlayerPortraitIDs"]==7
    assert audit["knownPortraitIDsInGreenV16Staff"]==len(validIds)
    assert audit["assignments"]["GB:headCoach"]["portraitId"]=="portrait-0675"
    assert audit["preserved"]["96ScoutsAndDoctors"] and audit["preserved"]["448FreeAgentStaff"]
    print(json.dumps({
        "status":"V22_STAFF_POOL_CI_PASS_GAME_VISUAL_QA_REQUIRED",
        "known_green_staff_ids":len(validIds),
        "rejected_v21_player_ids":len(badIds),
        "v22_portrait_fields_changed":changes,
        "no_player_portrait_ids":True,
        "all_others_unchanged":True
    },indent=2))

if __name__=="__main__":
    main()
