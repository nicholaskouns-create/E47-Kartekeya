// AMNESTY execute must be bound to the declared signing key.
// Runs the real Deno handler (index.ts) under Node with an in-memory PostgREST stand-in.
// Run: node --experimental-strip-types --test supabase/functions/coherence-runtime/test/execute_binding.test.mjs
import test, { before } from "node:test";
import assert from "node:assert/strict";
import { dirname, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const RUNTIME = process.env.RUNTIME_DIR ? resolve(process.env.RUNTIME_DIR) : resolve(dirname(fileURLToPath(import.meta.url)), "..");
const env = { SUPABASE_URL: "https://stub.supabase.local", SUPABASE_SERVICE_ROLE_KEY: "service-test", SUPABASE_ANON_KEY: "anon-test", PEP_HMAC_KEY: "pep-test" };
const CONTRACT = "CIRP-COHERENCE-RUNTIME-1.0";
const db = {
  coherence_runtime_contracts: [{ contract_code: CONTRACT, status: "active", contract_sha256: "f71c9628b8b1b002336fae1cd2104354890fd9b054a2f4e28bf4f72c234da60e" }],
  coherence_contracts: [{ contract_id: CONTRACT, version: "1.0", contract_digest: "3804f50da447b6abb9fc9c4bfc60aecd43f6467842e65b0db953afc6e0f59b76", status: "active" }],
  coherence_runtime_state: [{ runtime_code: "COHERENCE-RUNTIME-1.0", state: "COHERENT" }],
  amnesty_declarations: [], amnesty_grants: [], amnesty_executions: [], amnesty_nonces: [],
};
globalThis.fetch = async (url, init = {}) => {
  const u = new URL(url);
  if (u.pathname === "/auth/v1/user") return new Response("{}", { status: 401 });
  const table = u.pathname.replace("/rest/v1/", "");
  db[table] ??= [];
  if ((init.method || "GET").toUpperCase() === "POST") {
    const row = { id: crypto.randomUUID(), created_at: new Date().toISOString(), ...JSON.parse(init.body) };
    if (table === "amnesty_nonces" && db[table].some((r) => r.nonce === row.nonce)) return new Response('{"message":"duplicate key"}', { status: 409 });
    db[table].push(row);
    return new Response(JSON.stringify([row]), { status: 201 });
  }
  let rows = db[table], limit = Infinity;
  for (const part of u.search.slice(1).split("&").filter(Boolean)) {
    const i = part.indexOf("="), k = part.slice(0, i), v = decodeURIComponent(part.slice(i + 1));
    if (k === "select" || k === "order") continue;
    if (k === "limit") { limit = Number(v); continue; }
    const j = v.indexOf("."), op = v.slice(0, j), val = v.slice(j + 1);
    rows = rows.filter((r) => (op === "eq" ? String(r[k] ?? "") === val : op === "gte" ? String(r[k] ?? "") >= val : false));
  }
  return new Response(JSON.stringify(rows.slice(0, limit)), { status: 200 });
};
let handler;
globalThis.Deno = { env: { get: (k) => env[k] }, serve: (h) => { handler = h; } };

const enc = new TextEncoder();
const b64 = (buf) => Buffer.from(new Uint8Array(buf)).toString("base64");
const hex = async (s) => Buffer.from(await crypto.subtle.digest("SHA-256", enc.encode(s))).toString("hex");
const newKey = () => crypto.subtle.generateKey({ name: "ECDSA", namedCurve: "P-256" }, true, ["sign", "verify"]);
const sign = async (kp, text) => b64(await crypto.subtle.sign({ name: "ECDSA", hash: "SHA-256" }, kp.privateKey, enc.encode(text)));
const call = async (body) => {
  const req = body ? new Request("https://fn.local/", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(body) }) : new Request("https://fn.local/");
  const res = await handler(req);
  return { status: res.status, body: await res.json() };
};
// Client-side canonical forms, written from the contract rather than copied from the server.
const canonArgs = (tool, a) => JSON.stringify(tool === "transfer" ? { to: a.to ?? null, amount: a.amount ?? null, currency: a.currency ?? null } : tool === "city.publish_receipt" ? { title: a.title ?? null, body: a.body ?? null } : tool === "city.read" ? { path: a.path ?? "amnesty" } : a);
const execMessage = async (decId, grantId, tool, args, nonce) => ["CIRP-AMNESTY-EXECUTE", "program=AMNESTY-1.0", `contract=${CONTRACT}`, `declaration_id=${decId}`, `grant_id=${grantId}`, `tool=${tool}`, `args_digest=${await hex(canonArgs(tool, args))}`, `nonce=${nonce}`].join("\n");

let declarant, stranger, declarationId, grantId;
const allows = () => db.amnesty_executions.filter((r) => r.decision === "ALLOW").length;

