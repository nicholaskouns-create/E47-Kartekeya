import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const headers = {"content-type":"application/json; charset=utf-8","cache-control":"no-store"};
const json = (body: unknown, status=200) => new Response(JSON.stringify(body), {status, headers});

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return json({error:"POST required"},405);
  const url = Deno.env.get("SUPABASE_URL");
  const key = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if (!url || !key) return json({error:"runtime secrets missing"},500);
  const sb = createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}});
  const body = await req.json().catch(()=>({})) as Record<string,unknown>;
  const mode = typeof body.mode === "string" ? body.mode : "snapshot";

  if (mode === "snapshot") {
    const tables = ["source_artifacts","mathematical_identities","machine_certificates","corrections","failure_atlas","theorem_graph_edges","claim_digital_twins","cross_platform_discrepancies","stranded_math_recovery","provenance_events","publication_bundles","proof_negative_constraints","cross_domain_correspondences","citizen_proof_candidates","approval_queue"];
    const counts: Record<string,number> = {};
    for (const t of tables) {
      const {count,error} = await sb.from(t).select("*",{count:"exact",head:true});
      if (error) return json({error:error.message,table:t},500);
      counts[t]=count ?? 0;
    }
    const runCode = `LAB-SNAPSHOT-${new Date().toISOString().replace(/[-:.TZ]/g,"")}`;
    await sb.from("research_lab_runs").insert({run_code:runCode,capability_code:"EDGE_LAB_SNAPSHOT",input_scope:{mode},inspected_count:counts.source_artifacts+counts.mathematical_identities,changed_count:counts.cross_platform_discrepancies,validated_count:counts.citizen_proof_candidates,approval_count:counts.approval_queue,residuals:{counts},status:"completed",completed_at:new Date().toISOString()});
    return json({status:"completed",run_code:runCode,counts});
  }

  if (mode === "queue_proof_search") {
    const trace = `EDGE-FORGE-${crypto.randomUUID()}`;
    const payload = {
      action:"proof_search",
      requested_agent:"EUCLID",
      canonical_source_url:"supabase:mathematical_identities",
      claim_boundary:"Generate candidate proofs only from explicitly type-compatible validated identities; no canonical promotion.",
      instruction:"Build a typed compatibility graph over validated Mathematical City identities. Generate one nontrivial pairwise or three-parent conjecture only when ambient types, operators, assumptions, and maps compose. Attempt exact derivation first; request executable validation if useful; preserve negative attempts and evidence boundaries; never promote canon.",
      reviewer_approved:false
    };
    const {data,error} = await sb.from("transit_events").insert({operation_code:"CITY-EDGE-PROOF-SEARCH",event_type:"theorem review candidate",source_system:"supabase",destination_system:"city-proof-forge",payload,correlation_id:trace,status:"queued"}).select("id").single();
    if (error) return json({error:error.message},500);
    return json({status:"queued",trace_id:trace,event_id:data.id});
  }

  if (mode === "queue_recovery") {
    const {data:rows,error} = await sb.from("stranded_math_recovery").select("recovery_code,source_title,source_url,validation_plan,evidence_boundary").in("status",["candidate","held"]).limit(10);
    if (error) return json({error:error.message},500);
    let queued=0;
    for (const row of rows ?? []) {
      const trace=`RECOVERY-${row.recovery_code}`;
      const {error:ie}=await sb.from("transit_events").insert({operation_code:"CITY-EDGE-RECOVERY",event_type:"python validation provenance",source_system:"supabase",destination_system:"stranded-math-recovery",correlation_id:trace,status:"queued",payload:{action:"validate_recovery",requested_agent:"SAL",canonical_source_url:row.source_url ?? `supabase:stranded_math_recovery:${row.recovery_code}`,claim_boundary:row.evidence_boundary ?? "Candidate recovery only; preserve source authority.",instruction:`Validate stranded-mathematics recovery candidate ${row.recovery_code}: ${row.source_title}. Check declared validation plan, identify exact reusable formalism, retain provenance, and return candidate/held/rejected status without canonical promotion.`,validation_plan:row.validation_plan}});
      if (!ie) queued++;
    }
    return json({status:"completed",queued});
  }

  return json({error:"unknown mode",allowed:["snapshot","queue_proof_search","queue_recovery"]},400);
});
