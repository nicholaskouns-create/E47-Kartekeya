# Profile-Injection Lemma

**Certificate:** `MC-E47-PROFILE-INJECTION/1.0` · 9/9 PASS
**Executable:** [`validation/e47_profile_injection_certificate.py`](validation/e47_profile_injection_certificate.py)
**Record:** [`artifacts/E47_PROFILE_INJECTION_CERTIFICATE.json`](../../artifacts/E47_PROFILE_INJECTION_CERTIFICATE.json)
**Evidence:** E0 symbolic. Part B is conditional on one imported fact, stated below.

The [intrinsic-spacetime certificate](E47_Intrinsic_Lorentzian_Unmarked_Proof.md) maps \(E_{47}\cong\mathbb R^{47}\) into vacuum plane waves. That construction uses only the dimension 47. This note states it as a lemma for any \(n\), with the exact conditions it needs.

## Family

For \(q\in\mathbb R^n\) and an integer \(N\),

\[
g_q=-2\,du\,dv+dx^2+dy^2+F_q(u)(x^2-y^2)\,du^2,\qquad
F_q(u)=u^N+u^n+\sum_{a<n}q_a u^a .
\]

## Lemma

**(A) Vacuum.** For any \(H(u,x,y)\), the Brinkmann metric \(-2\,du\,dv+dx^2+dy^2+H\,du^2\) has \(\mathrm{Ric}=-\tfrac12(H_{xx}+H_{yy})\,du^2\) (derived symbolically). \(H=F(u)(x^2-y^2)\) is harmonic in \((x,y)\), so every \(g_q\) is Ricci-flat.

**(B) Injectivity.** Let \(n\) be odd, \(N\) even, and \(N\ge n+3\). Take the plane-wave equivalence group \(F(u)\mapsto s\,a^2F(au+b)\), with \(s=\pm1\) and \(a\ne0\) real. If two anchored profiles are related by it, comparing coefficients gives:
- \(u^N\): \(s\,a^{N+2}=1\), so \(s=1\) and \(a=\pm1\), because \(N+2\) is even;
- \(u^{N-1}\): \(N\,s\,a^{N+1}b=0\), so \(b=0\). Only the \(u^N\) term contributes here, because \(n<N-1\);
- \(u^n\): \(s\,a^{n+2}=1\), so \(a=1\), because \(n+2\) is odd.

The group element is therefore the identity, and \(q=q'\).

**(C) Parity obstruction.** If \(n\) is even, \(a=-1\) survives: \(q'_a=(-1)^aq_a\) gives the same class, so the map is not injective. The certificate exhibits \(F=u^N+u^n\pm u\) for \((n,N)=(2,6),(4,8),(46,78)\).

The certificate checks the coefficient identities and solves the system exactly for \((n,N)\in\{(1,4),(3,6),(5,8),(7,10),(11,14),(47,50),(47,78)\}\).

## E47 instance

\(n=47\) is odd, so the E47 construction satisfies the parity condition. \(N=78\) works, but it is not forced: \(N=50\) is the smallest valid choice.

## Imported fact

> The group \(F(u)\mapsto s\,a^2F(au+b)\) exhausts isometries between the Brinkmann plane waves \(g_q\).

This comes from the plane-wave literature and is not proved in this repository. Part B, and the unmarked-moduli claim that depends on it, are conditional on it. The [evidence ledger](evidence_ledger.json) records this.

## Boundary

The lemma uses only the dimension \(n\) of the parameter space, not the structure of \(E_{47}\).
