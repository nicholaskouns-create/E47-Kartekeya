import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import postgres from "postgres";

const sql = postgres(Deno.env.get("SUPABASE_DB_URL")!, { prepare: false, max: 1 });
const ZERO = "0".repeat(64);
const ID = Array.from({ length: 125 }, (_, i) => i);
const BASE = ["R","L","U","D","F","B","L2","M","R2","B2","S","F2","D2","E","U2"] as const;
const SPEC: Record<string,["x"|"y"|"z",number,number]> = {
  R:["x",4,1], L:["x",0,-1], U:["y",4,1], D:["y",0,-1], F:["z",4,1], B:["z",0,-1],
  R2:["x",3,1], M:["x",2,-1], L2:["x",1,-1], F2:["z",3,1], S:["z",2,1], B2:["z",1,-1],
  U2:["y",3,1], E:["y",2,-1], D2:["y",1,-1]
};
const CORS = {"access-control-allow-origin":"*","access-control-allow-headers":"authorization,content-type,x-agent-name","access-control-allow-methods":"GET,POST,OPTIONS"};

class AppError extends Error { constructor(public status:number, message:string){ super(message); } }
const coords=(i:number):[number,number,number]=>[Math.floor(i/25),Math.floor(i/5)%5,i%5];
const idx=(x:number,y:number,z:number)=>25*x+5*y+z;
function rot(x:number,y:number,z:number,a:string,d:number):[number,number,number]{
  if(a==="x"){ let Y=y-2,Z=z-2; [Y,Z]=d>0?[-Z,Y]:[Z,-Y]; return [x,Math.round(Y+2),Math.round(Z+2)]; }
  if(a==="y"){ let X=x-2,Z=z-2; [X,Z]=d>0?[Z,-X]:[-Z,X]; return [Math.round(X+2),y,Math.round(Z+2)]; }
  let X=x-2,Y=y-2; [X,Y]=d>0?[-Y,X]:[Y,-X]; return [Math.round(X+2),Math.round(Y+2),z];
}
function parseMove(m:string){
  const prime=m.endsWith("'"); const base=prime?m.slice(0,-1):m;
  const s=SPEC[base]; if(!s) throw new AppError(400,`invalid move: ${m}`);
  return {base,axis:s[0],layer:s[1],dir:s[2]*(prime?-1:1)};
}
function applyMove(state:number[], m:string){
  const {axis,layer,dir}=parseMove(m); const out=state.slice();
  for(let p=0;p<125;p++){
    const [x,y,z]=coords(p); const c={x,y,z}; if(c[axis]!==layer) continue;
    const [X,Y,Z]=rot(x,y,z,axis,dir); out[idx(X,Y,Z)]=state[p];
  }
  return out;
}
const inv=(m:string)=>m.endsWith("'")?m.slice(0,-1):m+"'";
function metrics(state:number[]){
  let displaced=0, e=0;
  for(let p=0;p<125;p++){
    const cubie=state[p]; if(cubie!==p) displaced++;
    const [x,y,z]=coords(p), [a,b,c]=coords(cubie); e+=(x-a)**2+(y-b)**2+(z-c)**2;
  }
  return {displaced, geometry_energy:e/125};
}
function bijective(state:number[]){ return state.length===125 && new Set(state).size===125 && state.every(v=>Number.isInteger(v)&&v>=0&&v<125); }
function rng(seed:number){ let t=seed>>>0; return ()=>{ t+=0x6D2B79F5; let r=Math.imul(t^(t>>>15),1|t); r^=r+Math.imul(r^(r>>>7),61|r); return ((r^(r>>>14))>>>0)/4294967296; }; }
function scramble(seed:number, depth:number){
  const R=rng(seed), out:string[]=[]; let prev="";
  for(let i=0;i<depth;i++){
    let b=""; do{ b=BASE[Math.floor(R()*BASE.length)]; }while(b===prev && BASE.length>1); prev=b;
    out.push(R()<0.5?b:b+"'");
  }
  return out;
}
async function sha256(value:unknown){ const bytes=new TextEncoder().encode(JSON.stringify(value)); const d=await crypto.subtle.digest("SHA-256",bytes); return [...new Uint8Array(d)].map(x=>x.toString(16).padStart(2,"0")).join(""); }
function decodeClaims(req:Request){
  const h=req.headers.get("authorization")||""; const token=h.replace(/^Bearer\s+/i,""); const parts=token.split(".");
  if(parts.length<2) throw new AppError(401,"missing bearer token");
  try{ let s=parts[1].replace(/-/g,"+").replace(/_/g,"/"); s+="=".repeat((4-s.length%4)%4); const p=JSON.parse(atob(s)); const actor=p.sub||p.role; if(!actor) throw 0; return {actor:String(actor),role:String(p.role||"")}; }
  catch{ throw new AppError(401,"invalid bearer token"); }
}
function source(req:Request){ return (req.headers.get("x-agent-name")||"cube-state").slice(0,128); }
function normalizeRow(r:any){ return {...r, move_count:Number(r.move_count), ledger_seq:Number(r.ledger_seq), seed:Number(r.seed)}; }
function view(r:any){
  r=normalizeRow(r); const m=metrics(r.permutation);
  return {id:r.id,owner_sub:r.owner_sub,created_at:r.created_at,updated_at:r.updated_at,seed:r.seed,status:r.status,move_count:r.move_count,ledger_seq:r.ledger_seq,head_hash:r.head_hash,word:r.word,permutation:r.permutation,metrics:m,carrier:{shape:[5,5,5],dimension:125,index:"25x+5y+z"},e47:{dimension:47,omega_c:47/125,k2_gap:11664,epsilon_star:1/99144,rho_star:15/17},certificate:{bijective:bijective(r.permutation),identity:m.displaced===0}};
}
function authorize(row:any, c:{actor:string,role:string}){ if(c.role!=="service_role" && row.owner_sub!==c.actor) throw new AppError(403,"instance belongs to another subject"); }
async function appendEvent(tx:any,row:any,kind:string,move:string|null,actor:string,perm:number[],details:any,src:string){
  const seq=Number(row.ledger_seq)+1, prev=row.head_hash, met=metrics(perm);
  const hash=await sha256({instance_id:row.id,seq,kind,move,actor,prev_hash:prev,permutation:perm,details});
  await tx`insert into public.cube_moves(instance_id,seq,kind,move,source,prev_hash,hash,displaced,geometry_energy,permutation,actor,details)
    values(${row.id}::uuid,${seq},${kind},${move},${src},${prev},${hash},${met.displaced},${met.geometry_energy},${JSON.stringify(perm)}::jsonb,${actor},${JSON.stringify(details||{})}::jsonb)`;
  row.ledger_seq=seq; row.head_hash=hash; return {seq,hash,...met};
}
async function save(tx:any,row:any){
  await tx`update public.cube_instances set status=${row.status},permutation=${JSON.stringify(row.permutation)}::jsonb,word=${JSON.stringify(row.word)}::jsonb,move_count=${row.move_count},ledger_seq=${row.ledger_seq},head_hash=${row.head_hash},owner_sub=${row.owner_sub},metadata=${JSON.stringify(row.metadata||{})}::jsonb where id=${row.id}::uuid`;
}
async function load(tx:any,id:string){ const a=await tx`select id::text,created_at,updated_at,seed,status,permutation,word,move_count,ledger_seq,head_hash,owner_sub,metadata from public.cube_instances where id=${id}::uuid for update`; if(!a.length) throw new AppError(404,"cube instance not found"); return normalizeRow(a[0]); }
async function applyWord(tx:any,row:any,word:string[],kind:string,actor:string,src:string,details:any){
  for(const mv of word){ row.permutation=applyMove(row.permutation,mv); row.word=[...row.word,mv]; row.move_count++; await appendEvent(tx,row,kind,mv,actor,row.permutation,details,src); }
}

