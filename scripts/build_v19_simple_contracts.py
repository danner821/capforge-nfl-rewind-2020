#!/usr/bin/env python3
"""V19: game-scale, source-informed 2020 contracts for a SEPARATE trial import.

Keep all V15 player fields (including hidden progression) byte-equivalent at
record level except starting-roster contract. Do not change draft-class deals.
Use only OTC contracts signed before/during 2020 with a matching 2020 annual
cap record; fall back explicitly if identity or yearly numbers are ambiguous.
Translate to CapForge's simple salary/bonus/guarantee/year-by-year fields.
No player-level salary, hidden potential or individual result in public report.
"""
from __future__ import annotations
import collections
import copy
import hashlib
import io
import json
import math
import re
from pathlib import Path
import pyarrow.parquet as pq
from audit_v18_parquet_2020 import get_bytes, normalized_name, integer, SOURCE
from capforge_ovr import estimate

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
INPUT=PREVIEW/"players-2020-nine-class-scout-audit-v15.json"
OUTPUT=PREVIEW/"players-2020-nine-class-contracts-v19.json"
REPORT=PREVIEW/"v19-simplified-contracts-audit.json"
REFERENCE=PREVIEW/"v18-parquet-contract-history-audit.json"
TEAMS=PREVIEW/"teams-2020-roofs-v2.json"

SIM_CAP=300_000_000
NFL_CAP_2020=198_200_000
SOURCE_CAP_SCALER=SIM_CAP/NFL_CAP_2020
START_YEAR=2020
MIN_SALARY=850_000
# Aim for at least $20m of modeled headroom for all clubs at the beginning.
MAX_OPENING_CHARGE=280_000_000
ROUND=1000
TEAM_ALIASES={
 "ARI":("arizona","cardinals"),"ATL":("atlanta","falcons"),
 "BAL":("baltimore","ravens"),"BUF":("buffalo","bills"),
 "CAR":("carolina","panthers"),"CHI":("chicago","bears"),
 "CIN":("cincinnati","bengals"),"CLE":("cleveland","browns"),
 "DAL":("dallas","cowboys"),"DEN":("denver","broncos"),
 "DET":("detroit","lions"),"GB":("greenbay","packers"),
 "HOU":("houston","texans"),"IND":("indianapolis","colts"),
 "JAX":("jacksonville","jaguars"),"KC":("kansascity","chiefs"),
 "LAC":("losangeleschargers","sandiegochargers","chargers"),
 "LAR":("losangelesrams","stlouisrams","rams"),
 "LV":("lasvegas","oakland","raiders"),"MIA":("miami","dolphins"),
 "MIN":("minnesota","vikings"),"NE":("newengland","patriots"),
 "NO":("neworleans","saints"),"NYG":("newyorkgiants","giants"),
 "NYJ":("newyorkjets","jets"),"PHI":("philadelphia","eagles"),
 "PIT":("pittsburgh","steelers"),"SEA":("seattle","seahawks"),
 "SF":("sanfrancisco","49ers"),"TB":("tampabay","buccaneers"),
 "TEN":("tennessee","titans"),"WAS":("washington","redskins","footballteam","commanders")
}
POSITION_GROUP={
 "QB":"QB","HB":"RB","FB":"RB","RB":"RB",
 "WR":"WR","TE":"TE","OT":"OL","T":"OL","RT":"OL","LT":"OL","OG":"OL","G":"OL","LG":"OL","RG":"OL","C":"OL","OL":"OL",
 "DE":"DL","EDGE":"DL","DL":"DL","DT":"DL","NT":"DL",
 "LB":"LB","OLB":"LB","ILB":"LB","MLB":"LB","CB":"CB","DB":"DB","FS":"DB","SS":"DB","S":"DB",
 "K":"K","P":"P"
}

def money(x,default=0):
    try:
        if x is None:return default
        val=float(x)
        if math.isfinite(val) and val>=0:return val
    except (ValueError,TypeError,OverflowError):
        pass
    return default

