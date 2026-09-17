// Run with: node --test scripts/check_e47_bridge.cjs (Node.js 22+).
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");
const { Script } = require("node:vm");

const root = resolve(__dirname, "..");
const bridgePath = resolve(root, "website/interfaces/kouns-core/bridge.html");
const bridge = readFileSync(bridgePath, "utf8");
const scriptMatch = bridge.match(/<script>([\s\S]*?)<\/script>/);

function requireToken(token) {
  assert.ok(bridge.includes(token), `Missing E47 bridge contract token: ${token}`);
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
});

test("bridge script parses as JavaScript", () => {
  assert.ok(scriptMatch, "Bridge must contain an inline script");
  assert.doesNotThrow(() => new Script(scriptMatch[1], { filename: "bridge.inline.js" }));
});