const ORDER4=BASE.every(g=>{let s=ID.slice(); for(let i=0;i<4;i++) s=applyMove(s,g); return s.every((v,i)=>v===i);});

Deno.serve(async(req:Request)=>{
  if(req.method==="OPTIONS") return new Response(null,{status:204,headers:CORS});
  try{
    const c=decodeClaims(req), src=source(req), u=new URL(req.url);
    if(req.method==="GET"){
      const id=u.searchParams.get("id"); if(!id) return Response.json({service:"cube-state",version:1,authenticated:true,generators:BASE,generator_order_4:ORDER4},{headers:CORS});
      const result=await sql.begin(async tx=>{ const row=await load(tx,id); authorize(row,c); const history=u.searchParams.get("history")==="1" ? await tx`select seq,created_at,kind,move,source,prev_hash,hash,displaced,geometry_energy,actor,details from public.cube_moves where instance_id=${id}::uuid order by seq asc limit 500` : undefined; return {instance:view(row),history}; });
      return Response.json(result,{headers:CORS});
    }
    if(req.method!=="POST") throw new AppError(405,"use GET or POST");
    const b=await req.json(); const action=String(b.action||"");
    const result=await sql.begin(async tx=>{
      if(action==="create"){
        const seed=Math.max(0,Number.isFinite(Number(b.seed))?Math.trunc(Number(b.seed)):Date.now()%2147483647);
        const depth=Math.max(0,Math.min(200,Math.trunc(Number(b.depth||0))));
        const rows=await tx`insert into public.cube_instances(seed,status,permutation,word,move_count,ledger_seq,head_hash,owner_sub,metadata)
          values(${seed},'solved',${JSON.stringify(ID)}::jsonb,'[]'::jsonb,0,0,${ZERO},${c.actor},${JSON.stringify({api:"cube-state",schema_version:1})}::jsonb)
          returning id::text,created_at,updated_at,seed,status,permutation,word,move_count,ledger_seq,head_hash,owner_sub,metadata`;
        const row=normalizeRow(rows[0]);
        const createHash=await sha256({instance_id:row.id,seq:0,kind:"create",move:null,actor:c.actor,prev_hash:ZERO,permutation:ID,details:{seed}});
        await tx`insert into public.cube_moves(instance_id,seq,kind,move,source,prev_hash,hash,displaced,geometry_energy,permutation,actor,details) values(${row.id}::uuid,0,'create',null,${src},${ZERO},${createHash},0,0,${JSON.stringify(ID)}::jsonb,${c.actor},${JSON.stringify({seed})}::jsonb)`;
        row.head_hash=createHash;
        if(depth){ const w=scramble(seed,depth); await applyWord(tx,row,w,"scramble",c.actor,src,{seed,depth}); row.status=metrics(row.permutation).displaced?"scrambled":"solved"; }
        await save(tx,row); return {action,instance:view(row)};
      }
      const id=String(b.id||""); if(!id) throw new AppError(400,"id required");
      const row=await load(tx,id); authorize(row,c);
      if(action==="move"){
        const mv=String(b.move||""); parseMove(mv); await applyWord(tx,row,[mv],"move",c.actor,src,{}); row.status=metrics(row.permutation).displaced?"active":"solved"; await save(tx,row); return {action,instance:view(row)};
      }
      if(action==="scramble"){
        const depth=Math.max(1,Math.min(200,Math.trunc(Number(b.depth||12)))); const seed=Math.max(0,Number.isFinite(Number(b.seed))?Math.trunc(Number(b.seed)):row.seed+row.move_count+1); const w=scramble(seed,depth); await applyWord(tx,row,w,"scramble",c.actor,src,{seed,depth}); row.status=metrics(row.permutation).displaced?"scrambled":"solved"; await save(tx,row); return {action,word:w,instance:view(row)};
      }
      if(action==="solve"){
        const solution=[...row.word].reverse().map(inv); if(solution.length){ for(const mv of solution){ row.permutation=applyMove(row.permutation,mv); row.move_count++; await appendEvent(tx,row,"solve",mv,c.actor,row.permutation,{solution_length:solution.length},src); } } else await appendEvent(tx,row,"solve",null,c.actor,row.permutation,{noop:true},src);
        row.word=[]; row.status="solved"; if(!row.permutation.every((v:number,i:number)=>v===i)) throw new AppError(500,"inverse solution failed identity check"); await save(tx,row); return {action,solution,instance:view(row)};
      }
      if(action==="reset"){
        row.permutation=ID.slice(); row.word=[]; row.status="solved"; await appendEvent(tx,row,"reset",null,c.actor,row.permutation,{reason:String(b.reason||"explicit reset")},src); await save(tx,row); return {action,instance:view(row)};
      }
      if(action==="handoff"){
        const target=String(b.target_owner_sub||"").trim(); if(!target) throw new AppError(400,"target_owner_sub required"); const from=row.owner_sub; await appendEvent(tx,row,"handoff",null,c.actor,row.permutation,{from,to:target},src); row.owner_sub=target; await save(tx,row); return {action,from,to:target,instance:view(row)};
      }
      throw new AppError(400,"unknown action");
    });
    return Response.json(result,{headers:CORS});
  }catch(e){ const status=e instanceof AppError?e.status:500; return Response.json({error:e instanceof Error?e.message:String(e)},{status,headers:CORS}); }
});
