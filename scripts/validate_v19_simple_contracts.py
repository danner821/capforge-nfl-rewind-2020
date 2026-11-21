#!/usr/bin/env python3
"""V19 CI: immutable V15 non-contract player data and game-scale contracts."""
from __future__ import annotations
import collections
import copy
import hashlib
import json
from pathlib import Path
from build_v19_simple_contracts import INPUT, OUTPUT, REPORT, MAX_OPENING_CHARGE, MIN_SALARY
from capforge_ovr import estimate

def main():
    a=json.loads(INPUT.read_text())
    b=json.loads(OUTPUT.read_text())
    d=json.loads(REPORT.read_text())
    assert len(a["players"])==len(b["players"])==6613
    assert a["meta"]==b["meta"]=={"baseSeason":2020}
    assert a["deadCap"]==b["deadCap"]==[]
    assert d["status"]=="V19_STRUCTURAL_PASS_GAME_IMPORT_AND_FREE_AGENCY_UNTESTED"
    assert d["baseFileSha256"]==hashlib.sha256(INPUT.read_bytes()).hexdigest()
    assert d["contractsWith2020AnnualSource"]+d["fallbackContracts"]==2293
    assert d["contractsWith2020AnnualSource"]>=1200
    before={p["iden"]:p for p in a["players"]}
    after={p["iden"]:p for p in b["players"]}
    assert set(before)==set(after)
    by_team=collections.Counter()
    years=collections.Counter()
    changed=0
    unchanged=0
    for ident,p in before.items():
        q=after[ident]
        assert p["pool"]==q["pool"]
        if p["pool"]=="draftClass":
            assert p==q, "Future prospect or development altered"
            unchanged+=1
            continue
        assert p["pool"]=="roster"
        assert {k:v for k,v in p.items() if k!="contract"}=={k:v for k,v in q.items() if k!="contract"}, "Historical 2020 non-contract record changed"
        c=q["contract"]
        n=c["years"]
        assert type(n) is int and 1<=n<=5
        assert c["signedSeason"]==2020 and c["currentYearIndex"]==0
        assert c["salary"]==c["salaryByYear"][0]>0
        assert c["guarantee"]==c["currentGuarantee"]==c["guaranteeByYear"][0]
        assert len(c["salaryByYear"])==len(c["bonusByYear"])==len(c["guaranteeByYear"])==n
        assert c["extension"]=={"salary":0,"guarantee":0,"years":0}
        assert all(type(x) is int and x>=MIN_SALARY for x in c["salaryByYear"])
        assert all(type(x) is int and x>=0 for x in c["bonusByYear"])
        assert all(type(x) is int and 0<=x<=s for x,s in zip(c["guaranteeByYear"],c["salaryByYear"]))
        assert c["salary"]%1000==0 and c["guarantee"]%1000==0
        assert all(x%1000==0 for arr in ("salaryByYear","bonusByYear","guaranteeByYear") for x in c[arr])
        years[n]+=1
        by_team[q["teamAbbr"]]+=c["salary"]+c["bonusByYear"][0]
        changed+=(c!=p["contract"])
    assert unchanged==4320 and changed>=2000 and len(by_team)==32
    assert all(100_000_000<=x<=MAX_OPENING_CHARGE+1000 for x in by_team.values())
    assert dict(by_team)==d["gameModel"]["openingSalaryPlusBonusByTeam"]
    assert len({round(x/100_000) for x in by_team.values()})>=8
    assert all(x>=20_000_000 for x in [300_000_000-v for v in by_team.values()])
    counts=collections.Counter(p["bio"]["draftSeason"] for p in b["players"] if p["pool"]=="draftClass")
    assert all(counts[y]==480 for y in range(2021,2030))
    assert d["protectedNonContractFieldsFor2020Players"] is True
    assert "progressionCurve" not in REPORT.read_text()
    assert "potential" not in d
    print(json.dumps({
      "status":"V19_STRUCTURAL_TEST_PASS_CAPFORGE_IMPORT_NOT_YET_VERIFIED",
      "contract_changes":changed,
      "preserved_drafts":unchanged,
      "sourced_2020_annual":d["contractsWith2020AnnualSource"],
      "modeled_fallback":d["fallbackContracts"],
      "payroll_min":min(by_team.values()),
      "payroll_max":max(by_team.values()),
      "contract_years":dict(years)
    },indent=2))

if __name__=="__main__":
    main()
