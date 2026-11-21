#!/usr/bin/env python3
"""V27: reconcile ACTUAL CapForge 2020/2021 team cap video to V19 contract fields.

Read-only analysis. Distinguish game UI CAP from V19 salary/bonus forecasts.
Infer whether CapForge charges only salary, salary + bonus, or something else.
Compare 30 teams present in both user-provided screens. NEVER invent player
transactions, run a mock game engine, or modify the approved import files.
"""
from __future__ import annotations
import collections,hashlib,json,statistics
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
VIDEO=ROOT/"data/v27-video-team-cap-space-2020-vs-2021.json"
PLAYERS=PREVIEW/"players-2020-nine-class-contracts-v19.json"
V19AUDIT=PREVIEW/"v19-simplified-contracts-audit.json"
V26AUDIT=PREVIEW/"v26-2021-offseason-static-preflight.json"
OUTPUT=PREVIEW/"v27-video-cap-space-reconciliation.json"
CAP=300_000_000

def pct(v):return round(v,2)
def money_m(v):return round(v/1_000_000,3)
def median(v):return round(statistics.median(v),3)
def mean(v):return round(statistics.mean(v),3)
def mae(a,b):return mean([abs(a[k]-b[k]) for k in a])
def main():
    if OUTPUT.exists():
        print("V27 report frozen on main; refusing rewrite")
        return
    data=json.loads(VIDEO.read_text())
    blob=PLAYERS.read_bytes()
    original=json.loads(blob)
    audit=json.loads(V19AUDIT.read_text())
    v26=json.loads(V26AUDIT.read_text())
    assert data["version"]=="V27_SCREEN_VIDEO_OBSERVATIONS"
    assert original["schemaVersion"]==3 and original["meta"]["baseSeason"]==2020
    assert len(original["players"])==6613
    roster=[p for p in original["players"] if p["pool"]=="roster"]
    assert len(roster)==2293
    before=data["before"]
    after=data["after"]
    b=before["teamSpaceMillions"]
    a=after["teamSpaceMillions"]
    assert len(b)==len(a)==31
    assert before["selectedTeam"]=="CAR" and after["selectedTeam"]=="SEA"
    assert set(b)==set(before["teamOverall"]) and set(a)==set(after["teamOverall"])
    both=sorted(set(a)&set(b))
    assert len(both)==30
    assert "SEA" not in a and "CAR" not in b

    detail=collections.defaultdict(lambda:{
        "rosterPlayers":0,"baseSalary":0,"proratedBonus":0,
        "otherGuaranteedSalary":0,"expiring":0,"year2Salary":0,"year2Bonus":0
    })
    for p in roster:
        c=p["contract"]
        t=detail[p["teamAbbr"]]
        t["rosterPlayers"]+=1
        t["baseSalary"]+=c["salaryByYear"][0]
        t["proratedBonus"]+=c["bonusByYear"][0]
        t["otherGuaranteedSalary"]+=c["guaranteeByYear"][0]
        if c["years"]==1:
            t["expiring"]+=1
        else:
            t["year2Salary"]+=c["salaryByYear"][1]
            t["year2Bonus"]+=c["bonusByYear"][1]
    assert len(detail)==32
    assert sum(t["rosterPlayers"] for t in detail.values())==2293
    assert sum(t["expiring"] for t in detail.values())==943
    for team,t in detail.items():
        assert t["baseSalary"]+t["proratedBonus"]==audit["gameModel"]["openingSalaryPlusBonusByTeam"][team]
    assert len(v26["perTeamStaticPreflight"])==32

    cap2020salary={team:money_m(CAP-t["baseSalary"]) for team,t in detail.items()}
    cap2020salaryBonus={team:money_m(CAP-t["baseSalary"]-t["proratedBonus"]) for team,t in detail.items()}
    obs2020={team:b[team] for team in b}
    errOnly={team:round(obs2020[team]-cap2020salary[team],3) for team in b}
    errAll={team:round(obs2020[team]-cap2020salaryBonus[team],3) for team in b}
    onlyMAE=mae(obs2020,cap2020salary)
    salaryPlusBonusMAE=mae(obs2020,cap2020salaryBonus)
    # Fair comparator: CapForge displays rounded $0.1M, many other users may
    # have selected an operating team not included in the Market partner list.
    matchesOnly=sum(abs(errOnly[t])<=1.5 for t in b)
    matchesBoth=sum(abs(errAll[t])<=1.5 for t in b)

    by_team={}
    for team in sorted(detail):
        t=detail[team]
        row={
            "importedStartingPlayers":t["rosterPlayers"],
            "v19FirstYearSalaryMillions":money_m(t["baseSalary"]),
            "v19FirstYearBonusMillions":money_m(t["proratedBonus"]),
            "v19FirstYearSalaryPlusBonusMillions":money_m(t["baseSalary"]+t["proratedBonus"]),
            "modelCapSpaceSalaryOnlyMillions":cap2020salary[team],
            "modelCapSpaceSalaryPlusBonusMillions":cap2020salaryBonus[team],
            "importedContractsHypotheticallyExpiringEnd2020":t["expiring"],
            "year2SurvivingV19ContractsSalaryMillions":money_m(t["year2Salary"]),
            "year2SurvivingV19ContractsBonusMillions":money_m(t["year2Bonus"]),
        }
        if team in b:
            row["videoBefore2020CapSpaceMillions"]=b[team]
            row["videoBeforeOverall"]=before["teamOverall"][team]
            row["videoMinusSalaryOnlyModelMillions"]=errOnly[team]
            row["videoMinusSalaryPlusBonusModelMillions"]=errAll[team]
        if team in a:
            row["videoAfter2021CapSpaceMillions"]=a[team]
            row["videoAfterOverall"]=after["teamOverall"][team]
        if team in both:
            row["observedCapSpaceChangeMillions"]=round(a[team]-b[team],3)
            row["observedOverallChange"]=after["teamOverall"][team]-before["teamOverall"][team]
        by_team[team]=row

    changed=[a[t]-b[t] for t in both]
    ovr_delta=[after["teamOverall"][t]-before["teamOverall"][t] for t in both]
    out={
       "status":"V27_VIDEO_CAP_MECHANICS_AUDITED_NOT_YET_CALIBRATED_OR_IN_GAME_REIMPORTED",
       "scope":"2020 CAR selected-team video compared with 2021 SEA selected-team video; Market > Trade Center > Partners CAP and OVR columns",
       "userInputVideoFilesNotDistributed":True,
       "baseV19PlayersFile":PLAYERS.name,
       "baseV19PlayersSha256":hashlib.sha256(blob).hexdigest(),
       "capAssumedInV19Import":CAP,
       "v19ReportedCommonSalaryScalingFactor":audit["gameModel"]["effectiveCommonGameScaleFactor"],
       "actualNFLSalaryCapsReference":{"2020":198200000,"2021":182500000,"2026":301200000},
       "historicalCapToGameReference":{
          "2020NFLTo300MGameMultiplier":round(CAP/198200000,6),
          "2021NFLTo300MGameMultiplier":round(CAP/182500000,6),
          "V19FractionOfPure2020Proportion":round(audit["gameModel"]["effectiveCommonGameScaleFactor"]/(CAP/198200000),4),
          "warning":"Direct full multiplier was intentionally reduced because the highest-payroll imported team exceeded model cap; never increase all player contracts uniformly without preserving legal cap.",
       },
       "teamVideoCoverage":{
           "before2020Teams":len(b),"after2021Teams":len(a),"sameTeamsCompared":len(both),
           "notShownBefore":"CAR","notShownAfter":"SEA"
       },
       "observedVideoCapMillions":{
           "before2020OnComparableTeams":{"mean":mean([b[x] for x in both]),"median":median([b[x] for x in both]),"min":min(b[x] for x in both),"max":max(b[x] for x in both)},
           "after2021OnComparableTeams":{"mean":mean([a[x] for x in both]),"median":median([a[x] for x in both]),"min":min(a[x] for x in both),"max":max(a[x] for x in both)},
           "changeAcrossSameTeams":{"mean":mean(changed),"median":median(changed),"increased":sum(x>0 for x in changed),"decreased":sum(x<0 for x in changed),"unchanged":sum(x==0 for x in changed)},
       },
       "overallComparisonSame30":{
           "beforeMean":mean([before["teamOverall"][x] for x in both]),
           "afterMean":mean([after["teamOverall"][x] for x in both]),
           "beforeMedian":median([before["teamOverall"][x] for x in both]),
           "afterMedian":median([after["teamOverall"][x] for x in both]),
           "averageChange":mean(ovr_delta),
           "largestDeclines":sorted([{"team":x,"difference":after["teamOverall"][x]-before["teamOverall"][x]} for x in both],key=lambda y:y["difference"])[:4],
           "largestIncreases":sorted([{"team":x,"difference":after["teamOverall"][x]-before["teamOverall"][x]} for x in both],key=lambda y:y["difference"],reverse=True)[:4],
           "note":"OVR depends on roster changes and in-game progression; a rating change alone cannot identify cause."
       },
       "starting2020ModelVsGame":{
          "comparedTeams":len(b),
          "meanAbsoluteDifferenceSalaryOnlyMillions":onlyMAE,
          "meanAbsoluteDifferenceSalaryPlusBonusMillions":salaryPlusBonusMAE,
          "teamsWithin1_5MillionsSalaryOnly":matchesOnly,
          "teamsWithin1_5MillionsSalaryPlusBonus":matchesBoth,
          "medianObservedMinusSalaryOnlyModelMillions":median(list(errOnly.values())),
          "medianObservedMinusSalaryPlusBonusModelMillions":median(list(errAll.values())),
          "calculation":"Predicted Cap space = $300M minus sum over roster of first-year base salary (or base+prorated bonus). Compare to visible in-game 2020 Market CAP.",
          "interpretation":"Lower residual identifies which import field combination better approximates CapForge's Trade Center display, but cannot prove underlying engine cap calculation or whether a few players were waived at league start.",
       },
       "perTeamAggregateEconomics":by_team,
       "preservation":{"V19PlayersUnmodified":True,"V2TeamsAndV25StaffUnmodified":True,"2021To2029DraftClassesUnmodified":True,"existingSavesUnaffected":True,"noHiddenPotentialData":True},
       "nextEngineeringGate":"If evidence shows bonus cap-model mismatch, test how CapForge counts bonus vs salaries and rebalance with a versioned V28 trial; never overwrite V19. Repeat 2020 starting-cap and 2021 offseason in disposable game, with enough room for rookie signings.",
       "limitations":[
           "Videos show Market Trade Center partner CAP/OVR, not itemized payroll. CAP may include dead money, release penalties and market-specific cap adjustments.",
           "2021 team payroll is after unknown in-game AI signings, trades, retirements, cuts, draft/rookie deals and game progression; cannot infer exact cause of each team's change.",
           "The original V19 roster imports 2293 players, but CapForge may assign different roster status to imports; exact active-cap cohort not externally verified.",
           "No player individual salaries, OVR, portrait or hidden potential are revealed in this public report.",
           "Actual full 2021 salary cap was lower than 2020 due to COVID; game seems to use a modern approximate $300M benchmark, but no game configuration screenshot confirms its formula."
       ]
    }
    assert "progressionCurve" not in json.dumps(out)
    OUTPUT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps({"status":out["status"],"capSpaceBeforeMedian":out["observedVideoCapMillions"]["before2020OnComparableTeams"]["median"],"capSpaceAfterMedian":out["observedVideoCapMillions"]["after2021OnComparableTeams"]["median"],"v19CalibrationFactor":out["v19ReportedCommonSalaryScalingFactor"],"salaryOnlyMAE":onlyMAE,"salaryPlusBonusMAE":salaryPlusBonusMAE,"teamHitsOnly":matchesOnly,"teamHitsAll":matchesBoth,"averageOverallChange":mean(ovr_delta)},indent=2))
if __name__=="__main__":main()
