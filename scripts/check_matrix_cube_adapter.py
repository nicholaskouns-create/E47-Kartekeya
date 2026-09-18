import json, urllib.request
u="https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter"
state=[[0.0,0.0] for _ in range(125)]
state[0]=[1.0,0.0]
req=urllib.request.Request(u,data=json.dumps({"statevector":state,"circuit":{"gates":[]}}).encode(),headers={"content-type":"application/json"},method="POST")
with urllib.request.urlopen(req,timeout=20) as r:
 print(r.status)
 print(r.read().decode()[:2000])
