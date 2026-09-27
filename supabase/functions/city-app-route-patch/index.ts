import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const BUCKET = "city-apps";
const SEE = "see";

Deno.serve(async (req: Request) => {
  if (req.method !== "POST" && req.method !== "GET") {
    return new Response("Method not allowed", { status: 405 });
  }
  return Response.json({
    service: "city-app-route-patch",
    status: "exported",
    note: "Canonical live source should be re-fetched if this stub is incomplete; see sync PR follow-ups.",
    bucket: BUCKET,
    suite: SEE,
  });
});
