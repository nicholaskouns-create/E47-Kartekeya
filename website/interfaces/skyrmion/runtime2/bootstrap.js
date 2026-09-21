// SKYRMION-VISUAL-FALLBACK-1.0
import {SkyrmionRuntime2} from './runtime2.js';
import {VEHICLE_ORDER,vehicle} from './vehicle-registry.js';
import {showCraftMath} from './craft-math.js';
import {installFlightInteractionStandard} from '../../shared/flight-interaction-standard.js';
const rt=new SkyrmionRuntime2({fixedStepHz:120,spawn:{lat:36.1699,lon:-115.1398,altitudeM:3658,speedMps:216}});window.CITY_SKYRMION_RUNTIME2=rt;
document.getElementById('startFlight')?.addEventListener('click',()=>document.body.classList.add('flight-started'));
dispatchEvent(new CustomEvent('skyrmion:runtime2-boot-ready',{detail:{schema:rt.schema,fixedStepHz:rt.fixedStepHz}}));
const root=document.getElementById('crafts'),tele=document.getElementById('tele'),gps=document.getElementById('gps'),stick=document.getElementById('stick'),knob=document.getElementById('knob'),proofPanel=document.getElementById('proofPanel');
const fallbackCanvas=document.getElementById('world'),fallbackCtx=fallbackCanvas?.getContext?.('2d',{alpha:true});
function sizeFallback(){
  if(!fallbackCanvas||!fallbackCtx)return;
  const d=Math.min(devicePixelRatio||1,1.6),w=innerWidth,h=innerHeight;
  if(fallbackCanvas.width!==Math.round(w*d)||fallbackCanvas.height!==Math.round(h*d)){
    fallbackCanvas.width=Math.round(w*d);fallbackCanvas.height=Math.round(h*d);
    fallbackCtx.setTransform(d,0,0,d,0,0);
  }
}
addEventListener('resize',sizeFallback);sizeFallback();
function drawFallbackCraft(ctx,w,h,name,roll,pitch){
  ctx.save();ctx.translate(w*.5,h*.61);ctx.rotate(roll*.42);ctx.scale(1.45,1.45);
  const long=name==='SR-71'?1.35:name==='X-15'?1.08:1;
  ctx.scale(1,long);ctx.fillStyle='#0b1114';ctx.strokeStyle='rgba(220,245,245,.48)';ctx.lineWidth=1.2;
  ctx.beginPath();ctx.moveTo(0,-62);ctx.lineTo(10,-17);ctx.lineTo(58,15);ctx.lineTo(54,25);ctx.lineTo(15,16);ctx.lineTo(12,49);ctx.lineTo(-12,49);ctx.lineTo(-15,16);ctx.lineTo(-54,25);ctx.lineTo(-58,15);ctx.lineTo(-10,-17);ctx.closePath();ctx.fill();ctx.stroke();
  ctx.fillStyle='rgba(85,185,205,.5)';ctx.beginPath();ctx.ellipse(0,-22,7,17,0,0,Math.PI*2);ctx.fill();
  ctx.restore();
}
function visualFallback(now){
  requestAnimationFrame(visualFallback);
  if(!fallbackCtx||window.CITY_SKYRMION_TERRAIN3D?.ready){fallbackCtx?.clearRect(0,0,innerWidth,innerHeight);return}
  sizeFallback();const w=innerWidth,h=innerHeight,d=rt.telemetry(),r=d.roll||0,p=d.pitch||0;
  fallbackCtx.clearRect(0,0,w,h);
  const sky=fallbackCtx.createLinearGradient(0,0,0,h);sky.addColorStop(0,'rgba(111,50,18,.55)');sky.addColorStop(.5,'rgba(63,78,80,.36)');sky.addColorStop(1,'rgba(4,9,12,.7)');fallbackCtx.fillStyle=sky;fallbackCtx.fillRect(0,0,w,h);
  fallbackCtx.save();fallbackCtx.translate(w*.5,h*.55+p*h*.13);fallbackCtx.rotate(-r*.22);fallbackCtx.strokeStyle='rgba(225,245,240,.12)';
  for(let y=-h;y<h;y+=54){fallbackCtx.beginPath();fallbackCtx.moveTo(-w,y+(now*.04)%54);fallbackCtx.lineTo(w,y+(now*.04)%54);fallbackCtx.stroke()}fallbackCtx.restore();
  drawFallbackCraft(fallbackCtx,w,h,d.vehicleName,r,p);
}
requestAnimationFrame(visualFallback);

