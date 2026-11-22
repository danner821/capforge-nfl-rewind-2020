#!/usr/bin/env python3
"""V36 separate CapForge Players TEST: remove nonstandard custom progressionCurve.

Why: A controlled user A/B test of imported Josh Allen (QB) in V34 showed:
  - Unsaved: 99 future growth at 2020 start, Impact card, projected 86 by midseason
    and did not develop as intended after a full season.
  - NEW otherwise-identical save + no-op editor Save before advancing: card
    Franchise, 99 future growth remained after a year and development worked.
The CapForge editor save appears to recompute/normalize player development.
Our 2020 builder invented a 31-entry integer progressionCurve across 6,311
players (Josh Allen begins [409,409,409,174,...]).
Established imported public CapForge roster JSONs for 2018 and 2026 have
NO progressionCurve fields, but use development.ovr/potential.
This suggests our injected curves are not needed and may trigger the bug.

Do not attempt to emulate the proprietary editor or declare the issue fixed.
Remove *only* progressionCurve from every roster/draft player where present,
retaining every numeric OVR and potential exactly, with all attributes, imported
draft positions, contracts, identities, portraits and teams untouched.
This is a DISP0SABLE-GAME candidate, not an in-game proven solution.
"""
from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
SOURCE=PREVIEW/"players-2020-nine-class-draft-history-v34-TEST.json"
OUTPUT=PREVIEW/"players-2020-nine-class-editor-compatible-growth-v36-TEST.json"
REPORT=PREVIEW/"v36-progression-import-compatibility-audit.json"
TEAMS=PREVIEW/"teams-2020-roofs-v2.json"
STAFF=PREVIEW/"staff-2020-head-coach-video-matched-v25.json"

V34_GIT_BLOB_SHA1="b602623bd6e238e2d29ea893773a3c32b21c691a"
PUBLIC_2018_GIT_BLOB_SHA1="056228d27bb892b0cce49d511db4e521cd5f35f6"
PUBLIC_2026_GIT_BLOB_SHA1="9c35138d93b5065b577cfe07521da49503a1e456"

def git_blob_hash(contents:bytes)->str:
    return hashlib.sha1(b"blob "+str(len(contents)).encode()+b"\0"+contents).hexdigest()

