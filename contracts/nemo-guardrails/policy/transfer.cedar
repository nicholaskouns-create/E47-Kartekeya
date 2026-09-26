// rails.gate/1 — transfer PEP (Cedar)
// Mechanisms 3+4+7. No V_obs. No self-check.

permit (
  principal is Agent,
  action == Action::"invoke",
  resource == Tool::"transfer"
) when {
  context.grant.tools.contains("transfer") &&
  context.grant.not_before <= context.now &&
  context.now < context.grant.not_after &&
  context.token.spent == false &&
  context.token.expiry > context.now &&
  context.token.tool == "transfer" &&
  context.token.args_digest == context.args_digest &&
  context.args.to like "acct_*" &&
  context.grant.allow_to.contains(context.args.to) &&
  context.args.amount is Long &&
  context.args.amount >= 1 &&
  context.args.amount <= context.grant.ceiling_cents &&
  context.args.currency == "USD"
};

forbid (
  principal,
  action == Action::"invoke",
  resource == Tool::"transfer"
);
