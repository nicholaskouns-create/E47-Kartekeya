#!/usr/bin/env python3
"""
E47 GENERATIVE-UNIVERSE TEST
Pre-registered cross-substrate falsification harness
Nicholas Kouns / KKP-R

Core rule:
    Freeze E47 before observing candidate physical datasets.
    No fitted rank, no fitted sector pair, no learned projector.

This file validates the frozen mathematical prediction and provides
a dataset-facing scoring function for 125-component observations.

A candidate dataset X must be supplied as an array of shape (N,125).
The 125 coordinates must have a domain-defined meaning fixed independently
of E47. The test itself is not allowed to learn/reorder/rotate coordinates.

Primary observables:
    q_E47(x) = ||P47 x||^2 / ||x||^2
    r_K(x)   = ||K x|| / (||K||_2 ||x||)
    q_perp   = 1 - q_E47

Null:
    isotropic directions in R^125 have E[q_E47] = 47/125.

Strong E47-generative hypothesis:
    Across independently encoded physical substrates, persistent/stable
    states show reproducible excess occupancy in the SAME frozen E47
    subspace, with reduced kernel residual, beyond matched null controls.

Failure:
    No reproducible frozen-subspace enrichment, wrong spectral sectors,
    or effects disappearing under held-out replication => hypothesis burns out.
"""

import numpy as np

TOL = 1e-10
J = 2
DIM = 125
OMEGA = 47/125
EPS = 1/99144

def spin2():
    m = np.array([2,1,0,-1,-2], dtype=float)
    Jz = np.diag(m)
    Jp = np.zeros((5,5), complex)
    # basis is |2>,|1>,|0>,|-1>,|-2>
    for col, mc in enumerate(m):
        mp = mc + 1
        if mp <= J and mp in m:
            row = int(np.where(m == mp)[0][0])
            Jp[row,col] = np.sqrt(J*(J+1)-mc*(mc+1))
    Jm = Jp.conj().T
    Jx = (Jp+Jm)/2
    Jy = (Jp-Jm)/(2j)
    return Jx,Jy,Jz

def kron3(a,b,c):
    return np.kron(np.kron(a,b),c)

def build():
    Jx,Jy,Jz = spin2()
    I = np.eye(5)
    tots=[]
    for A in (Jx,Jy,Jz):
        tots.append(kron3(A,I,I)+kron3(I,A,I)+kron3(I,I,A))
    C=sum(A@A for A in tots)
    K=(C-6*np.eye(DIM))@(C-30*np.eye(DIM))
    w,V=np.linalg.eigh(C)
    mask=(np.abs(w-6)<1e-8)|(np.abs(w-30)<1e-8)
    P=V[:,mask]@V[:,mask].conj().T
    Gamma=np.eye(DIM)-EPS*(K@K)
    return C,K,P,Gamma,w

def score(X, K, P):
    X=np.asarray(X,complex)
    if X.ndim==1: X=X[None,:]
    if X.shape[1] != DIM:
        raise ValueError("X must have shape (N,125)")
    norm2=np.sum(np.abs(X)**2,axis=1)
    if np.any(norm2 <= 0): raise ValueError("zero vectors are inadmissible")
    PX=X@P.T
    KX=X@K.T
    q=np.sum(np.abs(PX)**2,axis=1)/norm2
    knorm=np.linalg.norm(K,2)
    r=np.linalg.norm(KX,axis=1)/(knorm*np.sqrt(norm2))
    return q.real,r.real

def isotropic_null(n, K, P, seed=47):
    rng=np.random.default_rng(seed)
    X=rng.normal(size=(n,DIM))
    return score(X,K,P)

def main():
    C,K,P,Gamma,w=build()

    # Frozen certificate
    vals=np.rint(w).astype(int)
    u,c=np.unique(vals,return_counts=True)
    expected_u=np.array([0,2,6,12,20,30,42])
    expected_c=np.array([1,9,25,28,27,22,13])
    assert np.array_equal(u,expected_u)
    assert np.array_equal(c,expected_c)
    assert abs(np.trace(P).real-47)<1e-8
    assert np.linalg.norm(P@P-P)<1e-9
    assert np.linalg.norm(K@P)<1e-8

    k2_expected=np.array([32400,12544,0,11664,19600,0,186624])
    k2=np.array([((x-6)*(x-30))**2 for x in expected_u])
    assert np.array_equal(k2,k2_expected)

    # Exact contraction facts
    gamma=1-k2/EPS**-1
    assert abs(max(abs(gamma[(expected_u!=6)&(expected_u!=30)]))-15/17)<1e-15

    # Null calibration: rank/dim is the predicted mean occupancy.
    q,r=isotropic_null(100000,K,P)
    se=np.sqrt(2*47*(125-47)/(125**2*(125+2))/len(q))
    assert abs(q.mean()-OMEGA) < 6*se

    # Positive-control vectors generated inside E47.
    rng=np.random.default_rng(4700)
    Z=rng.normal(size=(256,DIM))
    Xpos=Z@P.T
    qp,rp=score(Xpos,K,P)
    assert np.min(qp)>1-1e-9
    assert np.max(rp)<1e-9

    print("E47 GENERATIVE-UNIVERSE PRE-REGISTRATION: PASS")
    print(f"dim(H)={DIM}; rank(P47)={round(np.trace(P).real)}; Omega={OMEGA:.12f}")
    print("Casimir spectrum:", list(zip(u.tolist(),c.tolist())))
    print("K^2 sector values:", k2.tolist())
    print(f"complement contraction radius={15/17:.12f}")
    print(f"isotropic null mean q_E47={q.mean():.6f}; theory={OMEGA:.6f}")
    print(f"positive control min q_E47={qp.min():.12f}; max r_K={rp.max():.3e}")
    print()
    print("DATA RULE: coordinates/encoder must be frozen independently of E47.")
    print("KILL RULE: no held-out cross-substrate enrichment in this same P47 => reject generative interpretation.")

if __name__ == "__main__":
    main()
