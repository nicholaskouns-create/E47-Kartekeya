#!/usr/bin/env python3
"""Civic interface link audit: static local graph and optional live HTTP crawl.
Usage: python scripts/audit_city_links.py [--live]
Exit nonzero on missing canonical entrypoints, orphaned civic page or broken local links.
"""
from __future__ import annotations
import html.parser, pathlib, sys, urllib.parse, urllib.request, time
ROOT=pathlib.Path(__file__).resolve().parents[1]/"website"
BASE="https://nicholaskouns-create.github.io/E47-Kartekeya/"
PAGES=["index.html","interfaces/city-live/index.html","interfaces/formalism-atlas/index.html","interfaces/route-packets/index.html","interfaces/civic-assignment/index.html"]
TARGET="interfaces/civic-assignment/index.html"
class Links(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag in ("a","link","script","img"):
            d=dict(attrs)
            for key in ("href","src"):
                if key in d and d[key]:self.links.append(d[key])
def normalized(current,link):
    u=urllib.parse.urlsplit(link)
    if u.scheme in ("mailto","tel","javascript","data") or link.startswith("#") or link.startswith("//"):return None
    if u.scheme and u.netloc not in ("nicholaskouns-create.github.io",):return None
    if u.netloc:
        if not u.path.startswith("/E47-Kartekeya/"):return None
        rel=u.path[len("/E47-Kartekeya/"):]
    elif u.path.startswith("/E47-Kartekeya/"):rel=u.path[len("/E47-Kartekeya/"):]
    elif u.path.startswith("/"):return None
    else:rel=urllib.parse.urljoin(current,link).split("?",1)[0].split("#",1)[0]
    if not rel or rel.endswith("/"):rel+="index.html"
    return urllib.parse.unquote(rel)
def main():
    issues=[];graph={}
    for page in PAGES:
        file=ROOT/page
        if not file.is_file():issues.append("missing page "+page);continue
        parser=Links();parser.feed(file.read_text(encoding="utf-8"))
        graph[page]=set()
        for link in parser.links:
            rel=normalized(page,link)
            if rel is None:continue
            graph[page].add(rel)
            if not (ROOT/rel).is_file():issues.append(page+" -> missing "+rel)
    inbound=[p for p,links in graph.items() if p!=TARGET and TARGET in links]
    if len(inbound)<3:issues.append("civic assignment orphan: expected 3+ inbound routes; got "+str(inbound))
    if "index.html" not in graph.get(TARGET,set()):issues.append("civic assignment lacks home backlink")
    if "--live" in sys.argv:
        for page in PAGES+["data/city-assignment.json"]:
            url=urllib.parse.urljoin(BASE,page)
            ok=False
            for attempt in range(3):
                try:
                    req=urllib.request.Request(url,headers={"User-Agent":"MathematicalCityLinkAudit/1.0"})
                    with urllib.request.urlopen(req,timeout=15) as resp:
                        ok=resp.status==200
                        if ok:break
                except Exception as e:last=str(e)
                if attempt<2:time.sleep(5)
            if not ok:issues.append("LIVE FAIL "+url+" "+str(locals().get("last","HTTP non-200")))
    print("CITY LINK AUDIT", "PASS" if not issues else "FAIL", "pages",len(PAGES),"civic inbound",len(inbound),"live",("--live" in sys.argv))
    for i in issues:print("ERROR",i)
    return int(bool(issues))
if __name__=="__main__":raise SystemExit(main())
