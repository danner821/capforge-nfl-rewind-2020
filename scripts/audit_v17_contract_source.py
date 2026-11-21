#!/usr/bin/env python3
"""V17: audit OTC/nflverse historical-contract source BEFORE changing any salary.

This is a source-shape and identity coverage diagnostic only.
No V15 player JSON, portrait, development, or contract is modified.
"""
from __future__ import annotations
import csv,gzip,io,json,urllib.request,time
from collections import Counter,defaultdict
from pathlib import Path
from audit_draft_classes import norm

ROOT=Path(__file__).resolve().parents[1]
SOURCE_URL="https://github.com/nflverse/nflverse-data/releases/download/contracts/historical_contracts.csv.gz"
BASE=ROOT/"preview/players-2020-nine-class-scout-audit-v15.json"
TEAMS=ROOT/"preview/teams-2020-roofs-v2.json"
OUT=ROOT/"preview/v17-contract-source-coverage-audit.json"
ACTUAL_2020_NFL_CAP=198200000  # per NFL.com 2020 league statement
SIMULATOR_ASSUMED_CAP=300000000  # historic project builder's 2020 model
TEAMS_ALIASES={
 "WAS":{"Washington","Football Team","Redskins","Commanders"},
 "LV":{"Raiders","Las Vegas","Oakland"},
 "LAR":{"Rams","Los Angeles Rams"},
 "LAC":{"Chargers","Los Angeles Chargers"},
 "NYJ":{"Jets","New York Jets"},
 "NYG":{"Giants","New York Giants"},
}

def fetch():
    req=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"CapForge-NFL-Rewind-2020/V17"})
    for i in range(4):
        try:
            with urllib.request.urlopen(req,timeout=120) as response:
                return gzip.decompress(response.read()).decode("utf-8-sig")
        except Exception:
            if i==3:raise
            time.sleep(2**i)

def number(x):
    try:return int(float(str(x).replace(",","")))
    except (ValueError,TypeError):return None

def year_active(row,year):
    start=number(row.get("year_signed"))
    term=number(row.get("years"))
    return start is not None and term is not None and term>0 and start<=year<start+term

def team_matches(row,abbr,name):
    team=(row.get("team") or "").lower()
    aliases={name,abbr} | TEAMS_ALIASES.get(abbr,set())
    # Different OTC contract rows may include multiple teams from a trade.
    return any(a.lower() in team for a in aliases if len(a)>2)

def format_signature(raw):
    if not raw:return "empty"
    stripped=raw.strip()
    if not stripped:return "empty"
    try:
        nested=json.loads(stripped)
        return "json_"+type(nested).__name__
    except (ValueError,TypeError,RecursionError):
        if stripped.startswith(("list(","c(","structure(")):return "r_literal"
        if stripped.startswith("[") or stripped.startswith("{"):return "unparsed_json_like"
        return "other_serialized"

