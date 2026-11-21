#!/usr/bin/env python3
"""V28: read-only 2021 real CapForge payroll and cap ceiling reconciliation.

Actual user screenshots anchor two clubs' displayed commitment and headroom.
Compare to V19 prior-year contract survivors, but NEVER infer individual
signings, salaries, exact engine bonus/dead cap treatment, or edit imports.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBS = ROOT / "data/v28-payroll-2021-team-observations.json"
V27 = ROOT / "preview/v27-video-cap-space-reconciliation.json"
V19 = ROOT / "preview/players-2020-nine-class-contracts-v19.json"
REPORT = ROOT / "preview/v28-payroll-cap-ceiling-reconciliation.json"
EXPECTED_2021_CAP_M = 330.0

def million(value):
    return round(float(value), 3)

def main():
    if REPORT.exists():
        print("V28 published report is immutable; refusing to overwrite")
        return
    obs = json.loads(OBS.read_text())
    old = json.loads(V27.read_text())
    digest = hashlib.sha256(V19.read_bytes()).hexdigest()
    assert digest == old["baseV19PlayersSha256"], "V19 source was modified"
    assert obs["version"] == "V28_GAME_2021_PAYROLL_SCREEN_OBSERVATIONS"
    assert set(obs["teams"]) == {"PIT", "BAL"}
    assert obs["season"] == 2021
    previous = old["perTeamAggregateEconomics"]
    rows = {}
    for abbr, screen in obs["teams"].items():
        actual_ceiling = screen["committedMillions"] + screen["spaceMillions"]
        assert abs(actual_ceiling - EXPECTED_2021_CAP_M) <= .05
        assert abs(old["perTeamAggregateEconomics"][abbr]["videoAfter2021CapSpaceMillions"] - screen["spaceMillions"]) < .001
        survivor_salary = previous[abbr]["year2SurvivingV19ContractsSalaryMillions"]
        survivor_bonus = previous[abbr]["year2SurvivingV19ContractsBonusMillions"]
        survivor_charge = million(survivor_salary + survivor_bonus)
        extra = million(screen["committedMillions"] - survivor_charge)
        assert extra > 0, "unexpected negative bridge from imported surviving deals"
        position_checks = []
        for tile in screen["positionExamples"]:
            calculated_pct = round(100 * tile["amountMillions"] / EXPECTED_2021_CAP_M, 1)
            assert abs(calculated_pct - tile["displayedPctOfCap"]) <= .1
            position_checks.append({
                "position": tile["position"],
                "displayedCapChargeMillions": tile["amountMillions"],
                "displayedPctOfCap": tile["displayedPctOfCap"],
                "recomputedPctOf330M": calculated_pct,
            })
        row = {
            "club": screen["name"],
            "displayed2021CommittedMillions": screen["committedMillions"],
            "displayed2021SpaceMillions": screen["spaceMillions"],
            "observedCapCeilingMillions": million(actual_ceiling),
            "v19Existing2020ContractsCarriedTo2021SalaryMillions": survivor_salary,
            "v19Existing2020ContractsCarriedTo2021BonusMillions": survivor_bonus,
            "v19Year2ImportedSurvivorSalaryPlusBonusMillions": survivor_charge,
            "observedCommitmentMinusV19SurvivorsMillions": extra,
            "observed2020MarketCapRoomMillions": previous[abbr]["videoBefore2020CapSpaceMillions"],
            "observed2020To2021CapRoomChangeMillions": million(screen["spaceMillions"] - previous[abbr]["videoBefore2020CapSpaceMillions"]),
            "positionPercentagesConsistentWith330M": position_checks,
        }
        if "freeTreemapTileMillions" in screen:
            assert abs(screen["freeTreemapTileMillions"]-screen["spaceMillions"])<.001
            row["freeTreemapTileIsUnusedCapNotExpense"] = True
        rows[abbr] = row
    pit, bal = rows["PIT"], rows["BAL"]
    payload = {
        "status": "V28_REAL_2021_PAYROLL_CEILING_VERIFIED_NO_CONTRACT_IMPORT",
        "scope": "PIT and BAL 2021 actual CapForge Payroll screenshots vs original unmodified V19 historical contracts and V27 2020/21 trade-market observations",
        "2021CapCeilingInGameMillions": EXPECTED_2021_CAP_M,
        "relativeToV19Modeled2020Cap": {
            "V19Assumed2020CapMillions": million(old["capAssumedInV19Import"] / 1_000_000),
            "absoluteDifferenceMillions": 30,
            "differencePercent": 10,
            "qualification": "The V19 $300M cap is an importer modeling assumption; this is not standalone proof of CapForge's 2020 game cap or a uniform yearly growth rule."
        },
        "teams": rows,
        "contrasting2021Clubs": {
            "BALMinusPITCommittedMillions": million(bal["displayed2021CommittedMillions"] - pit["displayed2021CommittedMillions"]),
            "BALMinusPITV19SurvivingContractsMillions": million(bal["v19Year2ImportedSurvivorSalaryPlusBonusMillions"]-pit["v19Year2ImportedSurvivorSalaryPlusBonusMillions"]),
            "BALMinusPITUnexplainedAdditionalCommitmentMillions": million(bal["observedCommitmentMinusV19SurvivorsMillions"]-pit["observedCommitmentMinusV19SurvivorsMillions"]),
            "interpretation": "The imported 2020 contract survivor gap is already large, but neither the balance nor its unexplained residual can be attributed to specific free-agent moves without the 2021 game transaction/payroll ledger."
        },
        "nextAction": {
            "decision": "Do not publish an unsafe V28 salary-adjusted Players file yet; the screen establishes the 2021 ceiling and team commitments but not which import salary/bonus/dead-cap fields contribute.",
            "evidenceNeeded": "If available, expand Payroll's full cap panel for PIT/BAL to record base, bonus, dead money, full cap ceiling and player count; preserve current 2021 save.",
            "candidateGuardrails": "Any later separately versioned contract trial should explicitly model 2021 $330M, avoid initial 2020 over-cap, allow rookie signings, preserve V19 noncontract fields and all 4,320 draft prospects, and be validated in a separate new game."
        },
        "preservation": {
            "v19OriginalPlayersSHA256": digest,
            "2021To2029ProspectsProtectedByExistingV19File": 4320,
            "teamsV2StaffV25AndAllExistingSavesUnmodified": True,
            "projectIceUnmodified": True
        },
        "limitations": [
            "2021 screenshot amounts rounded; one team's $293K space is more precise than $329.7M committed.",
            "A 2021 franchise has AI signings, releases, rookie deals and possibly dead cap not contained in the original V19 2020 snapshot.",
            "Survivor salary+bonus is imported contract math, not verified actual 2021 charge per player; difference is unassigned rather than proved FA spend.",
            "No salary, roster, development, rating, portrait, future draft, coaching or staff change is made by V28."
        ]
    }
    assert payload["contrasting2021Clubs"]["BALMinusPITCommittedMillions"] == 118.0
    REPORT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": payload["status"],
        "observedCap2021Millions": EXPECTED_2021_CAP_M,
        "BALminusPITCommittedMillions": 118,
        "V19PlayersPreserved": True,
    }, indent=2))

if __name__ == "__main__":
    main()
