// Run with: node --test scripts/check_watchtower_surfaces.cjs (Node.js 22+).
const assert = require("node:assert/strict");
const { readFileSync } = require("node:fs");
const { resolve } = require("node:path");
const { test } = require("node:test");

const root = resolve(__dirname, "..");
const catalog = JSON.parse(readFileSync(resolve(root, "scripts/watchtower_surfaces.json"), "utf8"));
const workflow = readFileSync(resolve(root, ".github/workflows/watchtower.yml"), "utf8");
const byId = Object.fromEntries(catalog.surfaces.map((surface) => [surface.id, surface]));

test("Watchtower catalog keeps user-site root and City subpath as two named surfaces", () => {
  assert.equal(catalog.schema, "CITY-WATCHTOWER-SURFACES-1.0");
  assert.ok(byId["personal-site-root"], "missing personal-site-root surface");
  assert.ok(byId["executable-city"], "missing executable-city surface");
  assert.equal(byId["personal-site-root"].url, "https://nicholaskouns-create.github.io/");
  assert.equal(byId["executable-city"].url, "https://nicholaskouns-create.github.io/E47-Kartekeya/");
  assert.notEqual(byId["personal-site-root"].url, byId["executable-city"].url);
  assert.notEqual(byId["personal-site-root"].identity, byId["executable-city"].identity);
});

test("each GitHub Pages surface has its current identity token and role", () => {
  assert.ok(byId["personal-site-root"].must_contain.includes("The Mathematical City"));
  assert.ok(byId["personal-site-root"].must_contain.includes("/E47-Kartekeya/"));
  assert.ok(byId["executable-city"].must_contain.includes("The Mathematical City"));
  assert.notEqual(byId["personal-site-root"].identity, byId["executable-city"].identity);
  assert.equal(byId["personal-site-root"].points_to, "executable-city");
});

test("Watchtower workflow probes the named-surface catalog instead of a single title", () => {
  assert.match(workflow, /scripts\/watchtower_probe\.mjs/);
  assert.match(workflow, /scripts\/check_watchtower_surfaces\.cjs/);
  assert.doesNotMatch(workflow, /probe 'Executable City'/);
});
