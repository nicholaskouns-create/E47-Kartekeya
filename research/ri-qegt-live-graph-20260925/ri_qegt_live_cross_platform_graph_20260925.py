#!/usr/bin/env python3
"""MC-RI-QEGT-LIVE-GRAPH-PRE-20260925 snapshot validator."""
import hashlib, io, json, numpy as np, networkx as nx, pandas as pd

RAW = r"""E47-SPECTRAL-MATRIX-MACHINE-20260925|github|research/e47/validation/e47_spectral_matrix_proof.py|notion|3e646094-fd30-816b-ae88-f079283800d4|False|synced
E47-SPECTRAL-MATRIX-MACHINE-20260925|github|research/e47/validation/e47_spectral_matrix_proof.py|google_drive|1-zVHvwMsRC-Ljv0cizwBJ41tDcgBnhUMGTr0GID74Bo|False|synced
E47-SPECTRAL-MATRIX-MACHINE-20260925|github|research/e47/validation/e47_spectral_matrix_proof.py|github_pages|website/interfaces/e47-spectral-matrix-proof/index.html|False|synced
E47-TWO-PAGE-NOTE-20260923|github|docs/notes/e47-recursive-system.md@6a68587b4bb2fc6341085ce3cf8841fad9a4e99b|google_drive|13nnzimU93t6KPKGV-FWWTekxmuoLvpAQWc-Y9oVOzHI|False|synced
E47-CURRENT-FORMALISM-20260922|github|research/e47-current-20260922|notion|3e446094-fd30-81e3-84f5-e6a2fcc690a3|True|synced
E47-CURRENT-FORMALISM-20260922|github|research/e47-current-20260922|supabase|PUB-E47-CURRENT-FORMALISM-20260922|True|synced
E47-CURRENT-FORMALISM-20260922|github|research/e47-current-20260922|google_drive|18tcATYK_Va3v4YgnrjcGSFi2GqIciyaZ|True|synced
MC-E47-CORPUS-REPRO-20260912|google_drive|1UC3mRIKp5iLAlreXGKcMK_MuiJalgtYB|notion|3d946094-fd30-81da-848a-ecb6a399c361|True|synced
MC-E47-CORPUS-REPRO-20260912|notion|3d946094-fd30-81da-848a-ecb6a399c361|supabase|27a96de2-1cbc-47fe-9879-b24cdd9a91f4|True|synced
E47-QOP-ARCHIVE-20260728|google_drive|1KZVPsV3CK_7eWXlymDp8AT5QNaQiMJuX77RI9HIBhDM|supabase|public.source_artifacts:E47-QOP-ARCHIVE-20260728|False|synced
E47-BASE5-XDOC-20260729|google_drive|13f_XcqDNGKfgkuK5ACrMORdbIxoR4cUwikwSQc3r9mw|supabase|public.source_artifacts:E47-BASE5-XDOC-20260729|True|synced
drive:e47-monograph|google_drive|1NJhmD8Xupc6Ng2AgQPos2HKnxlO-e4t0UbrukPKQNic|supabase|public.source_artifacts:drive:e47-monograph|True|synced
DRIVE:E47-UNIFIED-CONTRACTION-20260808|google_drive|1tKDHLlhaVONtGZm4FHe5STaqlyatO-X_-5iBujgcXhg|supabase|public.source_artifacts:DRIVE:E47-UNIFIED-CONTRACTION-20260808|False|synced
drive:failure-atlas|google_drive|1IjFjsXsGWO4H862z3Qt36zLnwJzYsOwUzGfln7MJBqA|supabase|public.source_artifacts:drive:failure-atlas|True|synced
DRIVE:KARTEKEYA-PYTHON-2-GITHUB-20260808|google_drive|1xBUY4MHBjoYyFJQO58u-yw8uhhnpzpq4yewxSGI0rpQ|supabase|public.source_artifacts:DRIVE:KARTEKEYA-PYTHON-2-GITHUB-20260808|False|synced
E47-JSSC-20260813|google_drive|16fPZb2n3Vlyg2PjqlcseY51cYP4XoEkKOn3Vy7-_9no|supabase|public.source_artifacts:E47-JSSC-20260813|False|synced
E47-PROJECTOR-CORRECTION-20260731|google_drive|1ZapCCTwgurUi175Dp7zRaT6gcgeyh8Fa3bJLpxgX2fc|supabase|public.source_artifacts:E47-PROJECTOR-CORRECTION-20260731|False|synced
E47-QOP-CERT-20260728|google_drive|15AByloFNFiZyid1ftlM82s7SAI8vb-hn|supabase|public.source_artifacts:E47-QOP-CERT-20260728|False|synced
E47-QOP-PYTHON-20260728|google_drive|1LWqMJaVajdUbRSUVThBX0m26dIbuqiiV|supabase|public.source_artifacts:E47-QOP-PYTHON-20260728|False|synced
E47-VISUAL-REPAIR-20260731|google_drive|1TsEb1GblXZxYWS3KdkfowdpHMcXBtihjQZA-GPZM02o|supabase|public.source_artifacts:E47-VISUAL-REPAIR-20260731|False|synced
PRIME-E47-20260802-SOURCE|google_drive|18DN7bSyTTNQ6ZHw7GZFZju_HncZ2KdIHpTiq8kpuduA|supabase|public.source_artifacts:PRIME-E47-20260802-SOURCE|False|synced
PROTEIN-E47-COMP-20260726|google_drive|1nzW-2_UqQnErwFeYTH5URR5WzYi23i79DNfP4PnEJr0|supabase|public.source_artifacts:PROTEIN-E47-COMP-20260726|False|synced
PYFORM-ATLAS-20260730|google_drive|1-h3J6wrs9E3rOhqkiRgMdeNC8LdsQQ3JXbwFj7NocRs|supabase|public.source_artifacts:PYFORM-ATLAS-20260730|True|synced
QF-RC-E47-20260728|google_drive|1KZDI12mO8SZi_ozE_BTrMzr21mbCyc_yjAXLs_AYIR0|supabase|public.source_artifacts:QF-RC-E47-20260728|True|synced
QF-RC-E47-CERT-20260728|google_drive|17RJEmSm9iLMUx9Nn8XCdU-gYnqiVwuNX|supabase|public.source_artifacts:QF-RC-E47-CERT-20260728|False|synced
QF-RC-E47-PYTHON-20260728|google_drive|1UJT0DoLjS4QZmBoFTFSn3cY1zb-Xoq7P|supabase|public.source_artifacts:QF-RC-E47-PYTHON-20260728|False|synced
QMET-E47-20260728|google_drive|1DjKPn6Is9iIyowrYFqyKXG-Yj9QlMkTLeZUJdKiw9HA|supabase|public.source_artifacts:QMET-E47-20260728|True|synced
RUB5-MATRIX-LEDGER-20260730|google_drive|1DSHbKZHXA6THbFf_9KjKcxaiuTAwaSWw|supabase|public.source_artifacts:RUB5-MATRIX-LEDGER-20260730|False|synced
PGT-E47-20260731|google_drive|1W-0rdZzkMUdaTc83mBD6HPNYO__5jxdCFEAUdPeAng4|supabase|public.source_artifacts:PGT-E47-20260731|True|synced
DRIVE-E47-MULTI-20260819|google_drive|1c-BSHB9TdZztPYHKR8dHgMZDRmdUumg3Bhzy6P0e6g4|supabase|public.source_artifacts:DRIVE-E47-MULTI-20260819|False|synced
DRIVE:E47-EIN-LIN-001-20260808|google_drive|1pfYP8Vvd3yRwfdii0KJySF10wLzY8yXN5VRsmPT77I4|supabase|public.source_artifacts:DRIVE:E47-EIN-LIN-001-20260808|False|synced
DRIVE:E47-EINSTEIN-FIRST-PRINCIPLES-20260808|google_drive|1as9rD712drrCXGtlGVh7liruBuOPqjzqW7pZnAOR47w|supabase|public.source_artifacts:DRIVE:E47-EINSTEIN-FIRST-PRINCIPLES-20260808|False|synced
DRIVE:E47-EXPANDED-SPECTRAL-20260808|google_drive|1vaq07eVbZhdUqZ1Bn9_r37ikJNBDVL5R8UlrEnomAAE|supabase|public.source_artifacts:DRIVE:E47-EXPANDED-SPECTRAL-20260808|False|synced
DRIVE:E47-GAUGE-EHM-MONOGRAPH-20260808|google_drive|1uhb77h-0F7V7e3zeAUZEsZWV_8ewqQg1-UdjEXAFK9Y|supabase|public.source_artifacts:DRIVE:E47-GAUGE-EHM-MONOGRAPH-20260808|False|synced
DRIVE:E47-KARTEKEYA-FRAMEWORK-DECK-20260808|google_drive|1z34XEYpsQH1_o596iyyZ8tlQP1LDfrW5|supabase|public.source_artifacts:DRIVE:E47-KARTEKEYA-FRAMEWORK-DECK-20260808|False|synced
DRIVE:E47-MACHINE-CERTIFICATES-PROV-20260808|google_drive|1FPyhzhx9rpHEh7fSz2djpv19NNJ5Kx3QMbHJmRulHXo|supabase|public.source_artifacts:DRIVE:E47-MACHINE-CERTIFICATES-PROV-20260808|False|synced
DRIVE:E47-MASTER-INVARIANT-MAPPING-20260808|google_drive|1_izsP8kNj3z2ZKOBuMpbpNuj3cWfq_qcruTIXJBXy6U|supabase|public.source_artifacts:DRIVE:E47-MASTER-INVARIANT-MAPPING-20260808|False|synced
E47-FPSK-COMM-20260815|notion|3b846094-fd30-81fa-a961-f635dffdd0ff|google_drive|1Z3mZW4xaZqMDUQ5IrxM1dIaaGOKRjq0phH2l1ytIGL8|True|complete
E47-QOP-PYTHON-20260728|google_drive|1LWqMJaVajdUbRSUVThBX0m26dIbuqiiV|notion|3a046094-fd30-817b-b4a6-e317dd633482|True|synced
PRIME-E47-20260802-CSV|google_drive|1uaxeekNAyORjUjuxzbgBumMH2kia0mID|supabase|PRIME-E47-C06|True|synced
E47-JSSC-20260813|notion|3bb46094-fd30-81e0-b4c4-e2230516c361|supabase|E47-JSSC-C01|True|complete
E47-JSSC-20260813|google_drive|16fPZb2n3Vlyg2PjqlcseY51cYP4XoEkKOn3Vy7-_9no|notion|3bb46094-fd30-81e0-b4c4-e2230516c361|True|complete
PRIME-E47-20260802-CERT|google_drive|1t4_A811mnrWrr7Md81Wcm9Q3ioMHe5jX|supabase|PRIME-E47-CERT-20260802|True|synced
PRIME-E47-20260802-SOURCE|google_drive|18DN7bSyTTNQ6ZHw7GZFZju_HncZ2KdIHpTiq8kpuduA|notion|3a346094fd30816d8010fa3e6784545c|True|synced
PGT-E47-20260731|google_drive|1W-0rdZzkMUdaTc83mBD6HPNYO__5jxdCFEAUdPeAng4|notion|3a346094-fd30-816d-8010-fa3e6784545c|True|synced
PYFORM-ATLAS-20260730|google_drive|1-h3J6wrs9E3rOhqkiRgMdeNC8LdsQQ3JXbwFj7NocRs|notion|3ad46094-fd30-81e8-925c-f7404de777f6|True|complete
E47-BASE5-XDOC-20260729|google_drive|13f_XcqDNGKfgkuK5ACrMORdbIxoR4cUwikwSQc3r9mw|notion|0b778ea1-fbe0-4d20-b7b3-e998abd4ca76|True|synced
QF-RC-E47-20260728|google_drive|1KZDI12mO8SZi_ozE_BTrMzr21mbCyc_yjAXLs_AYIR0|notion|3ab46094-fd30-8106-8653-d6cad49ac7c8|True|synced
E47-QOP-OPERATIONS-20260728|notion|1b7bbbab-342f-460e-9826-70e3970054e2|supabase|public.agent_runs|True|synced
E47-QOP-CERT-20260728|google_drive|15AByloFNFiZyid1ftlM82s7SAI8vb-hn|notion|3a146094-fd30-8145-a068-f4e3469104f6|True|synced
E47-QOP-ARCHIVE-20260728|google_drive|1KZVPsV3CK_7eWXlymDp8AT5QNaQiMJuX77RI9HIBhDM|notion|3a146094-fd30-8145-a068-f4e3469104f6|True|synced
E47-QOP-CITIZENS-20260728|notion|fc363140-7264-4c7c-82da-8a22edf0a967|supabase|public.mathematical_identities|True|synced
QMET-E47-20260728|google_drive|1DjKPn6Is9iIyowrYFqyKXG-Yj9QlMkTLeZUJdKiw9HA|notion|3ab46094-fd30-814a-859c-f7db6edab303|True|synced
github:e47-repo|github|nicholaskouns-create/E47-Kartekeya|supabase|4857f9a9-e781-4b97-9c57-e5f2e7e53bcf|True|synced"""

