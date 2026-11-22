#!/usr/bin/env python3
"""V39 disposable-game experiment: omit ONLY custom per-player personality.

V36 in-game A/B failed even without nonstandard progression curves. V38
compared 6,613 V36 players to 4,565 published CapForge roster players and
found ONE authored V36-only top-level key: personality, on 6,311 players.
This is a concrete source-format difference, NOT an established bug cause.

Keep imported numeric development, ratings, identity, history, contracts,
portraits, future draft classes and exact team/staff inputs invariant.
Never overwrite or label this experimental file as a permanent-game release.
Never disclose per-player hidden development data to logs or reports.
"""
from __future__ import annotations

import collections
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
SOURCE = PREVIEW / "players-2020-nine-class-editor-compatible-growth-v36-TEST.json"
OUTPUT = PREVIEW / "players-2020-nine-class-no-personality-v39-TEST.json"
REPORT = PREVIEW / "v39-no-personality-import-audit.json"
TEAMS = PREVIEW / "teams-2020-roofs-v2.json"
STAFF = PREVIEW / "staff-2020-head-coach-video-matched-v25.json"
V38 = PREVIEW / "v38-public-import-development-schema-audit.json"

FROZEN_V36_GIT_BLOB = "c0bfebadba5116312449b33076eee0eeecab2a27"


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def transform(doc: dict) -> tuple[dict, dict]:
    assert doc["schemaVersion"] == 3 and doc["meta"] == {"baseSeason": 2020}
    assert doc["deadCap"] == []
    assert len(doc["players"]) == 6613
    out = {key: value for key, value in doc.items() if key != "players"}
    out["players"] = []
    removed = collections.Counter()
    pools = collections.Counter()
    years = collections.Counter()
    for old in doc["players"]:
        assert old["pool"] in ("roster", "draftClass")
        pools[old["pool"]] += 1
        if old["pool"] == "draftClass":
            years[old["bio"]["draftSeason"]] += 1
            assert old["bio"]["draftNum"] == -1
        new = {key: value for key, value in old.items() if key != "personality"}
        if "personality" in old:
            assert isinstance(old["personality"], dict)
            removed[old["pool"]] += 1
        # Exact JSON invariance: anything except our authored optional personality remains.
        assert new == {key: value for key, value in old.items() if key != "personality"}
        assert new["development"] == old["development"]
        assert "progressionCurve" not in new["development"]
        assert old["development"]["ovr"] <= old["development"]["potential"]
        out["players"].append(new)
    assert pools == {"roster": 2293, "draftClass": 4320}
    assert sum(removed.values()) == 6311
    assert sum(years.values()) == 4320
    assert all(years[year] == 480 for year in range(2021, 2030))
    assert all("personality" not in p for p in out["players"])
    assert all(a["iden"] == b["iden"] for a, b in zip(doc["players"], out["players"]))
    return out, {
        "personalityEntriesRemovedByPool": dict(removed),
        "rosteredPlayers": pools["roster"],
        "futureProspects": pools["draftClass"],
        "futureProspectsBySeason": {str(year): years[year] for year in range(2021, 2030)},
    }


def main() -> None:
    raw = SOURCE.read_bytes()
    assert git_blob_sha(raw) == FROZEN_V36_GIT_BLOB, "Frozen V36 source unexpectedly changed"
    evidence = json.loads(V38.read_text())
    assert evidence["status"].startswith("V38_STATIC_SCHEMA_FORENSICS_ONLY")
    assert evidence["ourV36Shape"]["playerFieldPresence"]["personality"] == 6311
    assert evidence["comparison"]["v36PlayerKeysAbsentFromBothPublishedExamples"] == ["personality"]
    assert evidence["comparison"]["v36DevelopmentKeysAbsentFromBothPublishedExamples"] == []
    before = json.loads(raw)
    after, counts = transform(before)
    # Verify original identity, historical draft-pick correction and per-player development.
    for prior, curr in zip(before["players"], after["players"]):
        assert {k: v for k, v in prior.items() if k != "personality"} == curr
    assert all("personality" not in p for p in after["players"])
    report = {
        "status": "V39_EXPERIMENTAL_IMPORT_NOT_TESTED_IN_CAPFORGE",
        "sourceFile": SOURCE.name,
        "outputFile": OUTPUT.name,
        "frozenV36GitBlobSha1": FROZEN_V36_GIT_BLOB,
        "frozenV36Sha256": hashlib.sha256(raw).hexdigest(),
        "sourceV38SchemaAudit": V38.name,
        "onlyChangedPlayerField": "personality",
        "publishedReferencesHaveThisPlayerField": False,
        **counts,
        "protected": {
            "all6613IdsPositionsTeamAssignmentsUnchanged": True,
            "allPlayerDevelopmentNumericFieldsUnchanged": True,
            "everyPlayerRatingUnchanged": True,
            "allContractsAndHistoricalDraftPicksUnchanged": True,
            "allPortraitsAndBiographiesUnchanged": True,
            "allFutureProspectRecordsPreservedExceptPersonality": True,
            "nine480PlayerDraftClassesPreserved": True,
            "V36PlayersImmutable": True,
            "V2TeamsSha256": hashlib.sha256(TEAMS.read_bytes()).hexdigest(),
            "V25StaffSha256": hashlib.sha256(STAFF.read_bytes()).hexdigest(),
            "ProjectIceUnchanged": True,
        },
        "hypothesis": (
            "The custom personality object absent from both published sample imports "
            "could influence a player initialization path. Omitting it may or may "
            "not affect the runtime discrepancy; this is not a verified cause."
        ),
        "gameTestRequired": (
            "Create a NEW disposable 2020 game using V39 Players and unchanged V2 Teams "
            "and V25 Staff, with EXACTLY the same mode/settings as the previous V36 "
            "failed test. Do not Save Changes in Josh Allen's editor. Compare Bills "
            "preview, Week 1, midpoint and end of 2020 future-growth and actual OVR "
            "against the prior untouched V36 outcome. If same failure, halt further "
            "speculative imports and perform the V36 ARCADE mode-controlled discriminator."
        ),
        "warnings": [
            "Changing imported personality information may alter actual in-game behavior even though all development potential numbers are identical.",
            "A schema-compatible JSON import and passing CI cannot establish CapForge growth behavior.",
            "No imported player or existing save can be updated retroactively.",
            "Do not recommend permanent launch without no-editor-save in-game success.",
        ],
    }
    output_bytes = (json.dumps(after, separators=(",", ":")) + "\n").encode()
    report["newV39GitBlobSha1"] = git_blob_sha(output_bytes)
    report_text = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if OUTPUT.exists() or REPORT.exists():
        assert OUTPUT.exists() and REPORT.exists(), "V39 partial publication"
        assert OUTPUT.read_bytes() == output_bytes, "Published V39 import changed"
        assert REPORT.read_text() == report_text, "Published V39 report changed"
    else:
        OUTPUT.write_bytes(output_bytes)
        REPORT.write_text(report_text)
    assert SOURCE.read_bytes() == raw
    print(json.dumps({
        "status": report["status"],
        "rosterEntries": counts["rosteredPlayers"],
        "futureProspects": counts["futureProspects"],
        "personalityOnlyFieldsOmitted": sum(counts["personalityEntriesRemovedByPool"].values()),
        "allNumericDevelopmentAndAllOtherFieldsPreserved": True,
        "inGameVerified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
