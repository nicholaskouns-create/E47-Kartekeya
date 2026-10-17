import torch, math
T=torch.complex128; R=torch.float64
I5=torch.eye(5,dtype=T); m=torch.arange(2,-3,-1,dtype=R)
Sp=torch.zeros((5,5),dtype=T)
for i in range(1,5):
 x=m[i].item();Sp[i-1,i]=math.sqrt((2-x)*(3+x))
Sx=(Sp+Sp.conj().T)/2;Sy=(Sp-Sp.conj().T)/(2j);Sz=torch.diag(m).to(T)
k=torch.kron
J=[k(k(s,I5),I5)+k(k(I5,s),I5)+k(k(I5,I5),s) for s in [Sx,Sy,Sz]]
C=sum((a@a for a in J)); I=torch.eye(125,dtype=T)
w,V=torch.linalg.eigh(C);P=V[:,((w-6).abs()<1e-7)|((w-30).abs()<1e-7)]
P=P@P.conj().T
K=(C-6*I)@(C-30*I); A=K@K
vals=sorted(set(int(((l-6)*(l-30))**2) for l in [0,2,6,12,20,30,42] if l not in [6,30]))
print('nonzero eigenvalues K2:',vals)
Q=I.clone()
for mu in vals: Q=Q@(I-A/mu)
print('polynomial projector Fro error',torch.linalg.matrix_norm(Q-P).item())
print('poly idempotence Fro error',torch.linalg.matrix_norm(Q@Q-Q).item())
print('poly trace',torch.trace(Q).real.item())
G=I-A/99144
G220=torch.linalg.matrix_power(G,220)
print('iterative 220 Fro error',torch.linalg.matrix_norm(G220-P).item())
print('expected operator norm', (15/17)**220)
print('polynomial projector operator error',torch.linalg.matrix_norm(Q-P,ord=2).item())
print('iterative projector operator error',torch.linalg.matrix_norm(G220-P,ord=2).item())
B=C@(C-42*I)@(C-31*I)@(C-20*I)@(C-12*I)@(C-2*I)/1814400
print('Casimir polynomial projector Fro error',torch.linalg.matrix_norm(B-P).item())
print('Casimir polynomial projector operator error',torch.linalg.matrix_norm(B-P,ord=2).item())