def round1k(value):
    return int(max(0,round(value/ROUND)*ROUND))

def canonical_team_token(x):
    return re.sub(r"[^a-z0-9]","",str(x or "").lower())

def matching_team(raw,abbr):
    if not raw:return False
    x=canonical_team_token(raw)
    if x==abbr.lower() or x in TEAM_ALIASES[abbr]:return True
    # The source sometimes lists trades as ATL/NE. Match exact split tokens.
    pieces=re.split(r"[/,&;|\s]+",str(raw))
    if any(canonical_team_token(token)==abbr.lower() for token in pieces):
        return True
    return any(len(t)>3 and t in x for t in TEAM_ALIASES[abbr])

def matching_pos(nflpos,gamepos):
    a=POSITION_GROUP.get(str(nflpos or "").strip().upper())
    b=POSITION_GROUP.get(gamepos)
    if a==b:return True
    if a in ("CB","DB") and b in ("CB","DB"):return True
    if a=="DL" and b=="LB":return True
    if a=="LB" and b=="DL":return True
    return False

def college_match(src_college,game_college):
    a=canonical_team_token(src_college)
    b=canonical_team_token(game_college)
    return bool(a and b and (a==b or (len(a)>=5 and len(b)>=5 and (a in b or b in a))))

def annual_rows(contract):
    arr=contract.get("season_history") or []
    if not isinstance(arr,list):return {}
    out={}
    for d in arr:
        if not isinstance(d,dict):continue
        yr=integer(d.get("year"))
        if yr is None or yr<START_YEAR or yr>START_YEAR+4:continue
        if yr in out:
            # Duplicates cannot be represented faithfully; discard this
            # entire contract as a source of annual financial figures.
            return {}
        out[yr]=d
    return out

def source_contract_candidates(player,contracts):
    matches=[]
    for row in contracts:
        start=integer(row.get("year_signed"))
        length=integer(row.get("years"))
        if start is None or length is None or length<1 or start>2020 or start+length<=2020:
            continue
        annual=annual_rows(row)
        entry=annual.get(2020)
        if not entry:continue
        cap=money(entry.get("cap_number"))
        base=money(entry.get("base_salary"))
        bonus=money(entry.get("prorated_bonus"))
        if cap<300_000 and base+bonus<300_000:continue
        annual_team=matching_team(entry.get("team"),player["teamAbbr"])
        contract_team=matching_team(row.get("team"),player["teamAbbr"])
        if not annual_team and not contract_team:continue
        position_good=matching_pos(row.get("position"),player["position"])
        college_good=college_match(row.get("college"),player["bio"].get("college"))
        # Source with conflicting known position AND college is a likely
        # namesake, not a valid match even if a 2020 team token coincides.
        if not position_good and row.get("position") and not college_good:
            continue
        score=(100 if annual_team else 0)+(35 if contract_team else 0)+(
            20 if position_good else 0)+(8 if college_good else 0)
        # Match a real player with its draft year where possible.
        src_draft=integer(row.get("draft_year"))
        game_draft=integer(player["bio"].get("draftSeason"))
        if src_draft and game_draft and src_draft==game_draft:score+=10
        matches.append((score,start,cap,row,annual))
    if not matches:return None,"fallback_missing_or_mismatched_annual_source"
    matches.sort(key=lambda x:(x[0],x[1],x[2]),reverse=True)
    best=matches[0]
    if len(matches)>1:
        next_=matches[1]
        # If same score but a different contract or uncertain identity,
        # leave the player on a disclosed approximation.
        if best[0]==next_[0] and best[1]==next_[1]:
            return None,"fallback_ambiguous_2020_source"
        if best[0]<next_[0]+15 and best[1]<=next_[1]:
            return None,"fallback_ambiguous_2020_source"
    if best[0]<120:
        return None,"fallback_low_confidence_match"
    label="sourced_unambiguous" if len(matches)==1 else "sourced_disambiguated"
    return (best[3],best[4]),label

