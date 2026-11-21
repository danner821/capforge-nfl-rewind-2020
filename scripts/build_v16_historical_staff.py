#!/usr/bin/env python3
"""V16 experimental 2020 authentic coaching chairs / simulated other staff.

Source-backed identities, not historical staff ratings, ages or contracts.
Creates a separate CapForge staff import; never edits player/teams JSON.
"""
from __future__ import annotations
import copy
import json
import urllib.request
import uuid
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
DATA=ROOT/"data/coaches_2020_preseason.json"
TEAMS=PREVIEW/"teams-2020-roofs-v2.json"
OUT=PREVIEW/"staff-2020-coaching-v16.json"
REPORT=PREVIEW/"v16-coaching-report.json"
SOURCE_STAFF="https://raw.githubusercontent.com/jmansfield96/capforge-custom-rosters/main/staff-files/2018-staff.json"
ROLES=("headCoach","offCoordinator","defCoordinator","specialTeams")
ALL_ROLES=ROLES+("offScout","defScout","teamDoctor")

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

def template():
    req=urllib.request.Request(SOURCE_STAFF,headers={"User-Agent":"CapForge-NFL-Rewind-2020/V16"})
    with urllib.request.urlopen(req,timeout=100) as f:
        payload=json.load(f)
    assert isinstance(payload,list) and len(payload)==672,"Historical staff template layout unexpectedly changed"
    return payload

def main():
    if OUT.exists() or REPORT.exists():
        if not OUT.exists() or not REPORT.exists():
            raise RuntimeError("Partial published V16 assets: refusing to rewrite")
        print("Frozen V16 staff and report already exist; skipping generation")
        return
    source=read(DATA)
    assert source["season"]==2020 and set(source["roles"])==set(ROLES)
    teams=read(TEAMS)["teams"]
    by_abbr={t["abbr"]:t for t in teams}
    assert len(by_abbr)==32 and len(source["teams"])==32
    assert set(by_abbr)==set(source["teams"])
    original=template()
    records=copy.deepcopy(original)
    counts=Counter()
    signed=set()
    assigned=set()
    assigned_ids=set()
    for s in records:
        old_abbr=s.get("teamAbbr")
        if old_abbr=="OAK":
            s["teamAbbr"]="LV"
            s["teamId"]=by_abbr["LV"]["teamId"]
        if s["pool"]=="staff":
            team=s["teamAbbr"]
            role=s["role"]
            assert team in by_abbr and role in ALL_ROLES, "Template's occupied chair changed"
            s["teamId"]=by_abbr[team]["teamId"]
            slot=(team,role)
            assert slot not in assigned, "Multiple coaches assigned to same chair"
            assigned.add(slot)
            if role in ROLES:
                real=source["teams"][team][role]
                first,last=real.split(" ",1)
                s.update(
                    iden=str(uuid.uuid5(uuid.NAMESPACE_URL,
                        "capforge-rewind-2020:coaching:"+team+":"+role+":"+real)).upper(),
                    forename=first,surname=last)
                # Template attributes are fictional, so never imply actual
                # historical headshot/portrait matches; game picks a cartoon.
                s["bio"].pop("portraitId",None)
                # Simulation career origin, not real historical tenure.
                s["bio"]["startSeason"]=2020
                counts[role]+=1
                if slot in {tuple(k.split(":")) for k in source["functionalProxies"]}:
                    assert source["functionalProxies"][team+":"+role]["name"]==real
            else:
                counts["unverified_staff_roles"]+=1
            assigned_ids.add(s["iden"])
        else:
            assert s["pool"]=="freeAgent"
    ids=[s["iden"] for s in records]
    assert len(ids)==len(set(ids)), "Duplicate staff IDs"
    assert len(records)==672 and len(assigned)==32*7
    assert len(assigned_ids)==224
    assert len([x for x in records if x["pool"]=="freeAgent"])==448
    assert all(counts[role]==32 for role in ROLES)
    assert counts["unverified_staff_roles"]==96
    for abbr in by_abbr:
        assert {s["role"] for s in records if s["pool"]=="staff" and s["teamAbbr"]==abbr}==set(ALL_ROLES)
    assert len(source["functionalProxies"])==4
    OUT.write_text(json.dumps(records,separators=(",",":"))+"\n",encoding="utf-8")
    report={
        "status":"EXPERIMENTAL_V16_STAFF_CHAIR_IDENTITIES_SOURCED_GAME_IMPORT_UNTESTED",
        "season":2020,
        "teamCount":32,
        "staffRecords":len(records),
        "occupiedChairs":224,
        "freeAgentStaffRecords":448,
        "verifiedNamedLeadChairs":sum(counts[x] for x in ROLES),
        "leadChairsWithFunctionalProxyTitle":len(source["functionalProxies"]),
        "teamDoctorsAndScoutsNotHistorical":96,
        "otherStaffFreeAgentsModeled":448,
        "teamNameAliases":{"2018 OAK":"2020 LV","2018 WAS":"2020 Washington Football Team"},
        "teamIdIntegrityVerifiedAgainst":TEAMS.name,
        "source_primary":source["source_primary"],
        "source_primary_as_of":source["source_published"],
        "source_template":SOURCE_STAFF,
        "functionalProxyRoles":source["functionalProxies"],
        "otherExceptions":source["otherExceptions"],
        "perTeamLeadership":{abbr:source["teams"][abbr] for abbr in sorted(source["teams"])},
        "limitations":[
            "Only four leadership chair names per team are historical; scouting and doctor identities remain generic model templates.",
            "Four coordinator slots are functional proxies, not formal 2020 OC/DC titles; see proxy list.",
            "2020 role starts are used as an importer base-season marker, not factual hiring dates.",
            "Numeric coach skills, personality, ages, scheme styles, potential and contract terms come from a generic game template; NOT historical facts.",
            "2020 midseason staff changes and interim appointments are not modeled.",
            "Real facial appearance and compatibility of 2020 staff import must be confirmed in disposable CapForge league.",
        ],
        "privacy":"No staff/player hidden individual development values included"
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":report["status"],
        "teams":32,"verified_historical_lead_chair_names":128,
        "formal_role_substitutes":4,
        "fictional_doctor_and_scout_chairs":96,
        "fictional_free_agent_staff":448,
        "export":OUT.name
    },indent=2))

if __name__=="__main__":
    main()
