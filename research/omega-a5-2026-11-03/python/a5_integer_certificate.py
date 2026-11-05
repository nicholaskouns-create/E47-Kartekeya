import numpy as np
from sympy.combinatorics.named_groups import AlternatingGroup
G=list(AlternatingGroup(5).generate_schreier_sims())
assert len(G)==60
idx={tuple(g.array_form):i for i,g in enumerate(G)}
A=np.ones((60,60),dtype=np.int64)
for g in G:
 c={1:5,2:1,3:-1,5:0}[int(g.order())]
 if c:
  for j,h in enumerate(G):
   A[idx[tuple((g*h).array_form)],j]+=5*c
assert np.array_equal(A@A,60*A)
assert np.trace(A)==1560
assert np.linalg.matrix_rank(A.astype(float))==26
print('A5 exact integer identity PASS; projector rank 26')
