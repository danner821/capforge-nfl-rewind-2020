#!/usr/bin/env python3
"""V18: audit nflverse historical contracts PARQUET annual history; no roster edits.

No historical contract terms are inferred from APY / total value. This only
measures whether source annual breakdowns exist and can be identified safely.
Published report includes aggregates and field names, never individual salary,
potential, development or player data.
"""
from __future__ import annotations
import hashlib
import io
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
import pyarrow.parquet as pq

ROOT=Path(__file__).resolve().parents[1]
PREVIEW=ROOT/"preview"
INPUT=PREVIEW/"players-2020-nine-class-scout-audit-v15.json"
OUTPUT=PREVIEW/"v18-parquet-contract-history-audit.json"
SOURCE="https://github.com/nflverse/nflverse-data/releases/download/contracts/historical_contracts.parquet"
SOURCE_DICTIONARY="https://nflreadr.nflverse.com/articles/dictionary_contracts.html"
CAPFIELDS=("cap_number","cap_hit","cap_hit_pct","base_salary","salary","signing_bonus","prorated_bonus","roster_bonus","option_bonus","incentives","guarantee","guaranteed","cash_paid","cash")
YEARFIELDS=("year","season","season_year","contract_year","season_id","year_id")

def get_bytes(url):
    req=urllib.request.Request(url,headers={"User-Agent":"CapForge-Rewind2020-OTC-Source-Audit-V18"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=150) as f:
                value=f.read()
            if len(value)<100_000:raise RuntimeError("Unexpectedly small historical parquet asset")
            return value
        except Exception:
            if attempt==3:raise
            time.sleep(2**attempt)

def integer(x):
    try:
        if x is None:return None
        return int(float(str(x).replace(",",")))
    except (ValueError,TypeError,OverflowError):
        return None

def normalized_name(name):
    if name is None:return ""
    name=str(name).lower().replace("’","").replace("'","")
    name=re.sub(r"\b(jr|sr|ii|iii|iv)\b","",name)
    return re.sub(r"[^a-z0-9]","",name)

def shape(value):
    if value is None:return "null"
    if isinstance(value,list):return "list"
    if isinstance(value,dict):return "struct"
    if isinstance(value,str):return "string"
    return type(value).__name__

def flatten_structs(value,depth=0):
    if depth>4:return
    if isinstance(value,dict):
        yield value
        for v in value.values():
            if isinstance(v,(dict,list)):
                yield from flatten_structs(v,depth+1)
    elif isinstance(value,list):
        for v in value:
            yield from flatten_structs(v,depth+1)

def candidate_season(record):
    if not isinstance(record,dict):return None
    for k,v in record.items():
        if str(k).lower() in YEARFIELDS:
            y=integer(v)
            if y is not None and 1990<=y<=2040:return y
    return None

def norm_team(s):
    s=re.sub(r"[^a-z0-9]","",str(s or "").lower())
    return s

def expected_team_tokens(abbr,team_name):
    alias={
      "LV":["raiders","oakland","lasvegas","lv"],
      "WAS":["redskins","washington","footballteam","commanders"],
      "LAR":["rams","losangelesrams","stlouis"],
      "LAC":["chargers","losangeleschargers","sandiego"],
      "NYG":["giants","newyorkgiants"],
      "NYJ":["jets","newyorkjets"],
    }
    vals=[abbr,team_name]+alias.get(abbr,[])
    return [norm_team(t) for t in vals if len(norm_team(t))>=3]

def main():
    if OUTPUT.exists():
        print("V18 versioned research report already exists; refusing overwrite")
        return
    starting=json.loads(INPUT.read_text())
    assert starting["schemaVersion"]==3 and starting["meta"]["baseSeason"]==2020
    roster=[p for p in starting["players"] if p["pool"]=="roster"]
    assert len(roster)==2293 and len(starting["players"])==6613
    teams=json.loads((PREVIEW/"teams-2020-roofs-v2.json").read_text())["teams"]
    team_names={t["abbr"]:t["name"] for t in teams}
    assert len(team_names)==32

    asset=get_bytes(SOURCE)
    tab=pq.read_table(io.BytesIO(asset))
    fields=list(tab.column_names)
    assert len(tab)>30_000, "Unexpected historical contract source size"
    assert {"player","team","year_signed","years"}.issubset(fields),fields
    column_types={field.name:str(field.type) for field in tab.schema}
    # Avoid json-serializing personal records: keep all intermediate candidate
    # matching in-memory only; publish field names/counts with no identifiers.
    wanted=[x for x in ("player","team","year_signed","years","otc_id","season_history") if x in fields]
    dataset=tab.select(wanted).to_pylist()
    assert len(dataset)==len(tab)
    by_name=defaultdict(list)
    for idx,record in enumerate(dataset):
        by_name[normalized_name(record.get("player"))].append(idx)

    shapes=Counter()
    annual_field_names=Counter()
    year_record_counts=Counter()
    annual_records_present=0
    nonempty_history_contracts=0
    duplicate_seasons_in_contract=0
    nonparseable_with_history=0
    example_types=Counter()
    annual_by_contract={}
    for idx,row in enumerate(dataset):
        hist=row.get("season_history")
        shapes[shape(hist)]+=1
        if hist is None or hist==[] or hist=="":
            continue
        nonempty_history_contracts+=1
        example_types[shape(hist)]+=1
        # Only recognize a given 2020 record if year explicitly tagged 2020.
        structs=list(flatten_structs(hist))
        annual=Counter()
        for d in structs:
            annual_field_names.update(str(k) for k in d.keys())
            year=candidate_season(d)
            if year is not None:
                annual[year]+=1
                year_record_counts[str(year)]+=1
        if not annual:
            nonparseable_with_history+=1
        if any(count>1 for count in annual.values()):
            duplicate_seasons_in_contract+=1
        annual_by_contract[idx]=annual

    outcomes=Counter()
    history_match=Counter()
    ambiguous_with_history=0
    duplicate_2020_matched_contracts=0
    verified_candidate_count=0
    for p in roster:
        name=normalized_name(p["forename"]+" "+p["surname"])
        same=by_name.get(name,[])
        if not same:
            outcomes["no_name_match"]+=1
            continue
        active=[]
        for idx in same:
            r=dataset[idx]
            start=integer(r.get("year_signed")); term=integer(r.get("years"))
            if start is not None and term is not None and term>0 and start<=2020<start+term:
                active.append(idx)
        if not active:
            outcomes["name_no_2020_term"]+=1
            continue
        team_tokens=expected_team_tokens(p["teamAbbr"],team_names[p["teamAbbr"]])
        match=[idx for idx in active if any(tok in norm_team(dataset[idx].get("team")) for tok in team_tokens)]
        if len(match)==1:
            outcomes["one_name_term_team_candidate"]+=1
            idx=match[0]
            entries=annual_by_contract.get(idx,Counter())
            if entries.get(2020,0)==1:
                history_match["unique_contract_with_single_2020_annual_entry"]+=1
                verified_candidate_count+=1
            elif entries.get(2020,0)>1:
                history_match["unique_contract_with_duplicate_2020_annual_entries"]+=1
                duplicate_2020_matched_contracts+=1
            else:
                history_match["unique_contract_without_2020_annual_entry"]+=1
        elif len(match)>1:
            outcomes["ambiguous_team_and_term_candidates"]+=1
            if any(annual_by_contract.get(idx,Counter()).get(2020,0)>0 for idx in match):
                ambiguous_with_history+=1
        else:
            outcomes["team_mismatch"]+=1
    assert sum(outcomes.values())==2293

    # Determine if annual fields include cap charge/salary components without
    # making false assertions of their accuracy/appropriateness.
    common_annual=sorted(k for k,v in annual_field_names.items() if v>=100)
    possible_cap=[k for k in common_annual if any(t in k.lower() for t in CAPFIELDS)]
    report={
        "status":"V18_PARQUET_SOURCE_SHAPE_AUDIT_ONLY_NO_PLAYER_CONTRACTS_CHANGED",
        "source":SOURCE,
        "source_dictionary":SOURCE_DICTIONARY,
        "parquet_sha256":hashlib.sha256(asset).hexdigest(),
        "parquet_bytes":len(asset),
        "source_contract_rows":len(dataset),
        "source_field_names":fields,
        "source_column_types":column_types,
        "annual_history_source_column": "season_history" if "season_history" in fields else None,
        "season_history_field_shapes":dict(shapes),
        "nonempty_history_contracts":nonempty_history_contracts,
        "nested_history_value_shapes":dict(example_types),
        "annual_nested_field_names_and_counts":dict(annual_field_names),
        "common_annual_field_names":common_annual,
        "possible_cap_related_annual_fields":possible_cap,
        "annual_recognized_year_counts":dict(year_record_counts),
        "contracts_with_duplicate_recognized_years":duplicate_seasons_in_contract,
        "contracts_with_nonempty_but_unparseable_years":nonparseable_with_history,
        "2020_starting_roster_count":2293,
        "2020_roster_candidate_matches":dict(outcomes),
        "annual_2020_history_for_unique_candidate":dict(history_match),
        "ambiguous_candidates_with_some_2020_history":ambiguous_with_history,
        "duplicate_2020_history_for_unique_candidate":duplicate_2020_matched_contracts,
        "unique_team_term_candidates_with_one_explicit_2020_history":verified_candidate_count,
        "cap_model": {
            "actual_2020_NFL_base_cap":198200000,
            "CapForge_previously_assumed_model_cap":300000000,
            "direct_ratio_is_not_an_approved_scaling_policy":True
        },
        "next_gate":"Identify stable 2020 season cap-hit/bonus fields; reconcile duplicates and missing/ambiguous players; determine actual CapForge salary mechanics before any new versioned contract import.",
        "limitations":[
           "This is source-shape and candidate-match evidence, not verified historical salary accuracy.",
           "Term overlap is not sufficient to prove contract was in force on Week 1 of 2020.",
           "Some annual rows might be duplicated or omit the season label.",
           "No player contract numbers or hidden development values are written to this report.",
           "Existing approved V15 players, V16 staff, and all saves are left unchanged."
        ]
    }
    OUTPUT.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({
      "status":report["status"],"source_rows":len(dataset),
      "annual_nonempty_contracts":nonempty_history_contracts,
      "annual_years_unparseable":nonparseable_with_history,
      "single_matching_2020_annual_history":verified_candidate_count,
      "ambiguous_candidates":outcomes["ambiguous_team_and_term_candidates"],
      "annual_structural_duplicates":duplicate_seasons_in_contract,
      "common_annual_fields":common_annual[:30],
    },indent=2))

if __name__=="__main__":
    main()
