import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "@supabase/supabase-js";

Deno.serve(async (req: Request) => {
  const url = Deno.env.get("SUPABASE_URL")!;
  const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
  const sb = createClient(url, serviceKey, { auth: { persistSession: false } });

  const [workspaces, memberships, audits, agents] = await Promise.all([
    sb.from("city_workspaces").select("id,slug,name,status", { count: "exact" }),
    sb.from("city_memberships").select("workspace_id,user_id,role,status", { count: "exact" }),
    sb.from("city_row_audit").select("id,table_name,operation,occurred_at", { count: "exact" }).order("occurred_at", { ascending: false }).limit(20),
    sb.from("agents").select("agent_code,display_name,role,active").in("agent_code", ["CUSTOS","ARGUS","JANUS"])
  ]);

  const body = {
    service: "city-access-sentinel",
    posture: "human-sovereign multi-tenant ownership",
    workspaces: workspaces.data ?? [],
    membership_count: memberships.count ?? 0,
    memberships: memberships.data ?? [],
    recent_audit_events: audits.data ?? [],
    ownership_agents: agents.data ?? [],
    invariants: {
      row_ownership: true,
      workspace_scope: true,
      role_based_access: true,
      rls: true,
      row_versioning: true,
      audit_trail: true,
      service_role_bypass_for_orchestration: true,
      first_authenticated_user_becomes_workspace_owner: true
    }
  };
  return new Response(JSON.stringify(body), { headers: { "content-type": "application/json" } });
});