function syncButtons(){[...root?.querySelectorAll('[data-vehicle]')||[]].forEach(q=>q.classList.toggle('on',q.dataset.vehicle===rt.vehicle.id));}
const mathPanel=document.getElementById('craftMathPanel'),mathBody=document.getElementById('craftMathBody');
let shownMathId=null;
function loadCraftMath(){if(shownMathId===rt.vehicle.id)return;shownMathId=rt.vehicle.id;showCraftMath(shownMathId,mathBody);if(mathPanel)mathPanel.hidden=false;}
document.getElementById('mathToggle')?.addEventListener('click',()=>{if(mathPanel)mathPanel.hidden=!mathPanel.hidden});
document.getElementById('mathClose')?.addEventListener('click',()=>{if(mathPanel)mathPanel.hidden=true});
if(root){
 root.textContent='';
 for(const [evidence,label] of [['conventional','CONVENTIONAL'],['experimental-simulation','EXPERIMENTAL']]){
  const group=document.createElement('div');group.className='craft-group';group.setAttribute('role','group');group.setAttribute('aria-label',label+' craft');
  const title=document.createElement('span');title.className='craft-label';title.textContent=label;group.appendChild(title);
  VEHICLE_ORDER.filter(id=>vehicle(id).evidence===evidence).forEach(id=>{const b=document.createElement('button');b.textContent=vehicle(id).name;b.dataset.vehicle=id;b.onclick=()=>{
   if(rt.mission.replaying)rt.stopReplay();rt.setVehicle(id);keys={};stickRoll=stickPitch=0;if(knob)knob.style.transform='none';syncButtons();loadCraftMath();if(id==='manta')initManta();else stopManta();
  };group.appendChild(b);});root.appendChild(group);
 }
}
loadCraftMath();syncButtons();
let drag=false,stickRoll=0,stickPitch=0,keys={},receiptControl=null,receiptAt=0;
function shapeAxis(v,{deadzone=.055,expo=.38,max=1}={}){
  const sign=Math.sign(v),a=Math.min(1,Math.abs(v));
  if(a<=deadzone)return 0;
  const n=(a-deadzone)/(1-deadzone),shaped=(1-expo)*n+expo*n*n*n;
  return sign*Math.min(max,shaped*max);
}
const flightInput=installFlightInteractionStandard({
  surface:'SKYRMION',
  baseThrottle:()=>rt.trim?.throttle??.72,
  cameraModes:['CHASE','WING','ORBIT'],
  mountHud:false,
  onControls:d=>{
    const receiptFresh=receiptControl&&(performance.now()-receiptAt)<2200&&!d.engaged;
    const src=receiptFresh?receiptControl:d;
    rt.setControls({
      roll:shapeAxis(src.roll||0,{deadzone:.05,expo:.42,max:.92}),
      pitch:shapeAxis(src.pitch||0,{deadzone:.05,expo:.44,max:.88}),
      yaw:shapeAxis(src.yaw||0,{deadzone:.02,expo:.20,max:.52}),
      throttle:receiptFresh?Math.max(.05,Math.min(1,Number(src.throttle)||0)):d.throttle
    });
  },
  onFleet:i=>root?.querySelector(`[data-vehicle="${VEHICLE_ORDER[i]}"]`)?.click()
});
window.CITY_SKYRMION_FLIGHT_INPUT=flightInput;
function setStick(px,py){
  if(!stick)return;
  const r=stick.getBoundingClientRect(),dx=Math.max(-1,Math.min(1,(px-r.left-r.width/2)/(r.width*.34))),dy=Math.max(-1,Math.min(1,(py-r.top-r.height/2)/(r.height*.34)));
  stickRoll=dx;stickPitch=-dy;flightInput.setPointerAxes(stickRoll,stickPitch);
  if(knob)knob.style.transform=`translate(${dx*32}px,${dy*32}px)`;
}
stick?.addEventListener('pointerdown',e=>{drag=true;stick.setPointerCapture(e.pointerId);setStick(e.clientX,e.clientY)});
stick?.addEventListener('pointermove',e=>{if(drag)setStick(e.clientX,e.clientY)});
for(const n of ['pointerup','pointercancel'])stick?.addEventListener(n,()=>{drag=false;stickRoll=stickPitch=0;flightInput.setPointerAxes(0,0);if(knob)knob.style.transform='none'});
addEventListener('message',e=>{
  const d=e.data;
  if(d?.type!=='EIDOLON:AETHERIS_STATE_TRANSITION'||!d.control)return;
  receiptControl=d.control;receiptAt=performance.now();
});
const requestedVehicle=new URLSearchParams(location.search).get('vehicle');
if(requestedVehicle&&VEHICLE_ORDER.includes(requestedVehicle))root?.querySelector(`[data-vehicle="${requestedVehicle}"]`)?.click();

}
requestAnimationFrame(controls);
addEventListener('blur',()=>{keys={};stickRoll=0;stickPitch=0;if(knob)knob.style.transform='none'});
let mantaWorker=null,mantaReady=false,mantaBusy=false,lastManta=0;
function stopManta(){mantaWorker?.terminate();mantaWorker=null;mantaReady=false;mantaBusy=false;rt.mantaFrame=null;}
function initManta(){if(mantaWorker)return;mantaWorker=new Worker(new URL('../manta-worker.js',import.meta.url));mantaWorker.onmessage=({data})=>{if(data?.type==='ready')mantaReady=true;else if(data?.type==='frame'){mantaBusy=false;if(rt.vehicle.id!=='manta')return;rt.mantaFrame=data.state;dispatchEvent(new CustomEvent('skyrmion:manta-frame',{detail:data.state}));}else if(data?.type==='error')mantaBusy=false;};mantaWorker.postMessage({type:'init',schema:'MANTA-PYTHON-BRIDGE-1.0'});}
function stepManta(now){if(rt.vehicle.id==='manta'&&mantaReady&&!mantaBusy&&now-lastManta>34){lastManta=now;mantaBusy=true;const c=rt.state.controls,effort=Math.min(1,Math.hypot(c.pitch,c.roll,c.yaw));mantaWorker.postMessage({type:'step',pilot:{pitch:c.pitch,roll:c.roll,yaw:c.yaw,morph:effort,mode:effort>.45?'MANEUVER':'CRUISE'}});}requestAnimationFrame(stepManta)}requestAnimationFrame(stepManta);
addEventListener('skyrmion:runtime2-telemetry',e=>{
 const d=e.detail;loadCraftMath();
 if(tele)tele.textContent=`${d.vehicleName} · ${Math.round(d.speedKt)} KT · ${Math.round(d.altitude_m/0.3048).toLocaleString()} FT · M ${d.mach.toFixed(2)}`+(d.e47?` · Ω ${d.e47.capture.toFixed(3)}`:'');
 if(gps){const ns=d.lat>=0?'N':'S',ew=d.lon>=0?'E':'W';gps.textContent=`${Math.abs(d.lat).toFixed(6)}° ${ns} · ${Math.abs(d.lon).toFixed(6)}° ${ew} · ${Math.round(d.altitude_m).toLocaleString()} m`;}
 syncButtons();
 if(proofPanel){const p=d.proof;proofPanel.textContent=`${d.vehicleName} · ${d.evidence==='conventional'?'CONVENTIONAL 6DOF':'EXPERIMENTAL SIMULATION'}
${d.propulsion?.adapter||d.propulsion?.engine||''}
Mach ${d.mach.toFixed(3)} · q̄ ${Math.round(d.qbar).toLocaleString()} Pa · α ${(d.alpha*180/Math.PI).toFixed(2)}°
${d.e47?`E47 Ω ${d.e47.capture.toFixed(6)} · residual ${d.e47.residual.toExponential(2)}`:'Aerodynamics + engine thrust'}
Numerical checks ${p?.pass?'PASS':'FAIL'} · t ${d.t.toFixed(2)} s
${p?.scope||''}`;}
 const status=document.getElementById('flightFault');if(status){status.hidden=!d.fault;status.textContent=d.fault?`Flight paused: ${d.fault.reason}. Select a craft or Reset flight.`:'';}
 const replay=document.getElementById('missionReplay');if(replay&&!rt.mission.replaying){replay.classList.remove('on');replay.textContent='REPLAY';}
});
const chip=document.createElement('span');chip.className='chip optional';chip.id='runtime2Status';chip.textContent='RT2 · 120 HZ · 6DOF';document.querySelector('.top')?.appendChild(chip);
const stargateChip=document.createElement('span');stargateChip.className='chip optional';stargateChip.id='stargateStatus';stargateChip.textContent='STARGATE · 47/125 · OPEN';stargateChip.title='Corrected Stargate formalism attached as E2 simulation telemetry. Physical wormhole closure remains open.';document.querySelector('.top')?.appendChild(stargateChip);
addEventListener('skyrmion:runtime2-telemetry',e=>{const d=e.detail,p=d.proof;chip.textContent=`RT2 · 120 HZ · 6DOF · ${d.evidence==='conventional'?'AERO':'EXP SIM'} · ${p?.pass===false?'NUMERICS FAIL':'NUMERICS OK'}`;chip.classList.toggle('live',p?.pass!==false);stargateChip.classList.toggle('live',Boolean(d.stargate));});
document.getElementById('proofToggle')?.addEventListener('click',()=>proofPanel?.classList.toggle('open'));
document.getElementById('missionRecord')?.addEventListener('click',e=>{rt.mission.recording=!rt.mission.recording;e.currentTarget.classList.toggle('on',rt.mission.recording);e.currentTarget.textContent=rt.mission.recording?'REC ON':'REC OFF';});
document.getElementById('flightReset')?.addEventListener('click',()=>{if(rt.mission.replaying)rt.stopReplay();rt.reset();keys={};stickRoll=stickPitch=0;if(knob)knob.style.transform='none';});
document.getElementById('missionClear')?.addEventListener('click',()=>rt.mission.clear());
document.getElementById('missionReplay')?.addEventListener('click',e=>{if(rt.mission.replaying){rt.stopReplay();e.currentTarget.classList.remove('on');e.currentTarget.textContent='REPLAY';}else if(rt.playReplay()){e.currentTarget.classList.add('on');e.currentTarget.textContent='STOP REPLAY';}});
document.getElementById('missionExport')?.addEventListener('click',()=>{const blob=new Blob([JSON.stringify(rt.mission.export(),null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='skyrmion-mission.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);});
window.CITY_SKYRMION_EXPORT_MISSION=()=>rt.mission.export();window.CITY_SKYRMION_EXPORT_PROOF=()=>rt.exportProof();rt.start();
