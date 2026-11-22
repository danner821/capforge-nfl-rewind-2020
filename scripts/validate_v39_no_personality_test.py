#!/usr/bin/env python3
"""Independent V39 invariant audit: no change other than optional personality."""
from __future__ import annotations

import collections
import hashlib
import json

from build_v39_no_personality_test import (
    SOURCE, OUTPUT, REPORT, V38, TEAMS, STAFF, FROZEN_V36_GIT_BLOB, git_blob_sha
)


def main() -> None:
    raw = SOURCE.read_bytes()
    assert git_blob_sha(raw) == FROZEN_V36_GIT_BLOB
    source = json.loads(raw)
    changed = json.loads(OUTPUT.read_bytes())
    report = json.loads(REPORT.read_text())
    v38 = json.loads(V38.read_text())
    assert report["status"] == "V39_EXPERIMENTAL_IMPORT_NOT_TESTED_IN_CAPFORGE"
    assert report["onlyChangedPlayerField"] == "personality"
    assert report["newV39GitBlobSha1"] == git_blob_sha(OUTPUT.read_bytes())
    assert report["frozenV36Sha256"] == hashlib.sha256(raw).hexdigest()
    assert v38["ourV36Shape"]["playerFieldPresence"]["personality"] == 6311

    assert set(changed) == set(source)
    assert {k: v for k, v in changed.items() if k != "players"} == {
        k: v for k, v in source.items() if k != "players"
    }
    assert len(source["players"]) == len(changed["players"]) == 6613

    counts = collections.Counter()
    years = collections.Counter()
    roster_teams = set()
    unique_ids = set()
    for prior, current in zip(source["players"], changed["players"]):
        assert current == {k: v for k, v in prior.items() if k != "personality"}
        assert current["iden"] == prior["iden"]
        assert current["iden"] not in unique_ids
        unique_ids.add(current["iden"])
        assert "personality" not in current
        assert current["development"] == prior["development"]
        assert current["ratings"] == prior["ratings"]
        assert current["contract"] == prior["contract"]
        assert current["bio"] == prior["bio"]
        assert current.get("teamAbbr") == prior.get("teamAbbr")
        assert current.get("teamId") == prior.get("teamId")
        assert "progressionCurve" not in current["development"]
        if "personality" in prior:
            counts[prior["pool"]] += 1
        if current["pool"] == "draftClass":
            assert current["bio"]["draftNum"] == -1
            years[current["bio"]["draftSeason"]] += 1
        else:
            roster_teams.add(current["teamAbbr"])

    assert len(unique_ids) == 6613 and len(roster_teams) == 32
    assert sum(counts.values()) == 6311
    assert report["personalityEntriesRemovedByPool"] == dict(counts)
    assert sum(years.values()) == 4320
    assert all(years[year] == 480 for year in range(2021, 2030))
    assert report["futureProspectsBySeason"] == {
        str(year): years[year] for year in range(2021, 2030)
    }
    assert report["protected"]["V2TeamsSha256"] == hashlib.sha256(TEAMS.read_bytes()).hexdigest()
    assert report["protected"]["V25StaffSha256"] == hashlib.sha256(STAFF.read_bytes()).hexdigest()
    assert "inGameVerified" not in report or report["inGameVerified"] is False
    assert '\"potential\":' not in REPORT.read_text().lower()
    print(json.dumps({
        "status": "V39_STATIC_FIELD_LEVEL_INVARIANCE_PASSED__GAME_UNVERIFIED",
        "players": 6613,
        "removedPersonalityFields": 6311,
        "otherPlayerFieldsIncludingDevelopmentBytewiseSemanticEquality": True,
        "futureSeasons": 9,
        "perFutureSeason": 480,
        "existingFilesUntouched": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
