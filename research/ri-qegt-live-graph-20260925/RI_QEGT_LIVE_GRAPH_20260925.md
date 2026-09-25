# RI/QEGT Live Cross-Platform Object Graph — 2026-09-25

**Pre-publication certificate:** `MC-RI-QEGT-LIVE-GRAPH-PRE-20260925`  
**Post-publication certificate:** `MC-RI-QEGT-LIVE-GRAPH-POST-20260925`  
**Evidence class:** E1 machine validation  
**Topology:** empirical object graph from live platform records. No biological five-node topology was prescribed.

## Live sources

The graph was reconstructed from live GitHub, Notion, Google Drive, Supabase, and Google Calendar data. Cross-platform edges came from retrieved `public.sync_registry` rows for the E47 / MATRIX / RI / QEGT / Kartekeya / Atlas / spacetime corpus. Object-to-platform membership edges were derived from observed platform ownership or parent metadata.

Before publication, the primary Google Calendar was searched across calendar year 2026 for `E47`, `Mathematical City`, `Kartekeya`, `MATRIX`, `RI`, and `QEGT`. No matching project event existed, so Calendar entered the frozen pre-publication graph as an isolated component.

## Empirical operator

For the undirected structural collapse of each observed graph,

`K_live = D - A`.

## Frozen pre-publication result

- nodes: **96**
- edges: **145**
- live sync-registry edges: **54**
- platform-membership edges: **91**
- connected components: **2**
- `dim ker(K_live)=2`
- `lambda_gap=0.3983961403474403`
- `lambda_max=37.02915764005643`
- `epsilon=0.024305170772408326`
- measured contraction factor: `0.990316913773787`
- iterations selected from the measured spectrum: **2131**
- kernel-convergence residual: `4.326632938746049e-12`
- predicates: **12/13 PASS**

Every local/componentwise RI/QEGT invariant passed. The sole failed predicate was **unique global attractor**, because the research fabric and Calendar were two disconnected components. This is the independent pre-publication test and remains frozen.

## Publication closure

The finished report was then written to GitHub, Notion, Google Drive and Supabase, and a Google Calendar publication record was created. The Calendar record contains live links to the GitHub report/certificate/validator, Notion page, Drive mirror, and Supabase logical ID. Those links were then recorded in `public.sync_registry`.

Recomputing the graph from this actual post-publication topology produced:

- nodes: **101**
- edges: **157**
- connected components: **1**
- `dim ker(K_live)=1`
- `lambda_gap=0.40775585784689994`
- `lambda_max=38.02909622331191`
- `epsilon=0.02366608963607971`
- measured contraction factor: `0.9903500133185587`
- iterations: **2135**
- kernel-convergence residual: `5.335118796558469e-12`
- predicates: **13/13 PASS**

The post-publication global attractor is an integration result, not retroactive evidence for the frozen pre-publication topology.

## RI/QEGT equations used

`rho_(n+1) = (I - epsilon K_live) rho_n`

`(rho_(n+1)-rho_n)/epsilon + B J_n = 0`

`J_n=B^T rho_n`

`K_live=B B^T`

`kappa_n=||K_live rho_n||_2`

`Phi_n=1/(kappa_n+delta)`

## Cross-platform objects

GitHub report: https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/ri-qegt-live-graph-20260925/RI_QEGT_LIVE_GRAPH_20260925.md

GitHub pre certificate: https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/ri-qegt-live-graph-20260925/MC-RI-QEGT-LIVE-GRAPH-PRE-20260925.json

GitHub validator: https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/research/ri-qegt-live-graph-20260925/ri_qegt_live_cross_platform_graph_20260925.py

Notion: https://app.notion.com/p/3e646094fd3081f8ab4fd8facd48d7b4?pvs=204

Google Drive: https://docs.google.com/document/d/1akV583EFaSUqs-K_lFz5MBokGk90nq_eQSslGSEN8KE/edit

Calendar event ID: `4bjln3pee3gqe6ojm6gur9lfq0`

Supabase logical ID: `RI-QEGT-LIVE-GRAPH-20260925`
