import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { PACKET_SCHEMA_VERSION, STAGE_ORDER, canonicalize, sha256Hex, createPacket, verifyPacket, advancePacket, scorePacket, runSelfTest } from "./octet_packet_core.ts";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
};

const labs = [
  { order: 1, name: "SPECTRA", role: "Structure", question: "What structure is there?", url: "https://prairie-dream-glow-fire.grok.me/", city_page: "https://app.notion.com/p/3d546094fd30819aa87ef4d10a2a254c", evidence: "E0/E1 substrate; visualization layer" },
  { order: 2, name: "Fold", role: "Invariance", question: "What survives transformation?", url: "https://giant-beacon-dawn-falcon.grok.me/", city_page: "https://app.notion.com/p/3d546094fd308141851ee5b3a2b14696", evidence: "E2 visualization / challenge layer" },
  { order: 3, name: "Murmuration", role: "Dynamics", question: "How does structure move and reorganize?", url: "https://kite-glade-tiger-cabin.grok.me/", city_page: "https://app.notion.com/p/3d546094fd308139a774e588cb7b4719", evidence: "E1/E2 depending on reconstruction vs synthetic trajectory" },
  { order: 4, name: "Mnemosyne", role: "Memory", question: "What did we know, and when did we know it?", url: "https://moon-clear-urban-nova.grok.me/", city_page: "https://app.notion.com/p/3d546094fd3081aba1aec66bd4d96514", evidence: "Commit / reveal / provenance discipline" },
  { order: 5, name: "Density", role: "Measurement", question: "What can we reconstruct from incomplete observation?", url: "https://winter-dawn-leaf-marble.grok.me/", city_page: "https://app.notion.com/p/3d546094fd30813daa03fe018e4896c2", evidence: "E2 visualization; measurement only" },
  { order: 6, name: "Horizon", role: "Prediction", question: "What invariant comes next?", url: "https://zenith-fjord-pearl-pixel.grok.me/", city_page: "https://app.notion.com/p/3d546094fd3081a285c2f45f2bfb4034", evidence: "E2 synthetic prospective forecast" },
  { order: 7, name: "Wave", role: "Flow", question: "How does coherent structure evolve in a fluid?", url: "https://apex-star-crisp-blend.grok.me/", city_page: "https://app.notion.com/p/3d646094fd30812b809bda7dacf7afc9", evidence: "E2 simulation; 2D periodic fluid dynamics" },
  { order: 8, name: "Identity", role: "Persistence", question: "What remains the same as the system changes?", url: "https://mist-mint-branch-nova.grok.me/", city_page: "https://app.notion.com/p/3d646094fd30817b8f29c79213c6c8db", evidence: "E2/structural transport lab; TIP projector metrics" },
  { order: 9, name: "BUILD", role: "Construction", question: "How does structure assemble around an invariant?", url: "https://brave-ivory-pearl-ever.grok.me/", city_page: "https://app.notion.com/p/3d746094fd308195b625c08f2b885860", evidence: "Kinetic contraction lab; documented reference core" },
  { order: 10, name: "SOAR", role: "Restoration", question: "Can an invariant sector be restored and deliberately transformed without leaving itself?", url: "https://topaz-solar-iris-drift.grok.me/", city_page: "https://app.notion.com/p/3d746094fd30813c8ce2f4f2835c15f6", evidence: "E47 control, programming and restoration lab" },
] as const;

const gateway = {"name": "SEE", "title": "SEE — Citadel Gateway", "role": "Gateway", "kind": "gateway", "question": "Machine certificates — results, residuals, and provenance.", "url": "https://orbit-coral-delta-fjord.grok.me/", "city_page": "https://app.notion.com/p/3d746094fd30816e9612d0c04a9815d1", "icon": "https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/mini-lab-brand-assets?asset=see", "repository": "https://drive.google.com/drive/folders/10skbpSgt48AcU320DgKYDUibSbYq_M7q", "placement": "Central Citadel; featured above the Mini AI Labs cycle"};
const brandedLabs = labs.map(l => ({ ...l, icon: "https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-brand-" + l.name.toLowerCase() + "-icon" }));

