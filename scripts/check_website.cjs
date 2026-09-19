// Run with: node --test scripts/check_website.cjs (Node.js 22+).
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
    assert.deepEqual(json(resolve(site, "data", name)), json(resolve(root, "certificates", name)), `Refresh website/data/${name} from certificates/${name}`);
  });
}

test("Syntax Jacob uses the server-side JPL truth proxy", () => {
  assert.match(syntaxJacobApp, /city-app-host\/syntax-jacob-ephemeris/);
  assert.match(syntaxJacobApp, /matrix-cube-adapter/);
  assert.match(syntaxJacobApp, /city-graphics-accelerator/);
  assert.doesNotMatch(syntaxJacobApp, /fetch\(['"]https:\/\/ssd(?:-api)?\.jpl\.nasa\.gov/);
});

test("Mathematical City page preserves the canonical public structure", () => {
  for (const id of ["gate", "object", "world", "labs", "law", "see", "route"]) assert.match(html, new RegExp(`id=["']${id}["']`), `Missing City section: ${id}`);
  for (const token of ["The Mathematical City", "125", "47", "15/17", "E0/E1", "Egghead", "AETHERIS", "Eidolon"]) assert.ok(html.includes(token), `Missing public invariant/label: ${token}`);
});

test("visual grammar matches the archived City system", () => {
  for (const token of ["#0b0c0e", "#62d5cc", "#b9e6c8", "#b88352", "Newsreader", "IBM Plex Sans", "IBM Plex Mono"]) assert.ok(css.includes(token), `Missing visual grammar token: ${token}`);
  assert.ok(html.includes("CITY-VISUAL-GRAMMAR-20260915"));
});

test("unified client exposes all current districts and sovereign citizen population", () => {
  for (const district of ["SKYRMION", "Syntax Jacob", "SPECTRA", "Fold", "Murmuration", "Mnemosyne", "Density", "Horizon", "Wave", "Identity", "BUILD", "SOAR", "SCALAR", "InvariFold"]) assert.ok(app.includes(`name:'${district}'`), `Missing district: ${district}`);
  for (const citizen of ["ARGUS", "ARIADNE", "BITHOS", "CHRONOS", "CUSTOS", "EUCLID", "HERMES", "JANUS", "KEPLER", "MNEMOSYNE", "SAL", "SOL", "SYNE", "TALOS", "THEMIS"]) assert.ok(app.includes(`'${citizen}'`), `Missing citizen: ${citizen}`);
  assert.match(app, /CITY-INVARIANT: 1\.0/);
  assert.match(app, /AETHERIS: receipt-bound state transitions/);
});

test("research visualizers route through one local City portal", () => {
  assert.ok(existsSync(visualizerPortalPath));
  for (const id of ["spectra", "fold", "murmuration", "mnemosyne", "density", "horizon", "wave", "identity", "build", "soar", "scalar", "invarifold"]) {
    assert.ok(app.includes(`interfaces/visualizers/?lab=${id}`), `District does not route through visualizer portal: ${id}`);
    assert.ok(visualizerPortal.includes(`id:'${id}'`), `Visualizer portal missing instrument: ${id}`);
  }
  for (const token of ["VISUALIZER PORTAL", "OPEN ORIGINAL", "CITY CORE", "source visualizer is preserved unchanged"]) assert.ok(visualizerPortal.includes(token), `Visualizer portal missing shell contract: ${token}`);
});

test("browser JavaScript parses", () => assert.doesNotThrow(() => new Script(app, { filename: "website/js/app.js" })));

test("local links and assets remain inside the GitHub Pages subpath", () => {
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]));
  const repoPrefix = "https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/";
  for (const [, target] of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    if (/^(mailto:|data:|javascript:)/.test(target)) continue;
    if (target.startsWith(repoPrefix)) { assert.ok(existsSync(resolve(root, target.slice(repoPrefix.length))), `Missing repository target: ${target}`); continue; }
    const url = new URL(target, base);
    if (url.origin !== base.origin) continue;
    assert.ok(url.pathname.startsWith(base.pathname), `Escapes Pages subpath: ${target}`);
    if (url.hash) assert.ok(ids.has(url.hash.slice(1)), `Missing anchor: ${target}`);
    if (target.startsWith("#")) continue;
    const path = url.pathname.slice(base.pathname.length) || "index.html";
    assert.ok(existsSync(resolve(site, path)), `Missing local asset: ${target}`);
  }
});

