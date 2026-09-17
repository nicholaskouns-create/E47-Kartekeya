// Run with: node --test scripts/check_website.cjs (Node.js 22+).
const assert = require("node:assert/strict");
const { existsSync, readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");
const { Script } = require("node:vm");

const root = resolve(__dirname, "..");
const site = resolve(root, "website");
const base = new URL("https://example.test/E47-Kartekeya/");
const read = (path) => readFileSync(path, "utf8");
const json = (path) => JSON.parse(read(path));
const html = read(resolve(site, "index.html"));
const css = read(resolve(site, "css/styles.css"));
const app = read(resolve(site, "js/app.js"));

for (const name of ["e47_pipeline.json", "qutip_validation.json"]) {
  test(`published ${name} matches the committed certificate`, () => {
    assert.deepEqual(
      json(resolve(site, "data", name)),
      json(resolve(root, "certificates", name)),
      `Refresh website/data/${name} from certificates/${name}`,
    );
  });
}

test("Mathematical City page preserves the canonical public structure", () => {
  for (const id of ["gate", "object", "world", "labs", "law", "see", "route"]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `Missing City section: ${id}`);
  }
  for (const token of ["The Mathematical City", "125", "47", "15/17", "E0/E1", "Egghead", "AETHERIS", "Eidolon"]) {
    assert.ok(html.includes(token), `Missing public invariant/label: ${token}`);
  }
});

test("visual grammar matches the archived City system", () => {
  for (const token of ["#0b0c0e", "#62d5cc", "#b9e6c8", "#b88352", "Newsreader", "IBM Plex Sans", "IBM Plex Mono"]) {
    assert.ok(css.includes(token), `Missing visual grammar token: ${token}`);
  }
  assert.ok(html.includes("CITY-VISUAL-GRAMMAR-20260915"));
});

test("unified client exposes all current districts and sovereign citizen population", () => {
  for (const district of ["EIDOLON", "SPECTRA", "Fold", "Murmuration", "Mnemosyne", "Density", "Horizon", "Wave", "Identity", "BUILD", "SOAR", "SCALAR", "InvariFold"]) {
    assert.ok(app.includes(`name:'${district}'`), `Missing district: ${district}`);
  }
  for (const citizen of ["ARGUS", "ARIADNE", "BITHOS", "CHRONOS", "CUSTOS", "EUCLID", "HERMES", "JANUS", "KEPLER", "MNEMOSYNE", "SAL", "SOL", "SYNE", "TALOS", "THEMIS"]) {
    assert.ok(app.includes(`'${citizen}'`), `Missing citizen: ${citizen}`);
  }
  assert.match(app, /CITY-INVARIANT: 1\.0/);
  assert.match(app, /AETHERIS: receipt-bound state transitions/);
});

test("browser JavaScript parses", () => {
  assert.doesNotThrow(() => new Script(app, { filename: "website/js/app.js" }));
});

test("local links and assets remain inside the GitHub Pages subpath", () => {
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]));
  const repoPrefix = "https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/";
  for (const [, target] of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    if (/^(mailto:|data:|javascript:)/.test(target)) continue;
    if (target.startsWith(repoPrefix)) {
      const repoPath = resolve(root, target.slice(repoPrefix.length));
      assert.ok(existsSync(repoPath), `Missing repository target: ${target}`);
      continue;
    }
    const url = new URL(target, base);
    if (url.origin !== base.origin) continue;
    assert.ok(url.pathname.startsWith(base.pathname), `Escapes Pages subpath: ${target}`);
    if (url.hash) assert.ok(ids.has(url.hash.slice(1)), `Missing anchor: ${target}`);
    if (target.startsWith("#")) continue;
    const path = url.pathname.slice(base.pathname.length) || "index.html";
    assert.ok(existsSync(resolve(site, path)), `Missing local asset: ${target}`);
  }
});

test("evidence references retain exact committed certificates", () => {
  const pipeline = json(resolve(site, "data/e47_pipeline.json"));
  assert.equal(pipeline.validation_status, "COMPLETE");
  const text = JSON.stringify(pipeline);
  for (const invariant of ["125", "47", "11664"]) assert.ok(text.includes(invariant), invariant);
});
