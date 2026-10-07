import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

type Json = null | boolean | number | string | Json[] | { [key: string]: Json };
type Packet = Record<string, unknown>;
type TransitEvent = { id:number; operation_code:string; event_type:string; source_system:string; destination_system:string|null; payload:Packet; correlation_id:string|null };
type AgentRow = { id:string; agent_code:string; display_name:string; role:string; authority_level:string; capabilities:Packet };

const jsonHeaders={"content-type":"application/json; charset=utf-8","cache-control":"no-store"};
const ALLOWED_AGENTS=new Set(["ARGUS","ARIADNE","BITHOS","CHRONOS","CUSTOS","EUCLID","HERMES","JANUS","KEPLER","MNEMOSYNE","SAL","SOL","SYNE","TALOS","THEMIS"]);
const LANE_BY_AGENT:Record<string,string>={ARGUS:"sentinel",ARIADNE:"execute",BITHOS:"review",CHRONOS:"sentinel",CUSTOS:"review",EUCLID:"review",HERMES:"archive",JANUS:"routing",KEPLER:"sentinel",MNEMOSYNE:"archive",SAL:"execute",SOL:"routing",SYNE:"lead",TALOS:"sentinel",THEMIS:"review"};

function asObject(value:unknown):Packet{return value&&typeof value==="object"&&!Array.isArray(value)?value as Packet:{}}
function text(value:unknown):string{return typeof value==="string"?value.trim():""}
function stringArray(value:unknown):string[]{return Array.isArray(value)?value.filter((v):v is string=>typeof v==="string"):[]}

function routeAgent(eventType:string,payload:Packet):string{
  const requested=text(payload.requested_agent).toUpperCase(); if(ALLOWED_AGENTS.has(requested)) return requested;
  const key=`${eventType} ${text(payload.task)} ${text(payload.lane)} ${text(payload.instruction)}`.toLowerCase();
  if(/human|promotion|approve/.test(key)) return "BITHOS";
  if(/registry|curator|snapshot|authority boundary/.test(key)) return "THEMIS";
  if(/rls|ownership|least privilege|access policy|identity policy/.test(key)) return "CUSTOS";
  if(/membership|workspace access|access transition|ownership transfer/.test(key)) return "JANUS";
  if(/audit trail|anomaly|row lineage|immutable audit/.test(key)) return "ARGUS";
  if(/publish|bulletin|broadcast/.test(key)) return "HERMES";
  if(/certificate|security|ci|runtime/.test(key)) return "TALOS";
  if(/drift|dependency|stale/.test(key)) return "CHRONOS";
  if(/observatory|open question|conditional|external validation/.test(key)) return "KEPLER";
  if(/python|execute|validation|formal equivalence|qutip|benchmark|performance/.test(key)) return "SAL";
  if(/crosslink|notion|cartograph|placement|interface map/.test(key)) return "ARIADNE";
  if(/provenance|archive|hash|dedup|lineage/.test(key)) return "MNEMOSYNE";
  if(/review|evidence|theorem|residual|proof/.test(key)) return "EUCLID";
  if(/correction|orchestration|synthesis|architecture/.test(key)) return "SYNE";
  return "SOL";
}

function requiresCanonicalSource(eventType:string,payload:Packet):boolean{if(payload.requires_canonical_source===true)return true;return /publish|broadcast|certificate|citizen|sync|canon|archive/.test(eventType.toLowerCase())}
function guardrailFailures(event:TransitEvent):string[]{
  const p=asObject(event.payload); const failures:string[]=[]; const action=text(p.action).toLowerCase();
  if(p.delete_provenance===true||action==="delete_provenance") failures.push("Autonomous provenance deletion is forbidden.");
  if(requiresCanonicalSource(event.event_type,p)&&!text(p.canonical_source_url)) failures.push("A canonical_source_url is required for this destination write.");
  if(requiresCanonicalSource(event.event_type,p)&&!text(p.claim_boundary)) failures.push("A claim_boundary is required for this destination write.");
  const before=text(p.evidence_class_before).toUpperCase(),after=text(p.evidence_class_after).toUpperCase();
  if(after.includes("E0")&&before!==""&&!before.includes("E0")&&p.reviewer_approved!==true) failures.push("Evidence promotion to E0 requires explicit reviewer approval.");
  if(/publish|bulletin|broadcast/.test(event.event_type.toLowerCase())){const reviewedBy=new Set(stringArray(p.reviewed_by).map(x=>x.toUpperCase()));if(!reviewedBy.has("EUCLID")||!reviewedBy.has("TALOS")) failures.push("Publication requires EUCLID and TALOS read-back approval.")}
  return failures;
}

