#!/usr/bin/env python3
"""V21 staff proxy QA: known player art IDs, exact preserved attributes."""
import json
import re
from collections import Counter
from build_v21_staff_avatar_proxies import SOURCE,PLAYERS,MAPPINGS,OUTPUT,REPORT,load

def main():
    before=load(SOURCE)
    after=load(OUTPUT)
    report=load(REPORT)
    spec=load(MAPPINGS)
    player_roster=load(PLAYERS)["players"]
    assert len(before)==len(after)==672
    assert report["coachPortraitProxyAssignments"]==len(spec["mappings"])
    assert report["status"]=="V21_SOURCE_PLAYER_IDS_ASSIGNED_STAFF_COMPATIBILITY_AND_LIKENESS_UNVERIFIED"
    assert report["staffRowCount"]==672
    assert report["allCoachNamesRolesTeamsIdentifiersPreserved"] is True
    assert report["scoutsDoctorsFreeAgentsPreserved"] is True
    before_ids={x["iden"]:x for x in before}
    refids={}
    for p in player_roster:
        if p["pool"]=="roster":
            name=p["forename"]+" "+p["surname"]
            if p["bio"].get("portraitId"):refids[name]=p["bio"]["portraitId"]
    selected=0
    for item in after:
        assert item["iden"] in before_ids
        prev=before_ids[item["iden"]]
        ref={k:v for k,v in prev.items() if k!="bio"}
        got={k:v for k,v in item.items() if k!="bio"}
        assert ref==got,"Coach identity/team/staff attributes or contracts changed"
        oldbio=prev["bio"]
        newbio=item["bio"]
        slot=f'{item.get("teamAbbr")}:{item["role"]}'
        if slot in spec["mappings"]:
            m=spec["mappings"][slot]
            assert item["forename"]+" "+item["surname"]==m["coach"]
            assert m["referencePlayer"] in refids
            expected=refids[m["referencePlayer"]]
            assert newbio.get("portraitId")==expected
            assert report["assignments"][slot]["portraitId"]==expected
            assert re.fullmatch(r"portrait-\d{4}",expected)
            assert {k:v for k,v in oldbio.items() if k!="portraitId"}=={k:v for k,v in newbio.items() if k!="portraitId"}
            selected+=1
        else:
            assert oldbio==newbio,"Unselected coach/scout/doctor/free-agent record changed"
    assert selected==len(spec["mappings"])==7
    assert report["unreviewedDefaultCoachPortraits"]==128-selected
    assert ("GB:headCoach" in report["assignments"] and
            report["assignments"]["GB:headCoach"]["coach"]=="Matt LaFleur")
    assert "UNVERIFIED" in report["status"]
    print(json.dumps({
       "result":"V21_STRUCTURAL_PASS_COACH_PORTRAIT_LIKENESS_REQUIRES_GAME",
       "sourcePlayerAvatarsReused":selected,
       "protectedStaffRecords":672-selected,
       "reportedBadLaFleurDefaultReplacedWith":report["assignments"]["GB:headCoach"]["referencePlayer"],
       "gameCompatibility":"NOT_VERIFIED",
    },indent=2))

if __name__=="__main__":main()
