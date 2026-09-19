// CITY-GPS-RUNTIME-1.0
// Shared browser GPS + WGS84 rendering bridge for City simulators.
// Navigation/rendering only. No position is uploaded by this module.
import {CITY_GEO,formatGps,metersToWgs84,wgs84ToMeters} from './city-geo.js';
export {CITY_GEO,formatGps,metersToWgs84,wgs84ToMeters};

export function installCityGps({
  chip=null,
  container=null,
  postTarget=null,
  onUpdate=null,
  seed=CITY_GEO.defaultOrigin,
  watch=true,
  label='GPS'
}={}){
  const target=chip||document.createElement('span');
  if(!chip){
    target.className='chip';
    (container||document.querySelector('.hud .top .cluster')||document.querySelector('.hud .top')||document.body).appendChild(target);
  }
  const state={
    lat:Number(seed.lat),
    lon:Number(seed.lon),
    altitude_m:Number(seed.altitude_m||0),
    accuracy_m:null,
    source:'seed',
    timestamp:Date.now()
  };
  let watchId=null;
  function publish(next=null){
    if(next)Object.assign(state,next);
    const acc=Number.isFinite(state.accuracy_m)?' · ±'+Math.round(state.accuracy_m)+' m':'';
    target.textContent=label+' · '+formatGps(state)+(state.source==='device'?acc:' · SEED');
    target.classList.toggle('live',state.source==='device');
    const detail={...state,schema:CITY_GEO.schema,crs:CITY_GEO.crs,datum:CITY_GEO.datum};
    window.CITY_GPS={schema:'CITY-GPS-RUNTIME-1.0',state,chip:target};
    window.dispatchEvent(new CustomEvent('city:gps',{detail}));
    try{postTarget?.contentWindow?.postMessage({type:'CITY:GPS',...detail},'*')}catch{}
    try{onUpdate?.(detail)}catch{}
    return detail;
  }
  publish();
  if(watch&&navigator.geolocation){
    try{
      watchId=navigator.geolocation.watchPosition(
        p=>publish({
          lat:p.coords.latitude,
          lon:p.coords.longitude,
          altitude_m:Number.isFinite(p.coords.altitude)?p.coords.altitude:state.altitude_m,
          accuracy_m:p.coords.accuracy,
          source:'device',
          timestamp:p.timestamp||Date.now()
        }),
        ()=>publish({source:'seed'}),
        {enableHighAccuracy:true,maximumAge:5000,timeout:12000}
      );
    }catch{}
  }
  return {
    state,
    chip:target,
    publish,
    stop(){if(watchId!=null&&navigator.geolocation)navigator.geolocation.clearWatch(watchId);}
  };
}

export function drawGpsOverlay(ctx,w,h,state,{alpha=.08}={}){
  if(!ctx||!state)return;
  const fx=((Math.abs(state.lon)*1000)%1+1)%1;
  const fy=((Math.abs(state.lat)*1000)%1+1)%1;
  const step=96;
  ctx.save();
  ctx.lineWidth=1;
  ctx.strokeStyle='rgba(125,255,235,'+alpha+')';
  for(let x=-step+fx*step;x<w+step;x+=step){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,h);ctx.stroke();}
  for(let y=-step+fy*step;y<h+step;y+=step){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(w,y);ctx.stroke();}
  ctx.fillStyle='rgba(190,255,240,'+Math.min(.55,alpha*4)+')';
  ctx.font='9px ui-monospace,SFMono-Regular,Menlo,monospace';
  ctx.fillText('WGS84 · EPSG:4326',12,h-14);
  ctx.restore();
}
