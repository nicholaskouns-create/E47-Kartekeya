import "jsr:@supabase/functions-js/edge-runtime.d.ts";

type P = {x:number;y:number;z:number};
type MoveDef = {axis:"x"|"y"|"z"; layer:number; map:(p:P)=>P};

const N = 5;
const MOVES: Record<string, MoveDef> = {
  R:  {axis:"x",layer:4,map:({x,y,z})=>({x,y:4-z,z:y})},
  L:  {axis:"x",layer:0,map:({x,y,z})=>({x,y:z,z:4-y})},
  U:  {axis:"z",layer:4,map:({x,y,z})=>({x:y,y:4-x,z})},
  D:  {axis:"z",layer:0,map:({x,y,z})=>({x:4-y,y:x,z})},
  F:  {axis:"y",layer:4,map:({x,y,z})=>({x:z,y,z:4-x})},
  B:  {axis:"y",layer:0,map:({x,y,z})=>({x:4-z,y,z:x})},
  L2: {axis:"x",layer:1,map:({x,y,z})=>({x,y:4-z,z:y})},
  M:  {axis:"x",layer:2,map:({x,y,z})=>({x,y:4-z,z:y})},
  R2: {axis:"x",layer:3,map:({x,y,z})=>({x,y:4-z,z:y})},
  B2: {axis:"y",layer:1,map:({x,y,z})=>({x:z,y,z:4-x})},
  S:  {axis:"y",layer:2,map:({x,y,z})=>({x:z,y,z:4-x})},
  F2: {axis:"y",layer:3,map:({x,y,z})=>({x:z,y,z:4-x})},
  D2: {axis:"z",layer:1,map:({x,y,z})=>({x:y,y:4-x,z})},
  E:  {axis:"z",layer:2,map:({x,y,z})=>({x:y,y:4-x,z})},
  U2: {axis:"z",layer:3,map:({x,y,z})=>({x:y,y:4-x,z})},
};
const MOVE_NAMES = Object.keys(MOVES);
const idx = (x:number,y:number,z:number) => x*25+y*5+z;
const coord = (i:number):P => ({x:Math.floor(i/25), y:Math.floor((i%25)/5), z:i%5});

function applyQuarter(pos:P[], name:string){
  const d=MOVES[name];
  if(!d) throw new Error(`unknown move ${name}`);
  for(let i=0;i<pos.length;i++) if(pos[i][d.axis]===d.layer) pos[i]=d.map(pos[i]);
}
function applyToken(pos:P[], token:string){
  const prime=token.endsWith("'");
  const name=prime?token.slice(0,-1):token;
  const turns=prime?3:1;
  for(let k=0;k<turns;k++) applyQuarter(pos,name);
}
const inverse=(m:string)=>m.endsWith("'")?m.slice(0,-1):m+"'";

function xorshift32(seed:number){
  let x=(seed>>>0)||0x6d2b79f5;
  return ()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296};
}
function makeRun(depth:number, seed:number){
  const rand=xorshift32(seed);
  const state=Array.from({length:125},(_,i)=>coord(i));
  const scramble:string[]=[];
  let prev="";
  for(let i=0;i<depth;i++){
    let m=MOVE_NAMES[Math.floor(rand()*MOVE_NAMES.length)];
    while(m===prev) m=MOVE_NAMES[Math.floor(rand()*MOVE_NAMES.length)];
    scramble.push(m); prev=m; applyToken(state,m);
  }
  let displaced=0, energy=0;
  const permutation=new Array<number>(125);
  state.forEach((p,source)=>{
    const dest=idx(p.x,p.y,p.z); permutation[source]=dest;
    const q=coord(source);
    const e=(p.x-q.x)**2+(p.y-q.y)**2+(p.z-q.z)**2;
    energy+=e; if(dest!==source) displaced++;
  });
  const solve=scramble.slice().reverse().map(inverse);
  solve.forEach(m=>applyToken(state,m));
  const restored=state.every((p,i)=>idx(p.x,p.y,p.z)===i);
  const bijective=new Set(permutation).size===125;
  const order4=MOVE_NAMES.every(m=>{
    const s=Array.from({length:125},(_,i)=>coord(i));
    for(let k=0;k<4;k++) applyQuarter(s,m);
    return s.every((p,i)=>idx(p.x,p.y,p.z)===i);
  });
  return {
    instance_id:crypto.randomUUID(),
    created_at:new Date().toISOString(),
    engine:"THE CUBE / Supabase Edge Runtime",
    carrier:{shape:[5,5,5],dimension:125,index:"25x+5y+z"},
    generators:MOVE_NAMES,
    seed:seed>>>0,
    depth,
    scramble,
    solve,
    state:{displaced,geometry_energy:energy/125,permutation},
    certificate:{bijective,all_generators_order_4:order4,inverse_restores_identity:restored,pass:bijective&&order4&&restored},
    e47:{dimension:47,omega_c:47/125,k2_gap:11664,rho_star:15/17,epsilon_star:1/99144}
  };
}
const cors={"access-control-allow-origin":"*","access-control-allow-headers":"authorization, x-client-info, apikey, content-type"};

