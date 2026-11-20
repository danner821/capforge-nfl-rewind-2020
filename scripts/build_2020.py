#!/usr/bin/env python3
"""CapForge NFL Rewind 2020: historical roster + experimental draft class builder.
Fan-made research preview, NOT a verified in-game import.
Never print hidden per-player potential / retrospectively ranked players.
"""
from __future__ import annotations
import csv,hashlib,io,json,math,re,urllib.request,uuid
from collections import Counter,defaultdict
from pathlib import Path
from capforge_ovr import calibrate, estimate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"preview";OUT.mkdir(exist_ok=True)
SOURCES={
 "teams":"https://raw.githubusercontent.com/jmansfield96/capforge-custom-rosters/main/teams-files/2018-teams.json",
 "madden":"https://raw.githubusercontent.com/theedgepredictor/nfl-madden-data/main/data/madden/raw/{}.csv",
 "madden26":"https://raw.githubusercontent.com/thompgt/madden-analysis/master/data/processed/madden_clean.csv",
 "madden27":"https://raw.githubusercontent.com/jmansfield96/capforge-custom-rosters/main/player-files/madden-27-players.json"
}
def get(url):
 req=urllib.request.Request(url,headers={"User-Agent":"CapForge-NFL-Rewind-2020/preview"})
 with urllib.request.urlopen(req,timeout=120) as r:return r.read().decode("utf-8-sig")
def rows(url):
 content=get(url)
 data=list(csv.DictReader(io.StringIO(content)))
 if len(data)<100:raise ValueError("Missing/empty Madden data from "+url)
 return data
def k(s):return re.sub("[^a-z0-9]","",str(s).lower())
def field(row,*aliases,default=""):
 for a in aliases:
  for name,value in row.items():
   if k(name)==k(a) and value not in ("",None):return str(value).strip()
 return default
def num(row,*aliases,default=50):
 try:return float(field(row,*aliases,default=str(default)).replace("$","").replace(",",""))
 except ValueError:return float(default)
def cut(n,lower=0,upper=99):return max(lower,min(upper,int(round(float(n)))))
def normal(s):
 s=re.sub(r"[^a-z0-9 ]","",s.lower());return re.sub(r"\b(jr|sr|ii|iii|iv)\b","",s).strip().replace("  "," ")
def fullname(r):
 name=field(r,"Full Name","name")
 if name:return name
 return (field(r,"First Name","firstName")+" "+field(r,"Last Name","lastName")).strip()
def position(p):
 p=k(p)
 return {
 "hb":"RB","halfback":"RB","fb":"RB","fullback":"RB","runningback":"RB",
 "lt":"OT","rt":"OT","lefttackle":"OT","righttackle":"OT",
 "lg":"OG","rg":"OG","leftguard":"OG","rightguard":"OG",
 "le":"EDGE","re":"EDGE","rightedge":"EDGE","leftedge":"EDGE",
 "mlb":"LB","lolb":"LB","rolb":"LB","middlelinebacker":"LB","leftoutsidelinebacker":"LB","rightoutsidelinebacker":"LB",
 "fs":"S","ss":"S","freesafety":"S","strongsafety":"S",
 "quarterback":"QB","widereceiver":"WR","tightend":"TE","center":"C",
 "defensivetackle":"DT","linebacker":"LB","cornerback":"CB",
 "kicker":"K","punter":"P"
 }.get(p,p.upper())
