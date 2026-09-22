#!/usr/bin/env python3
"""SAT / Newton basin box-dimension experiment.

Babylonian/Newton -> Boolean polynomial residuals -> clause falsity
polynomials -> damped Gauss-Newton basins -> boundary -> box dimension.

Satisfying assignments are not used to construct or drive the dynamics;
they are used only after convergence to label Boolean endpoints.
"""
import argparse, json, math
from pathlib import Path
import numpy as np

CLAUSES=((1,2,3),(-1,-2,3),(1,-3,2))

def eval_formula_bits(bits):
    bits=np.asarray(bits,dtype=int)
    out=np.ones(bits.shape[:-1],dtype=bool)
    for clause in CLAUSES:
        ok=np.zeros(bits.shape[:-1],dtype=bool)
        for lit in clause:
            b=bits[...,abs(lit)-1].astype(bool)
            ok |= b if lit>0 else ~b
        out &= ok
    return out

ALL_BITS=np.array([[a,b,c] for a in (0,1) for b in (0,1) for c in (0,1)],dtype=int)
SAT_BITS=ALL_BITS[eval_formula_bits(ALL_BITS)]
SAT_KEYS=[tuple(map(int,row)) for row in SAT_BITS]
SAT_TO_LABEL={key:i for i,key in enumerate(SAT_KEYS)}

def residual_jacobian_batch(x):
    x=np.asarray(x,float); shape=x.shape[:-1]
    r=np.zeros(shape+(6,),float); j=np.zeros(shape+(6,3),float)
    for i in range(3):
        xi=x[...,i]; r[...,i]=xi*(1-xi); j[...,i,i]=1-2*xi
    for ci,clause in enumerate(CLAUSES):
        row=3+ci; vals=[]; ders=[]; idxs=[]
        for lit in clause:
            idx=abs(lit)-1; idxs.append(idx)
            if lit>0: vals.append(1-x[...,idx]); ders.append(-1.)
            else: vals.append(x[...,idx]); ders.append(1.)
        r[...,row]=vals[0]*vals[1]*vals[2]
        for k in range(3):
            other=np.ones(shape,float)
            for q in range(3):
                if q!=k: other*=vals[q]
            j[...,row,idxs[k]] += ders[k]*other
    return r,j

def solve_grid(resolution,fixed_x3=.37,max_iter=70,tol=1e-9,lam=1e-6,step_clip=1.):
    xs=np.linspace(-.5,1.5,resolution); ys=np.linspace(-.5,1.5,resolution)
    x1,x2=np.meshgrid(xs,ys)
    state=np.stack([x1,x2,np.full_like(x1,fixed_x3)],axis=-1)
    eye=np.eye(3)
    for _ in range(max_iter):
        residual,jac=residual_jacobian_batch(state)
        norm=np.linalg.norm(residual,axis=-1); active=norm>=tol
        if not np.any(active): break
        ja=jac[active]; ra=residual[active]
        a=np.einsum("nki,nkj->nij",ja,ja)+lam*eye[None,:,:]
        g=np.einsum("nki,nk->ni",ja,ra)
        delta=np.linalg.solve(a,(-g)[...,None])[...,0]
        dn=np.linalg.norm(delta,axis=-1); scale=np.ones_like(dn); large=dn>step_clip
        scale[large]=step_clip/dn[large]; delta*=scale[:,None]
        old=state[active].copy(); old_norm=norm[active].copy()
        eta=np.ones_like(old_norm); accepted=np.zeros_like(old_norm,dtype=bool); best=old.copy()
        for _ in range(18):
            trial=old+eta[:,None]*delta
            rr,_=residual_jacobian_batch(trial); nn=np.linalg.norm(rr,axis=-1)
            good=(~accepted)&(nn<=old_norm); best[good]=trial[good]; accepted|=good
            if np.all(accepted): break
            eta[~accepted]*=.5
        updated=old.copy(); updated[accepted]=best[accepted]; state[active]=updated
    rounded=np.rint(state).astype(int)
    close=np.max(np.abs(state-rounded),axis=-1)<1e-5
    valid=np.all((rounded==0)|(rounded==1),axis=-1)
    sat=np.zeros((resolution,resolution),bool); check=close&valid
    if np.any(check): sat[check]=eval_formula_bits(rounded[check])
    labels=np.full((resolution,resolution),-1,int)
    for key,label in SAT_TO_LABEL.items():
        labels[sat & np.all(rounded==np.array(key),axis=-1)] = label
    return labels

