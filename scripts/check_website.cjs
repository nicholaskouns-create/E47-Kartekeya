// Run with: node --test scripts/check_website.cjs (Node.js 22+).
require('./check_skyrmion_runtime.cjs');
const assert = require("node:assert/strict");
const { existsSync, readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");
const { Script, runInNewContext } = require("node:vm");

const root = resolve(__dirname, "..");
const site = resolve(root, "website");
const base = new URL("https://example.test/E47-Kartekeya/");
const read = (path) => readFileSync(path, "utf8");
const json = (path) => JSON.parse(read(path));
const html = read(resolve(site, "index.html"));
const css = read(resolve(site, "css/styles.css"));
const app = read(resolve(site, "js/app.js"));
const visualizerPortalPath = resolve(site, "interfaces/visualizers/index.html");
const visualizerPortal = read(visualizerPortalPath);
const syntaxJacobApp = read(resolve(site, "interfaces/syntax-jacob/app.js"));

for (const name of ["e47_pipeline.json", "qutip_validation.json"]) {
  test(`published ${name} matches the committed certificate`, () => {
    assert.deepEqual(
      json(resolve(site, "data", name)),
      json(resolve(root, "certificates", name)),
      `Refresh website/data/${name} from certificates/${name}`
    );
  });
}

test("Syntax Jacob uses the server-side JPL truth proxy", () => {
  assert.match(syntaxJacobApp, /city-app-host\/syntax-jacob-ephemeris/);
  assert.match(syntaxJacobApp, /matrix-cube-adapter/);
  assert.match(syntaxJacobApp, /city-graphics-accelerator/);
  assert.doesNotMatch(syntaxJacobApp, /fetch\(['"]https:\/\/ssd(?:-api)?\.jpl\.nasa\.gov/);
});

test("homepage exposes the focused public entry architecture", () => {
  for (const id of ["flight", "labs", "proof"]) {
    assert.match(html, new RegExp(`id=["']${id}["']`), `Missing homepage section: ${id}`);
  }
  for (const token of [
    "The Mathematical City",
    "125",
    "47",
    "E0 / E1",
    "SKYRMION Runtime 2",
    "Syntax Jacob",
    "CITY CORE",
    "Canonical repository"
  ]) {
    assert.ok(html.includes(token), `Missing public invariant/entry: ${token}`);
  }
  for (const removed of ["district-orbit", "Egghead", "External Labs // Launch Network"]) {
    assert.ok(!html.includes(removed), `Legacy homepage clutter returned: ${removed}`);
  }
});

test("visual grammar remains coherent after homepage simplification", () => {
  for (const token of [
    "#090b0d",
    "#6edfd4",
    "#c1e8ce",
    "Newsreader",
    "IBM Plex Sans",
    "IBM Plex Mono"
  ]) {
    assert.ok(css.includes(token), `Missing visual grammar token: ${token}`);
  }
});

test("homepage routes flagship experiences directly", () => {
  for (const target of [
    'interfaces/skyrmion/',
    'interfaces/syntax-jacob/',
    'interfaces/kouns-core/?module=eidolon#flight',
    'interfaces/visualizers/'
  ]) {
    assert.ok(html.includes(`href="${target}"`), `Missing public route: ${target}`);
  }
});

test("visualizer portal retains the full research instrument set", () => {
  assert.ok(existsSync(visualizerPortalPath));
  for (const id of [
    "spectra", "fold", "murmuration", "mnemosyne", "density", "horizon",
    "wave", "identity", "build", "soar", "scalar", "invarifold"
  ]) {
    assert.ok(visualizerPortal.includes(`id:'${id}'`), `Visualizer portal missing instrument: ${id}`);
  }
  for (const token of ["VISUALIZER PORTAL", "OPEN ORIGINAL", "CITY CORE", "source visualizer is preserved unchanged"]) {
    assert.ok(visualizerPortal.includes(token), `Visualizer portal missing shell contract: ${token}`);
  }
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
      assert.ok(existsSync(resolve(root, target.slice(repoPrefix.length))), `Missing repository target: ${target}`);
      continue;
    }

    const url = new URL(target, base);
    if (url.origin !== base.origin) continue;
    assert.ok(url.pathname.startsWith(base.pathname), `Escapes Pages subpath: ${target}`);

    if (url.hash && target.startsWith("#")) {
      assert.ok(ids.has(url.hash.slice(1)), `Missing anchor: ${target}`);
      continue;
    }

    const path = url.pathname.slice(base.pathname.length) || "index.html";
    assert.ok(existsSync(resolve(site, path)), `Missing local asset: ${target}`);
  }
});

test("homepage JavaScript renders the curated lab index", () => {
  const grid = { innerHTML: "" };
  runInNewContext(app, {
    document: { getElementById: (id) => id === "lab-grid" ? grid : null }
  });

  assert.equal((grid.innerHTML.match(/class="lab-card"/g) || []).length, 9);
  for (const lab of ["SPECTRA", "Fold", "Murmuration", "Mnemosyne", "Density", "Horizon", "Wave", "InvariFold", "MANIFOLD"]) {
    assert.ok(grid.innerHTML.includes(lab), `Curated lab missing from homepage: ${lab}`);
  }
});

test("homepage lab routes stay inside the local visualizer portal", () => {
  for (const id of ["spectra", "fold", "murmuration", "mnemosyne", "density", "horizon", "wave", "invarifold"]) {
    assert.ok(app.includes(`interfaces/visualizers/?lab=${id}`), `Curated lab does not route through local portal: ${id}`);
  }
});

test("evidence references retain exact committed certificates", () => {
  const pipeline = json(resolve(site, "data/e47_pipeline.json"));
  assert.equal(pipeline.validation_status, "COMPLETE");
  assert.ok(Array.isArray(pipeline.pipeline));
  assert.ok(pipeline.pipeline.length >= 7);
  assert.ok(pipeline.pipeline.every((stage) => stage.validated === true));
  const text = JSON.stringify(pipeline);
  for (const invariant of ["125", "47", "11664"]) assert.ok(text.includes(invariant), invariant);
});

test("Syntax Jacob publishes runtime provenance", () => {
  const dir = resolve(site, "interfaces/syntax-jacob");
  const provenance = json(resolve(dir, "provenance.json"));
  assert.equal(provenance.original_work, true);
  assert.equal(provenance.e47.dimension, 125);
  assert.equal(provenance.e47.kernel_dimension, 47);
  const runtime = read(resolve(dir, "app.js"));
  for (const token of ["syntax-jacob-ephemeris", "matrix-cube-adapter", "aetheris.receipt", "1/99144"]) {
    assert.ok(runtime.includes(token), token);
  }
});
