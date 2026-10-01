#!/usr/bin/env python3
import numpy as np
from math import radians, degrees, sin, cos, atan2, sqrt, pi, asin
from itertools import permutations
np.set_printoptions(precision=10, suppress=True)

p,h=12,35; F=p+h; E=(5*p+6*h)//2; V=2*E//3
print("FEV chi",F,E,V,V-E+F)
cen={3:24,5:12,6:6,7:4,8:1}
print("pl5 sum n",sum(k*v for k,v in cen.items()),"sum(6-n)",sum((6-k)*v for k,v in cen.items()))
print("eps",repr(1/99144),"rho",repr(15/17),"Om",47/125)
Vc=8.0;Vs=4*pi/3;Vp=3.9392;c=47*(1-Vp/Vs)
print("Vs",Vs,"VvS",Vc-Vs,"VvP",Vc-Vp,"VvP/Vc",(Vc-Vp)/Vc,"VvP/Vs",(Vc-Vp)/Vs,"VvS/Vc",(Vc-Vs)/Vc,"def",1-Vp/Vs,"c",c)
for Fk in (47,188,1504):
    vp=Vs*(1-c/Fk); print(Fk,round(vp,4),round(Vc-vp,4),round((Vc-vp)/Vc,4))

def enu(la,lo):
    f,l=radians(la),radians(lo)
    return (np.array([cos(f)*cos(l),cos(f)*sin(l),sin(f)]),
            np.array([-sin(l),cos(l),0.0]),
            np.array([-sin(f)*cos(l),-sin(f)*sin(l),cos(f)]))
rD,eD,nD=enu(37.6439,-84.7729)
az=lambda A:cos(radians(A))*nD+sin(radians(A))*eD
xh,yh=az(81),az(351)
print("uD",rD,np.linalg.norm(rD)); print("xh",xh); print("yh",yh)
print("xh x yh",np.cross(xh,yh),"dots",xh@yh,xh@rD,yh@rD)
print("pl5 norm",np.linalg.norm([0.0746,-0.9934,0.6119]))
print("sep",46.6418024518-37.6439)

hms=lambda a,b,s:15*(a+b/60+s/3600)
dms=lambda g,a,b,s:g*(a+b/60+s/3600)
O=[(dms(-1,0,17,56.7),hms(5,32,0.40)),(dms(-1,1,12,6.9),hms(5,36,12.81)),(dms(-1,1,56,33.3),hms(5,40,45.53))]
G=[(29.9792,31.1342),(29.9761,31.1308),(29.9725,31.1283)]
U=lambda la,lo:enu(la,lo)[0]
Ou=[U(*x) for x in O]; Gu=[U(*x) for x in G]
def gnom(us):
    c=sum(us);c/=np.linalg.norm(c)
    la,lo=degrees(asin(c[2])),degrees(atan2(c[1],c[0]))
    r,e,n=enu(la,lo)
    return np.array([complex(u@e/(u@r),u@n/(u@r)) for u in us]),c,(r,e,n),la,lo
zO,cO,EO,laO,loO=gnom(Ou); zG,cG,EG,laG,loG=gnom(Gu)
print("Ocent",laO,loO%360,"Gcent",laG,loG)
for nm,(a_,d_) in zip(["Mint","Alnl","Alnt"],[(x[1],x[0]) for x in O]): print(nm,round(a_,4),round(d_,4))
sd=lambda z:(abs(z[1]-z[0]),abs(z[2]-z[1]),abs(z[2]-z[0]))
sO,sG=sd(zO),sd(zG)
print("O deg",[round(degrees(x),5) for x in sO],"G km",[round(x*6371.0088,4) for x in sG])
print("O ratio",[round(x/sO[0],4) for x in sO],"G ratio",[round(x/sG[0],4) for x in sG])
k=lambda z:(z[2]-z[0])/(z[1]-z[0])
print("kO",k(zO),degrees(np.angle(k(zO))),"kG",k(zG),degrees(np.angle(k(zG))),"|dk|",abs(k(zO)-k(zG)))
def fit(z,w,mir):
    if mir: z=np.conj(z)
    zt,wt=z-z.mean(),w-w.mean()
    A=(wt*np.conj(zt)).sum()/(abs(zt)**2).sum()
    zn,wn=zt/abs(z[1]-z[0]),wt/abs(w[1]-w[0])
    An=(wn*np.conj(zn)).sum()/(abs(zn)**2).sum()
    rms12=sqrt((abs(wn-An*zn)**2).sum()/3)
    zc,wc=zt/sqrt((abs(zt)**2).sum()),wt/sqrt((abs(wt)**2).sum())
    dP=sqrt(max(0,1-abs((wc*np.conj(zc)).sum())**2))
    return rms12,abs(A),degrees(np.angle(A)),dP,abs(An)
res=[]
for pm in permutations(range(3)):
    for mir in (False,True):
        r=fit(zO[list(pm)],zG,mir); res.append((round(r[0],5),pm,mir,r[1],round(r[2],3),round(r[3],5),round(r[4],5)))
res.sort()
for r in res: print(r)
b=res[0]; th=radians(b[4])
M=np.array([[1,0,0],[0,cos(th),-sin(th)],[0,sin(th),cos(th)]])
if b[2]: M=M@np.diag([1,1,-1])
R=np.column_stack(EG)@M@np.column_stack(EO).T
print("R",R,"det",np.linalg.det(R),"err",np.abs(R@cO-cG).max(),np.abs(R@R.T-np.eye(3)).max())
print("a* km/deg",b[3]*6371.0088*pi/180)
