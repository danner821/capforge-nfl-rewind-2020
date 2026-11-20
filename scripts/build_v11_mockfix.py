#!/usr/bin/env python3
"""V11: patch observed CapForge import warnings and 2027 mock-draft omissions.

Inputs: immutable V9/V10 JSON and verifiable 2026 college rosters.
Outputs: NEW, frozen V11 seven/nine-class exports. Never write to V9/V10.
Readiness levels are preseason projections, NOT claims about future NFL careers.
Do not print any individual's hidden potential or progression.
"""
from __future__ import annotations
import copy
import hashlib
import json
import uuid
from collections import Counter, defaultdict
from pathlib import Path

from audit_draft_classes import norm
from build_2020 import development
from build_v10_future import download, normalize_candidate, projected_player, quality, QUOTAS
from capforge_ovr import calibrate, estimate
from expand_v9_drafts import template_library

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
BASE=PREVIEW/"players-2020-six-class-authentic-v9.json"
V10=PREVIEW/"players-2020-nine-class-projection-v10.json"
OUTPUT_SEVEN=PREVIEW/"players-2020-seven-class-mockfix-v11.json"
OUTPUT_NINE=PREVIEW/"players-2020-nine-class-mockfix-v11.json"
REPORT=PREVIEW/"v11-draft-corrections-report.json"
TARGET=480
PROJECTED_YEARS=(2027,2028,2029)
MOCK_SOURCE="https://whynfl.com/2027-nfl-mock-draft-consensus-13-mocks-jeremiah-smith-drew-mestemaker-qb1-nine-arch-manning-november-2026/"
ADDITIONAL_SOURCE="https://www.pff.com/draft/big-board?custom=true"

# Broad Nov 2026 consensus/round-one coverage, not a forced draft pick order.
# Name, position, 2026 school. Never infer a player's future NFL destination.
CONSENSUS_2027=[
 ("Jeremiah Smith","WR","Ohio State"),
 ("Colin Simmons","EDGE","Texas"),
 ("Leonard Moore","CB","Notre Dame"),
 ("Dylan Stewart","EDGE","South Carolina"),
 ("Drew Mestemaker","QB","Oklahoma State"),
 ("Charlie Becker","WR","Indiana"),
 ("Darian Mensah","QB","Miami"),
 ("Jordan Seaton","OT","LSU"),
 ("Ellis Robinson IV","CB","Georgia"),
 ("Will Echoles","DT","Ole Miss"),
 ("Cam Coleman","WR","Texas"),
 ("Trevor Goosby","OT","Texas"),
 ("Ashton Hampton","CB","Clemson"),
 ("Trey'Dez Green","TE","LSU"),
 ("Trinidad Chambliss","QB","Ole Miss"),
 ("Nick Marsh","WR","Indiana"),
 ("Chris Cole","LB","Georgia"),
 ("CJ Carr","QB","Notre Dame"),
 ("Jadan Baugh","RB","Florida"),
 ("Yhonzae Pierre","EDGE","Alabama"),
 ("Xavier Gilliam","DT","Tennessee"),
 ("Kelley Jones","CB","Mississippi State"),
 ("Dante Moore","QB","Oregon"),
 ("KJ Bolden","S","Georgia"),
 ("Greg Johnson","OG","Minnesota"),
 ("Jamari Johnson","TE","Oregon"),
 ("Arch Manning","QB","Texas"),
 ("David Stone","DT","Oklahoma"),
 ("KJ Duff","WR","Rutgers"),
 ("Ryan Coleman-Williams","WR","Alabama"),
 ("Trevor Lauck","OT","Iowa"),
 ("Brauntae Johnson","S","Notre Dame"),
]
# Small, documented subset of headshot-compatible built-in CapForge portraits
# already accepted in V9. Similar-looking *cartoon* faces, not photographic
# likenesses or verified exact player identities. Must match QB position.
PORTRAIT_QB_REFERENCES={
    "archmanning":"Joe Burrow",           # short brown hair, lighter complexion
    "drewmestemaker":"Mac Jones",          # short brown hair, lighter complexion
    "cjcarr":"Zach Wilson",                # short lighter-brown hair, lighter complexion
}
# Verified 2027 scouting/roster data when the 2026 roster feed lacks a player.
# Dimensions omitted here are estimated from positional templates, not asserted.
MEASUREMENTS={
    "charliebecker":(76,208),
    "drewmestemaker":(76,211),
    "cjcarr":(74,215),
}

