import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
function key(){const r=Deno.env.get("SUPABASE_SECRET_KEYS");if(r)return JSON.parse(r).default;const l=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");if(l)return l;throw new Error("No secret key")}
const sb=createClient(Deno.env.get("SUPABASE_URL")!,key(),{auth:{persistSession:false,autoRefreshToken:false}});
const origin="https://orbit-coral-delta-fjord.grok.me";
const routes=["/registry","/suite"];
function pathFor(p:string){p=p.replace(/^\/+/,"");return `see/${p}/index.html`}
Deno.serve(async()=>{const out=[];for(const p of routes){const r=await fetch(origin+p,{redirect:"follow"});if(!r.ok){out.push({path:p,status:r.status});continue}const ct=(r.headers.get("content-type")||"text/html").split(";")[0];const buf=new Uint8Array(await r.arrayBuffer());const {error}=await sb.storage.from("city-apps").upload(pathFor(p),buf,{contentType:ct,upsert:true,cacheControl:"31536000"});if(error)throw error;out.push({path:p,status:r.status,bytes:buf.byteLength});}return Response.json({patched:out});});
