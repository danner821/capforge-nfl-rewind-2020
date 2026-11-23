#!/usr/bin/env python3
"""V42 independent, read-only audit for population-limit diagnostic fixtures.

No CapForge engine access; this only validates that diagnostic variants are pure
subsets of the frozen, failed V39 Arcade import. Never print individual potentials.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
SOURCE = PREVIEW / "players-2020-nine-class-no-personality-v39-TEST.json"
A = PREVIEW / "players-2020-v42-A-nfl-only-TEST.json"
B = PREVIEW / "players-2020-v42-B-2021-2023-full-TEST.json"
C = PREVIEW / "players-2020-v42-C-nine-class-160-TEST.json"
D = SOURCE
EXPECTED_V39_BLOB = "b69f4643932460e0369765e0d7d49f9e361420e4"
NOTABLE = {
    "Penei Sewell", "Jeremiah Smith", "Darian Mensah",
    "Arch Manning", "Tavien St Clair", "Akili Smith Jr."
}


def blob_sha(data: bytes) -> str:
    prefix = b"blob " + str(len(data)).encode() + b"\0"
    return hashlib.sha1(prefix + data).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_bytes())


def main() -> None:
    raw = SOURCE.read_bytes()
    assert blob_sha(raw) == EXPECTED_V39_BLOB, "Frozen V39 source changed"
    source = json.loads(raw)
    assert source["schemaVersion"] == 3 and source["meta"] == {"baseSeason": 2020}
    assert len(source["players"]) == 6613
    originals = source["players"]
    by_id = {p["iden"]: p for p in originals}
    assert len(by_id) == len(originals)
    assert Counter(p["pool"] for p in originals) == {"roster": 2293, "draftClass": 4320}
    originals_by_year = Counter(p["bio"]["draftSeason"] for p in originals if p["pool"] == "draftClass")
    assert originals_by_year == Counter({y: 480 for y in range(2021, 2030)})
    original_roster_ids = {p["iden"] for p in originals if p["pool"] == "roster"}
    original_elite_ids = {p["iden"] for p in originals if p["pool"] == "draftClass" and p["development"]["potential"] >= 90}
    original_high_ids = {p["iden"] for p in originals if p["pool"] == "draftClass" and p["development"]["potential"] >= 85}
    assert len(original_elite_ids) == 76 and len(original_high_ids) == 203

    for name, path, length, expected_years in (
        ("A", A, 2293, {}),
        ("B", B, 3733, {y: 480 for y in range(2021, 2024)}),
        ("C", C, 3733, {y: 160 for y in range(2021, 2030)}),
        ("D", D, 6613, {y: 480 for y in range(2021, 2030)}),
    ):
        data = load(path)
        assert {k: v for k, v in data.items() if k != "players"} == {k: v for k, v in source.items() if k != "players"}
        players = data["players"]
        assert len(players) == length
        ids = [p["iden"] for p in players]
        assert len(ids) == len(set(ids))
        assert all(by_id.get(p["iden"]) == p for p in players), f"{name}: player content unexpectedly modified"
        assert ids == [p["iden"] for p in originals if p["iden"] in set(ids)], f"{name}: source ordering modified"
        assert {p["iden"] for p in players if p["pool"] == "roster"} == original_roster_ids
        years = Counter(p["bio"]["draftSeason"] for p in players if p["pool"] == "draftClass")
        assert years == Counter(expected_years), f"{name}: unexpected draft years/count"
        assert all("personality" not in p and "progressionCurve" not in p["development"] for p in players)
        if name == "C":
            assert original_high_ids <= set(ids), "C lost a high-potential prospect"
            assert original_elite_ids <= set(ids), "C lost an elite prospect"
            for y in range(2021, 2030):
                original_positions = {p["position"] for p in originals if p["pool"] == "draftClass" and p["bio"]["draftSeason"] == y}
                selected_positions = {p["position"] for p in players if p["pool"] == "draftClass" and p["bio"]["draftSeason"] == y}
                assert selected_positions == original_positions
            for p in originals:
                if p["pool"] == "draftClass" and f"{p['forename']} {p['surname']}" in NOTABLE:
                    assert p["iden"] in ids
        roster_high = sum(p["pool"] == "roster" and p["development"]["potential"] >= 90 for p in players)
        future_high = sum(p["pool"] == "draftClass" and p["development"]["potential"] >= 90 for p in players)
        print(f"V42 {name}: PASS; players={length}; NFL90+={roster_high}; future90+={future_high}; years={dict(sorted(years.items()))}")
    print("V42 STATIC PASS: all three variants pure V39 subsets; gameplay still unverified")


if __name__ == "__main__":
    main()
