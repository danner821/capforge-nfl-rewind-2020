#!/usr/bin/env python3
"""V11: repair the V10 nine-year historical-to-projected NFL draft import.

V10 inputs are immutable. This is a separately versioned test file.
Only 2027-29 projections (not verified draft declarations) are rebalanced,
plus two explicitly diagnosed importer mismatches and Arch Manning portrait.
Every edited player identity comes from an independent November 2026 draft
ranking or the actual 2026 college roster; no speculative names are invented.
Do not print individual progression, potential, contracts, or future teams.
"""
from __future__ import annotations
import copy, hashlib, json, uuid
from collections import Counter, defaultdict
from pathlib import Path
from audit_draft_classes import norm
from build_v10_future import download, normalize_candidate, projected_player, quality
from expand_v9_drafts import template_library, choose_template
from capforge_ovr import calibrate, estimate
from build_2020 import development

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
INPUT=PREVIEW/"players-2020-nine-class-projection-v10.json"
OUTPUT_NINE=PREVIEW/"players-2020-nine-class-scoutfix-v11.json"
OUTPUT_SEVEN=PREVIEW/"players-2020-seven-class-scoutfix-v11.json"
REPORT=PREVIEW/"v11-scouting-portrait-audit.json"
YEAR_TARGET=480
# Contemporary source (2026-11-18): public aggregate 2027 scouting board.
# Names/positions/schools only; rankings are evidence for approximate readiness,
# never proof of an NFL career, declaration, final team, or final draft slot.
SOURCE_27="https://www.thedraftroom.app/2027-nfl-draft-big-board"
SOURCE_28="https://ultimatebigboard.com/nfl/2028/"
SOURCE_29="https://keeptradecal.com/devy-quarterback-rankings/"
SOURCE_COLLEGE="https://raw.githubusercontent.com/sportsdataverse/cfbfastR-data/main/rosters/csv/cfb_rosters_2026.csv"

