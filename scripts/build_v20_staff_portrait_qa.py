#!/usr/bin/env python3
"""V20 staff QA: source-backed 2020 head-coach ages and verified portraits only.

Preserve user-validated V16 import layout and identities. All 32 HCs receive
historical kickoff ages. Portrait IDs are assigned only after a screenshot of
a specific CapForge built-in cartoon has been approved. Until then this file
retains CapForge default-generated coach portraits; never guess numeric IDs.
Scouts, doctors, free agents and all non-HC coaches remain unchanged.
"""
from __future__ import annotations
import copy
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
BASE=PREVIEW/"staff-2020-coaching-v16.json"
OUTPUT=PREVIEW/"staff-2020-coaches-age-qa-v20.json"
REPORT=PREVIEW/"v20-staff-portrait-qa-report.json"
BIRTHDATES=ROOT/"data/coaches_2020_head_coach_birthdates.json"
OVERRIDES=ROOT/"data/coaches_2020_portrait_overrides.json"
ROLES={"headCoach","offCoordinator","defCoordinator","specialTeams"}
ALL_ROLES=ROLES|{"offScout","defScout","teamDoctor"}

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def age_on(birth,when):
    return when.year-birth.year-((when.month,when.day)<(birth.month,birth.day))

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Partial frozen V20 assets: refusing to overwrite")
        print("Frozen V20 staff assets already exist; skipping generation")
        return
    baseline=read(BASE)
    source=read(BIRTHDATES)
    choices=read(OVERRIDES)
    assert source["season"]==2020 and len(source["teams"])==32
    when=date.fromisoformat(source["asOf"])
    assert when==date(2020,9,10)
    assert isinstance(choices["verifiedOverrides"],dict)
    roster=copy.deepcopy(baseline)
    assert len(roster)==672
    before_by_id={s["iden"]:s for s in baseline}
    after_by_id={s["iden"]:s for s in roster}
    assert len(before_by_id)==len(after_by_id)==672
    head_coaches={}
    slots=set()
    for s in roster:
        if s["pool"]!="staff":
            assert s["pool"]=="freeAgent"
            continue
        role=s["role"]
        abbr=s["teamAbbr"]
        assert role in ALL_ROLES
        assert (abbr,role) not in slots
        slots.add((abbr,role))
        if role=="headCoach":
            assert abbr not in head_coaches
            person=source["teams"][abbr]
            name=s["forename"]+" "+s["surname"]
            assert name==person["name"],f"Birthdate is for different coach: {abbr} {name}"
            birthday=date.fromisoformat(person["birthDate"])
            historical=age_on(birthday,when)
            assert 30<=historical<=80, f"Unexpected head coach age: {name}"
            head_coaches[abbr]={"name":name,"age2020":historical,"originalTemplateAge":s["bio"]["age"]}
            s["bio"]["age"]=historical
    assert len(head_coaches)==32
    assert len(slots)==32*7

    overrides=choices["verifiedOverrides"]
    applied=[]
    for abbr,roles in overrides.items():
        assert abbr in source["teams"]
        assert isinstance(roles,dict)
        for role,entry in roles.items():
            assert role in ROLES and isinstance(entry,dict)
            name=entry["name"]
            portrait=entry["portraitId"]
            evidence=entry["evidence"]
            assert isinstance(evidence,str) and evidence.strip().startswith(("screenshot:","app-picker:"))
            assert re.fullmatch(r"portrait-\d{4}",portrait), "Not a CapForge portrait ID"
            matches=[s for s in roster if s["pool"]=="staff" and s["teamAbbr"]==abbr and s["role"]==role]
            assert len(matches)==1
            s=matches[0]
            assert s["forename"]+" "+s["surname"]==name, "Portrait mapping names wrong coach"
            # Never infer validity from the number alone: evidence is required
            # to show this exact ID in the actual CapForge portrait picker.
            assert int(portrait.split("-")[1])>=1
            s["bio"]["portraitId"]=portrait
            applied.append((abbr,role))
    assert len(applied)==len(set(applied))
    assert len(roster)==672 and len({p["iden"] for p in roster})==672
    assert len({(s["teamAbbr"],s["role"]) for s in roster if s["pool"]=="staff"})==224
    hcs_with_age_changes=0
    for s in roster:
        old=before_by_id[s["iden"]]
        if s["pool"]=="staff" and s["role"]=="headCoach":
            if s["bio"]["age"]!=old["bio"]["age"]:
                hcs_with_age_changes+=1
        expected=copy.deepcopy(old)
        if s["pool"]=="staff" and s["role"]=="headCoach":
            expected["bio"]["age"]=head_coaches[s["teamAbbr"]]["age2020"]
        if (s.get("teamAbbr"),s.get("role")) in applied:
            match=overrides[s["teamAbbr"]][s["role"]]
            expected["bio"]["portraitId"]=match["portraitId"]
        assert s==expected,"Unexpected change to identity, role, traits or untouched personnel"
    assert hcs_with_age_changes>=20,"Template ages unexpectedly already authentic"
    explicit={r:0 for r in sorted(ROLES)}
    for s in roster:
        if s["pool"]=="staff" and s["role"] in ROLES and s["bio"].get("portraitId"):
            explicit[s["role"]]+=1
    OUTPUT.write_text(json.dumps(roster,separators=(",",":"))+"\n",encoding="utf-8")
    report={
        "status":"V20_STAFF_AGE_FIXES_CI_ONLY_PORTRAIT_LIKENESS_NOT_VERIFIED",
        "baseStaffFile":BASE.name,
        "staffFile":OUTPUT.name,
        "baselineStaffCount":len(baseline),
        "occupiedCoachAndPersonnelChairs":len(slots),
        "teams":32,
        "publicSourceForHeadCoachBirthdates":source["source"],
        "ageAsOf":source["asOf"],
        "historicalHeadCoachAgeCorrections":hcs_with_age_changes,
        "historicalHeadCoachAges":{abbr:head_coaches[abbr]["age2020"] for abbr in sorted(head_coaches)},
        "verifiedCustomCoachPortraitsAdded":len(applied),
        "explicitPortraitIdsByCoachRole":explicit,
        "coachPositionsAwaitingVisualPortraitVerification":128-len(applied),
        "portraitPolicy":choices["policy"],
        "inGameOutcome":"V16 staff import was green for user, but V20 staff age import and visual portrait match not yet checked in app",
        "unchanged":{
            "staffIdentitiesAndUUIDs":True,
            "allCoachingNamesAndTeamIds":True,
            "allSkillsAndContractTerms":True,
            "96ScoutsAndDoctors":True,
            "448FreeAgentStaff":True,
            "2020PlayersAnd2021To2029DraftClasses":True,
        },
        "limitations":[
            "Corrected head-coach ages do not imply that CapForge automatically selects more accurate portraits.",
            "No proof of coach-specific similarity is possible from the source JSON alone; needs real CapForge avatar-picker screenshots to curate specific IDs.",
            "Assistant-coach ages remain inherited from fictional V16 template until source-backed dates are verified.",
            "Staff default portraits are still used for uncurated coaches, not real-life photo portraits.",
            "Actual V20 CapForge game validation and visual QA are pending."
        ]
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
       "status":report["status"],
       "headCoachAgesCorrected":hcs_with_age_changes,
       "verifiedPortraitsAdded":len(applied),
       "waitingForVisualPortraitIds":128-len(applied),
       "teams":32,
       "scoutsAndDoctorsUntouched":True,
       "totalStaff":len(roster)
    },indent=2))
if __name__=="__main__":
    main()