async function render({ search = "" } = {}) {
  const makeClassList = () => { const classNames = new Set(); return { toggle(name, force) { if (force === undefined) { if (classNames.has(name)) classNames.delete(name); else classNames.add(name); return classNames.has(name); } if (force) classNames.add(name); else classNames.delete(name); return force; }, contains(name) { return classNames.has(name); } }; };
  const makeElement = () => { let innerHTML = ""; let districts = []; return { get innerHTML() { return innerHTML; }, set innerHTML(value) { innerHTML = value; districts = [...value.matchAll(/class="district[^"]*"[^>]*data-index="(\d+)"/g)].map(([, index]) => ({ dataset: { index }, listeners: {}, addEventListener(type, listener) { this.listeners[type] = listener; } })); }, textContent: "", classList: makeClassList(), attributes: {}, dataset: {}, listeners: {}, addEventListener(type, listener) { this.listeners[type] = listener; }, setAttribute(name, value) { this.attributes[name] = value; }, querySelectorAll(selector) { return selector === ".district" ? districts : []; }, scrollIntoView() { this.scrolled = true; }, onclick: null }; };
  const elements = Object.fromEntries(["pipeline-root","status-bar","lab-grid","district-orbit","world-title","world-description","guide-what","guide-try","world-enter","egg-world","egg-toggle","route-egg","law","world"].map((id) => [id, makeElement()]));
  const body = { classList: makeClassList() };
  const window = { openCalls: [], open(...args) { this.openCalls.push(args); } };
  const location = { search, href: "" };
  runInNewContext(app, { document: { getElementById: (id) => elements[id], querySelectorAll: () => [], body }, window, location, URLSearchParams, console: { warn() {} } });
  return { body, elements, location, fire(id, type = "click") { elements[id].listeners[type]?.({ preventDefault() {} }); }, fireOrbit(index, type = "click") { elements["district-orbit"].querySelectorAll(".district")[index]?.listeners[type]?.({ preventDefault() {} }); }, window };
}

test("renders the city districts and selects SKYRMION by default", async () => {
  const { elements } = await render();
  assert.equal((elements["lab-grid"].innerHTML.match(/class="lab-card"/g) || []).length, 14);
  assert.equal((elements["district-orbit"].innerHTML.match(/class="district/g) || []).length, 14);
  assert.match(elements["lab-grid"].innerHTML, /SKYRMION/);
  assert.equal(elements["world-title"].textContent, "SKYRMION · Flagship Flight");
  assert.equal(elements["world-enter"].textContent, "Fly Skyrmion");
  assert.match(elements["egg-world"].textContent, /DISTRICT: SKYRMION/);
});

test("district query parameters select the requested lab and scroll to the world view", async () => {
  const { elements } = await render({ search: "?district=Fold" });
  assert.equal(elements["world-title"].textContent, "Fold · Invariance");
  assert.match(elements["guide-what"].textContent, /Fold is the City district for invariance\./);
  assert.equal(elements["world-enter"].textContent, "Open visualizer");
  assert.equal(elements.world.scrolled, true);
});

test("clicking a generated district button selects that district", async () => {
  const result = await render(); result.fireOrbit(3);
  assert.equal(result.elements["world-title"].textContent, "Fold · Invariance");
  assert.equal(result.elements["world-enter"].textContent, "Open visualizer");
  assert.match(result.elements["egg-world"].textContent, /DISTRICT: Fold/);
});

test("visualizer districts navigate to the local portal shell", async () => {
  const result = await render({ search: "?district=Fold" }); result.elements["world-enter"].onclick();
  assert.equal(result.location.href, "interfaces/visualizers/?lab=fold"); assert.deepEqual(result.window.openCalls, []);
});

test("egghead controls toggle the body state and route shortcut scrolls to the law page", async () => {
  const result = await render(); result.fire("egg-toggle");
  assert.ok(result.body.classList.contains("egghead-on")); assert.ok(result.elements["egg-toggle"].classList.contains("on")); assert.equal(result.elements["egg-toggle"].attributes["aria-pressed"], "true"); assert.equal(result.elements["egg-toggle"].textContent, "🥚 Egghead · ON"); result.fire("route-egg"); assert.ok(result.body.classList.contains("egghead-on")); assert.equal(result.elements.law.scrolled, true);
});

test("evidence references retain exact committed certificates", () => {
  const pipeline = json(resolve(site, "data/e47_pipeline.json")); assert.equal(pipeline.validation_status, "COMPLETE"); assert.ok(Array.isArray(pipeline.pipeline)); assert.ok(pipeline.pipeline.length >= 7); assert.ok(pipeline.pipeline.every((stage) => stage.validated === true)); const text = JSON.stringify(pipeline); for (const invariant of ["125", "47", "11664"]) assert.ok(text.includes(invariant), invariant);
});

test("Syntax Jacob keeps its standalone portal semantics", async () => {
  const { elements, location } = await render({ search: "?district=Syntax%20Jacob" }); assert.equal(elements["world-title"].textContent, "Syntax Jacob · 3I Copilot"); assert.equal(elements["world-enter"].textContent, "Launch copilot"); elements["world-enter"].onclick(); assert.equal(location.href, "interfaces/syntax-jacob/");
});

test("Syntax Jacob publishes runtime provenance", () => {
  const dir = resolve(site, "interfaces/syntax-jacob"); const provenance = json(resolve(dir, "provenance.json")); assert.equal(provenance.original_work, true); assert.equal(provenance.e47.dimension, 125); assert.equal(provenance.e47.kernel_dimension, 47); const runtime = read(resolve(dir, "app.js")); for (const token of ["syntax-jacob-ephemeris", "matrix-cube-adapter", "aetheris.receipt", "1/99144"]) assert.ok(runtime.includes(token), token);
});
