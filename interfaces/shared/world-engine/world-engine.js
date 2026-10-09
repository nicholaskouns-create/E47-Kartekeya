// CITY-WORLD-ENGINE-1.0
// Browser-native deterministic geospatial + procedural world generator.
// Pure math core: no renderer dependency. Consumers may use Three.js, Canvas, or other renderers.

export const WORLD_ENGINE_VERSION='CITY-WORLD-ENGINE-1.0';
export const EARTH_RADIUS_M=6378137;
const DEG=Math.PI/180;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;
const smooth=t=>t*t*(3-2*t);

function hash32(x){
  x|=0;x=Math.imul(x^(x>>>16),0x45d9f3b);x=Math.imul(x^(x>>>16),0x45d9f3b);
  return (x^(x>>>16))>>>0;
}
export function seedFor(lat,lon,seed=470125){
  const a=Math.round((Number(lat)+90)*100000);
  const b=Math.round((Number(lon)+180)*100000);
  return hash32(a^Math.imul(b,0x9e3779b1)^seed);
}
function random01(ix,iy,seed){
  return hash32(Math.imul(ix,374761393)^Math.imul(iy,668265263)^seed)/4294967295;
}
function valueNoise2D(x,y,seed){
  const x0=Math.floor(x),y0=Math.floor(y),tx=smooth(x-x0),ty=smooth(y-y0);
  const a=random01(x0,y0,seed),b=random01(x0+1,y0,seed);
  const c=random01(x0,y0+1,seed),d=random01(x0+1,y0+1,seed);
  return lerp(lerp(a,b,tx),lerp(c,d,tx),ty)*2-1;
}
function fbm(x,y,seed,octaves=6){
  let sum=0,amp=.55,freq=1,norm=0;
  for(let i=0;i<octaves;i++){sum+=valueNoise2D(x*freq,y*freq,seed+i*1013)*amp;norm+=amp;freq*=2;amp*=.5}
  return sum/Math.max(norm,1e-9);
}
function ridged(x,y,seed){
  const n=fbm(x,y,seed,5);
  return 1-Math.abs(n);
}

export function localMeters(origin,lat,lon){
  const lat0=Number(origin.lat)*DEG;
  return {
    x:(Number(lon)-Number(origin.lon))*DEG*EARTH_RADIUS_M*Math.cos(lat0),
    z:-(Number(lat)-Number(origin.lat))*DEG*EARTH_RADIUS_M
  };
}

export function classifyBiome({lat,elevationM=0,moisture=.5,temperatureC=null}={}){
  const absLat=Math.abs(Number(lat)||0);
  const temp=temperatureC??(30-absLat*.48-Number(elevationM||0)*.0062);
  const wet=clamp(Number(moisture)||0,0,1);
  let id='temperate';
  if(elevationM>3800)id='alpine';
  else if(temp<-4)id='tundra';
  else if(temp>24&&wet<.30)id='desert';
  else if(temp>20&&wet>.72)id='tropical';
  else if(wet<.24)id='steppe';
  else if(wet>.63)id='forest';
  const table={
    desert:{ground:'#7c6248',urbanity:.72,vegetation:.08,roughness:.58},
    steppe:{ground:'#6b684d',urbanity:.42,vegetation:.25,roughness:.48},
    temperate:{ground:'#526450',urbanity:.55,vegetation:.52,roughness:.40},
    forest:{ground:'#2f4c3b',urbanity:.24,vegetation:.86,roughness:.52},
    tropical:{ground:'#24533e',urbanity:.20,vegetation:.95,roughness:.48},
    alpine:{ground:'#777b76',urbanity:.04,vegetation:.12,roughness:.92},
    tundra:{ground:'#6e7772',urbanity:.06,vegetation:.16,roughness:.38}
  };
  return {id,tempC:temp,moisture:wet,...table[id]};
}

export function proceduralWeather({lat,lon,timestamp=Date.now(),seed=470125}={}){
  const bucket=Math.floor(Number(timestamp)/21600000);
  const s=seedFor(lat,lon,seed)^hash32(bucket);
  const moisture=clamp(.5+.34*valueNoise2D(Number(lon)*.065,Number(lat)*.065,s),0,1);
  const cloudCover=clamp(.18+moisture*.72+.12*valueNoise2D(bucket*.17,Number(lat)*.1,s^0x51ed270b),0,1);
  const windMps=3+18*random01(bucket,Math.round(Number(lat)*10),s);
  const windHeadingDeg=360*random01(Math.round(Number(lon)*10),bucket,s^0x85ebca6b);
  const visibilityKm=clamp(90-cloudCover*52-moisture*18,8,100);
  return {schema:'CITY-WEATHER-1.0',moisture,cloudCover,windMps,windHeadingDeg,visibilityKm};
}

