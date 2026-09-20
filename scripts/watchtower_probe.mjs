#!/usr/bin/env node
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

const root = resolve(new URL("..", import.meta.url).pathname);
const catalog = JSON.parse(readFileSync(resolve(root, "scripts/watchtower_surfaces.json"), "utf8"));
const tsvPath = resolve(process.cwd(), "watchtower.tsv");
const UA = "Mozilla/5.0 Mathematical-City-Watchtower/1.0";

function sleep(ms) {
  return new Promise((resolveSleep) => setTimeout(resolveSleep, ms));
}

async function fetchSurface(url) {
  const response = await fetch(url, {
    redirect: "follow",
    headers: { "user-agent": UA },
    signal: AbortSignal.timeout(35000),
  });
  const body = await response.text();
  return { status: response.status, body };
}

async function probe(surface) {
  const attempts = surface.retry?.attempts ?? 3;
  const delay = surface.retry?.delay_ms ?? 2000;
  let last = { status: 0, body: "" };
  for (let attempt = 1; attempt <= attempts; attempt += 1) {
    try {
      last = await fetchSurface(surface.url);
    } catch (error) {
      last = { status: 0, body: String(error) };
    }
    const missing = (surface.must_contain ?? []).filter((token) => !last.body.includes(token));
    if (last.status === 200 && missing.length === 0) {
      return { ok: true, status: last.status, attempt, missing: [] };
    }
    if (attempt < attempts) {
      console.log(`${surface.id}: attempt ${attempt} HTTP ${last.status}; waiting for surface readiness...`);
      await sleep(delay);
    } else {
      return { ok: false, status: last.status, attempt, missing };
    }
  }
  return { ok: false, status: last.status, attempt: attempts, missing: surface.must_contain ?? [] };
}

const rows = [];
const failures = [];
for (const surface of catalog.surfaces) {
  const result = await probe(surface);
  rows.push(`${surface.name}\t${result.status}\t${surface.url}`);
  console.log(`${result.ok ? "PASS" : "FAIL"}\t${surface.name}\tHTTP ${result.status}\t${surface.url}`);
  if (!result.ok) {
    failures.push(`${surface.id}: HTTP ${result.status}; missing ${result.missing.join(" | ") || "body"}`);
  }
}

writeFileSync(tsvPath, `${rows.join("\n")}\n`);

if (failures.length) {
  console.error(`WATCHTOWER FAIL: ${failures.join("; ")}`);
  process.exit(1);
}

console.log(`WATCHTOWER PASS: ${catalog.surfaces.length} named surfaces`);
