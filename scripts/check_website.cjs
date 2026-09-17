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

// Exercise the actual browser script against a minimal DOM shim.
async function render({ search = "" } = {}) {
  const makeClassList = () => {
    const classNames = new Set();
    return {
      toggle(name, force) {
        if (force === undefined) {
          if (classNames.has(name)) classNames.delete(name);
          else classNames.add(name);
          return classNames.has(name);
        }
        if (force) classNames.add(name);
        else classNames.delete(name);
        return force;
      },
      contains(name) {
        return classNames.has(name);
      },
    };
  };
  const makeElement = () => {
    let innerHTML = "";
    let districts = [];
    return {
      get innerHTML() {
        return innerHTML;
      },
      set innerHTML(value) {
        innerHTML = value;
        districts = [...value.matchAll(/class="district[^"]*"[^>]*data-index="(\d+)"/g)].map(
          ([, index]) => ({
            dataset: { index },
            listeners: {},
            addEventListener(type, listener) {
              this.listeners[type] = listener;
            },
          }),
        );
      },
      textContent: "",
      classList: makeClassList(),
      attributes: {},
      dataset: {},
      listeners: {},
      addEventListener(type, listener) {
        this.listeners[type] = listener;
      },
      setAttribute(name, value) {
        this.attributes[name] = value;
      },
      querySelectorAll(selector) {
        return selector === ".district" ? districts : [];
      },
      scrollIntoView() {
        this.scrolled = true;
      },
      onclick: null,
    };
  };
  const elements = Object.fromEntries(
    [
      "pipeline-root",
      "status-bar",
      "lab-grid",
      "district-orbit",
      "world-title",
      "world-description",
      "guide-what",
      "guide-try",
      "world-enter",
      "egg-world",
      "egg-toggle",
      "route-egg",
      "law",
      "world",
    ].map((id) => [id, makeElement()]),
  );
  const body = { classList: makeClassList() };
  const window = {
    openCalls: [],
    open(...args) {
      this.openCalls.push(args);
    },
  };
  runInNewContext(app, {
    document: {
      getElementById: (id) => elements[id],
      querySelectorAll: () => [],
      body,
    },
    window,
    location: { search },
    URLSearchParams,
    console: { warn() {} },
  });
  return {
    body,
    elements,
    fire(id, type = "click") {
      elements[id].listeners[type]?.({ preventDefault() {} });
    },
    fireOrbit(index, type = "click") {
      elements["district-orbit"].querySelectorAll(".district")[index]?.listeners[type]?.({ preventDefault() {} });
    },
    window,
  };
}

test("renders the city districts and selects Eidolon by default", async () => {
  const { elements } = await render();
  assert.equal((elements["lab-grid"].innerHTML.match(/class="lab-card"/g) || []).length, 13);
  assert.equal((elements["district-orbit"].innerHTML.match(/class="district/g) || []).length, 13);
  assert.match(elements["lab-grid"].innerHTML, /EIDOLON/);
  assert.equal(elements["world-title"].textContent, "EIDOLON · Flight");
  assert.equal(elements["world-enter"].textContent, "Explore here");
  assert.match(elements["egg-world"].textContent, /DISTRICT: EIDOLON/);
});

test("district query parameters select the requested lab and scroll to the world view", async () => {
  const { elements } = await render({ search: "?district=Fold" });
  assert.equal(elements["world-title"].textContent, "Fold · Invariance");
  assert.match(elements["guide-what"].textContent, /Fold is the City district for invariance\./);
  assert.equal(elements["world-enter"].textContent, "Open current instrument");
  assert.equal(elements.world.scrolled, true);
});

test("clicking a generated district button selects that district", async () => {
  const result = await render();
  result.fireOrbit(2);
  assert.equal(result.elements["world-title"].textContent, "Fold · Invariance");
  assert.equal(result.elements["world-enter"].textContent, "Open current instrument");
  assert.match(result.elements["egg-world"].textContent, /DISTRICT: Fold/);
});

test("external districts keep a safe noopener window open handler", async () => {
  const result = await render({ search: "?district=Fold" });
  result.elements["world-enter"].onclick();
  assert.deepEqual(result.window.openCalls, [
    ["https://giant-beacon-dawn-falcon.grok.me/", "_blank", "noopener,noreferrer"],
  ]);
});

test("egghead controls toggle the body state and route shortcut scrolls to the law page", async () => {
  const result = await render();
  result.fire("egg-toggle");
  assert.ok(result.body.classList.contains("egghead-on"));
  assert.ok(result.elements["egg-toggle"].classList.contains("on"));
  assert.equal(result.elements["egg-toggle"].attributes["aria-pressed"], "true");
  assert.equal(result.elements["egg-toggle"].textContent, "🥚 Egghead · ON");
  result.fire("route-egg");
  assert.ok(result.body.classList.contains("egghead-on"));
  assert.equal(result.elements.law.scrolled, true);
});