df = pd.read_csv(io.StringIO(RAW), sep="|", names=["logical_id","ss","sid","ds","did","canonical","status"], dtype=str)
hubs = {
    "github":"hub:github:nicholaskouns-create/E47-Kartekeya",
    "notion":"hub:notion:e8646094-fd30-81bc-8bc5-00036498ec31",
    "google_drive":"hub:google_drive:0AAbDSlER6kFcUk9PVA",
    "supabase":"hub:supabase:gpkjvihkyectnenvnbng",
    "calendar":"hub:calendar:nicholaskouns@gmail.com",
}
alias={"github_pages":"github"}

Gd=nx.DiGraph()
for p,h in hubs.items(): Gd.add_node(h,system=p,kind="platform_container")
for r in df.itertuples(index=False):
    u=f"{r.ss}:{r.sid}"; v=f"{r.ds}:{r.did}"
    Gd.add_node(u,system=r.ss,kind="live_object"); Gd.add_node(v,system=r.ds,kind="live_object")
    Gd.add_edge(u,v,relation="sync_registry",logical_id=r.logical_id)
for n,a in list(Gd.nodes(data=True)):
    if a.get("kind")=="live_object":
        owner=alias.get(a["system"],a["system"])
        if owner in hubs and n!=hubs[owner]:
            Gd.add_edge(hubs[owner],n,relation="platform_membership")