def boundary_mask(labels,neighbors=8):
    shifts=[(-1,0),(1,0),(0,-1),(0,1)]
    if neighbors==8: shifts += [(-1,-1),(-1,1),(1,-1),(1,1)]
    b=np.zeros_like(labels,dtype=bool)
    for dy,dx in shifts:
        shifted=np.roll(np.roll(labels,dy,axis=0),dx,axis=1)
        diff=shifted!=labels
        if dy<0: diff[dy:,:]=False
        elif dy>0: diff[:dy,:]=False
        if dx<0: diff[:,dx:]=False
        elif dx>0: diff[:,:dx]=False
        b|=diff
    return b

def box_count(mask,s):
    h,w=mask.shape; H=math.ceil(h/s)*s; W=math.ceil(w/s)*s
    p=np.zeros((H,W),bool); p[:h,:w]=mask
    return int(p.reshape(H//s,s,W//s,s).any(axis=(1,3)).sum())

def estimate_dimension(mask,drop_finest=True,drop_coarsest=False):
    n=mask.shape[0]; sizes=[s for s in (2,4,8,16,32,64,128) if s<=n//4]
    counts=np.array([box_count(mask,s) for s in sizes],float)
    x=np.log(n/np.asarray(sizes,float)); y=np.log(counts); idx=np.arange(len(sizes))
    if drop_finest and len(idx)>=5: idx=idx[1:]
    if drop_coarsest and len(idx)>3: idx=idx[:-1]
    slope,intercept=np.polyfit(x[idx],y[idx],1); pred=slope*x[idx]+intercept
    ss_res=np.sum((y[idx]-pred)**2); ss_tot=np.sum((y[idx]-y[idx].mean())**2)
    r2=1-ss_res/ss_tot if ss_tot>0 else 1.
    dof=max(len(idx)-2,1); s2=ss_res/dof; sxx=np.sum((x[idx]-x[idx].mean())**2)
    se=math.sqrt(s2/sxx) if sxx>0 else float("nan")
    return {"resolution":n,"box_sizes":sizes,"box_counts":counts.astype(int).tolist(),
            "fit_box_sizes":[sizes[i] for i in idx],"dimension":float(slope),
            "ci95_low":float(slope-1.96*se),"ci95_high":float(slope+1.96*se),
            "r2":float(r2),"boundary_fraction":float(mask.mean())}

def run(resolutions=(96,128,192,256,384,512)):
    estimates=[]
    for n in resolutions:
        labels=solve_grid(n); e=estimate_dimension(boundary_mask(labels,8))
        e["unresolved_fraction"]=float((labels<0).mean())
        e["basins_present"]=int(len(np.unique(labels[labels>=0])))
        estimates.append(e)
    high=np.array([e["dimension"] for e in estimates if e["resolution"]>=192])
    robust=[]
    for n in (256,384,512):
        labels=solve_grid(n)
        for neighbors in (4,8):
            robust.append(estimate_dimension(boundary_mask(labels,neighbors))["dimension"])
    mean=float(high.mean()); lo=float(high.min()); hi=float(high.max())
    return {"schema":"SAT-NEWTON-BOXDIM-1.0","clauses":[list(c) for c in CLAUSES],
      "satisfying_boolean_roots_posthoc":[list(k) for k in SAT_KEYS],
      "slice":{"x1":[-.5,1.5],"x2":[-.5,1.5],"x3_initial":.37},
      "estimates":estimates,"high_resolution_mean_dimension":mean,
      "high_resolution_range":[lo,hi],"distance_to_nearest_integer":min(abs(mean-1),abs(mean-2)),
      "noninteger_across_high_resolution_range":not(lo<=1<=hi or lo<=2<=hi),
      "robustness":{"boundary_definitions":["4-neighbor","8-neighbor"],"resolutions":[256,384,512],
                    "fit_window":"drop finest pixel scale","dimension_range":[float(min(robust)),float(max(robust))],
                    "mean_dimension":float(np.mean(robust))}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--out",default="sat_newton_boxdim_results.json")
    ap.add_argument("--resolutions",default="96,128,192,256,384,512")
    args=ap.parse_args(); result=run(tuple(int(v) for v in args.resolutions.split(",")))
    Path(args.out).write_text(json.dumps(result,indent=2)); print(json.dumps(result,indent=2))
if __name__=="__main__": main()
