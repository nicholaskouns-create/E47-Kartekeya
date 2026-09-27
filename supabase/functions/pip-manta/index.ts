import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const SOURCE = "https://raw.githubusercontent.com/nicholaskouns-create/E47-Kartekeya/main/website/interfaces/pip-manta/index.html";

Deno.serve(async (req: Request) => {
  if (req.method !== "GET" && req.method !== "HEAD") {
    return new Response("Method not allowed", { status: 405 });
  }
  const upstream = await fetch(SOURCE, { headers: { "accept": "text/html" } });
  if (!upstream.ok) {
    return new Response("PIP app source unavailable", { status: 502 });
  }
  const html = await upstream.text();
  return new Response(req.method === "HEAD" ? null : html, {
    status: 200,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "no-cache, no-store, must-revalidate",
      "access-control-allow-origin": "*",
      "x-content-type-options": "nosniff",
      "referrer-policy": "strict-origin-when-cross-origin",
      "content-security-policy": "default-src 'self' 'unsafe-inline' data: https:; connect-src https:; img-src 'self' data: https:; frame-ancestors *"
    }
  });
});