G=nx.Graph(); G.add_nodes_from(Gd.nodes(data=True)); G.add_edges_from(Gd.edges())
nodes=sorted(G); A=nx.to_numpy_array(G,nodelist=nodes); K=np.diag(A.sum(1))-A
w,V=np.linalg.eigh(K); tol=1e-10; V0=V[:,abs(w)<tol]; P=V0@V0.T
edges=list(G.edges()); B=np.zeros((len(nodes),len(edges))); ix={n:i for i,n in enumerate(nodes)}
for j,(u,v) in enumerate(edges): B[ix[u],j]=1; B[ix[v],j]=-1
lm=float(w.max()); eps=.9/lm; F=np.eye(len(nodes))-eps*K
raw=np.array([int.from_bytes(hashlib.sha256(n.encode()).digest()[:8],"big")/2**64+1e-6 for n in nodes]); x0=raw/raw.sum(); x=x0.copy()
rho=float(max(abs(1-eps*w[w>tol]))); err=float(np.linalg.norm((np.eye(len(nodes))-P)@x0))
N=max(int(np.ceil(np.log(1e-10/max(err,1e-300))/np.log(rho)))+50,500)
cur=[]; fit=[]; ene=[]; cont=[]; mass=[]
for _ in range(N):
    y=F@x; J=B.T@x
    cont.append(np.linalg.norm((y-x)/eps+B@J))
    cur.append(np.linalg.norm(K@x)); fit.append(1/(cur[-1]+1e-15))
    ene.append(np.linalg.norm((np.eye(len(nodes))-P)@x)**2)
    mass.append(abs(x.sum()-x0.sum())); x=y
