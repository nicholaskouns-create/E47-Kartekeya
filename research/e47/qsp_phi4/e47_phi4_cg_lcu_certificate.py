"""E47 product-basis CG / degree-4 QSP / 500D LCU, reproducible NumPy certificate.
Run: OPENBLAS_NUM_THREADS=1 python e47_phi4_cg_lcu_certificate.py
"""
import json, math, hashlib
from pathlib import Path
import numpy as np

N=125
mvals=(2,1,0,-1,-2)
I125=np.eye(N,dtype=complex)

def cg(j1,j2,m1,m2,J,M):
    if m1+m2!=M or abs(j1-j2)>J or J>j1+j2 or abs(M)>J:return 0.
    pref=math.sqrt((2*J+1)*math.factorial(J+j1-j2)*math.factorial(J-j1+j2)*math.factorial(j1+j2-J)/math.factorial(j1+j2+J+1))
    tm=math.sqrt(math.factorial(J+M)*math.factorial(J-M)*math.factorial(j1-m1)*math.factorial(j1+m1)*math.factorial(j2-m2)*math.factorial(j2+m2))
    val=0.
    for k in range(max(0,j2-J-m1,j1-J+m2),min(j1+j2-J,j1-m1,j2+m2)+1):
        den=(math.factorial(k)*math.factorial(j1+j2-J-k)*math.factorial(j1-m1-k)*math.factorial(j2+m2-k)*math.factorial(J-j2+m1+k)*math.factorial(J-j1-m2+k))
        val+=(-1.)**k/den
    return pref*tm*val

def coupled_basis():
    U=np.zeros((N,N),complex);labels=[];col=0
    for J in range(7):
        for j12 in range(5):
            if abs(j12-2)<=J<=j12+2:
                for M in range(J,-J-1,-1):
                    labels.append((J,j12,M))
                    for i,m1 in enumerate(mvals):
                        for j,m2 in enumerate(mvals):
                            m12=m1+m2
                            if abs(m12)>j12:continue
                            c1=cg(2,2,m1,m2,j12,m12)
                            for k,m3 in enumerate(mvals):
                                if m12+m3==M: U[i*25+j*5+k,col]=c1*cg(j12,2,m12,m3,J,M)
                    col+=1
    assert col==125
    return U,labels

def phases_exact_pair():
    P=np.array([353,0,-2176+272j,0,2048],complex)/353
    R=np.array([0,-1152+16j*math.sqrt(817),0,2048],complex)/353
    rev=[]
    for d in range(4,0,-1):
        phi=.5*np.angle(P[d]/R[d-1]);rev.append(float(phi))
        em,ep=np.exp(-1j*phi),np.exp(1j*phi)
        Pnew=(em*np.r_[0,P]+ep*(np.r_[R,0,0]-np.r_[0,0,R]))[:d]
        if d>1:R=(-em*P+ep*np.r_[0,R])[:d-1]
        P=Pnew
    rev.append(float(np.angle(P[0])))
    return np.array(rev[::-1]),float(abs(abs(P[0])-1))

def z_phase(phi):
    return np.block([[np.exp(1j*phi)*I125,np.zeros((N,N),complex)], [np.zeros((N,N),complex),np.exp(-1j*phi)*I125]])

