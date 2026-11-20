#!/usr/bin/env python3
"""V9 NFL-drafted-name audit. Aggregated counts only: no prospect potential."""
import json
from collections import defaultdict
from pathlib import Path
from audit_draft_classes import get_source, norm, ALIASES, MIN_DRAFTED_MATCHES, SOURCE_PAGE

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/"preview/players-2020-six-class-authentic-v9.json"
REPORT=ROOT/"preview/v9-draft-coverage-report.json"

def canonical(name):
    k=norm(name)
    return ALIASES.get(k,k)

def run():
    data=json.loads(PACK.read_text())
    byyear=defaultdict(set)
    for p in data["players"]:
        if p["pool"]=="draftClass":
            y=int(p["bio"]["draftSeason"])
            byyear[y].add(canonical(p["forename"]+" "+p["surname"]))
    picks=get_source()
    stats={}
    for y in range(2021,2027):
        rows=[r for r in picks if int(r["Year"])==y]
        if len(rows)<250:raise RuntimeError("Incomplete external draft results")
        absent=[r for r in rows if canonical(r["Selection"]) not in byyear[y]]
        missing_early=[r for r in absent if int(r["Round"])<=3]
        found=len(rows)-len(absent)
        if missing_early or found<MIN_DRAFTED_MATCHES[y]:
            raise RuntimeError(f"V9 drafted name coverage regressed in {y}")
        stats[str(y)]={
            "actual_NFL_draft_picks":len(rows),
            "real_picks_represented":found,
            "missing_rounds_1_to_3":len(missing_early),
            "missing_late_round":len(absent),
            "total_class":len(byyear[y])
        }
    out={
        "status":"SIX_480_CLASSES_HISTORIC_DRAFT_NAMES_VERIFIED_NOT_APP_TESTED",
        "source":SOURCE_PAGE,
        "playersFile":"preview/players-2020-six-class-authentic-v9.json",
        "by_year":stats,
        "method":"Name + draft year; real NFL draft destinations not assigned",
        "privacy":"No potential or progression information included"
    }
    REPORT.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2))
if __name__=="__main__":
    run()
