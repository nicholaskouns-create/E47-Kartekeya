const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Cache-Control": "public, max-age=60, stale-while-revalidate=300",
  "Content-Type": "application/json; charset=utf-8",
};

type Surface = { label: string; substrate: string; kind: string; url: string };
type Packet = {
  id: string;
  title: string;
  packet_type: string;
  evidence: string[];
  status?: string | null;
  boundary?: string | null;
  summary?: string | null;
  surfaces: Surface[];
  certificates?: string[];
  provenance?: Record<string, unknown>;
};

function classify(url: string): string {
  try {
    const h = new URL(url).hostname.toLowerCase();
    if (h === "github.com" || h === "raw.githubusercontent.com" || h.endsWith("github.io")) return "github";
    if (h.includes("notion.")) return "notion";
    if (h === "docs.google.com" || h === "drive.google.com") return "drive";
    if (h.endsWith("supabase.co")) return "supabase";
    if (h === "www.aims.healthcare" || h === "aims.healthcare") return "aims";
    return "external";
  } catch {
    return "internal";
  }
}

function isHttp(v: unknown): v is string {
  return typeof v === "string" && /^https?:\/\//i.test(v);
}

function deepUrls(value: unknown, path = "reference", out: Array<{label:string,url:string}> = []) {
  if (isHttp(value)) out.push({ label: path.replace(/[_.-]+/g, " "), url: value });
  else if (Array.isArray(value)) value.forEach((v, i) => deepUrls(v, path + " " + (i + 1), out));
  else if (value && typeof value === "object") {
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) deepUrls(v, k, out);
  }
  return out;
}

function addSurface(packet: Packet, url: unknown, label: string, kind = "reference") {
  if (!isHttp(url)) return;
  if (packet.surfaces.some((s) => s.url === url)) return;
  packet.surfaces.push({ label, substrate: classify(url), kind, url });
}

function evidenceFrom(...values: unknown[]): string[] {
  const out = new Set<string>();
  const rx = /\b(E[0-4]|H0)\b/g;
  for (const v of values) {
    const text = typeof v === "string" ? v : JSON.stringify(v ?? "");
    for (const m of text.matchAll(rx)) out.add(m[1]);
  }
  return [...out];
}