SUPPORTED={"QB","RB","WR","TE","OT","OG","C","EDGE","DE","DT","LB","CB","S","K","P"}
def stats(row,pos):
 def v(*args,d=50):return cut(num(row,*args,default=d))
 r={"speed":v("Speed","stats/speed/value"),"agility":v("Agility","stats/agility/value"),
    "acceleration":v("Acceleration","stats/acceleration/value"),
    "strength":v("Strength","stats/strength/value"),"jumping":v("Jumping","stats/jumping/value"),
    "stamina":v("Stamina","stats/stamina/value"),"awareness":v("Awareness","stats/awareness/value"),
    "discipline":cut(45+v("Awareness","stats/awareness/value")*.17),
    "vision":v("Ball Carrier Vision","BC Vision","stats/bCVision/value","Awareness"),
    "decisions":v("Awareness","stats/awareness/value"),"toughness":v("Toughness","stats/toughness/value"),
    "injuryProne":cut(100-v("Injury","stats/injury/value",d=85))}
 if pos=="QB":
  r.update(sPassAcc=v("Throw Accuracy Short","Throw Acc Short","stats/throwAccuracyShort/value"),
    mPassAcc=v("Throw Accuracy Mid","Throw Accuracy Middle","Throw Acc Mid","stats/throwAccuracyMid/value"),
    dPassAcc=v("Throw Accuracy Deep","Throw Acc Deep","stats/throwAccuracyDeep/value"),
    throwPower=v("Throw Power","stats/throwPower/value"),throwOnRun=v("Throw On The Run","stats/throwOnTheRun/value"),
    pocketPresence=v("Throw Under Pressure","stats/throwUnderPressure/value"),
    elusiveness=v("Break Sack","stats/breakSack/value"),ballSecurity=v("Carrying","stats/carrying/value"),
    trucking=v("Trucking","stats/trucking/value"),changeOfDirection=v("Change Of Direction","Change of Dir","stats/changeOfDirection/value"),
    runBlock=v("Run Blocking","Run Block","stats/runBlock/value"))
 elif pos in ("RB","WR","TE"):
  r.update(ballSecurity=v("Carrying","stats/carrying/value"),elusiveness=v("Juke Move","stats/jukeMove/value"),
    trucking=v("Trucking","stats/trucking/value"),changeOfDirection=v("Change Of Direction","Change of Dir","stats/changeOfDirection/value"),
    runBlock=v("Run Blocking","Run Block","stats/runBlock/value"),
    catching=v("Catching","stats/catching/value"),
    routeRun=cut(sum(v(x,y) for x,y in [
       ("Short Route Running","stats/shortRouteRunning/value"),("Medium Route Running","stats/mediumRouteRunning/value"),
       ("Deep Route Running","stats/deepRouteRunning/value")])/3),
    pressRelease=v("Release","stats/release/value"),passBlock=v("Pass Blocking","Pass Block","stats/passBlock/value"),
    returnSkill=v("Kick Return","stats/kickReturn/value"),catchTraffic=v("Catch In Traffic","stats/catchInTraffic/value"),
    impactBlock=v("Impact Blocking","stats/impactBlocking/value"))
 elif pos in ("OT","OG","C"):
  r.update(runBlock=v("Run Blocking","Run Block","stats/runBlock/value"),
    passBlock=v("Pass Blocking","Pass Block","stats/passBlock/value"),
    impactBlock=v("Impact Blocking","stats/impactBlocking/value"),
    playRecognition=v("Play Recognition","stats/playRecognition/value"))
 elif pos in ("CB","S","LB","EDGE","DE","DT"):
  r.update(playRecognition=v("Play Recognition","stats/playRecognition/value"),
    blockShedding=v("Block Shedding","stats/blockShedding/value"),tackle=v("Tackle","stats/tackle/value"),
    hitPower=v("Hit Power","stats/hitPower/value"),pursuit=v("Pursuit","stats/pursuit/value"),
    manCover=v("Man Coverage","stats/manCoverage/value"),
    zoneCover=v("Zone Coverage","stats/zoneCoverage/value"),press=v("Press","stats/press/value"))
 elif pos in ("K","P"):
  r.update(kickAccuracy=v("Kick Accuracy","stats/kickAccuracy/value"),
           legPower=v("Kick Power","stats/kickPower/value"))
  if pos=="P":r["puntPlacement"]=cut((r["awareness"]+r["kickAccuracy"])/2)
 if pos in ("EDGE","DE","DT","LB","CB","S","OT","OG","C"):
  # Vision is positional recognition for linemen/defenders, not Madden ball-carrier vision.
  r["vision"]=v("Awareness","stats/awareness/value")
 if pos in ("CB","S"):
  # CapForge includes defensive-back receiving/return traits in its OVR model.
  r.update(catching=v("Catching","stats/catching/value"),
    returnSkill=v("Kick Return","stats/kickReturn/value"),
    elusiveness=v("Juke Move","stats/jukeMove/value"),
    ballSecurity=v("Carrying","stats/carrying/value"),
    changeOfDirection=v("Change Of Direction","stats/changeOfDirection/value"))
 return r
