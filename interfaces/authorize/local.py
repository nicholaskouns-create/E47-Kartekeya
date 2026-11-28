#!/usr/bin/env python3
"""Local-only Medicare CSV archive workbench. Python 3 standard library."""
import csv, io, json, sqlite3, zipfile, pathlib, urllib.request, hashlib, datetime, threading, webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
ROOT=pathlib.Path(__file__).resolve().parent
DATA=ROOT/'local-data'; DATA.mkdir(exist_ok=True)
DB=DATA/'catalog.sqlite'
def connect():
    c=sqlite3.connect(DB,timeout=30)
    c.execute("CREATE TABLE IF NOT EXISTS archives (name TEXT PRIMARY KEY, sha TEXT, imported TEXT, count INTEGER)")
    c.execute("CREATE VIRTUAL TABLE IF NOT EXISTS records USING fts5(archive UNINDEXED, table_name UNINDEXED, content, tokenize='unicode61')")
    return c
def import_zip(path):
    path=pathlib.Path(path)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    with connect() as c, zipfile.ZipFile(path) as z:
        if c.execute('SELECT 1 FROM archives WHERE name=? AND sha=?',(path.name,digest)).fetchone(): return
        c.execute('DELETE FROM records WHERE archive=?',(path.name,))
        count=0
        for info in z.infolist():
            if not info.filename.lower().endswith('.csv') or info.file_size>500_000_000: continue
            with z.open(info) as raw:
                sample=raw.read(4096)
            encoding='utf-8-sig'
            try: sample.decode(encoding)
            except UnicodeError: encoding='cp1252'
            with z.open(info) as raw:
                reader=csv.DictReader(io.TextIOWrapper(raw,encoding=encoding,errors='replace',newline=''))
                batch=[]
                for row in reader:
                    content=' | '.join(str(k)+': '+str(v) for k,v in row.items() if v)
                    batch.append((path.name,info.filename,content))
                    if len(batch)>=1000:
                        c.executemany('INSERT INTO records VALUES (?,?,?)',batch);count+=len(batch);batch=[]
                if batch: c.executemany('INSERT INTO records VALUES (?,?,?)',batch);count+=len(batch)
        if not count: raise ValueError('No CSV records in archive')
        c.execute('INSERT OR REPLACE INTO archives VALUES (?,?,?,?)',(path.name,digest,datetime.datetime.now().isoformat(),count))
def scan():
    errors=[]
    for p in DATA.glob('*.zip'):
        try: import_zip(p)
        except Exception as e: errors.append(p.name+': '+str(e))
    return errors
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u=urlparse(self.path)
        if u.path=='/':
            self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write((ROOT/'local.html').read_bytes());return
        if u.path not in ('/status','/search'):
            self.send_error(404);return
        with connect() as c:
            if u.path=='/status': result={'folder':str(DATA),'archives':c.execute('SELECT name,imported,count FROM archives').fetchall()}
            else:
                q=parse_qs(u.query).get('q',[''])[0][:100]
                terms=q.split()
                fts=' AND '.join('"'+t.replace('"','""')+'"' for t in terms)
                offset=max(0,min(100000,int(parse_qs(u.query).get('offset',['0'])[0])))
                result={'rows':c.execute('SELECT archive,table_name,content FROM records WHERE records MATCH ? LIMIT 25 OFFSET ?',(fts,offset)).fetchall() if terms else []}
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
    def do_POST(self):
        if self.path!='/import' or self.headers.get('Origin') not in (None,'http://127.0.0.1:8765'):
            self.send_error(403);return
        result={'errors':scan()}
        self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers();self.wfile.write(json.dumps(result).encode())
if __name__=='__main__':
    connect().close()
    print('Place official CMS CSV ZIP archives in',DATA)
    print('Import errors:',scan())
    server=ThreadingHTTPServer(('127.0.0.1',8765),Handler)
    webbrowser.open('http://127.0.0.1:8765/')
    server.serve_forever()