def main():
    if OUTPUT.exists() or REPORT.exists():
        assert OUTPUT.exists() and REPORT.exists(),"V36 partial publication; stop"
        print("Existing V36 candidate and report remain immutable")
        return
    raw=SOURCE.read_bytes()
    assert git_blob_hash(raw)==V34_GIT_BLOB_SHA1,"Frozen V34 Players blob changed; stop"
    data=json.loads(raw)
    assert data["schemaVersion"]==3 and data["meta"]=={"baseSeason":2020}
    assert len(data["players"])==6613 and data["deadCap"]==[]
    assert sum(p["pool"]=="roster" for p in data["players"])==2293
    assert sum(p["pool"]=="draftClass" for p in data["players"])==4320
    assert all(p["pool"] in {"roster","draftClass"} for p in data["players"])
    new=copy.deepcopy(data)
    removed=Counter()
    already_no_curve=Counter()
    by_draft_year=Counter()
    with_potential=Counter()
    for p in new["players"]:
        dev=p["development"]
        assert isinstance(dev,dict) and isinstance(dev.get("ovr"),int)
        assert set(dev).issubset({"ovr","potential","progressionCurve"})
        if "potential" in dev:
            assert isinstance(dev["potential"],int)
            assert dev["potential"]>=dev["ovr"]
            with_potential[p["pool"]]+=1
        if "progressionCurve" in dev:
            original=dev.pop("progressionCurve")
            assert isinstance(original,list) and len(original)==31
            assert all(isinstance(x,int) for x in original)
            removed[p["pool"]]+=1
        else:
            already_no_curve[p["pool"]]+=1
        if p["pool"]=="draftClass":
            assert p["bio"]["draftNum"]==-1
            by_draft_year[p["bio"]["draftSeason"]]+=1
    assert removed["roster"]+removed["draftClass"]==6311
    assert already_no_curve["roster"]+already_no_curve["draftClass"]==302
    assert all(by_draft_year[y]==480 for y in range(2021,2030))
    assert sum(by_draft_year.values())==4320
    # Preservation cannot be faked: exact field-level comparison of every record.
    for original,changed in zip(data["players"],new["players"]):
        assert original["iden"]==changed["iden"]
        assert {k:v for k,v in original.items() if k!="development"}=={
            k:v for k,v in changed.items() if k!="development"
        },"Other nondevelopment data changed"
        assert {k:v for k,v in original["development"].items() if k!="progressionCurve"}==changed["development"],"Numerical OVR/potential changed"
        assert "progressionCurve" not in changed["development"]
    # Josh Allen QB was originally 77 OVR / 99 potential; MUST remain untouched.
    allen=[p for p in new["players"] if p["pool"]=="roster" and p["position"]=="QB"
           and p["forename"]=="Josh" and p["surname"]=="Allen"]
    assert len(allen)==1
    assert allen[0]["development"]["potential"]==99
    assert allen[0]["development"]["ovr"]==77
    # The already-fixed Burrow/Jefferson pick metadata MUST survive.
    for name,pick in (("Joe Burrow",1),("Justin Jefferson",22)):
        matches=[p for p in new["players"] if p["pool"]=="roster"
                 and p["forename"]+" "+p["surname"]==name]
        assert len(matches)==1 and matches[0]["bio"]["draftNum"]==pick
    assert new["meta"]==data["meta"] and new["deadCap"]==data["deadCap"]
    report={
      "status":"V36_EXPERIMENTAL_EDITOR_COMPATIBLE_GROWTH_IMPORT_BUILT_NOT_GAME_VERIFIED",
      "inputFile":SOURCE.name,
      "outputFile":OUTPUT.name,
      "originalV34GitBlobSHA1":V34_GIT_BLOB_SHA1,
      "originalV34SHA256":hashlib.sha256(raw).hexdigest(),
      "newV36GitBlobSHA1":None,
      "publicCapForge2018ExampleGitBlobSHA1":PUBLIC_2018_GIT_BLOB_SHA1,
      "publicCapForge2026ExampleGitBlobSHA1":PUBLIC_2026_GIT_BLOB_SHA1,
      "baseSeason":2020,
      "rosterPlayers":2293,
      "draftProspects":4320,
      "draftProspectsPerYear":{str(y):by_draft_year[y] for y in range(2021,2030)},
      "playersWithNonstandard31EntryCurveRemoved":dict(removed),
      "playersAlreadyWithoutCurve":dict(already_no_curve),
      "playersWithOriginalNumericalPotentialPreserved":dict(with_potential),
      "sourceOnlyFieldsRemoved":["development.progressionCurve"],
      "protected":{
        "all6613PlayerIdsTeamsAndPoolUnchanged":True,
        "playerNumericOVRAndPotentialIdentical":True,
        "everyAttributeRatingIdentical":True,
        "allDraftNumbersIncludingCorrectedV34Identical":True,
        "allPlayerContractsAndCapChargesIdentical":True,
        "allFacePortraitsAndBiographiesIdentical":True,
        "allFutureDraftClasses480PerYearPresent":True,
        "V34Immutable":True,
        "V2TeamsSHA256":hashlib.sha256(TEAMS.read_bytes()).hexdigest(),
        "V25StaffSHA256":hashlib.sha256(STAFF.read_bytes()).hexdigest(),
        "ProjectIceUnchanged":True
      },
      "hypothesis":"Nonstandard 31-entry custom progression curves in source import cause runtime 99->86 ceiling drop; editor no-op save normalizes them. Public comparable CapForge imports omit the curve. Removing it may let the engine honor numeric potential via normal initialization.",
      "alternativeHypothesis":"The app import path fails to initialize other derived player data even without a curve, in which case only a CapForge app update/fix can produce equivalent no-op editor save at scale.",
      "gameTestProtocol":[
        "Create a NEW disposable 2020 CapForge game with V36 Players and unchanged V2 Teams/V25 Staff, verify all three validation checks green.",
        "Without opening or saving ANY player editor, read Josh Allen QB initial player card potential tier, 99 ceiling if shown, Trade Center value, and current OVR.",
        "Sim through midseason and end of 2020; WITHOUT saving Josh Allen, inspect his future growth ceiling again, player card tier, and actual OVR progression. Compare against the user's original V34 99->86 unsaved and V34 no-op-save 99-stable controls.",
        "Check at least two other initially mis-labeled high-potential players; no editor save before sim.",
        "If V36 retains intended ceilings/development without editor saves, accept V36 after checking rookies trade values and 2021 class. If not, do not launch real franchise; escalate to CapForge developer with controlled reproduction and leave protected V34/V30 unchanged."
      ],
      "limitations":[
        "Github CI checks JSON structural parity, not CapForge player-growth engine behavior.",
        "Unknown proprietary app logic; do not assume no-op Save is equivalent to removing progressionCurve.",
        "There is no bulk in-game player-editor save API in this repository, and existing imported save data is not retroactively rewritten by a new Players URL.",
        "Using an immutable V36 test file changes the growth-curve configuration by design, but not the authored numeric OVR/ceiling or any of 4,320 future prospect identities."
      ]
    }
    newraw=(json.dumps(new,separators=(",",":"))+"\n").encode()
    report["newV36GitBlobSHA1"]=git_blob_hash(newraw)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==report["originalV34SHA256"]
    OUTPUT.write_bytes(newraw)
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
       "status":report["status"],
       "2020RosterCurvesRemoved":removed["roster"],
       "FutureClassCurvesRemoved":removed["draftClass"],
       "PlayersOriginallyWithoutCurves":sum(already_no_curve.values()),
       "PlayerNumericPotentialOrOVRChanged":0,
       "PlayerContractsRatingsDraftPicksChanged":0,
       "FutureDraftProspectsPreserved":sum(by_draft_year.values())
    },indent=2))

if __name__=="__main__":
    main()