def player_bio(r,year,group):
 age=cut(num(r,"Age","age",default=23),18,50)
 yrs=int(num(r,"Years Pro","years_pro","yearsPro",default=0))
 original=field(r,"Position","position")
 name=fullname(r);college=field(r,"College","college")
 digest=hashlib.sha256(f"{normal(name)}|{year}|{college}|{original}".encode()).digest()
 return {"age":age,"jerseyNumber":0 if group=="draftClass" else cut(num(r,"Jersey Number","Jersey #","jerseyNum","number",default=0)),
  "college":college,"portraitId":f"portrait-{int.from_bytes(digest[:2],'big')%800+1:04d}",
  "draftSeason":year if group=="draftClass" else year-max(0,yrs),
  "draftNum":-1,"heightInches":cut(num(r,"Height","height",default=73),60,87),
  "weightLbs":cut(num(r,"Weight","weight",default=225),135,425)}
def development(start,age,peak):
 ceiling=cut(max(start,peak)+(2 if age<27 else 0),start,99)
 gap=max(0,ceiling-start)
 curve=[]
 for i in range(31):
  a=age+i
  if a<=26:delta=round(min(450,35+17*gap)) if gap else 0
  elif a<=29:delta=round(min(200,20+7*gap)) if gap else 0
  elif a<=31:delta=0
  else:delta=-round(55+(a-32)*10)
  curve.append(delta)
 return {"ovr":start,"potential":ceiling,"progressionCurve":curve}
def contract(r,ovr,group):
 if group=="draftClass":return {"salary":0,"guarantee":0,"years":0,"extension":{"salary":0,"guarantee":0,"years":0}}
 # PREVIEW ONLY: Madden Total Salary is total contract, NOT a verified NFL cap hit.
 amount=max(0,num(r,"Total Salary",default=0))
 yrs=max(1,min(5,math.ceil(amount/max(1500000,ovr*150000))))
 annual=max(850000,round(amount/max(1,yrs)*1.5/1000)*1000)
 guaranteed=round(annual*.25)
 return {"salary":annual,"guarantee":guaranteed,"years":yrs,
  "signedSeason":2020,"salaryByYear":[annual]*yrs,"bonusByYear":[0]*yrs,
  "guaranteeByYear":[guaranteed]+[0]*(yrs-1),"currentGuarantee":guaranteed,
  "currentYearIndex":0,"extension":{"salary":0,"guarantee":0,"years":0}}
def build_player(r,year,group,teams,peaks):
 name=fullname(r);original=field(r,"Position","position")
 if " " not in name:return None
 p=position(original)
 if p not in SUPPORTED:return None
 source_ovr=cut(num(r,"Overall Rating","Overall","Rating","stats/overall/value",default=62),20,99)
 # Rookie readiness uplift is uniform by rating bracket, never hindsight-specific.
 uplift=(3 if source_ovr<=68 else 2 if source_ovr<=78 else 1) if group=="draftClass" else 0
 ovr=cut(source_ovr+uplift,20,99)
 age=cut(num(r,"Age","age",default=23),18,50)
 bio=player_bio(r,year,group)
 # Let CapForge pick a valid portrait by stable player id.
 # Randomly assigned portrait IDs trigger a warning for nearly every player.
 bio.pop("portraitId",None)
 rating_values,calibrated_ovr,_,_=calibrate(p,stats(r,p),ovr)
 ovr=calibrated_ovr
 first,last=name.split(" ",1)
 seed=f"{normal(name)}|{year}|{p}|{bio['college']}"
 h=hashlib.sha256(seed.encode()).digest()
 entry={
  "iden":str(uuid.uuid5(uuid.NAMESPACE_URL,"capforge-nfl-rewind-2020:"+seed)).upper(),
  "forename":first,"surname":last,"position":p,"pool":group,
  "bio":bio,"personality":{"loyalty":30+h[0]%65,"greed":25+h[1]%70,"ambition":30+h[2]%65,
     "personality":25+h[3]%70,"workEthic":30+h[4]%65},
  "ratings":rating_values,
  "development":development(ovr,age,peaks.get(normal(name),ovr)),
  "contract":contract(r,ovr,group)
 }
 if group=="roster":
  t=teams.get(field(r,"Team","team").lower())
  if not t:raise RuntimeError("Unmapped 2020 team "+field(r,"Team")+" for "+name)
  entry.update(teamAbbr=t["abbr"],teamId=t["teamId"])
 return entry
