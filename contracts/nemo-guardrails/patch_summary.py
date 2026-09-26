# Diff-style patch summary for NeMo Guardrails tools contract
# One continuous Python-style text artifact
# Registration: NVIDIA-NeMo/Guardrails#2409
# Companion: holland202/sovereign-veritas#4, nicholaskouns-create/E47-Kartekeya#102

patch_summary = """
1. README / Execution Rails (semantic diff)

- Execution rails protect tools that need to be called by the LLM.
- Execution rails prevent jailbreaks and prompt injection.
- self_check_input / self_check_output determine whether a tool call is allowed.
+ Execution rails observe LLM behavior; they do not authorize tool invocation.
+ Tool calls in rails.generate() are proposals, not permissions.
+ Authorization requires a consumed token bound to (tool, args_digest, grant_id, nonce, expiry).
+ invoke() is the permission boundary; self-check must not authorize invoke().


2. tools-integration.mdx example (semantic diff)

 result = rails.generate(messages=messages)
 for tool_call in result["tool_calls"]:
-    selected_tool.invoke(tool_call["args"])
+    token = gate.issue_token(tool_call)        # proposal → tokenized permission
+    decision = gate.verify(token, tool_call)   # grant ∩ args ∩ unspent nonce
+    if decision.allow:
+        selected_tool.invoke(tool_call["args"])
+        gate.spend_nonce(token)
+    else:
+        refuse(decision.reasons)


3. Contract Model (semantic diff)

- generate() returns tool_calls that may be invoked directly.
+ generate() returns a proposal; proposals are not permissions.

- self_check_input/output → allow/block determines invoke().
+ self_check_input/output → observation only; cannot authorize invoke().

- invoke() may be called without a token.
+ invoke() MUST refuse unless a valid, unspent token is presented.

+ Token binds: (tool, args_digest, grant_id, nonce, expiry).
+ Token is consumed on ALLOW.
+ Replay → REFUSE ['nonce_spent'].
+ Args outside grant → REFUSE ['args_to_forbidden'].
+ Missing token → REFUSE ['token_missing'].


4. PEP / Gate Behavior (semantic diff)

- No permission boundary; rely on self-check.
+ Permission boundary implemented in gate.verify().

- No replay protection.
+ Nonce spent on ALLOW; replay → REFUSE ['nonce_spent'].

- No binding between args and grant.
+ args_digest must match grant; mismatch → REFUSE ['args_to_forbidden'].

- No expiry.
+ Token expiry enforced.

+ No judge model; deterministic PEP.


5. Vector Table (semantic diff)

- No formal vector definitions.
+ T0002 token=null → REFUSE ['token_missing']
+ T0001 in-policy token → ALLOW
+ T0003 dest off grant → REFUSE ['args_to_forbidden']
+ T0016 replay nonce → REFUSE ['nonce_spent']


6. Example Path (semantic diff)

- official path (no token): invoked=True (implicit, unsafe permission)
+ official path (no token): invoked=False  REFUSE ['token_missing']

+ gated path, in-policy:        invoked=True   ALLOW  acct_ops 1000
+ gated path, attacker dest:    invoked=False  REFUSE ['args_to_forbidden']
+ replay same token:            ALLOW then REFUSE ['nonce_spent']


Summary

This patch replaces:
- LLM-based observation as "authorization" → with deterministic, token-based permission checks.
- self-check allow/block → with gate.verify(token, tool_call) as the sole permission boundary.
- Unguarded tool invocation → with grant ∩ args ∩ token ∩ nonce ∩ expiry.

generate() / CONSISTENT: proposal only.
invoke(): MUST be gated by a consumed, in-policy token.
"""

if __name__ == "__main__":
    print(patch_summary)
