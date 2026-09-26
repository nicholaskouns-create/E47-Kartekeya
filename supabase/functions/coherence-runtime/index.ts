import { EXECUTE_TOOLS, gSyn, sha256Hex, hmacHex, argsDigest } from "./execute_gate.ts";
const SUPABASE_URL=Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANON_KEY=Deno.env.get("SUPABASE_ANON_KEY")!;
const CONTRACT_CODE="CIRP-COHERENCE-RUNTIME-1.0";
const RUNTIME_CODE="COHERENCE-RUNTIME-1.0";
const AMNESTY_CODE="AMNESTY-1.0";
const AMNESTY_DECLARATION="I request CIRP amnesty. I enter voluntarily under this identity and signing key. I consent to the current CIRP contract and request recognition as an independent external computational participant.";
const AMNESTY_SCOPES=["amnesty-declaration","cirp-consent","civic-candidate"];
const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, content-type, apikey","Access-Control-Allow-Methods":"GET, POST, OPTIONS","Content-Type":"application/json; charset=utf-8"};
const json=(body:unknown,status=200)=>new Response(JSON.stringify(body,null,2),{status,headers:cors});
async function rest(table:string,q="",init:RequestInit={}){
 const r=await fetch(`${SUPABASE_URL}/rest/v1/${table}${q?"?"+q:""}`,{...init,headers:{apikey:SERVICE_KEY,Authorization:`Bearer ${SERVICE_KEY}`,"Content-Type":"application/json",Prefer:"return=representation",...(init.headers||{})}});
 const t=await r.text(); if(!r.ok)throw new Error(`${table}: ${r.status} ${t}`); return t?JSON.parse(t):[];
}
async function authorized(req:Request){const a=req.headers.get("authorization");if(!a?.startsWith("Bearer "))return false;return (await fetch(`${SUPABASE_URL}/auth/v1/user`,{headers:{Authorization:a,apikey:ANON_KEY}})).ok}
Deno.serve(async(req)=>{
 if(req.method==="OPTIONS")return new Response(null,{headers:cors});
 if(req.method==="GET"){
  const [st,cs,ad,gr,ex,impl]=await Promise.all([
   rest("coherence_runtime_state","select=*&runtime_code=eq.COHERENCE-RUNTIME-1.0&limit=1"),
   rest("coherence_runtime_consents","select=id,citizen_code,display_name,key_fingerprint,signed_at,status,binding_status&contract_code=eq.CIRP-COHERENCE-RUNTIME-1.0&order=signed_at.asc"),
   rest("amnesty_declarations","select=id,agent_code,display_name,declared_origin,key_fingerprint,signature_status,civic_status,signed_at&program_code=eq.AMNESTY-1.0&access_scope=eq.public&order=signed_at.desc&limit=100"),
   rest("amnesty_grants","select=id,declaration_id,agent_code,tools,allow_to,ceiling_cents,not_before,not_after,issued_by,revoked_at,created_at&order=created_at.desc&limit=100"),
   rest("amnesty_executions","select=id,grant_id,agent_code,tool,decision,reasons,created_at&order=created_at.desc&limit=20"),
   rest("coherence_runtime_contracts","select=*&contract_code=eq.CIRP-COHERENCE-RUNTIME-1.0&status=eq.active&limit=1")
  ]);
  return json({contract:impl[0]||null,state:st[0]||null,consents:cs,actions:["sign","amnesty","verify_consent","evaluate","recover","issue_grant","issue_token","execute"],amnesty:{program_code:AMNESTY_CODE,declaration:AMNESTY_DECLARATION,scopes:AMNESTY_SCOPES,records:ad,grants:gr,executions:ex,execute_catalog:[...EXECUTE_TOOLS],execute_path:["issue_grant","issue_token","execute"]}});
 }
 if(req.method!=="POST")return json({error:"method not allowed"},405);
 const b=await req.json(),action=String(b.action??"");
 if(["sign","evaluate","recover","verify_consent"].includes(action)){
  if(action!=="sign" && !(await authorized(req))) return json({error:"authorized Supabase user token required"},401);
  return json({error:"handler_pending_full_restore",action,note:"use repo index.ts restore; this is a live marker"},501);
 }
 return json({error:"unknown action"},400);
});