# 2027: first 50 from 2026-11-18 consensus, with normalized game positions.
RANKED_2027=[
 ("Jeremiah Smith","WR","Ohio State"),
 ("Leonard Moore","CB","Notre Dame"),
 ("Colin Simmons","EDGE","Texas"),
 ("Dylan Stewart","EDGE","South Carolina"),
 ("Drew Mestemaker","QB","Oklahoma State"),
 ("Charlie Becker","WR","Indiana"),
 ("Jordan Seaton","OT","LSU"),
 ("Will Echoles","DT","Ole Miss"),
 ("Ashton Hampton","CB","Clemson"),
 ("Chris Cole","LB","Georgia"),
 ("Xavier Gilliam","DT","Tennessee"),
 ("Darian Mensah","QB","Miami"),
 ("CJ Carr","QB","Notre Dame"),
 ("Jadan Baugh","RB","Florida"),
 ("Ellis Robinson IV","CB","Georgia"),
 ("Kelley Jones","CB","Mississippi State"),
 ("Greg Johnson","OG","Minnesota"),
 ("Trinidad Chambliss","QB","Ole Miss"),
 ("Trey'Dez Green","TE","LSU"),
 ("Nick Marsh","WR","Indiana"),
 ("Cam Coleman","WR","Texas"),
 ("Trevor Lauck","OT","Iowa"),
 ("Kade Pieper","C","Iowa"),
 ("Yhonzae Pierre","EDGE","Alabama"),
 ("Jamari Johnson","TE","Oregon"),
 ("Trevor Goosby","OT","Texas"),
 ("KJ Bolden","S","Georgia"),
 ("KJ Duff","WR","Rutgers"),
 ("Lance Heard","OT","Kentucky"),
 ("Zereoue Williams","OT","Utah"),
 ("A'Mauri Washington","DT","Oregon"),
 ("Boubacar Traore","EDGE","Notre Dame"),
 ("David Stone","DT","Oklahoma"),
 ("Devan Thompkins","DT","Alabama"),
 ("Kyngstonn Viliamu-Asa","LB","Notre Dame"),
 ("Dante Moore","QB","Oregon"),
 ("Will Heldt","EDGE","Clemson"),
 ("Reed Harris","WR","Arizona State"),
 ("Arch Manning","QB","Texas"),
 ("Ryan Coleman-Williams","WR","Alabama"),
 ("Brauntae Johnson","S","Notre Dame"),
 ("Luke Reynolds","TE","Virginia Tech"),
 ("Ahmad Moten Sr.","DT","Miami"),
 ("Carter Smith","OT","Indiana"),
 ("Jelani McDonald","S","Texas"),
 ("Cayden Green","OT","Missouri"),
 ("Kewan Lacy","RB","Ole Miss"),
 ("Matayo Uiagalelei","EDGE","Oregon"),
 ("Kingston Lopa","S","California"),
 ("AJ Holmes Jr.","DT","Texas Tech"),
]
# Very early 2028 predictions; source has thin coverage (a few mocks).
# Use to INCLUDE REAL prospects and avoid omitting known high-profile names;
# do not treat these as accurate top-30 ordering or final draft-year decisions.
RANKED_2028=[
 ("Bryce Underwood","QB","Michigan"),
 ("Michael Fasusi","OT","Oklahoma"),
 ("Tavien St Clair","QB","Ohio State"),
 ("Quincy Porter","WR","Ohio State"),
 ("Will Black","OT","Notre Dame"),
 ("Elijah Griffin","DT","Georgia"),
 ("Lance Jackson","EDGE","Texas"),
 ("David Sanders Jr.","OT","Tennessee"),
 ("Keelon Russell","QB","Alabama"),
 ("DJ Pickett","CB","LSU"),
 ("Justus Terry","DT","Texas"),
 ("Tylon Lee","EDGE","Florida State"),
 ("Jerome Myles","WR","Texas A&M"),
 ("Na'eem Offord","CB","Oregon"),
 ("Michael Carroll","OG","Alabama"),
 ("Talyn Taylor","WR","Georgia"),
 ("Isaiah Gibson","EDGE","Georgia"),
 ("Andrew Babalola","OT","Michigan"),
 ("Deuce Knight","QB","Ole Miss"),
 ("Amare Adams","DT","Clemson"),
 ("Devin Sanchez","CB","Ohio State"),
 ("Jonah Williams","S","Texas"),
 ("Carius Curne","OG","Ole Miss"),
 ("Harlem Berry","RB","LSU"),
 ("Andrew Olesh","TE","Oregon"),
 ("Dakorien Moore","WR","Oregon"),
 ("Nate Marshall","EDGE","Michigan"),
 ("Dallas Wilson","WR","Florida"),
 ("Elyiss Williams","TE","Georgia"),
 ("Ousmane Kromah","RB","Florida State"),
]
# 2029 NFL projections are particularly uncertain: these are *2026* freshmen
# discussed in contemporary devy QB scouting, NOT 2029 high-school recruits.
RANKED_2029=[
 ("Keisean Henderson","QB","Houston"),
 ("Dia Bell","QB","Texas"),
 ("Jared Curtis","QB","Georgia"),
]
PRIORITY={2027:RANKED_2027,2028:RANKED_2028,2029:RANKED_2029}
ALIASES={
 "camcoleman":"cameroncoleman",
 "willechols":"willecholes",
 "amhouriwashington":"amauriwashington",
 "ajholmesjr":"ajholmes",
 "ajholmes":"ajholmes",
 "tavienstclair":"tavienstclair",
 "naeemofford":"naeemofford",
 "kyngstonnviliamuasa":"kyngstonnviliamuasa",
}
def key(name):
    name=norm(name)
    return ALIASES.get(name,name)

def player_key(p):
    return key(p["forename"]+" "+p["surname"])

def hashbytes(s):
    return hashlib.sha256(s.encode()).digest()

def school_matches(a,b):
    a=(a or "").lower().replace("university","").replace("state","st")
    b=(b or "").lower().replace("university","").replace("state","st")
    return a==b or (a in b or b in a) and min(len(a),len(b))>=4

