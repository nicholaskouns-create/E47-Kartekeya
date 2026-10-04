#!/usr/bin/env python3
"""
THE UDU_39 ATTRACTOR THEOREM
A Finite Projector Proof of Semantic-Accounting Invariance
in the Uruk Livestock Ledger P325352

Nicholas Shane Kouns
2026-10-04

This executable certifies the finite arithmetic and projector identity encoded
from the approved P325352 ledger reconstruction. It does not assert that Late
Uruk scribes used projector terminology, nor does it resolve the exact
administrative semantics of the X mark.
"""

import numpy as np

x = np.array([
    5,  # UDUNITA~c ZATU773~a
    6,  # U8
    4,  # UDUNITA~c
    1,  # U8
    3,  # UD5~a
    3,  # MASZ2
    6,  # UDUNITA~c
    2,  # U8
    2,  # X U8 -- distinguished/excluded coordinate
    7,  # MASZ2
    2,  # UD5~a
], dtype=int)

P = np.diag([1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1])
I = np.eye(len(x), dtype=int)
accepted = P @ x
rejected = (I - P) @ x

A1 = np.array([16, 6, 17], dtype=int)
A2 = np.array([9, 7, 6, 8, 9], dtype=int)
UDU_39 = int(accepted.sum())

checks = {
    "obverse_total_41": x.sum() == 41,
    "P_idempotent": np.array_equal(P @ P, P),
    "excluded_X_state_2": rejected.sum() == 2,
    "projected_state_39": accepted.sum() == 39,
    "first_reconciliation_16_6_17": A1.sum() == 39,
    "second_reconciliation_9_7_6_8_9": A2.sum() == 39,
    "representations_distinct": A1.shape != A2.shape,
    "common_invariant": accepted.sum() == A1.sum() == A2.sum() == 39,
}

for name, passed in checks.items():
    print(f"{name:40s} {'PASS' if passed else 'FAIL'}")

assert all(checks.values())

print()
print("=" * 72)
print("UDU_39 ATTRACTOR THEOREM")
print("=" * 72)
print(f"Recorded state       |x|       = {x.sum()}")
print(f"Accepted projection  |Px|      = {accepted.sum()}")
print(f"Rejected residual    |(I-P)x|  = {rejected.sum()}")
print(f"A1                    {tuple(A1)} -> {A1.sum()}")
print(f"A2                    {tuple(A2)} -> {A2.sum()}")
print("Invariant identity:  1^T P x = 16+6+17 = 9+7+6+8+9 = 39")
print(f"UDU_39                = {UDU_39}")
print(f"ALL {sum(checks.values())}/{len(checks)} CHECKS PASS")