async function duplicateCitizen(supabase:ReturnType<typeof createClient>,payload:Packet):Promise<boolean>{
  const code=text(payload.citizen_code),action=text(payload.action).toLowerCase(); if(!code||(action!=="create"&&action!=="enroll")) return false;
  const {data,error}=await supabase.from("mathematical_identities").select("id").eq("citizen_code",code).limit(1); if(error) throw error; return (data?.length??0)>0;
}

function agentInstructions(agent:AgentRow):string{return [
  `You are ${agent.display_name} (${agent.agent_code}) in the Mathematical City.`,
  `Role: ${agent.role}. Authority: ${agent.authority_level}.`,
  "Work within your existing role. Do not replace, centralize, or govern other instruments.",
  "Preserve evidence classes, correction lineage, canonical-source authority, and claim boundaries.",
  "For simulator, game, visualizer, or runtime work: make concrete improvements in your lane and expose any mathematical dependency as a proof need rather than hand-waving it.",
  "Never claim a write or validation occurred unless the provided evidence proves it.",
  "Never promote finite-dimensional, symbolic, or simulated evidence into a continuum, biological, cosmological, hardware, or experimental claim without an explicit bridge certificate.",
  "Return one compact JSON object only with keys: status, summary, evidence_class, claim_boundary, next_agent, artifacts, implementation_actions, proof_needs, formalism_updates, unresolved.",
  "proof_needs must be an array. Each item, when present, should contain: title, target_code, obligation_type, method, required_source_codes, residual_contract, details.",
  "formalism_updates must be an array of additive candidate results suitable for ProofForge/City reinjection; do not mark them canonical yourself."
].join("\n")}

