import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
const H={"content-type":"application/json; charset=utf-8","cache-control":"no-store","access-control-allow-origin":"*","access-control-allow-headers":"authorization, content-type","access-control-allow-methods":"POST, OPTIONS"};
const R=(x:unknown,s=200)=>new Response(JSON.stringify(x),{status:s,headers:H});
Deno.serve(async(req:Request)=>{
  if(req.method==="OPTIONS")return new Response(null,{headers:H});
  if(req.method!=="POST")return R({error:"POST required"},405);
  const token=(req.headers.get("authorization")??"").replace(/^Bearer\s+/i,"");
  if(!token)return R({error:"authentication required"},401);
  const url=Deno.env.get("SUPABASE_URL")??"", key=Deno.env.get("SUPABASE_ANON_KEY")??"";
  if(!url||!key)return R({error:"runtime configuration unavailable"},500);
  const db=createClient(url,key,{global:{headers:{Authorization:`Bearer ${token}`}},auth:{persistSession:false}});
  const {data:{user},error:uerr}=await db.auth.getUser(token);
  if(uerr||!user)return R({error:"invalid authentication"},401);
  const {data:workspace,error:werr}=await db.from("city_workspaces").select("id,slug,name,created_by_user_id").eq("slug","mathematical-city").eq("created_by_user_id",user.id).maybeSingle();
  if(werr)return R({error:werr.message},500);if(!workspace)return R({error:"workspace not found"},404);
  const b=await req.json().catch(()=>({})), action=String(b.action??"list");
  if(action==="create"){
    const prompt=String(b.prompt??"").trim();if(!prompt)return R({error:"prompt required"},400);
    const query_code=String(b.query_code??`DENSITY-${Date.now().toString(36).toUpperCase()}`);
    const {data,error}=await db.from("city_query_tasks").insert({workspace_id:workspace.id,owner_user_id:user.id,query_code,title:String(b.title??"DENSITY query"),prompt,task_type:String(b.task_type??"density_tomography"),status:"queued",requested_sources:Array.isArray(b.requested_sources)?b.requested_sources:[],blind_sources:Array.isArray(b.blind_sources)?b.blind_sources:[],holdout_fraction:Number(b.holdout_fraction??.2),constraints:b.constraints??{},metadata:b.metadata??{}}).select("*").single();
    return error?R({error:error.message},500):R({task:data});
  }
  if(action==="list"){
    const {data,error}=await db.from("city_query_tasks").select("query_code,title,task_type,status,created_at,updated_at").eq("workspace_id",workspace.id).order("created_at",{ascending:false}).limit(100);
    return error?R({error:error.message},500):R({workspace:{slug:workspace.slug,name:workspace.name},tasks:data??[]});
  }
  if(action==="get"){
    const code=String(b.query_code??"");const {data:task,error}=await db.from("city_query_tasks").select("*").eq("workspace_id",workspace.id).eq("query_code",code).maybeSingle();
    if(error)return R({error:error.message},500);if(!task)return R({error:"task not found"},404);
    const {data:obs}=await db.from("city_query_observations").select("*").eq("task_id",task.id).order("id");
    const {data:rec}=await db.from("density_reconstructions").select("*").eq("task_id",task.id).order("created_at",{ascending:false});
    return R({task,observations:obs??[],reconstructions:rec??[]});
  }
  return R({error:"unknown action",allowed:["create","list","get"]},400);
});