async function rest(table: string, params: string): Promise<any[]> {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${params}`, {
    headers: { apikey: SERVICE_KEY, Authorization: `Bearer ${SERVICE_KEY}` },
  });
  if (!res.ok) throw new Error(`${table}: ${res.status} ${await res.text()}`);
  return await res.json();
}

async function safeRest(table: string, params: string, warnings: Array<{table:string,error:string}>): Promise<any[]> {
  try {
    return await rest(table, params);
  } catch (error) {
    warnings.push({ table, error: String(error) });
    console.error("route-packet source degraded", table, String(error));
    return [];
  }
}

function compact(packet: Packet): Packet {
  packet.surfaces.sort((a, b) => {
    const order: Record<string, number> = { github: 0, notion: 1, drive: 2, supabase: 3, aims: 4, external: 5, internal: 6 };
    return (order[a.substrate] ?? 9) - (order[b.substrate] ?? 9) || a.label.localeCompare(b.label);
  });
  packet.evidence = [...new Set(packet.evidence)];
  packet.certificates = [...new Set(packet.certificates ?? [])];
  return packet;
}

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: cors });
  if (req.method !== "GET") return new Response(JSON.stringify({ error: "GET only" }), { status: 405, headers: cors });

  try {
    const u = new URL(req.url);
    const query = (u.searchParams.get("q") ?? "").trim().toLowerCase();
    const wantedId = (u.searchParams.get("id") ?? "").trim();
    const wantedSubstrate = (u.searchParams.get("substrate") ?? "").trim().toLowerCase();
    const limit = Math.min(Math.max(Number(u.searchParams.get("limit") ?? 250) || 250, 1), 500);

    const warnings: Array<{table:string,error:string}> = [];
    const [surfaces, bundles, artifacts, identities, certificates, syncs] = await Promise.all([
      safeRest("city_interactive_surfaces", "select=surface_code,title,surface_type,route,lay_guide,egghead_reference,updated_at&active=eq.true&order=updated_at.desc&limit=500", warnings),
      safeRest("publication_bundles", "select=bundle_code,citizen_code,monograph_ref,json_certificate_ref,python_validator_ref,notion_ref,database_identity_ref,visualization_refs,provenance_hash,bundle_status,updated_at&access_scope=eq.public&order=updated_at.desc&limit=500", warnings),
      safeRest("source_artifacts", "select=id,logical_id,title,source_system,canonical_url,evidence_class,artifact_type,status,metadata,content_hash,updated_at&access_scope=eq.public&status=eq.active&order=updated_at.desc&limit=500", warnings),
      safeRest("mathematical_identities", "select=citizen_code,title,evidence_class,validation_status,source_artifact_id,boundary,metadata,updated_at&access_scope=eq.public&order=updated_at.desc&limit=500", warnings),
      safeRest("machine_certificates", "select=certificate_code,title,source_artifact_id,commit_sha,evidence_class,valid,result,updated_at&access_scope=eq.public&valid=eq.true&order=updated_at.desc&limit=500", warnings),
      safeRest("sync_registry", "select=logical_id,source_system,source_external_id,destination_system,destination_external_id,canonical,content_hash,sync_status,last_synced_at,metadata&access_scope=eq.public&sync_status=eq.synced&order=last_synced_at.desc&limit=1000", warnings),
    ]);

    const packets = new Map<string, Packet>();
    const artifactById = new Map(artifacts.map((a) => [a.id, a]));
    const identityByCode = new Map(identities.map((i) => [i.citizen_code, i]));
    const syncByLogical = new Map<string, any[]>();
    for (const s of syncs) {
      const list = syncByLogical.get(s.logical_id) ?? [];
      list.push(s); syncByLogical.set(s.logical_id, list);
    }
    const certByArtifact = new Map<string, any[]>();
    for (const c of certificates) {
      if (!c.source_artifact_id) continue;
      const list = certByArtifact.get(c.source_artifact_id) ?? [];
      list.push(c); certByArtifact.set(c.source_artifact_id, list);
    }

    for (const s of surfaces) {
      const p: Packet = {
        id: s.surface_code, title: s.title, packet_type: "interactive_surface",
        evidence: evidenceFrom(s.lay_guide, s.egghead_reference),
        status: "active",
        boundary: s.egghead_reference?.evidence_boundary ?? s.lay_guide?.boundary ?? null,
        summary: s.lay_guide?.what ?? s.lay_guide?.role ?? s.lay_guide?.public_question ?? null,
        surfaces: [], certificates: [],
        provenance: { surface_type: s.surface_type, updated_at: s.updated_at },
      };
      addSurface(p, s.route, "open", "runtime");
      for (const ref of deepUrls(s.egghead_reference)) addSurface(p, ref.url, ref.label, "lineage");
      packets.set(p.id, compact(p));
    }

    for (const b of bundles) {
      const identity = identityByCode.get(b.citizen_code);
      const id = b.citizen_code || b.bundle_code;
      const p: Packet = packets.get(id) ?? {
        id, title: identity?.title ?? b.bundle_code, packet_type: "publication_bundle",
        evidence: evidenceFrom(identity?.evidence_class, identity?.metadata),
        status: b.bundle_status,
        boundary: identity?.boundary ?? null,
        summary: null, surfaces: [], certificates: [],
        provenance: { bundle_code: b.bundle_code, provenance_hash: b.provenance_hash, updated_at: b.updated_at },
      };
      addSurface(p, b.monograph_ref, "monograph", "publication");
      addSurface(p, b.json_certificate_ref, "machine certificate", "certificate");
      addSurface(p, b.python_validator_ref, "python validator", "source");
      addSurface(p, b.notion_ref, "notion", "knowledge");
      for (const ref of deepUrls(b.visualization_refs)) addSurface(p, ref.url, ref.label, "visualization");
      packets.set(id, compact(p));
    }

    for (const a of artifacts) {
      const p: Packet = packets.get(a.logical_id) ?? {
        id: a.logical_id, title: a.title, packet_type: a.artifact_type ?? "source_artifact",
        evidence: evidenceFrom(a.evidence_class, a.metadata), status: a.status,
        boundary: a.metadata?.evidence_boundary ?? null, summary: null, surfaces: [], certificates: [],
        provenance: { content_hash: a.content_hash, source_system: a.source_system, updated_at: a.updated_at },
      };
      addSurface(p, a.canonical_url, a.source_system ?? "source", "source");
      for (const ref of deepUrls(a.metadata)) addSurface(p, ref.url, ref.label, "metadata");
      for (const s of syncByLogical.get(a.logical_id) ?? []) {
        const metaUrl = deepUrls(s.metadata)[0]?.url;
        addSurface(p, metaUrl, s.destination_system ?? "synced copy", "sync");
      }
      for (const c of certByArtifact.get(a.id) ?? []) {
        p.certificates!.push(c.certificate_code);
        p.evidence.push(...evidenceFrom(c.evidence_class, c.result));
      }
      packets.set(a.logical_id, compact(p));
    }

    for (const i of identities) {
      if (packets.has(i.citizen_code)) continue;
      const p: Packet = {
        id: i.citizen_code, title: i.title, packet_type: "mathematical_identity",
        evidence: evidenceFrom(i.evidence_class, i.metadata), status: i.validation_status,
        boundary: i.boundary, summary: null, surfaces: [], certificates: [],
        provenance: { updated_at: i.updated_at },
      };
      const a = i.source_artifact_id ? artifactById.get(i.source_artifact_id) : null;
      if (a) addSurface(p, a.canonical_url, a.source_system ?? "source", "source");
      for (const ref of deepUrls(i.metadata)) addSurface(p, ref.url, ref.label, "metadata");
      packets.set(i.citizen_code, compact(p));
    }

    for (const c of certificates) {
      const id = c.certificate_code;
      if (packets.has(id)) continue;
      const p: Packet = {
        id, title: c.title, packet_type: "machine_certificate",
        evidence: evidenceFrom(c.evidence_class, c.result), status: c.valid ? "valid" : "invalid",
        boundary: null, summary: null, surfaces: [], certificates: [id],
        provenance: { commit_sha: c.commit_sha, updated_at: c.updated_at },
      };
      const a = c.source_artifact_id ? artifactById.get(c.source_artifact_id) : null;
      if (a) addSurface(p, a.canonical_url, a.source_system ?? "source", "source");
      packets.set(id, compact(p));
    }

    let list = [...packets.values()];
    if (wantedId) list = list.filter((p) => p.id === wantedId);
    if (query) list = list.filter((p) => JSON.stringify(p).toLowerCase().includes(query));
    if (wantedSubstrate) list = list.filter((p) => p.surfaces.some((s) => s.substrate === wantedSubstrate));
    list.sort((a, b) => a.title.localeCompare(b.title));
    list = list.slice(0, limit);

    const substrateCounts: Record<string, number> = {};
    for (const p of list) for (const s of p.surfaces) substrateCounts[s.substrate] = (substrateCounts[s.substrate] ?? 0) + 1;

    return new Response(JSON.stringify({
      schema: "CITY-ROUTE-PACKETS/1.0",
      generated_at: new Date().toISOString(),
      principle: "Projection, not authority. Evidence class and independent lineage remain attached to source objects.",
      counts: {
        packets: list.length,
        registered_active_surfaces: surfaces.length,
        public_publication_bundles: bundles.length,
        public_source_artifacts: artifacts.length,
        public_mathematical_identities: identities.length,
        public_valid_machine_certificates: certificates.length,
        public_synced_routes: syncs.length,
        surfaces_by_substrate: substrateCounts,
      },
      warnings,
      packets: list,
    }, null, 2), { headers: cors });
  } catch (error) {
    return new Response(JSON.stringify({ error: String(error) }), { status: 500, headers: cors });
  }
});