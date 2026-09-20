import {createSkyrmionTerrain3D} from '../skyrmion/terrain-3d.js';
import {MantaABRuntime,DT,MISSION_DURATION_S,REFERENCE} from './manta-model.js';

const $=s=>document.querySelector(s);
const runtime=new MantaABRuntime();
let running=true,acc=0,last=performance.now(),speedFactor=1,world=null;

function qToEuler(q){
  const [w,x,y,z]=q;
  const roll=Math.atan2(2*(w*x+y*z),1-2*(x*x+y*y));
  const s=Math.max(-1,Math.min(1,2*(w*y-z*x)));
  const pitch=Math.asin(s);
  const yaw=Math.atan2(2*(w*z+x*y),1-2*(y*y+z*z));
  return {roll,pitch,yaw};
}

function mantaGeometry(m){
  const out=[];
  for(let a=0;a<5;a++)for(let b=0;b<5;b++)for(let c=0;c<5;c++){
    const u=(a-2)/2,v=(b-2)/2,w=(c-2)/2;
    let x=4*u,z=2.5*v*(1-.25*Math.abs(u));
    let y=.20*(1-u*u)-.12*v*v+.08*w;
    x*=1+.95*m.span;
    z+=-2.6*m.sweep*Math.sign(x)*(Math.abs(x)/4);
    y+=1.6*m.camber*(1-v*v)+.65*m.twist*Math.sign(x)*Math.abs(z)/2.5+.45*m.thickness*(1-u*u);
    out.push(x,y,z);
  }
  return {geometry:out,activation:new Array(125).fill(.72),stiffness:new Array(125).fill(.8),anisotropy:new Array(125).fill(.55)};
}

function applySnapshot(s){
  if(!world)return;
  const m=s.morph,e=qToEuler(m.quaternion);
  world.updateFlightState({
    lat:m.position.lat,lon:m.position.lon,altitude_m:m.altitudeM,
    heading:e.yaw,pitch:e.pitch,roll:e.roll,speed:m.speed,
    active:4,domain:0,enabled:true
  });
  world.updateMantaFrame(mantaGeometry(m.morph));
  $('#clock').textContent=`${s.t.toFixed(1)} / ${MISSION_DURATION_S}s`;
  $('#phase').textContent=m.phase;
  $('#speedM').textContent=`${m.speed.toFixed(1)} m/s`;
  $('#speedB').textContent=`${s.baseline.speed.toFixed(1)} m/s`;
  $('#dSpeed').textContent=`${s.delta.speed>=0?'+':''}${s.delta.speed.toFixed(1)}`;
  $('#dAlt').textContent=`${s.delta.altitude>=0?'+':''}${s.delta.altitude.toFixed(0)} m`;
  $('#energy').textContent=`${(m.morphEnergyJ/3.6e6).toFixed(3)} kWh`;
  $('#cl').textContent=m.CL.toFixed(3);
  $('#cd').textContent=m.CD.toFixed(3);
  $('#cm').textContent=m.Cm.toFixed(3);
  $('#mass').textContent=`${m.massKg.toFixed(0)} kg`;
  $('#mdot').textContent=`${m.mdot.toFixed(3)} kg/s`;
  $('#inertia').textContent=m.inertia.map(v=>Math.round(v).toLocaleString()).join(' / ');
  $('#status').textContent=s.done?'MISSION COMPLETE':running?'FLYING':'PAUSED';
}

async function boot(){
  try{
    $('#status').textContent='WORLD LOADING';
    world=await createSkyrmionTerrain3D({
      host:document.body,
      lat:36.1699,lon:-115.1398,altitude_m:3658,
      heading:0,pitch:0,roll:0,speed:216,
      active:4,zoom:12,lightingMode:'daylight'
    });
    world.setActiveCraft(4);
    $('#status').textContent='FLYING';
    $('#world').textContent='DAYLIGHT LOCK';
    applySnapshot(runtime.snapshot());
    requestAnimationFrame(frame);
  }catch(error){
    console.error(error);
    $('#status').textContent='RENDER FAULT';
    $('#status').classList.add('fault');
    $('#fault').hidden=false;
    $('#fault').textContent=String(error?.message||error);
  }
}

function frame(now){
  const elapsed=Math.min(.05,(now-last)/1000);last=now;
  if(running&&!runtime.done){
    acc+=elapsed*speedFactor;
    let n=0;
    while(acc>=DT&&n<48){
      const s=runtime.step();
      acc-=DT;n++;
      applySnapshot(s);
    }
    if(runtime.done)running=false;
  }
  requestAnimationFrame(frame);
}

function restart(){
  runtime.reset();acc=0;running=true;last=performance.now();applySnapshot(runtime.snapshot());
}
$('#run').onclick=()=>{if(runtime.done)restart();running=true};
$('#pause').onclick=()=>{running=false;applySnapshot(runtime.snapshot())};
$('#reset').onclick=restart;
$('#fast').onclick=e=>{speedFactor=speedFactor===1?4:speedFactor===4?10:1;e.currentTarget.textContent=speedFactor+'×'};
$('#data').onclick=()=>document.body.classList.toggle('show-data');
$('#closeData').onclick=()=>document.body.classList.remove('show-data');

boot();