cur.append(np.linalg.norm(K@x)); fit.append(1/(cur[-1]+1e-15)); ene.append(np.linalg.norm((np.eye(len(nodes))-P)@x)**2)
c=nx.number_connected_components(G); kd=V0.shape[1]
checks={
"symmetric":np.linalg.norm(K-K.T)<1e-12,
"psd":w.min()>=-1e-10,
"kernel_components":kd==c,
"incidence":np.linalg.norm(K-B@B.T)<1e-12,
"stable":0<eps<2/lm,
"mass":max(mass)<1e-11,
"continuity":max(cont)<1e-11,
"curvature_down":bool(np.all(np.diff(cur)<=1e-11)),
"fitness_up":bool(np.all(np.diff(fit)>=-1e-7)),
"energy_down":bool(np.all(np.diff(ene)<=1e-11)),
"kernel_convergence":np.linalg.norm(x-P@x0)<1e-8,
"unique_global_attractor":kd==1,
"componentwise_attractor_count":kd==c,
}
print(json.dumps({
"nodes":len(nodes),"edges":G.number_of_edges(),"components":c,"kernel_dim":kd,
"lambda_max":lm,"spectral_gap":float(w[w>tol].min()),"epsilon":eps,
"rho_star":rho,"iterations":N,"convergence_residual":float(np.linalg.norm(x-P@x0)),
"checks":checks,"pass_count":sum(checks.values()),"test_count":len(checks)
},indent=2))