def main():
 rawteams=json.loads(get(SOURCES["teams"]))
 assert rawteams["schemaVersion"]==3
 for t in rawteams["teams"]:
  a=t["abbr"]
  if a=="OAK":t.update(abbr="LV",city="Las Vegas",name="Raiders",stadium="Allegiant Stadium",roof="fixed",logo="assets/logos/fictional/lv.png")
  elif a=="WAS":t.update(city="Washington",name="Football Team",stadium="FedExField")
  elif a in ("LAR","LAC"):t.update(stadium="SoFi Stadium",roof="fixed")
  elif a=="BUF":t["stadium"]="Bills Stadium"
 rawteams["note"]="EXPERIMENTAL 2020 NFL teams (2018 source updated); not final historical audit."
 (OUT/"teams-2020.json").write_text(json.dumps(rawteams,indent=2)+"\n")
 tm={t["name"].lower():t for t in rawteams["teams"]}
 tm["redskins"]=next(t for t in rawteams["teams"] if t["abbr"]=="WAS")
 all_madden={y:rows(SOURCES["madden"].format(y)) for y in range(2020,2025)}
 all_madden[2025]=rows(SOURCES["madden26"])
 src26=json.loads(get(SOURCES["madden27"]))
 if isinstance(src26,dict):src26=src26.get("players",[])
 assert isinstance(src26,list) and len(src26)>1000,"Missing 2026 Madden source"
 peaks={}
 for records in all_madden.values():
  for p in records:
   nm=normal(fullname(p))
   if nm:peaks[nm]=max(peaks.get(nm,0),cut(num(p,"Overall Rating","Overall","Rating","stats/overall/value",default=50),20,99))
 for p in src26:
  nm=normal(p.get("forename","")+" "+p.get("surname",""))
  if nm:peaks[nm]=max(peaks.get(nm,0),int(p.get("development",{}).get("ovr",0)))
 starters=[]
 for r in all_madden[2020]:
  p=build_player(r,2020,"roster",tm,peaks)
  if p:starters.append(p)
 # Scale estimated Madden salaries so preview clubs don't trivially exceed a $300M model cap.
 byteam=defaultdict(list)
 for p in starters:byteam[p["teamAbbr"]].append(p)
 for team,people in byteam.items():
  total=sum(p["contract"]["salary"] for p in people)
  if total>285000000:
   scale=285000000/total
   for p in people:
    c=p["contract"];c["salary"]=round(c["salary"]*scale)
    c["guarantee"]=round(c["guarantee"]*scale)
    c["salaryByYear"]=[round(v*scale) for v in c["salaryByYear"]]
    c["guaranteeByYear"]=[round(v*scale) for v in c["guaranteeByYear"]]
    c["currentGuarantee"]=round(c["currentGuarantee"]*scale)
 draft=[]
 for year in range(2021,2026):
  for r in all_madden[year]:
   if int(num(r,"Years Pro","years_pro","yearsPro",default=-1))!=0:continue
   p=build_player(r,year,"draftClass",tm,peaks)
   if p:draft.append(p)
 for original in src26:
  if original.get("bio",{}).get("draftSeason")!=2026:continue
  p=json.loads(json.dumps(original))
  p.pop("teamAbbr",None);p.pop("teamId",None)
  p["pool"]="draftClass"
  seed=normal(p.get("forename","")+" "+p.get("surname",""))+"|2026|"+p.get("position","")
  p["iden"]=str(uuid.uuid5(uuid.NAMESPACE_URL,"capforge-nfl-rewind-2020:"+seed)).upper()
  p["bio"]["draftSeason"]=2026
  p["bio"]["draftNum"]=-1
  p["bio"]["jerseyNumber"]=0
  p["bio"].pop("portraitId",None)
  p["ratings"],p["development"]["ovr"],_,_=calibrate(p["position"],p["ratings"],p["development"]["ovr"])
  p["development"]["potential"]=max(p["development"]["ovr"],p["development"]["potential"])
  p["contract"]={"salary":0,"guarantee":0,"years":0,"extension":{"salary":0,"guarantee":0,"years":0}}
  draft.append(p)
 # Prevent duplicate IDs and duplicate people within a class.
 found=set();unique=[];dupes=0
 for p in starters+draft:
  idkey=(p["pool"],p["bio"]["draftSeason"] if p["pool"]=="draftClass" else p["teamAbbr"],normal(p["forename"]+" "+p["surname"]))
  if idkey in found:dupes+=1;continue
  found.add(idkey);unique.append(p)
 starters=[p for p in unique if p["pool"]=="roster"]
 draft=[p for p in unique if p["pool"]=="draftClass"]
 assert len(set(p["iden"] for p in unique))==len(unique),"Duplicate player IDs"
 assert len({p["teamAbbr"] for p in starters})==32
 assert len(starters)>=2000
 cc=Counter(p["bio"]["draftSeason"] for p in draft)
 # Structural validation cannot guarantee in-game parity, but catch gross mismatches.
 misaligned=[p for p in unique if p["position"] in ("QB","RB","WR","TE","OT","OG","C","EDGE","DE","DT","LB","CB","S","K","P")
             and abs(estimate(p["position"],p["ratings"])-p["development"]["ovr"])>2]
 assert not misaligned,f"Ratings/OVR mismatch: {len(misaligned)}"
 results={}
 for label,end in (("three-class",2023),("four-class-test",2024),("extended-experimental",2026)):
  out=starters+[p for p in draft if p["bio"]["draftSeason"]<=end]
  payload={"schemaVersion":3,"meta":{"baseSeason":2020},"players":out,"deadCap":[]}
  path=OUT/("players-2020-"+label+".json")
  path.write_text(json.dumps(payload,separators=(",",":"))+"\n")
  assert len(json.loads(path.read_text())["players"])==len(out)
  results[label]={"players":len(out),"bytes":path.stat().st_size}
 report={"status":"PREVIEW_NOT_GAME_VALIDATED","baseSeason":2020,"rosteredPlayers":len(starters),
  "teams":32,"draftClassSizes":dict(sorted(cc.items())),"duplicateNameRowsRemoved":dupes,"exports":results,
  "warnings":["Madden 21 launch teams; not independently verified Week 1","2020 contracts are provisional",
  "2025 Madden 26 roster may be a later snapshot, not confirmed launch",
  "2026 rookies from fan-made Madden 27 conversion; not verified as complete",
  "Real draft pick order, staff and full 480-player classes not yet implemented",
  "Fourth and later imported classes must be tested in-game",
  "No individual potential figures included in this report",
  "CapForge OVR prediction is calibrated from a separate game export and must be tested in-app"],
  "ovrQualityCheck":{"players_with_estimated_ovr_gap_over_2":len(misaligned)},
  "portraitQualityCheck":{"explicit_portrait_ids":sum("portraitId" in p["bio"] for p in unique)}}
 (OUT/"build-report.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report,indent=2))
if __name__=="__main__":main()
