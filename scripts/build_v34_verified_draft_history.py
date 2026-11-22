#!/usr/bin/env python3
"""V34 protected roster-only historical draftNum fix for starting 2020 rosters.

V33 V30 used -1 for every player, not just undrafted rookies, making real
drafted players appear undrafted and reportedly collapsing game trade value.
A real user test changed 2020 Joe Burrow's draft number -1 -> 1 and saw a
~6 -> ~4100 trade value; this is evidence, not proof of all engine internals.

This builder uses frozen actual 2000-2020 PFR draft facts to repair draftNum
ONLY when drafted year+normalized full name+position/age pass guardrails.
Keep draftSeason, class, roster team, all ratings, portraits, potential,
progression curves, contracts, hidden attributes, draft classes, etc. EXACT.
Do not invent pick numbers for undrafted/ambiguous/not-covered players.
"""
from __future__ import annotations
import collections,csv,hashlib,json,re,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
SOURCE=PREVIEW/"players-2020-nine-class-contracts-v30-TEST.json"
SOURCE_SHA_RECORD=PREVIEW/"v31-v30-real-2021-cap-rollover-audit.json"
NFL=ROOT/"data/nfl-draft-2000-2020-pfr-frozen.csv"
OUTPUT=PREVIEW/"players-2020-nine-class-draft-history-v34-TEST.json"
REPORT=PREVIEW/"v34-historical-draft-history-audit.json"
YEAR=2020
MAX_SOURCE_YEAR=2020
BIRTH_TOLERANCE=3
PFR_REFERENCE="https://github.com/pwendel3/NFL_Draft_Dashboard/blob/main/pfr_draft_complete_2000_2025.csv"
# More general historical official draft position labels map to CapForge ones.
P_COMP={
 "QB":{"QB"},"RB":{"RB"},"HB":{"RB"},"FB":{"RB"},"WR":{"WR"},
 "TE":{"TE"},"T":{"OT"},"OT":{"OT"},"G":{"OG"},"OG":{"OG"},"C":{"C"},
 "OL":{"OT","OG","C"},"DE":{"DE","EDGE","LB"},"DT":{"DT","DE"},
 "DL":{"DT","DE","EDGE"},"EDGE":{"EDGE","DE","LB"},
 "LB":{"LB","EDGE","DE"},"OLB":{"LB","EDGE","DE"},"ILB":{"LB"},
 "CB":{"CB","S"},"DB":{"CB","S"},"S":{"S","CB"},"SAF":{"S","CB"},
 "FS":{"S","CB"},"SS":{"S","CB"},"K":{"K"},"P":{"P"}
}

def norm(name):
    value=unicodedata.normalize("NFKD",str(name).casefold())
    value="".join(x for x in value if not unicodedata.combining(x))
    value=value.replace("’","").replace("'","")
    value=re.sub(r"\b(jr|sr|ii|iii|iv|v)\b","",value)
    return re.sub(r"[^a-z0-9]","",value)

def age_close(p,source_age,year):
    if not source_age:return True
    try: expected=float(source_age)+(YEAR-year)
    except ValueError:return True
    return abs(int(p["bio"]["age"])-expected)<=BIRTH_TOLERANCE

def position_close(p,row):
    return p["position"] in P_COMP.get(str(row.get("position","")).strip().upper(),set())

def valid_source():
    with NFL.open(newline="",encoding="utf-8-sig") as f: rows=list(csv.DictReader(f))
    assert len(rows)==5350,"Frozen PFR 2000-2020 draft source row count changed"
    seen=set()
    by_key=collections.defaultdict(list)
    by_year=collections.Counter()
    for row in rows:
        year=int(row["year"])
        pick=int(row["pick"])
        rd=int(row["round"])
        assert 2000<=year<=2020 and 1<=pick<=300 and 1<=rd<=7
        key=(year,pick)
        assert key not in seen,"Duplicate source draft pick number"
        seen.add(key)
        assert row["player"].strip()
        by_key[(year,norm(row["player"]))].append(row)
        by_year[year]+=1
    assert by_year[2020]==255 and by_year[2019]==254
    for name,pick in (("Joe Burrow",1),("Justin Jefferson",22),("Tua Tagovailoa",5),("Chase Young",2)):
        rows=by_key[(2020,norm(name))]
        assert len(rows)==1 and int(rows[0]["pick"])==pick
    return by_key,by_year

