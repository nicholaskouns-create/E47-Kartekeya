import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
function key(){const r=Deno.env.get("SUPABASE_SECRET_KEYS");if(r)return JSON.parse(r).default;const l=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");if(l)return l;throw new Error("No secret key")}
const sb=createClient(Deno.env.get("SUPABASE_URL")!,key(),{auth:{persistSession:false,autoRefreshToken:false}});
const origin="https://orbit-coral-delta-fjord.grok.me";
const routes=["/registry","/suite"];
const ADMIN_HEADER="x-city-admin-token";
function pathFor(p:string){p=p.replace(/^\/+/,"");return `see/${p}/index.html`}
async function sha256(data:Uint8Array){return new Uint8Array(await crypto.subtle.digest("SHA-256",data))}
const hex=(b:Uint8Array)=>[...b].map(x=>x.toString(16).padStart(2,"0")).join("");
// Publishing requires CITY_ADMIN_TOKEN. Digests are compared in constant time; an unset secret refuses everyone.
async function adminAuthorized(req:Request){const expected=Deno.env.get("CITY_ADMIN_TOKEN")||"";const given=req.headers.get(ADMIN_HEADER)||"";if(!expected||!given)return false;const enc=new TextEncoder();const[a,b]=await Promise.all([sha256(enc.encode(expected)),sha256(enc.encode(given))]);let diff=0;for(let i=0;i<a.length;i++)diff|=a[i]^b[i];return diff===0}
Deno.serve(async(req)=>{if(!(await adminAuthorized(req)))return Response.json({error:`${ADMIN_HEADER} required`},{status:401});const out=[];for(const p of routes){const r=await fetch(origin+p,{redirect:"follow"});if(!r.ok){out.push({path:p,status:r.status});continue}const ct=(r.headers.get("content-type")||"text/html").split(";")[0];const buf=new Uint8Array(await r.arrayBuffer());const {error}=await sb.storage.from("city-apps").upload(pathFor(p),buf,{contentType:ct,upsert:true,cacheControl:"31536000"});if(error)throw error;out.push({path:p,status:r.status,bytes:buf.byteLength,sha256:hex(await sha256(buf))});}return Response.json({patched:out},{headers:{"cache-control":"no-store"}});});
