export const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
export const add=(a,b)=>[a[0]+b[0],a[1]+b[1],a[2]+b[2]];
export const sub=(a,b)=>[a[0]-b[0],a[1]-b[1],a[2]-b[2]];
export const scale=(a,s)=>[a[0]*s,a[1]*s,a[2]*s];
export const dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
export const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
export const norm=a=>Math.hypot(a[0],a[1],a[2]);
export const normalize=a=>{const n=norm(a)||1;return scale(a,1/n)};
export const qNorm=q=>Math.hypot(q[0],q[1],q[2],q[3]);
export const qNormalize=q=>{const n=qNorm(q)||1;return q.map(v=>v/n)};
export const qMul=(a,b)=>[
 a[0]*b[0]-a[1]*b[1]-a[2]*b[2]-a[3]*b[3],
 a[0]*b[1]+a[1]*b[0]+a[2]*b[3]-a[3]*b[2],
 a[0]*b[2]-a[1]*b[3]+a[2]*b[0]+a[3]*b[1],
 a[0]*b[3]+a[1]*b[2]-a[2]*b[1]+a[3]*b[0]
];
export const qConj=q=>[q[0],-q[1],-q[2],-q[3]];
export const qRotate=(q,v)=>qMul(qMul(q,[0,...v]),qConj(q)).slice(1);
export const qRotateInv=(q,v)=>qRotate(qConj(q),v);
export function qFromEuler(roll,pitch,yaw){
 const cr=Math.cos(roll/2),sr=Math.sin(roll/2),cp=Math.cos(pitch/2),sp=Math.sin(pitch/2),cy=Math.cos(yaw/2),sy=Math.sin(yaw/2);
 return qNormalize([cr*cp*cy+sr*sp*sy,sr*cp*cy-cr*sp*sy,cr*sp*cy+sr*cp*sy,cr*cp*sy-sr*sp*cy]);
}
export function qToEuler(q){
 const [w,x,y,z]=q;
 const roll=Math.atan2(2*(w*x+y*z),1-2*(x*x+y*y));
 const s=clamp(2*(w*y-z*x),-1,1);const pitch=Math.asin(s);
 const yaw=Math.atan2(2*(w*z+x*y),1-2*(y*y+z*z));
 return {roll,pitch,yaw};
}
