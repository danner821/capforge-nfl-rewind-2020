#!/usr/bin/env python3
"""V17 checks: source coverage report completeness, not contract correctness."""
import json
from pathlib import Path
from audit_v17_contract_source import OUT,BASE,ACTUAL_2020_NFL_CAP,SIMULATOR_ASSUMED_CAP
def main():
    r=json.loads(OUT.read_text())
    assert r["status"]=="V17_SOURCE_AUDIT_ONLY_DO_NOT_USE_AS_REPLACEMENT_CONTRACTS"
    assert r["totalSourceContractRecords"]>30000
    assert r["startingRoster"]==2293
    assert sum(r["matchCountDiagnostic"].values())==2293
    assert r["actualNFL2020BaseCap"]==ACTUAL_2020_NFL_CAP
    assert r["assumedCapForgeSimulatorCap"]==SIMULATOR_ASSUMED_CAP
    assert "player" in r["sourceSchemaFields"]
    assert "year_signed" in r["sourceSchemaFields"]
    assert "season_history" in r["nestedHistoryFieldsAvailable"] or "season_history" not in r["sourceSchemaFields"]
    assert r["contractAccuracyWarnings"]
    assert "progressionCurve" not in OUT.read_text()
    assert BASE.exists()
    print(json.dumps({"result":"V17_CONTRACT_SOURCE_DIAGNOSTIC_PASSED_NO_PLAYER_REPLACEMENT",
        "sourceRows":r["totalSourceContractRecords"],
        "uniquePlausible2020TeamNameMatches":r["matchCountDiagnostic"].get("single_name_2020_term_and_team_match",0),
        "all2020Players":2293,
        "sourceAnnualHistoryShapes":r["seasonHistorySerializedTypes"]},indent=2))
if __name__=="__main__":main()
