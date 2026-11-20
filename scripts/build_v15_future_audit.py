#!/usr/bin/env python3
"""V15: source-backed 2028 and provisional 2029 coverage + honest portrait audit.

Preserve approved 2027 (and all older players) exactly. Never overwrite V12.
2029 targets are 2026 top college freshmen, NOT known 2029 draft selections.
No guessing cartoon appearance, skin tone, or unverified portrait IDs.
No individual potential or progression in public audit output.
"""
from __future__ import annotations
import copy
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from build_v12_future import (
    RANKED_2028, key, modeled_player, recalibrate, school_matches,
    ranked_target, hashbytes
)
from build_v10_future import download, normalize_candidate, projected_player, quality
from expand_v9_drafts import template_library
from capforge_ovr import estimate

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
BASE=PREVIEW/"players-2020-nine-class-scoutfix-v12.json"
OUTPUT=PREVIEW/"players-2020-nine-class-scout-audit-v15.json"
REPORT=PREVIEW/"v15-2028-2029-scout-portrait-audit.json"

S_28_BOARD="https://ultimatebigboard.com/nfl/2028/big-board/"
S_28_DEVY="https://www.firstballotff.com/rookie-rankings/2028"
S_29_ROSTER="https://www.thedepthchartcfb.com/recruiting"
S_29_VERIFIED_QB="https://vucommodores.com/sports/football/roster/player/jared-curtis-2"
S_COLLEGE="https://raw.githubusercontent.com/sportsdataverse/cfbfastR-data/main/rosters/csv/cfb_rosters_2026.csv"

# V12 established 30 of 32 early 2028 consensus first-round candidates.
# Another broad early devy view captures 2025-entry offensive standouts.
FUTURE_2028=list(RANKED_2028)+[
    ("Jackson Lloyd","OT","Alabama"),
    ("Hayden Lowe","EDGE","Miami"),
    ("Malachi Toney","WR","Miami"),
    ("Jaime Ffrench Jr.","WR","Michigan"),
    ("Caleb Hawkins","RB","Oklahoma State"),
    ("JJ Buchanan","TE","Michigan"),
    ("Nate Sheppard","RB","Duke"),
    ("Malik Washington","QB","Maryland"),
    ("Donovan Olugbode","WR","Missouri"),
    ("Jaron-Keawe Sagapolutele","QB","California"),
    ("JonAnthony Hall","WR","Stanford"),
    ("Bo Jackson","RB","Ohio State"),
    ("TaRon Francis","WR","West Virginia"),
    ("Andrew Marsh","WR","Michigan"),
    ("Kiotti Armstrong","TE","Texas A&M"),
    ("Kamario Taylor","QB","Mississippi State"),
    ("Vernell Brown III","WR","Florida"),
    ("Nate Roberts","TE","Ohio State"),
    ("Lotzeir Brooks","WR","Alabama"),
    ("Dierre Hill Jr.","RB","Oregon"),
    ("Linkon Cure","TE","Kansas State"),
    ("Kaleb Edwards","TE","Alabama"),
    ("DaSaahn Brame","TE","Tennessee"),
    ("Jordon Davison","RB","Oregon"),
]