def first_year_source(record):
    cap=money(record.get("cap_number"))
    base=money(record.get("base_salary"))
    proration=money(record.get("prorated_bonus"))
    if cap<300_000:cap=base+proration+money(record.get("roster_bonus"))
    if cap<300_000:return None
    # Contract-wide cap charge is the simpler game analogue. Keep known
    # prorated bonus separated, never count it twice as salary.
    bonus=min(proration,cap*0.6)
    salary=max(MIN_SALARY,cap-bonus)
    guarantee=min(salary,money(record.get("guaranteed_salary")))
    return (salary,bonus,guarantee)

def fallback_terms(player):
    old=player["contract"]
    years=max(1,min(5,integer(old.get("years")) or 1))
    year_drafted=integer(player["bio"].get("draftSeason"))
    # Prior game heuristic gives almost all players 1-year contracts.
    # Preserve a rookie's remaining four-season agreement where source
    # data cannot be resolved; never confer multi-year deals on veterans.
    if year_drafted is not None and 2017<=year_drafted<=2020 and player["bio"]["age"]<=26:
        years=max(years,4-(2020-year_drafted))
    salary=max(MIN_SALARY,money(old.get("salary"))*.78)
    values=[(salary*(1.03**i),0,salary*0.12 if i==0 else 0)
            for i in range(years)]
    return years,values

def source_terms(player,source,first):
    row,yearly=source
    start=integer(row.get("year_signed"))
    length=integer(row.get("years"))
    remain=max(1,min(5,start+length-2020))
    values=[]
    previous=first_year_source(first)
    if previous is None:return None
    for i in range(remain):
        y=2020+i
        item=yearly.get(y)
        result=first_year_source(item) if item else None
        if result is None:
            # Flat-ish forward projection when there is no *documented*
            # annual charge. Preserve the signed duration (not APY).
            salary=previous[0]*(1.035**i)
            bonus=previous[1]
            guaranteed=0
            result=(salary,bonus,guaranteed)
        values.append(result)
    return remain,values

def scale_items(prepared):
    by_team=collections.defaultdict(list)
    for p,item in prepared:
        by_team[p["teamAbbr"]].append(item)
    assert len(by_team)==32
    def total(items,factor):
        amount=0
        for v in items:
            salary,bonus,_=v[0]
            amount+=max(MIN_SALARY,round1k(salary*factor))
            amount+=round1k(bonus*factor)
        return amount
    upper=max(total(items,SOURCE_CAP_SCALER) for items in by_team.values())
    factor=SOURCE_CAP_SCALER
    if upper>MAX_OPENING_CHARGE:
        lo,hi=0.0,SOURCE_CAP_SCALER
        for _ in range(48):
            mid=(lo+hi)/2
            if max(total(items,mid) for items in by_team.values())<=MAX_OPENING_CHARGE:
                lo=mid
            else:
                hi=mid
        factor=lo
    # Safety slack for game interpretation and rounding.
    factor*=0.997
    opening={}
    for team,items in by_team.items():
        opening[team]=total(items,factor)
    assert max(opening.values())<=MAX_OPENING_CHARGE+ROUND
    assert min(opening.values())>=100_000_000,"Unexpectedly low opening CapForge payroll"
    return factor,opening

def map_contract(item,factor):
    years,values=item
    salary_by=[]
    bonus_by=[]
    guarantee_by=[]
    for salary,bonus,guarantee in values:
        s=max(MIN_SALARY,round1k(salary*factor))
        b=round1k(bonus*factor)
        g=min(s,round1k(guarantee*factor))
        salary_by.append(s)
        bonus_by.append(b)
        guarantee_by.append(g)
    assert 1<=years<=5 and len(salary_by)==years
    return {
        "salary":salary_by[0],
        "guarantee":guarantee_by[0],
        "years":years,
        # Import starts 2020 with first year of REMAINING deal. Real signed
        # year isn't reproduced; source labels are in private logic only.
        "signedSeason":2020,
        "salaryByYear":salary_by,
        "bonusByYear":bonus_by,
        "guaranteeByYear":guarantee_by,
        "currentGuarantee":guarantee_by[0],
        "currentYearIndex":0,
        "extension":{"salary":0,"guarantee":0,"years":0}
    }

