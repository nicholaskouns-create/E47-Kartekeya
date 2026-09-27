const runtime = {
  source: "src/e47/recursive_runtime.py",
  github: "https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/src/e47/recursive_runtime.py",
  sha256: "8ec779cbb5247f9dc733cd2f4e341c8378d5ec6acfc21d56d9d3da33b322e716",
  cycle: "Σ → Ψ → Γ^n → Ω → Λ → Σ′ → α → Σ",
  gate_order: "Ω before Λ",
  gate: "||K M_pre|| <= tolerance",
  tolerance: 1e-10,
  contractions: 252,
  pre_projection_residual: 9.353585941533422e-11,
  post_projection_residual: 4.833244591885603e-12,
  certificate: "PASS"
};

const payload = {
  schema: "E47-RECURSIVE-NOTE-1.1",
  title: "E47 in Two Pages — K², V₂, Recursive Selection, and Residual-Gated Runtime",
  updated: "2026-09-23",
  exact: {
    carrier: "V = V_2^{⊗3}",
    dim_V2: 5,
    dim_carrier: 125,
    selector: "K=(C-6I)(C-30I)",
    positive_generator: "K^2=K†K",
    kernel_dim: 47,
    kernel_decomposition: "E_6 ⊕ E_30",
    omega_c: "47/125",
    epsilon_opt: "1/99144",
    complement_factor: "15/17",
    stability_interval: "0 < epsilon < 2/186624"
  },
  runtime,
  interpretation: "finite model of recursive invariant selection with residual-gated collapse",
  claim_boundary: [
    "47 is not asserted as a universal dimensionality of nature",
    "47/125 is a rank fraction of this construction, not a universal measured constant",
    "physical and domain applications require additional mappings and evidence"
  ],
  links: {
    github_pages: "https://nicholaskouns-create.github.io/E47-Kartekeya/notes/e47-recursive-system/",
    notion: "https://app.notion.com/p/3e446094fd30811ba779f8af95af5c02?pvs=204",
    github_note: "https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/docs/notes/e47-recursive-system.md",
    github_runtime: runtime.github,
    drive_certificate: "https://docs.google.com/document/d/1Ptf5GgT0bFM0VLrXlhQRPzvX7Bx1q8i5DQ8R9bp_hiU/edit?usp=drivesdk"
  }
};

const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>E47 Recursive Runtime</title>
<style>
body{margin:0;background:#06090b;color:#e8eef1;font:16px/1.6 system-ui,sans-serif}
main{max-width:920px;margin:auto;padding:48px 22px 80px}
section{background:#0d1317;border:1px solid #26343c;padding:28px;margin:24px 0}
h1{font-size:clamp(2.6rem,7vw,5.5rem);line-height:.95}h2{color:#9ce9c6}
code,.eq{font-family:ui-monospace,monospace}.eq{border-left:2px solid #c79a67;padding:12px 16px;background:#070b0d}
a{color:#69dff2}.pass{color:#9ce9c6}.muted{color:#9fb0b8}
</style></head><body><main>
<p class="muted">E47 Research · updated 2026-09-23</p>
<h1>E47 Recursive Runtime</h1>
<p>The locked 125→47 spectral object now has an explicit residual-gated execution cycle.</p>
<section><h2>Exact object</h2>
<div class="eq">K=(C−6I)(C−30I)<br>Γ=I−K²/99144<br>Λ=P₆+P₃₀<br>rank Λ=47 · Ωc=47/125 · ρ⊥=15/17</div></section>
<section><h2>Runtime</h2>
<div class="eq">Σ → Ψ → Γⁿ → Ω → Λ → Σ′ → α → Σ</div>
<p><strong>Ω is evaluated before Λ.</strong> The gate tests ||K M_pre||≤τ on the contracted state. Projection comes only after the bound is satisfied, avoiding the tautology KΛM≈0.</p>
<ul><li class="pass">certificate PASS</li><li>tolerance 1e−10</li><li>252 contractions</li><li>pre-projection residual 9.353585941533422e−11</li><li>post-projection residual 4.833244591885603e−12</li></ul>
<p><code>SHA-256 8ec779cbb5247f9dc733cd2f4e341c8378d5ec6acfc21d56d9d3da33b322e716</code></p></section>
<section><h2>Surfaces</h2>
<p><a href="${payload.links.github_pages}">GitHub Pages</a> · <a href="${payload.links.notion}">Notion</a> · <a href="${payload.links.github_runtime}">Runtime source</a> · <a href="${payload.links.drive_certificate}">Drive certificate</a></p></section>
</main></body></html>`;

Deno.serve((req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, {headers:{
      "Access-Control-Allow-Origin":"*",
      "Access-Control-Allow-Methods":"GET,OPTIONS",
      "Access-Control-Allow-Headers":"content-type,accept"
    }});
  }
  const url = new URL(req.url);
  const wantsJson = url.searchParams.get("format") === "json" ||
    (req.headers.get("accept") || "").includes("application/json");
  return new Response(wantsJson ? JSON.stringify(payload, null, 2) : html, {
    status: 200,
    headers: {
      "content-type": wantsJson ? "application/json; charset=utf-8" : "text/html; charset=utf-8",
      "cache-control": "public, max-age=300",
      "access-control-allow-origin": "*"
    }
  });
});