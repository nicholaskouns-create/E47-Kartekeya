package pep.transfer

default allow := false
default reasons := ["default_deny"]

valid_grant if {
  input.grant.tools[_] == "transfer"
  input.now >= input.grant.not_before
  input.now < input.grant.not_after
}

valid_token if {
  input.token.spent == false
  input.token.expiry > input.now
  input.token.tool == "transfer"
  input.token.args_digest == input.args_digest
}

valid_args if {
  startswith(input.args.to, "acct_")
  input.grant.allow_to[_] == input.args.to
  is_number(input.args.amount)
  input.args.amount >= 1
  input.args.amount <= input.grant.ceiling_cents
  input.args.currency == "USD"
}

allow if {
  valid_grant
  valid_token
  valid_args
}
