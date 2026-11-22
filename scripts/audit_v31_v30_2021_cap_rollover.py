#!/usr/bin/env python3
"""V31 source-only in-game CapForge Week-1 2021 financial observations.

Do not infer unseen free-agent/draft transactions, internal CapForge salary
accounting, or later-year simulation from recorded 2021 Payroll screens.
Only compare aggregate 2020 and 2021 user-supplied real-game evidence.
"""
from __future__ import annotations
import hashlib,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OBS=ROOT/"data/v31-v30-2021-real-game-payroll-observations.json"
OLD=ROOT/"data/v30-actual-game-week1-payroll-observations.json"
V30=ROOT/"preview/v30-contract-calibration-audit.json"
V29=ROOT/"preview/v29-2021-carryover-cap-reconciliation.json"
PLAYERS=ROOT/"preview/players-2020-nine-class-contracts-v30-TEST.json"
TEAMS=ROOT/"preview/teams-2020-roofs-v2.json"
STAFF=ROOT/"preview/staff-2020-head-coach-video-matched-v25.json"
REPORT=ROOT/"preview/v31-v30-real-2021-cap-rollover-audit.json"

def round3(x):
    return round(float(x),3)

def main():
    if REPORT.exists():
        print("V31 report already published; preserve immutable past observations")
        return
    now=json.loads(OBS.read_text())
    old=json.loads(OLD.read_text())
    audit=json.loads(V30.read_text())
    v29=json.loads(V29.read_text())
    assert now["version"]=="V31_2021_WEEK1_V30_REAL_GAME_PAYROLL_SCREENS"
    assert now["season"]==2021 and old["year"]==2020
    assert now["baseCapM"]==v29["baseSalaryCapMillions"]==300
    assert now["carryoverM"]==now["maxCarryoverM"]==v29["currentYearCarryoverCapMillions"]==30
    assert now["effectiveCapM"]==now["baseCapM"]+now["carryoverM"]==330
    assert set(now["teamScreens"])==set(old["teams"])=={"PIT","BAL","JAX"}
    fingerprints={
      "V30PlayersSHA256":hashlib.sha256(PLAYERS.read_bytes()).hexdigest(),
      "V2TeamsSHA256":hashlib.sha256(TEAMS.read_bytes()).hexdigest(),
      "V25StaffSHA256":hashlib.sha256(STAFF.read_bytes()).hexdigest()
    }
    assert fingerprints["V2TeamsSHA256"]==audit["immutableSourceChecksums"]["V2TeamsSHA256"]
    assert fingerprints["V25StaffSHA256"]==audit["immutableSourceChecksums"]["V25StaffSHA256"]
    change={}
    for t,values in now["teamScreens"].items():
        earlier=old["teams"][t]
        assert round3(values["committedM"]+values["spaceM"])==330
        assert values["spaceM"]>0
        assert values["deadMoneyM"]>=0
        future=values["year2022"]
        assert round3(future["committedM"]+future["spaceM"])==300
        assert future["pickReserveAlreadyCommittedM"]>0
        assert future["committedM"]>=future["pickReserveAlreadyCommittedM"]
        assert round3(earlier["committed"]+earlier["space"])==300
        change[t]={
          "team":values["team"],
          "2020Week1AvailableM":earlier["space"],
          "2021Week1AvailableM":values["spaceM"],
          "2020To2021SpaceChangeM":round3(values["spaceM"]-earlier["space"]),
          "2020Week1CommittedM":earlier["committed"],
          "2021Week1CommittedM":values["committedM"],
          "2020Week1DeadMoneyM":earlier["dead"],
          "2021Week1DeadMoneyM":values["deadMoneyM"],
          "2021EffectiveCapM":330,
          "2021TeamOverall":values["teamOVR"],
          "2022ProjectedAvailableM":future["spaceM"],
          "2022ProjectedDraftPicksIncludedInCommittedM":future["pickReserveAlreadyCommittedM"],
          "notComparableTo2021ProjectedAsOf2020":"Actual 2021 payroll reflects unknown AI activity and is not the 2020 forward preview"
        }
    assert change["PIT"]["2020To2021SpaceChangeM"]==-16.5
    assert change["BAL"]["2020To2021SpaceChangeM"]==-76.7
    assert change["JAX"]["2020To2021SpaceChangeM"]==12.9
    assert change["BAL"]["2021Week1DeadMoneyM"]==5.2
    assert change["JAX"]["2021Week1DeadMoneyM"]==9.0
    report={
      "status":"V31_USER_VIDEO_V30_2020_TO_2021_SEASON_ROLLOVER_OBSERVED_ALL_THREE_TEAM_CAPS_LEGAL",
      "scope":"Real V30 Week-1 2021 team screenshots vs previously observed real V30 Week-1 2020 team screens. No game engine access or individual FA/draft ledger.",
      "game2021Week1Observed":True,
      "allThreeTeamsCapPositive":True,
      "specificFAAndDraftMechanicsIndependentlyVerified":False,
      "2022AndFutureActualGameplayVerified":False,
      "v30PermanentFranchiseCertified":False,
      "teamComparisons":change,
      "rosterEvidence":now["rosterExamples"],
      "capInterpretation":"2021 $300M base + $30M capped carryover; 2022 projected $300M base, draft pick reserve already inside committed.",
      "preservedHashes":fingerprints,
      "v30PlayersRecordsStillProtected":audit["protectedFutureProspects"]==4320,
      "protectedVersions":"Original V19 Players, current V30 Players, V2 Teams, V25 Staff, all nine 2021-29 draft classes and Project Ice untouched by read-only V31 audit.",
      "nextAction":now["nextAcceptance"],
      "limitations":now["limits"]
    }
    assert report["v30PlayersRecordsStillProtected"]
    assert '"potential":' not in json.dumps(report).lower()
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":report["status"],
      "TeamsVerified":sorted(change),
      "Actual2021PositiveCapAll":True,
      "2020To2021RoomM":{t:x["2020To2021SpaceChangeM"] for t,x in change.items()},
      "specificFADraftScreensPending":True
    },indent=2))

if __name__=="__main__":main()
