#!/usr/bin/env python3
"""V30 OPTIONAL 2020 CapForge players import: conservative, evidence-gated contracts.

Starting point is the *frozen V19 file* already observed working in CapForge.
Only change existing 2020 roster contracts; preserve all player portraits,
ratings, team identities, skills, potential/development, coaches and 480 real
prospects for every 2021-2029 draft class. This script never changes game rules.

V27 user-observed 2020 market space and 2021 market space constrain additions.
V29 established the $300M BASE cap, max $30M CARRYOVER and fixed $300M forward
projection with PICKS already in commitments. The 2021 room shown by the game
includes real AI activity, not just the imported V19 2020 contracts.
NO exact future simulation can be inferred from offline math.

We limit proportional uplifts to 28% over V19 (whose 1.181 source multiplier
was reduced from a 1.514 source ratio). Multi-year deals get an extra ceiling
from their team's observed 2021 free space, and opening changes retain >$34M
observed 2020 room on the simple *linear sensitivity* assumption. One-year
deal changes expire before 2021. No contract terms are extended artificially.
"""
from __future__ import annotations

import collections
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
SOURCE=PREVIEW/"players-2020-nine-class-contracts-v19.json"
V19=PREVIEW/"v19-simplified-contracts-audit.json"
V27=PREVIEW/"v27-video-cap-space-reconciliation.json"
V29=PREVIEW/"v29-2021-carryover-cap-reconciliation.json"
TEAMS=PREVIEW/"teams-2020-roofs-v2.json"
STAFF=PREVIEW/"staff-2020-head-coach-video-matched-v25.json"
OUTPUT=PREVIEW/"players-2020-nine-class-contracts-v30-TEST.json"
REPORT=PREVIEW/"v30-contract-calibration-audit.json"

V19_SHA256="c6d021d0b1573d475d3b8c399b16cdb7c4222230cfc9700093885e8958b0fdc9"
CAP=300_000_000
MAX_MODELED_OPENING=292_000_000
MIN_MODELED_OPENING_SPACE=8_000_000
MIN_OBSERVED_2020_SPACE_AFTER_DELTA_M=34.0
SCALE_CEILING=1.28
MIN_SALARY=850_000
ROUND=1000
DESIRED_2021_REMAINING_SPACE_M=65.0
MAX_2021_EXTRA_ORIGINAL_SURVIVORS_M=28.0
# Conservative 2022 PIT/BAL checks do not assume unearned 2022 carryover.
MIN_2022_OBSERVED_PROJECTED_ROOM_M=15.0

def rounded(x):
    return int(max(0,round(x/ROUND)*ROUND))

def current_charge(p,offset=0):
    c=p["contract"]
    return c["salaryByYear"][offset]+c["bonusByYear"][offset] if c["years"]>offset else 0

def adjusted_contract(c,scale):
    x=copy.deepcopy(c)
    if scale==1:
        return x
    for key in ("salaryByYear","bonusByYear","guaranteeByYear"):
        x[key]=[rounded(v*scale) for v in c[key]]
    assert all(s>=MIN_SALARY for s in x["salaryByYear"])
    for i in range(x["years"]):
        x["guaranteeByYear"][i]=min(x["salaryByYear"][i],x["guaranteeByYear"][i])
    x["salary"]=x["salaryByYear"][0]
    x["guarantee"]=x["currentGuarantee"]=x["guaranteeByYear"][0]
    return x

def charge_after(p,factor,offset):
    c=p["contract"]
    if c["years"]<=offset:return 0
    return rounded(c["salaryByYear"][offset]*factor)+rounded(c["bonusByYear"][offset]*factor)

def delta_for_group(players,factor,year_offset):
    return sum(charge_after(p,factor,year_offset)-current_charge(p,year_offset) for p in players)

def max_factor_for_delta(players,desired,year_offset,cap=SCALE_CEILING):
    if not players or desired<=0:return 1.0
    if delta_for_group(players,cap,year_offset)<=desired:return cap
    lo,hi=1.0,cap
    for _ in range(36):
        mid=(lo+hi)/2
        if delta_for_group(players,mid,year_offset)<=desired:lo=mid
        else:hi=mid
    return lo

