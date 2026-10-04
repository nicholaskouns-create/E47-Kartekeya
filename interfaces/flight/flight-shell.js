import {installCityCinemaCodec} from './city-cinema-codec.js';
import {installCityGps,drawGpsOverlay} from '../shared/city-gps-runtime.js';
import {installStargateInvariantBridge} from '../shared/stargate-invariants.js';
import {installWorldBinding,readWorldState} from '../shared/world-engine/world-binding.js';
import {installCanonicalE47Binding} from '../shared/e47-kernel-binding.js';
const body=document.body;
const source=body.dataset.source;
const mode=body.dataset.mode||'Flight mode';
const level=Number(body.dataset.level||1);
const step=Number(body.dataset.step||1);
const total=Number(body.dataset.total||6);
const objective=body.dataset.objective||'Explore the interface.';
const next=body.dataset.next||'';
const prev=body.dataset.prev||'';

const sim=document.getElementById('sim');
const sourceOpen=document.getElementById('sourceOpen');
const modeName=document.getElementById('modeName');
const objectiveEl=document.getElementById('objective');
const progress=document.getElementById('progress');
const gpuChip=document.getElementById('gpuChip');
const inputChip=document.getElementById('inputChip');
const qualityChip=document.getElementById('qualityChip');
const qualityBtn=document.getElementById('qualityBtn');
const fullscreenBtn=document.getElementById('fullscreenBtn');
const nextLink=document.getElementById('nextLink');
const prevLink=document.getElementById('prevLink');
const field=document.getElementById('field');
const ctx=field?.getContext('2d');
const savedWorld=readWorldState();
const worldChip=document.createElement('span');
worldChip.className='chip live';
document.querySelector('.hud .top .cluster')?.appendChild(worldChip);
const world=installWorldBinding({
  surface:'FLIGHT/'+String(mode).toUpperCase(),
  initial:savedWorld||undefined,
  postTarget:sim,
  generateCell:true,
  onState:(s,cell)=>{
    worldChip.textContent='WORLD · '+(cell?.biome?.id||'WGS84').toUpperCase()+' · '+s.lat.toFixed(4)+' · '+s.lon.toFixed(4);
  }
});
window.CITY_WORLD=world;
const seedWorld=world.state;
const gps=installCityGps({
  postTarget:sim,
  label:'GPS',
  seed:{lat:seedWorld.lat,lon:seedWorld.lon,altitude_m:seedWorld.altitudeM},
  onUpdate:d=>world.update({lat:d.lat,lon:d.lon,altitude_m:d.altitude_m})
});
sim?.addEventListener('load',()=>{gps.publish();world.publishTo(sim)});

const stargate=installStargateInvariantBridge({
  surface:`FLIGHT/${mode}`,
  container:document.querySelector('.hud .top .cluster'),
  postTarget:sim,
  readModeled:()=>({
    mode,
    level,
    step,
    receipt_step:Number(body.dataset.receiptStep||0)||null,
    receipt_digest:body.dataset.receiptDigest||null
  })
});
window.CITY_STARGATE=stargate;

const e47Binding=installCanonicalE47Binding({
  surface:`FLIGHT/${mode}`,
  container:document.querySelector('.hud .top .cluster'),
  postTarget:sim
}).catch(()=>null);
window.CITY_E47_BINDING=e47Binding;

let receiptFlightBinding=null;
let receiptChip=null;
if(mode.toUpperCase()==='EIDOLON'){
  receiptChip=document.createElement('span');
  receiptChip.className='chip';
  receiptChip.textContent='AETHERIS · WAITING';
  document.querySelector('.hud .top .cluster')?.appendChild(receiptChip);
  import('./aetheris-flight-binding.js').then(({createEidolonFlightReceiptBinding})=>{
    receiptFlightBinding=createEidolonFlightReceiptBinding({
      sim,
      onApply:r=>{
        const live=['PASS','RECEIVED','COMPLETED','LOCAL-WITNESS'].includes(String(r.status||'').toUpperCase());
        receiptChip.textContent=`AETHERIS · ${String(r.status||'RECEIVED').toUpperCase()} · STEP ${r.step ?? '—'}`;
        receiptChip.classList.toggle('live',live);
        if(r.step!=null)body.dataset.receiptStep=String(r.step);
        if(r.state_after_digest)body.dataset.receiptDigest=String(r.state_after_digest).slice(0,12);
      }
    });
  }).catch(()=>{
    receiptChip.textContent='AETHERIS · BINDING UNAVAILABLE';
    receiptChip.classList.remove('live');
  });
}

sim.src=source;
sourceOpen.href=source;
modeName.textContent=mode;
objectiveEl.textContent=objective;
body.classList.add(`level-${level}`);

const coreHref=new URL('../../kouns-core/?module=eidolon#flight',location.href).href;
const coreLink=document.createElement('a');
coreLink.className='button';
coreLink.href=coreHref;
coreLink.textContent='CITY CORE';
document.querySelector('.hud .top .cluster:last-of-type')?.prepend(coreLink);

if(next){nextLink.href=next;nextLink.hidden=false}else nextLink.hidden=true;
if(prev){prevLink.href=prev;prevLink.hidden=false}else prevLink.hidden=true;

for(let i=1;i<=total;i++){
  const bar=document.createElement('i');
  if(i<=step)bar.className='on';
  progress.appendChild(bar);
}

