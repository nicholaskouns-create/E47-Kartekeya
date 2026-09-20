const DEFAULT_URL = new URL("../../data/e47-canonical-kernel.json", import.meta.url);

export async function loadCanonicalE47(url = DEFAULT_URL) {
  const response = await fetch(url, { cache: "no-store" });
  if (!response.ok) throw new Error(`E47 canonical kernel unavailable: HTTP ${response.status}`);
  const payload = await response.json();
  const k = payload?.canonical;
  const pass =
    payload?.schema === "E47-CANONICAL-KERNEL-1.0" &&
    payload?.authority === "src/e47/spectral_compilation.py" &&
    payload?.kernel_source === "src/e47/su2_kernel.py" &&
    k?.spin === 2 &&
    k?.copies === 3 &&
    JSON.stringify(k?.selected_spins) === "[2,5]" &&
    JSON.stringify(k?.casimir_roots) === "[6,30]" &&
    k?.carrier_dimension === 125 &&
    k?.kernel_dimension === 47 &&
    k?.coherence_fraction === "47/125";
  if (!pass) throw new Error("E47 canonical kernel contract MISS");
  return Object.freeze({ ...payload, canonical: Object.freeze({ ...k }) });
}

export async function installCanonicalE47Binding({ surface = "CITY", container = null, postTarget = null } = {}) {
  const chip = container ? document.createElement("span") : null;
  if (chip) {
    chip.className = "chip";
    chip.textContent = "E47 · BINDING";
    container.appendChild(chip);
  }
  try {
    const contract = await loadCanonicalE47();
    window.CITY_E47_CANONICAL = contract;
    document.dispatchEvent(new CustomEvent("city:e47-bound", { detail: { surface, contract } }));
    postTarget?.contentWindow?.postMessage?.({ type: "CITY_E47_CANONICAL", surface, contract }, "*");
    if (chip) {
      chip.classList.add("live");
      chip.textContent = "E47 · BOUND · 47/125";
    }
    return contract;
  } catch (error) {
    if (chip) {
      chip.classList.remove("live");
      chip.textContent = "E47 · MISS";
    }
    document.dispatchEvent(new CustomEvent("city:e47-miss", { detail: { surface, error: String(error) } }));
    throw error;
  }
}
