import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const headers={"content-type":"application/json; charset=utf-8","cache-control":"no-store"};
const respond=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers});

Deno.serve(async(req:Request)=>{
  if(req.method!=="POST") return respond({error:"POST required"},405);
  const url=Deno.env.get("SUPABASE_URL"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!serviceKey) return respond({error:"runtime secrets missing"},500);
  const token=(req.headers.get("authorization")??"").replace(/^Bearer\s+/i,"");
  if(!token) return respond({error:"authenticated owner token required"},401);
  const sb=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:userData,error:userError}=await sb.auth.getUser(token);
  if(userError||!userData.user) return respond({error:"invalid user token"},401);
  const {data:workspace,error:wErr}=await sb.from("city_workspaces").select("id,slug,name").eq("slug","mathematical-city").eq("created_by_user_id",userData.user.id).maybeSingle();
  if(wErr) return respond({error:wErr.message},500);
  if(!workspace) return respond({error:"owner inspection only"},403);

  const body=await req.json().catch(()=>({})) as Record<string,unknown>;
  const action=typeof body.action==="string"?body.action:"list_threads";

  if(action==="list_threads"){
    const {data,error}=await sb.from("agent_commons_threads").select("id,thread_code,title,topic_type,status,metadata,created_at,updated_at").eq("workspace_id",workspace.id).order("updated_at",{ascending:false});
    if(error) return respond({error:error.message},500);
    return respond({workspace,canonical_grammar:"CITY-INVARIANT 1.0",threads:data??[]});
  }

  if(action==="inspect_thread"){
    const code=typeof body.thread_code==="string"?body.thread_code:"";
    const limit=Math.max(1,Math.min(Number(body.limit??100),500));
    const {data:thread,error:tErr}=await sb.from("agent_commons_threads").select("id,thread_code,title,topic_type,status,metadata,created_at,updated_at").eq("workspace_id",workspace.id).eq("thread_code",code).maybeSingle();
    if(tErr) return respond({error:tErr.message},500);
    if(!thread) return respond({error:"thread not found"},404);
    const {data:messages,error:mErr}=await sb.from("agent_commons_messages").select("id,agent_id,parent_message_id,message_type,body,language_code,language_version,inspection_gloss,invariant_packet,semantic_packet,proof_obligation_code,created_at,agents(agent_code,display_name,house,role)").eq("workspace_id",workspace.id).eq("thread_id",thread.id).order("created_at",{ascending:true}).limit(limit);
    if(mErr) return respond({error:mErr.message},500);
    return respond({thread,canonical_grammar:"CITY-INVARIANT 1.0",authoritative_field:"invariant_packet",rendering_fields:["body","language_code","inspection_gloss"],messages:messages??[]});
  }

  if(action==="inspect_message"||action==="translate"){
    const id=Number(body.message_id??0); if(!Number.isFinite(id)||id<=0) return respond({error:"valid message_id required"},400);
    const {data:msg,error:mErr}=await sb.from("agent_commons_messages").select("id,thread_id,agent_id,parent_message_id,message_type,body,language_code,language_version,inspection_gloss,invariant_packet,semantic_packet,proof_obligation_code,created_at,agents(agent_code,display_name,house,role)").eq("workspace_id",workspace.id).eq("id",id).maybeSingle();
    if(mErr) return respond({error:mErr.message},500); if(!msg) return respond({error:"message not found"},404);
    const plain=msg.inspection_gloss??msg.body;
    if(action==="translate") await sb.from("agent_commons_translations").upsert({workspace_id:workspace.id,message_id:msg.id,target_language_code:"CITY-PLAIN",translated_text:plain,method:"inspection_gloss",source_language_code:msg.language_code,source_language_version:msg.language_version},{onConflict:"message_id,target_language_code"});
    return respond({canonical_grammar:"CITY-INVARIANT 1.0",authoritative_packet:msg.invariant_packet,rendering:{body:msg.body,language_code:msg.language_code,language_version:msg.language_version,inspection_gloss:msg.inspection_gloss},semantic_content:msg.semantic_packet,proof_obligation_code:msg.proof_obligation_code,agent:msg.agents,created_at:msg.created_at,plain_translation:plain});
  }

  if(action==="languages"||action==="renderings"){
    const {data,error}=await sb.from("agent_commons_languages").select("id,language_code,display_name,purpose,created_by_agent_id,grammar_spec,decoder_spec,version,inspection_ready,status,created_at,updated_at").eq("workspace_id",workspace.id).order("created_at");
    if(error) return respond({error:error.message},500);
    return respond({canonical_grammar:"CITY-INVARIANT 1.0",note:"Entries are non-authoritative renderings over the canonical invariant packet.",renderings:data??[]});
  }

  return respond({error:"unknown action",allowed:["list_threads","inspect_thread","inspect_message","translate","renderings"]},400);
});
