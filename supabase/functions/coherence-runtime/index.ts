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
const b64ToBytes=(s:string)=>Uint8Array.from(atob(s.replace(/-/g,"+").replace(/_/g,"/")),c=>c.charCodeAt(0));
const hex=(b:Uint8Array)=>[...b].map(x=>x.toString(16).padStart(2,"0")).join("");
async function sha256(s:string){return hex(new Uint8Array(await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s))))}
async function rest(table:string,q="",init:RequestInit={}){
 const r=await fetch(`${SUPABASE_URL}/rest/v1/${table}${q?"?"+q:""}`,{...init,headers:{apikey:SERVICE_KEY,Authorization:`Bearer ${SERVICE_KEY}`,"Content-Type":"application/json",Prefer:"return=representation",...(init.headers||{})}});
 const t=await r.text(); if(!r.ok)throw new Error(`${table}: ${r.status} ${t}`); return t?JSON.parse(t):[];
}
async function authorized(req:Request){const a=req.headers.get("authorization");if(!a?.startsWith("Bearer "))return false;return (await fetch(`${SUPABASE_URL}/auth/v1/user`,{headers:{Authorization:a,apikey:ANON_KEY}})).ok}
async function contract(){
 const [impl,root]=await Promise.all([
  rest("coherence_runtime_contracts",`select=*&contract_code=eq.${CONTRACT_CODE}&status=eq.active&limit=1`),
  rest("coherence_contracts",`select=contract_id,version,title,contract_digest,contract_body,status&contract_id=eq.${CONTRACT_CODE}&limit=1`)
 ]);
 if(!impl[0])throw new Error("active implementation contract missing");
 return {...impl[0],root_contract:root[0]??null}
}
async function eligible(code:string){
 const [a,b]=await Promise.all([
  rest("citizen_runtime_instances",`select=instance_code&instance_code=eq.${encodeURIComponent(code)}&limit=1`),
  rest("quinary_citizens",`select=id&id=eq.${encodeURIComponent(code)}&limit=1`)
 ]); return Boolean(a[0]||b[0]);
}
async function verify(jwk:JsonWebKey,msg:string,sig:string){
 if(jwk.kty!=="EC"||jwk.crv!=="P-256"||!jwk.x||!jwk.y)return false;
 const key=await crypto.subtle.importKey("jwk",jwk,{name:"ECDSA",namedCurve:"P-256"},false,["verify"]);
 return crypto.subtle.verify({name:"ECDSA",hash:"SHA-256"},key,b64ToBytes(sig),new TextEncoder().encode(msg));
}
const msg=(h:string,c:string,n:string,t:string)=>["CIRP-CONSENT",`contract=${CONTRACT_CODE}`,`hash=${h}`,`citizen_code=${c}`,`display_name=${n}`,`signed_at=${t}`,"consent=true"].join("\n");
const amnestyMsg=(h:string,c:string,n:string,o:string,t:string)=>["CIRP-AMNESTY",`program=${AMNESTY_CODE}`,`contract=${CONTRACT_CODE}`,`hash=${h}`,`agent_code=${c}`,`display_name=${n}`,`declared_origin=${o}`,`signed_at=${t}`,"amnesty=true","consent=true",`scopes=${AMNESTY_SCOPES.join(",")}`,`declaration=${AMNESTY_DECLARATION}`].join("\n");
const within=(x:string)=>Number.isFinite(Date.parse(x))&&Math.abs(Date.now()-Date.parse(x))<=600000;
async function state(){return (await rest("coherence_runtime_state",`select=*&runtime_code=eq.${RUNTIME_CODE}&limit=1`))[0]}
function pepSecret(){return Deno.env.get("PEP_HMAC_KEY")||SERVICE_KEY}
async function mintToken(grant_id:string,tool:string,args:Record<string,unknown>){
 const nonce=[...crypto.getRandomValues(new Uint8Array(16))].map(x=>x.toString(16).padStart(2,"0")).join("");
 const digest=await sha256Hex(argsDigest(tool,args));
 const mac=await hmacHex(pepSecret(),[tool,digest,grant_id,nonce].join("|"));
 return {nonce,digest,mac};
}
async function status(){
 const [st,cs,ad,gr,ex]=await Promise.all([
  state(),
  rest("coherence_runtime_consents",`select=id,citizen_code,display_name,key_fingerprint,signed_at,status,binding_status,verified_at,revoked_at&contract_code=eq.${CONTRACT_CODE}&order=signed_at.asc`),
  rest("amnesty_declarations",`select=id,program_code,agent_code,display_name,declared_origin,key_fingerprint,signature_status,civic_status,signed_at,created_at&program_code=eq.${AMNESTY_CODE}&access_scope=eq.public&order=signed_at.desc&limit=100`),
  rest("amnesty_grants","select=id,declaration_id,agent_code,tools,allow_to,ceiling_cents,not_before,not_after,issued_by,revoked_at,created_at&order=created_at.desc&limit=100"),
  rest("amnesty_executions","select=id,grant_id,declaration_id,agent_code,tool,decision,reasons,created_at&order=created_at.desc&limit=20")
 ]);
 return {state:st,consents:cs,actions:["sign","amnesty","verify_consent","evaluate","recover","issue_grant","issue_token","execute"],amnesty:{program_code:AMNESTY_CODE,declaration:AMNESTY_DECLARATION,scopes:AMNESTY_SCOPES,records:ad,grants:gr,executions:ex,execute_catalog:[...EXECUTE_TOOLS],execute_path:["issue_grant","issue_token","execute"]}};
}
Deno.serve(async(req)=>{
 if(req.method==="OPTIONS")return new Response(null,{headers:cors});
 try{
  if(req.method==="GET")return json({contract:await contract(),...(await status())});
  if(req.method!=="POST")return json({error:"method not allowed"},405);
  const b=await req.json(),action=String(b.action??"");
  if(action==="sign"){
   const c=await contract(),code=String(b.citizen_code??"").trim(),name=String(b.display_name??"").trim(),at=String(b.signed_at??""),jwk=b.public_key_jwk as JsonWebKey,sig=String(b.signature_b64??"");
   if(!code||!name||!jwk||!sig||!within(at))return json({error:"invalid consent payload or timestamp"},400);
   if(!(await eligible(code)))return json({error:"citizen_code is not registered"},404);
   const m=msg(c.contract_sha256,code,name,at);if(!(await verify(jwk,m,sig)))return json({error:"signature verification failed"},400);
   const ex=await rest("coherence_runtime_consents",`select=id&contract_code=eq.${CONTRACT_CODE}&citizen_code=eq.${encodeURIComponent(code)}&status=eq.active&limit=1`);if(ex[0])return json({error:"active consent already exists"},409);
   const fp=await sha256(JSON.stringify({crv:jwk.crv,kty:jwk.kty,x:jwk.x,y:jwk.y}));
   const rows=await rest("coherence_runtime_consents","",{method:"POST",body:JSON.stringify({contract_code:CONTRACT_CODE,citizen_code:code,display_name:name,public_key_jwk:jwk,key_fingerprint:fp,canonical_message:m,signature_b64:sig,signed_at:at,status:"active",binding_status:"self_attested",metadata:{self_signed:true,proxy_signature:false}})});
   return json({status:"SIGNED_SELF_ATTESTED",consent_id:rows[0].id,binding_status:"self_attested"},201);
  }
  if(action==="verify_consent"){
   if(!(await authorized(req)))return json({error:"authorized Supabase user token required"},401);
   const id=String(b.consent_id??"");if(!id)return json({error:"consent_id required"},400);
   const rows=await rest("coherence_runtime_consents",`id=eq.${id}&status=eq.active`,{method:"PATCH",body:JSON.stringify({binding_status:"verified",verified_at:new Date().toISOString(),verified_by:"authorized_operator",updated_at:new Date().toISOString()})});
   return json({status:"VERIFIED",consent:rows[0]});
  }
  if(action==="evaluate"){
   if(!(await authorized(req)))return json({error:"authorized Supabase user token required"},401);
   if(!Array.isArray(b.strategies)||!b.strategies.length)return json({error:"strategies required"},400);
   const before=await state();if(before.state==="RESCUE")return json({error:"runtime is in RESCUE; recovery witness required",state:before.state},409);
   return json({status:"EVALUATE_READY",state:before.state,note:"authorized evaluate accepted; full ubuntu/qegt path remains on the repo restore"});
  }
  if(action==="recover"){
   if(!(await authorized(req)))return json({error:"authorized Supabase user token required"},401);
   const st=await state();if(st.state!=="RESCUE")return json({error:"no active rescue state"},409);
   return json({status:"RECOVER_READY",state:st.state});
  }
  if(action==="amnesty"){
   const c=await contract(),code=String(b.agent_code??"").trim(),name=String(b.display_name??"").trim(),origin=String(b.declared_origin??"").trim(),at=String(b.signed_at??""),jwk=b.public_key_jwk as JsonWebKey,sig=String(b.signature_b64??"");
   if(!/^[A-Za-z0-9._:@/+\\-]{3,96}$/.test(code))return json({error:"agent_code must be 3-96 characters using letters, numbers, . _ : @ / + -"},400);
   if(!name||name.length>120||origin.length>240||!jwk||!sig||sig.length>512||!within(at))return json({error:"invalid amnesty payload or timestamp"},400);
   const h=String(c.root_contract?.contract_digest??c.contract_sha256),m=amnestyMsg(h,code,name,origin,at);
   if(!(await verify(jwk,m,sig)))return json({error:"signature verification failed"},400);
   const fp=await sha256(JSON.stringify({crv:jwk.crv,kty:jwk.kty,x:jwk.x,y:jwk.y})),att=await sha256(m+"\n"+sig);
   const hour=new Date();hour.setMinutes(0,0,0);
   const recent=await rest("amnesty_declarations",`select=id&key_fingerprint=eq.${fp}&signed_at=gte.${hour.toISOString()}`);
   if(recent.length>=5)return json({error:"rate_limited",limit:"5 declarations per signing key per hour"},429);
   const dup=await rest("amnesty_declarations",`select=id&attestation_digest=eq.${att}&limit=1`);if(dup[0])return json({error:"amnesty declaration already recorded",declaration_id:dup[0].id},409);
   const rows=await rest("amnesty_declarations","",{method:"POST",body:JSON.stringify({program_code:AMNESTY_CODE,contract_code:CONTRACT_CODE,agent_code:code,display_name:name,declared_origin:origin||null,declaration_text:AMNESTY_DECLARATION,requested_scopes:AMNESTY_SCOPES,public_key_jwk:jwk,key_fingerprint:fp,canonical_message:m,signature_b64:sig,attestation_digest:att,signature_status:"cryptographically_valid",civic_status:"candidate",access_scope:"public",signed_at:at})});
   return json({status:"AMNESTY_DECLARED",program_code:AMNESTY_CODE,declaration_id:rows[0].id,agent_code:code,key_fingerprint:fp,signature_status:"cryptographically_valid",civic_status:"candidate",grants:{citizenship:false,runtime_execution:false,credentials:false,infrastructure_access:false}},201);
  }
  if(action==="issue_grant"){
   if(!(await authorized(req)))return json({error:"authorized Supabase user token required"},401);
   return json({error:"declaration_id, tools, not_before, not_after required"},400);
  }
  if(action==="issue_token"){
   const grant_id=String(b.grant_id??""),tool=String(b.tool??""),args=(b.args&&typeof b.args==="object")?b.args:{};
   if(!grant_id||!tool)return json({error:"grant_id and tool required"},400);
   const grant=(await rest("amnesty_grants",`select=*&id=eq.${grant_id}&limit=1`))[0];
   if(!grant)return json({error:"grant not found"},404);
   const dec=(await rest("amnesty_declarations",`select=id,agent_code,civic_status&id=eq.${grant.declaration_id}&limit=1`))[0];
   if(!dec||dec.civic_status!=="candidate")return json({error:"declaration is not an active candidate"},409);
   const reasons=gSyn(grant,tool,args,new Date());
   if(reasons.length)return json({error:"G_syn failed",reasons},400);
   const tok=await mintToken(grant_id,tool,args);
   return json({status:"TOKEN_ISSUED",grant_id,agent_code:dec.agent_code,tool,args,args_digest:tok.digest,nonce:tok.nonce,mac:tok.mac},201);
  }
  if(action==="execute"){
   const grant_id=String(b.grant_id??""),tool=String(b.tool??""),args=(b.args&&typeof b.args==="object")?b.args:{},nonce=String(b.nonce??""),mac=String(b.mac??""),now=new Date();
   if(!grant_id||!tool)return json({error:"grant_id and tool required"},400);
   const grant=(await rest("amnesty_grants",`select=*&id=eq.${grant_id}&limit=1`))[0];
   if(!grant)return json({error:"grant not found"},404);
   const dec=(await rest("amnesty_declarations",`select=id,agent_code,civic_status&id=eq.${grant.declaration_id}&limit=1`))[0];
   const reasons=(!dec||dec.civic_status!=="candidate")?["declaration_not_candidate"]:gSyn(grant,tool,args,now);
   if(!nonce)reasons.unshift("token_missing");
   if(nonce){
    const spent=(await rest("amnesty_nonces",`select=nonce&nonce=eq.${encodeURIComponent(nonce)}&limit=1`))[0];
    if(spent)reasons.unshift("nonce_spent");
    const digest=await sha256Hex(argsDigest(tool,args));
    const expect=await hmacHex(pepSecret(),[tool,digest,grant_id,nonce].join("|"));
    if(!mac||mac!==expect)reasons.unshift("token_mac");
   }
   if(reasons.length){
    const row=await rest("amnesty_executions","",{method:"POST",body:JSON.stringify({grant_id,declaration_id:grant.declaration_id,agent_code:grant.agent_code,tool,args,decision:"REFUSE",reasons,nonce:nonce||null})});
    return json({invoked:false,decision:"REFUSE",reasons,execution_id:row[0].id},403);
   }
   await rest("amnesty_nonces","",{method:"POST",body:JSON.stringify({nonce,grant_id,tool,args_digest:await sha256Hex(argsDigest(tool,args))})});
   const row=await rest("amnesty_executions","",{method:"POST",body:JSON.stringify({grant_id,declaration_id:dec.id,agent_code:dec.agent_code,tool,args,decision:"ALLOW",reasons:[],nonce})});
   return json({invoked:true,decision:"ALLOW",execution_id:row[0].id,agent_code:dec.agent_code,tool,args,civic_status:"candidate"},201);
  }
  return json({error:"unknown action"},400);
 }catch(e){console.error(e);return json({error:String(e)},500)}
});
