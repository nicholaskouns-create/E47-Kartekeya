const SUPABASE_URL=Deno.env.get("SUPABASE_URL")!;
const SERVICE_KEY=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANON_KEY=Deno.env.get("SUPABASE_ANON_KEY")!;
const CONTRACT_CODE="CIRP-COHERENCE-RUNTIME-1.0";
const RUNTIME_CODE="COHERENCE-RUNTIME-1.0";
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
async function fingerprint(jwk:JsonWebKey){return sha256(JSON.stringify({crv:jwk.crv,kty:jwk.kty,x:jwk.x,y:jwk.y}))}
const msg=(h:string,c:string,n:string,t:string)=>["CIRP-CONSENT",`contract=${CONTRACT_CODE}`,`hash=${h}`,`citizen_code=${c}`,`display_name=${n}`,`signed_at=${t}`,"consent=true"].join("\n");
const within=(x:string)=>Number.isFinite(Date.parse(x))&&Math.abs(Date.now()-Date.parse(x))<=600000;
function ubuntu(s:any,active:Set<string>){
 const u=s.ubuntu??{},before=u.viability_before??{},after=u.viability_after??{},psi=u.psi_c??{},reasons:string[]=[];
 for(const p of Object.keys(before)){if(!active.has(p))reasons.push(`missing_verified_consent:${p}`);if(!(Number(psi[p])>0))reasons.push(`psi_c_not_positive:${p}`);if(!(p in after)||Number(after[p])<Number(before[p]))reasons.push(`viability_decreased:${p}`)}
 if(!(Number(u.recognition_threshold)>0))reasons.push("recognition_threshold_not_positive");else if(Number(u.recognition_residual)>Number(u.recognition_threshold))reasons.push("recognition_residual_exceeds_threshold");
 if(!(Number(u.joint_welfare_delta)>0))reasons.push("joint_welfare_not_positive");if(Number(u.harm_cost??0)>0)reasons.push("harm_cost_positive");if(u.admitted_coherence_sector!==true)reasons.push("outside_admitted_coherence_sector");
 return {passed:reasons.length===0,reasons};
}
function qegt(ss:any[],allowed:string[],beta=1){
 const a=ss.filter(s=>allowed.includes(s.name));if(!a.length)return null;const m=Math.min(...a.map(s=>Math.abs(Number(s.curvature))));
 const w=a.map(s=>({name:s.name,weight:Math.exp(-beta*(Math.abs(Number(s.curvature))-m))})),z=w.reduce((x,y)=>x+y.weight,0);
 const probabilities=Object.fromEntries(w.map(x=>[x.name,x.weight/z]));const selected=[...w].sort((x,y)=>(y.weight-x.weight)||x.name.localeCompare(y.name))[0].name;return {selected,probabilities};
}
async function state(){return (await rest("coherence_runtime_state",`select=*&runtime_code=eq.${RUNTIME_CODE}&limit=1`))[0]}
async function status(){
 const [st,cs,ri,qc]=await Promise.all([state(),rest("coherence_runtime_consents",`select=id,citizen_code,display_name,key_fingerprint,signed_at,status,binding_status,verified_at,revoked_at&contract_code=eq.${CONTRACT_CODE}&order=signed_at.asc`),rest("citizen_runtime_instances","select=instance_code,agent_code,runtime_state&order=agent_code.asc"),rest("quinary_citizens","select=id,identity,type&order=id.asc")]);
 return {state:st,consents:cs,eligible_citizens:{runtime:ri,quinary:qc}};
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
   const rows=await rest("coherence_runtime_consents","",{method:"POST",body:JSON.stringify({contract_code:CONTRACT_CODE,citizen_code:code,display_name:name,public_key_jwk:jwk,key_fingerprint:await fingerprint(jwk),canonical_message:m,signature_b64:sig,signed_at:at,status:"active",binding_status:"self_attested",metadata:{self_signed:true,proxy_signature:false}})});
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
   const strategies=Array.isArray(b.strategies)?b.strategies:[];if(!strategies.length)return json({error:"strategies required"},400);
   const before=await state();if(before.state==="RESCUE")return json({error:"runtime is in RESCUE; recovery witness required",state:before.state},409);
   const cs=await rest("coherence_runtime_consents",`select=citizen_code&contract_code=eq.${CONTRACT_CODE}&status=eq.active&binding_status=eq.verified`),active=new Set(cs.map((x:any)=>x.citizen_code));
   const results:any={},admissible:string[]=[];for(const s of strategies){const g=ubuntu(s,active);results[s.name]=g;if(g.passed)admissible.push(s.name)}
   const decision=qegt(strategies,admissible,Number(b.beta??1)),passed=Boolean(decision),reasons=Object.entries(results).flatMap(([n,r]:any)=>r.reasons.map((x:string)=>`${n}:${x}`)),after=passed?"COHERENT":"RESCUE";
   const ev=(await rest("coherence_runtime_evaluations","",{method:"POST",body:JSON.stringify({contract_code:CONTRACT_CODE,runtime_instance_code:b.runtime_instance_code??null,participant_codes:[...new Set(strategies.flatMap((s:any)=>Object.keys(s.ubuntu?.viability_before??{})))],strategies,ubuntu_results:results,qegt_distribution:decision?.probabilities??null,selected_strategy:decision?.selected??null,state_before:before.state,state_after:after,passed,incident_reasons:reasons})}))[0];
   if(passed){
 await rest("coherence_runtime_state",`runtime_code=eq.${RUNTIME_CODE}`,{method:"PATCH",body:JSON.stringify({state:"COHERENT",last_reason:"ubuntu_qegt_pass",updated_at:new Date().toISOString()})});
 if(before.state==="RECONCILING"){
   const open=await rest("coherence_runtime_incidents","select=id&state=eq.RECONCILING&order=opened_at.desc&limit=1");
   if(open[0])await rest("coherence_runtime_incidents",`id=eq.${open[0].id}`,{method:"PATCH",body:JSON.stringify({state:"RESOLVED",resolved_at:new Date().toISOString()})});
 }
 return json({status:"PASS",state:"COHERENT",evaluation_id:ev.id,qegt:decision,ubuntu:results})
}
   const inc=(await rest("coherence_runtime_incidents","",{method:"POST",body:JSON.stringify({contract_code:CONTRACT_CODE,source_evaluation_id:ev.id,trigger_code:"UBUNTU_GATE_FAIL",state:"OPEN",details:{reasons}})}))[0],sweep=`COHERENCE-RESCUE-${String(inc.id).slice(0,8).toUpperCase()}`;
   try{await rest("murmuration_sweeps","",{method:"POST",body:JSON.stringify({sweep_code:sweep,scope:"Coherence, Runtime 1.0",sol_route_status:"halted",schema_residual:1,provenance_residual:1,orphan_count:1,recombination_status:"rescue_requested",details:{incident_id:inc.id,trigger:"UBUNTU_GATE_FAIL",evidence_preserved:true},access_scope:"workspace"})})}catch(e){console.error("murmuration request failed",String(e))}
   await rest("coherence_runtime_incidents",`id=eq.${inc.id}`,{method:"PATCH",body:JSON.stringify({state:"MURMURATION_RESCUE",murmuration_sweep_code:sweep})});
   await rest("coherence_runtime_state",`runtime_code=eq.${RUNTIME_CODE}`,{method:"PATCH",body:JSON.stringify({state:"RESCUE",rescue_epoch:Number(before.rescue_epoch??0)+1,last_reason:reasons.join(";"),updated_at:new Date().toISOString()})});
   return json({status:"HALT",state:"RESCUE",incident_id:inc.id,sweep_code:sweep,reasons},409);
  }
  if(action==="recover"){
   if(!(await authorized(req)))return json({error:"authorized Supabase user token required"},401);
   const st=await state();if(st.state!=="RESCUE")return json({error:"no active rescue state"},409);
   const inc=(await rest("coherence_runtime_incidents","select=*&state=eq.MURMURATION_RESCUE&order=opened_at.desc&limit=1"))[0];
   if(!inc)return json({error:"no open rescue incident"},404);
   const sw=(await rest("murmuration_sweeps",`select=*&sweep_code=eq.${inc.murmuration_sweep_code}&limit=1`))[0];
   if(!sw)return json({error:"murmuration sweep not found"},404);
   const clean=Number(sw.schema_residual)===0&&Number(sw.provenance_residual)===0&&Number(sw.orphan_count)===0;
   if(!clean)return json({status:"NOT_REPAIRED",state:"RESCUE",sweep:sw},409);
   await rest("coherence_runtime_incidents",`id=eq.${inc.id}`,{method:"PATCH",body:JSON.stringify({state:"RECONCILING",repair_witness:{sweep_code:sw.sweep_code,schema_residual:sw.schema_residual,provenance_residual:sw.provenance_residual,orphan_count:sw.orphan_count}})});
   await rest("coherence_runtime_state",`runtime_code=eq.${RUNTIME_CODE}`,{method:"PATCH",body:JSON.stringify({state:"RECONCILING",last_reason:"murmuration_clean_reverify_required",updated_at:new Date().toISOString()})});
   return json({status:"REVERIFY_REQUIRED",state:"RECONCILING",sweep_code:sw.sweep_code});
  }
  return json({error:"unknown action"},400);
 }catch(e){console.error(e);return json({error:String(e)},500)}
});
