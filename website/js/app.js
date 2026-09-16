(() => {
  "use strict";

  const pipelineRoot = document.getElementById("pipeline-root");
  const statusBar = document.getElementById("status-bar");

  function escapeHtml(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#39;");
  }

  function stageMeta(stage) {
    if (stage.dimension != null) return `dim ${stage.dimension}`;
    if (stage.kernel_dimension != null) return `ker dim ${stage.kernel_dimension}`;
    if (stage.spectral_gap != null) return `gap ${stage.spectral_gap}`;
    if (stage.coherence_fraction != null) return `Ω ${stage.coherence_fraction}`;
    if (stage.operator) return stage.operator;
    if (stage.equation) return stage.equation;
    if (stage.map) return stage.map;
    if (stage.property) return stage.property;
    return "";
  }

  function renderPipeline(data) {
    if (!pipelineRoot || !data || !Array.isArray(data.pipeline)) return;

    const stages = data.pipeline
      .map((stage) => {
        const ok = stage.validated ? '<span class="stage-ok">validated</span>' : "";
        const meta = escapeHtml(stageMeta(stage));
        return `
          <article class="pipeline-stage">
            <div class="stage-badge">${escapeHtml(stage.stage || "?")}</div>
            <div class="stage-body">
              <h3>${escapeHtml(stage.name || "Stage")}</h3>
              <p>${escapeHtml(stage.role || stage.computation || "")}</p>
            </div>
            <div class="stage-meta">
              ${ok}
              <div>${meta}</div>
            </div>
          </article>
        `;
      })
      .join("");

    pipelineRoot.innerHTML = stages;
  }

  function renderStatus(pipeline, qutip) {
    if (!statusBar) return;

    const pills = [];

    if (pipeline && pipeline.validation_status) {
      const pass = String(pipeline.validation_status).toUpperCase() === "COMPLETE";
      pills.push(
        `<span class="pill ${pass ? "pass" : ""}"><span class="dot"></span> Pipeline: ${escapeHtml(pipeline.validation_status)}</span>`
      );
      if (pipeline.timestamp) {
        pills.push(
          `<span class="pill">Timestamp: ${escapeHtml(pipeline.timestamp)}</span>`
        );
      }
    } else {
      pills.push(`<span class="pill"><span class="dot"></span> Pipeline: unavailable</span>`);
    }

    if (qutip) {
      const status = qutip.status || "unknown";
      const pass = String(status).toLowerCase() === "pass";
      pills.push(
        `<span class="pill ${pass ? "pass" : ""}"><span class="dot"></span> QuTiP cert: ${escapeHtml(status)}</span>`
      );
      if (qutip.results) {
        const r = qutip.results;
        if (r.carrier_dimension != null) {
          pills.push(`<span class="pill">dim(V)=${escapeHtml(r.carrier_dimension)}</span>`);
        }
        if (r.kernel_dimension != null) {
          pills.push(`<span class="pill">dim(E₄₇)=${escapeHtml(r.kernel_dimension)}</span>`);
        }
        if (r.coherence_fraction_exact) {
          pills.push(`<span class="pill">Ω=${escapeHtml(r.coherence_fraction_exact)}</span>`);
        } else if (r.coherence_fraction != null) {
          pills.push(`<span class="pill">Ω=${escapeHtml(r.coherence_fraction)}</span>`);
        }
        if (r.spectral_gap != null) {
          pills.push(`<span class="pill">gap=${escapeHtml(r.spectral_gap)}</span>`);
        }
      }
    } else {
      pills.push(`<span class="pill"><span class="dot"></span> QuTiP cert: unavailable</span>`);
    }

    statusBar.innerHTML = pills.join("");
  }

  async function loadJson(path) {
    const response = await fetch(path, { cache: "no-cache" });
    if (!response.ok) {
      throw new Error(`Failed to load ${path}: ${response.status}`);
    }
    return response.json();
  }

  async function boot() {
    let pipeline = null;
    let qutip = null;

    try {
      pipeline = await loadJson("data/e47_pipeline.json");
      renderPipeline(pipeline);
    } catch (error) {
      console.warn(error);
      if (pipelineRoot) {
        pipelineRoot.innerHTML = `
          <article class="pipeline-stage">
            <div class="stage-badge">!</div>
            <div class="stage-body">
              <h3>Pipeline data unavailable</h3>
              <p>Could not load certificates/e47_pipeline.json into the site data folder.</p>
            </div>
            <div class="stage-meta"></div>
          </article>
        `;
      }
    }

    try {
      qutip = await loadJson("data/qutip_validation.json");
    } catch (error) {
      console.warn(error);
    }

    renderStatus(pipeline, qutip);
  }

  // Active section highlighting
  function setupNavHighlight() {
    const links = Array.from(document.querySelectorAll(".nav-links a"));
    const sections = links
      .map((link) => {
        const id = link.getAttribute("href");
        if (!id || !id.startsWith("#")) return null;
        const el = document.querySelector(id);
        return el ? { link, el } : null;
      })
      .filter(Boolean);

    if (!sections.length || !("IntersectionObserver" in window)) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          const match = sections.find((s) => s.el === entry.target);
          if (!match) return;
          links.forEach((l) => l.classList.remove("active"));
          match.link.classList.add("active");
        });
      },
      { rootMargin: "-35% 0px -55% 0px", threshold: 0.01 }
    );

    sections.forEach(({ el }) => observer.observe(el));
  }

  boot();
  setupNavHighlight();
})();
