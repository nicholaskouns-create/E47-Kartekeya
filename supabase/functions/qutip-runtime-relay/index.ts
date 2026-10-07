import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SOURCE = "https://files.pythonhosted.org/packages/a7/22/6d27913df8f13f7d4151df6d5d55d8ab2e06fbf6e1134cb9bf7066ea917e/qutip-5.3.0-cp313-cp313-manylinux_2_24_x86_64.manylinux_2_28_x86_64.whl";
const TOKEN = Deno.env.get("FUNCTION_TOKEN") ?? "";

Deno.serve(async (req: Request) => {
  const presented = req.headers.get("x-function-token") ?? "";
  if (!TOKEN || presented !== TOKEN) {
    return new Response("Not found", { status: 404 });
  }
  const upstream = await fetch(SOURCE);
  if (!upstream.ok || !upstream.body) {
    return new Response(`Upstream failure: ${upstream.status}`, { status: 502 });
  }
  return new Response(upstream.body, {
    status: 200,
    headers: {
      "Content-Type": "application/zip",
      "Content-Disposition": "attachment; filename=qutip-5.3.0-cp313-manylinux.whl",
      "Cache-Control": "no-store",
      "X-Content-Type-Options": "nosniff"
    }
  });
});
