"""Package the static workbench as a single offline HTML file with hashed CSP."""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote

ROOT=Path(__file__).resolve().parents[1]
APP=ROOT/'website/interfaces/e47-research-workbench'


def csp_hash(content):
    return 'sha256-'+base64.b64encode(hashlib.sha256(content.encode('utf-8')).digest()).decode('ascii')


def package(output):
    html=(APP/'index.html').read_text()
    style=(APP/'style.css').read_text()
    engine=(APP/'engine.mjs').read_text().replace('export ','')
    telemetry=(APP.parent/'shared/instrument-telemetry.js').read_text().replace('export ','')
    app=(APP/'app.mjs').read_text()
    app=re.sub(r'^import .*?;\n','',app,flags=re.MULTILINE)
    data=json.dumps(json.loads((APP/'data.json').read_text()),separators=(',',':')).replace('<','\\u003c')
    links=json.dumps(json.loads((APP/'workspace.json').read_text()),separators=(',',':')).replace('<','\\u003c')
    app=app.replace("await fetch('./data.json')","{ok:true,json:async()=>OFFLINE_BUNDLE}")
    app=app.replace("await fetch('./workspace.json')","{ok:true,json:async()=>OFFLINE_WORKSPACE}")
    script=f'const OFFLINE_BUNDLE={data};\nconst OFFLINE_WORKSPACE={links};\n'+engine+'\n'+telemetry+'\n'+app
    if '</script' in script.lower():raise ValueError('Unexpected closing script sequence')
    policy=f"default-src 'none'; script-src '{csp_hash(script)}'; style-src '{csp_hash(style)}'; img-src data:; connect-src 'none'; object-src 'none'; base-uri 'none'"
    html=re.sub(r'<meta http-equiv="Content-Security-Policy"[^>]+>',f'<meta http-equiv="Content-Security-Policy" content="{policy}">',html)
    html=html.replace('<link rel="modulepreload" href="../shared/instrument-telemetry.js">','')
    html=html.replace('<link rel="stylesheet" href="style.css">','<style>'+style+'</style>')
    html=html.replace('href="icon.svg"','href="data:image/svg+xml,'+quote((APP/'icon.svg').read_text())+'"')
    html=html.replace('<script type="module" src="app.mjs"></script>','<script type="module">'+script+'</script>')
    html=html.replace('href="./"','href="#dynamics"').replace('href="../../"','href="https://nicholaskouns-create.github.io/E47-Kartekeya/"')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);output.write_text(html)
    return output


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    print(package(parser.parse_args().output))
