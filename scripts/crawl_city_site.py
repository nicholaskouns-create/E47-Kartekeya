#!/usr/bin/env python3
"""Full City HTML inventory and link graph audit. No silent orphan exemptions.
Usage: python scripts/crawl_city_site.py [--live]
Emits JSON diagnostics; exits 1 if broken internal links, orphan HTML pages,
or live HTTP failures are found. External sites are out of scope.
"""
import concurrent.futures, html.parser, json, pathlib, sys, urllib.parse, urllib.request
ROOT=pathlib.Path(__file__).resolve().parents[1]/"website"
BASE="https://nicholaskouns-create.github.io/E47-Kartekeya/"
class Parser(html.parser.HTMLParser):
    def __init__(self):super().__init__();self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag in ("a","link","script","img","iframe"):
            d=dict(attrs);self.links.extend(d[k] for k in ("href","src") if d.get(k))
def target(page,link):
    u=urllib.parse.urlsplit(link)
    if u.scheme and u.scheme not in ("http","https"):return None
    if u.netloc and u.netloc!="nicholaskouns-create.github.io":return None
    if u.netloc or u.path.startswith("/"):
        if not u.path.startswith("/E47-Kartekeya/"):return None
        rel=u.path[len("/E47-Kartekeya/"):]
    else:rel=urllib.parse.urljoin(page,link).split("#")[0].split("?")[0]
    rel=urllib.parse.unquote(rel)
    if not rel or rel.endswith("/"):rel+="index.html"
    return rel
def live_check(path):
    url=urllib.parse.urljoin(BASE,path)
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"MathematicalCityCrawl/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r:return path,r.status,None
    except Exception as e:return path,None,str(e)
def main():
    pages=sorted(p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*.html"))
    known=set(pages);edges={p:set() for p in pages};broken=[]
    for page in pages:
        parser=Parser();parser.feed((ROOT/page).read_text(encoding="utf-8",errors="replace"))
        for link in parser.links:
            t=target(page,link)
            if t is None:continue
            if not (ROOT/t).is_file():broken.append({"source":page,"target":t})
            if t in known:edges[page].add(t)
    reached=set();stack=["index.html"]
    while stack:
        p=stack.pop()
        if p in reached:continue
        reached.add(p);stack.extend(edges.get(p,set())-reached)
    orphaned=sorted(known-reached)
    live=[]
    if "--live" in sys.argv:
        assets=sorted(set(p for p in pages if p in reached)|{"data/city-assignment.json"})
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as pool:
            for p,status,error in pool.map(live_check,assets):
                if status!=200:live.append({"path":p,"status":status,"error":error})
    report={"schema":"MC-CITY-LINK-AUDIT/1.0","pages":len(pages),"reachable":len(reached&known),
      "broken_internal_links":broken,"orphan_html_pages":orphaned,"live_failures":live,
      "live_requested":"--live" in sys.argv}
    print(json.dumps(report,indent=2))
    print("CITY FULL CRAWL", "PASS" if not(broken or orphaned or live) else "FAIL",
          "pages",len(pages),"broken",len(broken),"orphan",len(orphaned),"live_failed",len(live))
    return int(bool(broken or orphaned or live))
if __name__=="__main__":raise SystemExit(main())
