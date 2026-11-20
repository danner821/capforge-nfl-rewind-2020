#!/usr/bin/env python3
"""V15 checks: preserve approved V12 through 2027, validate future cohorts and audit."""
import json
import re
from collections import Counter
from pathlib import Path

from build_v15_future_audit import BASE,OUTPUT,REPORT,PRIORITY,canonical,pname,school_matches
from capforge_ovr import estimate

def main():
    base=json.loads(BASE.read_text())
    out=json.loads(OUTPUT.read_text())
    report=json.loads(REPORT.read_text())
    old=base["players"]
    new=out["players"]
    assert len(old)==len(new)==6613
    assert out["schemaVersion"]==3 and out["meta"]["baseSeason"]==2020
    assert out["deadCap"]==base["deadCap"]==[]
    old_approved={p["iden"]:p for p in old if p["pool"]=="roster" or p["bio"]["draftSeason"]<=2027}
    ids={p["iden"]:p for p in new}
    assert len(old_approved)==5653 and len(ids)==6613
    for uid,p in old_approved.items():
        assert ids.get(uid)==p,"Previously approved roster or 2021–2027 class was changed"
    counts=Counter(p["bio"]["draftSeason"] for p in new if p["pool"]=="draftClass")
    assert all(counts[y]==480 for y in range(2021,2030))
    assert {p["teamAbbr"] for p in new if p["pool"]=="roster"}=={p["teamAbbr"] for p in old if p["pool"]=="roster"}
    assert sum(p["pool"]=="roster" for p in new)==2293
    seen=set()
    for p in new:
        assert 140<=p["bio"]["weightLbs"]<=400
        pid=p["bio"].get("portraitId")
        assert pid is None or re.fullmatch(r"portrait-\d{4}",pid)
        if p["pool"]=="draftClass":
            assert not p.get("teamAbbr") and not p.get("teamId")
            if p["bio"]["draftSeason"]>=2028:
                key=pname(p)
                assert key not in seen, "Duplicate future prospect: "+key
                seen.add(key)
    for y,priority in PRIORITY.items():
        records={pname(p):p for p in new if p["pool"]=="draftClass"
                 and p["bio"]["draftSeason"]==y}
        assert len(records)==480
        for name,pos,school in priority:
            p=records.get(canonical(name))
            assert p is not None, "Missing current top prospect: "+name
            assert p["position"]==pos, "Wrong position: "+name
            assert school_matches(p["bio"].get("college",""),school), "Wrong school: "+name
            assert abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])<=2, "OVR mismatch: "+name
    assert report["status"]=="V15_STRUCTURAL_SCOUTING_AND_PORTRAIT_AUDIT_PASS_GAME_IMPORT_UNTESTED"
    assert report["preservedApproved2020Through2027"]==5653
    assert report["totalPlayers"]==6613
    assert report["coverageTargets"]=={str(y):len(PRIORITY[y]) for y in (2028,2029)}
    for y in ("2028","2029"):
        assert report["portraitAuditAfter"][y]["class_players"]==480
        audit=report["portraitAuditAfter"][y]
        assert audit["explicit_cartoon_portrait_ids"]+audit["default_game_generated_portraits"]==480
        assert audit["face_likeness_verified_by_app"] is False
        assert audit["featured_names_with_explicit_cartoon_portraits"]+audit["featured_names_needing_visual_review"]==len(PRIORITY[int(y)])
    print(json.dumps({
        "status":"V15_PASSED_CI_ONLY_GAME_IMPORT_PENDING",
        "protected":5653,
        "2028_featured":len(PRIORITY[2028]),
        "2029_featured":len(PRIORITY[2029]),
        "drafts_480_each":9,
        "portrait_face_likeness":"requires CapForge visual review",
        "report":str(REPORT.name),
    },indent=2))
if __name__=="__main__":main()
