"""Evidence-only backfill of drafted NFL prospects absent from an import.

Only use authentic Madden rows in the prospect's later NFL career or the
creator's 2026 Madden-derived player records; never invent a player or copy
their later NFL destination into the pre-draft CapForge class.

All reconstructed starting ratings are explicitly provisional. Hidden
potential is not printed or exported to reports.
"""
import copy
import csv
import hashlib
import io
import uuid
from collections import Counter, defaultdict

from audit_draft_classes import norm, ALIASES


def canonical(value):
    k=norm(value)
    return ALIASES.get(k,k)


def _name(record, fullname):
    return fullname(record)


def backfill_drafted_prospects(
    draft, historical_madden, fan_roster, draft_source_csv,
    build_player, teams, peaks, field, num, cut, calibrate, development,
    fullname, normal
):
    picks=list(csv.DictReader(io.StringIO(draft_source_csv.lstrip("\ufeff"))))
    current=defaultdict(set)
    for p in draft:
        current[int(p["bio"]["draftSeason"])].add(canonical(p["forename"]+" "+p["surname"]))

    # A missing 2021 Madden rookie can be found as an ordinary player
    # in the Madden 23 (2022) roster. Require correct years-pro to prevent
    # accidentally using two people with the same name.
    later=defaultdict(list)
    for src_year in sorted(historical_madden):
        if src_year<=2021:continue
        for record in historical_madden[src_year]:
            n=canonical(_name(record,fullname))
            if not n:continue
            age=int(num(record,"Age","age",default=0))
            pro=int(num(record,"Years Pro","years_pro","yearsPro",default=-1))
            if age<18 or pro<0:continue
            later[n].append((src_year,pro,record))

    # Fan creator 2026 roster is used only for a person with exactly
    # matching original draft class AND name. Never preassign their team.
    by_community=defaultdict(list)
    for p in fan_roster:
        year=p.get("bio",{}).get("draftSeason")
        if year is None:continue
        year=int(year)
        if year not in range(2021,2027):continue
        by_community[(year,canonical(p.get("forename","")+" "+p.get("surname","")))].append(p)

    repaired=Counter()
    unresolved=Counter()
    skipped_ls=Counter()
    duplicate_pick_names=Counter()
    used=set()

    for row in picks:
        try:year=int(row["Year"])
        except (ValueError,KeyError,TypeError):continue
        if year not in range(2021,2027):continue
        pick_name=row["Selection"].strip()
        key=canonical(pick_name)
        if not key or key in current[year]:continue
        if (year,key) in used:
            duplicate_pick_names[year]+=1
            continue
        used.add((year,key))
        if row["Position"].strip().upper()=="LS":
            # A separate LS position is not supported by current CapForge
            # import schema; do not disguise long snappers as elite TEs.
            skipped_ls[year]+=1
            continue

        def add(p, method):
            if not p:return False
            p["bio"]["draftSeason"]=year
            p["bio"]["draftNum"]=-1
            p["bio"]["jerseyNumber"]=0
            p["pool"]="draftClass"
            p.pop("teamAbbr",None)
            p.pop("teamId",None)
            draft.append(p)
            current[year].add(key)
            repaired[(year,method)]+=1
            return True

        candidates=[
            (src_year,record)
            for src_year,pro,record in later.get(key,[])
            if src_year>year and pro==src_year-year
        ]
        candidates.sort(key=lambda x:x[0])
        if candidates:
            src_year,record=candidates[0]
            rec=dict(record)
            elapsed=src_year-year
            rec["Full Name"]=pick_name
            rec["College"]=row.get("College","").strip()
            rec["Age"]=str(max(18,int(num(record,"Age","age",default=23))-elapsed))
            rec["Years Pro"]="0"
            # Post-draft observed OVR isn't a rookie OVR. Move it slightly
            # toward a more conservative draft-day baseline.
            observed=int(num(record,"Overall Rating","Overall","Rating",
                             "stats/overall/value",default=60))
            rec["Overall Rating"]=str(max(40,observed-2*elapsed))
            p=build_player(rec,year,"draftClass",teams,peaks)
            if add(p,"later_Madden"):
                continue

        match=by_community.get((year,key),[])
        # Ambiguous same-name players are never auto-filled.
        if len(match)==1:
            raw=match[0]
            current_ovr=int(raw.get("development",{}).get("ovr",55))
            p=copy.deepcopy(raw)
            full=pick_name.split(" ",1)
            if len(full)!=2:
                unresolved[year]+=1
                continue
            p["forename"],p["surname"]=full
            original_pos=p.get("position","")
            if not original_pos or original_pos not in (
                "QB","RB","WR","TE","OT","OG","C","DE","DT",
                "EDGE","LB","CB","S","K","P"
            ):
                unresolved[year]+=1
                continue
            years_elapsed=max(0,2026-year)
            orig_age=int(p.get("bio",{}).get("age",23))
            age=max(18,orig_age-years_elapsed)
            p["bio"]["age"]=age
            p["bio"]["college"]=row.get("College","").strip()
            p["bio"].pop("portraitId",None)
            p["iden"]=str(uuid.uuid5(uuid.NAMESPACE_URL,
                 "capforge-nfl-rewind-2020:historical-draft-backfill:"
                 +normal(pick_name)+"|"+str(year)+"|"+original_pos)).upper()
            target=cut(max(40,current_ovr-2*years_elapsed)+(
                 3 if current_ovr<70 else 2 if current_ovr<80 else 1),20,99)
            p["ratings"],target,_,_=calibrate(original_pos,p["ratings"],target)
            p["development"]=development(target,age,max(target,current_ovr))
            p["contract"]={"salary":0,"guarantee":0,"years":0,
                           "extension":{"salary":0,"guarantee":0,"years":0}}
            if "personality" not in p:
                h=hashlib.sha256((str(year)+pick_name).encode()).digest()
                p["personality"]={"loyalty":30+h[0]%65,"greed":25+h[1]%70,
                                  "ambition":30+h[2]%65,"personality":25+h[3]%70,
                                  "workEthic":30+h[4]%65}
            if add(p,"2026_community"):
                continue

        unresolved[year]+=1

    by_year={str(y):{
        "added_from_later_madden":repaired[(y,"later_Madden")],
        "added_from_community_2026":repaired[(y,"2026_community")],
        "unresolved_without_source":unresolved[y],
        "unmodeled_long_snappers":skipped_ls[y]
    } for y in range(2021,2027)}
    return {
        "source":"Actual draft picks cross-checked against 7LayerLabs 2017-2026 NFL drafts",
        "method":"Earliest reliable follow-up Madden roster or same-year 2026 community player; draft-day OVR conservatively reconstructed",
        "by_year":by_year,
        "total_added":sum(v for (y,m),v in repaired.items()),
        "remaining_limitations":"Not all drafted prospects have suitable individual-attribute source data; no unsupported players fabricated",
        "spoiler_policy":"No hidden player potential or future draft destinations in report"
    }
