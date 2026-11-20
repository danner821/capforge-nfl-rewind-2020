#!/usr/bin/env python3
"""V11 non-destructive import warning / portrait QA on the V10 preview.

The 2020–2029 nine-class V10 import was user-verified in CapForge:
- players[5179] (Dylan Stewart): OVR 79 but game's ratings calculate 77.
- players[4772] (Desmond Watson): 425 lbs becomes 400 lbs importer maximum.
- Arch Manning (2027): the auto-picked cartoon face was visibly unsuitable.

Fix only these three public-facing properties; keep every remaining player
value, team, contract, portrait, potential and progression curve immutable.
Do not overwrite V6/V7/V8/V9/V10 or touch the user's save.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
SOURCE_SEVEN=PREVIEW/"players-2020-seven-class-projection-v10.json"
SOURCE_NINE=PREVIEW/"players-2020-nine-class-projection-v10.json"
OUTPUT_SEVEN=PREVIEW/"players-2020-seven-class-importfix-v11.json"
OUTPUT_NINE=PREVIEW/"players-2020-nine-class-importfix-v11.json"
REPORT=PREVIEW/"v11-import-qa-report.json"

# portrait-0256 belongs to Eli Manning (QB) in the community's hand-curated
# 2018 CapForge player reference. A position-compatible, light-complexioned,
# family-related likeness proxy for Arch; not an authentic Arch headshot.
PORTRAIT_ARCH="portrait-0256"

def find(players,name,year):
    matched=[p for p in players
             if p["forename"]+" "+p["surname"]==name
             and p["pool"]=="draftClass"
             and p["bio"]["draftSeason"]==year]
    if len(matched)!=1:
        raise ValueError(f"V10 source drift: expected one {name} {year}; found {len(matched)}")
    return matched[0]

def patch(path):
    raw=json.loads(path.read_text())
    assert raw["schemaVersion"]==3 and raw["meta"]["baseSeason"]==2020
    players=raw["players"]
    assert len(players) in (5653,6613)
    # Exact indices are grounded in user's nine-year CapForge warning display.
    if len(players)==6613:
        assert players[4772]["forename"]+" "+players[4772]["surname"]=="Desmond Watson"
        assert players[5179]["forename"]+" "+players[5179]["surname"]=="Dylan Stewart"
    dylan=find(players,"Dylan Stewart",2027)
    assert dylan["development"]["ovr"]==79, "Dylan starting OVR was not the user-reported 79"
    # CapForge explicitly says the imported ratings can only produce OVR 77.
    # Preserve ratings, potential and full hidden progression curve unchanged.
    dylan["development"]["ovr"]=77

    watson=find(players,"Desmond Watson",2024)
    assert watson["bio"]["weightLbs"]==425, "Watson source weight unexpected"
    # CapForge's imported player field weightOverrideLbs accepts only 140–400.
    # Keep real-world weight 425 in this audit report, not the in-game field.
    watson["bio"]["weightLbs"]=400

    arch=find(players,"Arch Manning",2027)
    assert arch["position"]=="QB"
    assert "portraitId" not in arch["bio"], "Arch already has a curated portrait"
    arch["bio"]["portraitId"]=PORTRAIT_ARCH
    return raw

def main():
    outputs=(OUTPUT_SEVEN,OUTPUT_NINE,REPORT)
    if any(x.exists() for x in outputs):
        if not all(x.exists() for x in outputs):
            raise RuntimeError("Partial published V11 files detected; never overwrite")
        print("V11 already published; using frozen versioned files")
        return
    seven=patch(SOURCE_SEVEN)
    nine=patch(SOURCE_NINE)
    assert len(seven["players"])==5653 and len(nine["players"])==6613
    for name,yrs,path,payload in (
        ("seven",(2021,2027),OUTPUT_SEVEN,seven),
        ("nine",(2021,2029),OUTPUT_NINE,nine),
    ):
        path.write_text(json.dumps(payload,separators=(",",":"))+"\n")
    report={
        "status":"V11_GITHUB_VALIDATED_PENDING_IN_GAME_TEST",
        "source":"User's V10 CapForge nine-class importer screenshot, 2026-11-20",
        "provenancePortraitArch":"Eli Manning QB portrait in community 2018 CapForge match: https://github.com/jmansfield96/capforge-custom-rosters/blob/main/player-files/madden-2018-players.json",
        "changes":[
          {"player":"Dylan Stewart","draftYear":2027,"property":"displayed overall",
           "from":79,"to":77,"reason":"CapForge calculated 77 using existing unchanged player skills"},
          {"player":"Desmond Watson","draftYear":2024,"property":"CapForge player weight",
           "from":425,"to":400,"reason":"Importer weight limit 400 lb; source observed weight preserved in this public report"},
          {"player":"Arch Manning","draftYear":2027,"property":"CapForge cartoon portrait",
           "from":"automatic","to":PORTRAIT_ARCH,
           "reason":"Manually chosen position-compatible family proxy; visual match requires user confirmation"}
        ],
        "preserved":"Every other V10 field, every player ID, all team assignments, salaries, potentials and progression curves unchanged",
        "exports":{
           "sevenClass":"preview/players-2020-seven-class-importfix-v11.json",
           "nineClass":"preview/players-2020-nine-class-importfix-v11.json"
        },
        "warning":"GitHub structural checks are not proof of CapForge import-warning clearance; user must check a new disposable 2020 league"
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
      "status":report["status"],"sevenPlayerRecords":len(seven["players"]),
      "ninePlayerRecords":len(nine["players"]),
      "targetedCorrections":len(report["changes"]),
      "hiddenProgressionPreserved":True
    },indent=2))

if __name__=="__main__":
    main()
