#!/usr/bin/env python3
"""Validate V10 projected classes without exposing hidden player attributes."""
import json
from collections import Counter
from pathlib import Path
from capforge_ovr import estimate
ROOT=Path(__file__).resolve().parents[1]/"preview"
BASE=ROOT/"players-2020-six-class-authentic-v9.json"
SEVEN=ROOT/"players-2020-seven-class-projection-v10.json"
NINE=ROOT/"players-2020-nine-class-projection-v10.json"
REPORT=ROOT/"v10-projection-report.json"

def read(path):
    d=json.loads(path.read_text())
    assert d["schemaVersion"]==3
    assert d["meta"]["baseSeason"]==2020
    assert d["deadCap"]==[]
    return d["players"]

def check():
    base=read(BASE); seven=read(SEVEN); nine=read(NINE)
    report=json.loads(REPORT.read_text())
    assert report["status"]=="EXPERIMENTAL_FUTURE_DRAFT_PROJECTIONS_NOT_GAME_TESTED"
    assert len(base)==5173
    assert len(seven)==5653
    assert len(nine)==6613
    ids={p["iden"]:p for p in base}
    assert len(ids)==len(base)
    seven_ids={p["iden"]:p for p in seven}
    nine_ids={p["iden"]:p for p in nine}
    assert len(seven_ids)==len(seven) and len(nine_ids)==len(nine)
    assert all(seven_ids.get(k)==v and nine_ids.get(k)==v for k,v in ids.items()), "V9 player data changed"
    assert all(nine_ids.get(k)==v for k,v in seven_ids.items()),"Seven-year players differ from nine-year version"
    def years(players):
        return Counter(p["bio"]["draftSeason"] for p in players if p["pool"]=="draftClass")
    assert years(seven)==dict.fromkeys(range(2021,2028),480)
    assert years(nine)==dict.fromkeys(range(2021,2030),480)
    new=[p for p in nine if p["iden"] not in ids]
    assert len(new)==1440
    seen=set()
    for p in nine:
        if p["pool"]=="draftClass":
            key=(p["bio"]["draftSeason"],p["forename"].lower(),p["surname"].lower())
            assert key not in seen, "Repeated prospect in draft year"
            seen.add(key)
    for p in new:
        assert p["pool"]=="draftClass"
        assert p["bio"]["draftSeason"] in (2027,2028,2029)
        assert not p.get("teamAbbr") and not p.get("teamId")
        assert "portraitId" not in p["bio"]
        assert p["contract"]["salary"]==0
        assert abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])<=2
        assert p["development"]["potential"]>=p["development"]["ovr"]
        assert p["bio"]["college"] and p["bio"]["college"]!="Fictional Depth Pool"
    assert all(v["fictional_added"]==0 for v in report["projectedYears"].values())
    print(json.dumps({
      "status":"V10_STRUCTURAL_VALIDATION_PASSED_APP_TEST_REQUIRED",
      "2020Roster":2293,"originalV9RecordsUnchanged":len(base),
      "sevenClassFilePlayers":len(seven),"nineClassFilePlayers":len(nine),
      "newRealCollegeNames":len(new),"projectedDraftYears":[2027,2028,2029],
      "noHiddenPlayerValuesPrinted":True
    },indent=2))

if __name__=="__main__":check()