# Contemporary 2026 recruiting rank + 2026 college enrollment, treated as
# candidates for *first* NFL eligibility in 2029, not predictive top-2029 picks.
# Two 2026 recruiting aliases use their official displayed roster names.
FRESHMEN_2029=[
    ("Keisean Henderson","QB","Houston"),
    ("Jackson Cantwell","OT","Miami"),
    ("Lamar Brown","DT","LSU"),
    ("Jared Curtis","QB","Vanderbilt"),
    ("Zion Elee","EDGE","Maryland"),
    ("Luke Wafle","EDGE","USC"),
    ("Rodney Dunham","EDGE","Notre Dame"),
    ("Brandon Arrington","CB","Texas A&M"),
    ("Carter Meadows","EDGE","Michigan"),
    ("Faizon Brandon","QB","Tennessee"),
    ("Immanuel Iheanacho","OG","Oregon"),
    ("Savion Hiter","RB","Michigan"),
    ("Tristen Keys","WR","Tennessee"),
    ("Chris Henry Jr.","WR","Ohio State"),
    ("EJ Crowell","RB","Alabama"),
    ("Cincere Johnson","LB","Ohio State"),
    ("Richard Anderson","DT","LSU"),
    ("Dia Bell","QB","Texas"),
    ("Jalen Lott","WR","Oregon"),
    ("John Meredith III","CB","Texas"),
    ("Ian Premer","TE","Notre Dame"),
    ("Kelvin Obot","OT","Utah"),
    ("Xavier Griffin","LB","Alabama"),
    ("Khary Adams","CB","Notre Dame"),
    ("Jay Timmons","CB","Ohio State"),
    ("Kodi Greene","OT","Washington"),
    ("LaDamion Guyton","EDGE","Texas Tech"),
    ("Joey O'Brien","S","Notre Dame"),
    ("Jorden Edmonds","CB","Alabama"),
    ("Mark Bowman","TE","USC"),
    ("Tyler Atkinson","LB","Texas"),
    ("Richard Wesley","EDGE","Texas"),
    ("Jireh Edwards","S","Alabama"),
    ("Kendre Harrison","TE","Oregon"),
    ("Jaimeon Winfield","DT","USC"),
    ("Ekene Ogboko","OT","Georgia"),
    ("Julian Walker","EDGE","South Carolina"),
    ("Kaiden Prothro","TE","Georgia"),
    ("Jett Washington","S","Oregon"),
    ("Ethan Feaster","WR","USC"),
    ("Darius Gray","OG","South Carolina"),
    ("Cederian Morgan","WR","Alabama"),
    ("Jerquaden Guilford","WR","Ohio State"),
    ("Bralan Womack","S","Mississippi State"),
    ("Felix Ojo","OT","Texas Tech"),
    ("KJ Edwards","RB","Texas A&M"),
]
PRIORITY={2028:FUTURE_2028,2029:FRESHMEN_2029}
ALIASES={
    "tkkeys":"tristenkeys", "tristenkeys":"tristenkeys",
    "ezaviercrowell":"ejcrowell", "ejcrowell":"ejcrowell",
    "jaronkeawasagapolutele":"jaronkeawesagapolutele",
}
def canonical(name):
    n=key(name)
    return ALIASES.get(n,n)
def pname(p):
    return canonical(p["forename"]+" "+p["surname"])
def group(players, year):
    return [p for p in players if p["pool"]=="draftClass"
            and p["bio"]["draftSeason"]==year]
