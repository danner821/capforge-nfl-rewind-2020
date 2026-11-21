#!/usr/bin/env python3
"""Regression: V24 must never change staff roles or per-role sparse fields."""
from __future__ import annotations
import json
from collections import Counter
from build_v24_role_safe_staff_gallery import V16,BASE,OUTPUT,REPORT,PRIORITY,read

def main():
    old=read(BASE); new=read(OUTPUT); green=read(V16); report=read(REPORT)
    assert len(old)==len(new)==len(green)==672
    assert report["status"]=="V24_ROLE_SAFE_STAFF_GALLERY_CI_PASS_GAME_IMPORT_PENDING_TEST_ONLY"
    known={x["bio"]["portraitId"] for x in green if x["bio"].get("portraitId")}
    assert len(known)==len(report["portraitToMarketLabel"])==73
    assert set(report["portraitToMarketLabel"])==known
    assert all(x in known for x in PRIORITY)
    old_by_id={x["iden"]:x for x in old}
    assert len(old_by_id)==672 and len({x["iden"] for x in new})==672
    changed=Counter()
    ids=set()
    for item in new:
        previous=old_by_id[item["iden"]]
        # Main regression: NEVER reinterpret scout/doctor/OC role as HC.
        assert item["role"]==previous["role"],"V23 role-switching regression"
        assert item["pool"]==previous["pool"]
        assert item.get("teamAbbr")==previous.get("teamAbbr")
        assert item.get("teamId")==previous.get("teamId")
        assert item["styles"]==previous["styles"]
        assert item["skills"]==previous["skills"]
        assert item["development"]==previous["development"]
        assert item["personality"]==previous["personality"]
        assert item["contract"]==previous["contract"]
        if item["pool"]=="staff":
            assert item==previous,"Historical employed staff changed!"
            continue
        assert item["pool"]=="freeAgent"
        if item!=previous:
            changed[item["role"]]+=1
            assert item["role"] in ("headCoach","offCoordinator")
            assert item["forename"]=="Avatar"
            assert item["surname"].startswith("Pic")
            pic=item["bio"]["portraitId"]
            assert pic in known and pic not in ids
            ids.add(pic)
            assert item["forename"]+" "+item["surname"]==report["portraitToMarketLabel"][pic]["displayName"]
            assert {k:v for k,v in item.items() if k not in ("forename","surname","bio")}=={
                k:v for k,v in previous.items() if k not in ("forename","surname","bio")}
            assert {k:v for k,v in item["bio"].items() if k!="portraitId"}=={
                k:v for k,v in previous["bio"].items() if k!="portraitId"}
        else:
            assert item==previous
    assert changed==Counter({"headCoach":64,"offCoordinator":9})
    assert ids==known
    assert report["labeledDiagnosticFreeAgents"]==73
    assert report["employedStaffUnchanged"]==224
    assert report["unchangedFictionalFreeAgents"]==375
    assert sum(x["pool"]=="freeAgent" for x in new)==448
    assert report["preservation"]["allStaffRoles"] is True
    print(json.dumps({
      "status":"V24_STAFF_SPARSE_SCHEMA_REGRESSION_PASS_IN_GAME_PENDING",
      "portraitIds":len(ids),
      "diagnosticFreeAgents":sum(changed.values()),
      "unchangedEmployedStaff":224,
      "originalRolesPreserved":True,
      "changedRoleDistribution":dict(changed),
    },indent=2))

if __name__=="__main__":
    main()