def main():
    if OUT.exists():
        print("V17 frozen audit exists; skipping");return
    meta=json.loads(TEAMS.read_text())
    by_team={x["abbr"]:x for x in meta["teams"]}
    assert len(by_team)==32
    base=json.loads(BASE.read_text())
    roster=[p for p in base["players"] if p["pool"]=="roster"]
    assert len(roster)==2293
    content=fetch()
    reader=csv.DictReader(io.StringIO(content))
    cols=reader.fieldnames or []
    required={"player","team","position","year_signed","years","value","apy","guaranteed"}
    assert required.issubset(cols),"Unexpected contract source headers "+repr(cols[:35])
    rows=list(reader)
    assert len(rows)>30000, "Contracts source unexpectedly small"
    byname=defaultdict(list)
    for row in rows:
        byname[norm(row.get("player",""))].append(row)
    results=Counter()
    matched_positions=Counter()
    unmatched_positions=Counter()
    for p in roster:
        name=norm(p["forename"]+" "+p["surname"])
        allname=byname.get(name,[])
        if not allname:
            results["no_name_match"]+=1
            unmatched_positions[p["position"]]+=1
            continue
        candidates=[r for r in allname if year_active(r,2020)]
        if not candidates:
            results["name_but_no_contract_covering_2020"]+=1
            unmatched_positions[p["position"]]+=1
            continue
        team=[r for r in candidates if team_matches(r,p["teamAbbr"],by_team[p["teamAbbr"]]["name"])]
        if len(team)==1:
            results["single_name_2020_term_and_team_match"]+=1
            matched_positions[p["position"]]+=1
        elif len(team)>1:
            results["ambiguous_multiple_contracts"]+=1
        else:
            results["name_active_but_team_mismatch"]+=1
            unmatched_positions[p["position"]]+=1
    assert sum(results.values())==2293
    signed=Counter()
    for row in rows:
        y=number(row.get("year_signed"))
        if y is not None and y in range(2016,2022):signed[str(y)]+=1
    signatures=Counter(format_signature(r.get("season_history")) for r in rows)
    history_cols={"season_history","contract_history"}.intersection(cols)
    report={
        "status":"V17_SOURCE_AUDIT_ONLY_DO_NOT_USE_AS_REPLACEMENT_CONTRACTS",
        "source":SOURCE_URL,
        "source_dictionary":"https://nflreadr.nflverse.com/articles/dictionary_contracts.html",
        "source_scope":"OverTheCap historic NFL contract rows; year_signed + years is an approximate 2020 range filter, NOT actual full 2020 cap charge",
        "totalSourceContractRecords":len(rows),
        "sourceSchemaFields":cols,
        "yearSignedCountsSelected":dict(sorted(signed.items())),
        "nestedHistoryFieldsAvailable":sorted(history_cols),
        "seasonHistorySerializedTypes":dict(signatures),
        "startingRoster":len(roster),
        "matchCountDiagnostic":dict(results),
        "singleMatchedPositionCounts":dict(sorted(matched_positions.items())),
        "unmatchedPositionCounts":dict(sorted(unmatched_positions.items())),
        "actualNFL2020BaseCap":ACTUAL_2020_NFL_CAP,
        "assumedCapForgeSimulatorCap":SIMULATOR_ASSUMED_CAP,
        "actualToSimulatorCapRatioReference":round(SIMULATOR_ASSUMED_CAP/ACTUAL_2020_NFL_CAP,6),
        "contractAccuracyWarnings":[
            "Original V15 2020 contracts are heuristically generated and all 32 modeled payrolls are near $285M",
            "Contract years/signed dates may be historical but do not establish whether the contract was still in force on Week 1 of 2020",
            "Source team values may contain multiple teams due trades; name+team matching is not enough for all players",
            "2020 annual cap hit, bonus proration, cash and guaranteed salary need year-specific season_history data",
            "Nested CSV fields may not preserve machine-readable structures; prefer original parquet if inaccessible",
            "A recent nflreadr issue reports duplicate season_history entries; validate independently before any rewrite",
            "Actual NFL 2020 salary cap differs from CapForge modeled 300M cap and cannot simply be transcribed unchanged",
            "This diagnostic cannot claim real 2020 signed deals or balanced game cap headroom"
        ],
        "nextAction":"Recover reliable season_history 2020 rows; corroborate candidate identities/team/2020 cap numbers; build separate V14 salary import only after >=95% uniquely verified coverage and explicit fallback auditing",
        "privacy":"Aggregate counts only; no player potential, hidden progression or personal contract values",
    }
    OUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({"status":report["status"],
        "contracts":len(rows),
        "matched":results["single_name_2020_term_and_team_match"],
        "ambiguous":results["ambiguous_multiple_contracts"],
        "unmatched":2293-results["single_name_2020_term_and_team_match"],
        "season_history_shapes":dict(signatures)},indent=2))
if __name__=="__main__":
    main()
