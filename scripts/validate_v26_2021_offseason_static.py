#!/usr/bin/env python3
"""V26 regression: static 2021 transition math, not CapForge game engine."""
from __future__ import annotations
import collections,hashlib,json
from audit_v26_2021_offseason_static import PLAYERS,BASELINE,OUTPUT,CAP,MIN_BASE

def main():
    data=json.loads(PLAYERS.read_text())
    old=json.loads(BASELINE.read_text())
    v=json.loads(OUTPUT.read_text())
    assert v["status"]=="V26_STATIC_OFFSEASON_PREFLIGHT_CI_ONLY_NO_GAME_SIMULATION"
    assert v["inputSHA256"]==hashlib.sha256(PLAYERS.read_bytes()).hexdigest()
    assert len(data["players"])==6613
    assert v["originalFutureProspects"]==4320
    assert v["totalStarting2020RosterPlayers"]==2293
    assert v["teamCount"]==32
    assert v["gameCapAssumption"]==CAP and v["minimumBaseSalaryAssumption"]==MIN_BASE
    assert all(v["futureProspectsByYear"][str(y)]==480 for y in range(2021,2030))
    assert v["remaining2020ContractYearsHistogram"]==old["remainingYearsHistogram"]
    teams=v["perTeamStaticPreflight"]
    assert len(teams)==32 and set(teams)==set(old["gameModel"]["openingSalaryPlusBonusByTeam"])
    e=survivors=total=need=0
    flagged=set((x["team"],x["type"]) for x in v["reviewFlags"])
    for abbr,t in teams.items():
        assert t["roster2020"]>=53
        assert t["hypotheticalExpiringEnd2020"]+t["stillUnderContract2021"]==t["roster2020"]
        assert t["opening2020SalaryPlusBonus"]==old["gameModel"]["openingSalaryPlusBonusByTeam"][abbr]
        assert t["survivor2021SalaryPlusBonus"]<=CAP
        assert t["2021HeadroomBeforeNewDeals"]==CAP-t["survivor2021SalaryPlusBonus"]
        assert t["minimumNewPlayersToReach53"]==max(0,53-t["stillUnderContract2021"])
        assert t["minimumBaseSalaryToReach53"]==t["minimumNewPlayersToReach53"]*MIN_BASE
        assert t["2021HeadroomAfterMinimum53Fill"]==t["2021HeadroomBeforeNewDeals"]-t["minimumBaseSalaryToReach53"]
        assert t["hypotheticalExpiredPctOf2020Roster"]==round(100*t["hypotheticalExpiringEnd2020"]/t["roster2020"],1)
        if t["hypotheticalExpiringEnd2020"]/t["roster2020"]>0.55:
            assert (abbr,"high_single_season_churn") in flagged
        if t["2021HeadroomBeforeNewDeals"]<t["minimumBaseSalaryToReach53"]:
            assert (abbr,"low_headroom_to_reach_minimum53_players") in flagged
        total+=t["roster2020"]
        e+=t["hypotheticalExpiringEnd2020"]
        survivors+=t["stillUnderContract2021"]
        need+=t["minimumNewPlayersToReach53"]
    assert total==2293
    assert e==v["hypothetical2021ContractExpirations"]==943
    assert survivors==v["existing2020RosterStillContractedFor2021"]==1350
    assert need==v["minimumNewPlayersAcrossTeamsToReach53"]
    assert v["preservation"]["V19PlayerFileUnmodified"]
    assert v["preservation"]["all4320FutureClassProspectsIntact"]
    assert "progressionCurve" not in OUTPUT.read_text()
    assert "potential" not in OUTPUT.read_text().lower()
    print(json.dumps({
      "status":"V26_STATIC_PRESIM_QA_PASSED_GAME_TRANSITION_NOT_OBSERVED",
      "oneYearExpirations":e,
      "continuing":survivors,
      "teamChurnFlags":v["reviewFlagCounts"].get("high_single_season_churn",0),
      "teamsWithMinimum53CapConcern":v["reviewFlagCounts"].get("low_headroom_to_reach_minimum53_players",0),
      "draftProspectsPreserved":4320
    },indent=2))
if __name__=="__main__":main()
