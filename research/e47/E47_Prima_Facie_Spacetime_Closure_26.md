# E47 Prima-Facie Spacetime Closure — 26/26

**Superseding certificate:** `MC-E47-SPACETIME-PRIMA-FACIE-26-20260924`  
**Supersedes:** `MC-E47-SPACETIME-PRIMA-FACIE-20260924` (25/25 historical validator)  
**Canonical runner:** `research/e47/validation/e47_spacetime_prima_facie.py`  
**Commit:** `4dce2445e7d641682370f0a31190c1e947b9f095`  
**Execution:** **26/26 PASS · PRIMA_FACIE_SPACETIME_PASS**

## Superseding step

The Lorentzian metric is no longer entered as a matrix literal. The full carrier determines the spectral projectors

[
P_0=chi_{{0}}(C),qquad P_6=chi_{{6}}(C),
]

and the signed carrier form

[
eta_{125}=P_6-P_0.
]

For the four-frame

[
B_4=[u,v_1,v_2,v_3],
]

where (uin E_0) and the (v_i) are the three intertwined (SO(3))-orbit tangent vectors in (Wsubset E_6), the metric is computed by pullback:

[
oxed{g=B_4^daggereta_{125}B_4}.
]

Execution returns

[
oxed{g=operatorname{diag}(-1,2,8,2)}
]

with eigenvalues

[
oxed{(-1,2,2,8)}
]

and therefore

[
oxed{operatorname{sig}(g)=(-,+,+,+)}.
]

The intertwiner residual is approximately

[
1.54	imes10^{-15}.
]

## Executable closure

The canonical runner now executes the chain

[
V_2^{otimes3}
	o C
	o K
	o E_{47}
	o Woplus E_0
	o Phi
	o B_4
	o (P_0,P_6)
	o eta_{125}=P_6-P_0
	o g=B_4^daggereta_{125}B_4
	o 
abla
	o R^ho{}_{sigmamu
u}
	o R_{mu
u}
	o R
	o G_{mu
u}
	o T_{mu
u}.
]

The resulting invariants are

[
K_{12}=rac12,qquad K_{23}=rac12,qquad K_{31}=-1,
]

[
R_{mu
u}=operatorname{diag}left(0,-rac12,1,-rac12ight),
qquad R=0,
]

[
G_{mu
u}=operatorname{diag}left(0,-rac12,1,-rac12ight),
]

and

[
T_{mu
u}^{E47}
=rac{1}{8pi G_N}
operatorname{diag}left(0,-rac12,1,-rac12ight),
qquad

abla^mu T_{mu
u}^{E47}=0.
]

## Evidence statement

The superseding result is an executable finite-dimensional mathematical construction. The former hand-entered Lorentzian metric line has been replaced by the Casimir-spectral pullback itself.