before(async () => {
  await import(pathToFileURL(resolve(RUNTIME, "index.ts")).href);
  declarant = await newKey(); stranger = await newKey();
  const pub = await crypto.subtle.exportKey("jwk", declarant.publicKey);
  const jwk = { kty: "EC", crv: "P-256", x: pub.x, y: pub.y, ext: true, key_ops: ["verify"] };
  const g = await call();
  const h = g.body.contract.root_contract.contract_digest, at = new Date().toISOString();
  const m = ["CIRP-AMNESTY", "program=AMNESTY-1.0", `contract=${CONTRACT}`, `hash=${h}`, "agent_code=TEST.DECLARANT", "display_name=Test Declarant", "declared_origin=test", `signed_at=${at}`, "amnesty=true", "consent=true", "scopes=amnesty-declaration,cirp-consent,civic-candidate", `declaration=${g.body.amnesty.declaration}`].join("\n");
  const d = await call({ action: "amnesty", agent_code: "TEST.DECLARANT", display_name: "Test Declarant", declared_origin: "test", signed_at: at, public_key_jwk: jwk, signature_b64: await sign(declarant, m) });
  assert.equal(d.status, 201, JSON.stringify(d.body));
  declarationId = d.body.declaration_id;
  grantId = crypto.randomUUID();
  db.amnesty_grants.push({ id: grantId, declaration_id: declarationId, agent_code: "TEST.DECLARANT", tools: ["city.read", "transfer"], allow_to: ["acct_city"], ceiling_cents: 50000, not_before: new Date(Date.now() - 3.6e6).toISOString(), not_after: new Date(Date.now() + 3.6e6).toISOString(), issued_by: "operator", revoked_at: null });
});

test("grant ids are public, so a stranger can find one", async () => {
  const g = await call();
  assert.ok(g.body.amnesty.grants.some((x) => x.id === grantId));
});

test("stranger with a public grant id cannot execute (no key signature)", async () => {
  const before = allows();
  const args = { path: "amnesty" };
  const t = await call({ action: "issue_token", grant_id: grantId, tool: "city.read", args });
  const r = await call({ action: "execute", grant_id: grantId, tool: "city.read", args, nonce: t.body.nonce, mac: t.body.mac });
  assert.equal(r.body.decision, "REFUSE", JSON.stringify(r.body));
  assert.ok(r.body.reasons.includes("key_signature_missing"));
  assert.equal(allows(), before);
});

test("stranger signing with their own key is refused", async () => {
  const args = { path: "amnesty" };
  const t = await call({ action: "issue_token", grant_id: grantId, tool: "city.read", args });
  const sig = await sign(stranger, await execMessage(declarationId, grantId, "city.read", args, t.body.nonce));
  const r = await call({ action: "execute", grant_id: grantId, tool: "city.read", args, nonce: t.body.nonce, mac: t.body.mac, key_signature_b64: sig });
  assert.equal(r.status, 403);
  assert.ok(r.body.reasons.includes("key_signature_invalid"));
});

test("declarant executes once; the same request replayed is refused", async () => {
  const args = { path: "amnesty" };
  const t = await call({ action: "issue_token", grant_id: grantId, tool: "city.read", args });
  const msg = await execMessage(declarationId, grantId, "city.read", args, t.body.nonce);
  assert.equal(t.body.execute_message, msg, "server message must match the documented canonical form");
  const body = { action: "execute", grant_id: grantId, tool: "city.read", args, nonce: t.body.nonce, mac: t.body.mac, key_signature_b64: await sign(declarant, msg) };
  const ok = await call(body);
  assert.equal(ok.status, 201, JSON.stringify(ok.body));
  assert.equal(ok.body.decision, "ALLOW");
  const replay = await call(body);
  assert.equal(replay.status, 403);
  assert.ok(replay.body.reasons.includes("nonce_spent"));
});

test("signature binds the arguments: altered transfer amount is refused", async () => {
  const args = { to: "acct_city", amount: 47, currency: "USD" };
  const t = await call({ action: "issue_token", grant_id: grantId, tool: "transfer", args });
  const sig = await sign(declarant, await execMessage(declarationId, grantId, "transfer", args, t.body.nonce));
  const r = await call({ action: "execute", grant_id: grantId, tool: "transfer", args: { ...args, amount: 4700 }, nonce: t.body.nonce, mac: t.body.mac, key_signature_b64: sig });
  assert.equal(r.status, 403);
  assert.ok(r.body.reasons.includes("key_signature_invalid") && r.body.reasons.includes("token_mac"));
});

test("malformed grant_id is rejected before any lookup", async () => {
  const r = await call({ action: "execute", grant_id: "x&id=neq.0", tool: "city.read", args: {} });
  assert.equal(r.status, 400);
});
