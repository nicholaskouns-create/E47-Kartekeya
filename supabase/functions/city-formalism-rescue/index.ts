import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
};

const operation = {
  operation_code: "CITY-MURMURATION-STRANDED-RESCUE-20260910-A",
  status: "in_progress",
  title: "City Murmuration · Stranded Formalism Rescue",
  initiated: "2026-09-10",
  active_machine_agents_tasked: 15,
  queued_agent_runs: 15,
  typed_handoffs: 15,
  launch_inventory: {
    stranded_math_nonterminal: 10,
    open_cross_platform_discrepancies_at_launch: 3,
    python_corpus_review_queue: 2,
    physics_rescue_nonterminal: 7,
  },
  current_registry_state: {
    open_cross_platform_discrepancies: 4,
    note: "A fourth review discrepancy was created by this operation for the 13-row Notion civic registry versus 15 active Supabase machine-agent mapping. It is held for explicit reconciliation, not guessed auto-repair.",
  },
  links: {
    notion: "https://app.notion.com/p/3d746094fd30812cb966c8e8980704b5",
    drive_operation_record: "https://docs.google.com/document/d/1HLitBCCFK2czbTlnXiRvpDasg9-arUjLZuMxxyxc98s/edit",
    soar_repository: "https://drive.google.com/drive/folders/1xiEfmUjrXgreUsz2GDijNE1DVjXF1ZOo",
    soar_manifest: "https://drive.google.com/file/d/18qMUzdOGhlJpZPygOw3VoQBlnWEkB4dT/view",
    mini_ai_labs: "https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-mini-labs",
  },
  rescue_law: [
    "preserve source before normalization",
    "deduplicate before creating a new formal citizen",
    "rerun machine-checkable claims and preserve failures",
    "separate theorem, computational proxy, simulation, physical model, empirical claim, and open bridge",
    "repair only unambiguous cross-platform drift automatically",
    "keep existing human and publication gates intact",
    "return every rescued object to a canonical destination with reciprocal links and an explicit boundary",
  ],
  boundary: "This public page reports durable City tasking and registry state. It does not assert that queued agents have independently completed their lanes. Notion Custom Agent live sessions are not represented as executed.",
} as const;

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: { ...cors, "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mathematical City · Formalism Rescue</title><style>:root{color-scheme:dark;--bg:#07090d;--p:#101720;--line:#2a3947;--txt:#edf4f7;--muted:#93a3ad;--cyan:#79dce5}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 50% -10%,#19303b,#07090d 46%);color:var(--txt);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}main{max-width:980px;margin:auto;padding:46px 22px}.eyebrow{letter-spacing:.25em;color:var(--muted);font-size:11px}h1{font:500 clamp(38px,7vw,66px)/1 Georgia,serif;margin:10px 0}.lead{font:italic 18px/1.5 Georgia,serif;color:#c8d1d8}.panel{border:1px solid var(--line);background:linear-gradient(180deg,#111a23,#0b1117);border-radius:18px;padding:20px;margin:18px 0}.status{color:var(--cyan);letter-spacing:.12em}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}.metric{border:1px solid var(--line);border-radius:14px;padding:14px}.metric b{display:block;font:500 30px Georgia,serif}.metric span{font-size:11px;color:var(--muted)}li{margin:.7em 0;line-height:1.45}a{color:var(--cyan)}.foot{color:var(--muted);font-size:11px;line-height:1.6}@media(max-width:700px){.grid{grid-template-columns:repeat(2,1fr)}}</style></head><body><main><div class="eyebrow">THE MATHEMATICAL CITY · CONTROL PLANE</div><h1>Formalism Rescue</h1><div class="lead">Recover the stranded mathematics. Preserve the trail.</div><section class="panel"><div class="status">IN PROGRESS · CITY-MURMURATION-STRANDED-RESCUE-20260910-A</div><p>All 15 active machine agents have durable queued tasking and typed handoffs. The operation preserves provenance, reruns executable claims, repairs only unambiguous drift, and routes unresolved bridges without promoting evidence by resemblance.</p></section><div class="grid"><div class="metric"><b>15</b><span>agents tasked</span></div><div class="metric"><b>10</b><span>stranded records</span></div><div class="metric"><b>4</b><span>open discrepancies now</span></div><div class="metric"><b>7</b><span>physics rescue rows</span></div></div><section class="panel"><h2>Rescue law</h2><ol>${operation.rescue_law.map(x=>`<li>${x}</li>`).join("")}</ol></section><section class="panel"><h2>Registry drift</h2><p>Launch inventory contained 3 open discrepancies. This operation added a fourth review discrepancy for the 13-row Notion civic registry versus 15 active Supabase machine agents. The mapping is intentionally held for explicit reconciliation rather than guessed duplication.</p></section><section class="panel"><h2>Authority</h2><p><a href="${operation.links.notion}" target="_blank" rel="noopener">Notion operation page</a> · <a href="${operation.links.drive_operation_record}" target="_blank" rel="noopener">Drive operation record</a> · <a href="${operation.links.soar_repository}" target="_blank" rel="noopener">SOAR repository</a> · <a href="${operation.links.soar_manifest}" target="_blank" rel="noopener">SOAR manifest</a> · <a href="${operation.links.mini_ai_labs}" target="_blank" rel="noopener">Mini AI Labs</a></p></section><div class="foot">${operation.boundary} · <a href="?format=json">machine-readable JSON</a></div></main></body></html>`;

Deno.serve((req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  if (req.method !== "GET") return json({ error: "Method not allowed" }, 405);
  const url = new URL(req.url);
  if (url.searchParams.get("format") === "json") return json(operation);
  return new Response(html, { headers: { ...cors, "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=60" } });
});
