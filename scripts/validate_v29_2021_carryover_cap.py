#!/usr/bin/env python3
"""Read-only V29 checks: $300M base, $30M carryover, projected years."""
import json,hashlib
from audit_v29_2021_carryover_cap import OBS, OLD, V27, PLAYERS, OUTPUT
def main():
    x=json.loads(OUTPUT.read_text())
    o=json.loads(OBS.read_text())
    old=json.loads(OLD.read_text())
    assert x["status"]=="V29_GAME_PAYROLL_BASE_CAP_AND_CARRYOVER_VERIFIED_READ_ONLY_NO_NEW_IMPORT"
    assert x["baseSalaryCapMillions"]==300
    assert x["effective2021CapAtMaximumCarryoverMillions"]==330
    assert x["currentYearCarryoverCapMillions"]==30
    assert x["observed2021BaseCapGrowthOverModeled2020BaseMillions"]==0
    assert x["v19Reconciliation"]["unchanged2020V19PlayersSHA256"]==hashlib.sha256(PLAYERS.read_bytes()).hexdigest()
    assert x["lockedPreservation"]["prospects2021To2029Protected"]==4320
    assert x["lockedPreservation"]["teamsV2AndVisuallyApprovedV25StaffUnmodified"]
    assert x["lockedPreservation"]["existingUserSaveAndProjectIceUnmodified"]
    assert set(x["teamComparisons"])=={"PIT","BAL"}
    for t,v in x["teamComparisons"].items():
        assert v["2021EffectiveCapMillions"]==v["2021BaseCapMillions"]+v["2021CarryoverUsedMillions"]
        assert abs(v["2021CommittedMillions"]+v["2021UnspentMillions"]-330)<.025
        assert v["2021DeadMoneyMillions"]==0
        for year,p in v["futureYearProjection"].items():
            assert p["projectedBaseCapMillions"]==300
            assert p["isCurrentYearEffectiveCapWithCarryover"]==(year=="2021")
            if year!="2021":
                assert abs(p["committedMillionsIncludesPickReserve"]+p["spaceMillions"]-300)<.01
            if p["reservedDraftPicksMillionsAlreadyIncluded"] is not None:
                assert p["committedMillionsIncludesPickReserve"]>=p["reservedDraftPicksMillionsAlreadyIncluded"]
    assert x["teamComparisons"]["PIT"]["futureYearProjection"]["2022"]["spaceMillions"]==123.4
    assert x["teamComparisons"]["BAL"]["futureYearProjection"]["2022"]["spaceMillions"]==24.8
    assert "progressionCurve" not in OUTPUT.read_text()
    assert '"potential":' not in OUTPUT.read_text().lower()
    print("V29 screenshot accounting, V19 preservation, projections PASS")
if __name__=="__main__":main()
