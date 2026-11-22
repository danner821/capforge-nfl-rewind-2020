#!/usr/bin/env python3
"""V31 guard against turning real payroll screens into invented gameplay proof."""
import hashlib,json
from audit_v31_v30_2021_cap_rollover import (
OBS,OLD,V30,REPORT,PLAYERS,TEAMS,STAFF
)
def main():
    out=json.loads(REPORT.read_text())
    raw=json.loads(OBS.read_text())
    old=json.loads(OLD.read_text())
    assert out["status"]=="V31_USER_VIDEO_V30_2020_TO_2021_SEASON_ROLLOVER_OBSERVED_ALL_THREE_TEAM_CAPS_LEGAL"
    assert out["game2021Week1Observed"] and out["allThreeTeamsCapPositive"]
    assert not out["specificFAAndDraftMechanicsIndependentlyVerified"]
    assert not out["2022AndFutureActualGameplayVerified"]
    assert not out["v30PermanentFranchiseCertified"]
    assert set(out["teamComparisons"])=={"PIT","BAL","JAX"}
    for team,entry in out["teamComparisons"].items():
        x=raw["teamScreens"][team]
        start=old["teams"][team]
        assert x["spaceM"]==entry["2021Week1AvailableM"]
        assert x["committedM"]+x["spaceM"]==330
        assert start["committed"]+start["space"]==300
        assert entry["2020To2021SpaceChangeM"]==round(x["spaceM"]-start["space"],3)
        assert x["year2022"]["committedM"]+x["year2022"]["spaceM"]==300
        assert x["year2022"]["committedM"]>=x["year2022"]["pickReserveAlreadyCommittedM"]
    assert out["preservedHashes"]["V30PlayersSHA256"]==hashlib.sha256(PLAYERS.read_bytes()).hexdigest()
    assert out["preservedHashes"]["V2TeamsSHA256"]==hashlib.sha256(TEAMS.read_bytes()).hexdigest()
    assert out["preservedHashes"]["V25StaffSHA256"]==hashlib.sha256(STAFF.read_bytes()).hexdigest()
    assert out["v30PlayersRecordsStillProtected"]
    assert '"potential":' not in REPORT.read_text().lower()
    print("V31 real game report, 3-team 2021 $330M cap, 2022 $300M forecast and frozen imports validated")
if __name__=="__main__":main()
