import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const CORS={"access-control-allow-origin":"*","access-control-allow-headers":"authorization,content-type,x-agent-name","access-control-allow-methods":"GET,POST,OPTIONS"};
const SPECTRUM=[0,2,6,12,20,30,42];
const MULTIPLICITY:Record<number,number>={0:1,2:9,6:25,12:28,20:27,30:22,42:13};
type Matrix=number[][];

function matrix(v:unknown):Matrix{
  if(!Array.isArray(v)||v.length!==125||!v.every(r=>Array.isArray(r)&&r.length===2&&r.every(x=>typeof x==="number"&&Number.isFinite(x)))) throw new Error("statevector must be 125 complex amplitudes encoded as [[re,im],...]");
  return (v as Matrix).map(r=>r.slice());
}
const norm2=(a:Matrix)=>a.reduce((s,r)=>s+r[0]*r[0]+r[1]*r[1],0);
const sub=(a:Matrix,b:Matrix)=>a.map((r,i)=>[r[0]-b[i][0],r[1]-b[i][1]]);
const combine=(a:Matrix,b:Matrix,k:number)=>a.map((r,i)=>[r[0]+k*b[i][0],r[1]+k*b[i][1]]);
function casimir(state:Matrix):Matrix{
  const out=Array.from({length:125},()=>[0,0]);
  for(let i=0;i<125;i++){
    const d=[Math.floor(i/25),Math.floor(i/5)%5,i%5],m=d.map(x=>2-x),str=[25,5,1];
    const diag=18+2*(m[0]*m[1]+m[0]*m[2]+m[1]*m[2]);
    for(let c=0;c<2;c++)out[i][c]+=diag*state[i][c];
    for(let a=0;a<3;a++)for(let b=a+1;b<3;b++)for(const sign of [-1,1]){
      if(Math.abs(m[a]+sign)>2||Math.abs(m[b]-sign)>2)continue;
      const t=i-sign*str[a]+sign*str[b],coef=Math.sqrt((6-m[a]*(m[a]+sign))*(6-m[b]*(m[b]-sign)));
      for(let c=0;c<2;c++)out[t][c]+=coef*state[i][c];
    }
  }
  return out;
}
function projectRoot(state:Matrix,root:number):Matrix{
  let p=state.map(r=>r.slice());
  for(const ev of SPECTRUM.filter(v=>v!==root)){
    const cp=casimir(p);
    p=p.map((r,i)=>r.map((v,j)=>(cp[i][j]-ev*v)/(root-ev)));
  }
  return p;
}
function projectE47(state:Matrix):Matrix{return combine(projectRoot(state,6),projectRoot(state,30),1);}
function kernel(state:Matrix){const c=casimir(state),cc=casimir(c);return state.map((r,i)=>r.map((v,j)=>cc[i][j]-36*c[i][j]+180*v));}
async function digest(v:unknown){const b=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(JSON.stringify(v)));return [...new Uint8Array(b)].map(x=>x.toString(16).padStart(2,"0")).join("");}

Deno.serve(async(req:Request)=>{
  if(req.method==="OPTIONS")return new Response(null,{status:204,headers:CORS});
  if(req.method==="GET")return Response.json({service:"matrix-cube-adapter",version:2,input_basis:"spin2-tensor3-descending-m",carrier:125,output:"CITY-INVARIANT 1.0 typed E47/Cube witness + Casimir spectral bands",evidence:"numerical-demonstration",canonical_promotion:false},{headers:CORS});
  try{
    if(req.method!=="POST")return Response.json({error:"use GET or POST"},{status:405,headers:CORS});
    const body=await req.json(), amplitudes=matrix(body.statevector??body.amplitudes);
    const n2=norm2(amplitudes); if(!(n2>0))throw new Error("statevector norm must be nonzero");
    const bands=SPECTRUM.map(root=>{const pr=projectRoot(amplitudes,root);return {lambda:root,multiplicity:MULTIPLICITY[root],weight:norm2(pr)/n2,selected:root===6||root===30};});
    const spectralWeightSum=bands.reduce((s,b)=>s+b.weight,0);
    const e47FromBands=bands.filter(b=>b.selected).reduce((s,b)=>s+b.weight,0);
    const p=projectE47(amplitudes), leak=sub(amplitudes,p), k=kernel(amplitudes), e47Weight=norm2(p)/n2;
    const witness={
      schema:"CITY-INVARIANT 1.0",
      object:{name:"THE MATRIX statevector",carrier:"V2^tensor3",dimension:125,basis:"spin2-tensor3-descending-m",state_hash:await digest(amplitudes),circuit_hash:body.circuit?await digest(body.circuit):null},
      operator:{name:"E47 spectral selector",C:"J_tot^2",K:"(C-6I)(C-30I)",P47:"P6+P30"},
      invariant:{e47_dimension:47,omega_c:47/125,spectrum:SPECTRUM,multiplicities:SPECTRUM.map(x=>MULTIPLICITY[x])},
      witness:{norm:Math.sqrt(n2),spectral_bands:bands,spectral_weight_sum:spectralWeightSum,e47_weight:e47Weight,e47_weight_from_bands:e47FromBands,e47_band_parity_residual:Math.abs(e47Weight-e47FromBands),complement_weight:norm2(leak)/n2,leakage_norm:Math.sqrt(norm2(leak)),k2_energy:norm2(k),k2_energy_normalized:norm2(k)/n2},
      evidence:"numerical-demonstration",
      provenance:{source:"THE MATRIX",adapter:"matrix-cube-adapter@2",received_at:new Date().toISOString(),circuit:body.circuit??null},
      next_action:"Eligible for authenticated city-cube-bus binding/stage witness; no evidence or canonical promotion is implied."
    };
    return Response.json({ok:true,witness},{headers:{...CORS,"cache-control":"no-store"}});
  }catch(e){return Response.json({ok:false,error:e instanceof Error?e.message:String(e)},{status:400,headers:CORS});}
});