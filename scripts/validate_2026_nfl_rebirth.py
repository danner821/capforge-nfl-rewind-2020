#!/usr/bin/env python3
"""Validate isolated NFL Rebirth 2026 Draft Day import assets.

Static JSON validation ONLY. A pass does not establish CapForge game-side
Draft Day acceptance, player drafting, editor-save behavior, or potential retention.
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
PLAYERS_PATH = PREVIEW / "players-2026-nfl-rebirth-480-fantasy-draft-TEST.json"
TEAMS_PATH = PREVIEW / "teams-2026-nfl-rebirth-TEST.json"
MANIFEST_PATH = PREVIEW / "nfl-rebirth-2026-draft-manifest.json"

def main():
    obj = json.loads(PLAYERS_PATH.read_text())
    teams_obj = json.loads(TEAMS_PATH.read_text())
    manifest = json.loads(MANIFEST_PATH.read_text())
    assert obj["schemaVersion"] == 3
    assert obj["meta"]["baseSeason"] == 2026
    assert "deadCap" not in obj, "Reset universe must not inherit 2026 NFL dead cap"
    players = obj["players"]
    teams = teams_obj["teams"]
    assert len(teams) == 32
    by_abbr = {t["abbr"]: t for t in teams}
    assert len(by_abbr) == 32
    assert len({t["teamId"] for t in teams}) == 32
    assert len(players) == 2652
    assert len({p["iden"] for p in players}) == len(players)
    by_pool = collections.Counter(p["pool"] for p in players)
    assert dict(by_pool) == {"roster": 1472, "draftClass": 480, "freeAgent": 700}, by_pool

    fictional = [p for p in players if p["pool"] == "roster"]
    by_team = collections.Counter(p["teamAbbr"] for p in fictional)
    assert set(by_team) == set(by_abbr)
    assert set(by_team.values()) == {46}
    positions = {
        "QB": 2, "RB": 3, "WR": 6, "TE": 3, "OT": 4,
        "OG": 4, "C": 2, "DE": 3, "DT": 3, "EDGE": 3,
        "LB": 4, "CB": 4, "S": 3, "K": 1, "P": 1,
    }
    assert sum(positions.values()) == 46
    for team in by_abbr:
        group = [p for p in fictional if p["teamAbbr"] == team]
        assert collections.Counter(p["position"] for p in group) == positions
        assert len({p["surname"] for p in group}) >= 40, "Fictional names lack variety for " + team
        for p in group:
            assert p["teamId"] == by_abbr[team]["teamId"]
            assert p["development"]["ovr"] >= 58
            assert p["development"]["ovr"] <= 68
            assert p["development"]["potential"] <= 71
            assert p["development"]["potential"] >= p["development"]["ovr"]
            assert p["contract"]["years"] >= 1
            assert p["contract"]["salary"] >= 850000
            assert p["bio"]["draftSeason"] <= 2025
    assert len({(p["forename"], p["surname"]) for p in fictional}) == 1472

    drafted = [p for p in players if p["pool"] == "draftClass"]
    assert len(drafted) == 480
    for p in drafted:
        assert p["bio"]["draftSeason"] == 2026
        assert p["bio"]["draftNum"] == -1
        assert p["development"]["potential"] >= p["development"]["ovr"]
        assert "teamAbbr" not in p and "teamId" not in p
        assert "contract" not in p

    fa = [p for p in players if p["pool"] == "freeAgent"]
    assert len(fa) == 700
    assert all("teamAbbr" not in p and "teamId" not in p for p in fa)
    assert all("contract" not in p for p in fa)

    expected_real_draft = set(manifest["controls"]["allSource2026DraftIds"])
    expected_fa = set(manifest["controls"]["allSource2026FreeAgentIds"])
    advanced = manifest["advanced2027"]
    advanced_ids = {entry["id"] for entry in advanced}
    assert len(advanced) == len(advanced_ids) == 10
    assert len(expected_real_draft) == 470
    assert len(expected_fa) == 700
    assert len(expected_real_draft & expected_fa) == 0
    actual_draft = {p["iden"] for p in drafted}
    assert actual_draft == expected_real_draft | advanced_ids
    assert {p["iden"] for p in fa} == expected_fa
    for spec in advanced:
        matches = [p for p in drafted if p["iden"] == spec["id"]]
        assert len(matches) == 1
        p = matches[0]
        assert p["forename"] + " " + p["surname"] == spec["name"]
        assert p["development"] == spec["development"]
        assert p["position"] == spec["position"]
        assert p["bio"]["college"] == spec["college"]

    original_kinds = collections.Counter(p["position"] for p in drafted if p["iden"] in expected_real_draft)
    assert original_kinds == manifest["selectionQuotas"], (original_kinds, manifest["selectionQuotas"])
    assert manifest["sources"]["public2026PlayersGitBlob"] == "9c35138d93b5065b577cfe07521da49503a1e456"
    assert manifest["sources"]["historical2027FutureGitBlob"] == "b69f4643932460e0369765e0d7d49f9e361420e4"

    print(json.dumps({
        "status": "STATIC_VALIDATION_PASS_GAMEPLAY_UNVERIFIED",
        "totalPlayers": len(players),
        "pools": dict(by_pool),
        "teams": len(by_team),
        "fictionalPerTeam": 46,
        "real2026Draftees": 470,
        "advanced2027Draftees": 10,
        "real2026FreeAgents": 700,
        "maxFictionalOVR": max(p["development"]["ovr"] for p in fictional),
        "maxFictionalPotential": max(p["development"]["potential"] for p in fictional),
    }, indent=2))

if __name__ == "__main__":
    main()
