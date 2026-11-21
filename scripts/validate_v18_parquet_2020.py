#!/usr/bin/env python3
"""Safeguard: V18 is a read-only source audit, not a player import."""
import json
from pathlib import Path
from audit_v18_parquet_2020 import OUTPUT,INPUT

def main():
    report=json.loads(OUTPUT.read_text())
    assert report["status"]=="V18_PARQUET_SOURCE_SHAPE_AUDIT_ONLY_NO_PLAYER_CONTRACTS_CHANGED"
    assert report["source_contract_rows"]>30000
    assert report["2020_starting_roster_count"]==2293
    assert sum(report["2020_roster_candidate_matches"].values())==2293
    assert isinstance(report["nonempty_history_contracts"],int)
    assert isinstance(report["common_annual_field_names"],list)
    assert "player" in report["source_field_names"]
    assert report["cap_model"]["direct_ratio_is_not_an_approved_scaling_policy"] is True
    assert report["parquet_bytes"]>100000
    assert len(report["parquet_sha256"])==64
    assert INPUT.exists()
    assert "progressionCurve" not in OUTPUT.read_text()
    assert "potential" not in report
    print(json.dumps({
        "status":"V18_SOURCE_AUDIT_STRUCTURAL_VALIDATION_PASSED_NO_PLAYER_CONTRACTS_CHANGED",
        "contracts":report["source_contract_rows"],
        "annual_history_nonempty":report["nonempty_history_contracts"],
        "annual_unique_2020_candidates":report["unique_team_term_candidates_with_one_explicit_2020_history"],
        "annual_duplicate_source_contracts":report["contracts_with_duplicate_recognized_years"]
    },indent=2))
if __name__=="__main__":main()