def main():
    if OUTPUT.exists() or REPORT.exists():
        if not OUTPUT.exists() or not REPORT.exists():
            raise RuntimeError("Partial V19 assets: will not overwrite protected preview")
        print("V19 preview frozen; skipping generation")
        return
    base=json.loads(INPUT.read_text())
    assert base["schemaVersion"]==3 and base["meta"]["baseSeason"]==2020
    assert len(base["players"])==6613 and base["deadCap"]==[]
    actual=[p for p in base["players"] if p["pool"]=="roster"]
    assert len(actual)==2293
    v18=json.loads(REFERENCE.read_text())
    asset=get_bytes(SOURCE)
    # Reproduce exact V18 source snapshot (protect from silent source updates).
    source_sha=hashlib.sha256(asset).hexdigest()
    assert source_sha==v18["parquet_sha256"],"OTC source changed: re-audit before contract import"
    source=pq.read_table(io.BytesIO(asset))
    assert len(source)==v18["source_contract_rows"]
    columns=["player","position","team","year_signed","years","college",
             "draft_year","gsis_id","otc_id","season_history"]
    entries=source.select(columns).to_pylist()
    by_name=collections.defaultdict(list)
    for row in entries:
        by_name[normalized_name(row["player"])].append(row)
    result=copy.deepcopy(base)
    lookup={p["iden"]:p for p in result["players"]}
    audit=collections.Counter()
    years_hist=collections.Counter()
    prepared=[]
    preview_samples=[]
    for original in actual:
        identity=normalized_name(original["forename"]+" "+original["surname"])
        candidate,kind=source_contract_candidates(original,by_name.get(identity,[]))
        if candidate is not None:
            terms=source_terms(original,candidate,candidate[1].get(2020))
            if terms is None:
                terms=fallback_terms(original)
                kind="fallback_invalid_annual_charge"
        else:
            terms=fallback_terms(original)
        audit[kind]+=1
        years_hist[terms[0]]+=1
        prepared.append((original,terms))
    assert sum(audit.values())==2293
    sourced=sum(v for k,v in audit.items() if k.startswith("sourced"))
    assert sourced>=1200,"Insufficient annual historical coverage for trial; don't publish"
    factor,opening=scale_items(prepared)
    for original,item in prepared:
        p=lookup[original["iden"]]
        p["contract"]=map_contract(item,factor)
    for before in base["players"]:
        after=lookup[before["iden"]]
        if before["pool"]!="roster":
            assert after==before,"Historical 2021-29 draft class changed"
        else:
            stripped_before={k:v for k,v in before.items() if k!="contract"}
            stripped_after={k:v for k,v in after.items() if k!="contract"}
            assert stripped_before==stripped_after,"Player attributes/portraits/ratings/progression changed"
    payroll=collections.Counter()
    for p in result["players"]:
        if p["pool"]!="roster":continue
        c=p["contract"]
        assert all(k in c for k in ("salary","guarantee","years","salaryByYear","bonusByYear","guaranteeByYear","currentGuarantee","currentYearIndex"))
        assert len(c["salaryByYear"])==len(c["bonusByYear"])==len(c["guaranteeByYear"])==c["years"]
        assert c["salary"]==c["salaryByYear"][0]
        assert c["guarantee"]==c["currentGuarantee"]==c["guaranteeByYear"][0]
        assert all(0<=g<=s for s,g in zip(c["salaryByYear"],c["guaranteeByYear"]))
        payroll[p["teamAbbr"]]+=c["salary"]+c["bonusByYear"][0]
    assert dict(payroll)==dict(collections.Counter(opening))
    assert max(payroll.values())<=MAX_OPENING_CHARGE+ROUND
    assert len({round(v/100_000)*100_000 for v in payroll.values()})>=8,"Team cap totals suspiciously uniform"
    result["players"]=[lookup[p["iden"]] for p in base["players"]]
    OUTPUT.write_text(json.dumps(result,separators=(",",":"))+"\n")
    report={
        "status":"V19_STRUCTURAL_PASS_GAME_IMPORT_AND_FREE_AGENCY_UNTESTED",
        "playerFile":OUTPUT.name,
        "baseFile":INPUT.name,
        "baseFileSha256":hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "source":SOURCE,
        "sourceParquetSha256":source_sha,
        "totalPlayers":len(result["players"]),
        "startingRosterPlayers":2293,
        "protectedDraftClassPlayers":4320,
        "protectedNonContractFieldsFor2020Players":True,
        "contractSourceConfidence":dict(audit),
        "contractsWith2020AnnualSource":sourced,
        "fallbackContracts":2293-sourced,
        "remainingYearsHistogram":dict(sorted(years_hist.items())),
        "gameModel":{
            "baseSeason":2020,
            "gameCap":SIM_CAP,
            "sourceNFL2020BaseCap":NFL_CAP_2020,
            "unrestrictedHistoricalConversionFactor":round(SOURCE_CAP_SCALER,6),
            "effectiveCommonGameScaleFactor":round(factor,8),
            "minimumYearlyBaseSalary":MIN_SALARY,
            "maximumOpeningTeamSalaryPlusBonus":MAX_OPENING_CHARGE,
            "openingSalaryPlusBonusByTeam":dict(sorted(payroll.items())),
            "openingSalaryPlusBonusRange":{"min":min(payroll.values()),"max":max(payroll.values())},
            "yearIndexConvention":"Every starting player begins at index 0 of REMAINING contract; signedSeason=2020 is importer normalization, not historical signed date",
            "sourceChargeMapping":"annual cap_number less source prorated_bonus -> salaryByYear; source prorated_bonus -> bonusByYear, never double counted; guarantees capped at salary",
            "fallbackTerms":"original V15 contract estimate; 2020 recent draft picks may receive remaining four-year rookie term; otherwise conservative salary model",
            "leagueWideScaleNotExactNFL":"Common game scaling factor adjusted to keep the highest 2020 modeled team under $280M; team payrolls differ, no per-team forced equal totals"
        },
        "limitations":[
            "A sourced contract is a plausible 2020 player/team/annual match, not fully audited legal NFL contract accuracy.",
            "OTC annual breakdowns and future years can reflect restructures after 2020; all imported amounts are gameplay approximations.",
            "Some ambiguous identities or absent 2020 annual rows use a disclosed baseline estimate.",
            "Game salary/bonus/guarantee interpretation and future free agency must be inspected in a disposable 2020 CapForge save.",
            "DeadCap remains empty, as in V15; real historical dead-cap accuracy is not reconstructed.",
            "Actual NFL 2020 cap $198.2M is not the game's $300M cap; all figures are game-scaled, not true historical NFL dollar amounts.",
            "2020 starting roster includes more than 53 players per team; modeled payrolls cover the whole imported roster.",
            "All draft picks, ratings, potentials, portraits, teams, names and staff remain unchanged."
        ],
        "privacy":"Only aggregate source confidence and team-level modeled totals; no individual salaries or hidden progression"
    }
    REPORT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
        "result":report["status"],
        "historicAnnualContractsUsed":sourced,
        "fallbackPlayers":2293-sourced,
        "teams":32,
        "gameScale":report["gameModel"]["effectiveCommonGameScaleFactor"],
        "openingPayrollMin":min(payroll.values()),
        "openingPayrollMax":max(payroll.values()),
        "remainingYearsHistogram":dict(years_hist)
    },indent=2))

if __name__=="__main__":
    main()
