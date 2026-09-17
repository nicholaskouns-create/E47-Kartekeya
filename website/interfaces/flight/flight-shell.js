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

sim.src=source;
sourceOpen.href=source;
modeName.textContent=mode;
objectiveEl.textContent=objective;
body.classList.add(`level-${level}`);

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

function sizeField(){
  if(!field||!ctx)return;
  const scale=quality==='high'?Math.min(devicePixelRatio||1,2):1;
  field.width=Math.floor(innerWidth*scale);
  field.height=Math.floor(innerHeight*scale);
  field.style.width=`${innerWidth}px`;
  field.style.height=`${innerHeight}px`;
  ctx.setTransform(scale,0,0,scale,0,0);
}
window.addEventListener('resize',sizeField);
sizeField();

let t0=performance.now();
function draw(now){
  if(!ctx||quality==='low'||matchMedia('(prefers-reduced-motion: reduce)').matches){requestAnimationFrame(draw);return;}
  const w=innerWidth,h=innerHeight,t=(now-t0)/1000;
  ctx.clearRect(0,0,w,h);
  ctx.lineWidth=1;
  const alpha=level===3?.16:level===2?.11:.07;
  ctx.strokeStyle=`rgba(102,221,211,${alpha})`;
  const cx=w/2,cy=h/2;
  const rings=level===3?5:level===2?3:2;
  for(let r=1;r<=rings;r++){
    ctx.beginPath();
    const radius=(80+r*78)+(Math.sin(t*.45+r)*7);
    ctx.ellipse(cx,cy,radius,radius*.56,Math.sin(t*.11)*.08,0,Math.PI*2);
    ctx.stroke();
  }
  if(level>=2){
    const n=level===3?26:14;
    for(let i=0;i<n;i++){
      const phase=i/n*Math.PI*2+t*(level===3?.08:.04);
      const r=Math.min(w,h)*(.22+(i%5)*.035);
      const x=cx+Math.cos(phase)*r;
      const y=cy+Math.sin(phase)*r*.55;
      ctx.fillStyle=`rgba(185,230,200,${level===3?.35:.2})`;
      ctx.fillRect(x,y,1.5,1.5);
    }
  }
  requestAnimationFrame(draw);
}
requestAnimationFrame(draw);