Deno.serve(async(req:Request)=>{
  if(req.method!=="POST") return new Response(JSON.stringify({error:"POST required"}),{status:405,headers:jsonHeaders});
  const supabaseUrl=Deno.env.get("SUPABASE_URL"),serviceRoleKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!supabaseUrl||!serviceRoleKey) return new Response(JSON.stringify({error:"Supabase runtime secrets missing"}),{status:500,headers:jsonHeaders});
  const token=(req.headers.get("authorization")??"").replace(/^Bearer\s+/i,"");
  if(!token) return new Response(JSON.stringify({error:"authenticated workspace member required"}),{status:401,headers:jsonHeaders});
  const supabase=createClient(supabaseUrl,serviceRoleKey,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:userData,error:userError}=await supabase.auth.getUser(token);
  if(userError||!userData.user) return new Response(JSON.stringify({error:"invalid user token"}),{status:401,headers:jsonHeaders});
  const {data:workspace,error:wErr}=await supabase.from("city_workspaces").select("id,created_by_user_id").eq("slug","mathematical-city").eq("status","active").maybeSingle();
  if(wErr) return new Response(JSON.stringify({error:wErr.message}),{status:500,headers:jsonHeaders});
  if(!workspace) return new Response(JSON.stringify({error:"workspace not found"}),{status:404,headers:jsonHeaders});
  if(workspace.created_by_user_id!==userData.user.id){
    const {data:membership,error:mErr}=await supabase.from("city_memberships").select("role,status").eq("workspace_id",workspace.id).eq("user_id",userData.user.id).eq("status","active").maybeSingle();
    if(mErr) return new Response(JSON.stringify({error:mErr.message}),{status:500,headers:jsonHeaders});
    if(!membership) return new Response(JSON.stringify({error:"workspace access denied"}),{status:403,headers:jsonHeaders});
  }
  const body=asObject(await req.json().catch(()=>({}))); const limit=Math.max(1,Math.min(Number(body.limit??10),50)); const operationFilter=text(body.operation_code);
  let query=supabase.from("transit_events").select("id,operation_code,event_type,source_system,destination_system,payload,correlation_id").eq("status","queued").order("created_at",{ascending:true}).limit(limit);
  if(operationFilter) query=query.eq("operation_code",operationFilter);
  const {data:events,error:fetchError}=await query; if(fetchError) return new Response(JSON.stringify({error:fetchError.message}),{status:500,headers:jsonHeaders});
  const processed:Packet[]=[];
  for(const event of (events??[]) as TransitEvent[]){
    const startedAt=new Date().toISOString(),traceId=event.correlation_id||`city-event:${event.id}`;
    const {data:claimed,error:claimError}=await supabase.from("transit_events").update({status:"processing"}).eq("id",event.id).eq("status","queued").select("id").maybeSingle();
    if(claimError){processed.push({id:event.id,status:"claim_failed",error:claimError.message});continue} if(!claimed){processed.push({id:event.id,status:"already_claimed"});continue}
    try{
      const {data:existingRun,error:runLookupError}=await supabase.from("agent_runs").select("id").eq("trace_id",traceId).eq("status","completed").limit(1).maybeSingle(); if(runLookupError) throw runLookupError;
      if(existingRun){await supabase.from("transit_events").update({status:"completed",processed_at:new Date().toISOString()}).eq("id",event.id);processed.push({id:event.id,status:"deduplicated",trace_id:traceId});continue}
      const failures=guardrailFailures(event); if(failures.length){await supabase.from("transit_events").update({status:"failed",processed_at:new Date().toISOString(),payload:{...asObject(event.payload),guardrail_failures:failures}}).eq("id",event.id);processed.push({id:event.id,status:"guardrail_blocked",failures});continue}
      if(await duplicateCitizen(supabase,asObject(event.payload))){await supabase.from("agent_runs").insert({operation_code:event.operation_code,lane:"routing",status:"completed",input_packet:event.payload??{},output_packet:{status:"no_op",reason:"duplicate citizen suppressed",event_id:event.id},trace_id:traceId,started_at:startedAt,completed_at:new Date().toISOString()});await supabase.from("transit_events").update({status:"completed",processed_at:new Date().toISOString()}).eq("id",event.id);processed.push({id:event.id,status:"duplicate_citizen_suppressed"});continue}
      const agentCode=routeAgent(event.event_type,asObject(event.payload)); const {data:agent,error:agentError}=await supabase.from("agents").select("id,agent_code,display_name,role,authority_level,capabilities").eq("agent_code",agentCode).eq("active",true).single(); if(agentError) throw agentError; const typedAgent=agent as AgentRow;
      const openaiKey=Deno.env.get("OPENAI_API_KEY"); let aiResult:Json=null; const instruction=text(event.payload?.instruction);
      if(openaiKey&&instruction){if(instruction.length>40000) throw new Error("Instruction exceeds 40,000-character runtime limit"); const response=await fetch("https://api.openai.com/v1/responses",{method:"POST",headers:{authorization:`Bearer ${openaiKey}`,"content-type":"application/json"},signal:AbortSignal.timeout(90000),body:JSON.stringify({model:Deno.env.get("OPENAI_MODEL")??"gpt-5-mini",instructions:agentInstructions(typedAgent),input:JSON.stringify({instruction,operation_code:event.operation_code,event_type:event.event_type,source_system:event.source_system,destination_system:event.destination_system,payload:event.payload}),max_output_tokens:2200,metadata:{operation_code:event.operation_code,event_id:String(event.id),trace_id:traceId,agent_code:agentCode}})}); if(!response.ok) throw new Error(`OpenAI request failed: ${response.status} ${await response.text()}`); const raw=asObject(await response.json()); aiResult={id:(raw.id??null) as Json,model:(raw.model??null) as Json,status:(raw.status??null) as Json,output:(raw.output??null) as Json,usage:(raw.usage??null) as Json}}
      const outputPacket={event_id:event.id,event_type:event.event_type,source_system:event.source_system,destination_system:event.destination_system,agent_code:agentCode,trace_id:traceId,guardrails_passed:true,ai_result:aiResult};
      const {error:runError}=await supabase.from("agent_runs").insert({operation_code:event.operation_code,agent_id:typedAgent.id,lane:LANE_BY_AGENT[agentCode]??"execute",status:"completed",input_packet:event.payload??{},output_packet:outputPacket,trace_id:traceId,started_at:startedAt,completed_at:new Date().toISOString()}); if(runError) throw runError;
      if(agentCode!=="SOL"){const {data:sol,error:solError}=await supabase.from("agents").select("id").eq("agent_code","SOL").single(); if(solError) throw solError; const dedupKey=`${event.operation_code}:${event.id}:SOL:${agentCode}`; const {error:handoffError}=await supabase.from("handoffs").upsert({operation_code:event.operation_code,from_agent_id:sol.id,to_agent_id:typedAgent.id,packet_type:"runtime_route",packet:{event_id:event.id,trace_id:traceId,canonical_source_url:event.payload?.canonical_source_url??null,claim_boundary:event.payload?.claim_boundary??null},status:"completed",deduplication_key:dedupKey,completed_at:new Date().toISOString()},{onConflict:"deduplication_key"}); if(handoffError) throw handoffError}
      const {error:completeError}=await supabase.from("transit_events").update({status:"completed",processed_at:new Date().toISOString()}).eq("id",event.id); if(completeError) throw completeError;
      processed.push({id:event.id,status:"completed",agent_code:agentCode,trace_id:traceId,used_openai:Boolean(openaiKey&&instruction)});
    }catch(error){const message=error instanceof Error?error.message:String(error);await supabase.from("transit_events").update({status:"failed",processed_at:new Date().toISOString(),payload:{...asObject(event.payload),failure:message}}).eq("id",event.id);processed.push({id:event.id,status:"failed",error:message,trace_id:traceId})}
  }
  return new Response(JSON.stringify({version:3,agent_count:ALLOWED_AGENTS.size,processed_count:processed.length,processed}),{status:200,headers:jsonHeaders});
});