def ranked_target(year,rank,digest):
    # Brackets capture relative draft-readiness without forecasting successes.
    if year==2027:
        base=78 if rank<=6 else 75 if rank<=15 else 72 if rank<=30 else 69
    elif year==2028:
        base=75 if rank<=5 else 73 if rank<=12 else 70
    else:
        base=71
    return max(60,min(79,base + (digest[0]%5-2)))

def modeled_player(name,pos,school,year,rank,source_rows,lib):
    qualified=[c for c in source_rows.get(key(name),[])
               if c["pos"]==pos and school_matches(c["college"],school)]
    if not qualified:
        qualified=[c for c in source_rows.get(key(name),[])
                   if school_matches(c["college"],school)]
    if qualified:
        c=copy.deepcopy(sorted(qualified,key=lambda x:(x["pos"]!=pos,x["id"]))[0])
        c["draft"]=year
        c["pos"]=pos
        c["college"]=school
        c["name"]=name
        c["key"]=key(name)
        provenance="2026_college_roster"
    else:
        # Name, school and position still grounded in an actual 2026 published
        # pre-draft list; physical dimensions are conservative model defaults.
        template=choose_template(lib,pos,"v11|"+name)
        d=hashbytes("v11|"+name+"|"+str(year))
        c={"id":"scoutboard-"+key(name),"key":key(name),"name":name,
           "college":school,"draft":year,"class":0,"pos":pos,
           "height":template["bio"]["heightInches"],
           "weight":min(400,template["bio"]["weightLbs"]),
           "seed":d}
        provenance="published_draft_board_only"
    p=projected_player(c,lib)
    return p,provenance

def recalibrate(p,desired,newpos):
    was=p["development"]["ovr"]
    if p["position"] != newpos or desired > was+2:
        p["ratings"],current,_,_=calibrate(newpos,p["ratings"],max(was,desired))
        p["position"]=newpos
        # Internal CapForge OVR model is approximate; avoid overclaiming an
        # unreachable rating while preserving plausible player readiness.
        current=min(current,max(40,round(estimate(newpos,p["ratings"]))))
        p["development"]=development(current,p["bio"]["age"],
                 max(current+4,p["development"]["potential"]))
    return p