def main():
    if OUTPUT.exists() or REPORT.exists():
        assert OUTPUT.exists() and REPORT.exists(),"Partial V30 publication!"
        print("Frozen V30 files present; skip rewriting the candidate")
        return
    raw=SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==V19_SHA256,"Protected original V19 changed"
    data=json.loads(raw)
    v19=json.loads(V19.read_text())
    v27=json.loads(V27.read_text())
    v29=json.loads(V29.read_text())
    assert v29["baseSalaryCapMillions"]==300 and v29["currentYearCarryoverCapMillions"]==30
    assert v27["baseV19PlayersSha256"]==V19_SHA256
    assert data["meta"]["baseSeason"]==2020 and len(data["players"])==6613
    assert data["deadCap"]==[]
    teams=collections.defaultdict(list)
    for p in data["players"]:
        if p["pool"]=="roster":teams[p["teamAbbr"]].append(p)
    assert len(teams)==32 and sum(map(len,teams.values()))==2293
    before=v27["perTeamAggregateEconomics"]
    assert set(before)==set(teams)
    team_data={}
    for abbr,roster in sorted(teams.items()):
        one=[p for p in roster if p["contract"]["years"]==1]
        multi=[p for p in roster if p["contract"]["years"]>1]
        old_open=sum(current_charge(p) for p in roster)
        old_survivor=sum(current_charge(p,1) for p in multi)
        old_second=sum(current_charge(p,2) for p in roster)
        assert old_open==v19["gameModel"]["openingSalaryPlusBonusByTeam"][abbr]
        baseline=before[abbr]
        game2020=baseline.get("videoBefore2020CapSpaceMillions")
        game2021=baseline.get("videoAfter2021CapSpaceMillions")
        # 2020 source-based cap safety: no club modeled beyond $292M.
        model_budget=max(0,MAX_MODELED_OPENING-old_open)
        if game2020 is None:
            # This team was selected in the 2020 Trade Center video, not
            # observed. Don't pretend to know its actual opening headroom.
            observed_budget=8_000_000
            target2020=0
        else:
            observed_budget=max(0,round((game2020-MIN_OBSERVED_2020_SPACE_AFTER_DELTA_M)*0.80*1_000_000))
            target2020=max(0,round((game2020-58.0)*0.65*1_000_000))
        total_budget=min(model_budget,observed_budget)
        if game2021 is None:
            desired_y2=0
        else:
            desired_y2=round(min(MAX_2021_EXTRA_ORIGINAL_SURVIVORS_M,
                max(0,(game2021-DESIRED_2021_REMAINING_SPACE_M)*0.55))*1_000_000)
        # Protect clubs with effectively NO room for their 2021 offseason.
        if game2021 is not None and game2021<=15.0:
            desired_y2=0
        fac_multi=max_factor_for_delta(multi,desired_y2,1)
        delta_multi2020=delta_for_group(multi,fac_multi,0)
        if delta_multi2020>total_budget:
            fac_multi=max_factor_for_delta(multi,total_budget,0,cap=fac_multi)
            delta_multi2020=delta_for_group(multi,fac_multi,0)
        # Protect projected PIT/BAL 2022 headroom (includes pick reserve).
        if abbr in v29["teamComparisons"]:
            y2022=v29["teamComparisons"][abbr]["futureYearProjection"]["2022"]["spaceMillions"]
            y3limit=max(0,round((y2022-MIN_2022_OBSERVED_PROJECTED_ROOM_M)*1_000_000))
            if delta_for_group(multi,fac_multi,2)>y3limit:
                fac_multi=max_factor_for_delta(multi,y3limit,2,cap=fac_multi)
                delta_multi2020=delta_for_group(multi,fac_multi,0)
        remaining=max(0,total_budget-delta_multi2020)
        # First-year increases on EXPIRING 2020 deals do not add a new 2021
        # multi-year liability, minimizing 2021 AI free-agency disruption.
        intended_one=max(0,min(remaining,target2020-delta_multi2020))
        fac_one=max_factor_for_delta(one,intended_one,0)
        delta_one2020=delta_for_group(one,fac_one,0)
        final_delta2020=delta_multi2020+delta_one2020
        final_survivor=old_survivor+delta_for_group(multi,fac_multi,1)
        assert final_delta2020<=total_budget+2000
        assert old_open+final_delta2020<=MAX_MODELED_OPENING+2000
        if game2020 is not None:
            assert game2020-final_delta2020/1_000_000>=MIN_OBSERVED_2020_SPACE_AFTER_DELTA_M-0.01
        if game2021 is not None and game2021<=15.0:
            assert final_survivor==old_survivor,"Tight 2021 team received forbidden continuing salary increases"
        team_data[abbr]={
            "oldOpening":old_open,
            "old2021Survivors":old_survivor,
            "old2022Survivors":old_second,
            "game2020":game2020,
            "game2021":game2021,
            "fMulti":fac_multi,
            "fOne":fac_one,
            "planned2020Delta":final_delta2020,
            "planned2021Delta":delta_for_group(multi,fac_multi,1),
            "planned2022Delta":delta_for_group(multi,fac_multi,2),
            "multiCount":len(multi),
            "oneCount":len(one)
        }
    result=copy.deepcopy(data)
    changed=0
    for p in result["players"]:
        if p["pool"]!="roster":continue
        team=team_data[p["teamAbbr"]]
        scale=team["fOne"] if p["contract"]["years"]==1 else team["fMulti"]
        before_contract=p["contract"]
        p["contract"]=adjusted_contract(before_contract,scale)
        changed+=int(p["contract"]!=before_contract)
    # Verify record-level integrity, especially hidden progression.
    assert len(result["players"])==len(data["players"])
    count_by_year=collections.Counter()
    aggregated=collections.defaultdict(lambda:collections.Counter())
    for before_p,after_p in zip(data["players"],result["players"]):
        assert before_p["iden"]==after_p["iden"]
        if before_p["pool"]=="draftClass":
            assert before_p==after_p
            count_by_year[before_p["bio"]["draftSeason"]]+=1
            continue
        assert {k:v for k,v in before_p.items() if k!="contract"}=={
            k:v for k,v in after_p.items() if k!="contract"}
        c=after_p["contract"]
        assert c["signedSeason"]==2020 and c["currentYearIndex"]==0
        assert c["salary"]==c["salaryByYear"][0]
        assert c["guarantee"]==c["currentGuarantee"]==c["guaranteeByYear"][0]
        assert c["extension"]=={"salary":0,"guarantee":0,"years":0}
        assert len(c["salaryByYear"])==len(c["bonusByYear"])==len(c["guaranteeByYear"])==c["years"]
        assert all(s>=MIN_SALARY and s%ROUND==0 for s in c["salaryByYear"])
        assert all(b>=0 and b%ROUND==0 for b in c["bonusByYear"])
        assert all(0<=g<=s and g%ROUND==0 for g,s in zip(c["guaranteeByYear"],c["salaryByYear"]))
        old=before_p["contract"]
        assert old["years"]==c["years"],"Contract length altered"
        assert c["salaryByYear"][0]>=old["salaryByYear"][0]
        for offset in range(c["years"]):
            assert c["salaryByYear"][offset]>=old["salaryByYear"][offset]
            assert c["bonusByYear"][offset]>=old["bonusByYear"][offset]
            assert c["guaranteeByYear"][offset]>=old["guaranteeByYear"][offset]
            assert c["salaryByYear"][offset]<=old["salaryByYear"][offset]*SCALE_CEILING+1000
            assert c["bonusByYear"][offset]<=old["bonusByYear"][offset]*SCALE_CEILING+1000
            assert c["guaranteeByYear"][offset]<=old["guaranteeByYear"][offset]*SCALE_CEILING+1000
            aggregated[after_p["teamAbbr"]][offset]+=current_charge(after_p,offset)
    assert all(count_by_year[y]==480 for y in range(2021,2030))
    assert sum(count_by_year.values())==4320
    assert changed>100,"Not a meaningful calibrated 2020 starting-roster update"
    for abbr,t in team_data.items():
        assert aggregated[abbr][0]==t["oldOpening"]+t["planned2020Delta"]
        assert aggregated[abbr][1]==t["old2021Survivors"]+t["planned2021Delta"]
        assert aggregated[abbr][2]==t["old2022Survivors"]+t["planned2022Delta"]
        assert aggregated[abbr][0]<=MAX_MODELED_OPENING+2000
        for y in range(1,5):
            assert aggregated[abbr][y]<=CAP,"Existing V30 contracts exceed future fixed $300M base before FA"
    total_2020=sum(v["planned2020Delta"] for v in team_data.values())
    total_2021=sum(v["planned2021Delta"] for v in team_data.values())
    assert total_2020>80_000_000,"No material initial 2020 cap correction occurred"
    assert team_data["BAL"]["planned2021Delta"]==0
    assert team_data["PIT"]["planned2021Delta"]>=8_000_000
    assert team_data["PIT"]["planned2022Delta"]<=round(
        (v29["teamComparisons"]["PIT"]["futureYearProjection"]["2022"]["spaceMillions"]-15)*1_000_000)+1000
    assert team_data["BAL"]["planned2022Delta"]==0
    report={
      "status":"V30_CONTRACTS_CALIBRATED_STRUCTURAL_TEST_READY_FOR_GAME_NOT_GAME_APPROVED",
      "base":"Frozen CapForge green V19 players, green V2 teams, user-approved V25 staff",
      "newPlayersImport":OUTPUT.name,
      "frozenV19SHA256":V19_SHA256,
      "baseSeason":2020,
      "protectedFutureProspects":4320,
      "prospectsByYear":{str(y):count_by_year[y] for y in range(2021,2030)},
      "playersInInitialRoster":2293,
      "teamCount":32,
      "startingRosterContractsAdjusted":changed,
      "maximumIndividualContractMultiplier":SCALE_CEILING,
      "capBaseMillions":300,
      "currentCarryoverCeilingMillions":30,
      "2020ModeledOpeningPayrollSafetyCeilingMillions":292,
      "sourceBased2020To2021ImportChargesChangedMillions":{
        "2020":round(total_2020/1_000_000,3),
        "2021":round(total_2021/1_000_000,3),
      },
      "teamAggregate":{
        a:{
          "initialV19OpeningSalaryPlusBonusMillions":round(t["oldOpening"]/1_000_000,3),
          "v30OpeningSalaryPlusBonusMillions":round(aggregated[a][0]/1_000_000,3),
          "estimated2020MarketSpaceV19Millions":t["game2020"],
          "illustrative2020MarketSpaceIfDollarForDollarMillions":None if t["game2020"] is None else round(t["game2020"]-t["planned2020Delta"]/1_000_000,3),
          "originalV19Survivor2021Millions":round(t["old2021Survivors"]/1_000_000,3),
          "v30Survivor2021Millions":round(aggregated[a][1]/1_000_000,3),
          "originalV19Survivor2022Millions":round(t["old2022Survivors"]/1_000_000,3),
          "v30Survivor2022Millions":round(aggregated[a][2]/1_000_000,3),
          "observed2021MarketSpaceInSeparateV19GameMillions":t["game2021"],
          "modeled2021SurvivingContractDeltaMillions":round(t["planned2021Delta"]/1_000_000,3),
          "oneYearDeals":t["oneCount"],
          "multiyearDeals":t["multiCount"],
          "scaledMultiYearFactor":round(t["fMulti"],5),
          "scaledOneYearFactor":round(t["fOne"],5),
        } for a,t in sorted(team_data.items())
      },
      "immutableSourceChecksums":{
        "V19PlayersSHA256":V19_SHA256,
        "V2TeamsSHA256":hashlib.sha256(TEAMS.read_bytes()).hexdigest(),
        "V25StaffSHA256":hashlib.sha256(STAFF.read_bytes()).hexdigest(),
      },
      "gameRiskGuardrails":[
        "At most 28% proportional uplift to current V19 2020 contract charges; 2020 salary and bonus scale together, no new contract terms.",
        "Clubs with <=$15M observed 2021 room receive no raise to continuing V19 contract obligations.",
        "For teams whose 2020 market room was visible, protect >$34M there on a cautious dollar-for-dollar assumption, guarding potential $30M carryover.",
        "Current imported-only 2020 payroll may not exceed $292M; game may treat payroll differently, so user must check new 2020 league cap.",
        "2022 projection guard for actual PIT/BAL screens; do not count PICK reserves twice.",
        "Unobserved 2020 selected-team CAR and unobserved 2021 selected-team SEA are not assigned invented cap room.",
        "Does NOT invent 2021 AI signing behavior or guarantee 2021 transaction/rookie legality from offline checks."
      ],
      "immutability":{
        "noDraftRecordsChanged":True,
        "noRosterNonContractFieldsChanged":True,
        "noCoachTeamFileChanges":True,
        "noProjectIceOrUserSaveChanges":True,
        "noRosterTeamOrDevelopmentDataRevealed":True,
      },
      "limitations":[
        "CapForge game engine belongs to CapForge; importing contracts cannot change AI logic, base cap or carryover mechanism.",
        "Prior V27 2020 market room includes CapForge accounting discrepancies, so projected dollar-for-dollar effects are rough sensitivity, not guaranteed new game cap values.",
        "2021/22 observed space originates in a different V19-generated franchise and includes unknown transactions; V30 may change AI actions.",
        "This is a separate V30 TEST candidate, not a permanent-franchise-approved import until the game validates a fresh 2020 start and an offseason progression.",
        "Contract amounts remain gameplay-scaled estimates, not exact legal NFL historical 2020 cap hits."
      ]
    }
    assert '"potential":' not in json.dumps(report).lower()
    assert "progressionCurve" not in json.dumps(report)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==V19_SHA256
    OUTPUT.write_text(json.dumps(result,separators=(",",":"))+"\n")
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":report["status"],
      "adjusted2020Players":changed,
      "originalRookiesPreserved":4320,
      "2020NewModeledPayrollM":[round(min(aggregated[t][0] for t in teams)/1e6,1),round(max(aggregated[t][0] for t in teams)/1e6,1)],
      "totalOpeningExtraChargesMillions":round(total_2020/1e6,1),
      "total2021OriginalSurvivorExtraMillions":round(total_2021/1e6,1),
      "PIT2021ExtraMillions":round(team_data["PIT"]["planned2021Delta"]/1e6,2),
      "BAL2021ExtraMillions":round(team_data["BAL"]["planned2021Delta"]/1e6,2),
      "teams":32
    },indent=2))

if __name__=="__main__":
    main()
