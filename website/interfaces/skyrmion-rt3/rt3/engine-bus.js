// SKYRMION RT3 · City engine bus.
// Every engine already standing on the sites is bound here, in one place, so the
// simulator both feeds them and is fed by them rather than being an island:
//   world-engine        biome, procedural weather, solar state, world cells
//   world-binding       BroadcastChannel + storage sync with every other City page
//   e47-lock            canonical kernel constants, generated from src/e47
//   stargate-invariants E2 simulator packets with the physical gate held shut
//   city-geo            WGS84 <-> local metre conversions used across the City
//   instrument-telemetry the shared failure schema
// Each binding is optional: a missing module degrades that one channel and leaves
// the simulator flying.
const MODULES={
 worldEngine:'../../shared/world-engine/world-engine.js',
 worldBinding:'../../shared/world-engine/world-binding.js',
 e47Lock:'../../shared/e47-lock.js',
 stargate:'../../shared/stargate-invariants.js',
 cityGeo:'../../shared/city-geo.js',
 instrument:'../../shared/instrument-telemetry.js'
};

async function tryImport(path){
 try{return await import(path)}catch{return null}
}

export class CityEngineBus extends EventTarget{
 constructor({surface='SKYRMION-RT3',componentId='skyrmion-rt3',version='3.0.0'}={}){
  super();
  this.schema='RT3-CITY-ENGINE-BUS-1.0';
  this.surface=surface;this.componentId=componentId;this.version=version;
  this.modules={};this.binding=null;this.worldCell=null;
  this.status=Object.fromEntries(Object.keys(MODULES).map(k=>[k,'pending']));
  this.weather=null;this.solar=null;this.biome=null;this.lastPublish=0;
 }
 async connect({lat=36.1699,lon=-115.1398,onWorldState=null}={}){
  const entries=await Promise.all(Object.entries(MODULES).map(async([key,path])=>[key,await tryImport(path)]));
  for(const [key,mod] of entries){this.modules[key]=mod;this.status[key]=mod?'bound':'unavailable'}
  const we=this.modules.worldEngine;
  if(we){
   this.refreshWorld(lat,lon);
   this.engineVersion=we.WORLD_ENGINE_VERSION;
  }
  const wb=this.modules.worldBinding;
  if(wb){
   // Any other City page that moves the world moves this simulator with it.
   this.binding=wb.installWorldBinding({
    surface:this.surface,initial:{lat,lon},
    onState:detail=>{
     this.refreshWorld(detail.lat,detail.lon);
     this.dispatchEvent(new CustomEvent('world',{detail}));
     try{onWorldState?.(detail)}catch{}
    }
   });
  }
  const lock=this.modules.e47Lock;
  if(lock)this.kernel={lock:lock.E47_LOCK,carrier:lock.N,kernelDim:lock.DIM_E47,omegaC:lock.OMEGA_C,epsilon:lock.EPS};
  const inst=this.modules.instrument;
  if(inst)this.failure=(phase,error,context={})=>inst.failureTelemetry({
   componentId:this.componentId,version:this.version,phase,error,context});
  this.dispatchEvent(new CustomEvent('ready',{detail:this.report()}));
  return this;
 }
 refreshWorld(lat,lon,timestamp=Date.now()){
  const we=this.modules.worldEngine;
  if(!we)return null;
  this.weather=we.proceduralWeather({lat,lon,timestamp});
  this.solar=we.solarState(timestamp,lat,lon);
  this.biome=we.classifyBiome({lat,elevationM:0,moisture:this.weather.moisture});
  this.dispatchEvent(new CustomEvent('environment',{detail:{weather:this.weather,solar:this.solar,biome:this.biome}}));
  return {weather:this.weather,solar:this.solar,biome:this.biome};
 }
 // The world engine's wind becomes the simulator's wind, so weather on one page is
 // the same weather the aircraft is flying through on this one.
 windFor(runtime){
  if(!this.weather)return null;
  const next={speed10:this.weather.windMps,direction10:this.weather.windHeadingDeg*Math.PI/180,roughness:.12};
  runtime.setWind(next);
  return next;
 }
 // Flight state goes back out to the City so the observatory, radar bridge and
 // planetarium can see the aircraft without any of them knowing about this page.
 publish(telemetry,{minIntervalMs=250}={}){
  const now=Date.now();
  if(now-this.lastPublish<minIntervalMs)return false;
  this.lastPublish=now;
  this.binding?.update({lat:telemetry.position.lat,lon:telemetry.position.lon,altitude_m:telemetry.altitude_m});
  const detail={schema:'CITY-FLIGHT-STATE-1.0',surface:this.surface,t:telemetry.t,
   vehicleId:telemetry.vehicleId,evidence:telemetry.evidence,
   position:telemetry.position,heading:telemetry.heading,
   speedMps:telemetry.speed,mach:telemetry.aero.mach,altitude_m:telemetry.altitude_m};
  if(typeof globalThis.dispatchEvent==='function'&&typeof CustomEvent==='function')
   globalThis.dispatchEvent(new CustomEvent('city:flight-state',{detail}));
  this.dispatchEvent(new CustomEvent('published',{detail}));
  return true;
 }
 // E2 packet for an experimental craft. The physical gate stays shut here exactly
 // as it does everywhere else in the City; nothing about flying promotes it.
 stargatePacket(telemetry){
  const sg=this.modules.stargate;
  if(!sg||!telemetry.e47)return null;
  return sg.createStargatePacket({
   surface:this.surface,
   modeled:{capture:telemetry.e47.capture,residual:telemetry.e47.residual,
    omegaC:telemetry.e47.omegaC,iterations:telemetry.e47.iterations,
    speedMps:telemetry.speed,altitude_m:telemetry.altitude_m},
   conditional:{rankFraction:telemetry.e47.capture}
  });
 }
 localMeters(origin,lat,lon){
  const geo=this.modules.cityGeo;
  if(!geo)return null;
  return geo.wgs84ToMeters(origin,lat,lon);
 }
 report(){
  return {schema:this.schema,surface:this.surface,bound:this.status,
   worldEngine:this.engineVersion??null,kernel:this.kernel??null,
   weather:this.weather,solar:this.solar,biome:this.biome,
   channels:{broadcast:!!this.binding,flightState:'city:flight-state'}};
 }
 destroy(){try{this.binding?.destroy()}catch{}}
}
