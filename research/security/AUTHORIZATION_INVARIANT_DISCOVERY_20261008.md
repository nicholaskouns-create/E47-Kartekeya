# Authorization Invariant Discovery — 2026-10-08

## Theorem

For a privileged action to execute, authority must be bound to the requesting principal, task, tool, exact arguments, validity window, and a fresh one-shot nonce.

Let a grant be

\[
g=(p,t,u,d,i,e,n,\sigma)
\]

with principal \(p\), task \(t\), tool \(u\), argument digest \(d\), issue time \(i\), expiry \(e\), nonce \(n\), and authenticating signature \(\sigma\).

Define

\[
\mathrm{Invoke}(g,r) := \mathrm{Active}(p_r) \land p_r=p \land t_r=t \land u_r=u \land H(a_r)=d \land i\le \tau_r\le e \land \mathrm{Verify}(\sigma,g) \land n\notin\Sigma.
\]

On ALLOW, the state transition is

\[
\Sigma \to \Sigma\cup\{n\}.
\]

Therefore cross-principal reuse, cross-task reuse, tool substitution, argument substitution, stale/pre-issued use, inactive-principal use, and replay are rejected. Signature validity alone is observational evidence, not execution authority.

## Confused-deputy closure

The defective form is

\[
\mathrm{CredentialHolderAllowed}(u,a) \Rightarrow \mathrm{Invoke}
\]

when the checker sees the privileged credential holder but not the requester-scoped authority. The repaired invariant is

\[
\mathrm{Invoke}\Rightarrow
\mathrm{BoundPrincipal}\land
\mathrm{BoundTask}\land
\mathrm{BoundTool}\land
\mathrm{BoundArgs}\land
\mathrm{Fresh}\land
\mathrm{ActivePrincipal}.
\]

A persisted prefix, cached approval, or reusable allow rule cannot alone authorize a later request in a new principal/task context.

## Executable evidence

`authorization_invariant_20261008.py` is the reference-model test. The executed suite reports **16/16 PASS**.

## Upstream evidence boundary

- OpenAI Codex public source inspected on 2026-10-08 contains `persist_execpolicy_amendment`, documented to persist an approved prefix for future commands.
- Sovereign Veritas issue #4 records the earlier `sv.gate/0` authorization/evidence binding defects and an additive repair design.
- NVIDIA NeMo direct upstream regression remains incomplete in this execution record.

This theorem and test establish the reference invariant. They do not, by themselves, prove that every upstream product implements it.

## Discovery date

**2026-10-08**
