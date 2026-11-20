#!/usr/bin/env python3
"""Build an EXPERIMENTAL 2027–2029 CapForge projection using current college rosters.

Not real NFL drafts: eligibility, declarations and future rankings are unknown.
Never overwrite V9 or the existing working save. Preserve every V9 record
identically, including hidden player development. Public output reports contain
only aggregate counts and provenance; no player potential.
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
from collections import defaultdict
from pathlib import Path

from audit_draft_classes import norm
from build_2020 import development
from capforge_ovr import calibrate
from expand_v9_drafts import POS_MAP, choose_template, template_library

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
BASE=PREVIEW/"players-2020-six-class-authentic-v9.json"
SEVEN=PREVIEW/"players-2020-seven-class-projection-v10.json"
NINE=PREVIEW/"players-2020-nine-class-projection-v10.json"
REPORT=PREVIEW/"v10-projection-report.json"
URL="https://raw.githubusercontent.com/sportsdataverse/cfbfastR-data/main/rosters/csv/cfb_rosters_2026.csv"
TARGET=480
YEARS=(2027,2028,2029)

# The number of NFL prospects per position is not fixed in reality. Keep
# every class balanced, including positions that CapForge needs for depth.
QUOTAS={"QB":30,"RB":42,"WR":60,"TE":26,"OT":36,"OG":32,"C":16,
        "DE":30,"DT":30,"EDGE":30,"LB":36,"CB":50,"S":36,"K":12,"P":14}
assert sum(QUOTAS.values())==TARGET

# Pre-draft, *non-hindsight* scouting reference names, documented as
# 2027 prospects in public Sep–Nov 2026 boards. We do not assert they
# enter the 2027 draft; the year is a projected entry, not a fact.
# The ranking is not copied verbatim from any board.
SCOUTED_2027={
 "jeremiahsmith","colinsimmons","leonardmoore","darianmensah",
 "drewmestemaker","jordanseaton","chriscole","jadanbaugh",
 "dylanstewart","kjbolden","cjcarr","matayouiagalelei",
 "dantemoore","sammybrown","ryanwingo","archmanning",
 "cameroncoleman","kewanlacy","trevorgoosby","ellisrobinson"
}
PREFERRED_PROGRAMS={
 "Alabama","Georgia","Ohio State","Michigan","Notre Dame","Texas",
 "Oregon","LSU","Clemson","USC","Miami","Penn State","Florida",
 "Florida State","Oklahoma","Tennessee","Ole Miss","Texas A&M",
 "South Carolina","Texas Tech","Utah","Indiana","Washington",
 "Auburn","Wisconsin","Iowa","Oklahoma State","Louisville","UCLA",
 "Arizona State","Kansas State","Nebraska","Minnesota","Missouri",
 "Arkansas","Kentucky","North Carolina","NC State","SMU",
 "Virginia Tech","Baylor","TCU","West Virginia","Maryland",
 "Colorado","Kansas","Pittsburgh","Illinois","Boise State"
}

def clamp(value, low, high):
    return max(low,min(high,int(round(float(value)))))

def number(value,default=None):
    try:
        x=float(value)
        return x if x==x else default
    except (ValueError,TypeError):
        return default

def canonical(name):
    return norm(name)

def digest(s):
    return hashlib.sha256(s.encode("utf-8")).digest()

def download():
    req=urllib.request.Request(URL,headers={"User-Agent":"Capforge-Rosters-Project-V10/1.0"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        text=resp.read().decode("utf-8-sig")
    rows=list(csv.DictReader(io.StringIO(text)))
    if len(rows)<20000 or "athlete_id" not in rows[0] or "year" not in rows[0]:
        raise RuntimeError("2026 college roster source missing critical data")
    return rows

def normalize_position(p,weight,height,tag):
    p=(p or "").strip().upper()
    if p in ("NA","", "ATH","ATHLETE","LS"):return None
    if p=="DL":
        return "DT" if weight>=290 else "DE"
    if p=="OL":
        if weight>=310:return "OG" if tag[0]%4 else "C"
        return "OT" if tag[0]%2 else "OG"
    if p=="DB":
        return "S" if height>=73 and tag[0]%3==0 else "CB"
    if p=="OLB":return "EDGE" if weight>=235 else "LB"
    return POS_MAP.get(p)

def normalize_candidate(row):
    a=(row.get("first_name") or "").strip()
    b=(row.get("last_name") or "").strip()
    if not (a and b):return None
    name=a+" "+b
    if not re.fullmatch(r"[A-Za-z][A-Za-z .'\-]+[A-Za-z.]",name):
        return None
    n=canonical(name)
    if len(n)<6:return None
    grade=(row.get("year") or "").strip()
    # College roster year field uses 1=freshman,2=sophomore,3=junior,4=senior.
    # Unexpected four-digit year values are not class standing and are skipped.
    if grade not in ("1","2","3","4"):return None
    class_standing=int(grade)
    draft_year={1:2029,2:2028,3:2027,4:2027}[class_standing]
    h=number(row.get("height"),73)
    w=number(row.get("weight"),220)
    dg=digest(str(row.get("athlete_id"))+"|"+name)
    pos=normalize_position(row.get("position"),w,h,dg)
    if pos not in QUOTAS:return None
    name_key=n
    return {
       "id":str(row.get("athlete_id") or "").strip(),
       "key":name_key,"name":name,
       "college":str(row.get("team") or "").strip() or "College",
       "draft":draft_year,"class":class_standing,"pos":pos,
       "height":clamp(h,60,87),"weight":clamp(w,135,425),
       "seed":dg
    }

def quality(c):
    # Rookie readiness is not future career performance or draft position.
    # Give current pre-draft publicly scouted 2027 talent a noticeable yet
    # imperfect advantage. 2028–29 players remain much more uncertain.
    dg=c["seed"]
    program=4 if c["college"] in PREFERRED_PROGRAMS else 0
    scouted=20 if c["draft"]==2027 and c["key"] in SCOUTED_2027 else 0
    tag=(dg[0]*256+dg[1])
    selection=program*10+scouted*30+tag%85
    return selection

def projected_player(c,lib):
    year=c["draft"]
    pos=c["pos"]
    d=c["seed"]
    tmpl=choose_template(lib,pos,"v10|"+str(year)+"|"+c["id"]+"|"+c["name"])
    # Rough, conservative pre-draft readiness with broad variance.
    scouted=(year==2027 and c["key"] in SCOUTED_2027)
    big=c["college"] in PREFERRED_PROGRAMS
    desired=52+(d[2]%13)+(3 if big else 0)
    if scouted:desired=max(desired,74+d[3]%8)
    elif d[3]%35==0:desired+=6 # Occasional unsung prospects
    desired=clamp(desired,45,83)
    stats=copy.deepcopy(tmpl["ratings"])
    ratings,ovr,_,_=calibrate(pos,stats,desired)
    age=22 if year==2027 else 21 if year==2028 else 21
    age+=d[4]%2
    peak=clamp(ovr+3+d[5]%14,ovr,96)
    first,last=c["name"].split(" ",1)
    bio={"age":age,"jerseyNumber":0,"college":c["college"],
         "draftSeason":year,"draftNum":-1,
         "heightInches":c["height"],"weightLbs":c["weight"]}
    return {
       "iden":str(uuid.uuid5(uuid.NAMESPACE_URL,
              "capforge-nfl-rewind-2020:v10:projected:"+str(year)+"|"+c["id"]+"|"+c["key"])).upper(),
       "forename":first,"surname":last,"position":pos,"pool":"draftClass",
       "bio":bio,
       "personality":{"loyalty":30+d[6]%65,"greed":25+d[7]%70,
                      "ambition":30+d[8]%65,"personality":25+d[9]%70,
                      "workEthic":30+d[10]%65},
       "ratings":ratings,
       "development":development(ovr,age,peak),
       "contract":{"salary":0,"guarantee":0,"years":0,
                   "extension":{"salary":0,"guarantee":0,"years":0}},
    }

def main():
    files=(SEVEN,NINE,REPORT)
    if any(p.exists() for p in files):
        if not all(p.exists() for p in files):
            raise RuntimeError("Partial V10 export exists; do not overwrite")
        print("V10 versioned exports already frozen; reusing")
        return
    base=json.loads(BASE.read_text())
    assert base["schemaVersion"]==3 and base["meta"]["baseSeason"]==2020
    originals=base["players"]
    assert len(originals)==5173
    assert sum(p["pool"]=="roster" for p in originals)==2293
    old_names={canonical(p["forename"]+" "+p["surname"]) for p in originals}
    seen_id=set()
    byyear=defaultdict(list)
    for row in download():
        p=normalize_candidate(row)
        if not p or p["key"] in old_names or p["id"] in seen_id:continue
        seen_id.add(p["id"])
        byyear[p["draft"]].append(p)
    lib=template_library(originals)
    new=[]
    report={}
    for year in YEARS:
        roster=byyear[year]
        roster.sort(key=lambda p:(-quality(p),p["key"],p["id"]))
        chosen=[]
        used=set()
        perpos=defaultdict(int)
        for p in roster:
            if p["key"] in used or perpos[p["pos"]]>=QUOTAS[p["pos"]]:
                continue
            chosen.append(p)
            used.add(p["key"])
            perpos[p["pos"]]+=1
        missing={pos:count-perpos[pos] for pos,count in QUOTAS.items() if perpos[pos]<count}
        if missing:
            raise RuntimeError("Too few verifiable 2026 college identities for "+str(year)+": "+str(missing))
        assert len(chosen)==TARGET
        new.extend(projected_player(p,lib) for p in chosen)
        report[str(year)]={
            "source_candidates":len(roster),
            "projected_real_college_players":len(chosen),
            "fictional_added":0,
            "position_counts":dict(sorted(perpos.items())),
            "ranked_2027_candidates_included":sum(p["key"] in SCOUTED_2027 for p in chosen) if year==2027 else None,
            "class_year_rule":("junior/senior" if year==2027 else "sophomore" if year==2028 else "freshman")
        }
    assert len(new)==1440
    all_players=originals+new
    all_ids=[p["iden"] for p in all_players]
    assert len(all_ids)==len(set(all_ids))
    for file,yrs in ((SEVEN,{2027}),(NINE,set(YEARS))):
        data={"schemaVersion":3,"meta":{"baseSeason":2020},
              "players":originals+[p for p in new if p["bio"]["draftSeason"] in yrs],
              "deadCap":[]}
        file.write_text(json.dumps(data,separators=(",",":"))+"\n")
    summary={
       "status":"EXPERIMENTAL_FUTURE_DRAFT_PROJECTIONS_NOT_GAME_TESTED",
       "source":URL,"baseYear":2020,
       "baseRosterPlayers":2293,
       "preservedV9Records":len(originals),
       "projectedYears":report,
       "sevenClassTotal":len(originals)+480,
       "nineClassTotal":len(all_players),
       "limitations":[
         "2027, 2028, 2029 NFL draft declarations and exact eligibility are not known",
         "College 2026 class standing is an imperfect projection of future NFL entry year",
         "All attributes, scouting quality and hidden progression of future prospects are modeled, not authentic Madden or guaranteed future outcomes",
         "Only the 2027 projected early tier uses contemporary pre-draft scouting evidence",
         "Game might ignore years beyond six; must verify via disposable-save season progression",
         "No future NFL destination or pick order is forced",
         "Every 2021-2026 V9 player record, portrait, rating and hidden development setting preserved unchanged"
       ]
    }
    REPORT.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps({"status":summary["status"],
                      "sevenClassTotal":summary["sevenClassTotal"],
                      "nineClassTotal":summary["nineClassTotal"],
                      "byyear":{k:{"players":v["projected_real_college_players"],
                                   "fictional":v["fictional_added"]}
                                for k,v in report.items()}},indent=2))

if __name__=="__main__":
    main()
