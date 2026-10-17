"""MANTA programmable-matter reference engine.

Exact algebra:
  V = V2^⊗3, dim 125
  K = (C-6I)(C-30I)
  ker K has dimension 47
  Gamma = I - eps K^2

Simulation layer:
  125 spectral coordinates -> 125 Manta control nodes -> constrained morphing geometry.

The geometry bridge is a software model. It is not a claim that E47 physically deforms matter.
"""
from dataclasses import dataclass
from enum import Enum
import numpy as np

CASIMIR=np.array([0.,2.,6.,12.,20.,30.,42.])
MULT=np.array([1,9,25,28,27,22,13])
C=np.repeat(CASIMIR,MULT)
K=(C-6.0)*(C-30.0)
K2=K*K
P=((C==6.0)|(C==30.0)).astype(float)
EPS_STAR=1.0/99144.0
assert C.size==125 and int(P.sum())==47

def gamma_step(psi,eps=EPS_STAR):
    return (1.0-eps*K2)*psi

def capture(psi):
    d=np.vdot(psi,psi).real
    if d==0:return 0.0
    q=P*psi
    return float(np.vdot(q,q).real/d)

def leak(psi):
    d=np.linalg.norm(psi)
    return 0.0 if d==0 else float(np.linalg.norm(K2*psi)/d)

@dataclass
class MantaNode:
    index:int
    base_position:np.ndarray
    position:np.ndarray
    activation:float=0.0
    stiffness:float=1.0
    anisotropy:float=0.0
    phase:float=0.0

def build_manta_nodes():
    nodes=[]
    for a in range(5):
        for b in range(5):
            for c in range(5):
                i=a*25+b*5+c
                u=(a-2)/2; v=(b-2)/2; w=(c-2)/2
                x=4.0*u
                z=2.5*v*(1.0-.25*abs(u))
                y=.20*(1-u*u)-.12*v*v+.08*w
                p=np.array([x,y,z],dtype=float)
                nodes.append(MantaNode(i,p.copy(),p.copy()))
    return nodes

class MorphMode(Enum):
    CRUISE=0
    MANEUVER=1
    TRANSITION=2
    RECOVERY=3

@dataclass
class PilotInput:
    pitch:float=0.0
    roll:float=0.0
    yaw:float=0.0
    morph:float=0.0

def spectral_activation(psi):
    amp=np.abs(psi)
    m=amp.max()
    return amp/m if m>0 else amp

def update_manta(nodes,psi,pilot,mode=MorphMode.CRUISE,strength=.45):
    act=spectral_activation(psi)
    coh=capture(psi)
    morph=float(np.clip(pilot.morph,0.0,1.0))
    for n in nodes:
        i=n.index
        x,y,z=n.base_position
        a=act[i]
        n.activation=float(a)
        n.stiffness=.5+1.5*a
        n.anisotropy=coh*a
        n.phase=float(np.angle(psi[i]))
        spectral_y=strength*(a-.5)*coh
        pitch_deform=pilot.pitch*.15*z
        roll_deform=pilot.roll*.12*np.sign(x)*abs(x)
        if mode==MorphMode.CRUISE:sweep=1.0
        elif mode==MorphMode.MANEUVER:sweep=1.0-.12*morph
        elif mode==MorphMode.TRANSITION:sweep=1.0-.45*morph
        else:sweep=.85+.15*coh
        n.position[:]=[
            x*sweep,
            y+spectral_y+pitch_deform+roll_deform,
            z+.06*np.sin(n.phase)*a,
        ]

def smooth_geometry(nodes,alpha=.12):
    pos=np.array([n.position for n in nodes])
    out=pos.copy()
    idx=lambda a,b,c:a*25+b*5+c
    for a in range(5):
        for b in range(5):
            for c in range(5):
                ns=[]
                for da,db,dc in ((1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)):
                    aa,bb,cc=a+da,b+db,c+dc
                    if 0<=aa<5 and 0<=bb<5 and 0<=cc<5:
                        ns.append(pos[idx(aa,bb,cc)])
                if ns:
                    i=idx(a,b,c)
                    out[i]=(1-alpha)*pos[i]+alpha*np.mean(ns,axis=0)
    for n,p in zip(nodes,out):
        n.position[:]=p

class MantaEngine:
    def __init__(self,seed=470125):
        r=np.random.default_rng(seed)
        psi=r.normal(size=125)+1j*r.normal(size=125)
        self.psi=psi/np.linalg.norm(psi)
        self.nodes=build_manta_nodes()
        self.step_number=0

    def step(self,pilot=None,mode=MorphMode.CRUISE):
        pilot=pilot or PilotInput()
        self.psi=gamma_step(self.psi)
        d=np.linalg.norm(self.psi)
        if d>0:self.psi/=d
        update_manta(self.nodes,self.psi,pilot,mode)
        smooth_geometry(self.nodes)
        self.step_number+=1
        return self.telemetry()

    def telemetry(self):
        return {
            "step":self.step_number,
            "e47_capture":capture(self.psi),
            "kernel_dimension":int(P.sum()),
            "carrier_dimension":len(self.psi),
            "omega_c":47/125,
            "residual":leak(self.psi),
            "geometry_nodes":len(self.nodes),
            "bridge":"spectral-state -> control-field -> simulated-geometry",
        }

    def geometry(self):
        return np.array([n.position for n in self.nodes])

    def frame(self):
        state=self.telemetry()
        state.update({
            "geometry":self.geometry().astype(np.float32).reshape(-1).tolist(),
            "activation":[float(n.activation) for n in self.nodes],
            "stiffness":[float(n.stiffness) for n in self.nodes],
            "anisotropy":[float(n.anisotropy) for n in self.nodes],
        })
        return state

    def step_packet(self,pitch=0.0,roll=0.0,yaw=0.0,morph=0.0,mode="CRUISE"):
        pilot=PilotInput(
            pitch=float(pitch),
            roll=float(roll),
            yaw=float(yaw),
            morph=float(morph),
        )
        morph_mode=mode if isinstance(mode,MorphMode) else MorphMode[str(mode).upper()]
        self.step(pilot,morph_mode)
        return self.frame()

if __name__=="__main__":
    manta=MantaEngine()
    pilot=PilotInput(pitch=.15,roll=.25,morph=.65)
    for _ in range(50):
        state=manta.step(pilot,MorphMode.TRANSITION)
    print(state)
    print("geometry",manta.geometry().shape)
