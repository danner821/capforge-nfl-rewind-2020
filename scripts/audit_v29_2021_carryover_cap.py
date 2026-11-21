#!/usr/bin/env python3
"""V29 source-only audit: CapForge base cap, carryover and year-by-year
commitments from REAL user screenshots, preserving original V19 and V28 files.

Never equate effective cap with base cap or treat pick reserves as extra charges.
This is an arithmetic/reconciliation audit, NOT CapForge game engine simulation.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OBS=ROOT/"data/v29-2021-expanded-payroll-screens.json"
OLD=ROOT/"preview/v28-payroll-cap-ceiling-reconciliation.json"
V27=ROOT/"preview/v27-video-cap-space-reconciliation.json"
PLAYERS=ROOT/"preview/players-2020-nine-class-contracts-v19.json"
OUTPUT=ROOT/"preview/v29-2021-carryover-cap-reconciliation.json"

def n(x):
    return round(float(x),3)

def main():
    if OUTPUT.exists():
        print("V29 published audit frozen; no report rewrite")
        return
    obs=json.loads(OBS.read_text())
    old=json.loads(OLD.read_text())
    video=json.loads(V27.read_text())
    digest=hashlib.sha256(PLAYERS.read_bytes()).hexdigest()
    assert digest==old["preservation"]["v19OriginalPlayersSHA256"]==video["baseV19PlayersSha256"]
    assert obs["version"]=="V29_REAL_GAME_EXPANDED_PAYROLL_EVIDENCE"
    assert set(obs["teams"])=={"BAL","PIT"} and obs["saveSeason"]==2021
    results={}
    for abbr,team in obs["teams"].items():
        now=team["currentYear"]
        assert now["baseCapMillions"]==300
        assert now["carryoverMillions"]==now["carryoverMaxMillions"]==30
        assert now["effectiveCapMillions"]==330
        assert now["deadMoneyMillions"]==0
        assert abs(now["baseCapMillions"]+now["carryoverMillions"]-now["effectiveCapMillions"])<.001
        assert abs(now["committedMillions"]+now["spaceMillions"]-now["effectiveCapMillions"])<.025
        assert now["spaceMillions"]==old["teams"][abbr]["displayed2021SpaceMillions"]
        assert now["committedMillions"]==old["teams"][abbr]["displayed2021CommittedMillions"]
        future={}
        for year,s in team["projectedBySeason"].items():
            year_int=int(year)
            assert 2021<=year_int<=2026
            assert s["capMillions"]==300
            if year_int==2021:
                assert s["picksMillions"] is None
                # Actual 2021 display uses $330M effective cap with carryover
                assert abs(s["committedMillions"]+s["spaceMillions"]-330)<.025
            else:
                assert abs(s["committedMillions"]+s["spaceMillions"]-300)<.01
            if s["picksMillions"] is not None:
                assert s["picksMillions"]>0
                assert s["committedMillions"]>=s["picksMillions"]
            future[year]={
                "committedMillionsIncludesPickReserve":s["committedMillions"],
                "reservedDraftPicksMillionsAlreadyIncluded":s["picksMillions"],
                "projectedBaseCapMillions":s["capMillions"],
                "spaceMillions":s["spaceMillions"],
                "isCurrentYearEffectiveCapWithCarryover":year_int==2021
            }
        before=video["perTeamAggregateEconomics"][abbr]["videoBefore2020CapSpaceMillions"]
        after=now["spaceMillions"]
        # This is a hypothetical common base-cap comparison, not actual
        # spendable room without carryover: a team can legally spend carryover.
        after_base_equivalent=n(after-now["carryoverMillions"])
        assert before>=30
        result={
          "team":team["name"],
          "2021BaseCapMillions":300.0,
          "2021CarryoverUsedMillions":30.0,
          "2021EffectiveCapMillions":330.0,
          "2021CommittedMillions":now["committedMillions"],
          "2021DeadMoneyMillions":0.0,
          "2021UnspentMillions":after,
          "2020MarketSpaceMillions":before,
          "2021ApparentRoomChangeMillions":n(after-before),
          "2021RoomLessCarryoverForComparisonOnlyMillions":after_base_equivalent,
          "2020To2021RoomChangeExcludingCarryoverForComparisonMillions":n(after_base_equivalent-before),
          "2020CapRoomBeyondMax30MCarryoverMillions":n(before-30),
          "futureYearProjection":future
        }
        results[abbr]=result
    assert results["PIT"]["2021ApparentRoomChangeMillions"]==39.4
    assert results["PIT"]["2020To2021RoomChangeExcludingCarryoverForComparisonMillions"]==9.4
    assert results["BAL"]["2021ApparentRoomChangeMillions"]==-102.407
    assert results["BAL"]["2020To2021RoomChangeExcludingCarryoverForComparisonMillions"]==-132.407
    out={
      "status":"V29_GAME_PAYROLL_BASE_CAP_AND_CARRYOVER_VERIFIED_READ_ONLY_NO_NEW_IMPORT",
      "baseSalaryCapMillions":300,
      "effective2021CapAtMaximumCarryoverMillions":330,
      "currentYearCarryoverCapMillions":30,
      "observed2021BaseCapGrowthOverModeled2020BaseMillions":0,
      "explicitCorrectionToV28":"Earlier V28 identified $330M displayed ceiling but could not see decomposition. V29 confirms $300M base + $30M capped carryover. Do NOT describe a 10% base cap raise.",
      "evidence":"User-supplied actual expanded 2021 Payroll screenshots for PIT and BAL; no save or individual contract data copied",
      "draftPickAccounting":"Projected PICKS reserve is already included in COMMITTED and deducted in SPACE. Never add projected PICKS again.",
      "deadMoneyObservation":"Zero displayed dead money for PIT/BAL in this 2021 test state; not evidence other clubs/years have zero.",
      "futureProjectionNote":"2022-2026 projections use the flat $300M base cap; potential future carryover is not assumed. The game's note says new deals book roughly 7% cheaper each year out, and 2025/26 zero forecasts need not imply contractual reality after the projected horizon.",
      "teamComparisons":results,
      "v19Reconciliation":{
        "starting2020ContractScaleFactor":video["v19ReportedCommonSalaryScalingFactor"],
        "unchanged2020V19PlayersSHA256":digest,
        "note":"V19 originally modeled a $300M cap; V29 verifies the in-game base-cap number and 2021 carryover. Actual 2021 AI moves and contract accounting cannot be reconstructed from V19 import or these aggregate screens.",
      },
      "economicRiskAssessment":{
        "blanketRaiseUnsafe":"2021 BAL has only $0.293M space even after $30M carryover, and 2022 projected BAL has $24.8M space. Increasing all retained contracts could create over-cap clubs or forced releases.",
        "2020CarryoverSensitivity":"Both 2020 Market snapshots show over $30M room. A 2020 player-charge increase smaller than (2020 room minus $30M) would not by itself lower the $30M carryover if all else held constant, but repeated 2021 charges would still constrain already tight teams.",
        "PIT2021CarryoverContributionMillions":30,
        "PITSpaceChange2020To2021Millions":39.4,
        "PITRoomChangeExcluding2021CarryoverForComparisonMillions":9.4,
        "recommendation":"Do not apply universal 1.51x contracts or overwrite V19. Any separate experimental players import must audit both original year and carryover-dependent offseason plus 2022 $300M base and pick reservations. Current 2021 user save stays unchanged."
      },
      "lockedPreservation":{
        "originalV19PlayerFileUnmodified":True,
        "teamsV2AndVisuallyApprovedV25StaffUnmodified":True,
        "prospects2021To2029Protected":4320,
        "existingUserSaveAndProjectIceUnmodified":True,
        "noPlayerRatingsOrHiddenDevelopmentDisclosed":True
      },
      "limitations":[
        "Displayed 2021 payroll rounded to $0.1M except BAL $293K space.",
        "No per-player 2021 transaction ledger or full individual salary/bonus details; cannot prove exact engine charge basis.",
        "2022-26 panels are CURRENT-SAVE projections, not seasons actually simulated.",
        "No 2020 actual Team Payroll expanded screen provided; 2020 Market CAP videos are comparative evidence, not per-player reconciliation."
      ]
    }
    OUTPUT.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":out["status"],"baseCapM":300,"carryoverM":30,"PIT2021RoomChangeExCarryoverM":9.4,"V19Unmodified":True},indent=2))

if __name__=="__main__":
    main()