const html=`<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>The Cube · Supabase Instance</title><style>
*{box-sizing:border-box}body{margin:0;background:#05070c;color:#eaf4ff;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}main{max-width:1050px;margin:auto;padding:28px}.eyebrow{color:#70e8ff;letter-spacing:.16em;font-size:12px}h1{font:700 clamp(52px,11vw,116px)/.82 system-ui;margin:34px 0 20px;letter-spacing:-.07em}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.card{border:1px solid #263143;background:#0a0e17;border-radius:16px;padding:18px}.big{font-size:34px;font-weight:700}.muted{color:#91a0b7}.pass{color:#79ffc0}.fail{color:#ff718e}button,input{font:inherit;background:#0f1725;color:#eaf4ff;border:1px solid #33415a;border-radius:9px;padding:10px}button{cursor:pointer;border-color:#70e8ff}.row{display:flex;gap:8px;align-items:center;flex-wrap:wrap}.word{overflow-wrap:anywhere;line-height:1.7}.perm{max-height:240px;overflow:auto;font-size:11px;color:#91a0b7}@media(max-width:760px){.grid{grid-template-columns:1fr}}</style></head><body><main><div class="eyebrow">MATHEMATICAL CITY · SERVER-SIDE GEOMETRIC COMPUTATION</div><h1>THE<br>CUBE</h1><p class="muted">Fresh 125-site Professor's Cube executions on Supabase. Each run is scrambled by legal generators, solved by the exact inverse word, and certified server-side.</p><div class="card row"><label>depth <input id="d" type="number" min="1" max="100" value="12"></label><label>seed <input id="s" type="number" min="0" value="470125"></label><button id="run">RUN INSTANCE</button></div><div id="out" class="grid"></div></main><script>
const out=document.getElementById('out');async function run(){out.innerHTML='<div class="card">executing…</div>';const base=location.pathname.replace(/\/$/,'');const d=document.getElementById('d').value,s=document.getElementById('s').value;const r=await fetch(base+'/api?depth='+encodeURIComponent(d)+'&seed='+encodeURIComponent(s));const x=await r.json();out.innerHTML='<div class="card"><div class="muted">INSTANCE</div><div class="big">'+x.instance_id.slice(0,8)+'</div><div>'+x.created_at+'</div></div><div class="card"><div class="muted">CERTIFICATE</div><div class="big '+(x.certificate.pass?'pass':'fail')+'">'+(x.certificate.pass?'PASS':'FAIL')+'</div><div>bijective '+x.certificate.bijective+' · order-4 '+x.certificate.all_generators_order_4+' · inverse '+x.certificate.inverse_restores_identity+'</div></div><div class="card"><div class="muted">SCRAMBLE · '+x.depth+' MOVES</div><div class="word">'+x.scramble.join(' ')+'</div></div><div class="card"><div class="muted">EXACT INVERSE SOLUTION</div><div class="word">'+x.solve.join(' ')+'</div></div><div class="card"><div class="muted">GEOMETRY</div><div class="big">'+x.state.displaced+'/125</div><div>displaced · E='+x.state.geometry_energy.toFixed(6)+'</div></div><div class="card"><div class="muted">E47 REFERENCE</div><div class="big">47 / 125</div><div>Ωc='+x.e47.omega_c.toFixed(3)+' · gap='+x.e47.k2_gap+' · ρ*='+(x.e47.rho_star).toFixed(6)+'</div></div><div class="card" style="grid-column:1/-1"><div class="muted">PERMUTATION · SOURCE → DESTINATION</div><div class="perm">'+x.state.permutation.map((v,i)=>i+'→'+v).join(' · ')+'</div></div>'}document.getElementById('run').onclick=run;run();</script></body></html>`;

Deno.serve((req:Request)=>{
  if(req.method==="OPTIONS") return new Response("ok",{headers:cors});
  const u=new URL(req.url);
  if(u.pathname.endsWith("/health")) return Response.json({app:"The Cube Instance",status:"ok",runtime:"supabase-edge",carrier:125,generators:15},{headers:{...cors,"cache-control":"no-store"}});
  if(u.pathname.endsWith("/api")){
    const depth=Math.max(1,Math.min(100,Number(u.searchParams.get("depth")||12)|0));
    const supplied=u.searchParams.get("seed");
    const seed=supplied===null?crypto.getRandomValues(new Uint32Array(1))[0]:(Number(supplied)>>>0);
    return Response.json(makeRun(depth,seed),{headers:{...cors,"cache-control":"no-store"}});
  }
  return new Response(html,{headers:{...cors,"content-type":"text/html; charset=utf-8","cache-control":"no-store","content-security-policy":"default-src 'self' 'unsafe-inline'; connect-src 'self'"}});
});