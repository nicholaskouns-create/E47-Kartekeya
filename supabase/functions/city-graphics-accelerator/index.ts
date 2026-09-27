import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const H={
  "access-control-allow-origin":"*",
  "access-control-allow-methods":"GET,OPTIONS",
  "content-security-policy":"default-src 'none'",
  "cross-origin-resource-policy":"cross-origin",
  "cache-control":"public,max-age=300"
};

const profiles=[
  {order:1,name:"SPECTRA",profile:"spectral-2d",priority:["batched-geometry","adaptive-dpr","worker-precompute"],host_status:"external-host-migration"},
  {order:2,name:"Fold",profile:"protein-geometry",priority:["instancing","lod","worker-geometry","adaptive-dpr"],host_status:"external-host-migration"},
  {order:3,name:"Murmuration",profile:"instanced-agents",priority:["gpu-instancing","spatial-binning","worker-simulation","adaptive-dpr"],host_status:"external-host-migration"},
  {order:4,name:"Mnemosyne",profile:"ui-low-motion",priority:["visibility-throttling","layer-caching","reduced-motion"],host_status:"external-host-migration"},
  {order:5,name:"Density",profile:"volume-field",priority:["webgpu-compute-ready","texture-atlas","adaptive-resolution"],host_status:"external-host-migration"},
  {order:6,name:"Horizon",profile:"timeseries",priority:["decimated-series","offscreen-render","visibility-throttling"],host_status:"external-host-migration"},
  {order:7,name:"Wave",profile:"field-solver",priority:["webgpu-compute-ready","ping-pong-textures","fixed-step","worker-solver"],host_status:"external-host-migration"},
  {order:8,name:"Identity",profile:"transport",priority:["batched-arrows","adaptive-dpr","worker-metrics"],host_status:"external-host-migration"},
  {order:9,name:"BUILD",profile:"instanced-construction",priority:["gpu-instancing","frustum-culling","lod","compressed-textures"],host_status:"external-host-migration"},
  {order:10,name:"SOAR",profile:"trajectory",priority:["trajectory-batching","fixed-step","adaptive-dpr"],host_status:"external-host-migration"},
  {order:11,name:"SCALAR",profile:"scalar-field",priority:["webgpu-compute-ready","field-texture","adaptive-resolution"],host_status:"external-host-migration"},
  {order:12,name:"EIDOLON",profile:"flight-simulator",priority:["webgpu-render-path","gpu-instancing","terrain-lod","ktx2-basis","temporal-upscale-ready","worker-flight-dynamics","fixed-step"],host_status:"source-migration-required"},
  {order:13,name:"SYNTAX JACOB",profile:"interstellar-flight",priority:["webgpu-render-path","adaptive-dpr","fixed-step","gpu-particles","ephemeris-decoupling","typed-e47-witness"],host_status:"integrated-github-pages"},
  {order:14,name:"InvariFold",profile:"protein-cinema",priority:["instanced-residues","lod","worker-geometry","adaptive-dpr"],host_status:"fold-payload-migration"}
];

const proofGates=[
  "accelerated_vs_reference_state_equivalence",
  "frame_rate_independence",
  "backend_fallback_equivalence"
];

const manifest={
  contract:"CITY-GRAPHICS-ACCELERATOR-1.0",
  service_version:3,
  status:"active",
  canonical_grammar:"CITY-INVARIANT 1.0",
  invariant:"Rendering acceleration must not alter solver timestep, state-transition law, deterministic seed, evidence class, provenance, or scientific outputs.",
  backends:["webgpu","webgl2","webgl1","canvas2d"],
  acceleration:["adaptive-resolution","fixed-timestep-render-decoupling","offscreen-canvas-worker-ready","visibility-throttling","wasm-simd-ready","ktx2-basis-ready"],
  quality_tiers:{ultra:"WebGPU + worker-capable",high:"WebGL2",compatible:"WebGL/Canvas"},
  proof_gates:proofGates,
  public_surface_count:profiles.length,
  module_url:"https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-graphics-accelerator?format=module",
  profiles_url:"https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-graphics-accelerator?format=profiles",
  boundary:"Performance/runtime contract only. It does not validate physical models or promote evidence class."
};

