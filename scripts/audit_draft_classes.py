#!/usr/bin/env python3
"""Audits historical NFL draft-pick coverage without exposing player potentials.

Compare independent public 2017-2026 NFL draft results with CapForge prospects.
No drafted prospect is assigned to their historical NFL team: game determines that.
This script is a provenance audit, not a complete list of 480 eligible prospects.
"""
import csv, io, json, re, sys, unicodedata, urllib.request
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE_URL="https://raw.githubusercontent.com/7LayerLabs/nfldraft/main/nfl-drafts-2017-2026.csv"
SOURCE_PAGE="https://github.com/7LayerLabs/nfldraft/blob/main/nfl-drafts-2017-2026.csv"
PACK=ROOT/"preview/players-2020-six-class-draftfix-v7.json"
REPORT=ROOT/"preview/draft-coverage-report.json"

def norm(value):
    s=unicodedata.normalize("NFKD",str(value).lower())
    s="".join(c for c in s if not unicodedata.combining(c))
    s=s.replace("\u2019","").replace("'","")
    s=re.sub(r"([a-z])\.\s*",r"\1",s)
    s=re.sub(r"\b(jr|sr|ii|iii|iv)\b","",s)
    return re.sub(r"[^a-z0-9]","",s)
# Historical roster nickname/expanded-name differences. Not rating overrides.
ALIASES={
  "joetryonshoyinka":"joetryon",
  "boogiebasham":"carlosbasham",
  "jujubrents":"juliusbrents",
  "quanmartin":"jartaviusmartin",
  "olufashanu":"olumuyiwafashanu",
  "cobiedurant":"decobiedurant",
  "chigokonkwo":"chigoziemokonkwo",
  "riqwoolen":"tariqwoolen",
  "drewogletree":"andrewogletree",
  "oluoluwatimi":"olusegunoluwatimi",
  "natethomas":"nathanthomas",
  "nicholassingleton":"nicksingleton",
  "gabrielrubio":"gaberubio",

}
def get_source():
    request=urllib.request.Request(SOURCE_URL,headers={"User-Agent":"CapForge-Historical-Draft-Audit/1.0"})
    with urllib.request.urlopen(request,timeout=80) as response:
        decoded=response.read().decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(decoded)))

def main():
    if not PACK.exists():raise SystemExit("Expected six-class preview is missing")
    data=json.loads(PACK.read_text())
    assert data["schemaVersion"]==3 and data["meta"]["baseSeason"]==2020
    by_year=defaultdict(set)
    for p in data["players"]:
        if p["pool"]!="draftClass":continue
        year=p["bio"]["draftSeason"]
        if year in range(2021,2027):
            by_year[year].add(norm(p["forename"]+" "+p["surname"]))
    picks=get_source()
    stats={}
    for year in range(2021,2027):
        year_picks=[r for r in picks if int(r["Year"])==year]
        if len(year_picks)<250:raise ValueError(f"Draft source missing expected year {year}")
        unmatched=[]
        for row in year_picks:
            name=norm(row["Selection"])
            name=ALIASES.get(name,name)
            if name not in by_year[year]:
                unmatched.append(row)
        early=[r for r in unmatched if int(r["Round"])<=3]
        stats[str(year)]={
            "actual_nfl_draft_picks":len(year_picks),
            "capforge_draft_prospects":len(by_year[year]),
            "drafted_players_found":len(year_picks)-len(unmatched),
            "drafted_players_not_found":len(unmatched),
            "round_1_to_3_missing":len(early),
        }
    summary={
        "source":SOURCE_PAGE,
        "import_file":str(PACK.relative_to(ROOT)),
        "scope":"2021-2026 real NFL draft selections only; not a count of all eligible college prospects",
        "by_year":stats,
        "verified":"All actual NFL draft selections in rounds 1-3 are present" if all(v["round_1_to_3_missing"]==0 for v in stats.values()) else "Some rounds 1-3 players missing",
        "future_development":"No individual player potentials, progression curves or hindsight rankings revealed",
        "next_step":"Research unresolved rounds 4-7 players and add where reliable Madden attributes exist"
    }
    REPORT.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
    if any(v["round_1_to_3_missing"] for v in stats.values()):
        raise SystemExit("Historical rounds 1-3 are incomplete: see coverage report")
if __name__=="__main__":main()
