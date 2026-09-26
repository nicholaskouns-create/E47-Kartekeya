# CIRP / AMNESTY RLS lock

Locked 2026-09-26. This is the operating guidance, not a civic grant.

RLS is not a lock on the table. It is an implicit WHERE / WITH CHECK that Postgres adds for roles that do not have BYPASSRLS. In this project that means anon and authenticated. service_role (the edge function) skips every policy. That split is the whole model.

## Rules

1. Two layers, both required. Grants decide whether a role can touch the object. RLS decides which rows survive. A public SELECT policy with no GRANT SELECT is a dead door. A GRANT SELECT with RLS on and no policy is deny-all.
2. Enable RLS on every exposed table. Every public table here already has RLS on.
3. One policy per operation. SELECT uses USING. INSERT uses WITH CHECK. UPDATE needs both. DELETE uses USING. Do not use FOR ALL unless every verb shares the same predicate.
4. Name the role. TO public covers anon + authenticated. Prefer TO authenticated when auth.uid() is in the predicate.
5. Wrap auth.uid() / auth.jwt() in a subquery: `(select auth.uid())`.
6. Least privilege on grants, not only on policies. If clients should never insert, do not GRANT INSERT to anon.
7. service_role is a server credential. Keep it in the edge function. Never ship it to GitHub Pages.
8. RLS-on + zero policies is a valid deny-all for function-owned tables. Leave it on amnesty_nonces, coherence_runtime_state, coherence_runtime_evaluations. Do not add a policy to silence the lint.
9. Helpers that read other tables should be SECURITY DEFINER with a fixed search_path. Pin search_path on amnesty_reject_status_promotion.
10. Policies do not hide columns. Do not put MAC secrets on a publicly selectable table.
11. Test as the role, not as postgres. Proof is PostgREST with the anon key or `set role anon`.
12. Filter in the client anyway. Prefer `.eq('agent_code','NICHOLAS.KOUNS')` even when the policy is `using (true)`.

## Locked lattice

- page may SELECT: amnesty_declarations (public scope), amnesty_grants, amnesty_executions
- page may not write those tables
- function writes with service_role
- nonce / state / evaluate remain deny-all for clients
- do not open amnesty_nonces
- do not FORCE RLS on these tables unless owner policies exist
