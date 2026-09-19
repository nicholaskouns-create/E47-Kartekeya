// SKYRMION-WORLD-REGISTRY-1.0
// Read-only bridge to the on-platform Supabase geospatial registry.
// Rendering/navigation only. Never mutates flight solver state.

export const WORLD_RUNTIME_ENDPOINT=
  'https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/skyrmion-world-runtime';

const FALLBACK_SOURCES=Object.freeze({
  imagery:{
    id:'esri-world-imagery',name:'Esri World Imagery',kind:'satellite',
    url_template:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
    attribution:'Tiles © Esri — Source: Esri, Maxar, Earthstar Geographics',max_zoom:19
  },
  hillshade:{
    id:'esri-world-hillshade',name:'Esri World Hillshade',kind:'topo',
    url_template:'https://server.arcgisonline.com/ArcGIS/rest/services/Elevation/World_Hillshade/MapServer/tile/{z}/{y}/{x}',
    attribution:'Tiles © Esri',max_zoom:16
  },
  dem:{
    id:'maplibre-jaxa-dem',name:'MapLibre JAXA AW3D30 Terrain RGB',kind:'dem',
    url_template:'https://demotiles.maplibre.org/terrain-tiles/{z}/{x}/{y}.png',
    attribution:'AW3D30 © JAXA · served by MapLibre demo tiles',max_zoom:12
  },
  global:{
    id:'nasa-blue-marble',name:'NASA Blue Marble',kind:'marble',
    url_template:'https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/BlueMarble_NextGeneration/default/GoogleMapsCompatible_Level8/{z}/{y}/{x}.jpg',
    attribution:'NASA GIBS / Blue Marble',max_zoom:8
  }
});

let cached=null;
let pending=null;

function validateSource(s){
  return s&&typeof s.url_template==='string'&&s.url_template.includes('{z}')&&
    (s.url_template.includes('{x}')||s.url_template.includes('{y}'));
}

export function tileUrl(source,z,x,y,{time=null}={}){
  if(!validateSource(source))throw new Error('invalid map source');
  const max=Number.isFinite(source.max_zoom)?source.max_zoom:z;
  const zz=Math.min(z,max);
  const factor=2**Math.max(0,z-zz);
  const xx=Math.floor(x/factor),yy=Math.floor(y/factor);
  const date=time||new Date(Date.now()-86400000).toISOString().slice(0,10);
  return source.url_template
    .replaceAll('{z}',String(zz))
    .replaceAll('{x}',String(xx))
    .replaceAll('{y}',String(yy))
    .replaceAll('{time}',date);
}

export function selectWorldSources(registry,{altitude_m=0,domain=0}={}){
  const selected=registry?.selected||{};
  const orbital=Number(domain)>0||Number(altitude_m)>45000;
  return {
    imagery:(orbital&&validateSource(selected.global)?selected.global:selected.imagery)||FALLBACK_SOURCES.imagery,
    hillshade:orbital?null:(selected.hillshade||FALLBACK_SOURCES.hillshade),
    dem:selected.dem||FALLBACK_SOURCES.dem,
    streets:selected.streets||null,
    topo:selected.topo||null,
    weather:selected.weather||null
  };
}

export async function loadWorldRegistry({timeoutMs=2500,force=false}={}){
  if(cached&&!force)return cached;
  if(pending&&!force)return pending;
  pending=(async()=>{
    const controller=new AbortController();
    const timer=setTimeout(()=>controller.abort(),timeoutMs);
    try{
      const response=await fetch(WORLD_RUNTIME_ENDPOINT,{mode:'cors',cache:'no-cache',signal:controller.signal});
      if(!response.ok)throw new Error('world registry HTTP '+response.status);
      const data=await response.json();
      if(data?.schema!=='SKYRMION-WORLD-RUNTIME-2.0')throw new Error('unexpected world registry schema');
      if(!validateSource(data?.selected?.imagery)||!validateSource(data?.selected?.dem))throw new Error('world registry missing imagery/DEM');
      cached={...data,online:true,fallback:false};
    }catch(error){
      cached={
        schema:'SKYRMION-WORLD-RUNTIME-FALLBACK-1.0',online:false,fallback:true,
        error:String(error?.message||error),crs:'EPSG:4326',datum:'WGS84',
        selected:{...FALLBACK_SOURCES},map_sources:Object.values(FALLBACK_SOURCES),
        geo_anchors:[],places:[]
      };
    }finally{
      clearTimeout(timer);pending=null;
    }
    return cached;
  })();
  return pending;
}

export function nearestPlaces(registry,lat,lon,{limit=8,maxKm=250,kinds=null}={}){
  const rad=Math.PI/180,R=6371,filter=kinds?new Set(kinds):null;
  return (registry?.places||[])
    .filter(p=>Number.isFinite(p.lat)&&Number.isFinite(p.lon)&&(!filter||filter.has(p.kind)))
    .map(p=>{
      const a1=lat*rad,a2=p.lat*rad,dlat=(p.lat-lat)*rad,dlon=(p.lon-lon)*rad;
      const a=Math.sin(dlat/2)**2+Math.cos(a1)*Math.cos(a2)*Math.sin(dlon/2)**2;
      return {...p,distance_km:2*R*Math.asin(Math.min(1,Math.sqrt(a)))};
    })
    .filter(p=>p.distance_km<=maxKm)
    .sort((a,b)=>a.distance_km-b.distance_km)
    .slice(0,limit);
}
