#!/usr/bin/env python3
"""V16 historic coaching names, CapForge staff shape, team ID and audit checks."""
import json
from collections import Counter
from pathlib import Path

from build_v16_historical_staff import DATA,TEAMS,OUT,REPORT,ROLES,ALL_ROLES

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    rows=read(OUT)
    report=read(REPORT)
    source=read(DATA)
    teams={t["abbr"]:t for t in read(TEAMS)["teams"]}
    assert len(rows)==672 and len({s["iden"] for s in rows})==672
    assert len(source["teams"])==len(teams)==32
    assert report["status"]=="EXPERIMENTAL_V16_STAFF_CHAIR_IDENTITIES_SOURCED_GAME_IMPORT_UNTESTED"
    assert report["staffRecords"]==672 and report["verifiedNamedLeadChairs"]==128
    assigned=[s for s in rows if s["pool"]=="staff"]
    free=[s for s in rows if s["pool"]=="freeAgent"]
    assert len(assigned)==224 and len(free)==448
    assert all(not s.get("teamAbbr") and not s.get("teamId") for s in free)
    slots=Counter((s["teamAbbr"],s["role"]) for s in assigned)
    assert len(slots)==224 and all(n==1 for n in slots.values())
    for abbr,t in teams.items():
        byrole={s["role"]:s for s in assigned if s["teamAbbr"]==abbr}
        assert set(byrole)==set(ALL_ROLES),abbr
        assert all(s["teamId"]==t["teamId"] for s in byrole.values())
        for role in ROLES:
            s=byrole[role]
            assert s["forename"]+" "+s["surname"]==source["teams"][abbr][role],(abbr,role)
            assert not s["bio"].get("portraitId"),"Unverified coach headshot leaked"
            assert s["bio"]["startSeason"]==2020
            assert s["pool"]=="staff"
            assert set(s["skills"]) and isinstance(s["personality"],dict)
            assert isinstance(s["development"],dict)
            assert isinstance(s["contract"],dict)
            assert s["contract"]["years"]>=1
    assert len(source["functionalProxies"])==4
    for slot, proxy in source["functionalProxies"].items():
        abbr,role=slot.split(":")
        assert role in ROLES and abbr in teams
        assert source["teams"][abbr][role]==proxy["name"]
        assert proxy["actual_title"] and proxy["source"].startswith("https://")
    assert report["teamDoctorsAndScoutsNotHistorical"]==96
    assert report["otherStaffFreeAgentsModeled"]==448
    assert "midseason" in " ".join(report["limitations"])
    assert report["privacy"].startswith("No staff/player hidden")
    print(json.dumps({"result":"V16_STAFF_STRUCTURE_CI_PASSED_GAME_IMPORT_PENDING",
       "teams":32,"historical_chairs":128,"functional_proxies":4,
       "other_staff_roles_modeled":96,"free_agents_modeled":448},indent=2))
if __name__=="__main__":
    main()
