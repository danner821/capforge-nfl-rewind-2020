#!/usr/bin/env python3
"""Offline integrity checks for the disposable NFL Rebirth 2026 import."""
from collections import Counter, defaultdict
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "preview/nfl-rebirth-2026-fantasy-draft-v1-TEST.json"
PROMOTED = (
    "Jeremiah Smith", "Arch Manning", "Drew Mestemaker",
    "Dante Moore", "CJ Carr", "Colin Simmons",
    "Dylan Stewart", "Leonard Moore", "Charlie Becker", "Jordan Seaton",
)
POSITIONS = {
    "QB", "RB", "WR", "TE", "OT", "OG", "C", "DE",
    "EDGE", "DT", "LB", "CB", "S", "K", "P",
}
COUNTS_PER_CLUB = {
    "ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE",
    "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
    "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG",
    "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS",
}


def validate():
    payload = json.loads(FILE.read_text(encoding="utf-8"))
    assert payload["schemaVersion"] == 3
    assert payload["meta"]["baseSeason"] == 2026
    players = payload["players"]
    assert len(players) == 2876
    assert len(set(p["iden"] for p in players)) == len(players)
    assert all(p["position"] in POSITIONS for p in players)
    roster = [p for p in players if p["pool"] == "roster"]
    drafts = [p for p in players if p["pool"] == "draftClass"]
    free = [p for p in players if p["pool"] == "freeAgent"]
    assert (len(roster), len(drafts), len(free)) == (1696, 480, 700)
    by_team = defaultdict(list)
    for p in roster:
        by_team[p["teamAbbr"]].append(p)
        assert isinstance(p["teamId"], int) and p["teamId"] > 0
        assert 58 <= p["development"]["ovr"] <= 68
        assert p["development"]["potential"] <= 70
        assert p["contract"]["years"] == 1
    assert set(by_team) == COUNTS_PER_CLUB
    assert all(len(rows) == 53 for rows in by_team.values())
    ids = {p["teamId"] for p in roster}
    assert len(ids) == 32
    assert len(set(p["forename"] + " " + p["surname"] for p in roster)) == 1696
    for team, rows in by_team.items():
        roles = Counter(p["position"] for p in rows)
        assert all(roles[pos] for pos in POSITIONS), (team, roles)
        assert roles["QB"] >= 2, team
        assert roles["DE"] >= 2 and roles["EDGE"] >= 2 and roles["DT"] >= 2, team
    for p in drafts:
        assert p["bio"]["draftSeason"] == 2026
        assert p["bio"]["draftNum"] == -1
        assert "teamAbbr" not in p and "teamId" not in p
        assert p["contract"]["years"] == 0
        assert p["development"]["potential"] >= p["development"]["ovr"]
    for p in free:
        assert "teamAbbr" not in p and "teamId" not in p
        assert p["contract"]["years"] == 0
    names = [p["forename"] + " " + p["surname"] for p in drafts]
    assert len(set(names)) == 480
    assert all(names.count(name) == 1 for name in PROMOTED)
    assert all(any(p["forename"] + " " + p["surname"] == name and p["bio"]["draftSeason"] == 2026
                   for p in drafts) for name in PROMOTED)
    # We do not interpret importer compatibility from static data checks.
    return {
        "status": "static-valid; CapForge actual Draft Day import NOT YET TESTED",
        "total": len(players),
        "fictional_roster": len(roster),
        "fictional_per_team": 53,
        "fictional_ovr_min": min(p["development"]["ovr"] for p in roster),
        "fictional_ovr_max": max(p["development"]["ovr"] for p in roster),
        "2026_draft_class": len(drafts),
        "accelerated_2027": len(PROMOTED),
        "real_free_agents": len(free),
        "teams": len(by_team),
        "positions_present_every_team": True,
    }


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
