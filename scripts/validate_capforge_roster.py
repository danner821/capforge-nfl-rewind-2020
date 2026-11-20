#!/usr/bin/env python3
"""Validate CapForge JSON structure without exposing hidden potential."""
import collections,json,re,sys
from pathlib import Path
def audit(path):
 d=json.loads(Path(path).read_text())
 assert d["schemaVersion"]==3
 assert d["meta"]["baseSeason"]==2020
 players=d["players"]
 ids=[p["iden"] for p in players]
 assert len(ids)==len(set(ids)), "duplicate UUIDs"
 grouped=collections.Counter(p["pool"] for p in players)
 teams={p["teamAbbr"] for p in players if p["pool"]=="roster"}
 assert len(teams)==32
 # Import parsing alone does not ensure the game can construct a legal
 # lineup. Verify all fifteen CapForge position groups on every team.
 by_team=collections.defaultdict(collections.Counter)
 for p in players:
  if p["pool"]=="roster":
   by_team[p["teamAbbr"]][p["position"]]+=1
 required=("QB","RB","WR","TE","OT","OG","C","DE","DT","EDGE","LB","CB","S","K","P")
 for team,counts in by_team.items():
  absent=[position for position in required if counts[position]==0]
  assert not absent, f"{team} missing required positions: {absent}"
  assert counts["DE"]>=2 and counts["EDGE"]>=3 and counts["DT"]>=2, f"{team} has insufficient defensive personnel"
 years=collections.Counter()
 for p in players:
  assert p["position"] and p["forename"] and p["surname"]
  assert isinstance(p["ratings"],dict) and isinstance(p["development"],dict)
  assert isinstance(p["contract"],dict)
  portrait=p["bio"].get("portraitId")
  if portrait is not None:
   assert re.fullmatch(r"portrait-\d{4}",portrait), f"Malformed portrait ID: {portrait}"
  if p["pool"]=="draftClass":
   y=p["bio"]["draftSeason"]
   assert y>2020
   years[y]+=1
 summary={"file":str(path),"players":len(players),"teams":len(teams),
          "poolCounts":dict(grouped),"draftClassCounts":dict(sorted(years.items())),
          "validated":"format-only, NOT tested inside CapForge"}
 print(json.dumps(summary))
if __name__=="__main__":
 for arg in sys.argv[1:]:audit(arg)
