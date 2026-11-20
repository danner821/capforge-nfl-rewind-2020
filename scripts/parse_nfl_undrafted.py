"""Parse only player identities and position labels from NFL.com UDFA trackers.

This collects real people who entered the league undrafted in a given year.
No article prose or copyrighted images are copied into the roster.
The article's team assignment is intentionally discarded: the game drafts freely.
"""
from __future__ import annotations

import html
import re
import urllib.request
from html.parser import HTMLParser

SLUG = {
    2021:"undrafted-rookie-free-agents-team-signings-after-2021-nfl-draft",
    2022:"undrafted-rookie-free-agents-team-signings-after-2022-nfl-draft",
    2023:"undrafted-rookie-free-agents-team-signings-after-2023-nfl-draft",
    2024:"undrafted-rookie-free-agents-team-signings-after-2024-nfl-draft",
    2025:"undrafted-rookie-free-agents-team-signings-after-2025-nfl-draft",
    2026:"undrafted-free-agent-signings-tracker-every-team-s-udfas-after-the-2026-nfl-draft",
}
URLS={year:"https://www.nfl.com/news/"+slug for year,slug in SLUG.items()}
POSITIONS="QB|RB|FB|WR|TE|OT|OL|OG|G|C|DE|DL|DT|EDGE|OLB|ILB|LB|CB|DB|S|FS|SS|K|PK|P|LS"

class ListCollector(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.depth=0
        self.stack=[]
        self.items=[]
    def handle_starttag(self,tag,attrs):
        if tag=="li":
            if self.depth==0:
                self.stack=[]
            self.depth+=1
        if self.depth and tag in ("span","a","strong","b"):
            self.stack.append(" ")
    def handle_data(self,data):
        if self.depth:
            self.stack.append(data)
    def handle_endtag(self,tag):
        if tag=="li":
            self.depth-=1
            if self.depth==0:
                self.items.append(re.sub(r"\s+"," ","".join(self.stack)).strip())
                self.stack=[]

def parse_rookies(markup, year):
    p=ListCollector()
    p.feed(markup)
    players=[]
    seen=set()
    for entry in p.items:
        m=re.match(r"^("+POSITIONS+r")\s+(.+?)(?:,\s*(.+))?$",entry,re.I)
        if not m:continue
        pos=m.group(1).upper()
        if pos=="LS":continue  # CapForge has no long-snapper position
        name=m.group(2).strip()
        name=html.unescape(name).replace("\u2019","'").replace("\u2018","'")
        name=re.sub(r"\s*\((?:waived|signed|invited|released).*?\)","",name,flags=re.I).strip()
        name=name.rstrip("* ").strip()
        college=(m.group(3) or "").strip()
        if "," in college:college=college.split(",",1)[0].strip()
        key=re.sub("[^a-z0-9]","",name.lower())
        if len(name.split())<2 or not re.fullmatch(r"[A-Za-z .'\-]+",name):
            continue
        if key in seen: continue
        seen.add(key)
        players.append({"year":year,"name":name,"pos":pos,"college":college,
                        "source":"nfl_udfa"})
    return players

def load_undrafted_sources():
    result={}
    errors={}
    for year,url in URLS.items():
        attempts=(url,url.replace("www.nfl.com","amp.nfl.com"),
                  url.replace("www.nfl.com","fantasy-www.nfl.com"))
        found=[]
        for candidate in attempts:
            try:
                request=urllib.request.Request(candidate,
                   headers={"User-Agent":"Mozilla/5.0 (compatible; CapforgeRostersHistoricalAudit/1.0)",
                            "Accept":"text/html"})
                with urllib.request.urlopen(request,timeout=18) as response:
                    page=response.read().decode("utf-8",errors="replace")
                rows=parse_rookies(page,year)
                if len(rows)>=15:
                    found=rows
                    break
            except Exception as exc:
                errors[year]=type(exc).__name__
        result[year]=found
        if not found:
            errors[year]=errors.get(year,"No parseable 2021-2026 UDFA list found")
    return result,errors
