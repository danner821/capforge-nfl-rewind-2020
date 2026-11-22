#!/usr/bin/env python3
"""Independent V36 protection tests — never infer actual game progression."""
import collections,hashlib,json
from build_v36_editor_compatible_growth import (
 SOURCE,OUTPUT,REPORT,V34_GIT_BLOB_SHA1,git_blob_hash,TEAMS,STAFF
)
def main():
    oldraw=SOURCE.read_bytes()
    assert git_blob_hash(oldraw)==V34_GIT_BLOB_SHA1
    orig=json.loads(oldraw);changed=json.loads(OUTPUT.read_bytes())
    report=json.loads(REPORT.read_text())
    assert report["status"]=="V36_EXPERIMENTAL_EDITOR_COMPATIBLE_GROWTH_IMPORT_BUILT_NOT_GAME_VERIFIED"
    assert report["newV36GitBlobSHA1"]==git_blob_hash(OUTPUT.read_bytes())
    assert orig["schemaVersion"]==changed["schemaVersion"]==3
    assert orig["meta"]==changed["meta"]=={"baseSeason":2020}
    assert orig["deadCap"]==changed["deadCap"]==[]
    assert len(orig["players"])==len(changed["players"])==6613
    updated=collections.Counter();already=collections.Counter();peryear=collections.Counter()
    for p,q in zip(orig["players"],changed["players"]):
        assert p["iden"]==q["iden"]
        assert p["pool"]==q["pool"]
        assert {k:v for k,v in p.items() if k!="development"}=={
            k:v for k,v in q.items() if k!="development"}
        assert "progressionCurve" not in q["development"]
        assert q["development"]=={k:v for k,v in p["development"].items() if k!="progressionCurve"}
        assert q["development"]["ovr"]==p["development"]["ovr"]
        assert q["development"].get("potential")==p["development"].get("potential")
        assert "ratings" in q and "contract" in q and "bio" in q
        if "progressionCurve" in p["development"]:updated[p["pool"]]+=1
        else:already[p["pool"]]+=1
        if q["pool"]=="draftClass":peryear[q["bio"]["draftSeason"]]+=1
    assert updated["roster"]+updated["draftClass"]==6311
    assert already["roster"]+already["draftClass"]==302
    assert sum(peryear.values())==4320 and all(peryear[y]==480 for y in range(2021,2030))
    assert sum(q["pool"]=="roster" for q in changed["players"])==2293
    assert report["playersWithNonstandard31EntryCurveRemoved"]==dict(updated)
    assert report["playersAlreadyWithoutCurve"]==dict(already)
    assert report["protected"]["V2TeamsSHA256"]==hashlib.sha256(TEAMS.read_bytes()).hexdigest()
    assert report["protected"]["V25StaffSHA256"]==hashlib.sha256(STAFF.read_bytes()).hexdigest()
    assert not any("actualGameTestPassed" in x for x in report)
    assert '"potential":' not in REPORT.read_text().lower()
    assert "progressionCurve" not in OUTPUT.read_text()
    print(json.dumps({"status":"V36_STRUCTURAL_PROTECTION_GREEN_IN_GAME_UNVERIFIED",
      "players":6613,"curvesRemoved":sum(updated.values()),
      "numericPotentialOverallsIdentical":True,"allOtherPlayerFieldsIdentical":True,
      "nine480ClassesPresent":True},indent=2))
if __name__=="__main__":main()
