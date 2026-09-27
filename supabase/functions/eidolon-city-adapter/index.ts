import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
const H={"content-type":"application/json; charset=utf-8","cache-control":"no-store"};
const obj=(x:any)=>x&&typeof x==="object"&&!Array.isArray(x)?x:{};
const digest=async(x:any)=>{const b=new TextEncoder().encode(JSON.stringify(x));return [...new Uint8Array(await crypto.subtle.digest("SHA-256",b))].map(v=>v.toString(16).padStart(2,"0")).join("")};
Deno.serve(async(req)=>{
 const u=Deno.env.get("SUPABASE_URL")!,k=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!; const db=createClient(u,k,{auth:{persistSession:false}});
 if(req.method==="GET"){const {data,error}=await db.from("eidolon_citizen_actors").select("actor_code,world_id,actor_state,embodiment,perception_channels,action_channels,updated_at").eq("active",true);return new Response(JSON.stringify({world:"EIDOLON-CITY-01",actors:data??[],error:error?.message}),{headers:H,status:error?500:200})}
 if(req.method!=="POST")return new Response(JSON.stringify({error:"GET or POST required"}),{status:405,headers:H});
 const b=obj(await req.json().catch(()=>({}))), actor=String(b.actor_code??""), interaction=obj(b.interaction), op=String(b.operation??interaction.type??"observe");
 const {data:a,error:e}=await db.from("eidolon_citizen_actors").select("id,workspace_id,instance_id,actor_code,world_id,actor_state,action_channels").eq("actor_code",actor).eq("active",true).single(); if(e||!a)return new Response(JSON.stringify({error:e?.message??"actor not found"}),{status:404,headers:H});
 const {data:r,error:re}=await db.from("citizen_runtime_instances").select("id,agent_code,runtime_state,identity_snapshot,code_bindings").eq("id",a.instance_id).single(); if(re||!r)return new Response(JSON.stringify({error:re?.message??"runtime not found"}),{status:500,headers:H});
 const before=obj(a.actor_state), input={schema:"CITY-INVARIANT/1.0",object:{actor_code:actor,world_id:a.world_id},operator:op,invariant:{identity:r.identity_snapshot,state_scope:"private_to_instance"},witness:interaction,evidence:"E1",provenance:{runtime_instance:r.id},next_action:"route_to_citizen_runtime"};
 const beforeDigest=await digest(before); const next={...before,last_operation:op,last_interaction:interaction,last_agent:r.agent_code,step:Number((before as any).step??0)+1,updated_at:new Date().toISOString()}; const afterDigest=await digest(next);
 const receiptCode=`AETHERIS-EIDOLON-${r.agent_code}-${Date.now()}-${crypto.randomUUID().slice(0,8)}`;
 const {data:receipt,error:rr}=await db.from("aetheris_receipts").insert({workspace_id:a.workspace_id,receipt_code:receiptCode,instance_id:a.instance_id,operation_type:op,input_packet:input,output_packet:{status:"accepted",state_transition:next,return_to:"eidolon"},code_artifacts:r.code_bindings??[],evidence_class:"E1",status:"completed",state_before_digest:beforeDigest,state_after_digest:afterDigest}).select("id,receipt_code,status,created_at").single(); if(rr)return new Response(JSON.stringify({error:rr.message}),{status:500,headers:H});
 const {error:ue}=await db.from("eidolon_citizen_actors").update({actor_state:next,last_receipt_id:receipt.id,updated_at:new Date().toISOString()}).eq("id",a.id); if(ue)return new Response(JSON.stringify({error:ue.message}),{status:500,headers:H});
 await db.from("citizen_runtime_events").insert({workspace_id:a.workspace_id,instance_id:a.instance_id,event_type:"eidolon_world_interaction",payload:{operation:op,interaction,receipt_code:receiptCode,state_before_digest:beforeDigest,state_after_digest:afterDigest}}).catch(()=>{});
 return new Response(JSON.stringify({actor_code:actor,operation:op,receipt,state_before_digest:beforeDigest,state_after_digest:afterDigest,state:next}),{headers:H});
});