export function solarState(timestamp=Date.now(),lat=0,lon=0){
  const d=new Date(timestamp),start=Date.UTC(d.getUTCFullYear(),0,0);
  const day=(d.getTime()-start)/86400000;
  const hour=d.getUTCHours()+d.getUTCMinutes()/60+d.getUTCSeconds()/3600;
  const decl=23.44*Math.sin((2*Math.PI/365)*(day-81))*DEG;
  const phi=Number(lat)*DEG;
  const solarHour=hour+Number(lon)/15;
  const H=(solarHour-12)*15*DEG;
  const sinAlt=Math.sin(phi)*Math.sin(decl)+Math.cos(phi)*Math.cos(decl)*Math.cos(H);
  const altitudeDeg=Math.asin(clamp(sinAlt,-1,1))/DEG;
  const daylight=clamp((altitudeDeg+7)/22,0,1);
  return {schema:'CITY-SOLAR-1.0',altitudeDeg,daylight,night:daylight<.12,solarHour};
}

export function generateHeightField({lat=0,lon=0,span=12000,samples=97,seed=470125}={}){
  const n=Math.max(3,Math.floor(samples)),heights=new Float32Array(n*n),s=seedFor(lat,lon,seed);
  const continental=fbm((Number(lon)+180)*.018,(Number(lat)+90)*.018,s^0x243f6a88,5);
  const mountainBias=clamp((continental+.55)*.9,0,1);
  const amplitude=120+mountainBias*1900;
  const base=Math.max(0,180+650*fbm(Number(lon)*.03,Number(lat)*.03,s^0xb7e15162,4));
  let min=Infinity,max=-Infinity;
  for(let j=0;j<n;j++)for(let i=0;i<n;i++){
    const x=(i/(n-1)-.5)*Number(span),z=(j/(n-1)-.5)*Number(span);
    const scale=1/5600;
    const broad=fbm(x*scale,z*scale,s,6);
    const ridge=Math.pow(clamp(ridged(x*scale*.67,z*scale*.67,s^0x9e3779b9),0,1),3);
    const detail=fbm(x/820,z/820,s^0x7f4a7c15,4);
    let h=base+amplitude*(broad*.52+ridge*.68+detail*.08-.18);
    if(Math.abs(lat)<12)h*=.78;
    h=Math.max(-80,h);
    const k=j*n+i;heights[k]=h;min=Math.min(min,h);max=Math.max(max,h);
  }
  const centerElevation=heights[Math.floor(n/2)*n+Math.floor(n/2)];
  return {heights,samples:n,min,max,centerElevation,seed:s,procedural:true};
}

export function generateWorldCell({lat=0,lon=0,span=12000,samples=97,seed=470125,timestamp=Date.now()}={}){
  const terrain=generateHeightField({lat,lon,span,samples,seed});
  const weather=proceduralWeather({lat,lon,timestamp,seed});
  const biome=classifyBiome({lat,elevationM:terrain.centerElevation,moisture:weather.moisture});
  const lighting=solarState(timestamp,lat,lon);
  return Object.freeze({
    schema:'CITY-WORLD-CELL-1.0',version:WORLD_ENGINE_VERSION,
    id:`${Number(lat).toFixed(4)}:${Number(lon).toFixed(4)}:${terrain.seed.toString(16)}`,
    origin:{lat:Number(lat),lon:Number(lon)},spanM:Number(span),terrain,biome,weather,lighting
  });
}

export function createWorldState(state={}){
  const lat=Number(state.lat??36.1699),lon=Number(state.lon??-115.1398);
  const altitudeM=Number(state.altitude_m??state.altitudeM??610);
  return Object.freeze({
    schema:'CITY-WORLD-STATE-1.0',version:WORLD_ENGINE_VERSION,
    lat,lon,altitudeM,
    heading:Number(state.heading||0),pitch:Number(state.pitch||0),roll:Number(state.roll||0),
    speedMps:Number(state.speed??state.speedMps??0),domain:Number(state.domain||0),
    solar:solarState(Date.now(),lat,lon)
  });
}

export function publishWorldState(state,eventName='city:world-state'){
  const detail=createWorldState(state);
  if(typeof globalThis.dispatchEvent==='function'&&typeof globalThis.CustomEvent==='function'){
    globalThis.dispatchEvent(new CustomEvent(eventName,{detail}));
  }
  return detail;
}

export const CITY_WORLD_ENGINE=Object.freeze({
  version:WORLD_ENGINE_VERSION,seedFor,localMeters,classifyBiome,proceduralWeather,solarState,
  generateHeightField,generateWorldCell,createWorldState,publishWorldState
});

if(typeof globalThis!=='undefined')globalThis.CITY_WORLD_ENGINE=CITY_WORLD_ENGINE;
