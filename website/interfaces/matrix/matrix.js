const $=id=>document.getElementById(id), log=(s)=>{$('log').textContent+=s+"\n"};
let last=null;
const C=(re=0,im=0)=>({re,im}), add=(a,b)=>C(a.re+b.re,a.im+b.im), mul=(a,b)=>C(a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re), scale=(a,s)=>C(a.re*s,a.im*s), abs2=a=>a.re*a.re+a.im*a.im;
function matVec(U,v){return [add(mul(U[0],v[0]),mul(U[1],v[1])),add(mul(U[2],v[0]),mul(U[3],v[1]))]}
function svd2(A){ // exact 2x2 SVD singular values, sufficient for one-site product/MPS pedagogic path
 const a=abs2(A[0])+abs2(A[2]), d=abs2(A[1])+abs2(A[3]), z=add(mul({re:A[0].re,im:-A[0].im},A[1]),mul({re:A[2].re,im:-A[2].im},A[3]));
 const disc=Math.sqrt(Math.max(0,(a-d)**2+4*abs2(z))); return [Math.sqrt(Math.max(0,(a+d+disc)/2)),Math.sqrt(Math.max(0,(a+d-disc)/2))];
}
function init(n){return Array.from({length:n},()=>[C(1),C(0)])}
function apply1(mps,q,U){mps[q]=matVec(U,mps[q])}
function trajectory(v,g1,gp){ // normalized stochastic trajectory, explicitly not density-matrix evolution
 const p1=Math.min(.999,Math.max(0,g1))*abs2(v[1]); if(Math.random()<p1)v=[C(1),C(0)]; else v=[v[0],scale(v[1],Math.sqrt(Math.max(0,1-g1)))];
 if(Math.random()<Math.min(.5,Math.max(0,gp)))v[1]=scale(v[1],-1); const n=Math.sqrt(abs2(v[0])+abs2(v[1]))||1;return [scale(v[0],1/n),scale(v[1],1/n)];
}
function run(){
 const n=+$('n').value,l=+$('layers').value,phi=+$('phi').value,g1=+$('g1').value,gp=+$('gphi').value,noise=$('noise').value;
 let m=init(n), H=[C(1/Math.sqrt(2)),C(1/Math.sqrt(2)),C(1/Math.sqrt(2)),C(-1/Math.sqrt(2))], R=[C(1),C(0),C(0),C(Math.cos(phi),Math.sin(phi))];
 for(let k=0;k<l;k++)for(let q=0;q<n;q++){apply1(m,q,H);apply1(m,q,R);if(noise==='trajectory')m[q]=trajectory(m[q],g1,gp)}
 // This browser reference path intentionally remains product-state χ=1; it never fakes entangling MPS contraction.
 const norm=m.reduce((p,v)=>p*(abs2(v[0])+abs2(v[1])),1); last={n,l,phi,g1,gp,noise,m,norm};
 $('norm').textContent=norm.toFixed(6);$('bond').textContent='1';$('discard').textContent='0 (reference path)';
 $('bars').innerHTML='<div class="bar" style="height:100%"></div>'; log(new Date().toISOString()+' circuit complete · reference χ=1 · '+n+' qubits · '+l+' layers');
}
function canonicalLift(){
 if(!last){run()} const out=[];
 // Explicit deterministic feature map: evaluate product-state amplitudes on the 125 codewords formed by 3 base-5 digits,
 // each digit encoded into three qubit samples. This is a feature lift, not a Hilbert-space isomorphism.
 for(let i=0;i<125;i++){let x=i,a=C(1);for(let block=0;block<3;block++){const d=x%5;x=Math.floor(x/5);const q=(block*5+d)%last.n;a=mul(a,last.m[q][d&1]);}out.push([a.re,a.im])}
 const z=Math.sqrt(out.reduce((s,a)=>s+a[0]*a[0]+a[1]*a[1],0))||1;return out.map(a=>[a[0]/z,a[1]/z]);
}
async function lift(){
 const statevector=canonicalLift(), circuit={schema:'MATRIX-CIRCUIT-1.0',qubits:last.n,layers:last.l,phase:last.phi,noise:last.noise,gamma_t1:last.g1,gamma_phase:last.gp,lift:{name:'matrix-product-feature-lift-125-v1',claim:'feature map; not Hilbert-space isomorphism'}};
 try{const r=await fetch('https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({statevector,circuit})});const x=await r.json();if(!x.ok)throw Error(x.error);const w=x.witness.witness;$('e47').textContent=(100*w.e47_weight).toFixed(3)+'%';$('e47detail').textContent='complement '+(100*w.complement_weight).toFixed(3)+'% · leakage '+w.leakage_norm.toExponential(3)+' · K² energy '+w.k2_energy.toExponential(3);log(new Date().toISOString()+' E47 witness · '+x.witness.object.state_hash.slice(0,16));window.parent.postMessage({type:'CITY_MATRIX_STATE',statevector,circuit},'*')}catch(e){$('e47').textContent='ADAPTER ERROR';$('e47detail').textContent=e.message}
}
$('run').onclick=run;$('lift').onclick=lift;run();