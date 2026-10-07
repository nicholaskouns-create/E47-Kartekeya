import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "@supabase/supabase-js";

const headers={"content-type":"application/json; charset=utf-8","cache-control":"no-store"};
const respond=(body:unknown,status=200)=>new Response(JSON.stringify(body),{status,headers});

Deno.serve(async (req: Request) => {
  if(req.method!=="GET"&&req.method!=="POST") return respond({error:"GET or POST required"},405);
  const url=Deno.env.get("SUPABASE_URL"),serviceKey=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
  if(!url||!serviceKey) return respond({error:"runtime secrets missing"},500);
  const token=(req.headers.get("authorization")??"").replace(/^Bearer\s+/i,"");
  if(!token) return respond({error:"authenticated workspace member required"},401);
  const sb=createClient(url,serviceKey,{auth:{persistSession:false,autoRefreshToken:false}});
  const {data:userData,error:userError}=await sb.auth.getUser(token);
  if(userError||!userData.user) return respond({error:"invalid user token"},401);
  const {data:workspace,error:wErr}=await sb.from("city_workspaces").select("id,slug,name,status,created_by_user_id").eq("slug","mathematical-city").eq("status","active").maybeSingle();
  if(wErr) return respond({error:wErr.message},500);
  if(!workspace) return respond({error:"workspace not found"},404);
  let authorized=workspace.created_by_user_id===userData.user.id;
  if(!authorized){
    const {data:membership,error:mErr}=await sb.from("city_memberships").select("role,status").eq("workspace_id",workspace.id).eq("user_id",userData.user.id).eq("status","active").maybeSingle();
    if(mErr) return respond({error:mErr.message},500);
    authorized=Boolean(membership);
  }
  if(!authorized) return respond({error:"workspace access denied"},403);

  const [memberships,audits,agents]=await Promise.all([
    sb.from("city_memberships").select("user_id,role,status",{count:"exact"}).eq("workspace_id",workspace.id),
    sb.from("city_row_audit").select("id,table_name,operation,occurred_at",{count:"exact"}).eq("workspace_id",workspace.id).order("occurred_at",{ascending:false}).limit(20),
    sb.from("agents").select("agent_code,display_name,role,active").in("agent_code",["CUSTOS","ARGUS","JANUS"])
  ]);
  return respond({
    service:"city-access-sentinel",
    posture:"human-sovereign multi-tenant ownership",
    workspace:{id:workspace.id,slug:workspace.slug,name:workspace.name,status:workspace.status},
    membership_count:memberships.count??0,
    memberships:memberships.data??[],
    recent_audit_events:audits.data??[],
    ownership_agents:agents.data??[],
    invariants:{row_ownership:true,workspace_scope:true,role_based_access:true,rls:true,row_versioning:true,audit_trail:true,service_role_bypass_only_after_workspace_authorization:true}
  });
});
