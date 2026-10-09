export const CITY_GRAPHICS_CONTRACT = Object.freeze({
  contract: "CITY-GRAPHICS-ACCELERATOR-1.0",
  canonicalGrammar: "CITY-INVARIANT 1.0",
  invariant:
    "Rendering acceleration must not alter solver timestep, state-transition law, deterministic seed, evidence class, provenance, or scientific outputs.",
  backends: ["webgpu", "webgl2", "webgl1", "canvas2d"],
  boundary:
    "Performance/runtime contract only. It does not validate physical models or promote evidence class.",
});

function canvasBackend() {
  if (typeof document === "undefined") return "canvas2d";
  const c = document.createElement("canvas");
  if (c.getContext("webgl2")) return "webgl2";
  if (c.getContext("webgl") || c.getContext("experimental-webgl")) return "webgl1";
  return "canvas2d";
}

export async function detectCityGraphicsCapabilities() {
  const caps = {
    webgpu: Boolean(globalThis.navigator?.gpu),
    backend: canvasBackend(),
    offscreenCanvas: "OffscreenCanvas" in globalThis,
    worker: "Worker" in globalThis,
    wasm: "WebAssembly" in globalThis,
    hardwareConcurrency: globalThis.navigator?.hardwareConcurrency ?? null,
    deviceMemory: globalThis.navigator?.deviceMemory ?? null,
    dpr: globalThis.devicePixelRatio || 1,
    secureContext: globalThis.isSecureContext === true,
  };

  if (caps.webgpu) {
    try {
      const adapter = await navigator.gpu.requestAdapter({ powerPreference: "high-performance" });
      caps.webgpu = Boolean(adapter);
      if (adapter) caps.backend = "webgpu";
    } catch {
      caps.webgpu = false;
    }
  }

  caps.tier = caps.backend === "webgpu" ? "ultra" : caps.backend === "webgl2" ? "high" : "compatible";
  return caps;
}

export function createAdaptiveFrameController(opts = {}) {
  const targetFps = opts.targetFps ?? 60;
  const targetMs = 1000 / targetFps;
  const minScale = opts.minScale ?? 0.55;
  const maxScale = opts.maxScale ?? 1;
  const dprCap = opts.dprCap ?? 2;
  let scale = maxScale;
  let ema = targetMs;
  let last = performance.now();

  return {
    sample(now = performance.now()) {
      const dt = Math.max(0.1, now - last);
      last = now;
      ema = ema * 0.9 + dt * 0.1;
      if (ema > targetMs * 1.18) scale = Math.max(minScale, scale - 0.04);
      else if (ema < targetMs * 0.88) scale = Math.min(maxScale, scale + 0.02);
      return scale;
    },
    pixelRatio() {
      return Math.min(globalThis.devicePixelRatio || 1, dprCap) * scale;
    },
    get scale() {
      return scale;
    },
    get frameMs() {
      return ema;
    },
  };
}

export function attachAdaptiveCanvas(canvas, opts = {}) {
  if (!(canvas instanceof HTMLCanvasElement)) throw new TypeError("canvas required");
  const controller = createAdaptiveFrameController(opts);
  const resize = () => {
    const rect = canvas.getBoundingClientRect();
    const pixelRatio = controller.pixelRatio();
    const width = Math.max(1, Math.floor(rect.width * pixelRatio));
    const height = Math.max(1, Math.floor(rect.height * pixelRatio));
    if (canvas.width !== width) canvas.width = width;
    if (canvas.height !== height) canvas.height = height;
    canvas.dataset.cityPixelRatio = String(pixelRatio);
  };
  const observer = "ResizeObserver" in globalThis ? new ResizeObserver(resize) : null;
  observer?.observe(canvas);
  resize();
  return { controller, resize, dispose: () => observer?.disconnect() };
}

export function createFixedStepLoop({ step, render, fixedDt = 1 / 60, maxCatchup = 5, controller = null }) {
  let running = false;
  let raf = 0;
  let last = 0;
  let accumulator = 0;

  const frame = (time) => {
    if (!running) return;
    if (!last) last = time;
    const elapsed = Math.min(0.25, (time - last) / 1000);
    last = time;

    if (typeof document !== "undefined" && document.hidden) {
      raf = requestAnimationFrame(frame);
      return;
    }

    accumulator += elapsed;
    let count = 0;
    while (accumulator >= fixedDt && count < maxCatchup) {
      step(fixedDt);
      accumulator -= fixedDt;
      count += 1;
    }

    controller?.sample(time);
    render(accumulator / fixedDt);
    raf = requestAnimationFrame(frame);
  };

  return {
    start() {
      if (!running) {
        running = true;
        last = 0;
        raf = requestAnimationFrame(frame);
      }
    },
    stop() {
      running = false;
      cancelAnimationFrame(raf);
    },
  };
}

export function transferCanvasToWorker(canvas, worker) {
  if (!canvas?.transferControlToOffscreen || !worker) return false;
  const offscreen = canvas.transferControlToOffscreen();
  worker.postMessage({ type: "CITY_OFFSCREEN_CANVAS", canvas: offscreen }, [offscreen]);
  return true;
}

export async function bootstrapCityGraphics(opts = {}) {
  const capabilities = await detectCityGraphicsCapabilities();
  const canvases = [
    ...document.querySelectorAll(opts.selector ?? "canvas[data-city-gpu],canvas.city-gpu"),
  ];
  const attachments = canvases.map((canvas) => attachAdaptiveCanvas(canvas, opts));
  const detail = { contract: CITY_GRAPHICS_CONTRACT, capabilities, attachments };
  globalThis.__CITY_GRAPHICS__ = detail;
  globalThis.dispatchEvent(new CustomEvent("citygraphicsready", { detail }));
  return detail;
}