def canonical(s):
    return norm(s)

def fullname(p):
    return p["forename"]+" "+p["surname"]

def digest(s):
    return hashlib.sha256(s.encode("utf8")).digest()

def reference_portraits(base):
    wanted=set(PORTRAIT_QB_REFERENCES.values())
    index={fullname(p):p["bio"]["portraitId"] for p in base
           if p["position"]=="QB" and fullname(p) in wanted and
              "portraitId" in p["bio"]}
    assert wanted==set(index),f"Missing validated reference portraits: {wanted-set(index)}"
    return index

def candidate_from_mock(name,pos,school,source_by_key,used_v9_names):
    key=canonical(name)
    options=source_by_key.get(key,[])
    best=next((x for x in options if x["college"].casefold()==school.casefold()),None)
    if best is None and options:best=options[0]
    if best is not None:
        c=copy.deepcopy(best)
        c["draft"]=2027
        c["name"]=name
        c["pos"]=pos
        c["college"]=school
        if key in MEASUREMENTS:
            h,w=MEASUREMENTS[key];c["height"]=h;c["weight"]=w
        return c,"2026_college_roster"
    # This person's name, school and position are independently documented
    # in the published 2027 mock source. No fake identity is generated.
    ident="verified-2027-mock:"+key
    h,w=MEASUREMENTS.get(key,(74,215))
    return {"id":ident,"key":key,"name":name,"college":school,
            "draft":2027,"class":3,"pos":pos,
            "height":h,"weight":w,"seed":digest(ident)}, "2027_published_mock"

def adjust_scout_readiness(p,desired,reposition=False):
    """Conservative readiness updates; never guarantee future success."""
    previous=int(p["development"]["ovr"])
    target=desired if (reposition or previous<desired) else previous
    if canonical(fullname(p))=="dylanstewart":
        # User's V10 screenshot: CapForge says imported 79 can only reach 77.
        target=77
    if target!=previous or reposition:
        ratings,adjusted,_,estimate_after=calibrate(p["position"],p["ratings"],target)
        # Avoid requesting an OVR that the imported attributes cannot reach.
        safe=min(adjusted,int(round(estimate_after)))
        if canonical(fullname(p))=="dylanstewart":safe=min(safe,77)
        p["ratings"]=ratings
        age=int(p["bio"]["age"])
        # These remain modeled future development, not past career hindsight.
        past_ceiling=int(p["development"]["potential"])
        p["development"]=development(safe,age,max(safe,past_ceiling))
    return p

