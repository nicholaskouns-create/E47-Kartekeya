import sympy as s, json
from pathlib import Path
out=Path(__file__).parent
p=101
D=s.diag(-6,-5,-3,0,4); B=s.diag(0,s.Rational(-1,2),s.Rational(-3,2),-3,-5)
for i,v in enumerate([12,s.Rational(147,20),s.Rational(144,35),s.Rational(9,7)]):B[i,i+1]=v;B[i+1,i]=1
vec=lambda A:s.Matrix(25,1,list(A))
basis=[D,B]; parents=[None,None]; words=['D','B']; M=s.Matrix.hstack(*map(vec,basis)); q=0
while q<len(basis) and len(basis)<25:
 for j in range(q):
  C=basis[q]*basis[j]-basis[j]*basis[q]
  if C!=s.zeros(5) and M.row_join(vec(C)).rank()>len(basis):
   basis.append(C);parents.append([q,j]);words.append(f'[{words[q]},{words[j]}]');M=M.row_join(vec(C))
   if len(basis)==25:break
 q+=1
assert len(basis)==25
exact_det=M.det(method='domain-ge')
def residue(x):
 x=s.Rational(x);return (int(x.p)%p)*pow(int(x.q)%p,-1,p)%p
A=[[residue(M[i,j]) for j in range(25)] for i in range(25)]
Am=s.Matrix(A); inv=Am.inv_mod(p); W=[[int(inv[i,j])%p for j in range(25)] for i in range(25)]
assert all(sum(A[i][k]*W[k][j] for k in range(25))%p==int(i==j) for i in range(25) for j in range(25))
Bm=[[residue(B[i,j]) for j in range(5)] for i in range(5)]
Dm=[[residue(D[i,j]) for j in range(5)] for i in range(5)]
result={'prime':p,'D':Dm,'B_rational_similarity':Bm,'parents':parents,'words':words,'basis_mod_p':[[[residue(X[i,j]) for j in range(5)] for i in range(5)] for X in basis],'column_matrix_mod_p':A,'inverse_mod_p':W,'exact_determinant':str(exact_det),'det_mod_p':int(exact_det)%p,'rank':25,'similarity':'S^-1 B S with S[0]=1 and S[i+1]=S[i]*sqrt(c_i); upper c_i, lower 1; exact complex similarity'}
(out/'certificate.json').write_text(json.dumps(result,indent=2))
# Lean and Coq proofs of modular inverse identity; the matrices and inverse are fully explicit.
lean='''/- E47 exchange Lie closure: finite-field inverse witness.\n   Compile with Lean 4; no mathlib required.\n   The identity M*W=I over F_101 proves the 25 nested commutators independent.\n   This file has NOT been compiler-tested in this environment. -/\nnamespace E47Lie\ndef prime : Nat := 101\ndef mat : List (List Nat) :=\n'''
lean+='  '+repr(A).replace('[','[').replace('] ','], ')+'\n'
lean+='def inverse : List (List Nat) :=\n  '+repr(W)+'\n'
lean+='''def entry (a : List (List Nat)) (i j : Nat) : Nat := ((a[i]?).getD [])[j]?.getD 0\ndef productEntry (i j : Nat) : Nat :=\n  ((List.range 25).foldl (fun acc k => acc + entry mat i k * entry inverse k j) 0) % prime\ndef certificate : Bool :=\n  (List.range 25).all (fun i => (List.range 25).all (fun j => productEntry i j == (if i == j then 1 else 0)))\ntheorem independent25_mod101 : certificate = true := by native_decide\nend E47Lie\n'''
(out/'E47LieClosure.lean').write_text(lean)
coq='''(* E47 exchange Lie closure: finite-field inverse witness.\n   Coq standard library; no Admitted. Not yet compiled in this environment. *)\nFrom Coq Require Import List Arith Bool.\nImport ListNotations.\nModule E47Lie.\nDefinition prime : nat := 101.\nDefinition mat : list (list nat) :=\n'''
fmt=lambda rows:'[\n'+ ';\n'.join('['+';'.join(map(str,row))+']' for row in rows)+'\n]'
coq+=fmt(A)+'.\nDefinition inverse : list (list nat) :=\n'+fmt(W)+'.\n'
coq+='''Definition entry (a : list (list nat)) (i j : nat) : nat := nth j (nth i a []) 0.\nDefinition productEntry (i j : nat) : nat :=\n  Nat.modulo (fold_left (fun acc k => acc + entry mat i k * entry inverse k j) (seq 0 25) 0) prime.\nDefinition certificate : bool :=\n  forallb (fun i => forallb (fun j => Nat.eqb (productEntry i j) (if Nat.eqb i j then 1 else 0)) (seq 0 25)) (seq 0 25).\nTheorem independent25_mod101 : certificate = true.\nProof. vm_compute. reflexivity. Qed.\nEnd E47Lie.\n'''
(out/'E47LieClosure.v').write_text(coq)
print('exact determinant:',exact_det,'mod 101:',int(exact_det)%101,'basis:',len(basis))