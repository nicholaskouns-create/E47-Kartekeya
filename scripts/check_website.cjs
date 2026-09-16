// Run with: node --test scripts/check_website.cjs (Node.js 22+).
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");
const { runInNewContext } = require("node:vm");

const root = resolve(__dirname, "..");
const site = resolve(root, "website");
const base = new URL("https://example.test/E47-Kartekeya/");
const read = (path) => readFileSync(path, "utf8");
const json = (path) => JSON.parse(read(path));
const html = read(resolve(site, "index.html"));
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

test("local links, assets and documentation targets exist at the Pages subpath", () => {
  const ids = new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]));
  const repoPrefix = "https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/";
  for (const [, target] of html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
    if (target.startsWith(repoPrefix)) {
      assert.ok(read(resolve(root, target.slice(repoPrefix.length))).length, target);
      continue;
    }
    const url = new URL(target, base);
    if (url.origin !== base.origin) continue;
    assert.ok(url.pathname.startsWith(base.pathname), `Escapes Pages subpath: ${target}`);
    if (url.hash) assert.ok(ids.has(url.hash.slice(1)), `Missing anchor: ${target}`);
    const path = url.pathname.slice(base.pathname.length) || "index.html";
    assert.ok(read(resolve(site, path)).length, `Empty asset: ${target}`);
  }
});

// Exercise the actual browser script and its asynchronous fetch/render path.
async function render(overrides = {}) {
  const elements = {
    "pipeline-root": { innerHTML: "" },
    "status-bar": { innerHTML: "" },
  };
  runInNewContext(app, {
    document: {
      getElementById: (id) => elements[id],
      querySelectorAll: () => [],
    },
    window: {},
    console: { warn() {} },
    fetch: async (path) => {
      const url = new URL(path, base);
      assert.equal(url.origin, base.origin);
      assert.ok(url.pathname.startsWith(base.pathname));
      const content = Object.hasOwn(overrides, path)
        ? overrides[path]
        : read(resolve(site, url.pathname.slice(base.pathname.length)));
      return {
        ok: content !== null,
        status: content === null ? 404 : 200,
        json: async () => JSON.parse(content),
      };
    },
  });
  await new Promise(setImmediate);
  return { pipeline: elements["pipeline-root"].innerHTML, status: elements["status-bar"].innerHTML };
}

test("renders every pipeline stage and both certificate statuses", async () => {
  const result = await render();
  const stages = json(resolve(site, "data/e47_pipeline.json")).pipeline;
  assert.equal((result.pipeline.match(/class="pipeline-stage"/g) || []).length, stages.length);
  for (const stage of stages) assert.ok(result.pipeline.includes(stage.name));
  assert.match(result.status, /Pipeline: COMPLETE/);
  assert.match(result.status, /QuTiP cert: pass/);
  for (const invariant of ["dim(V)=125", "dim(E₄₇)=47", "Ω=47/125", "gap=11664"]) {
    assert.ok(result.status.includes(invariant), invariant);
  }
});

test("a missing QuTiP certificate is visible while the pipeline still renders", async () => {
  const result = await render({ "data/qutip_validation.json": null });
  assert.match(result.status, /QuTiP cert: unavailable/);
  assert.doesNotMatch(result.status, /QuTiP cert: pass/);
  assert.match(result.status, /Pipeline: COMPLETE/);
  assert.match(result.pipeline, /State Space/);
});

test("a missing pipeline is visible while the QuTiP certificate still renders", async () => {
  const result = await render({ "data/e47_pipeline.json": null });
  assert.match(result.pipeline, /Pipeline data unavailable/);
  assert.match(result.status, /Pipeline: unavailable/);
  assert.match(result.status, /QuTiP cert: pass/);
});

test("unreadable certificates show unavailable statuses without pass badges", async () => {
  const result = await render({ "data/e47_pipeline.json": "{", "data/qutip_validation.json": "{" });
  assert.match(result.status, /Pipeline: unavailable/);
  assert.match(result.status, /QuTiP cert: unavailable/);
  assert.doesNotMatch(result.status, /class="pill pass"/);
});
