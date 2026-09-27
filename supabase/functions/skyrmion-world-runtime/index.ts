import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const cors={
  "access-control-allow-origin":"*",
  "access-control-allow-headers":"authorization, x-client-info, apikey, content-type",
  "access-control-allow-methods":"GET, OPTIONS"
};

function secretKey(){
  const modern=Deno.env.get("SUPABASE_SECRET_KEYS");
  if(modern){try{return JSON.parse(modern).default}catch{}}
  return Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")||"";
}

function decodePointEWKB(hex){
  if(typeof hex!=="string"||hex.length<50)return null;
  try{
    const bytes=new Uint8Array(hex.match(/../g).map(x=>parseInt(x,16)));
    const view=new DataView(bytes.buffer);
    const little=bytes[0]===1;
    let offset=1;
    const type=view.getUint32(offset,little);offset+=4;
    const hasSrid=(type & 0x20000000)!==0;
    if(hasSrid)offset+=4;
    const lon=view.getFloat64(offset,little);offset+=8;
    const lat=view.getFloat64(offset,little);
    if(!Number.isFinite(lat)||!Number.isFinite(lon))return null;
    return {lat,lon};
  }catch{return null}
}

Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  if(req.method!=="GET")return new Response(JSON.stringify({error:"method_not_allowed"}),{status:405,headers:{...cors,"content-type":"application/json"}});
  try{
    const url=Deno.env.get("SUPABASE_URL")!;
    const key=secretKey();
    if(!key)throw new Error("server key unavailable");
    const db=createClient(url,key,{auth:{persistSession:false,autoRefreshToken:false}});
    const [srcQ,placeQ,anchorQ]=await Promise.all([
      db.from("gps_map_sources").select("id,name,kind,url_template,attribution,max_zoom,created_at").order("kind").order("id"),
      db.from("gps_places").select("id,name,kind,lat,lon,alt_m,country,region,icao,iata,theater").order("name"),
      db.from("city_geo_anchors").select("id,slug,name,location,altitude_m,source,source_version,metadata").order("id")
    ]);
    const errors=[srcQ.error,placeQ.error,anchorQ.error].filter(Boolean);
    if(errors.length)throw new Error(errors.map(e=>e.message).join("; "));
    const mapSources=srcQ.data||[];
    const anchors=(anchorQ.data||[]).map(a=>({...a,...decodePointEWKB(a.location),location:undefined}));
    const pick=(id)=>mapSources.find(s=>s.id===id)||null;
    const payload={
      schema:"SKYRMION-WORLD-RUNTIME-2.0",
      generated_at:new Date().toISOString(),
      crs:"EPSG:4326",
      datum:"WGS84",
      source:"Supabase gps_map_sources + gps_places + city_geo_anchors",
      map_sources:mapSources,
      selected:{
        imagery:pick("esri-world-imagery"),
        hillshade:pick("esri-world-hillshade"),
        topo:pick("esri-world-topo"),
        streets:pick("carto-voyager"),
        dem:pick("maplibre-jaxa-dem"),
        global:pick("nasa-blue-marble"),
        weather:pick("nasa-gibs-viirs")
      },
      geo_anchors:anchors,
      places:placeQ.data||[],
      render_contract:{
        tile_policy:"interactive viewport only; no bulk prefetch",
        attribution_required:true,
        terrain_encoding:"mapbox",
        terrain_max_zoom:12,
        flight_state_crs:"EPSG:4326",
        fixed_step_hz:120,
        note:"Map layers affect rendering/navigation only and do not alter solver evidence class."
      }
    };
    return new Response(JSON.stringify(payload),{
      headers:{...cors,"content-type":"application/json","cache-control":"public, max-age=60, stale-while-revalidate=300"}
    });
  }catch(error){
    return new Response(JSON.stringify({schema:"SKYRMION-WORLD-RUNTIME-2.0",error:String(error?.message||error)}),{
      status:500,headers:{...cors,"content-type":"application/json","cache-control":"no-store"}
    });
  }
});