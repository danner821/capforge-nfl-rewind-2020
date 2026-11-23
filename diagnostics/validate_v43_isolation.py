#!/usr/bin/env python3
"""Validate V43 last-resort *diagnostic only* 2020 roster imports.

Only allowed changes from immutable V42-A:
  A: remove development.potential from every player except Bills QB Josh Allen;
  B: set potential = current OVR for all except Bills QB Josh Allen.
Never treat these as permanent franchises.
"""
from __future__ import annotations
import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
SOURCE = PREVIEW / "players-2020-v42-A-nfl-only-TEST.json"
SOURCE_GIT_SHA = "74aecc7993d9cf6c045483c11e2bdafc60662376"
A = PREVIEW / "players-2020-v43-A-josh-only-explicit-TEST.json"
B = PREVIEW / "players-2020-v43-B-only-josh-has-growth-TEST.json"

def read(path: Path) -> dict:
    return json.loads(path.read_text())

def git_hash(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def is_josh(p: dict) -> bool:
    return (p["forename"], p["surname"], p["position"], p["teamAbbr"]) == (
        "Josh", "Allen", "QB", "BUF"
    )

def check() -> None:
    raw = SOURCE.read_bytes()
    assert git_hash(raw) == SOURCE_GIT_SHA, "Unrecognized V42-A source; stop"
    source = read(SOURCE)
    assert source["schemaVersion"] == 3 and source["meta"] == {"baseSeason": 2020}
    assert len(source["players"]) == 2293
    assert all(p["pool"] == "roster" for p in source["players"])
    ids = [p["iden"] for p in source["players"]]
    assert len(ids) == len(set(ids))
    assert sum(is_josh(p) for p in source["players"]) == 1
    assert next(p for p in source["players"] if is_josh(p))["development"] == {
        "ovr": 77, "potential": 99
    }

    for label, path in (("A", A), ("B", B)):
        data = read(path)
        assert all(source[k] == data[k] for k in ("schemaVersion", "meta", "deadCap"))
        assert len(data["players"]) == len(source["players"])
        josh_count = 0
        for original, edited in zip(source["players"], data["players"]):
            expected = copy.deepcopy(original)
            if is_josh(original):
                josh_count += 1
            elif label == "A":
                expected["development"].pop("potential")
            else:
                expected["development"]["potential"] = expected["development"]["ovr"]
            assert edited == expected, f"{label}: unauthorized change to {original['iden']}"
            assert "progressionCurve" not in edited["development"]
            assert "personality" not in edited
        assert josh_count == 1
        assert data["players"][-1]["iden"] == source["players"][-1]["iden"]
        explicit = sum("potential" in p["development"] for p in data["players"])
        growth = sum(p["development"].get("potential",p["development"]["ovr"]) > p["development"]["ovr"] for p in data["players"])
        assert explicit == (1 if label == "A" else 2293)
        assert growth == 1
        assert sum(p["pool"] == "draftClass" for p in data["players"]) == 0
        print(f"V43-{label} OK: 2293 original NFL players; only Josh Allen 77/99 retains positive growth; explicit potential={explicit}; records unchanged except intended potential fields; SHA256={hashlib.sha256(path.read_bytes()).hexdigest()[:16]}")
    print("V43 only validates source semantics, not CapForge engine behavior.")

if __name__ == "__main__":
    check()
