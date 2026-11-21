#!/usr/bin/env python3
"""V25 regression: visual labels anchored to V24 and all non-HC data frozen."""
from __future__ import annotations
import json
from collections import Counter
from build_v25_video_matched_head_coaches import (
    BASE,GREEN,GALLERY,COACHES,PROPOSALS,OUTPUT,REPORT,read
)

def main():
    original=read(BASE)
    output=read(OUTPUT)
    green=read(GREEN)
    gallery=read(GALLERY)
    proposals=read(PROPOSALS)
    report=read(REPORT)
    assert len(original)==len(output)==672
    assert report["status"]=="V25_32_VISUALLY_REFERENCED_HC_AVATARS_CI_PASS_INGAME_QA_PENDING"
    known={s["bio"]["portraitId"] for s in green if s["bio"].get("portraitId")}
    assert len(known)==73
    assert len(gallery["portraitToMarketLabel"])==73
    assert len(proposals["curations"])==32
    assert len(report["teamSelections"])==32
    old={s["iden"]:s for s in original}
    new={s["iden"]:s for s in output}
    assert set(old)==set(new)
    changed=0
    unchanged=0
    ids_seen=[]
    for ident,x in old.items():
        y=new[ident]
        assert x["iden"]==y["iden"]
        assert {k:v for k,v in x.items() if k!="bio"}=={k:v for k,v in y.items() if k!="bio"}
        if x["pool"]=="staff" and x["role"]=="headCoach":
            proposed=proposals["curations"][x["teamAbbr"]]
            pid=proposed["portraitId"]
            assert pid in known
            assert gallery["portraitToMarketLabel"][pid]["role"]=="headCoach"
            assert proposed["reviewStatus"]=="PROVISIONAL_VISUAL_MATCH_NEEDS_INGAME_COACH_CARD_QA"
            assert y["bio"].get("portraitId")==pid
            assert {k:v for k,v in x["bio"].items() if k!="portraitId"}=={k:v for k,v in y["bio"].items() if k!="portraitId"}
            assert report["teamSelections"][x["teamAbbr"]]["coach"]==x["forename"]+" "+x["surname"]
            assert report["teamSelections"][x["teamAbbr"]]["inGameEmployedCoachFaceReviewed"] is False
            changed+=(x["bio"].get("portraitId")!=pid)
            ids_seen.append(pid)
        else:
            assert x==y,"Unselected staff, coordinator or free agent changed"
            unchanged+=1
    assert len(ids_seen)==32 and len(set(ids_seen))>=30
    assert changed==report["headCoachCartoonIDsActuallyChangedFromV22"]
    assert unchanged==640
    assert report["laFleurRepair"]["oldPortrait"]=="portrait-0675"
    assert report["laFleurRepair"]["newPortrait"]=="portrait-0484"
    assert report["otherRolesPreserved"]["remaining96OC_DC_STcoaches"]
    assert report["otherRolesPreserved"]["teamScoutsAndDoctors"]
    assert report["otherRolesPreserved"]["freeAgentStaff"]
    assert report["sourceIDsAllSeenInHCMarketVideo"]
    assert "potential" not in json.dumps(report["teamSelections"]).lower()
    print(json.dumps({
        "status":"V25_HC_FACE_SOURCE_AND_STAFF_PRESERVATION_CI_PASS",
        "curatedHC":len(ids_seen),
        "actualPortraitChanges":changed,
        "unselectedStaffIdentical":unchanged,
        "knownSupportedStaffPoolOnly":True,
        "testInGamePending":True
    },indent=2))
if __name__=="__main__":
    main()