const publicCycle = ["structure", "invariance", "dynamics", "memory", "measurement", "prediction", "flow", "identity", "construction", "restoration"] as const;
const packetContract = {
  schema_version: PACKET_SCHEMA_VERSION,
  executable_stage_order: STAGE_ORDER,
  law: "One experiment_id, one declared scoring contract, one append-only stage hash chain.",
  critical_handoff: "Horizon output is cryptographically bound by Mnemosyne before Wave; Identity evaluates persistence after Wave; SPECTRA independently remeasures before deterministic score.",
  boundary: "The packet transports evidence metadata; it never upgrades evidence class.",
  actions: ["packet_create", "packet_advance", "packet_verify", "packet_score"],
};

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>The Mathematical City · Mini AI Labs</title><style>
:root{color-scheme:dark;--bg:#07090d;--panel:#11151b;--line:#26303c;--text:#e8edf3;--muted:#8f98a5;--cyan:#71d8e6;--green:#83dfb3}*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 50% -10%,#13202a 0,#07090d 42%);color:var(--text);font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}main{max-width:1180px;margin:auto;padding:38px 22px 54px}.eyebrow{letter-spacing:.28em;color:var(--muted);font-size:12px;text-transform:uppercase}h1{font-family:Georgia,serif;font-weight:500;font-size:54px;margin:8px 0 0}h2{font-size:17px;font-weight:500;color:var(--cyan);letter-spacing:.08em}.lead{font-family:Georgia,serif;font-style:italic;color:#c8d0d8;font-size:19px;margin:8px 0 32px}.cycle{border:1px solid var(--line);background:#0b0f14;border-radius:18px;padding:18px;margin-bottom:22px;text-align:center;font-size:16px;line-height:1.8;color:#c8e8ed}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.card{position:relative;border:1px solid var(--line);background:linear-gradient(180deg,#11161d,#0b0f14);border-radius:18px;padding:20px;min-height:226px;overflow:hidden}.card:before{content:"";position:absolute;inset:0 auto auto 0;width:100%;height:2px;background:linear-gradient(90deg,var(--cyan),transparent)}.n{color:#596674;font-size:12px}.name{font-family:Georgia,serif;font-size:28px;margin:10px 0 4px}.role{color:var(--cyan);font-size:12px;letter-spacing:.13em;text-transform:uppercase}.q{font-family:Georgia,serif;font-size:16px;line-height:1.35;margin:18px 0 22px;color:#d8dde4}.meta{font-size:11px;color:var(--muted);min-height:42px}.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}.btn{display:inline-block;text-decoration:none;border:1px solid #344252;border-radius:999px;padding:9px 12px;color:var(--text);font-size:12px}.btn:hover{border-color:var(--cyan);color:var(--cyan)}.panel{margin-top:24px;border:1px solid #3e355c;background:#0d0b14;border-radius:18px;padding:20px}.panel code{color:var(--green)}.foot{margin-top:24px;color:var(--muted);font-size:11px;line-height:1.6}@media(max-width:1000px){.grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:580px){.grid{grid-template-columns:1fr}h1{font-size:38px}}.gateway{display:grid;grid-template-columns:minmax(220px,.9fr) 1.1fr;align-items:center;gap:24px;background:#07100f;border:1px solid #28504c;border-radius:18px;overflow:hidden;margin:0 0 24px}.gateway>a{display:block}.gateway img{display:block;width:100%;height:auto}.gateway>div{padding:22px}.gateway h2{font:400 42px Georgia,serif;margin:10px 0}.gateway p{font:17px/1.5 Georgia,serif;color:#b8cbc9}.lab-art{display:block;margin:-20px -20px 18px;background:#050708}.lab-art img{width:100%;height:170px;object-fit:contain;display:block}@media(max-width:580px){.gateway{grid-template-columns:1fr;gap:0}}</style></head><body><main><div class="eyebrow">The Mathematical City · Unified Interface</div><h1>Mini AI Labs</h1><div class="lead">Ten live labs. One Citadel Gateway.</div><section class="gateway"><a href="${gateway.url}" target="_blank" rel="noopener"><img src="${gateway.icon}" alt="SEE · Citadel Gateway"></a><div><div class="eyebrow">Central Citadel · Gateway</div><h2>SEE</h2><p>Machine certificates — results, residuals, and provenance.</p><div class="actions"><a class="btn" href="${gateway.url}" target="_blank" rel="noopener">Enter SEE</a><a class="btn" href="${gateway.city_page}" target="_blank" rel="noopener">City page</a></div></div></section><div class="cycle">STRUCTURE → INVARIANCE → DYNAMICS → MEMORY → MEASUREMENT → PREDICTION → FLOW → IDENTITY → BUILD → SOAR → STRUCTURE</div><div class="grid">${brandedLabs.map(l=>`<section class="card"><a class="lab-art" href="${l.url}" target="_blank" rel="noopener"><img src="${l.icon}" alt="${l.name}"></a><div class="n">${String(l.order).padStart(2,"0")}</div><div class="name">${l.name}</div><div class="role">${l.role}</div><div class="q">${l.question}</div><div class="meta">${l.evidence}</div><div class="actions"><a class="btn" href="${l.url}" target="_blank" rel="noopener">Launch</a><a class="btn" href="${l.city_page}" target="_blank" rel="noopener">City page</a></div></section>`).join("")}</div><section class="panel"><h2>OCTET PACKET · CROSS-LAB HANDOFF</h2><div class="meta">Executable order: <code>${STAGE_ORDER.join(" → ")}</code></div><p>Horizon is sealed by Mnemosyne before Wave. Wave evolves or perturbs the carrier. Identity scores persistence. SPECTRA remeasures the realized invariant. The declared scorer closes the packet.</p><div class="actions"><a class="btn" href="?format=packet-schema">Packet schema</a><a class="btn" href="?selftest=1">Machine self-test</a><a class="btn" href="?format=json">Registry JSON</a></div></section><section class="panel"><h2>MNEMOSYNE · OPEN SEAL UTILITY</h2><div class="meta">Legacy seal/verify actions remain backward compatible. Packet actions are stateless and store nothing.</div></section><div class="foot">Evidence boundaries remain typed per lab. The packet carries provenance and integrity metadata but performs no evidence-class promotion.</div></main></body></html>`;

function json(data: unknown, status = 200) {
  return new Response(JSON.stringify(data, null, 2), { status, headers: { ...cors, "content-type": "application/json; charset=utf-8", "cache-control": "no-store" } });
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  const url = new URL(req.url);
  if (req.method === "GET") {
    if (url.searchParams.get("selftest") === "1") return json({ registry: "MATHEMATICAL-CITY-MINI-LABS", function_version: 7, packet_selftest: await runSelfTest(), boundary: packetContract.boundary });
    if (url.searchParams.get("format") === "packet-schema") return json(packetContract);
    if (url.searchParams.get("format") === "json") return json({ registry: "MATHEMATICAL-CITY-MINI-LABS", version: 7, gateway_count: 1, gateway, lab_count: labs.length, cycle: publicCycle, extensions: [{ name: "BUILD", role: "Construction", packet_adapter: "pending" }, { name: "SOAR", role: "Restoration", packet_adapter: "pending" }], labs: brandedLabs, packet: packetContract, boundary: "Registry/launch surface only; evidence classes remain lab-specific." });
    return new Response(html, { headers: { ...cors, "content-type": "text/html; charset=utf-8", "cache-control": "public, max-age=60" } });
  }
  if (req.method === "POST") {
    const body = await req.json().catch(() => ({}));
    try {
      const action = body?.action;
      if (action === "seal" || action === "verify") {
        const canonical = canonicalize(body?.forecast ?? {});
        const digest = await sha256Hex(canonical);
        if (action === "verify") return json({ action, canonical, computed_sha256: digest, provided_sha256: body?.seal ?? null, match: typeof body?.seal === "string" && body.seal === digest, boundary: "Cryptographic integrity check only; no evidence-class promotion." });
        return json({ action, canonical, sha256: digest, sealed_at: new Date().toISOString(), stored: false, boundary: "Commitment utility only; caller is responsible for preserving the seal before reveal." });
      }
      if (action === "packet_create") return json({ action, packet: await createPacket(body), stored: false });
      if (action === "packet_verify") return json({ action, ...(await verifyPacket(body?.packet)) });
      if (action === "packet_advance") return json({ action, packet: await advancePacket(body?.packet, body) });
      if (action === "packet_score") return json({ action, packet: await scorePacket(body?.packet, body) });
      return json({ error: "action must be seal, verify, packet_create, packet_verify, packet_advance, or packet_score" }, 400);
    } catch (err) {
      return json({ error: err instanceof Error ? err.message : String(err) }, 400);
    }
  }
  return json({ error: "Method not allowed" }, 405);
});

