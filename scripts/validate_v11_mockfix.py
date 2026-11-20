#!/usr/bin/env python3
"""V11 spoiler-free regression checks for actual reported in-game errors."""
import copy
import json
from collections import Counter
from pathlib import Path
from audit_draft_classes import norm
from build_v11_mockfix import CONSENSUS_2027, canonical
from capforge_ovr import estimate

ROOT=Path(__file__).resolve().parents[1]/"preview"
V9=ROOT/"players-2020-six-class-authentic-v9.json"
V10=ROOT/"players-2020-nine-class-projection-v10.json"
V11_NINE=ROOT/"players-2020-nine-class-mockfix-v11.json"
V11_SEVEN=ROOT/"players-2020-seven-class-mockfix-v11.json"
REPORT=ROOT/"v11-draft-corrections-report.json"

def read(path):
    j=json.loads(path.read_text())
    assert j["schemaVersion"]==3 and j["meta"]["baseSeason"]==2020
    assert j["deadCap"]==[]
    return j["players"]

def key(p):
    return canonical(p["forename"]+" "+p["surname"])

def run():
    old=read(V9); prev=read(V10); new=read(V11_NINE); seven=read(V11_SEVEN)
    report=json.loads(REPORT.read_text())
    assert len(old)==5173 and len(prev)==6613 and len(new)==6613 and len(seven)==5653
    assert len({p["iden"] for p in new})==len(new),"Duplicate UUID"
    assert len({p["iden"] for p in seven})==len(seven),"Duplicate seven-year UUID"
    oldidx={p["iden"]:p for p in old}
    now={p["iden"]:p for p in new}
    assert len(oldidx)==len(old)
    modified=[]
    for oldid,p in oldidx.items():
        q=now.get(oldid)
        assert q is not None,"V9 record missing"
        if q!=p:
            pcopy=copy.deepcopy(p)
            pcopy["bio"]["weightLbs"]=400
            assert pcopy==q and key(p)=="desmondwatson","Unexpected V9 change"
            modified.append(key(p))
    assert modified==["desmondwatson"],modified
    for year in range(2021,2030):
        rec=[p for p in new if p["pool"]=="draftClass" and p["bio"]["draftSeason"]==year]
        assert len(rec)==480,f"{year} draft count {len(rec)}"
        assert len({key(p) for p in rec})==480,f"{year} duplicate names"
    assert len([p for p in new if p["pool"]=="roster"])==2293
    assert len([p for p in seven if p["pool"]=="roster"])==2293
    assert {p["iden"] for p in seven}=={p["iden"] for p in new if p["pool"]=="roster" or p["bio"]["draftSeason"]<=2027}
    assert all(p==now[p["iden"]] for p in seven)
    assert all(p["bio"].get("weightLbs",0)<=400 for p in new)
    allnames={key(p):p for p in new if p["pool"]=="draftClass" and p["bio"]["draftSeason"]==2027}
    for name,pos,school in CONSENSUS_2027:
        p=allnames.get(canonical(name))
        assert p is not None,f"Missing current-mock prospect: {name}"
        assert p["position"]==pos,f"Wrong 2027 position: {name}"
        assert p["bio"]["college"]==school,f"Wrong 2027 school: {name}"
        assert p["bio"]["draftSeason"]==2027
    assert all(p.get("teamAbbr") is None and p.get("teamId") is None for p in new if p["pool"]=="draftClass")
    arch=allnames["archmanning"]
    assert arch["position"]=="QB" and arch["bio"].get("portraitId"),"Arch still generic portrait"
    for name in ("cjcarr","drewmestemaker"):
        assert allnames[name]["bio"].get("portraitId"),f"QB portrait not curated: {name}"
    dylan=allnames["dylanstewart"]
    assert dylan["position"]=="EDGE" and dylan["development"]["ovr"]<=77, "Game warning not repaired"
    by_id={p["iden"]:p for p in new}
    new_players=[p for p in new if p["iden"] not in oldidx]
    for p in new_players:
        if p["pool"]=="draftClass" and p["bio"]["draftSeason"]>=2027:
            assert abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])<=2.0, "Unreachable projected OVR"
    assert report["2027_consensus_represented"]==len(CONSENSUS_2027)
    print(json.dumps({
      "result":"V11_SCHEMA_AND_REGRESSION_PASSED_APP_TEST_REQUIRED",
      "2020Roster":2293,
      "2021_to_2029_class_count":9,
      "prospects_each_year":480,
      "current_2027_consensus_matched":len(CONSENSUS_2027),
      "previous_version_2020_team_ratings_preserved":True,
      "expected_v9_metadata_correction":"one 2024 player body weight capped to 400",
      "observed_2027_game_ovr_warning_corrected":True,
      "QB_cartoon_portraits_curated":3,
      "seven_year_total":len(seven),"nine_year_total":len(new),
      "game_verification":"NOT_YET_TESTED"
    },indent=2))
if __name__=="__main__":
    run()
