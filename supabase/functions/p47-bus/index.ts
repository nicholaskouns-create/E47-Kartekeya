import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const LOCK = {
  citizen: "P47-BUS-20260919",
  parent: "MC-P47-005",
  polynomial: "P47(C)=C(C-2)(C-12)(C-20)(C-31)(C-42)/1814400",
  kernel: "K=(C-6I)(C-30I)",
  flow: "rho_dot=-K^2 rho",
  dim_H: 125,
  dim_E47: 47,
  omega_c: 0.376,
  tr_P: 47,
  rank_K: 78,
  sockets: [
    "hilbert",
    "kernel",
    "flow",
    "discrete",
    "tomo_spatial",
    "tomo_hilbert",
    "eidolon",
    "city",
    "github",
    "supabase",
  ],
  lock: true,
};

Deno.serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "authorization, content-type" } });
  }
  return new Response(JSON.stringify(LOCK), {
    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" },
  });
});
