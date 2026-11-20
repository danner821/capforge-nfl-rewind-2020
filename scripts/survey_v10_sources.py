"""Print non-sensitive college roster schema and cohort distribution for 2027-29 design."""
import csv, io, urllib.request, collections
URL="https://raw.githubusercontent.com/sportsdataverse/cfbfastR-data/main/rosters/csv/cfb_rosters_{}.csv"
def load(y):
 req=urllib.request.Request(URL.format(y),headers={"User-Agent":"Capforge-V10-Research/1.0"})
 with urllib.request.urlopen(req,timeout=80) as f: data=f.read().decode("utf-8-sig")
 return list(csv.DictReader(io.StringIO(data)))
sets={}
for y in (2023,2024,2025,2026):
 rows=load(y)
 print("SEASON",y,"ROWS",len(rows),"COLUMNS",list(rows[0].keys()),"SAMPLE",[{k:r.get(k) for k in list(rows[0])[:10]} for r in rows[:2]])
 keys=[k for k in rows[0] if any(term in k.lower() for term in ("class","year","position","experience","grade","team","name","athlete"))]
 print("SELECTED FIELDS",keys)
 for k in keys:
  if any(term in k.lower() for term in ("class","position","year","experience")):
   print("COUNT",k,collections.Counter(str(r.get(k)) for r in rows).most_common(9))
 key_col="athlete_id" if "athlete_id" in rows[0] else "id"
 sets[y]={str(r.get(key_col)) for r in rows if r.get(key_col)}
for y in (2023,2024,2025):
 print("OVERLAP",y,"2026",len(sets[y]&sets[2026]))
print("FIRST SEEN 2026",len(sets[2026]-sets[2025]-sets[2024]-sets[2023]))
