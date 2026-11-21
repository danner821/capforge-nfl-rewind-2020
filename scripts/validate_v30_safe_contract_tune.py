#!/usr/bin/env python3
"""Independent V30 contract-only / protected draft and cap guardrail tests."""
from __future__ import annotations
import collections
import hashlib
import json
from build_v30_safe_contract_tune import (
 SOURCE,OUTPUT,REPORT,V27,V29,V19_SHA256,MIN_SALARY,
 MAX_MODELED_OPENING,MIN_OBSERVED_2020_SPACE_AFTER_DELTA_M,CAP
)

def main():
    a=json.loads(SOURCE.read_text())
    b=json.loads(OUTPUT.read_text())
    report=json.loads(REPORT.read_text())
    old=json.loads(V27.read_text())
    v29=json.loads(V29.read_text())
    assert report["status"]=="V30_CONTRACTS_CALIBRATED_STRUCTURAL_TEST_READY_FOR_GAME_NOT_GAME_APPROVED"
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==report["frozenV19SHA256"]==V19_SHA256
    assert len(a["players"])==len(b["players"])==6613
    assert a["meta"]==b["meta"]=={"baseSeason":2020}
    assert a["deadCap"]==b["deadCap"]==[]
    assert report["playersInInitialRoster"]==2293
    assert report["protectedFutureProspects"]==4320
    assert len(report["teamAggregate"])==32
    count=collections.Counter()
    changed=0
    financials=collections.defaultdict(lambda:collections.Counter())
    for x,y in zip(a["players"],b["players"]):
        assert x["iden"]==y["iden"]
        if x["pool"]=="draftClass":
            assert x==y
            count[x["bio"]["draftSeason"]]+=1
            continue
        assert x["pool"]==y["pool"]=="roster"
        assert {k:v for k,v in x.items() if k!="contract"}=={
            k:v for k,v in y.items() if k!="contract"}
        oldc=x["contract"]
        c=y["contract"]
        assert c["years"]==oldc["years"]
        assert c["signedSeason"]==2020 and c["currentYearIndex"]==0
        assert c["salary"]==c["salaryByYear"][0]
        assert c["guarantee"]==c["currentGuarantee"]==c["guaranteeByYear"][0]
        assert c["extension"]==oldc["extension"]=={"salary":0,"guarantee":0,"years":0}
        assert len(c["salaryByYear"])==len(c["bonusByYear"])==len(c["guaranteeByYear"])==c["years"]
        for i in range(c["years"]):
            assert MIN_SALARY<=c["salaryByYear"][i]<=round(oldc["salaryByYear"][i]*1.28)+1000
            assert 0<=c["bonusByYear"][i]<=round(oldc["bonusByYear"][i]*1.28)+1000
            assert 0<=c["guaranteeByYear"][i]<=c["salaryByYear"][i]
            assert c["salaryByYear"][i]>=oldc["salaryByYear"][i]
            assert c["bonusByYear"][i]>=oldc["bonusByYear"][i]
            assert c["guaranteeByYear"][i]>=oldc["guaranteeByYear"][i]
            assert all(c[z][i]%1000==0 for z in ("salaryByYear","bonusByYear","guaranteeByYear"))
            financials[x["teamAbbr"]][i]+=c["salaryByYear"][i]+c["bonusByYear"][i]
        changed+=int(c!=oldc)
    assert all(count[y]==480 for y in range(2021,2030))
    assert report["startingRosterContractsAdjusted"]==changed and changed>100
    assert set(financials)==set(old["perTeamAggregateEconomics"])
    for team,values in financials.items():
        t=report["teamAggregate"][team]
        assert round(values[0]/1e6,3)==t["v30OpeningSalaryPlusBonusMillions"]
        assert round(values[1]/1e6,3)==t["v30Survivor2021Millions"]
        assert round(values[2]/1e6,3)==t["v30Survivor2022Millions"]
        assert values[0]<=MAX_MODELED_OPENING+2000
        assert all(values[offset]<=CAP for offset in range(1,5))
        base20=old["perTeamAggregateEconomics"][team].get("videoBefore2020CapSpaceMillions")
        space21=old["perTeamAggregateEconomics"][team].get("videoAfter2021CapSpaceMillions")
        if base20 is not None:
            assert t["illustrative2020MarketSpaceIfDollarForDollarMillions"]>=MIN_OBSERVED_2020_SPACE_AFTER_DELTA_M-.01
        if space21 is not None and space21<=15:
            assert t["modeled2021SurvivingContractDeltaMillions"]==0
    assert report["teamAggregate"]["BAL"]["modeled2021SurvivingContractDeltaMillions"]==0
    assert report["teamAggregate"]["PIT"]["modeled2021SurvivingContractDeltaMillions"]>=8
    assert report["immutableSourceChecksums"]["V19PlayersSHA256"]==V19_SHA256
    assert report["immutability"]["noDraftRecordsChanged"]
    assert report["immutability"]["noRosterNonContractFieldsChanged"]
    assert report["immutability"]["noCoachTeamFileChanges"]
    assert report["immutability"]["noProjectIceOrUserSaveChanges"]
    assert report["currentCarryoverCeilingMillions"]==v29["currentYearCarryoverCapMillions"]==30
    assert report["capBaseMillions"]==v29["baseSalaryCapMillions"]==300
    assert "progressionCurve" not in REPORT.read_text()
    assert '"potential":' not in REPORT.read_text().lower()
    print(json.dumps({
      "status":"V30_INDEPENDENT_STRUCTURAL_QA_PASSED_NOT_GAME_TESTED",
      "changed2020Contracts":changed,
      "futureProspectsUnmodified":sum(count.values()),
      "tight2021ClubsProtected":sum(old["perTeamAggregateEconomics"][t].get("videoAfter2021CapSpaceMillions") is not None and old["perTeamAggregateEconomics"][t]["videoAfter2021CapSpaceMillions"]<=15 for t in financials),
      "all32TeamsBelow292M2020Modeled":True
    },indent=2))

if __name__=="__main__":main()
