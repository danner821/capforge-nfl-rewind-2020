#!/usr/bin/env python3
"""V26: spoiler-free static 2021 offseason preflight for approved V19 player import.

This is NOT the CapForge simulation engine. It tests contract arrays, computes
2020 -> 2021 obligations and possible free agents on expiration, and checks
the nine-year rookie pipeline. Does not edit any game input or player fields.

A contract with years == 1 *might* enter 2021 FA if neither game extension,
trade nor release happened. This audit cannot predict in-game resignings,
dead money, roster cuts, cap rollover, draft picks or simulation behavior.
"""
from __future__ import annotations
import collections
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
PLAYERS=PREVIEW/"players-2020-nine-class-contracts-v19.json"
BASELINE=PREVIEW/"v19-simplified-contracts-audit.json"
OUTPUT=PREVIEW/"v26-2021-offseason-static-preflight.json"
CAP=300_000_000
MIN_BASE=850_000
TARGET_ACTIVE_ROSTER=53

def main():
    if OUTPUT.exists():
        print("V26 published/frozen report exists; do not overwrite")
        return
    before=PLAYERS.read_bytes()
    data=json.loads(before)
    v19=json.loads(BASELINE.read_text())
    assert data["schemaVersion"]==3
    assert data["meta"]["baseSeason"]==2020
    assert len(data["players"])==6613
    assert len(data["deadCap"])==0
    assert len({p["iden"] for p in data["players"]})==6613
    roster=[p for p in data["players"] if p["pool"]=="roster"]
    prospects=[p for p in data["players"] if p["pool"]=="draftClass"]
    assert len(roster)==2293 and len(prospects)==4320
    assert len({p["teamAbbr"] for p in roster})==32
    draft_years=collections.Counter(int(p["bio"]["draftSeason"]) for p in prospects)
    assert all(draft_years[y]==480 for y in range(2021,2030))
    assert sum(draft_years.values())==4320

    per_team=collections.defaultdict(lambda:{
        "roster2020":0,
        "hypotheticalExpiringEnd2020":0,
        "stillUnderContract2021":0,
        "opening2020SalaryPlusBonus":0,
        "survivor2021SalaryPlusBonus":0,
        "2021SurvivorsWithBonuses":0,
        "2021SurvivorsWithGuaranteedSalary":0,
    })
    years=collections.Counter()
    for p in roster:
        abbr=p["teamAbbr"]
        c=p["contract"]
        n=c["years"]
        assert type(n) is int and 1<=n<=5
        assert c["signedSeason"]==2020
        assert c["currentYearIndex"]==0
        assert len(c["salaryByYear"])==len(c["bonusByYear"])==len(c["guaranteeByYear"])==n
        assert c["salary"]==c["salaryByYear"][0]
        assert c["guarantee"]==c["currentGuarantee"]==c["guaranteeByYear"][0]
        assert c["extension"]=={"salary":0,"guarantee":0,"years":0}
        for i in range(n):
            salary=c["salaryByYear"][i]
            bonus=c["bonusByYear"][i]
            guarantee=c["guaranteeByYear"][i]
            assert type(salary) is int and salary>=MIN_BASE
            assert type(bonus) is int and bonus>=0
            assert type(guarantee) is int and 0<=guarantee<=salary
        t=per_team[abbr]
        years[n]+=1
        t["roster2020"]+=1
        t["opening2020SalaryPlusBonus"]+=c["salaryByYear"][0]+c["bonusByYear"][0]
        if n==1:
            t["hypotheticalExpiringEnd2020"]+=1
        else:
            t["stillUnderContract2021"]+=1
            t["survivor2021SalaryPlusBonus"]+=c["salaryByYear"][1]+c["bonusByYear"][1]
            t["2021SurvivorsWithBonuses"]+=int(c["bonusByYear"][1]>0)
            t["2021SurvivorsWithGuaranteedSalary"]+=int(c["guaranteeByYear"][1]>0)

    assert dict(collections.Counter({k:v["opening2020SalaryPlusBonus"] for k,v in per_team.items()}))==v19["gameModel"]["openingSalaryPlusBonusByTeam"]
    assert sum(years.values())==2293
    assert years[1]==v19["remainingYearsHistogram"]["1"]
    assert len(per_team)==32
    issues=[]
    summaries={}
    for abbr,t in sorted(per_team.items()):
        assert t["roster2020"]==t["stillUnderContract2021"]+t["hypotheticalExpiringEnd2020"]
        assert 0<t["survivor2021SalaryPlusBonus"]<=CAP
        assert 0<t["opening2020SalaryPlusBonus"]<=CAP
        extra=max(0,TARGET_ACTIVE_ROSTER-t["stillUnderContract2021"])
        minimum_fill_cost=extra*MIN_BASE
        headroom=CAP-t["survivor2021SalaryPlusBonus"]
        estimate=t|{
            "hypotheticalExpiredPctOf2020Roster":round(
                100*t["hypotheticalExpiringEnd2020"]/t["roster2020"],1),
            "minimumNewPlayersToReach53":extra,
            "minimumBaseSalaryToReach53":minimum_fill_cost,
            "2021HeadroomBeforeNewDeals":headroom,
            "2021HeadroomAfterMinimum53Fill":headroom-minimum_fill_cost
        }
        summaries[abbr]=estimate
        if t["hypotheticalExpiringEnd2020"]/t["roster2020"]>0.55:
            issues.append({"team":abbr,"type":"high_single_season_churn","severity":"review"})
        if headroom<minimum_fill_cost:
            issues.append({"team":abbr,"type":"low_headroom_to_reach_minimum53_players","severity":"review"})
    expected2021=collections.Counter()
    for t in summaries.values():
        expected2021["survivors"]+=t["stillUnderContract2021"]
        expected2021["expiring"]+=t["hypotheticalExpiringEnd2020"]
        expected2021["minimum53Fill"]+=t["minimumNewPlayersToReach53"]
    assert expected2021["expiring"]==years[1]
    assert expected2021["survivors"]+expected2021["expiring"]==2293
    assert expected2021["minimum53Fill"]>=0

    report={
      "status":"V26_STATIC_OFFSEASON_PREFLIGHT_CI_ONLY_NO_GAME_SIMULATION",
      "baseVersion":"V19 Players; V2 Teams + V25 Staff unchanged",
      "inputPlayerFile":PLAYERS.name,
      "inputSHA256":hashlib.sha256(before).hexdigest(),
      "baseSeason":2020,
      "hypotheticalFirstOffseason":2021,
      "gameCapAssumption":CAP,
      "minimumBaseSalaryAssumption":MIN_BASE,
      "targetRosterForSizingOnly":TARGET_ACTIVE_ROSTER,
      "totalStarting2020RosterPlayers":len(roster),
      "teamCount":32,
      "originalFutureProspects":len(prospects),
      "futureProspectsByYear":{str(y):draft_years[y] for y in range(2021,2030)},
      "remaining2020ContractYearsHistogram":{str(k):years[k] for k in sorted(years)},
      "hypothetical2021ContractExpirations":expected2021["expiring"],
      "existing2020RosterStillContractedFor2021":expected2021["survivors"],
      "minimumNewPlayersAcrossTeamsToReach53":expected2021["minimum53Fill"],
      "perTeamStaticPreflight":summaries,
      "reviewFlags":issues,
      "reviewFlagCounts":dict(collections.Counter(x["type"] for x in issues)),
      "preservation":{
          "V19PlayerFileUnmodified":True,
          "all4320FutureClassProspectsIntact":True,
          "V25StaffAndV2TeamsNotWritten":True,
          "ProjectIceUnchanged":True,
          "noPlayerSpecificOrHiddenDevelopmentDataInPublicReport":True
      },
      "meaningOfExpirations":"Number of 2020 starting player contracts with only 1 remaining year, assuming no extension/trade/release before first 2021 offseason. NOT actual CapForge FA outcomes.",
      "scopeAndLimitations":[
          "STATIC math only; CapForge source/game engine is not controlled by this repository.",
          "Survivor salary/bonus commitments assume contract year 1 simply becomes current at 2021 offseason, not an observed game event.",
          "Excludes post-2020 new signings, re-signings, waivers, injuries, active roster eligibility, rookie contracts, cap rollover and dead-cap liability.",
          "2021 draft class 480 prospects must not be mistaken for 480 actual selections; game draft progression and persistence require manual game test.",
          "CapForge actual roster limit and changing salary-cap semantics may differ; 53-player roster minimum is an NFL-style comparison, not an asserted CapForge rule.",
          "Contract expirations across large imported rosters may appear high because all roster/depth players are included."
      ],
      "nextGameVerification":"In a NEW disposable V19 Players + V2 Teams + V25 Staff 2020 league: advance through 2020 season to 2021 offseason; inspect actual expiring contracts, cap screen, free-agent market, draft class and at least 3 teams; compare observed behavior to this static model. Preserve original save."
    }
    assert "potential" not in json.dumps(report).lower()
    assert PLAYERS.read_bytes()==before
    OUTPUT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
       "status":report["status"],
       "expiring_if_no_extensions":expected2021["expiring"],
       "survivors":expected2021["survivors"],
       "futureProspects":len(prospects),
       "teamsFlaggedForReview":len({x["team"] for x in issues}),
       "reviewFlagCounts":report["reviewFlagCounts"]
    },indent=2))

if __name__=="__main__":
    main()