def run():
    Ucg,labels=coupled_basis()
    Jz1=np.diag(mvals).astype(complex)
    Jp=np.zeros((5,5),complex)
    for i in range(4):
        m=mvals[i+1]
        Jp[i,i+1]=math.sqrt(6-m*(m+1))
    Jx=(Jp+Jp.conj().T)/2; Jy=-.5j*(Jp-Jp.conj().T);I5=np.eye(5)
    def total(g):return np.kron(np.kron(g,I5),I5)+np.kron(np.kron(I5,g),I5)+np.kron(np.kron(I5,I5),g)
    X,Y,Z=[total(g) for g in (Jx,Jy,Jz1)]
    C=X@X+Y@Y+Z@Z
    K=(C-6*I125)@(C-30*I125)
    Cc=Ucg.conj().T@C@Ucg
    Kc=Ucg.conj().T@K@Ucg
    expectC=np.array([J*(J+1) for J,j12,M in labels],float)
    expectK=(expectC-6)*(expectC-30)
    idx=np.array([i for i,(J,j12,M) in enumerate(labels) if J in (2,5)])
    Pcg=np.diag(np.isin(np.arange(125),idx).astype(float))
    P=Ucg@Pcg@Ucg.conj().T
    a=np.abs(expectK)/432; b=np.sqrt(np.maximum(0,1-a*a))
    A=Ucg@np.diag(a)@Ucg.conj().T
    B=Ucg@np.diag(b)@Ucg.conj().T
    W=np.block([[A,1j*B],[1j*B,A]])
    phi,phase_norm=phases_exact_pair()
    U=z_phase(float(phi[0]))
    for angle in phi[1:]:U=U@W@z_phase(float(angle))
    # LCU Hadamard–controlled(U,U†)–Hadamard.
    I250=np.eye(250,dtype=complex); O250=np.zeros((250,250),complex)
    H=np.kron(np.array([[1,1],[1,-1]],complex)/math.sqrt(2),I250)
    ctrl=np.block([[U,O250],[O250,U.conj().T]])
    V=H@ctrl@H
    targetQ=I125-(2176/353)*(A@A)+(2048/353)*np.linalg.matrix_power(A,4)
    expectedP=targetQ+1j*(272/353)*(A@A)
    records={
       'cg_unitarity_F':float(np.linalg.norm(Ucg.conj().T@Ucg-I125)),
       'casimir_diagonalization_F':float(np.linalg.norm(Cc-np.diag(expectC))),
       'K_diagonalization_F':float(np.linalg.norm(Kc-np.diag(expectK))),
       'projector_rank':int(np.linalg.matrix_rank(P)),
       'projector_idempotence_F':float(np.linalg.norm(P@P-P)),
       'kernel_annihilation_F':float(np.linalg.norm(K@P)),
       'phase_list_radians':[float(v) for v in phi],
       'stripping_final_phase_modulus_defect':phase_norm,
       'W250_unitarity_F':float(np.linalg.norm(W.conj().T@W-I250)),
       'U250_unitarity_F':float(np.linalg.norm(U.conj().T@U-I250)),
       'U250_top_left_vs_complex_P_F':float(np.linalg.norm(U[:125,:125]-expectedP)),
       'V500_unitarity_F':float(np.linalg.norm(V.conj().T@V-np.eye(500))),
       'V500_nested_top_left_vs_Q4_F':float(np.linalg.norm(V[:125,:125]-targetQ)),
       'Q4_distance_P47_2':float(np.linalg.norm(targetQ-P,ord=2)),
       'Q4_distance_exact':225/353,
       'coupled_J2_indices':[i for i,l in enumerate(labels) if l[0]==2],
       'coupled_J5_indices':[i for i,l in enumerate(labels) if l[0]==5],
    }
    tests={k:(v<1e-10) for k,v in records.items() if k.endswith('_F') or k=='stripping_final_phase_modulus_defect'}
    tests['rank_47']=records['projector_rank']==47
    tests['bound']=abs(records['Q4_distance_P47_2']-225/353)<1e-10
    tests['index_layout']=records['coupled_J2_indices']==list(range(10,35)) and records['coupled_J5_indices']==list(range(90,112))
    assert all(tests.values()),tests
    result={'tests':tests,'measurements':records}
    canonical=json.dumps(result,sort_keys=True,separators=(',',':'),allow_nan=False)
    out={'sha256':hashlib.sha256(canonical.encode()).hexdigest(),'payload':result}
    dest=Path(__file__).with_name('e47_phi4_cg_lcu_receipt.json')
    dest.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print('PASS',len(tests),'/',len(tests))
    for key in ('cg_unitarity_F','casimir_diagonalization_F','K_diagonalization_F','U250_unitarity_F','V500_unitarity_F','V500_nested_top_left_vs_Q4_F','Q4_distance_P47_2'):
        print(key,records[key])
    print('phases',phi)
    print('receipt',dest)

if __name__=='__main__':run()