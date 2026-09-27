import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";
const BUCKET="city-apps";
const origins:Record<string,string>={spectra:"https://prairie-dream-glow-fire.grok.me",fold:"https://giant-beacon-dawn-falcon.grok.me",murmuration:"https://kite-glade-tiger-cabin.grok.me",mnemosyne:"https://moon-clear-urban-nova.grok.me",density:"https://winter-dawn-leaf-marble.grok.me",horizon:"https://zenith-fjord-pearl-pixel.grok.me",wave:"https://apex-star-crisp-blend.grok.me",identity:"https://mist-mint-branch-nova.grok.me",build:"https://brave-ivory-pearl-ever.grok.me",soar:"https://topaz-solar-iris-drift.grok.me",scalar:"https://heart-eagle-blade-hazel.grok.me",eidolon:"https://lark-plaza-umbra-drum.grok.me",kartekeya:"https://velvet-king-quiet-amber.grok.me",see:"https://orbit-coral-delta-fjord.grok.me",cube:"https://garden-king-granite-pixel.grok.me","city-os":"https://spark-maple-sail-tiger.grok.me",matrix:"https://oasis-acorn-pearl-prism.grok.me",chimera:"https://zest-blade-turbo-rose.grok.me",sigillum:"https://prism-shadow-sage-craft.grok.me","proof-forge":"https://pepper-raven-blade-heart.grok.me",invarifold:"https://sapphire-cabin-crystal-king.grok.me",gestalt:"https://tundra-drift-dune-finch.grok.me","ufo-propulsion":"https://star-sage-atlas-rapid.grok.me","eidolon-harmonic":"https://nova-wood-clear-zest.grok.me","hover-build":"https://willow-fjord-king-cap.grok.me",hover:"https://bison-drum-daisy-plaza.grok.me",mav:"https://glow-garden-brick-cedar.grok.me"};
function secretKey(){const r=Deno.env.get("SUPABASE_SECRET_KEYS");if(r)return JSON.parse(r).default;const l=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");if(l)return l;throw new Error("No secret key")}
const sb=createClient(Deno.env.get("SUPABASE_URL")!,secretKey(),{auth:{persistSession:false,autoRefreshToken:false}});
function pathFor(slug:string,rest:string){const p=rest.replace(/^\/+/,"");if(!p)return`${slug}/index.html`;if(p.endsWith("/"))return`${slug}/${p}index.html`;const x=p.split("/").pop()||"";return x.includes(".")?`${slug}/${p}`:`${slug}/${p}/index.html`}
function mime(path:string,fallback:string){if(fallback&&fallback!=="application/octet-stream")return fallback;const e=path.split(".").pop()?.toLowerCase()||"";return({html:"text/html; charset=utf-8",js:"text/javascript; charset=utf-8",mjs:"text/javascript; charset=utf-8",css:"text/css; charset=utf-8",json:"application/json; charset=utf-8",webmanifest:"application/manifest+json; charset=utf-8",svg:"image/svg+xml",png:"image/png",jpg:"image/jpeg",jpeg:"image/jpeg",webp:"image/webp",gif:"image/gif",ico:"image/x-icon",wasm:"application/wasm",woff:"font/woff",woff2:"font/woff2",ttf:"font/ttf",otf:"font/otf",mp3:"audio/mpeg",mp4:"video/mp4",webm:"video/webm"}as Record<string,string>)[e]||"application/octet-stream"}
function rewrite(text:string,slug:string,ct:string,req:Request){const root=new URL(req.url).origin+"/functions/v1/city-app-host";const base=`${root}/${slug}`;let out=text;
 for(const [s,o] of Object.entries(origins)){const dest=`${root}/${s}`;out=out.replaceAll(o+"/",dest+"/").replaceAll(o,dest)}
 out=out.replace(/<script[^>]+src=["']https:\/\/grok\.com\/grok-app-builder\/extensions\.js[^>]*><\/script>/gi,"");
 if(ct.includes("html")){out=out.replace(/\b(href|src|poster|action)=(['"])\/(?!\/)/gi,`$1=$2${base}/`);out=out.replace(/\bcontent=(['"])\/(?!\/)/gi,`content=$1${base}/`)}
 out=out.replaceAll('"/assets/',`"${base}/assets/`).replaceAll("'/assets/",`'${base}/assets/`).replaceAll('`/assets/',`\`${base}/assets/`).replaceAll('"/__grok/',`"${base}/__grok/`).replaceAll("'/__grok/",`'${base}/__grok/`).replaceAll('`/__grok/',`\`${base}/__grok/`).replaceAll("url(/assets/",`url(${base}/assets/`).replaceAll("url('/assets/",`url('${base}/assets/`).replaceAll('url("/assets/',`url("${base}/assets/`);
 return out}

const SJ_AU_KM=149597870.7,SJ_DAY_S=86400;
function sjQuote(v:string){return `'${v}'`}
function sjNorm(v:number[]){return Math.hypot(...v)}
function sjSub(a:number[],b:number[]){return a.map((x,i)=>x-b[i])}
function sjParseVector(result:string){
  const s=result.indexOf("$SOE"),e=result.indexOf("$EOE");
  if(s<0||e<0||e<=s)throw new Error("Horizons returned no vector block");
  const row=result.slice(s+5,e).trim().split(/\r?\n/).map(x=>x.trim()).find(Boolean);
  if(!row)throw new Error("Horizons vector block empty");
  const f=row.replace(/,$/,"").split(",").map(x=>x.trim().replace(/^"|"$/g,"")),n=f.map(Number);
  if(f.length>=8&&n.slice(2,8).every(Number.isFinite))return{jd:n[0],calendar:f[1],position_au:n.slice(2,5),velocity_au_per_day:n.slice(5,8)};
  const grab=(k:string)=>{const m=result.match(new RegExp(k+"\\s*=\\s*([+\\-0-9.Ee]+)"));return m?Number(m[1]):NaN};
  const p=[grab("X"),grab("Y"),grab("Z")],v=[grab("VX"),grab("VY"),grab("VZ")];
  if(!p.every(Number.isFinite)||!v.every(Number.isFinite))throw new Error("Could not parse Horizons state vector");
  return{jd:null,calendar:null,position_au:p,velocity_au_per_day:v};
}
async function sjHorizons(command:string,at:string,objData="NO"){
  const p=new URLSearchParams({format:"json",COMMAND:sjQuote(command),OBJ_DATA:sjQuote(objData),MAKE_EPHEM:sjQuote("YES"),EPHEM_TYPE:sjQuote("VECTORS"),CENTER:sjQuote("500@10"),TLIST:sjQuote(at),TLIST_TYPE:sjQuote("CAL"),TIME_TYPE:sjQuote("TDB"),OUT_UNITS:sjQuote("AU-D"),VEC_TABLE:sjQuote("2"),VEC_LABELS:sjQuote("NO"),CSV_FORMAT:sjQuote("YES"),REF_PLANE:sjQuote("ECLIPTIC")});
  const r=await fetch("https://ssd.jpl.nasa.gov/api/horizons.api?"+p.toString(),{headers:{"accept":"application/json","user-agent":"Syntax-Jacob/1.0 Mathematical-City"}});
  if(!r.ok)throw new Error("Horizons HTTP "+r.status);
  const j=await r.json();
  if(j.error)throw new Error(String(j.error));
  return sjParseVector(String(j.result??""));
}
async function sjComet(at:string){
  let last:any;
  for(const c of ["3I/ATLAS;","C/2025 N1 (ATLAS);","DES=3I/ATLAS;"]){
    try{return{...(await sjHorizons(c,at,"YES")),command:c}}catch(e){last=e}
  }
  throw last??new Error("3I/ATLAS target unresolved");
}
async function sjSbdb(){
  const r=await fetch("https://ssd-api.jpl.nasa.gov/sbdb.api?sstr=3I%2FATLAS&full-prec=true&phys-par=true&discovery=true",{headers:{"accept":"application/json","user-agent":"Syntax-Jacob/1.0 Mathematical-City"}});
  if(!r.ok)throw new Error("SBDB HTTP "+r.status);
  const j=await r.json();
  if(j.message)throw new Error(String(j.message));
  return j;
}
async function sjResponse(u:URL,head=false){
  const raw=u.searchParams.get("at"),d=raw?new Date(raw):new Date();
  if(!Number.isFinite(d.getTime()))return Response.json({ok:false,error:"Invalid at timestamp"},{status:400,headers:{"access-control-allow-origin":"*"}});
  const at=d.toISOString().replace("T"," ").replace(/\.\d{3}Z$/,"");
  try{
    const [comet,earth,sbdb]=await Promise.all([sjComet(at),sjHorizons("399",at),sjSbdb()]);
    const rel=sjSub(comet.position_au,earth.position_au),rv=sjSub(comet.velocity_au_per_day,earth.velocity_au_per_day);
    const body={ok:true,schema:"SYNTAX-JACOB-EPHEMERIS-1.0",generated_at:new Date().toISOString(),requested_at:d.toISOString(),
      frame:{origin:"Sun center (500@10)",reference_plane:"ecliptic",units:"AU and AU/day"},
      comet:{name:"3I/ATLAS",...comet,heliocentric_distance_au:sjNorm(comet.position_au),speed_km_s:sjNorm(comet.velocity_au_per_day)*SJ_AU_KM/SJ_DAY_S},
      earth:{name:"Earth",...earth,heliocentric_distance_au:sjNorm(earth.position_au),speed_km_s:sjNorm(earth.velocity_au_per_day)*SJ_AU_KM/SJ_DAY_S},
      relative:{earth_to_comet_au:sjNorm(rel),earth_to_comet_km:sjNorm(rel)*SJ_AU_KM,relative_speed_km_s:sjNorm(rv)*SJ_AU_KM/SJ_DAY_S},
      sbdb,
      sources:{horizons:"NASA/JPL Horizons",sbdb:"NASA/JPL Small-Body Database"},
      boundary:"JPL data are the astronomy truth layer. Rendered morphology, display scaling, craft and scalar coherence remain model/visualization layers."};
    const h={"content-type":"application/json; charset=utf-8","cache-control":"public, max-age=60","access-control-allow-origin":"*","x-city-app":"syntax-jacob-ephemeris","x-content-type-options":"nosniff"};
    return new Response(head?null:JSON.stringify(body),{status:200,headers:h});
  }catch(e){
    return new Response(head?null:JSON.stringify({ok:false,schema:"SYNTAX-JACOB-EPHEMERIS-1.0",generated_at:new Date().toISOString(),error:e instanceof Error?e.message:String(e)}),{status:502,headers:{"content-type":"application/json; charset=utf-8","cache-control":"no-store","access-control-allow-origin":"*","x-city-app":"syntax-jacob-ephemeris"}});
  }
}

Deno.serve(async(req)=>{if(!["GET","HEAD"].includes(req.method))return new Response("Method not allowed",{status:405});const u=new URL(req.url),marker="/city-app-host/",i=u.pathname.indexOf(marker),tail=i>=0?u.pathname.slice(i+marker.length):"",parts=tail.split("/").filter(Boolean),slug=parts.shift()||"",rest=parts.join("/");if(!slug||slug==="city-live")return Response.redirect("https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/city-live/",302);if(slug==="syntax-jacob-ephemeris")return sjResponse(u,req.method==="HEAD");if(!origins[slug])return Response.json({error:"Unknown app",available:Object.keys(origins)},{status:404});const path=pathFor(slug,rest);const{data,error}=await sb.storage.from(BUCKET).download(path);if(error||!data)return Response.json({error:"Not migrated or asset missing",app:slug,path},{status:404});const ct=mime(path,data.type||"");const h=new Headers({"content-type":ct,"cache-control":ct.includes("text/html")?"no-cache":"public, max-age=31536000, immutable","x-city-app":slug,"x-content-type-options":"nosniff","referrer-policy":"strict-origin-when-cross-origin","content-security-policy":"frame-ancestors *"});if(req.method==="HEAD")return new Response(null,{status:200,headers:h});if(/^(text\/|application\/(?:javascript|json|manifest\+json)|image\/svg\+xml)/.test(ct))return new Response(rewrite(await data.text(),slug,ct,req),{status:200,headers:h});return new Response(data.stream(),{status:200,headers:h})});
