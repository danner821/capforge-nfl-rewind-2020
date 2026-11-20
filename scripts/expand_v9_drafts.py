#!/usr/bin/env python3
"""Versioned V9: rebuild full draft-class pools using documented real prospects.

Run AFTER build_2020.py. V8 (and V6/V7) are input/immutable. Real identities
come from published combine/pro-day and ESPN pre-draft rows; skill estimates
for new players are NOT authentic Madden ratings. Never put hidden development
values in console output or reports. Historical NFL draft destinations remain
unassigned, so the user's franchise determines each pick.
"""
from __future__ import annotations

import copy
import csv
import hashlib
import io
import json
import re
import urllib.request
import uuid
from collections import Counter, defaultdict
from pathlib import Path

from audit_draft_classes import norm, ALIASES
from build_2020 import development
from capforge_ovr import calibrate, estimate
from parse_nfl_undrafted import load_undrafted_sources, URLS as NFL_UDFAS

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "preview"
INPUT = PREVIEW / "players-2020-six-class-history-v8.json"
OUTPUT_SIX = PREVIEW / "players-2020-six-class-authentic-v9.json"
OUTPUT_FOUR = PREVIEW / "players-2020-four-class-authentic-v9.json"
REPORT = PREVIEW / "v9-draft-pool-report.json"
TARGET = 480
YEARS = range(2021, 2027)
SUPPORTED = {"QB","RB","WR","TE","OT","OG","C","DE","DT","EDGE","LB","CB","S","K","P"}
SOURCES = {
    "combine": "https://raw.githubusercontent.com/array-carpenter/nfl-draft-data/master/data/combine_pro_day.csv",
    "espn": "https://raw.githubusercontent.com/JackLich10/nfl-draft-data/main/nfl_draft_prospects.csv",
    "draft": "https://raw.githubusercontent.com/7LayerLabs/nfldraft/main/nfl-drafts-2017-2026.csv",
}
# Specific football positions: don't turn generic, ambiguous OL/DL/DB records
# into a random NFL position when their exact role isn't established.
POS_MAP = {
    "QB":"QB", "RB":"RB", "HB":"RB", "FB":"RB", "WR":"WR", "TE":"TE",
    "OT":"OT", "T":"OT", "LT":"OT", "RT":"OT", "OG":"OG", "G":"OG", "LG":"OG", "RG":"OG",
    "C":"C", "OC":"C", "DE":"DE", "DL":"DE", "DT":"DT", "NT":"DT",
    "EDGE":"EDGE", "ED":"EDGE", "OLB":"LB", "ILB":"LB", "MLB":"LB", "LB":"LB",
    "CB":"CB", "DB":"CB", "S":"S", "FS":"S", "SS":"S", "SAF":"S",
    "K":"K", "PK":"K", "P":"P", "PT":"P"
}
# Unambiguous group labels can rescue missing specific positions.
GROUP_MAP = {"QB":"QB","RB":"RB","WR":"WR","TE":"TE","LB":"LB","P":"P","K":"K"}
FIRST_NAMES = ("Aaron","Bryce","Caleb","Devin","Ethan","Felix","Grant","Hayden",
               "Ian","Jaden","Kyle","Logan","Marcus","Nolan","Owen","Parker",
               "Quentin","Ryan","Sam","Tanner","Victor","Wesley","Xavier","Zachary")
LAST_NAMES = ("Anderson","Baker","Carter","Davis","Edwards","Foster","Garcia",
              "Harris","Irving","James","Kelly","Lawson","Miller","Nelson",
              "Owens","Parker","Quinn","Reed","Simmons","Turner","Underwood",
              "Vaughn","Walker","Young")

def source_csv(url):
    request = urllib.request.Request(url, headers={"User-Agent":"Capforge-Rosters-V9/1.0"})
    with urllib.request.urlopen(request, timeout=95) as response:
        rows = list(csv.DictReader(io.StringIO(response.read().decode("utf-8-sig"))))
    if len(rows) < 250:
        raise ValueError("Unexpectedly small historical player source: " + url)
    return rows

def canonical(name):
    n = norm(name)
    return ALIASES.get(n, n)

def number(value):
    try:
        n = float(value)
        return n if n == n else None
    except (ValueError,TypeError):
        return None

def integer(value):
    n=number(value)
    return int(n) if n is not None else None

