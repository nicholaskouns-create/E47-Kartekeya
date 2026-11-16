// SKYRMION RT3 · integrators.
// RK4 is the fixed-step workhorse. Dormand-Prince 5(4) is the adaptive mode: it
// produces a fifth-order step and a fourth-order companion from the same stages,
// so the difference between them is a free local error estimate.
const A=[
 [],
 [1/5],
 [3/40,9/40],
 [44/45,-56/15,32/9],
 [19372/6561,-25360/2187,64448/6561,-212/729],
 [9017/3168,-355/33,46732/5247,49/176,-5103/18656],
 [35/384,0,500/1113,125/192,-2187/6784,11/84]
];
const C=[0,1/5,3/10,4/5,8/9,1,1];
const B5=[35/384,0,500/1113,125/192,-2187/6784,11/84,0];
const B4=[5179/57600,0,7571/16695,393/640,-92097/339200,187/2100,1/40];

export function rk4(y,dt,f){
 const n=y.length,k1=f(y,0);
 const y2=new Array(n),y3=new Array(n),y4=new Array(n),out=new Array(n);
 for(let i=0;i<n;i++)y2[i]=y[i]+dt*.5*k1[i];
 const k2=f(y2,dt*.5);
 for(let i=0;i<n;i++)y3[i]=y[i]+dt*.5*k2[i];
 const k3=f(y3,dt*.5);
 for(let i=0;i<n;i++)y4[i]=y[i]+dt*k3[i];
 const k4=f(y4,dt);
 for(let i=0;i<n;i++)out[i]=y[i]+dt*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6;
 return {y:out,k1,stages:4};
}

export class DormandPrince{
 constructor({absTol=1e-8,relTol=1e-7,minDt=1/4000,maxDt=1/30,safety=.9}={}){
  this.schema='RT3-DOPRI54-1.0';
  Object.assign(this,{absTol,relTol,minDt,maxDt,safety});
  this.lastError=0;this.rejects=0;this.accepts=0;this.stages=0;
 }
 // Advances exactly dt in one or more internally sized substeps. The caller keeps a
 // fixed outer cadence; only the inner step adapts.
 integrate(y0,dt,f,suggestedDt=dt){
  let y=y0.slice(),t=0,h=Math.min(Math.max(suggestedDt,this.minDt),dt,this.maxDt),k1=null;
  let guard=0;
  while(t<dt-1e-12&&guard++<64){
   h=Math.min(h,dt-t);
   const n=y.length,k=new Array(7);
   k[0]=k1||f(y,t);
   for(let s=1;s<7;s++){
    const ys=new Array(n);
    for(let i=0;i<n;i++){let acc=y[i];for(let j=0;j<s;j++)acc+=h*A[s][j]*k[j][i];ys[i]=acc}
    k[s]=f(ys,t+C[s]*h);
   }
   this.stages+=7;
   const y5=new Array(n);let err=0;
   for(let i=0;i<n;i++){
    let a5=y[i],a4=y[i];
    for(let s=0;s<7;s++){a5+=h*B5[s]*k[s][i];a4+=h*B4[s]*k[s][i]}
    y5[i]=a5;
    const sc=this.absTol+this.relTol*Math.max(Math.abs(y[i]),Math.abs(a5));
    const e=(a5-a4)/sc;err+=e*e;
   }
   err=Math.sqrt(err/n);
   if(err<=1||h<=this.minDt*1.0000001){
    y=y5;t+=h;this.accepts++;this.lastError=err;
    k1=k[6]; // First-same-as-last: stage 7 is the derivative at the accepted point.
    h=Math.min(this.maxDt,h*Math.min(5,Math.max(.2,this.safety*Math.pow(err||1e-12,-.2))));
   }else{
    this.rejects++;k1=null;
    h=Math.max(this.minDt,h*Math.max(.1,this.safety*Math.pow(err,-.25)));
   }
  }
  return {y,nextDt:h,error:this.lastError};
 }
 stats(){return {schema:this.schema,accepts:this.accepts,rejects:this.rejects,stages:this.stages,lastError:this.lastError}}
}
