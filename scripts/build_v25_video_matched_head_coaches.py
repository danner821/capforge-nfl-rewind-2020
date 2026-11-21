#!/usr/bin/env python3
"""V25: 2020 real head-coach cartoon curation from user-recorded V24 gallery.

V22 import passed in-game but visual likenesses were bad. User provided a
33.2-second screen recording of 64 labeled Head Coach avatar faces from V24.
Curated candidate IDs are grounded in actually seen cartoons, not staff age
metadata or guessed player-avatar IDs. This is a NEW versioned staff-only
import and still needs user validation of actual employed coach cards.
"""
from __future__ import annotations
import copy,json,re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
BASE=PREVIEW/"staff-2020-valid-coach-portraits-v22.json"
GREEN=PREVIEW/"staff-2020-coaching-v16.json"
GALLERY=PREVIEW/"v24-staff-portrait-gallery-map.json"
COACHES=ROOT/"data/coaches_2020_head_coach_birthdates.json"
PROPOSALS=ROOT/"data/coaches_2020_v25_video_verified_portrait_candidates.json"
OUTPUT=PREVIEW/"staff-2020-head-coach-video-matched-v25.json"
REPORT=PREVIEW/"v25-head-coach-cartoon-audit.json"

def read(p):return json.loads(p.read_text(encoding="utf-8"))

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Partial V25 outputs; refusing overwrite")
        print("V25 frozen outputs exist; no changes made")
        return
    source=read(BASE)
    accepted=read(GREEN)
    gallery=read(GALLERY)
    bio=read(COACHES)
    proposals=read(PROPOSALS)
    assert proposals["version"]=="V25"
    assert len(source)==len(accepted)==672
    assert len({s["iden"] for s in source})==672
    assert len(proposals["curations"])==len(bio["teams"])==32
    assert set(proposals["curations"])==set(bio["teams"])
    known={s["bio"]["portraitId"] for s in accepted if s["bio"].get("portraitId")}
    assert len(known)==73
    assert gallery["labeledDiagnosticFreeAgents"]==73
    observed=gallery["portraitToMarketLabel"]
    assert set(observed)==known
    out=copy.deepcopy(source)
    headcoaches={(s["teamAbbr"],s["role"]):s for s in out if s["pool"]=="staff" and s["role"]=="headCoach"}
    assert len(headcoaches)==32
    reportmap={}
    for abbr,entry in proposals["curations"].items():
        s=headcoaches[(abbr,"headCoach")]
        name=s["forename"]+" "+s["surname"]
        assert name==bio["teams"][abbr]["name"]
        pid=entry["portraitId"]
        assert re.fullmatch(r"portrait-\d{4}",pid)
        assert pid in known,"Unknown/rejected V21 portrait ID"
        assert observed[pid]["role"]=="headCoach","Portrait not observed on video HC gallery"
        assert observed[pid]["displayName"]=="Avatar Pic"+pid[-4:]
        assert isinstance(entry["videoSecond"],int) and 0<=entry["videoSecond"]<=33
        assert entry["confidence"] in ("high","medium","low")
        assert entry["reviewStatus"].startswith("PROVISIONAL")
        previous=s["bio"].get("portraitId")
        s["bio"]["portraitId"]=pid
        reportmap[abbr]={
            "coach":name,"fromV22":previous or "CapForge default",
            "newStaffPortrait":pid,
            "sourceVideoSecondApprox":entry["videoSecond"],
            "evidence":"label_and_avatar_observed_in_uploaded_V24_screen_recording",
            "confidence":entry["confidence"],
            "inGameEmployedCoachFaceReviewed":False
        }
    previous={s["iden"]:s for s in source}
    changed=0
    for staff in out:
        old=previous[staff["iden"]]
        if staff["pool"]=="staff" and staff["role"]=="headCoach":
            expected=copy.deepcopy(old)
            expected["bio"]["portraitId"]=proposals["curations"][staff["teamAbbr"]]["portraitId"]
            assert expected==staff,"Unexpected HC field changed"
            changed+=(old["bio"].get("portraitId")!=staff["bio"].get("portraitId"))
        else:
            assert staff==old,"Coordinator, doctor, scout or free agent changed!"
    assert changed>=25,"Not enough updated head-coach portraits for 32-team trial"
    assert sum(s["pool"]=="staff" for s in out)==224
    assert sum(s["pool"]=="freeAgent" for s in out)==448
    assert len(reportmap)==32
    assert reportmap["GB"]["fromV22"]=="portrait-0675"
    assert reportmap["GB"]["newStaffPortrait"]=="portrait-0484"
    status="V25_32_VISUALLY_REFERENCED_HC_AVATARS_CI_PASS_INGAME_QA_PENDING"
    OUTPUT.write_text(json.dumps(out,separators=(",",":"))+"\n",encoding="utf-8")
    report={
      "status":status,
      "trialFile":OUTPUT.name,
      "baseStaff":BASE.name,
      "staffCount":len(out),
      "historicalCoachSlots":128,
      "headCoachesAssignedVisuallyReferencedCartoons":32,
      "headCoachCartoonIDsActuallyChangedFromV22":changed,
      "video":"User provided 33-second V24 Head Coach Market scroll; actual cartoon faces were visible beside Avatar Pic#### IDs. Video not redistributed or embedded.",
      "laFleurRepair":{
          "oldPortrait":"portrait-0675",
          "newPortrait":"portrait-0484",
          "reason":"Video revealed bald, dark-bearded face for 0675 and lighter short-haired trimmed-beard face for 0484",
          "gameReviewPending":True,
      },
      "teamSelections":dict(sorted(reportmap.items())),
      "otherRolesPreserved":{
          "remaining96OC_DC_STcoaches":True,
          "teamScoutsAndDoctors":True,
          "freeAgentStaff":True,
          "staffIdentitiesContractsSkills":True,
          "V19PlayersTeamsV2AllDraftClasses":True
      },
      "confidence":dict(Counter(x["confidence"] for x in proposals["curations"].values())),
      "knownCompatibleStaffPortraitIds":len(known),
      "sourceIDsAllSeenInHCMarketVideo":True,
      "nextTest":"NEW disposable 2020 game V19 Players + Teams V2 + V25 Staff. Check Staff 672 green/no warning, Green Bay Matt LaFleur's card first, then other HC portraits. No inference of perfect likeness from CI.",
      "notImplemented":"Coordinator and special teams cartoon matching; separate reference photo review needed, although the known staff ID pool is available.",
      "limitations":[
        "Likeness choices are subjective approximations based on small game cartoons and 2019–20 public coach appearance; do not represent real photos.",
        "Video head-coach market displayed 64 face references, but not the nine additional OC-gallery avatars.",
        "Video observation verifies which face is tied to an ID, not which face is objectively best; user in-game visual approval is still required.",
        "No change to V19 Players, Teams V2, archived V16/V20/V22/V24 staff or any user save."
      ]
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"result":status,"headCoachCandidates":32,"actuallyChanged":changed,
                      "staffRows":len(out),"sourceIDs":len(known),
                      "GBNewPortrait":reportmap["GB"]["newStaffPortrait"],
                      "noCoordinatorOrScoutEdits":True},indent=2))
if __name__=="__main__":
    main()