def safe_name(value):
    value = str(value or "").strip()
    # Reject roster artifacts, anonymous placeholders and unusual parser noise.
    value = re.sub(r"\s+", " ", value)
    return bool(re.fullmatch(r"[A-Za-z][A-Za-z .'\-]+[A-Za-z.]",value)) and len(value.split())>=2

def to_position(raw, group=""):
    raw = str(raw or "").strip().upper().replace(" ", "")
    group = str(group or "").strip().upper().replace(" ", "")
    return POS_MAP.get(raw, GROUP_MAP.get(group))

def stable_hash(text):
    return hashlib.sha256(text.encode("utf8")).digest()

def clamp(n,lo,hi):
    return max(lo,min(hi,int(round(n))))

def season_key(p):
    return (int(p["bio"]["draftSeason"]),canonical(p["forename"]+" "+p["surname"]))

def template_library(players):
    lib=defaultdict(list)
    for p in players:
        if p["position"] in SUPPORTED and p["ratings"]:
            lib[p["position"]].append(p)
    for position in lib:
        # Real lower-OVR player traits form reasonable per-position templates.
        lib[position].sort(key=lambda p:(abs(p["development"]["ovr"]-59),
                                        p["iden"]))
    assert all(lib.get(pos) for pos in SUPPORTED), "Missing positional rating template"
    return lib

def source_candidate(r,origin):
    if origin=="combine":
        year=integer(r.get("Year"))
        name=r.get("player","")
        pos=to_position(r.get("POS"),r.get("POS_GP"))
        college=r.get("College","")
        height=number(r.get("Height (in)"))
        weight=number(r.get("Weight (lbs)"))
        forty=number(r.get("40 Yard"))
        grade=None
        rank=None
    elif origin=="nfl_udfa":
        year=integer(r.get("year"))
        name=r.get("name","")
        pos=to_position(r.get("pos"))
        college=r.get("college","")
        height=None
        weight=None
        forty=None
        grade=None
        rank=None
    else:
        year=integer(r.get("year"))
        name=r.get("player_name","")
        pos=to_position(r.get("pos_abbr"),r.get("position"))
        college=r.get("school_name") or r.get("school") or ""
        height=number(r.get("height"))
        weight=number(r.get("weight"))
        forty=None
        grade=number(r.get("grade"))
        rank=number(r.get("ovr_rk"))
    if year not in YEARS or not pos or pos not in SUPPORTED or not safe_name(name):
        return None
    key=canonical(name)
    if not key or len(key)<6:
        return None
    # Height/weight can be missing in original scouting records.
    return {"year":year, "name":name.strip(),"position":pos,"college":str(college).strip(),
            "height":height,"weight":weight,"forty":forty,"grade":grade,
            "rank":rank,"source":origin,"key":key}

def source_pool(combine_rows,espn_rows,nfl_udfa_rows):
    found=defaultdict(dict)
    for origin,rows in (("combine",combine_rows),("espn",espn_rows),("nfl_udfa",nfl_udfa_rows)):
        for raw in rows:
            c=source_candidate(raw,origin)
            if not c: continue
            key=c["key"]
            year=c["year"]
            existing=found[year].get(key)
            if existing:
                # Keep the combine-specific position/measurements where available.
                if existing["source"]=="combine":
                    if c["source"]=="espn":
                        existing["grade"]=c["grade"]
                        existing["rank"]=c["rank"]
                        if not existing["college"]: existing["college"]=c["college"]
                else:
                    if c["source"]=="combine":
                        c["grade"]=existing["grade"]
                        c["rank"]=existing["rank"]
                        found[year][key]=c
                continue
            found[year][key]=c
    return found

def choose_template(library,position,tag):
    options=library[position]
    # Stable shuffle within the poorest-rated few templates, not career results.
    return options[int.from_bytes(stable_hash(tag)[:2],"big") % min(16,len(options))]

