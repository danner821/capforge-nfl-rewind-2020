#!/usr/bin/env python3
"""V28 regression: 2021 CapForge screenshot arithmetic, no roster rewrite."""
import hashlib
import json
from audit_v28_payroll_2021_cap_ceiling import OBS, V27, V19, REPORT, EXPECTED_2021_CAP_M

def main():
    obs=json.loads(OBS.read_text())
    report=json.loads(REPORT.read_text())
    previous=json.loads(V27.read_text())
    assert report["status"]=="V28_REAL_2021_PAYROLL_CEILING_VERIFIED_NO_CONTRACT_IMPORT"
    assert report["2021CapCeilingInGameMillions"]==EXPECTED_2021_CAP_M==330
    assert set(report["teams"])=={"PIT","BAL"}
    assert report["preservation"]["v19OriginalPlayersSHA256"]==hashlib.sha256(V19.read_bytes()).hexdigest()
    assert report["preservation"]["v19OriginalPlayersSHA256"]==previous["baseV19PlayersSha256"]
    assert report["preservation"]["2021To2029ProspectsProtectedByExistingV19File"]==4320
    assert report["preservation"]["teamsV2StaffV25AndAllExistingSavesUnmodified"]
    assert report["preservation"]["projectIceUnmodified"]
    for team,screen in obs["teams"].items():
        row=report["teams"][team]
        assert abs(row["observedCapCeilingMillions"]-330.0)<.05
        assert abs(row["displayed2021CommittedMillions"]-screen["committedMillions"])<.001
        assert abs(row["displayed2021SpaceMillions"]-screen["spaceMillions"])<.001
        assert row["v19Year2ImportedSurvivorSalaryPlusBonusMillions"]==round(
          row["v19Existing2020ContractsCarriedTo2021SalaryMillions"]+
          row["v19Existing2020ContractsCarriedTo2021BonusMillions"],3)
        assert abs(row["observedCommitmentMinusV19SurvivorsMillions"]-
                   round(screen["committedMillions"]-row["v19Year2ImportedSurvivorSalaryPlusBonusMillions"],3))<.001
        assert row["observed2020MarketCapRoomMillions"]==previous["perTeamAggregateEconomics"][team]["videoBefore2020CapSpaceMillions"]
        for tile in row["positionPercentagesConsistentWith330M"]:
            assert abs(tile["displayedPctOfCap"]-tile["recomputedPctOf330M"])<=.1
    assert report["contrasting2021Clubs"]["BALMinusPITCommittedMillions"]==118.0
    assert report["relativeToV19Modeled2020Cap"]["V19Assumed2020CapMillions"]==300.0
    assert "potential" not in REPORT.read_text().lower()
    assert "progressionCurve" not in REPORT.read_text()
    print("V28 real-game payroll evidence and V19 file preservation validated")

if __name__=="__main__":
    main()
