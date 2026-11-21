#!/usr/bin/env python3
"""V27 regression: video-reconciled team cap/OVR and V19 input integrity."""
from __future__ import annotations
import hashlib,json
from audit_v27_game_cap_video_reconciliation import PLAYERS, VIDEO, OUTPUT, V19AUDIT, CAP

def main():
    data=json.loads(PLAYERS.read_text())
    notes=json.loads(VIDEO.read_text())
    audit=json.loads(V19AUDIT.read_text())
    result=json.loads(OUTPUT.read_text())
    assert result["status"]=="V27_VIDEO_CAP_MECHANICS_AUDITED_NOT_YET_CALIBRATED_OR_IN_GAME_REIMPORTED"
    assert result["baseV19PlayersSha256"]==hashlib.sha256(PLAYERS.read_bytes()).hexdigest()
    assert len(data["players"])==6613
    assert result["capAssumedInV19Import"]==CAP==300_000_000
    before=notes["before"]["teamSpaceMillions"]
    after=notes["after"]["teamSpaceMillions"]
    both=set(before)&set(after)
    assert len(before)==len(after)==31 and len(both)==30
    assert result["teamVideoCoverage"]["sameTeamsCompared"]==30
    assert result["observedVideoCapMillions"]["changeAcrossSameTeams"]["increased"]==7
    assert result["observedVideoCapMillions"]["changeAcrossSameTeams"]["decreased"]==23
    assert result["observedVideoCapMillions"]["before2020OnComparableTeams"]["median"]>=75
    assert result["observedVideoCapMillions"]["after2021OnComparableTeams"]["median"]<=50
    assert result["overallComparisonSame30"]["averageChange"]>-3
    assert result["overallComparisonSame30"]["averageChange"]<3
    assert len(result["perTeamAggregateEconomics"])==32
    assert result["starting2020ModelVsGame"]["comparedTeams"]==31
    assert result["starting2020ModelVsGame"]["meanAbsoluteDifferenceSalaryOnlyMillions"]>=0
    assert result["starting2020ModelVsGame"]["meanAbsoluteDifferenceSalaryPlusBonusMillions"]>=0
    for name,entry in result["perTeamAggregateEconomics"].items():
        assert entry["v19FirstYearSalaryMillions"]+entry["v19FirstYearBonusMillions"]-entry["v19FirstYearSalaryPlusBonusMillions"]<0.002
        assert entry["importedStartingPlayers"]>=53
        assert entry["modelCapSpaceSalaryOnlyMillions"]>=entry["modelCapSpaceSalaryPlusBonusMillions"]
        assert audit["gameModel"]["openingSalaryPlusBonusByTeam"][name]/1_000_000==entry["v19FirstYearSalaryPlusBonusMillions"]
        if name in both:
            assert "observedOverallChange" in entry
            assert "observedCapSpaceChangeMillions" in entry
    assert result["preservation"]["V19PlayersUnmodified"]
    assert result["preservation"]["V2TeamsAndV25StaffUnmodified"]
    assert result["preservation"]["2021To2029DraftClassesUnmodified"]
    assert "progressionCurve" not in OUTPUT.read_text()
    assert "potential" not in OUTPUT.read_text().lower()
    print(json.dumps({
        "status":"V27_USER_VIDEO_CAP_RECONCILIATION_TEST_PASSED_NO_ROSTER_CHANGE",
        "beforeMedianCapM":result["observedVideoCapMillions"]["before2020OnComparableTeams"]["median"],
        "afterMedianCapM":result["observedVideoCapMillions"]["after2021OnComparableTeams"]["median"],
        "salaryOnlyModelErrorM":result["starting2020ModelVsGame"]["meanAbsoluteDifferenceSalaryOnlyMillions"],
        "salaryPlusBonusModelErrorM":result["starting2020ModelVsGame"]["meanAbsoluteDifferenceSalaryPlusBonusMillions"],
        "overallMeanChange":result["overallComparisonSame30"]["averageChange"]
    },indent=2))
if __name__=="__main__":main()
