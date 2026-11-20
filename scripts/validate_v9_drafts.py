#!/usr/bin/env python3
"""Spoiler-free V9 structural/regression checks; no individual player output."""
import json
from collections import Counter
from pathlib import Path
from capforge_ovr import estimate

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
BASE=PREVIEW/"players-2020-six-class-history-v8.json"
SIX=PREVIEW/"players-2020-six-class-authentic-v9.json"
FOUR=PREVIEW/"players-2020-four-class-authentic-v9.json"
REPORT=PREVIEW/"v9-draft-pool-report.json"
YEARS=range(2021,2027)

def load(path):
    d=json.loads(path.read_text())
    assert d["schemaVersion"]==3 and d["meta"]["baseSeason"]==2020
    assert d["deadCap"]==[]
    return d["players"]

def class_sizes(players):
    return Counter(int(p["bio"]["draftSeason"]) for p in players if p["pool"]=="draftClass")

def audit():
    base=load(BASE)
    six=load(SIX)
    four=load(FOUR)
    report=json.loads(REPORT.read_text())
    assert report["status"]=="EXPERIMENTAL_NOT_VERIFIED_IN_CAPFORGE"
    assert len(base)==4180 and len(six)==2293+480*6
    assert len(four)==2293+480*4
    original_by_id={p["iden"]:p for p in base}
    assert len(original_by_id)==len(base)
    v9_by_id={p["iden"]:p for p in six}
    assert len(v9_by_id)==len(six), "duplicate V9 player ID"
    # Every 2020 player, old draft player, portrait assignment, rating, team,
    # contract AND hidden development record must survive unchanged.
    assert all(v9_by_id.get(i)==p for i,p in original_by_id.items()),"V8 player changed"
    four_ids={p["iden"] for p in four}
    assert len(four_ids)==len(four)
    assert {p["iden"] for p in six if p["pool"]=="roster" or p["bio"]["draftSeason"]<=2024}==four_ids
    assert all(v9_by_id[p["iden"]]==p for p in four)
    for y in YEARS:
        assert class_sizes(six)[y]==480,f"Incomplete class: {y}"
        if y<=2024:assert class_sizes(four)[y]==480
    assert set(class_sizes(four))==set(range(2021,2025))
    added=[p for p in six if p["iden"] not in original_by_id]
    duplicates=set()
    for p in six:
        if p["pool"]=="draftClass":
            key=(p["bio"]["draftSeason"],p["forename"].casefold(),p["surname"].casefold())
            assert key not in duplicates,"Duplicate player identity within class"
            duplicates.add(key)
    for p in added:
        assert p["pool"]=="draftClass"
        assert not p.get("teamId") and not p.get("teamAbbr"),"Future player preassigned to NFL team"
        assert "portraitId" not in p["bio"],"Unverified generated portrait"
        assert p["position"] in ("QB","RB","WR","TE","OT","OG","C","EDGE","DE","DT","LB","CB","S","K","P")
        assert len(p["ratings"])>=8
        assert abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])<=2
        assert p["development"]["potential"]>=p["development"]["ovr"]
    assert all(len({p["teamAbbr"] for p in six if p["pool"]=="roster"})==32 for _ in [0])
    assert sum(row["fictional_depth_added"] for row in report["classes"].values())==sum(
        p["bio"]["college"]=="Fictional Depth Pool" for p in added
    )
    print(json.dumps({
        "status":"V9_STRUCTURE_VALIDATED_NOT_GAME_TESTED",
        "startingRosterUnchanged":2293,
        "v8RecordsPreserved":len(base),
        "fourClassExport":len(four),
        "sixClassExport":len(six),
        "classCounts":{str(y):class_sizes(six)[y] for y in YEARS},
        "fictionalDepthSlots":sum(row["fictional_depth_added"] for row in report["classes"].values())
    },indent=2))
if __name__=="__main__":
    audit()
