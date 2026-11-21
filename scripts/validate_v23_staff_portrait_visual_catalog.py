#!/usr/bin/env python3
"""Ensure V23 diagnostic labels 73 known staff IDs and changes NO real coaches."""
import json
from collections import Counter
from build_v23_staff_portrait_visual_catalog import BASE,GREEN,OUTPUT,REPORT,read

def main():
    before=read(BASE); after=read(OUTPUT); green=read(GREEN); d=read(REPORT)
    assert len(before)==len(after)==len(green)==672
    assert d["status"]=="V23_DIAGNOSTIC_ONLY_NOT_FOR_PERMANENT_SAVES_GAME_VISUAL_CATALOG_PENDING"
    approved={x["iden"]:x for x in before}
    gallery=set(d["supportedPortraitIds"])
    valid={x["bio"]["portraitId"] for x in green if x["bio"].get("portraitId")}
    assert len(gallery)==len(valid)==73 and gallery==valid
    assert "portrait-0798" not in gallery
    adjusted=0
    changed_only_free_agents=0
    seen_portraits=set()
    for x in after:
        old=approved[x["iden"]]
        if old["pool"]=="staff":
            assert x==old,"Real 2020 team coach modified by diagnostic file"
            continue
        assert old["pool"]==x["pool"]=="freeAgent"
        if x!=old:
            changed_only_free_agents+=1
            assert x["forename"]=="Avatar"
            assert x["surname"].startswith("Pic")
            assert x["role"]=="headCoach"
            assert x["bio"]["portraitId"] in gallery
            assert x["bio"]["portraitId"] not in seen_portraits
            assert x["forename"]+" "+x["surname"]==d["portraitToMarketLabel"][x["bio"]["portraitId"]]["displayName"]
            assert all(v==95 for v in x["skills"].values())
            assert x["development"]["ovr"]==95
            assert x["development"]["potential"]==95
            assert x["contract"]==old["contract"]
            seen_portraits.add(x["bio"]["portraitId"])
            adjusted+=1
        else:
            assert x==old
    assert adjusted==changed_only_free_agents==73 and seen_portraits==gallery
    assert len([x for x in after if x["pool"]=="staff"])==224
    assert len([x for x in after if x["pool"]=="freeAgent"])==448
    assert d["occupiedStaffUnmodified"]==224 and d["otherFreeAgentsUnmodified"]==375
    assert d["priorV22CoachFacesPreserved"]
    assert "potential" not in d["portraitToMarketLabel"]["portrait-0675"]
    print(json.dumps({
        "status":"V23_VISUAL_CATALOG_CI_PASS_NOT_IN_GAME",
        "staff_portrait_ids_to_identify":73,
        "real_2020_employed_staff_preserved":224,
        "temporary_free_agent_visual_probes":73,
        "other_free_agents_unchanged":375,
        "next_gate":"screen recording of labeled CapForge coach portraits"
    },indent=2))

if __name__=="__main__":main()