def main():
    frozen=(OUTPUT_SEVEN,OUTPUT_NINE,REPORT)
    if any(p.exists() for p in frozen):
        if not all(p.exists() for p in frozen):
            raise RuntimeError("Partial V11 publication; refuse overwrite")
        print("Frozen V11 preview already published; no mutation")
        return
    data=json.loads(V10.read_text())
    v9=json.loads(BASE.read_text())
    assert data["schemaVersion"]==3 and data["meta"]["baseSeason"]==2020
    assert len(data["players"])==6613 and len(v9["players"])==5173
    assert data["players"][:5173]==v9["players"], "V9 baseline changed"
    base=copy.deepcopy(v9["players"])
    existing=copy.deepcopy(data["players"][5173:])
    assert len(existing)==1440
    # CapForge's 400-lb imported body-weight limit: preserve the man's REAL
    # published name; make only the explicitly reported game-valid cap fix.
    weight_fixes=[]
    for p in base+existing:
        if p["bio"].get("weightLbs",0)>400:
            weight_fixes.append({"name":fullname(p),"year":p["bio"]["draftSeason"],
                                 "old":p["bio"]["weightLbs"],"new":400})
            p["bio"]["weightLbs"]=400
    assert len(weight_fixes)==1 and weight_fixes[0]["name"]=="Desmond Watson",weight_fixes
    current={yr:[p for p in existing if p["bio"]["draftSeason"]==yr]
             for yr in PROJECTED_YEARS}
    assert all(len(current[yr])==480 for yr in PROJECTED_YEARS)
    source_rows=download()
    normalized=[normalize_candidate(row) for row in source_rows]
    college=[p for p in normalized if p is not None]
    source_by_key=defaultdict(list)
    for c in college:
        source_by_key[c["key"]].append(c)
    lib=template_library(base)
    portrait_refs=reference_portraits(base)
    baseline_names={canonical(fullname(p)) for p in base}
    original_by_key={canonical(fullname(p)):p for p in existing}
    protected=set()
    target_2027=[]
    changes=[]
    added_ids=set()
    for rank,(name,pos,school) in enumerate(CONSENSUS_2027,1):
        key=canonical(name)
        if key in protected or key in baseline_names:
            raise RuntimeError("2027 consensus duplicates past player: "+name)
        protected.add(key)
        found=original_by_key.get(key)
        if found:
            old_year=found["bio"]["draftSeason"]
            current[old_year].remove(found)
            player=found
            identity_source="v10_projected_college"
        else:
            candidate,identity_source=candidate_from_mock(name,pos,school,source_by_key,baseline_names)
            player=projected_player(candidate,lib)
            added_ids.add(player["iden"])
            old_year=None
        old_pos=player["position"]
        player["position"]=pos
        player["bio"]["college"]=school
        player["bio"]["draftSeason"]=2027
        # 2027 rank is a rough projection, not an actual future draft ranking.
        desired=77 if rank<=8 else 75 if rank<=16 else 73
        adjust_scout_readiness(player,desired,reposition=(old_pos!=pos))
        key=canonical(fullname(player))
        if key in PORTRAIT_QB_REFERENCES:
            ref=PORTRAIT_QB_REFERENCES[key]
            assert player["position"]=="QB"
            player["bio"]["portraitId"]=portrait_refs[ref]
        elif old_pos!=pos:
            # No longer reuse a portrait tied to an incompatible position.
            player["bio"].pop("portraitId",None)
        target_2027.append(player)
        changes.append({"name":name,"position":pos,"source":identity_source,
                        "from_year":old_year,"to_year":2027,
                        "position_corrected":old_pos!=pos,
                        "portrait_curated":key in PORTRAIT_QB_REFERENCES})
    assert len(target_2027)==len(CONSENSUS_2027)
    # Maintain the same fifteen-position depth distribution for a 480-player
    # class instead of letting extra QBs/WRs crowd out essential personnel.
    year2027=list(target_2027)
    used={canonical(fullname(p)) for p in base+current[2028]+current[2029]+target_2027}
    for pos,quota in QUOTAS.items():
        need=quota-sum(p["position"]==pos for p in year2027)
        if need<0:raise RuntimeError("Consensus watchlist exceeds 2027 "+pos+" quota")
        candidates=sorted(
            (p for p in current[2027] if p["position"]==pos and canonical(fullname(p)) not in used),
            key=lambda p:(-p["development"]["ovr"],canonical(fullname(p)))
        )
        for p in candidates[:need]:
            year2027.append(p);used.add(canonical(fullname(p)))
        need=quota-sum(p["position"]==pos for p in year2027)
        if need:
            fresh=sorted(
                (c for c in college if c["draft"]==2027 and c["pos"]==pos and
                 c["key"] not in used),
                key=lambda c:(-quality(c),c["key"],c["id"]))
            for c in fresh[:need]:
                x=projected_player(c,lib)
                year2027.append(x);used.add(c["key"]);added_ids.add(x["iden"])
            need=quota-sum(p["position"]==pos for p in year2027)
        if need:raise RuntimeError(f"Real 2027 {pos} short by {need}")
    assert len(year2027)==TARGET
    # Replace 2028 players who were moved to 2027 with real 2026 college
    # sophomores rather than retroactively forcing 2027 entries into 2028.
    used={canonical(fullname(p)) for p in base+year2027+current[2028]+current[2029]}
    needed_by_position=Counter(p["position"] for p in original_by_key.values()
                              if p["bio"]["draftSeason"]==2028)
    have_by_position=Counter(p["position"] for p in current[2028])
    for pos,nwant in needed_by_position.items():
        deficit=nwant-have_by_position[pos]
        if deficit<=0:continue
        options=sorted(
            (c for c in college if c["draft"]==2028 and c["pos"]==pos and c["key"] not in used),
            key=lambda c:(-quality(c),c["key"],c["id"]))
        for c in options[:deficit]:
            x=projected_player(c,lib)
            current[2028].append(x);used.add(c["key"]);added_ids.add(x["iden"])
    if len(current[2028])!=480:raise RuntimeError("Not enough 2028 real college candidates")
    if len(current[2029])!=480:raise RuntimeError("2029 class no longer exactly 480")
    final=base+year2027+current[2028]+current[2029]
    ids=[p["iden"] for p in final]
    assert len(ids)==len(set(ids)), "Duplicate player IDs"
    for y in PROJECTED_YEARS:
        assert sum(p["pool"]=="draftClass" and p["bio"]["draftSeason"]==y for p in final)==480
    assert len(final)==6613
    assert all(p["pool"]=="draftClass" for p in final[5173:])
    assert all(p["bio"].get("weightLbs",0)<=400 for p in final)
    for fn,yrs in ((OUTPUT_SEVEN,{2027}),(OUTPUT_NINE,set(PROJECTED_YEARS))):
        output={"schemaVersion":3,"meta":{"baseSeason":2020},
                "players":base+[p for p in final[5173:] if p["bio"]["draftSeason"] in yrs],
                "deadCap":[]}
        fn.write_text(json.dumps(output,separators=(",",":"))+"\n")
    report={
      "status":"V11_STRUCTURALLY_VALIDATED_IN_GAME_NOT_TESTED",
      "baseSeason":2020,
      "reference":MOCK_SOURCE,
      "secondary_reference":ADDITIONAL_SOURCE,
      "scope":"Nov 2026 consensus 2027 projected prospect identities; no future draft results asserted",
      "2027_consensus_represented":len(CONSENSUS_2027),
      "selected_adjustments":changes,
      "portrait_rule":"Three QB cartoon portrait IDs selected from user-approved position-compatible V9 player catalog; not actual photo headshots",
      "import_reported_weight_fix":weight_fixes,
      "import_reported_ovr_fix":{"name":"Dylan Stewart","previous":79,"requested_cap":77},
      "class_counts":{str(y):sum(p["pool"]=="draftClass" and p["bio"]["draftSeason"]==y for p in final)
                      for y in range(2021,2030)},
      "seven_class_total":len(base)+480,
      "nine_class_total":len(final),
      "caveats":[
        "Projected future draft eligibility is not verified and can change",
        "Not every player in 2027–2029 is guaranteed to enter that year's NFL draft",
        "Only named/position/college identities are independently documented; new attributes are modeled",
        "No historically accurate 2020 staff/contract audit yet",
        "2027+ year tab and season progression still require in-game verification",
        "Every V9 record except the capped Desmond Watson weight remains unchanged",
        "No individual future potential, hidden progression or forced NFL team assignments in reports"
      ]
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
       "status":report["status"],
       "total_records":report["nine_class_total"],
       "class_counts":report["class_counts"],
       "mock_consensus_prospects":len(CONSENSUS_2027),
       "prospects_newly_matched":sum(c["from_year"] is None for c in changes),
       "prospects_moved_from_later_years":sum(c["from_year"] in (2028,2029) for c in changes),
       "portrait_curations":sum(c["portrait_curated"] for c in changes),
       "import_warning_fixes":2,
    },indent=2))

if __name__=="__main__":
    main()