function chooseAutoQuality(){
  const memory=navigator.deviceMemory||4;
  const cores=navigator.hardwareConcurrency||4;
  const dpr=Math.min(devicePixelRatio||1,3);
  const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
  if(reduced||memory<=2||cores<=4||dpr>2.6)return 'low';
  if(memory>=8&&cores>=8)return 'high';
  return 'auto';
}

let quality=localStorage.getItem('city-flight-quality')||chooseAutoQuality();
function applyQuality(q){
  quality=q;
  body.dataset.quality=q;
  qualityChip.textContent=`VISUAL ${q.toUpperCase()}`;
  localStorage.setItem('city-flight-quality',q);
}
applyQuality(quality);
qualityBtn.addEventListener('click',()=>{
  const order=['auto','high','low'];
  applyQuality(order[(order.indexOf(quality)+1)%order.length]);
});

(async()=>{
  if(!navigator.gpu){gpuChip.textContent='GPU · WEBGL PATH';return;}
  try{
    const adapter=await navigator.gpu.requestAdapter({powerPreference:'high-performance'});
    gpuChip.textContent=adapter?'GPU · WEBGPU READY':'GPU · WEBGL PATH';
  }catch{gpuChip.textContent='GPU · WEBGL PATH';}
})();

function refreshGamepad(){
  const pads=navigator.getGamepads?.()||[];
  const pad=[...pads].find(Boolean);
  inputChip.textContent=pad?'INPUT · GAMEPAD':'INPUT · TOUCH/KEYS';
}
window.addEventListener('gamepadconnected',refreshGamepad);
window.addEventListener('gamepaddisconnected',refreshGamepad);
setInterval(refreshGamepad,1500);
refreshGamepad();

fullscreenBtn.addEventListener('click',async()=>{
  try{
    if(!document.fullscreenElement){
      await document.documentElement.requestFullscreen();
      try{await screen.orientation?.lock?.('landscape')}catch{}
    }else{
      await document.exitFullscreen();
    }
  }catch{}
});

const cinema=installCityCinemaCodec({canvas:field});
const renderChip=document.createElement('span');
renderChip.className='chip';
document.querySelector('.hud .top .cluster')?.appendChild(renderChip);
setInterval(()=>{
  const s=cinema?.state||{};
  renderChip.textContent='RENDER · '+String(s.backend||'canvas2d').toUpperCase()+' · '+(s.fps||0)+' FPS · '+Math.round((s.scale||1)*100)+'%';
  renderChip.classList.toggle('live',(s.fps||0)>=42);
},1000);

function sizeField(){
  if(!field||!ctx)return;
  const baseScale=quality==='high'?Math.min(devicePixelRatio||1,2):1;
  const scale=Math.max(.65,baseScale*(cinema?.state?.scale||1));
  field.width=Math.floor(innerWidth*scale);
  field.height=Math.floor(innerHeight*scale);
  field.style.width=`${innerWidth}px`;
  field.style.height=`${innerHeight}px`;
  ctx.setTransform(scale,0,0,scale,0,0);
}
window.addEventListener('resize',sizeField);
window.addEventListener('city:render-scale',sizeField);
sizeField();

let t0=performance.now();
function draw(now){
  if(!ctx||quality==='low'||matchMedia('(prefers-reduced-motion: reduce)').matches){requestAnimationFrame(draw);return;}
  const w=innerWidth,h=innerHeight,t=(now-t0)/1000;
  const receiptSample=receiptFlightBinding?.sample?.()||null;
  const control=receiptSample?.control||{yaw:0,pitch:0,roll:0,vertical:0,throttle:0,speed:0};
  const receiptStep=Number(receiptSample?.step||0);
  const phaseOffset=receiptStep*.015+control.yaw*.25;
  ctx.clearRect(0,0,w,h);
  ctx.lineWidth=1;
  const alpha=level===3?.16:level===2?.11:.07;
  ctx.strokeStyle=`rgba(102,221,211,${alpha})`;
  const cx=w/2+control.roll*w*.035,cy=h/2+control.pitch*h*.035-control.vertical*h*.02;
  const rings=level===3?5:level===2?3:2;
  for(let r=1;r<=rings;r++){
    ctx.beginPath();
    const radius=((80+r*78)+(Math.sin((t+phaseOffset)*.45+r)*7))*(1+control.throttle*.04);
    const rotation=Math.sin((t+phaseOffset)*.11)*.08+control.roll*.12;
    ctx.ellipse(cx,cy,radius,radius*.56,rotation,0,Math.PI*2);
    ctx.stroke();
  }
  if(level>=2){
    const n=level===3?26:14;
    for(let i=0;i<n;i++){
      const phase=i/n*Math.PI*2+(t+phaseOffset)*(level===3?.08:.04);
      const r=Math.min(w,h)*(.22+(i%5)*.035)*(1+control.throttle*.025);
      const x=cx+Math.cos(phase)*r;
      const y=cy+Math.sin(phase)*r*.55;
      ctx.fillStyle=`rgba(185,230,200,${level===3?.35:.2})`;
      ctx.fillRect(x,y,1.5,1.5);
    }
  }
  drawGpsOverlay(ctx,w,h,gps.state,{alpha:level===3?.075:.045});
  requestAnimationFrame(draw);
}
requestAnimationFrame(draw);