def source_player(c,library,actual_draft):
    year=c["year"]
    name=c["name"]
    pos=c["position"]
    dig=stable_hash(str(year)+"|"+c["key"]+"|"+pos)
    tmpl=choose_template(library,pos,name+str(year))
    # Newly modeled sourced players have observed real identities, not observed
    # Madden rookie attributes. Keep estimates at roster-depth grades.
    # Do not use their future professional careers to choose rookie ratings.
    drafted=c["key"] in actual_draft[year]
    score=(56 if drafted else 53)+dig[0]%8
    if c["rank"] is not None and c["rank"]<=300:
        score+=1
    if c["grade"] is not None and c["grade"]>=75:
        score+=1
    target=clamp(score,48,67)
    r=copy.deepcopy(tmpl["ratings"])
    # Blend recorded timed speed conservatively, without treating missing
    # workouts as zeros or implying the player has a Madden-tested rating.
    if c["forty"] is not None and 4.2<=c["forty"]<=6.1 and "speed" in r:
        measured=clamp(205-26*c["forty"],40,99)
        r["speed"]=clamp(0.7*r["speed"]+0.3*measured,30,99)
    ratings,overall,_,_=calibrate(pos,r,target)
    first,last=name.split(" ",1)
    age=21+dig[1]%3
    bio={"age":age,"jerseyNumber":0,"college":c["college"] or "Unknown College",
         "draftSeason":year,"draftNum":-1,
         "heightInches":clamp(c["height"] or tmpl["bio"]["heightInches"],60,87),
         "weightLbs":clamp(c["weight"] or tmpl["bio"]["weightLbs"],135,425)}
    peak=clamp(overall+5+dig[2]%8,overall,76)
    return {
        "iden":str(uuid.uuid5(uuid.NAMESPACE_URL,"capforge-nfl-rewind-2020:v9:real:"+str(year)+"|"+c["key"])).upper(),
        "forename":first,"surname":last,"position":pos,"pool":"draftClass",
        "bio":bio,
        "personality":{"loyalty":30+dig[3]%65,"greed":25+dig[4]%70,
                      "ambition":30+dig[5]%65,"personality":25+dig[6]%70,
                      "workEthic":30+dig[7]%65},
        "ratings":ratings,"development":development(overall,age,peak),
        "contract":{"salary":0,"guarantee":0,"years":0,
                    "extension":{"salary":0,"guarantee":0,"years":0}},
    }