def portrait_stats(players,year,names):
    candidates=group(players,year)
    selected={pname(p):p for p in candidates}
    assigned=[p for p in candidates if p["bio"].get("portraitId")]
    priority_with=[name for name,_,_ in names
                   if canonical(name) in selected and
                   selected[canonical(name)]["bio"].get("portraitId")]
    return {
        "class_players":len(candidates),
        "explicit_cartoon_portrait_ids":len(assigned),
        "default_game_generated_portraits":len(candidates)-len(assigned),
        "featured_names_with_explicit_cartoon_portraits":len(priority_with),
        "featured_names_needing_visual_review":len(names)-len(priority_with),
        "face_likeness_verified_by_app":False,
    }

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Incomplete V15 export; refusing to replace frozen assets")
        print("V15 versioned preview assets frozen; skipping regeneration")
        return
    assert len({canonical(n) for year in PRIORITY for n,_,_ in PRIORITY[year]})==sum(len(x) for x in PRIORITY.values()), "Duplicate priorities"
    base=json.loads(BASE.read_text())
    assert base["schemaVersion"]==3 and base["meta"]["baseSeason"]==2020
    assert len(base["players"])==6613 and base["deadCap"]==[]
    players=copy.deepcopy(base["players"])
    preserved={p["iden"]:copy.deepcopy(p) for p in players
               if p["pool"]=="roster" or
               p["bio"]["draftSeason"]<=2027}
    assert len(preserved)==5653
    input_ids={p["iden"] for p in players}
    lib=template_library(players)
    source=defaultdict(list)
    for row in download():
        candidate=normalize_candidate(row)
        if candidate:
            source[canonical(candidate["name"])].append(candidate)
    assert len(source)>11000
    source_biography=Counter()
    before={}
    added=Counter()
    moved=Counter()
    position_corrected=Counter()
    school_corrected=Counter()
    new_source=Counter()
    missing_before={}
    for year, priorities in PRIORITY.items():
        before[str(year)]=portrait_stats(players,year,priorities)
        existing={pname(p) for p in group(players,year)}
        missing_before[str(year)]=[name for name,_,_ in priorities
                                 if canonical(name) not in existing]
    for year, priorities in PRIORITY.items():
        for rank,(name,pos,school) in enumerate(priorities,1):
            match=[p for p in players if p["pool"]=="draftClass"
                   and p["bio"]["draftSeason"]>=2028
                   and pname(p)==canonical(name)]
            if len(match)>1:
                raise RuntimeError("Ambiguous 2028/29 prospect identity: "+name)
            if match:
                p=match[0]
                if p["bio"]["draftSeason"]!=year:
                    p["bio"]["draftSeason"]=year
                    p["bio"]["draftNum"]=-1
                    moved[year]+=1
                if p["position"]!=pos:
                    recalibrate(p,p["development"]["ovr"],pos)
                    position_corrected[year]+=1
                if not school_matches(p["bio"].get("college",""),school):
                    p["bio"]["college"]=school
                    school_corrected[year]+=1
            else:
                # Never conflate a different player in the fixed 2020-2027 pool.
                protected=[p for p in players
                           if p["iden"] in preserved and pname(p)==canonical(name)
                           and p["position"]==pos and
                           school_matches(p["bio"].get("college",""),school)]
                if protected:
                    raise RuntimeError("Priority prospect already exists in immutable history: "+name)
                p,origin=modeled_player(name,pos,school,year,rank,source,lib)
                p["bio"]["weightLbs"]=min(400,max(140,p["bio"]["weightLbs"]))
                recalibrate(p,ranked_target(year,rank,hashbytes(name)),pos)
                if p["iden"] in input_ids or any(x["iden"]==p["iden"] for x in players):
                    raise RuntimeError("Duplicate player ID generated: "+name)
                players.append(p)
                new_source[origin]+=1
                added[year]+=1
            if any(x["iden"]==p["iden"] and x!=p for x in players):
                raise RuntimeError("Inconsistent player record: "+name)

    # Keep every class at exactly 480 real-player identities. Rank-based
    # protections never compel exact draft order or future NFL team choice.
    drop=Counter()
    refill=Counter()
    for year in (2028,2029):
        current=group(players,year)
        protected_names={canonical(x[0]) for x in PRIORITY[year]}
        if len(current)>480:
            excess=len(current)-480
            counts=Counter(x["position"] for x in current)
            removable=[x for x in current if pname(x) not in protected_names]
            removable.sort(key=lambda x:(
                -(counts[x["position"]]-30),x["development"]["ovr"],x["iden"]))
            assert len(removable)>=excess
            banned={x["iden"] for x in removable[:excess]}
            players=[x for x in players if x["iden"] not in banned]
            drop[year]=excess
        current=group(players,year)
        if len(current)<480:
            missing=480-len(current)
            assigned={pname(x) for x in players}
            options=[]
            for rows in source.values():
                for c in rows:
                    if c["draft"]==year and canonical(c["name"]) not in assigned:
                        options.append(c)
            options.sort(key=lambda c:(-quality(c),canonical(c["name"]),c["id"]))
            for c in options:
                if missing==0:break
                k=canonical(c["name"])
                if k in assigned:continue
                p=projected_player(c,lib)
                p["bio"]["weightLbs"]=min(400,max(140,p["bio"]["weightLbs"]))
                if p["iden"] in {x["iden"] for x in players}: continue
                players.append(p)
                assigned.add(k)
                missing-=1
                refill[year]+=1
            if missing:
                raise RuntimeError("Insufficient sourced college refills for "+str(year))
    assert len(players)==6613
    assert len({p["iden"] for p in players})==len(players)
    idx={p["iden"]:p for p in players}
    assert all(idx.get(k)==v for k,v in preserved.items()), "2020-2027 approved record altered"
    assert all(140<=p["bio"]["weightLbs"]<=400 for p in players)
    assert all(sum(p["pool"]=="draftClass" and p["bio"]["draftSeason"]==y for p in players)==480 for y in range(2021,2030))
    names_all=Counter(pname(p) for p in players if p["pool"]=="draftClass" and p["bio"]["draftSeason"]>=2028)
    assert all(v==1 for v in names_all.values()), "Duplicate future prospect across classes"
    for year, entries in PRIORITY.items():
        selected={pname(p):p for p in group(players,year)}
        for name,pos,school in entries:
            p=selected.get(canonical(name))
            assert p and p["position"]==pos and school_matches(p["bio"].get("college",""),school),(year,name)
            assert not p.get("teamAbbr") and not p.get("teamId")
            assert abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])<=2,(year,name)
    after={str(y):portrait_stats(players,y,PRIORITY[y]) for y in (2028,2029)}
    for p in players:
        pid=p["bio"].get("portraitId")
        assert pid is None or re.fullmatch(r"portrait-\d{4}",pid),"Invalid cartoon portrait ID"
    OUTPUT.write_text(json.dumps({
        "schemaVersion":3,"meta":{"baseSeason":2020},
        "players":players,"deadCap":[]},separators=(",",":"))+"\n")
    report={
        "status":"V15_STRUCTURAL_SCOUTING_AND_PORTRAIT_AUDIT_PASS_GAME_IMPORT_UNTESTED",
        "baseSeason":2020,"totalPlayers":6613,"startingRoster":2293,
        "classSizes":{str(y):480 for y in range(2021,2030)},
        "baseline":"V12 nine-class published import",
        "preservedApproved2020Through2027":5653,
        "source_2028_board":S_28_BOARD,
        "source_2028_devy":S_28_DEVY,
        "source_2029_freshman_recruiting":S_29_ROSTER,
        "source_2029_jared_curtis_college":S_29_VERIFIED_QB,
        "source_2026_college_roster":S_COLLEGE,
        "source_scope":"2028 tentative scouting board and devy; 2029 actual 2026 freshmen as provisional draft-eligible candidates",
        "coverageTargets":{"2028":len(PRIORITY[2028]),"2029":len(PRIORITY[2029])},
        "newProspects":{str(k):added[k] for k in (2028,2029)},
        "prospectsMovedBetweenFutureYears":{str(k):moved[k] for k in (2028,2029)},
        "positionCorrections":{str(k):position_corrected[k] for k in (2028,2029)},
        "current2026CollegeCorrections":{str(k):school_corrected[k] for k in (2028,2029)},
        "newProspectSourceProvenance":dict(new_source),
        "rebalancingRemovedNonPriority":{str(k):drop[k] for k in (2028,2029)},
        "rebalancingAddedFrom2026Roster":{str(k):refill[k] for k in (2028,2029)},
        "beforeCoverageMissing":{str(y):missing_before[str(y)] for y in (2028,2029)},
        "portraitAuditBefore":before,
        "portraitAuditAfter":after,
        "portraitReviewQueue":{
           str(y):[name for name,_,_ in PRIORITY[y][:24]
                   if not any(pname(p)==canonical(name) and p["bio"].get("portraitId") for p in group(players,y))]
           for y in (2028,2029)
        },
        "portraitMethod":"Preserve known game-compatible cartoon IDs; default-generated faces for unmatched players. Never assign unverified skin-tone/face IDs from metadata.",
        "limitations":[
            "2028/29 final declarations and actual NFL draft board/rankings remain unknown",
            "2029 ranking is 2026 incoming college recruiting, not 2029 NFL mock consensus",
            "Draft placement and modeled attributes are estimates, not authenticated Madden grades",
            "Cartoon face resemblance cannot be established from JSON; screenshot review required",
            "Automated GitHub validation cannot prove CapForge importer warning count or future season persistence",
        ],
        "privacy":"No hidden individual potentials, developmental curves or NFL draft destinations reported",
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
        "result":report["status"],
        "coverageTargets":report["coverageTargets"],
        "newProspects":report["newProspects"],
        "moved":report["prospectsMovedBetweenFutureYears"],
        "portraitsNeedingVisualReview":{str(y):after[str(y)]["featured_names_needing_visual_review"] for y in (2028,2029)},
        "approvedThrough2027Preserved":len(preserved),
    },indent=2))
if __name__=="__main__":
    main()