def main():
    if OUTPUT.exists() or REPORT.exists():
        assert OUTPUT.exists() and REPORT.exists(),"V34 published partially"
        print("V34 immutable candidate and report already exist, skipped")
        return
    frozen=json.loads(SOURCE.read_text())
    assert frozen["schemaVersion"]==3 and frozen["meta"]["baseSeason"]==YEAR
    assert len(frozen["players"])==6613 and frozen["deadCap"]==[]
    published=json.loads(SOURCE_SHA_RECORD.read_text())
    V30_SHA=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert V30_SHA==published["preservedHashes"]["V30PlayersSHA256"]
    assert sum(p["pool"]=="roster" for p in frozen["players"])==2293
    assert sum(p["pool"]=="draftClass" for p in frozen["players"])==4320
    picks,yearcounts=valid_source()
    import copy
    out=copy.deepcopy(frozen)
    seen_picks=set()
    by_year=collections.Counter()
    reasons=collections.Counter()
    eligible=collections.Counter()
    changed=0
    drafted_2020=0
    for p in out["players"]:
        if p["pool"]!="roster":
            continue
        assert p["bio"]["draftNum"]==-1,"V30 unexpectedly has pre-existing drafted number; audit first"
        year=p["bio"]["draftSeason"]
        if not isinstance(year,int) or year not in yearcounts:
            reasons["outside_documented_2000_2020_years"]+=1
            continue
        name=p["forename"]+" "+p["surname"]
        candidates=picks.get((year,norm(name)),[])
        if not candidates:
            reasons["no_name_in_given_draft_year_likely_udfa_or_mismatch"]+=1
            continue
        if len(candidates)!=1:
            reasons["ambiguous_same_name_and_year"]+=1
            continue
        pick=candidates[0]
        if not position_close(p,pick):
            reasons["position_mismatch_requires_manual_review"]+=1
            continue
        if not age_close(p,pick.get("age"),year):
            reasons["draft_age_mismatch_requires_manual_review"]+=1
            continue
        picknum=int(pick["pick"])
        assert 1<=picknum<=300
        assert (year,picknum) not in seen_picks,"Two roster players mapped to one real pick"
        seen_picks.add((year,picknum))
        p["bio"]["draftNum"]=picknum
        by_year[year]+=1
        changed+=1
        if year==2020:drafted_2020+=1
    assert changed>1200,("Unexpectedly small coverage of historical 2020 rostered draftees",changed)
    assert drafted_2020>=135,("Unexpectedly small 2020 rookie coverage",drafted_2020)
    assert by_year[2019]>=130 and by_year[2018]>=130
    assert sum(by_year.values())==changed
    by_identity={(norm(p["forename"]+" "+p["surname"]),p["bio"]["draftSeason"]):p for p in out["players"] if p["pool"]=="roster"}
    for person,number in (("Joe Burrow",1),("Justin Jefferson",22),("Tua Tagovailoa",5),("Chase Young",2),("CeeDee Lamb",17)):
        x=by_identity.get((norm(person),2020))
        assert x is not None,("Missing known 2020 rookie",person)
        assert x["bio"]["draftNum"]==number,("Incorrect rookie provenance",person)
    preserved=0
    unchanged_drafts=0
    for first,next_ in zip(frozen["players"],out["players"]):
        assert first["iden"]==next_["iden"]
        if first["pool"]=="draftClass":
            assert first==next_,"Future draft class must NEVER be rewritten"
            assert next_["bio"]["draftNum"]==-1,"Draft prospects remain unselected until real simulation"
            unchanged_drafts+=1
            continue
        assert {k:v for k,v in first.items() if k!="bio"}=={k:v for k,v in next_.items() if k!="bio"}
        assert {k:v for k,v in first["bio"].items() if k!="draftNum"}=={k:v for k,v in next_["bio"].items() if k!="draftNum"}
        assert first["development"]==next_["development"],"Hidden player potential mutated"
        assert first["contract"]==next_["contract"],"Salary-cap calibration mutated"
        assert first["ratings"]==next_["ratings"],"Player ability mutated"
        preserved+=1
    assert preserved==2293 and unchanged_drafts==4320
    assert out["meta"]==frozen["meta"] and out["deadCap"]==frozen["deadCap"]
    report={
      "status":"V34_PFR_DRAFT_HISTORY_REPAIRED_IMPORT_CANDIDATE_NOT_YET_TESTED_INSIDE_GAME",
      "baseVersion":"V30 Players + unchanged V2 Teams + unchanged V25 Staff",
      "newPlayersFile":OUTPUT.name,
      "source2020CapForgeRoster":SOURCE.name,
      "sourceV30SHA256":V30_SHA,
      "historicalDraftSource":PFR_REFERENCE,
      "frozenSourceFile":str(NFL.relative_to(ROOT)),
      "draftSourceYears":"2000-2020",
      "draftSourceSelections":sum(yearcounts.values()),
      "actual2020DraftSelectionsInSource":yearcounts[2020],
      "2020RookieDraftNumbersCorrected":drafted_2020,
      "allHistoricalRosterDraftNumbersCorrected":changed,
      "sourceVerifiedBySeasonCounts":{str(y):by_year[y] for y in sorted(by_year)},
      "unchangedRosterdPlayerCount":preserved,
      "futureDraftProspectsUnchanged":unchanged_drafts,
      "futureDraftClassCounts":{str(y):sum(p["pool"]=="draftClass" and p["bio"]["draftSeason"]==y for p in out["players"]) for y in range(2021,2030)},
      "unmappedRosterReasonCounts":dict(reasons),
      "knownPublic2020DraftPositionSanity":{"Joe Burrow":1,"Justin Jefferson":22,"Tua Tagovailoa":5,"Chase Young":2,"CeeDee Lamb":17},
      "potentialDisplayConcern":{
        "userObserved":"Burrow potential badge Impact before editor save and Franchise after manual edit/save",
        "underlyingDevelopmentValuesUnchangedByV34":True,
        "actualGamePotentialDisplayCorrectionConfirmed":False,
        "nextGameTest":"Import V34 into a disposable 2020 game and compare trade value/potential badge BEFORE touching edit, then verify after optionally saving without potential change."
      },
      "safeguards":[
        "Only bio.draftNum fields of source-verified already-drafted 2020 roster players are changed.",
        "No inferred draft selections for undrafted/unmatched/ambiguous or position/age-inconsistent players.",
        "All future draftClass records 2021-2029 remain byte-equivalent at record level, with -1 pre-draft until simulation chooses teams/picks.",
        "All player attribute ratings, potential, development/progressionCurve, portraits, team IDs, contracts, and cap source files remain unchanged.",
        "V30 user-approved contract file retained as rollback, separate V34 TEST file produced, existing saves cannot be retroactively fixed by an import."
      ],
      "limitations":[
        "The user's 2020 Joe Burrow trade-value experiment is single-player evidence, not a confirmed app formula.",
        "A drafted but unrecognized player may retain -1; do not invent picks for undrafted or ambiguous identities.",
        "Historical draftSeason was inferred from Madden years pro in earlier V30 and is not independently rewritten here; source-year mismatches are intentionally skipped.",
        "Real-game 2020 rookie trade values and potential tier label must be tested with a new disposable V34 league before replacing V30 in a permanent franchise.",
        "The potential-tier discrepancy may be a game editor refresh/import serialization issue separate from missing draftNum; do not alter hidden player progression blindly.",
        "V34 import changes starting roster provenance only; an existing CapForge save cannot be updated with the Players file."
      ]
    }
    assert '"progressionCurve":' not in json.dumps(report)
    assert '"potential":' not in json.dumps(report)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==V30_SHA
    OUTPUT.write_text(json.dumps(out,separators=(",",":"))+"\n")
    REPORT.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
      "status":report["status"],
      "2020RookiesWithRealDraftNumbers":drafted_2020,
      "total2020RosterDraftNumbersRepaired":changed,
      "historicalYearCounts":dict(by_year),
      "unmappedAggregateCounts":dict(reasons),
      "futureClassProspectsIntact":4320,
      "potentialModelAltered":False
    },indent=2))

if __name__=="__main__":
    main()