def synthetic_depth_player(year,index,library,used):
    # Last resort ONLY if independently recorded real prospects are exhausted.
    # The source report transparently counts these fictional slots.
    for attempt in range(6000):
        i=index+attempt
        name=FIRST_NAMES[(i+year)%len(FIRST_NAMES)]+" "+LAST_NAMES[((i//len(FIRST_NAMES))+year)%len(LAST_NAMES)]
        key=canonical(name)
        if key not in used:
            used.add(key)
            break
    else:
        raise RuntimeError("Out of synthetic placeholder names")
    positions=("QB","RB","WR","WR","TE","OT","OT","OG","OG","C",
               "DE","DE","DT","EDGE","EDGE","LB","LB","CB","CB","S","K","P")
    pos=positions[index%len(positions)]
    t=choose_template(library,pos,"fictional:"+str(year)+":"+str(index))
    dig=stable_hash("fictional:"+str(year)+":"+name)
    score=46+dig[0]%8
    ratings,overall,_,_=calibrate(pos,copy.deepcopy(t["ratings"]),score)
    first,last=name.split(" ",1)
    age=21+dig[1]%3
    return {
        "iden":str(uuid.uuid5(uuid.NAMESPACE_URL,"capforge-nfl-rewind-2020:v9:fictional:"+str(year)+"|"+name)).upper(),
        "forename":first,"surname":last,"position":pos,"pool":"draftClass",
        "bio":{"age":age,"jerseyNumber":0,"college":"Fictional Depth Pool",
               "draftSeason":year,"draftNum":-1,"heightInches":t["bio"]["heightInches"],
               "weightLbs":t["bio"]["weightLbs"]},
        "personality":{"loyalty":30+dig[2]%65,"greed":25+dig[3]%70,
                       "ambition":30+dig[4]%65,"personality":25+dig[5]%70,
                       "workEthic":30+dig[6]%65},
        "ratings":ratings,"development":development(overall,age,overall+1),
        "contract":{"salary":0,"guarantee":0,"years":0,
                    "extension":{"salary":0,"guarantee":0,"years":0}},
    }

def main():
    base=json.loads(INPUT.read_text())
    if base.get("schemaVersion")!=3 or base["meta"]["baseSeason"]!=2020:
        raise RuntimeError("V8 schema/base-season changed; stop before V9 generation")
    original=base["players"]
    starters=[p for p in original if p["pool"]=="roster"]
    by_year=defaultdict(list)
    for p in original:
        if p["pool"]=="draftClass":
            by_year[int(p["bio"]["draftSeason"])].append(p)
    assert len(starters)==2293 and set(by_year)==set(YEARS)
    combine=source_csv(SOURCES["combine"])
    espn=source_csv(SOURCES["espn"])
    picks=source_csv(SOURCES["draft"])
    nfl_udfas,nfl_errors=load_undrafted_sources()
    udfa_rows=[r for year in YEARS for r in nfl_udfas.get(year,[])]
    pool=source_pool(combine,espn,udfa_rows)
    actual=defaultdict(set)
    for r in picks:
        year=integer(r.get("Year"))
        if year in YEARS:
            actual[year].add(canonical(r.get("Selection","")))
    library=template_library(original)
    output=list(original)
    counts={}
    for year in YEARS:
        original_rows=by_year[year]
        if len(original_rows)>TARGET:
            raise ValueError("Existing draft class already exceeds 480 for "+str(year))
        used={canonical(p["forename"]+" "+p["surname"]) for p in original_rows}
        fresh=[c for key,c in pool[year].items() if key not in used]
        # Missing drafted prospects FIRST; others ordered by their published
        # pre-draft ESPN rank/grade, never by a player's future NFL success.
        fresh.sort(key=lambda c:(0 if c["key"] in actual[year] else 1,
                                  c["rank"] if c["rank"] is not None and c["rank"]>0 else 99999,
                                  -(c["grade"] or 0),c["key"]))
        added={"combine":0,"espn":0,"nfl_udfa":0}
        picked=[]
        for c in fresh:
            if len(original_rows)+len(picked)>=TARGET: break
            player=source_player(c,library,actual)
            picked.append(player)
            used.add(c["key"])
            added[c["source"]]+=1
        fill=[]
        while len(original_rows)+len(picked)+len(fill)<TARGET:
            fill.append(synthetic_depth_player(year,len(fill),library,used))
        output.extend(picked+fill)
        counts[str(year)]={
            "original_real_madden_based":len(original_rows),
            "sourced_combine_added":added["combine"],
            "sourced_espn_added":added["espn"],
            "nfl_documented_undrafted_added":added["nfl_udfa"],
            "fictional_depth_added":len(fill),
            "total":len(original_rows)+len(picked)+len(fill),
            "source_candidates_after_name_dedup":len(fresh),
            "documented_real_prospects":len(original_rows)+len(picked)
        }
        assert counts[str(year)]["total"]==TARGET
    ids=[p["iden"] for p in output]
    assert len(ids)==len(set(ids)), "V9 duplicate UUID"
    assert len(output)==len(original)+sum(TARGET-len(by_year[y]) for y in YEARS)
    full={"schemaVersion":3,"meta":{"baseSeason":2020},"players":output,"deadCap":[]}
    four={"schemaVersion":3,"meta":{"baseSeason":2020},
          "players":[p for p in output if p["pool"]=="roster" or
                     (p["pool"]=="draftClass" and p["bio"]["draftSeason"]<=2024)],
          "deadCap":[]}
    OUTPUT_SIX.write_text(json.dumps(full,separators=(",",":"))+"\n")
    OUTPUT_FOUR.write_text(json.dumps(four,separators=(",",":"))+"\n")
    report={
        "status":"EXPERIMENTAL_NOT_VERIFIED_IN_CAPFORGE",
        "baseSeason":2020,"startingRosterPlayers":len(starters),
        "sourceURLs":{**SOURCES,"nfl_undrafted":NFL_UDFAS},
        "nflUndraftedSourceCounts":{str(y):len(nfl_udfas.get(y,[])) for y in YEARS},
        "nflUndraftedSourceErrors":{str(y):e for y,e in nfl_errors.items()},
        "method":"Keep all V8 players byte-equivalent at record level; append independently documented college prospects with conservative, modeled ratings; fictional low-tier depth only where required",
        "classTarget":TARGET,"classes":counts,
        "total":len(output),
        "importantCaveats":[
            "Combine/pro-day names establish real draft-year college prospect identity, not Madden-validated attributes",
            "New prospect OVR and development are conservative estimates, not authenticated rookie ratings",
            "The actual CapForge app must confirm it does not generate more filler or alter draft-board projections",
            "No historical NFL team is preassigned to future prospects",
            "Previous versions and all V8 records are unchanged; hidden potential is not printed"
        ]
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"classes":counts,"exportPlayers":len(output),
                      "fillerTotal":sum(v["fictional_depth_added"] for v in counts.values())},
                     indent=2))
if __name__=="__main__":
    main()