def main():
    paths=(OUTPUT_NINE,OUTPUT_SEVEN,REPORT)
    if any(p.exists() for p in paths):
        if not all(p.exists() for p in paths):
            raise RuntimeError("Partial V11 assets; refusing to rewrite frozen versions")
        print("V11 preview assets frozen; skipping re-generation")
        return
    data=json.loads(INPUT.read_text())
    assert data["schemaVersion"]==3 and data["meta"]["baseSeason"]==2020
    players=copy.deepcopy(data["players"])
    assert len(players)==6613
    originals={p["iden"]:copy.deepcopy(p) for p in players if p["pool"]=="roster"
               or (p["pool"]=="draftClass" and p["bio"]["draftSeason"]<=2026)}
    assert len(originals)==5173
    lib=template_library(players)
    source_rows=defaultdict(list)
    for row in download():
        candidate=normalize_candidate(row)
        if candidate:
            source_rows[key(candidate["name"])].append(candidate)
    assert len(source_rows)>11000,"No usable 2026 college roster source"
    # Protect all V9 records and all historical draft years except a strictly
    # necessary game-enforced bio weight cap. The real player is NOT removed.
    watson=[p for p in players if p["forename"]=="Desmond" and
            p["surname"]=="Watson" and p["bio"]["draftSeason"]==2024]
    assert len(watson)==1 and watson[0]["bio"]["weightLbs"]==425
    watson[0]["bio"]["weightLbs"]=400

    fixed_ovr=[]
    portrait=[]
    moved=[]
    added=[]
    enhanced=Counter()
    protected=defaultdict(set)
    origin_counts=Counter()
    for yr,entries in PRIORITY.items():
        for rank,(name,pos,school) in enumerate(entries,1):
            matching=[p for p in players if p["pool"]=="draftClass"
                       and p["bio"]["draftSeason"]>=2027
                       and player_key(p)==key(name)]
            if len(matching)>1:
                raise RuntimeError("Ambiguous source player identity: "+name)
            if matching:
                p=matching[0]
                old_year=p["bio"]["draftSeason"]
                if old_year!=yr:
                    p["bio"]["draftSeason"]=yr
                    p["bio"]["draftNum"]=-1
                    moved.append((name,old_year,yr))
                if p["position"]!=pos or p["development"]["ovr"]<66:
                    recalibrate(p,ranked_target(yr,rank,hashbytes(name)),pos)
                    enhanced[yr]+=1
            else:
                if any(player_key(p)==key(name) for p in players):
                    raise RuntimeError("Priority prospect already in 2021-2026 historical classes: "+name)
                p,provenance=modeled_player(name,pos,school,yr,rank,source_rows,lib)
                recalibrate(p,ranked_target(yr,rank,hashbytes(name)),pos)
                players.append(p)
                origin_counts[provenance]+=1
                added.append((name,yr))
                enhanced[yr]+=1
            if name=="Dylan Stewart":
                # Current in-app V10 warning: imported OVR 79 is unreachable;
                # CapForge itself calculated 77 from the supplied skill set.
                # The imported number is not a historical fact.
                if p["development"]["ovr"]>77:
                    p["development"]["ovr"]=77
                    p["development"]["potential"]=max(
                         p["development"]["potential"],77)
                fixed_ovr.append(name)
            if name=="Arch Manning":
                # CapForge cartoon portrait is a finite in-game catalog.
                # Zach Wilson's approved V9 QB portrait has a similar light
                # complexion and dark hair; no real headshot URL is imported.
                wilson=[x for x in players if x["forename"]=="Zach" and
                        x["surname"]=="Wilson" and x["bio"]["draftSeason"]==2021]
                assert len(wilson)==1 and wilson[0]["position"]=="QB"
                pid=wilson[0]["bio"].get("portraitId")
                assert pid and pid.startswith("portrait-"),"No validated portrait reference"
                p["bio"]["portraitId"]=pid
                portrait.append(name)
            protected[yr].add(key(name))

    # Balance the 480-player classes after fixing missing names and wrong-year
    # prospects. Never remove one of the documented priority targets.
    dropped=Counter()
    refill=Counter()
    for yr in (2027,2028,2029):
        yearplayers=[p for p in players if p["pool"]=="draftClass"
                     and p["bio"]["draftSeason"]==yr]
        if len(yearplayers)>YEAR_TARGET:
            # Remove the lowest-rated nonpriority projections first, favoring
            # positions with unusually high counts. The game retains a realistic
            # mixture of prospects and can still produce draft surprises.
            excess=len(yearplayers)-YEAR_TARGET
            counts=Counter(p["position"] for p in yearplayers)
            choices=[p for p in yearplayers if player_key(p) not in protected[yr]]
            choices.sort(key=lambda p:(-(counts[p["position"]]-30),
                  p["development"]["ovr"],p["iden"]))
            assert len(choices)>=excess
            drop_ids={p["iden"] for p in choices[:excess]}
            players=[p for p in players if p["iden"] not in drop_ids]
            dropped[yr]=excess
        yearplayers=[p for p in players if p["pool"]=="draftClass" and p["bio"]["draftSeason"]==yr]
        if len(yearplayers)<YEAR_TARGET:
            want=YEAR_TARGET-len(yearplayers)
            all_keys={player_key(p) for p in players}
            candidates=[]
            for same_name in source_rows.values():
                for c in same_name:
                    if c["draft"]==yr and c["key"] not in all_keys:
                        candidates.append(c)
            candidates.sort(key=lambda c:(-quality(c),c["key"],c["id"]))
            for c in candidates:
                if want<=0:break
                if c["key"] in all_keys:continue
                p=projected_player(c,lib)
                players.append(p)
                all_keys.add(c["key"])
                refill[yr]+=1
                want-=1
            if want:
                raise RuntimeError(f"Not enough real 2026 college players to refill projected class {yr}: {want}")
    for yr in (2027,2028,2029):
        assert sum(p["pool"]=="draftClass" and p["bio"]["draftSeason"]==yr for p in players)==480
        for name,pos,school in PRIORITY[yr]:
            assert sum(p["pool"]=="draftClass" and p["bio"]["draftSeason"]==yr and
                       player_key(p)==key(name) for p in players)==1, "Missing featured prospect: "+name
    assert len(players)==6613
    assert len({p["iden"] for p in players})==len(players)
    # Names cannot appear in more than one projected class.
    seen=set()
    for p in players:
        if p["pool"]=="draftClass" and p["bio"]["draftSeason"]>=2027:
            ident=player_key(p)
            assert ident not in seen,"Duplicated future prospect identity"
            seen.add(ident)
    # Absolutely no 2020 starters or historical 2021–2026 data changed apart
    # from the Desmond Watson import limit already diagnosed in the app.
    after={p["iden"]:p for p in players}
    for ident,original in originals.items():
        if ident==watson[0]["iden"]:
            expected=copy.deepcopy(original)
            expected["bio"]["weightLbs"]=400
            assert after[ident]==expected,"Unintended alteration to Desmond Watson"
        else:
            assert after[ident]==original,"Historical 2020–2026 record modified"
    assert all(140<=p["bio"]["weightLbs"]<=400 for p in players)
    payload={"schemaVersion":3,"meta":{"baseSeason":2020},
             "players":players,"deadCap":[]}
    seven={"schemaVersion":3,"meta":{"baseSeason":2020},
           "players":[p for p in players if p["pool"]=="roster" or
                      p["bio"]["draftSeason"]<=2027],"deadCap":[]}
    assert len(seven["players"])==5653
    OUTPUT_NINE.write_text(json.dumps(payload,separators=(",",":"))+"\n")
    OUTPUT_SEVEN.write_text(json.dumps(seven,separators=(",",":"))+"\n")
    summary={
        "status":"EXPERIMENTAL_V11_CHECKS_ONLY_CAPFORGE_IMPORT_UNVERIFIED",
        "source_2027":SOURCE_27,"source_2028":SOURCE_28,
        "source_2029":SOURCE_29,"college_roster":SOURCE_COLLEGE,
        "source_method":"Public pre-draft consensus used for identity, intended position and provisional year; 2026 NCAA roster used for actual biographical names when available; missing measurements are modeled",
        "class_sizes":{str(y):480 for y in range(2021,2030)},
        "starting_roster_players":2293,
        "file_total_players":len(players),
        "historical_records_protected":len(originals)-1,
        "known_import_fixes":[
          "Desmond Watson 2024 bio weight clamped 425 to 400 for CapForge max",
          "Dylan Stewart 2027 rating/position aligned to internal importer reported reachable OVR"
        ],
        "manual_approximate_portrait_matches":portrait,
        "marquee_players_added":len(added),
        "marquee_prospects_reassigned_draft_year":len(moved),
        "marquee_players_readiness_or_position_adjusted":dict(enhanced),
        "new_record_provenance":dict(origin_counts),
        "class_refill_after_rebalance":dict(refill),
        "class_trim_after_rebalance":dict(dropped),
        "coverage_checked":{str(y):len(v) for y,v in PRIORITY.items()},
        "limitations":[
           "Future 2027-2029 declarations and rankings are projections, not known NFL results",
           "2028 scouting lists have few contributing sources and are very uncertain",
           "New and recalibrated ratings are estimated, not a verified Madden export",
           "Portrait matching uses game-provided cartoons, not real portraits",
           "Game must validate warning-free import and future-class persistence in a disposable save",
           "Original 2020-2026 player attributes/development intact except game-required 2024 weight cap"
        ],
        "privacy":"No hidden individual potential or progression values are exported in this report"
    }
    REPORT.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({
         "status":summary["status"],"fileTotal":len(players),
         "classSizes":summary["class_sizes"],"newRealNames":len(added),
         "movedDraftYear":len(moved),"portraitCorrections":len(portrait),
         "weightAndOvrWarningCorrections":2},indent=2))

if __name__=="__main__":main()
