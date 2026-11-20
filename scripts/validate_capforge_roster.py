#!/usr/bin/env python3
"""Validate CapForge JSON structure without exposing hidden potential."""
import collections,json,sys
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
 years=collections.Counter()
 for p in players:
  assert p["position"] and p["forename"] and p["surname"]
  assert isinstance(p["ratings"],dict) and isinstance(p["development"],dict)
  assert isinstance(p["contract"],dict)
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