const moduleSource=String.raw`
export const CITY_GRAPHICS_CONTRACT=${JSON.stringify(manifest)};
export const CITY_GRAPHICS_PROFILES=${JSON.stringify(profiles)};
export const CITY_GRAPHICS_PROOF_GATES=${JSON.stringify(proofGates)};

function canvasBackend(){
  if(typeof document==='undefined') return 'canvas2d';
  const c=document.createElement('canvas');
  if(c.getContext('webgl2')) return 'webgl2';
  if(c.getContext('webgl')||c.getContext('experimental-webgl')) return 'webgl1';
  return 'canvas2d';
}

export function getCityGraphicsProfile(name){
  const key=String(name||'').toLowerCase();
  return CITY_GRAPHICS_PROFILES.find(p=>p.name.toLowerCase()===key)||null;
}

export async function detectCityGraphicsCapabilities(){
  const caps={
    webgpu:!!globalThis.navigator?.gpu,
    backend:canvasBackend(),
    offscreenCanvas:'OffscreenCanvas' in globalThis,
    worker:'Worker' in globalThis,
    wasm:'WebAssembly' in globalThis,
    hardwareConcurrency:globalThis.navigator?.hardwareConcurrency??null,
    deviceMemory:globalThis.navigator?.deviceMemory??null,
    dpr:globalThis.devicePixelRatio||1,
    secureContext:globalThis.isSecureContext===true
  };
  if(caps.webgpu){
    try{
      const adapter=await navigator.gpu.requestAdapter({powerPreference:'high-performance'});
      caps.webgpu=!!adapter;
      caps.backend=adapter?'webgpu':caps.backend;
    }catch{caps.webgpu=false;}
  }
  caps.tier=caps.backend==='webgpu'?'ultra':caps.backend==='webgl2'?'high':'compatible';
  return caps;
}

export function createAdaptiveFrameController(opts={}){
  const targetFps=opts.targetFps??60;
  const targetMs=1000/targetFps;
  const minScale=opts.minScale??0.55;
  const maxScale=opts.maxScale??1;
  const dprCap=opts.dprCap??2;
  let scale=maxScale,ema=targetMs,last=performance.now();
  return {
    sample(now=performance.now()){
      const dt=Math.max(.1,now-last);last=now;ema=ema*.9+dt*.1;
      if(ema>targetMs*1.18)scale=Math.max(minScale,scale-.04);
      else if(ema<targetMs*.88)scale=Math.min(maxScale,scale+.02);
      return scale;
    },
    pixelRatio(){return Math.min(globalThis.devicePixelRatio||1,dprCap)*scale;},
    get scale(){return scale;},
    get frameMs(){return ema;}
  };
}

export function attachAdaptiveCanvas(canvas,opts={}){
  if(!(canvas instanceof HTMLCanvasElement))throw new TypeError('canvas required');
  const ctl=createAdaptiveFrameController(opts);
  const resize=()=>{
    const r=canvas.getBoundingClientRect();
    const p=ctl.pixelRatio();
    const w=Math.max(1,Math.floor(r.width*p));
    const h=Math.max(1,Math.floor(r.height*p));
    if(canvas.width!==w)canvas.width=w;
    if(canvas.height!==h)canvas.height=h;
    canvas.dataset.cityPixelRatio=String(p);
  };
  const ro='ResizeObserver' in globalThis?new ResizeObserver(resize):null;
  ro?.observe(canvas);resize();
  return {controller:ctl,resize,dispose(){ro?.disconnect();}};
}

export function createFixedStepLoop({step,render,fixedDt=1/60,maxCatchup=5,controller=null}){
  let running=false,raf=0,last=0,acc=0;
  const frame=(t)=>{
    if(!running)return;
    if(!last)last=t;
    const elapsed=Math.min(.25,(t-last)/1000);last=t;
    if(typeof document!=='undefined'&&document.hidden){raf=requestAnimationFrame(frame);return;}
    acc+=elapsed;let n=0;
    while(acc>=fixedDt&&n<maxCatchup){step(fixedDt);acc-=fixedDt;n++;}
    controller?.sample(t);render(acc/fixedDt);raf=requestAnimationFrame(frame);
  };
  return {start(){if(!running){running=true;last=0;raf=requestAnimationFrame(frame);}},stop(){running=false;cancelAnimationFrame(raf);}};
}

export function transferCanvasToWorker(canvas,worker){
  if(!canvas?.transferControlToOffscreen||!worker)return false;
  const offscreen=canvas.transferControlToOffscreen();
  worker.postMessage({type:'CITY_OFFSCREEN_CANVAS',canvas:offscreen},[offscreen]);
  return true;
}

export async function bootstrapCityGraphics(opts={}){
  const capabilities=await detectCityGraphicsCapabilities();
  const canvases=[...document.querySelectorAll(opts.selector??'canvas[data-city-gpu],canvas.city-gpu')];
  const attachments=canvases.map(c=>attachAdaptiveCanvas(c,opts));
  const detail={contract:CITY_GRAPHICS_CONTRACT,capabilities,attachments,profile:getCityGraphicsProfile(opts.app)};
  globalThis.__CITY_GRAPHICS__=detail;
  globalThis.dispatchEvent(new CustomEvent('citygraphicsready',{detail}));
  return detail;
}
`;

Deno.serve((req:Request)=>{
  if(req.method==='OPTIONS')return new Response('ok',{headers:H});
  if(req.method!=='GET')return new Response(JSON.stringify({error:'GET required'}),{status:405,headers:{...H,'content-type':'application/json'}});
  const u=new URL(req.url);
  const format=u.searchParams.get('format');
  if(format==='module')return new Response(moduleSource,{headers:{...H,'content-type':'text/javascript; charset=utf-8','cache-control':'public,max-age=3600'}});
  if(format==='profiles')return new Response(JSON.stringify({schema:'CITY-GRAPHICS-PROFILES-1.0',contract:manifest.contract,proof_gates:proofGates,surfaces:profiles,boundary:manifest.boundary},null,2),{headers:{...H,'content-type':'application/json; charset=utf-8'}});
  if(u.searchParams.get('health')==='1')return new Response(JSON.stringify({status:'ok',service_version:2,contract:manifest.contract,public_surface_count:profiles.length,proof_gate_count:proofGates.length}),{headers:{...H,'content-type':'application/json; charset=utf-8','cache-control':'no-store'}});
  return new Response(JSON.stringify(manifest,null,2),{headers:{...H,'content-type':'application/json; charset=utf-8'}});
});
