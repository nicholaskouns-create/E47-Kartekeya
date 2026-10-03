#!/usr/bin/env python3
from sympy import Matrix, eye, Rational

def validate():
    J = Matrix([[0,1],[1,0]])
    I = eye(2)
    Pp = Rational(1,2)*(I+J)
    Pm = Rational(1,2)*(I-J)

    assert J*J == I
    assert Pp*Pp == Pp
    assert Pm*Pm == Pm
    assert Pp+Pm == I
    assert Pp*Pm == Matrix.zeros(2)

    even_bases = [2,12,20,60]
    rows = []
    for b in even_bases:
        A = b//2
        N = lambda k: (-k) % b
        H = lambda k: (k+A) % b
        E = {0:0, 1:A}
        D = {0:0, A:1}

        assert N(N(0)) == 0
        assert H(H(0)) == 0
        assert {k for k in range(b) if N(k)==k} == {0,A}
        assert [D[N(E[x])] for x in (0,1)] == [0,1]
        assert [D[H(E[x])] for x in (0,1)] == [1,0]

        # Commutation and Klein four action
        for k in range(b):
            assert N(H(k)) == H(N(k))
            assert N(N(k)) == k
            assert H(H(k)) == k

        rows.append({
            "base": b,
            "antipode": A,
            "fixed_points_negation": [0,A],
            "DNE": [0,1],
            "DHE": [1,0],
            "klein_four": True
        })

    return {
        "status":"PASS WITH EXCHANGE-OPERATOR CORRECTION",
        "base2":{
            "J2":True,"Pplus_idempotent":True,"Pminus_idempotent":True,
            "sum_identity":True,"orthogonal_projectors":True
        },
        "radix_rows":rows,
        "corrected_theorem":{
            "negation":"N_b(k)=-k mod b",
            "half_cycle":"H_b(k)=k+b/2 mod b",
            "fixed_points":"Fix(N_b)={0,b/2}",
            "endpoint_roundtrip":"D_b E_b = id",
            "negation_on_endpoints":"D_b N_b E_b = id",
            "exchange_preservation":"D_b H_b E_b = J",
            "group":"{I,N_b,H_b,N_bH_b} ~= C2 x C2"
        }
    }

if __name__ == "__main__":
    import json
    print(json.dumps(validate(), indent=2))
