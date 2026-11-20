#!/usr/bin/env python3
"""V12 spoiler-free regression checks: build on frozen V11, not overwrite it."""
import json
from collections import Counter
from pathlib import Path
from build_v12_future import PRIORITY, key
from capforge_ovr import estimate

ROOT=Path(__file__).resolve().parents[1]/"preview"
BASE=ROOT/"players-2020-nine-class-mockfix-v11.json"
NINE=ROOT/"players-2020-nine-class-scoutfix-v12.json"
SEVEN=ROOT/"players-2020-seven-class-scoutfix-v12.json"
REPORT=ROOT/"v12-scouting-coverage-audit.json"

def read(path):
 data=json.loads(path.read_text())
 assert data["schemaVersion"]==3 and data["meta"]["baseSeason"]==2020
 assert data["deadCap"]==[]
 return data["players"]

def main():
 v11=read(BASE)
 new=read(NINE)
 seven=read(SEVEN)
 report=json.loads(REPORT.read_text())
 assert report["status"]=="EXPERIMENTAL_V12_CHECKS_ONLY_CAPFORGE_IMPORT_UNVERIFIED"
 assert len(v11)==len(new)==6613
 assert len(seven)==5653
 original_ids={p["iden"]:p for p in v11}
 output_ids={p["iden"]:p for p in new}
 assert len(original_ids)==6613 and len(output_ids)==6613
 history=[p for p in v11 if p["pool"]=="roster" or
         (p["pool"]=="draftClass" and p["bio"]["draftSeason"]<=2026)]
 assert len(history)==5173
 assert all(output_ids.get(p["iden"])==p for p in history), "V11 historic record changed"
 assert all(p["bio"]["weightLbs"]<=400 and p["bio"]["weightLbs"]>=140 for p in new)
 years=Counter(p["bio"]["draftSeason"] for p in new if p["pool"]=="draftClass")
 assert all(years[y]==480 for y in range(2021,2030))
 seven_years=Counter(p["bio"]["draftSeason"] for p in seven if p["pool"]=="draftClass")
 assert all(seven_years[y]==480 for y in range(2021,2028))
 assert set(seven_years)==set(range(2021,2028))
 assert len({p["iden"] for p in seven})==len(seven)
 assert all(output_ids[p["iden"]]==p for p in seven)
 protected=set()
 for yr,ranked in PRIORITY.items():
  for name,pos,school in ranked:
   matches=[p for p in new if p["pool"]=="draftClass"
            and p["bio"]["draftSeason"]==yr
            and key(p["forename"]+" "+p["surname"])==key(name)]
   assert len(matches)==1, "Missing contemporary published prospect: "+name
   assert matches[0]["position"]==pos, "Incorrect projected position: "+name
   assert not matches[0].get("teamAbbr") and not matches[0].get("teamId")
   protected.add((yr,key(name)))
 for name,yr in [
     ("Charlie Becker",2027),("Drew Mestemaker",2027),
     ("Darian Mensah",2027),("CJ Carr",2027),
     ("Bryce Underwood",2028),("Keisean Henderson",2029)]:
  assert (yr,key(name)) in protected, f"Missing crucial {yr} prospect: {name}"
 allfuture=Counter(key(p["forename"]+" "+p["surname"]) for p in new
         if p["pool"]=="draftClass" and p["bio"]["draftSeason"]>=2027)
 assert all(v==1 for v in allfuture.values()), "Same prospect assigned to multiple future years"
 # The three QB portrait choices already curated in V11 must survive without
 # being replaced with an unverified new portrait mapping.
 for name in ("Arch Manning","Drew Mestemaker","CJ Carr"):
  matching=[p for p in new if p["pool"]=="draftClass"
            and p["bio"]["draftSeason"]==2027
            and key(p["forename"]+" "+p["surname"])==key(name)]
  assert len(matching)==1 and matching[0]["bio"].get("portraitId"),name
  originals=[p for p in v11 if key(p["forename"]+" "+p["surname"])==key(name)]
  assert len(originals)==1
  assert matching[0]["bio"]["portraitId"]==originals[0]["bio"]["portraitId"],name
 dylan=[p for p in new if p["pool"]=="draftClass"
        and p["bio"]["draftSeason"]==2027 and
        key(p["forename"]+" "+p["surname"])==key("Dylan Stewart")]
 assert len(dylan)==1 and dylan[0]["position"]=="EDGE"
 assert dylan[0]["development"]["ovr"]<=77
 assert report["historical_records_protected"]==5173
 for p in new:
  if p["iden"] not in original_ids and p["pool"]=="draftClass":
   assert 2027<=p["bio"]["draftSeason"]<=2029
   assert p["bio"]["college"]!="Fictional Depth Pool"
   assert abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])<=2
 print(json.dumps({
  "status":"V12_AUTOMATED_CHECKS_PASSED_NOT_YET_TESTED_IN_CAPFORGE",
  "preserved_V11_historical_records":len(history),
  "2027_consensus_players":len(PRIORITY[2027]),
  "2028_early_board_players":len(PRIORITY[2028]),
  "2029_freshman_watchlist":len(PRIORITY[2029]),
  "year_counts":{str(y):years[y] for y in range(2021,2030)},
  "nine_class_total":len(new),"seven_class_total":len(seven),
  "prior_V11_QB_portraits_preserved":3
 },indent=2))
if __name__=="__main__":
 main()
