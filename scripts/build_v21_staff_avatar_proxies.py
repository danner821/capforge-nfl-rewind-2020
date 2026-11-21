#!/usr/bin/env python3
"""V21 staff portrait PILOT: copy only explicit game-accepted player cartoon IDs.

This uses V20 staff (corrected ages) and IDs of named, existing players from
the V19 roster that was accepted by CapForge. Names and avatar proxies are
curated separately; this DOES NOT establish staff-role compatibility or visual
likeness until the user imports a throwaway game and inspects coach faces.
Never invent an avatar ID or infer an identity from generated/default art.
"""
from __future__ import annotations
import copy
import json
import re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
SOURCE=PREVIEW/"staff-2020-coaches-age-qa-v20.json"
PLAYERS=PREVIEW/"players-2020-nine-class-contracts-v19.json"
MAPPINGS=ROOT/"data/coaches_2020_v21_player_avatar_proxies.json"
OUTPUT=PREVIEW/"staff-2020-coach-portrait-proxies-v21.json"
REPORT=PREVIEW/"v21-coach-portrait-proxy-report.json"
ROLES={"headCoach","offCoordinator","defCoordinator","specialTeams"}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Incomplete versioned V21 output; refusing overwrite")
        print("V21 already published/frozen")
        return
    original=load(SOURCE)
    players=load(PLAYERS)
    spec=load(MAPPINGS)
    assert len(original)==672
    assert players["schemaVersion"]==3 and players["meta"]["baseSeason"]==2020
    assert len(players["players"])==6613
    assert spec["version"]=="V21-PILOT"
    assert 1<=len(spec["mappings"])<=32
    pool={}
    for p in players["players"]:
        if p["pool"]=="roster":
            full=p["forename"]+" "+p["surname"]
            pool.setdefault(full,[]).append(p)
    out=copy.deepcopy(original)
    team_roles={(x.get("teamAbbr"),x["role"]):x for x in out if x["pool"]=="staff"}
    assert len(team_roles)==224
    selections={}
    for key,info in spec["mappings"].items():
        abbr,role=key.split(":",1)
        assert role in ROLES
        row=team_roles.get((abbr,role))
        assert row is not None,key
        name=row["forename"]+" "+row["surname"]
        assert name==info["coach"],(key,info["coach"],name)
        assert "portraitId" not in row["bio"],"Unexpected existing curated coach face"
        ref_name=info["referencePlayer"]
        matches=pool.get(ref_name,[])
        assert len(matches)==1,f"Reference player {ref_name} not unambiguous in 2020 approved roster"
        portrait=matches[0]["bio"].get("portraitId")
        assert isinstance(portrait,str) and re.fullmatch(r"portrait-\d{4}",portrait),f"Missing known CapForge player cartoon ID: {ref_name}"
        row["bio"]["portraitId"]=portrait
        selections[key]={
            "coach":name,"referencePlayer":ref_name,"portraitId":portrait,
            "reviewStatus":"UNVERIFIED_STAFF_CARTOON_APPROXIMATION_NEEDS_GAME_VISUAL_REVIEW"
        }
    prev={x["iden"]:x for x in original}
    assert len(prev)==len({x["iden"] for x in out})==672
    for s in out:
        old=prev[s["iden"]]
        slot=(s.get("teamAbbr"),s["role"])
        if s["pool"]=="staff" and slot[0]+":"+slot[1] in selections:
            stripped_old=copy.deepcopy(old)
            stripped_new=copy.deepcopy(s)
            stripped_old["bio"].pop("portraitId",None)
            stripped_new["bio"].pop("portraitId",None)
            assert stripped_old==stripped_new, "Only portrait ID may change for selected coach"
        else:
            assert s==old,"Non-selected staff record changed"
    assert len([s for s in out if s["pool"]=="staff"])==224
    assert len([s for s in out if s["pool"]=="freeAgent"])==448
    assert sum(s["pool"]=="staff" and s["role"] in ROLES and s["bio"].get("portraitId") is not None for s in out)==len(selections)
    OUTPUT.write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf-8")
    report={
        "status":"V21_SOURCE_PLAYER_IDS_ASSIGNED_STAFF_COMPATIBILITY_AND_LIKENESS_UNVERIFIED",
        "sourceStaffFile":SOURCE.name,
        "sourcePlayerFile":PLAYERS.name,
        "outputStaffFile":OUTPUT.name,
        "version":"V21-PILOT",
        "coachSlots":128,
        "coachPortraitProxyAssignments":len(selections),
        "unreviewedDefaultCoachPortraits":128-len(selections),
        "assignments":selections,
        "staffRowCount":672,
        "allCoachNamesRolesTeamsIdentifiersPreserved":True,
        "allCoachAgesSkillsPersonalityContractsPreserved":True,
        "scoutsDoctorsFreeAgentsPreserved":True,
        "playerRostersTeamsAndDraftClassesUntouched":True,
        "uncertainty":[
          "Player portrait IDs have passed CapForge Player import; that does not guarantee Coach importer allows or correctly renders them.",
          "Resemblance is a proposed human-selected approximation, not based on visually comparing actual CapForge art.",
          "This pilot targets seven known named 2020 head coaches; other 121 coaching chairs keep CapForge default avatars.",
          "Do not call this a final portrait correction until a disposable-game import and face review pass.",
          "Keep V16 (in-game green) and V20 (age corrected) as separate fallbacks. Never update saves in-place.",
        ],
        "nextInGameCheck":"Create NEW disposable 2020 game with Players V19, Teams V2, Staff V21. Confirm Staff green, then view Green Bay head coach Matt LaFleur first, and other six coach cards. Report any wrong face or warning."
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
       "status":report["status"],
       "testedSourcePlayerReferences":len(selections),
       "mapped":selections,
       "otherCoachPortraitsDefault":128-len(selections),
       "scoutsDoctorsFreeAgentsUnchanged":True,
    },indent=2))

if __name__=="__main__":main()
