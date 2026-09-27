import "jsr:@supabase/functions-js/edge-runtime.d.ts";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, OPTIONS",
  "Access-Control-Allow-Headers": "content-type",
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "public, max-age=180"
};
const AU_KM=149597870.7, DAY_S=86400;

function q(v:string){return `'${v}'`}
function norm(v:number[]){return Math.hypot(...v)}
function sub(a:number[],b:number[]){return a.map((x,i)=>x-b[i])}

function parseVector(result:string){
  const a=result.indexOf("$$SOE"), b=result.indexOf("$$EOE");
  if(a<0||b<a) throw new Error("Horizons vector block missing");
  const line=result.slice(a+5,b).split(/\r?\n/).map(x=>x.trim()).find(Boolean);
  if(!line) throw new Error("Horizons vector block empty");
  const fields=line.replace(/,$/,"").split(",").map(x=>x.trim().replace(/^"|"$/g,""));
  const nums=fields.map(Number);
  if(fields.length < 8 || !nums.slice(2,8).every(Number.isFinite)){
    throw new Error("Unexpected Horizons vector row");
  }
  return {jd:nums[0], calendar:fields[1], position_au:nums.slice(2,5), velocity_au_per_day:nums.slice(5,8)};
}

async function sbdb(){
  const u=new URL("https://ssd-api.jpl.nasa.gov/sbdb.api");
  u.searchParams.set("sstr","3I/ATLAS");
  u.searchParams.set("full-prec","true");
  u.searchParams.set("phys-par","true");
  u.searchParams.set("discovery","true");
  const r=await fetch(u,{headers:{"accept":"application/json","user-agent":"Syntax-Jacob/1.0"}});
  if(!r.ok) throw new Error(`SBDB HTTP ${r.status}`);
  const j=await r.json();
  if(j.message) throw new Error(String(j.message));
  return {url:u.toString(),signature:j.signature??null,object:j.object??null,orbit:j.orbit??null,phys_par:j.phys_par??null,discovery:j.discovery??null};
}

async function horizons(command:string, at:string){
  const u=new URL("https://ssd.jpl.nasa.gov/api/horizons.api");
  const p={
    format:"json", COMMAND:q(command), OBJ_DATA:q("NO"), MAKE_EPHEM:q("YES"),
    EPHEM_TYPE:q("VECTORS"), CENTER:q("500@10"), TLIST:q(at), TLIST_TYPE:q("CAL"),
    TIME_TYPE:q("TDB"), OUT_UNITS:q("AU-D"), VEC_TABLE:q("2"), VEC_LABELS:q("NO"),
    CSV_FORMAT:q("YES"), REF_PLANE:q("ECLIPTIC"), REF_SYSTEM:q("ICRF")
  };
  for(const [k,v] of Object.entries(p)) u.searchParams.set(k,v);
  const r=await fetch(u,{headers:{"accept":"application/json","user-agent":"Syntax-Jacob/1.0"}});
  if(!r.ok) throw new Error(`Horizons HTTP ${r.status}`);
  const j=await r.json();
  if(j.error) throw new Error(String(j.error));
  return {url:u.toString(),signature:j.signature??null,...parseVector(String(j.result??""))};
}

Deno.serve(async(req:Request)=>{
  if(req.method==="OPTIONS") return new Response("ok",{headers:CORS});
  if(req.method!=="GET") return new Response(JSON.stringify({ok:false,error:"GET required"}),{status:405,headers:CORS});
  try{
    const raw=new URL(req.url).searchParams.get("at");
    const d=raw?new Date(raw):new Date();
    if(!Number.isFinite(d.getTime())) throw new Error("Invalid at timestamp");
    const at=d.toISOString().replace("T"," ").replace(/\.\d{3}Z$/,"");
    const sb=await sbdb();
    const spk=String(sb.object?.spkid??"").trim();
    if(!spk) throw new Error("SBDB did not return a SPK identifier");
    const [comet,earth]=await Promise.all([
      horizons(`DES=${spk};`,at),
      horizons("399",at)
    ]);
    const rel=sub(comet.position_au,earth.position_au);
    const rv=sub(comet.velocity_au_per_day,earth.velocity_au_per_day);
    const body={
      ok:true,
      schema:"SYNTAX-JACOB-EPHEMERIS-1.0",
      generated_at:new Date().toISOString(),
      requested_at:d.toISOString(),
      frame:{origin:"Sun center (500@10)",reference_plane:"ECLIPTIC",reference_system:"ICRF",units:"AU, AU/day"},
      comet:{name:"3I/ATLAS",spkid:spk,...comet,heliocentric_distance_au:norm(comet.position_au),speed_km_s:norm(comet.velocity_au_per_day)*AU_KM/DAY_S},
      earth:{name:"Earth",...earth,heliocentric_distance_au:norm(earth.position_au),speed_km_s:norm(earth.velocity_au_per_day)*AU_KM/DAY_S},
      relative:{earth_to_comet_vector_au:rel,earth_to_comet_au:norm(rel),earth_to_comet_km:norm(rel)*AU_KM,relative_speed_km_s:norm(rv)*AU_KM/DAY_S},
      sbdb:sb,
      sources:{
        horizons:"NASA/JPL Horizons API",
        sbdb:"NASA/JPL Small-Body Database API",
        nasa:"https://science.nasa.gov/solar-system/comets/3i-atlas/"
      },
      boundary:"JPL supplies the orbital state and orbit-solution metadata. Nucleus shape, coma/tails, craft, E47 coherence and scalar-flight behavior are visualization/model layers, not direct measurements or demonstrated propulsion."
    };
    return new Response(JSON.stringify(body),{headers:CORS});
  }catch(e){
    return new Response(JSON.stringify({ok:false,schema:"SYNTAX-JACOB-EPHEMERIS-1.0",generated_at:new Date().toISOString(),error:e instanceof Error?e.message:String(e)}),{status:502,headers:{...CORS,"Cache-Control":"no-store"}});
  }
});