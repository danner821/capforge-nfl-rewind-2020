"""Position-specific CapForge OVR calibration.

Coefficients estimated from the user's prior CapForge export (no player data
is bundled). This is an approximate model, not CapForge's published formula.
Keep player potential hidden: only displayed OVR is calibrated.
"""
import json
from pathlib import Path
MODEL=json.loads((Path(__file__).with_name("ovr_calibration_coefficients.json")).read_text())
FLEX={
 "QB":{"strength":2,"vision":2,"decisions":2,"awareness":1.8,"ballSecurity":2,"sPassAcc":.9,"mPassAcc":.9,"dPassAcc":.9,"speed":.6},
 "RB":{"passBlock":3,"strength":1.4,"awareness":1.4,"decisions":1.5,"vision":1.5,"acceleration":.7,"speed":.7},
 "WR":{"strength":1.8,"awareness":1.5,"vision":1.7,"decisions":1.7,"ballSecurity":2,"catching":.7,"speed":.65,"acceleration":.65},
 "TE":{"passBlock":3.5,"runBlock":1.8,"strength":1.5,"vision":1.8,"decisions":1.6,"catching":.8},
 "OT":{"strength":1.5,"vision":1.8,"decisions":1.7,"awareness":1.5,"passBlock":.85,"runBlock":.85},
 "OG":{"strength":1.5,"vision":1.8,"decisions":1.7,"awareness":1.5,"passBlock":.85,"runBlock":.85},
 "C":{"strength":1.5,"vision":1.8,"decisions":1.7,"awareness":1.5,"passBlock":.85,"runBlock":.85},
 "EDGE":{"strength":1.7,"blockShedding":1.3,"vision":2,"awareness":1.5,"decisions":1.7,"speed":.75},
 "DE":{"strength":1.7,"blockShedding":1.3,"vision":2,"awareness":1.5,"decisions":1.7,"speed":.75},
 "DT":{"strength":1.7,"blockShedding":1.3,"vision":2,"awareness":1.5,"decisions":1.7,"speed":.75},
 "LB":{"strength":1.8,"blockShedding":2,"tackle":1.2,"vision":1.8,"awareness":1.4,"decisions":1.5,"speed":.75},
 "CB":{"strength":2,"tackle":3,"vision":2,"decisions":1.8,"awareness":1.3,"manCover":.65,"zoneCover":.65,"speed":.65},
 "S":{"strength":2,"tackle":2.7,"vision":1.8,"decisions":1.6,"awareness":1.3,"manCover":.65,"zoneCover":.65,"speed":.65},
 "K":{"strength":3,"kickAccuracy":.7,"legPower":1.3},
 "P":{"strength":2.3,"kickAccuracy":.85,"legPower":.9}
}
def estimate(position,ratings):
 if position not in MODEL:return 50.0
 model=MODEL[position]
 return max(1,min(99,model["b"]+sum(c*ratings.get(k,0) for k,c in model["w"].items())))
def calibrate(position,ratings,desired):
 """Adapt Madden-style skill attributes so CapForge's weighted OVR matches.

 Returns (ratings, displayed_ovr, before_estimate, after_estimate).
 If the desired Madden OVR is genuinely unreachable, show a reachable OVR
 rather than an impossible value. The CapForge importer remains authoritative.
 """
 if position not in MODEL:return ratings,desired,desired,desired
 desired=max(1,min(99,int(desired)))
 old=estimate(position,ratings)
 r=dict(ratings)
 for cap in (12,30,70):
  for _ in range(35):
   gap=desired-estimate(position,r)
   if abs(gap)<.6:break
   direction=1 if gap>0 else -1
   available={}
   for key,coef in MODEL[position]["w"].items():
    if abs(coef)<.015 or key not in r:continue
    if coef*direction>0:
     room=min(99-r[key],cap-max(0,r[key]-ratings[key]))
    else:
     room=min(r[key]-1,cap-max(0,ratings[key]-r[key]))
    if room>0:available[key]=(coef,FLEX.get(position,{}).get(key,1.0),room)
   if not available:break
   denom=sum(coef*coef*flex for coef,flex,_ in available.values())
   if denom<=1e-10:break
   changed=False
   for key,(coef,flex,room) in available.items():
    delta=max(-room,min(room,gap*coef*flex/denom))
    new=max(1,min(99,round(r[key]+delta)))
    if new!=r[key]:r[key]=new;changed=True
   if not changed:break
 new_est=estimate(position,r)
 final=desired if abs(new_est-desired)<1.5 else round(new_est)
 return r,final,old,new_est
