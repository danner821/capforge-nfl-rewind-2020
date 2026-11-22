#!/usr/bin/env python3
"""Independent V34 trade-exploit regression: pick provenance only."""
from __future__ import annotations
import collections,hashlib,json
from build_v34_verified_draft_history import SOURCE,OUTPUT,REPORT,NFL,valid_source,norm
def main():
    a=json.loads(SOURCE.read_text())
    b=json.loads(OUTPUT.read_text())
    rep=json.loads(REPORT.read_text())
    assert rep["status"]=="V34_PFR_DRAFT_HISTORY_REPAIRED_IMPORT_CANDIDATE_NOT_YET_TESTED_INSIDE_GAME"
    assert len(a["players"])==len(b["players"])==6613
    assert a["meta"]==b["meta"]=={"baseSeason":2020}
    assert a["deadCap"]==b["deadCap"]==[]
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==rep["sourceV30SHA256"]
    index,_=valid_source()
    modified=0
    rookie=0
    years=collections.Counter()
    pcount=collections.Counter()
    for old,new in zip(a["players"],b["players"]):
        assert old["iden"]==new["iden"] and old["pool"]==new["pool"]
        if old["pool"]=="draftClass":
            assert old==new
            assert new["bio"]["draftNum"]==-1
            years[new["bio"]["draftSeason"]]+=1
            continue
        assert old["pool"]=="roster"
        assert {k:v for k,v in old.items() if k!="bio"}=={k:v for k,v in new.items() if k!="bio"}
        assert {k:v for k,v in old["bio"].items() if k!="draftNum"}=={k:v for k,v in new["bio"].items() if k!="draftNum"}
        assert old["development"]==new["development"]
        assert old["ratings"]==new["ratings"]
        assert old["contract"]==new["contract"]
        if old["bio"]["draftNum"]!=new["bio"]["draftNum"]:
            y=new["bio"]["draftSeason"]
            pick=new["bio"]["draftNum"]
            assert old["bio"]["draftNum"]==-1 and 1<=pick<=300
            name=norm(new["forename"]+" "+new["surname"])
            assert any(int(x["pick"])==pick for x in index.get((y,name),[]))
            modified+=1
            if y==2020:rookie+=1
        pcount[new["teamAbbr"]]+=1
    assert modified==rep["allHistoricalRosterDraftNumbersCorrected"] and modified>1200
    assert rookie==rep["2020RookieDraftNumbersCorrected"] and rookie>=135
    assert sum(pcount.values())==2293 and len(pcount)==32
    assert sum(years.values())==4320 and all(years[y]==480 for y in range(2021,2030))
    assert rep["potentialDisplayConcern"]["underlyingDevelopmentValuesUnchangedByV34"]
    assert not rep["potentialDisplayConcern"]["actualGamePotentialDisplayCorrectionConfirmed"]
    assert '"potential":' not in REPORT.read_text()
    assert '"progressionCurve":' not in REPORT.read_text()
    print(json.dumps({"status":"V34_HISTORICAL_DRAFT_PICK_REGRESSION_GREEN_CI_NOT_GAME", "startingRosters":sum(pcount.values()),"verifiedRealDraftNumbers":modified,"2020Rookies":rookie,"futureProspectsPreserved":sum(years.values()),"potentialAndSalaryUnchanged":True},indent=2))
if __name__=="__main__":main()
