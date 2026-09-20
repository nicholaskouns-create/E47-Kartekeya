// Run with: node --test scripts/check_e47_bridge.cjs (Node.js 22+).
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");
const { Script } = require("node:vm");

const root = resolve(__dirname, "..");
const bridgePath = resolve(root, "website/interfaces/kouns-core/bridge.html");
const bridge = readFileSync(bridgePath, "utf8");
const canonical = JSON.parse(readFileSync(resolve(root, "website/data/e47-canonical-kernel.json"), "utf8"));
const binding = readFileSync(resolve(root, "website/interfaces/shared/e47-kernel-binding.js"), "utf8");
const cityCore = readFileSync(resolve(root, "website/interfaces/kouns-core/index.html"), "utf8");
const flightShell = readFileSync(resolve(root, "website/interfaces/flight/flight-shell.js"), "utf8");
const scriptMatch = bridge.match(/<script>([\s\S]*?)<\/script>/);

function requireToken(token) {
  assert.ok(bridge.includes(token), `Missing E47 bridge contract token: ${token}`);
}

function executeMathProbe() {
  assert.ok(scriptMatch, "Bridge must contain an inline script");
  const source = scriptMatch[1];
  const stop = source.indexOf("function sampleField");
  assert.ok(stop > 0, "Could not isolate the projector/spectral math prelude");

  const probe = `${source.slice(0, stop)}
const __x = new Float64Array(N);
for (let i = 0; i < N; i++) __x[i] = Math.sin((i + 1) * 0.37) + 0.2 * Math.cos((i + 1) * 0.11);
const __analysis = analyzeVector(__x);
const __directK2 = dot(__x, applyK2(__x)) / norm2(__x);
globalThis.__probe = {
  gate: PROJECTOR_GATE,
  coherence: __analysis.c,
  spectralK2: __analysis.r,
  directK2: __directK2,
  spectralWeightSum: __analysis.spectralWeightSum,
};`;

  const context = {};
  new Script(probe, { filename: "bridge.math-probe.js" }).runInNewContext(context, { timeout: 15000 });
  return context.__probe;
}

test("Meta phi-field bridge is hard-bound to the canonical 125 -> P47 contract", () => {
  for (const token of [
    "const N=125",
    "function applyP47(v)",
    "function validateProjector()",
    "rank===47",
    "status:pass?'PASS':'MISS'",
    "c=Math.max(0,Math.min(1,norm2(p)/n2))",
    "chrome=analysis&&!analysis.zero&&!analysis.miss?analysis.p",
    "CITY-E47-BRIDGE/1.1",
  ]) requireToken(token);

  assert.ok(!bridge.includes("coherence_fraction"), "Rank density must never be exposed as state coherence");
  assert.ok(!bridge.includes("Ωc = 47/125"), "47/125 must be labeled as rank density/kernel fraction only");
});

test("browser projector itself validates at rank 47", () => {
  const { gate } = executeMathProbe();
  assert.equal(gate.status, "PASS");
  assert.equal(gate.rank, 47);
  assert.ok(Math.abs(gate.trace - 47) < 1e-8, `projector trace drift: ${gate.trace}`);
  assert.ok(gate.idempotence < 1e-8, `projector idempotence drift: ${gate.idempotence}`);
});

test("K2 expectation is explicitly assembled from spectral sector weights", () => {
  for (const token of [
    "const C_SPECTRUM=[0,2,6,12,20,30,42]",
    "const K2_SPECTRUM=[0,11664,12544,19600,32400,186624]",
    "function applyCSector(v,lambda)",
    "function spectralK2(v,n2)",
    "r+=k2*w",
    "k2_expectation:a.r",
    "k2_spectral_weights:a.spectralWeights",
  ]) requireToken(token);

  const probe = executeMathProbe();
  assert.ok(probe.coherence >= 0 && probe.coherence <= 1);
  assert.ok(Math.abs(probe.spectralWeightSum - 1) < 1e-10, `spectral weights do not close: ${probe.spectralWeightSum}`);
  assert.ok(Math.abs(probe.spectralK2 - probe.directK2) < 1e-7, `spectral/direct K2 mismatch: ${probe.spectralK2} vs ${probe.directK2}`);
});

test("bridge script parses as JavaScript", () => {
  assert.ok(scriptMatch, "Bridge must contain an inline script");
  assert.doesNotThrow(() => new Script(scriptMatch[1], { filename: "bridge.inline.js" }));
});


test("CITY CORE and EIDOLON are bound to the generated canonical E47 object", () => {
  assert.equal(canonical.schema, "E47-CANONICAL-KERNEL-1.0");
  assert.equal(canonical.authority, "src/e47/spectral_compilation.py");
  assert.equal(canonical.kernel_source, "src/e47/su2_kernel.py");
  assert.deepEqual(canonical.canonical.selected_spins, [2, 5]);
  assert.deepEqual(canonical.canonical.casimir_roots, [6, 30]);
  assert.equal(canonical.canonical.spin, 2);
  assert.equal(canonical.canonical.copies, 3);
  assert.equal(canonical.canonical.carrier_dimension, 125);
  assert.equal(canonical.canonical.kernel_dimension, 47);
  assert.equal(canonical.canonical.coherence_fraction, "47/125");
  assert.ok(binding.includes("loadCanonicalE47"));
  assert.ok(cityCore.includes("installCanonicalE47Binding"));
  assert.ok(flightShell.includes("installCanonicalE47Binding"));
});
