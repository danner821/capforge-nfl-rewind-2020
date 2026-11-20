#!/usr/bin/env python3
"""V11 protected-data, mock-consensus and importer regression validation.

No hidden OVR growth or potential figures printed or exported.
"""
import json
from collections import Counter
from pathlib import Path
from audit_draft_classes import norm
from repair_v11_future import PRIORITY, key
from capforge_ovr import estimate

ROOT=Path(__file__).resolve().parents[1]/"preview"
BASE=ROOT/"players-2020-nine-class-projection-v10.json"
NINE=ROOT/"players-2020-nine-class-scoutfix-v11.json"
SEVEN=ROOT/"players-2020-seven-class-scoutfix-v11.json"
REPORT=ROOT/"v11-scouting-portrait-audit.json"
def load(path):
 d=json.loads(path.read_text())
 assert d["schemaVersion"]==3 and d["meta"]["baseSeason"]==2020
 assert d["deadCap"]==[]
 return d["players"]
def main():
 old=load(BASE);new=load(NINE);seven=load(SEVEN)
 r=json.loads(REPORT.read_text())
 assert r["status"]=="EXPERIMENTAL_V11_CHECKS_ONLY_CAPFORGE_IMPORT_UNVERIFIED"
 assert len(old)==len(new)==6613 and len(seven)==5653
 orig={p["iden"]:p for p in old}
 now={p["iden"]:p for p in new}
 assert len(orig)==6613 and len(now)==6613
 early=[p for p in old if p["pool"]=="roster" or
        (p["pool"]=="draftClass" and p["bio"]["draftSeason"]<=2026)]
 assert len(early)==5173
 altered=[]
 for p in early:
  newp=now.get(p["iden"])
  assert newp is not None, "Historical player missing"
  if newp!=p:
   altered.append(p["forename"]+" "+p["surname"])
   assert p["forename"]=="Desmond" and p["surname"]=="Watson"
   a=json.loads(json.dumps(p))
   a["bio"]["weightLbs"]=400
   assert newp==a, "Unexpected historical player mutation"
 assert altered==["Desmond Watson"], "Historical V9 data must remain frozen"
 assert all(140<=p["bio"]["weightLbs"]<=400 for p in new)
 years=Counter(p["bio"]["draftSeason"] for p in new if p["pool"]=="draftClass")
 assert all(years[y]==480 for y in range(2021,2030))
 assert Counter(p["bio"]["draftSeason"] for p in seven if p["pool"]=="draftClass")==dict.fromkeys(range(2021,2028),480)
 assert len({p["iden"] for p in seven})==len(seven)
 assert all(now[p["iden"]]==p for p in seven)
 protected=set()
 for yr,ranked in PRIORITY.items():
  for name,position,college in ranked:
   matches=[p for p in new if p["pool"]=="draftClass"
            and p["bio"]["draftSeason"]==yr and key(p["forename"]+" "+p["surname"])==key(name)]
   assert len(matches)==1, "Unrepresented high-profile prospect: "+name
   assert matches[0]["position"]==position, "Incorrect prospect position: "+name
   assert not matches[0].get("teamAbbr") and not matches[0].get("teamId")
   protected.add((yr,key(name)))
 for name,y in [("Charlie Becker",2027),("Drew Mestemaker",2027),("Darian Mensah",2027),
                ("CJ Carr",2027),("Bryce Underwood",2028),("Keisean Henderson",2029)]:
  assert (y,key(name)) in protected
 allfuture=Counter(key(p["forename"]+" "+p["surname"]) for p in new
       if p["pool"]=="draftClass" and p["bio"]["draftSeason"]>=2027)
 assert all(x==1 for x in allfuture.values()),"Duplicated projected prospect across draft years"
 arch=[p for p in new if key(p["forename"]+" "+p["surname"])==key("Arch Manning") and p["bio"]["draftSeason"]==2027]
 zach=[p for p in new if key(p["forename"]+" "+p["surname"])==key("Zach Wilson") and p["bio"]["draftSeason"]==2021]
 assert len(arch)==len(zach)==1
 assert arch[0]["bio"]["portraitId"]==zach[0]["bio"]["portraitId"]
 dylan=[p for p in new if key(p["forename"]+" "+p["surname"])==key("Dylan Stewart") and p["bio"]["draftSeason"]==2027]
 assert len(dylan)==1 and dylan[0]["development"]["ovr"]<=77
 assert len(r["known_import_fixes"])==2
 assert all(p["position"] for p in new)
 added=[p for p in new if p["iden"] not in orig]
 for p in added:
  assert p["pool"]=="draftClass" and 2027<=p["bio"]["draftSeason"]<=2029
  assert p["bio"]["college"] and p["bio"]["college"]!="Fictional Depth Pool"
  assert abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])<=2, "New player calibration mismatch"
 print(json.dumps({
   "status":"V11_STRUCTURE_ACCEPTED_GAME_TEST_PENDING",
   "historical_players_preserved_except_known_weight_cap":5172,
   "2024_weight_cap_corrections":1,
   "portrait_corrections":1,
   "three_year_priority_coverage":{str(yr):len(items) for yr,items in PRIORITY.items()},
   "nine_years_of_480":True,
   "player_count":len(new),
   "draft_class_retention_in_game":"NOT_YET_TESTED"
 },indent=2))
if __name__=="__main__":main()
