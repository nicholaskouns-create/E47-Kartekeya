import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const TOKEN = Deno.env.get("FUNCTION_TOKEN") ?? "";
const EMAIL = Deno.env.get("OWNER_EMAIL") ?? "";
const SUPABASE_URL = Deno.env.get("SUPABASE_URL") ?? "";
const PUBLISHABLE_KEY = Deno.env.get("SUPABASE_ANON_KEY") ?? Deno.env.get("SUPABASE_PUBLISHABLE_KEY") ?? "";

Deno.serve(async (req: Request) => {
  const presented = req.headers.get("x-function-token") ?? "";
  if (!TOKEN || presented !== TOKEN) {
    return new Response("Unauthorized", { status: 401 });
  }
  const supabase = createClient(SUPABASE_URL, PUBLISHABLE_KEY, { auth: { persistSession: false, autoRefreshToken: false } });
  const { error } = await supabase.auth.signInWithOtp({ email: EMAIL, options: { shouldCreateUser: true } });
  if (error) return new Response(JSON.stringify({ ok:false, error:error.message }), { status: 500, headers: { "content-type":"application/json" } });
  return new Response(JSON.stringify({ ok:true, message:"Magic link sent. Open the email to complete authentication and owner bootstrap." }), { status: 200, headers: { "content-type":"application/json" } });
});
