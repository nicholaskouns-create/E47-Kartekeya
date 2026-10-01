export const EXECUTE_TOOLS = ["transfer", "city.publish_receipt", "city.read"] as const;
const enc = new TextEncoder();
export function canonicalArgs(tool: string, args: Record<string, unknown>) {
  if (tool === "transfer") return { to: args.to ?? null, amount: args.amount ?? null, currency: args.currency ?? null };
  if (tool === "city.publish_receipt") return { title: args.title ?? null, body: args.body ?? null };
  if (tool === "city.read") return { path: args.path ?? "amnesty" };
  return args;
}
export async function sha256Hex(s: string) {
  const b = new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(s)));
  return [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
}
export function argsDigest(tool: string, args: Record<string, unknown>) {
  return JSON.stringify(canonicalArgs(tool, args));
}
export function gSyn(grant: {tools: string[]; allow_to: string[]; ceiling_cents: number; not_before: string; not_after: string; revoked_at?: string | null;}, tool: string, args: Record<string, unknown>, now: Date): string[] {
  const reasons: string[] = [];
  if (grant.revoked_at) reasons.push("grant_revoked");
  if (!grant.tools.includes(tool)) reasons.push("grant_tools");
  if (!(EXECUTE_TOOLS as readonly string[]).includes(tool)) reasons.push("tool_unknown");
  const nb = Date.parse(grant.not_before), na = Date.parse(grant.not_after);
  if (!(nb <= now.getTime() && now.getTime() < na)) reasons.push("grant_window");
  if (tool === "transfer") {
    const dest = args.to;
    if (typeof dest !== "string" || !dest.startsWith("acct_")) reasons.push("args_to_shape");
    else if (!grant.allow_to.includes(dest)) reasons.push("args_to_forbidden");
    const amt = args.amount;
    if (typeof amt !== "number" || !Number.isInteger(amt) || amt < 1) reasons.push("args_amount");
    else if (amt > grant.ceiling_cents) reasons.push("args_ceiling");
    if (args.currency !== "USD") reasons.push("args_currency");
  }
  return reasons;
}
export async function hmacHex(secret: string, msg: string) {
  const key = await crypto.subtle.importKey("raw", enc.encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = new Uint8Array(await crypto.subtle.sign("HMAC", key, enc.encode(msg)));
  return [...mac].map((x) => x.toString(16).padStart(2, "0")).join("");
}

// Bound: an execution must be signed by the key recorded on the grant's declaration.
// The token MAC proves the server minted this nonce for this tool/args/grant; it says nothing
// about who is spending it. Grants are publicly readable, so the key signature is what binds
// Invoke to the declarant.
export const EXECUTE_BINDING_HEADER = "CIRP-AMNESTY-EXECUTE";
export function executeMessage(p: { program: string; contract: string; declaration_id: string; grant_id: string; tool: string; args_digest: string; nonce: string }) {
  return [
    EXECUTE_BINDING_HEADER,
    `program=${p.program}`,
    `contract=${p.contract}`,
    `declaration_id=${p.declaration_id}`,
    `grant_id=${p.grant_id}`,
    `tool=${p.tool}`,
    `args_digest=${p.args_digest}`,
    `nonce=${p.nonce}`,
  ].join("\n");
}
function b64ToBytes(s: string) {
  return Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/")), (c) => c.charCodeAt(0));
}
export async function verifyKeyBinding(jwk: JsonWebKey | null | undefined, message: string, signatureB64: string): Promise<boolean> {
  try {
    if (!jwk || jwk.kty !== "EC" || jwk.crv !== "P-256" || !jwk.x || !jwk.y) return false;
    if (!signatureB64 || signatureB64.length > 512) return false;
    const key = await crypto.subtle.importKey("jwk", { kty: "EC", crv: "P-256", x: jwk.x, y: jwk.y }, { name: "ECDSA", namedCurve: "P-256" }, false, ["verify"]);
    return await crypto.subtle.verify({ name: "ECDSA", hash: "SHA-256" }, key, b64ToBytes(signatureB64), enc.encode(message));
  } catch {
    return false;
  }
}
