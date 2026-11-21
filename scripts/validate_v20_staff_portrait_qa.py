#!/usr/bin/env python3
"""V20 staff schema, historical age correction, and portrait provenance checks."""
from __future__ import annotations
import copy
import json
from collections import Counter
from datetime import date
from build_v20_staff_portrait_qa import BASE,OUTPUT,REPORT,BIRTHDATES,OVERRIDES,ROLES,age_on,read

def main():
    old=read(BASE)
    now=read(OUTPUT)
    audit=read(REPORT)
    source=read(BIRTHDATES)
    overrides=read(OVERRIDES)["verifiedOverrides"]
    assert len(old)==len(now)==672
    assert audit["status"]=="V20_STAFF_AGE_FIXES_CI_ONLY_PORTRAIT_LIKENESS_NOT_VERIFIED"
    assert len(source["teams"])==32
    assert len({x["iden"] for x in now})==672
    prior={s["iden"]:s for s in old}
    next_={s["iden"]:s for s in now}
    assert set(prior)==set(next_)
    assert len([s for s in now if s["pool"]=="staff"])==224
    assert len([s for s in now if s["pool"]=="freeAgent"])==448
    changed_heads=0
    for ident,s in prior.items():
        t=next_[ident]
        assert (s["forename"],s["surname"],s["role"],s["pool"],s.get("teamAbbr"),s.get("teamId"))==(t["forename"],t["surname"],t["role"],t["pool"],t.get("teamAbbr"),t.get("teamId"))
        assert {k:v for k,v in s.items() if k!="bio"}=={k:v for k,v in t.items() if k!="bio"}
        if s["pool"]=="staff" and s["role"]=="headCoach":
            d=source["teams"][s["teamAbbr"]]
            assert d["name"]==s["forename"]+" "+s["surname"]
            age=age_on(date.fromisoformat(d["birthDate"]),date(2020,9,10))
            assert t["bio"]["age"]==age
            changed_heads+=(t["bio"]["age"]!=s["bio"]["age"])
        else:
            assert t["bio"]["age"]==s["bio"]["age"],"An assistant/scout/doctor/free agent's age changed"
        assert t["bio"].get("startSeason")==s["bio"].get("startSeason")
        if s["pool"]=="staff" and s["role"] in ROLES and s["teamAbbr"] in overrides and s["role"] in overrides[s["teamAbbr"]]:
            m=overrides[s["teamAbbr"]][s["role"]]
            assert t["bio"]["portraitId"]==m["portraitId"]
            assert m["name"]==s["forename"]+" "+s["surname"]
            assert m["evidence"].startswith(("screenshot:","app-picker:"))
        else:
            assert t["bio"].get("portraitId")==s["bio"].get("portraitId"),"An unverified portrait was assigned"
    assert changed_heads==audit["historicalHeadCoachAgeCorrections"]
    assert changed_heads>=20
    assert audit["verifiedCustomCoachPortraitsAdded"]==sum(len(x) for x in overrides.values())
    assert audit["coachPositionsAwaitingVisualPortraitVerification"]+audit["verifiedCustomCoachPortraitsAdded"]==128
    assert audit["unchanged"]["96ScoutsAndDoctors"] and audit["unchanged"]["448FreeAgentStaff"]
    print(json.dumps({
      "status":"V20_STAFF_CI_PASS_VISUAL_QA_STILL_REQUIRED",
      "coachingChairs":128,
      "headCoachHistoricalAgeCorrections":changed_heads,
      "portraitMappingsSupportedByInGameEvidence":audit["verifiedCustomCoachPortraitsAdded"],
      "allScoutsDoctorsFreeAgentsIdenticalToV16":True
    },indent=2))

if __name__=="__main__":
    main()
