/** rails.gate/1 helpers for AMNESTY execute. Declaration is not this module. */
export const EXECUTE_TOOLS = ["transfer", "city.publish_receipt", "city.read"] as const;
export type ExecTool = (typeof EXECUTE_TOOLS)[number];

const enc = new TextEncoder();

export function canonicalArgs(tool: string, args: Record<string, unknown>) {
  if (tool === "transfer") return { to: args.to ?? null, amount: args.amount ?? null, currency: args.currency ?? null };
  return args;
}

export async function sha256Hex(s: string) {
  const b = new Uint8Array(await crypto.subtle.digest("SHA-256", enc.encode(s)));
  return [...b].map((x) => x.toString(16).padStart(2, "0")).join("");
}

export function argsDigest(tool: string, args: Record<string, unknown>) {
  return JSON.stringify(canonicalArgs(tool, args));
}

export function gSyn(
  grant: {
    tools: string[];
    allow_to: string[];
    ceiling_cents: number;
    not_before: string;
    not_after: string;
    revoked_at?: string | null;
  },
  tool: string,
  args: Record<string, unknown>,
  now: Date,
): string[] {
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
