import {E47_LOCK, DIM_E47, N, OMEGA_C} from "./e47-lock.js";

export function loadCanonicalE47() {
  const k = E47_LOCK.canonical;
  const pass =
    E47_LOCK.schema === "E47-CANONICAL-KERNEL-1.0" &&
    E47_LOCK.authority === "src/e47/spectral_compilation.py" &&
    E47_LOCK.kernel_source === "src/e47/su2_kernel.py" &&
    k?.spin === 2 &&
    k?.copies === 3 &&
    JSON.stringify(k?.selected_spins) === "[2,5]" &&
    JSON.stringify(k?.casimir_roots) === "[6,30]" &&
    k?.carrier_dimension === N &&
    k?.kernel_dimension === DIM_E47 &&
    k?.coherence_fraction === "47/125";
  if (!pass) throw new Error("E47 canonical kernel contract MISS");
  return E47_LOCK;
}

export async function installCanonicalE47Binding({ surface = "CITY", container = null, postTarget = null } = {}) {
  const chip = container ? document.createElement("span") : null;
  if (chip) {
    chip.className = "chip";
    chip.textContent = "E47 · BINDING";
    container.appendChild(chip);
  }
  try {
    const contract = loadCanonicalE47();
    window.CITY_E47_CANONICAL = contract;
    document.dispatchEvent(new CustomEvent("city:e47-bound", { detail: { surface, contract } }));
    postTarget?.contentWindow?.postMessage?.({ type: "CITY_E47_CANONICAL", surface, contract }, "*");
    if (chip) {
      chip.classList.add("live");
      chip.textContent = `E47 · BOUND · ${contract.canonical.coherence_fraction}`;
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

export {E47_LOCK, OMEGA_C, N, DIM_E47};
