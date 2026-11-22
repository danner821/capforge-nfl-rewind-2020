#!/usr/bin/env python3
"""Read-only V38 comparison: CapForge published roster schema vs our V36.

Never print player-specific potential, rating targets, or rankings. This script
cannot test the proprietary CapForge new-franchise initialization or growth.
It does not emit a new Players import or touch any previous version.
"""
from __future__ import annotations

import collections
import hashlib
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
V36 = PREVIEW / "players-2020-nine-class-editor-compatible-growth-v36-TEST.json"
TEAMS = PREVIEW / "teams-2020-roofs-v2.json"
STAFF = PREVIEW / "staff-2020-head-coach-video-matched-v25.json"
OUTPUT = PREVIEW / "v38-public-import-development-schema-audit.json"

# Previously audited, immutable Git object identifiers.
PINNED_V36 = "c0bfebadba5116312449b33076eee0eeecab2a27"
REFERENCES = {
    "published2018": (
        "https://raw.githubusercontent.com/jmansfield96/capforge-custom-rosters/main/player-files/madden-2018-players.json",
        "056228d27bb892b0cce49d511db4e521cd5f35f6",
    ),
    "published2026": (
        "https://raw.githubusercontent.com/jmansfield96/capforge-custom-rosters/main/player-files/madden-27-players.json",
        "9c35138d93b5065b577cfe07521da49503a1e456",
    ),
}


def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def fetch_reference(url: str) -> bytes:
    req = urllib.request.Request(
        url, headers={"User-Agent": "CapForge-NFL-Rewind/Schema-Audit"}
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return response.read()
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            if attempt == 4:
                raise
            time.sleep(min(2 ** attempt, 8))
    raise RuntimeError("Reference download failed")


def profile(document: dict) -> dict:
    players = document.get("players")
    assert isinstance(players, list) and len(players) > 100
    top_keys = collections.Counter()
    dev_shapes = collections.Counter()
    dev_keys = collections.Counter()
    pool_counts = collections.Counter()
    ratings_presence = collections.Counter()
    for player in players:
        assert isinstance(player, dict)
        top_keys.update(player.keys())
        dev = player.get("development") or {}
        assert isinstance(dev, dict)
        dev_shapes[",".join(sorted(dev.keys())) or "(absent)"] += 1
        dev_keys.update(dev.keys())
        pool_counts[str(player.get("pool", "(absent)"))] += 1
        ratings_presence[str(isinstance(player.get("ratings"), dict))] += 1
    return {
        "playerCount": len(players),
        "rootKeys": sorted(document.keys()),
        "playerFieldPresence": dict(sorted(top_keys.items())),
        "developmentFieldPresence": dict(sorted(dev_keys.items())),
        "developmentShapes": dict(sorted(dev_shapes.items())),
        "poolCounts": dict(sorted(pool_counts.items())),
        "hasRatingsObjectCounts": dict(sorted(ratings_presence.items())),
    }


def main() -> None:
    assert V36.is_file() and TEAMS.is_file() and STAFF.is_file()
    frozen = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in (V36, TEAMS, STAFF)
    }
    our_raw = V36.read_bytes()
    assert git_blob_sha(our_raw) == PINNED_V36, "Protected V36 unexpectedly changed"
    our_document = json.loads(our_raw)
    assert our_document["schemaVersion"] == 3
    assert our_document["meta"] == {"baseSeason": 2020}
    assert len(our_document["players"]) == 6613
    our = profile(our_document)
    assert our["poolCounts"].get("roster") == 2293
    assert our["poolCounts"].get("draftClass") == 4320
    assert set(our["developmentFieldPresence"]).issubset({"ovr", "potential"})
    references = {}
    for name, (url, pinned_hash) in REFERENCES.items():
        raw = fetch_reference(url)
        assert git_blob_sha(raw) == pinned_hash, (
            f"{name} published example changed; review reference, never silently shift baseline"
        )
        references[name] = {
            "sourceUrl": url,
            "frozenGitBlobSha1": pinned_hash,
            **profile(json.loads(raw)),
        }

    reference_dev_keys = set().union(
        *(set(v["developmentFieldPresence"]) for v in references.values())
    )
    reference_player_keys = set().union(
        *(set(v["playerFieldPresence"]) for v in references.values())
    )
    report = {
        "status": "V38_STATIC_SCHEMA_FORENSICS_ONLY__ENGINE_BEHAVIOR_NOT_VERIFIED",
        "baseSeason": 2020,
        "frozenV36GitBlobSha1": PINNED_V36,
        "frozenSourceFilesSha256": frozen,
        "importValidationPreviouslyReportedGreen": True,
        "V36GameGrowthTestUserReportedFailed": True,
        "publishedSamples": references,
        "ourV36Shape": our,
        "comparison": {
            "v36DevelopmentKeysAbsentFromBothPublishedExamples":
                sorted(set(our["developmentFieldPresence"]) - reference_dev_keys),
            "v36PlayerKeysAbsentFromBothPublishedExamples":
                sorted(set(our["playerFieldPresence"]) - reference_player_keys),
            "publishedDevelopmentKeysAbsentFromV36":
                sorted(reference_dev_keys - set(our["developmentFieldPresence"])),
            "publishedPlayerKeysAbsentFromV36":
                sorted(reference_player_keys - set(our["playerFieldPresence"])),
        },
        "interpretation": (
            "Schema-key overlap is only input compatibility evidence. It cannot "
            "establish true or staff-read potential, dynamic future growth, engine "
            "normalization at career creation, or the effect of editor Save."
        ),
        "nextDiscriminator": (
            "In a disposable ARCADE 2020 V36/V2/V25 import without editor Save, "
            "compare the Bills preview, Week 1 card/editor Future Growth and "
            "midseason true ratings. If the true 99 ceiling falls there, ask "
            "CapForge developer to inspect new-game vs editor-save hydration."
        ),
        "mutations": "None: no new Players version, no potential or other player edits.",
    }
    rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if OUTPUT.exists():
        assert OUTPUT.read_text() == rendered, "Previously published V38 report changed"
    else:
        OUTPUT.write_text(rendered)
    for path in (V36, TEAMS, STAFF):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == frozen[path.name]
    # Never echo any numeric hidden potential or per-player dev records.
    print(json.dumps({
        "status": report["status"],
        "referencePlayerCounts": {
            name: value["playerCount"] for name, value in references.items()
        },
        "v36PlayerCount": our["playerCount"],
        "v36DevelopmentKeysMissingFromReferences":
            report["comparison"]["v36DevelopmentKeysAbsentFromBothPublishedExamples"],
        "noRosterMutation": True,
        "actualInGameGrowthVerified": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
