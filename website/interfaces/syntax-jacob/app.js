import {installCityCinemaCodec} from '../flight/city-cinema-codec.js';
import {installStargateInvariantBridge} from '../shared/stargate-invariants.js';
import {installWorldBinding,readWorldState} from '../shared/world-engine/world-binding.js';
import {installFlightInteractionStandard} from '../shared/flight-interaction-standard.js';
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';

const AU_KM=149597870.7,DAY_S=86400,EPS=1/99144;
const MATRIX_ENDPOINT='https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter';
const EPHEMERIS_ENDPOINT='https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/syntax-jacob-ephemeris';
const EPHEMERIS_MIRROR='https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/syntax-jacob-ephemeris';
const GRAPHICS_MODULE='https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-graphics-accelerator?format=module';
const EARTH_TEXTURE='https://assets.science.nasa.gov/content/dam/science/esd/eo/images/bmng/bmng-base/january/world.200401.3x5400x2700.jpg';
const SPECTRUM=[0,2,6,12,20,30,42],$=id=>document.getElementById(id);
const fmt=(n,d=3)=>Number.isFinite(n)?Number(n).toFixed(d):'—',norm=v=>Math.hypot(...v),subv=(a,b)=>a.map((x,i)=>x-b[i]);
let feed=null,focus='comet',scalarLock=true,lastContract=0,lastWitness=0,propulsionMode='coherence',throttle=.35,deltaV=0,lastAccel=0,lastCapture=0;
const sharedWorld=installWorldBinding({
  surface:'SYNTAX JACOB',
  initial:readWorldState()||undefined,
  generateCell:true,
  onState:(s,cell)=>{
    document.body.dataset.worldCell=cell?.id||'';
    document.body.dataset.worldAnchor=s.lat.toFixed(6)+','+s.lon.toFixed(6);
  }
});
window.CITY_WORLD=sharedWorld;
const stargate=installStargateInvariantBridge({
  surface:'SYNTAX JACOB',
  container:document.querySelector('.source-strip'),
  readModeled:()=>({
    e47_capture:lastCapture,
    scalar_lock:scalarLock,
    propulsion_mode:propulsionMode,
    throttle,
    modeled_delta_v:deltaV,
    modeled_accel:lastAccel,
    world_anchor:{lat:sharedWorld.state.lat,lon:sharedWorld.state.lon,altitude_m:sharedWorld.state.altitudeM}
  })
});
window.CITY_STARGATE=stargate;

function casimir(state){
  const out=Array.from({length:125},()=>[0,0]);
  for(let i=0;i<125;i++){
    const d=[Math.floor(i/25),Math.floor(i/5)%5,i%5],m=d.map(x=>2-x),str=[25,5,1];
    const diag=18+2*(m[0]*m[1]+m[0]*m[2]+m[1]*m[2]);
    for(let c=0;c<2;c++)out[i][c]+=diag*state[i][c];
    for(let a=0;a<3;a++)for(let b=a+1;b<3;b++)for(const sign of [-1,1]){
      if(Math.abs(m[a]+sign)>2||Math.abs(m[b]-sign)>2)continue;
      const t=i-sign*str[a]+sign*str[b],coef=Math.sqrt((6-m[a]*(m[a]+sign))*(6-m[b]*(m[b]-sign)));
      for(let c=0;c<2;c++)out[t][c]+=coef*state[i][c];
    }
  }
  return out;
}
function combine(a,b,k){return a.map((r,i)=>[r[0]+k*b[i][0],r[1]+k*b[i][1]])}
function kOp(state){const c=casimir(state),cc=casimir(c);return state.map((r,i)=>[cc[i][0]-36*c[i][0]+180*r[0],cc[i][1]-36*c[i][1]+180*r[1]])}
function projectRoot(state,root){let p=state.map(r=>r.slice());for(const ev of SPECTRUM.filter(v=>v!==root)){const cp=casimir(p);p=p.map((r,i)=>[(cp[i][0]-ev*r[0])/(root-ev),(cp[i][1]-ev*r[1])/(root-ev)])}return p}
function project47(state){return combine(projectRoot(state,6),projectRoot(state,30),1)}
function norm2(a){return a.reduce((s,r)=>s+r[0]*r[0]+r[1]*r[1],0)}
function normalized(a){const n=Math.sqrt(norm2(a))||1;return a.map(r=>[r[0]/n,r[1]/n])}
function witnessLocal(state){const p=project47(state),k=kOp(state);return{capture:norm2(p)/norm2(state),residual:Math.sqrt(norm2(k))}}
function contract(state){return normalized(combine(state,kOp(kOp(state)),-EPS))}
function seedState(){return normalized(Array.from({length:125},(_,i)=>[Math.sin(i*1.618+.47)+.17*Math.cos(i*.31),Math.cos(i*.73-.47)*.3]))}
let rho=seedState();
function postReceipt(kind,detail={}){
  const w=witnessLocal(rho);
  const receipt={
    type:'aetheris.receipt',
    module:'SYNTAX JACOB',
    status:'RECEIVED',
    evidence_class:'E2',
    timestamp:new Date().toISOString(),
    state_transition:{kind,focus,scalar_lock:scalarLock,propulsion_mode:propulsionMode,throttle,capture:w.capture,residual:w.residual,omega_c:47/125,...detail},
    certificate:{status:'PASS',evidence_class:'E2'},
    stargate:stargate.packet(),
    output_packet:{state_transition:{kind,focus,scalar_lock:scalarLock,propulsion_mode:propulsionMode,throttle,capture:w.capture,omega_c:47/125,...detail},world_anchor:sharedWorld.state,stargate:stargate.packet()}
  };
  try{window.parent?.postMessage(receipt,'*')}catch{}
}
function perturbState(amount=.015){rho=normalized(rho.map((r,i)=>[r[0]+amount*Math.sin(i*.91+performance.now()*.001),r[1]+amount*.4*Math.cos(i*.37)]))}

async function fetchEphemeris(url){
  const r=await fetch(url,{cache:'no-store'}),j=await r.json();
  if(!r.ok||!j.ok)throw new Error(j.error||('Ephemeris '+r.status));
  return j;
}
async function refreshData(){
  $('feed-dot').className='dot pending';$('feed-status').textContent='JPL · CONNECTING';$('refresh').textContent='SYNCING';
  try{
    let j,source='CITY PROXY';
    try{j=await fetchEphemeris(EPHEMERIS_ENDPOINT)}
    catch(primaryError){console.warn('Syntax Jacob City proxy fallback',primaryError);j=await fetchEphemeris(EPHEMERIS_MIRROR);source='MIRROR PROXY'}
    const comet={position:j.comet.position_au,velocity:j.comet.velocity_au_per_day,calendar:j.comet.calendar,command:j.comet.command};
    const earth={position:j.earth.position_au,velocity:j.earth.velocity_au_per_day,calendar:j.earth.calendar};
    feed={time:new Date(j.requested_at),comet,earth,sbdb:j.sbdb,range:j.relative.earth_to_comet_au,relSpeed:j.relative.relative_speed_km_s,source};
    $('feed-dot').className='dot live';$('feed-status').textContent='JPL · LIVE · '+source;updateTelemetry();placeBodies();
    rho=normalized(rho.map((r,i)=>[r[0]+.002*Math.sin((comet.position[i%3]||0)*i),r[1]+.002*Math.cos((earth.position[i%3]||0)*i)]));
    postReceipt('ephemeris-refresh',{source,earth_to_comet_au:feed.range});
  }catch(e){
    $('feed-dot').className='dot error';$('feed-status').textContent='JPL · FEED ERROR';
    $('copilot-text').textContent='Both server-side JPL truth feeds failed. The 3D scene remains interactive, but trajectory telemetry is not presented as current.';
    console.error(e);
  }finally{$('refresh').textContent='REFRESH'}
}
function updateTelemetry(){
  if(!feed)return;const{comet,sbdb:s}=feed,cr=norm(comet.position),cs=norm(comet.velocity)*AU_KM/DAY_S;
  $('epoch').textContent=feed.time.toISOString().replace('.000','');$('range').textContent=fmt(feed.range,4)+' AU';$('comet-r').textContent=fmt(cr,4)+' AU';$('comet-speed').textContent=fmt(cs,2)+' km/s';$('rel-speed').textContent=fmt(feed.relSpeed,2)+' km/s';$('orbit-id').textContent=s?.orbit?.orbit_id??'—';
  $('vector').textContent=['X  '+fmt(comet.position[0],9),'Y  '+fmt(comet.position[1],9),'Z  '+fmt(comet.position[2],9),'VX '+fmt(comet.velocity[0],9),'VY '+fmt(comet.velocity[1],9),'VZ '+fmt(comet.velocity[2],9)].join('\n');
}

const canvas=$('scene'),renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance',alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight,false);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.05;
const scene=new THREE.Scene();scene.background=new THREE.Color(0x020405);scene.fog=new THREE.FogExp2(0x020405,.0015);
const camera=new THREE.PerspectiveCamera(47,innerWidth/innerHeight,.05,1200);camera.position.set(18,13,48);
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.dampingFactor=.055;controls.minDistance=2.2;controls.maxDistance=300;
const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),.85,.55,.82));

const starG=new THREE.BufferGeometry(),starP=new Float32Array(9000*3);
for(let i=0;i<9000;i++){const r=160+Math.random()*580,u=Math.random()*2-1,t=Math.random()*Math.PI*2,s=Math.sqrt(1-u*u);starP[i*3]=r*s*Math.cos(t);starP[i*3+1]=r*u;starP[i*3+2]=r*s*Math.sin(t)}
starG.setAttribute('position',new THREE.BufferAttribute(starP,3));scene.add(new THREE.Points(starG,new THREE.PointsMaterial({size:.42,color:0x9bb8c7,transparent:true,opacity:.78,sizeAttenuation:true})));

const sun=new THREE.Mesh(new THREE.SphereGeometry(2.3,64,64),new THREE.MeshBasicMaterial({color:0xffd18a}));scene.add(sun);
const sunGlow=new THREE.Mesh(new THREE.SphereGeometry(3.7,48,48),new THREE.MeshBasicMaterial({color:0xff8a3b,transparent:true,opacity:.08,blending:THREE.AdditiveBlending,depthWrite:false}));scene.add(sunGlow);
scene.add(new THREE.PointLight(0xfff3dc,1500,0,1.1));scene.add(new THREE.AmbientLight(0x6e8292,.16));
const orbitPts=Array.from({length:256},(_,i)=>new THREE.Vector3(Math.cos(i/255*Math.PI*2)*34,0,Math.sin(i/255*Math.PI*2)*34));
scene.add(new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(orbitPts),new THREE.LineBasicMaterial({color:0x1e5964,transparent:true,opacity:.26})));

const earthGroup=new THREE.Group();scene.add(earthGroup);
const earthMat=new THREE.MeshStandardMaterial({color:0x476e90,roughness:.72,metalness:0}),earth=new THREE.Mesh(new THREE.SphereGeometry(2.15,128,128),earthMat);earth.rotation.z=THREE.MathUtils.degToRad(23.44);earthGroup.add(earth);
new THREE.TextureLoader().load(EARTH_TEXTURE,t=>{t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());earthMat.map=t;earthMat.color.set(0xffffff);earthMat.needsUpdate=true},undefined,()=>console.warn('NASA Earth texture unavailable; fallback retained'));
const atmosphere=new THREE.Mesh(new THREE.SphereGeometry(2.25,96,96),new THREE.ShaderMaterial({side:THREE.BackSide,transparent:true,blending:THREE.AdditiveBlending,depthWrite:false,vertexShader:'varying vec3 vN;varying vec3 vP;void main(){vN=normalize(normalMatrix*normal);vec4 p=modelViewMatrix*vec4(position,1.);vP=p.xyz;gl_Position=projectionMatrix*p;}',fragmentShader:'varying vec3 vN;varying vec3 vP;void main(){float f=pow(1.0-max(0.0,dot(normalize(-vP),vN)),3.2);gl_FragColor=vec4(.12,.55,1.,f*.55);}'}));earthGroup.add(atmosphere);

const cometGroup=new THREE.Group();scene.add(cometGroup);const geo=new THREE.IcosahedronGeometry(1.05,5),pos=geo.attributes.position;
for(let i=0;i<pos.count;i++){const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i),n=Math.sin(x*8.31+y*3.17+z*5.93)*.085+Math.sin(x*19.2-z*11.7)*.04+Math.cos(y*27.1+x*4.4)*.025,s=1+n;pos.setXYZ(i,x*s,y*s,z*s)}
geo.computeVertexNormals();const nucleus=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:0x5b4637,roughness:.91,metalness:.03}));nucleus.scale.set(1,.76,.68);cometGroup.add(nucleus);
const coma=new THREE.Mesh(new THREE.SphereGeometry(2.9,64,64),new THREE.ShaderMaterial({transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.BackSide,vertexShader:'varying vec3 vN;varying vec3 vP;void main(){vN=normalize(normalMatrix*normal);vec4 p=modelViewMatrix*vec4(position,1.);vP=p.xyz;gl_Position=projectionMatrix*p;}',fragmentShader:'varying vec3 vN;varying vec3 vP;void main(){float a=pow(1.0-max(0.0,dot(normalize(-vP),vN)),2.4);gl_FragColor=vec4(.25,.72,1.,a*.17);}'}));cometGroup.add(coma);
function tail(count,length,spread,color,size,opacity){const g=new THREE.BufferGeometry(),p=new Float32Array(count*3);for(let i=0;i<count;i++){const t=Math.pow(Math.random(),.65),w=.08+t*spread;p[i*3]=t*length+1.1;p[i*3+1]=(Math.random()-.5)*w*(1+t);p[i*3+2]=(Math.random()-.5)*w*(1+t)}g.setAttribute('position',new THREE.BufferAttribute(p,3));const pts=new THREE.Points(g,new THREE.PointsMaterial({color,size,transparent:true,opacity,depthWrite:false,blending:THREE.AdditiveBlending,sizeAttenuation:true}));cometGroup.add(pts);return pts}
const dustTail=tail(5200,23,2.6,0xffa05b,.075,.22),ionTail=tail(3700,31,.75,0x64cfff,.06,.24);

const craft=new THREE.Group(),ring=new THREE.Mesh(new THREE.TorusGeometry(.72,.065,16,72),new THREE.MeshStandardMaterial({color:0x8af0bd,emissive:0x1c8b62,emissiveIntensity:2.7,metalness:.72,roughness:.2}));ring.rotation.x=Math.PI/2;craft.add(ring);
const craftCore=new THREE.Mesh(new THREE.OctahedronGeometry(.25,2),new THREE.MeshStandardMaterial({color:0xffffff,emissive:0x2ba68b,emissiveIntensity:1.35,metalness:.45,roughness:.2}));craft.add(craftCore);
const enginePlume=new THREE.Mesh(new THREE.ConeGeometry(.18,1.7,24,1,true),new THREE.MeshBasicMaterial({color:0x62d7dc,transparent:true,opacity:0,blending:THREE.AdditiveBlending,depthWrite:false}));enginePlume.rotation.x=Math.PI/2;enginePlume.position.z=.95;craft.add(enginePlume);
const fieldShell=new THREE.Mesh(new THREE.TorusGeometry(.95,.018,8,96),new THREE.MeshBasicMaterial({color:0x8af0bd,transparent:true,opacity:.24,blending:THREE.AdditiveBlending,depthWrite:false}));fieldShell.rotation.x=Math.PI/2;craft.add(fieldShell);
craft.scale.setScalar(1.18);scene.add(craft);
let craftOffset=new THREE.Vector3(4,1.5,6),velocity=new THREE.Vector3();
function radialDisplay(v){const r=norm(v);if(!r)return new THREE.Vector3();return new THREE.Vector3(...v).normalize().multiplyScalar(18+16*Math.log1p(r*1.8))}
function placeBodies(){if(!feed)return;earthGroup.position.copy(radialDisplay(feed.earth.position));cometGroup.position.copy(radialDisplay(feed.comet.position));const outward=cometGroup.position.clone().normalize(),rot=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(1,0,0),outward);dustTail.quaternion.copy(rot);ionTail.quaternion.copy(rot);craft.position.copy(cometGroup.position).add(craftOffset);setFocus(focus,false)}
function setFocus(next,animate=true){
  focus=next;document.querySelectorAll('.mode').forEach(b=>b.classList.toggle('active',b.dataset.focus===next));document.querySelectorAll('[data-lab-focus]').forEach(b=>b.classList.toggle('active',b.dataset.labFocus===next));$('pilot-mode').textContent=next.toUpperCase();let target=new THREE.Vector3(),dist=48;
  if(next==='comet'){target.copy(cometGroup.position);dist=16;$('copilot-text').textContent='3I chase selected. Jacob maintains a display-space intercept while the telemetry panel retains the actual JPL vector.'}
  else if(next==='earth'){target.copy(earthGroup.position);dist=12;$('copilot-text').textContent='Earth lock selected. Surface texture is NASA Blue Marble; heliocentric position comes from JPL.'}
  else if(next==='system'){target.set(0,0,0);dist=74;$('copilot-text').textContent='System view selected. Orbital distances are nonlinearly scaled for simultaneous Earth / 3I visibility.'}
  else{$('copilot-text').textContent='Free flight. Use WASD and Q/E to perturb Jacob’s modeled copilot vector and move around the scene.';return}
  controls.target.copy(target);if(animate){const dir=camera.position.clone().sub(target).normalize();camera.position.copy(target).add(dir.multiplyScalar(dist))}else if(camera.position.distanceTo(target)>180)camera.position.copy(target).add(new THREE.Vector3(dist*.6,dist*.4,dist));
}
document.querySelectorAll('.mode').forEach(b=>b.addEventListener('click',()=>setFocus(b.dataset.focus)));
$('scalar-lock').addEventListener('click',()=>{scalarLock=!scalarLock;$('scalar-lock').classList.toggle('active',scalarLock);$('scalar-lock').textContent='SCALAR COHERENCE · '+(scalarLock?'LOCKED':'MANUAL');postReceipt('scalar-lock',{scalar_lock:scalarLock})});
$('refresh').addEventListener('click',refreshData);$('egg').onclick=()=>{$('egg-panel').hidden=false};$('egg-close').onclick=()=>{$('egg-panel').hidden=true};

const keys=new Set();
addEventListener('keydown',e=>{if(['INPUT','TEXTAREA'].includes(e.target?.tagName))return;keys.add(e.key.toLowerCase());if(['w','a','s','d','q','e','arrowup','arrowdown','arrowleft','arrowright'].includes(e.key.toLowerCase()))perturbState(.012)});
addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));

let cityFlightCommand=null;
const cityFlight=installFlightInteractionStandard({
  surface:'SYNTAX JACOB',
  baseThrottle:()=>throttle,
  cameraModes:['COMET','EARTH','SYSTEM','FREE'],
  mountHud:true,
  onControls:d=>{cityFlightCommand=d},
  onCamera:mode=>setFocus(mode.toLowerCase())
});
window.CITY_SYNTAX_JACOB_FLIGHT_INPUT=cityFlight;

function propulsionGain(){return propulsionMode==='coherence'?(.65+1.35*Math.max(0,Math.min(1,lastCapture))):propulsionMode==='inertial'?1:0}
function setPropulsionMode(mode){
  propulsionMode=mode;
  document.querySelectorAll('.prop-mode').forEach(b=>b.classList.toggle('active',b.dataset.propMode===mode));
  fieldShell.material.color.set(mode==='coherence'?0x8af0bd:mode==='inertial'?0xff9f45:0x62d7dc);
  postReceipt('propulsion-mode',{propulsion_mode:mode});
}
function updateThrottle(value){
  throttle=Math.max(0,Math.min(1,Number(value)/100));
  const pct=Math.round(throttle*100);
  $('throttle-value').textContent=pct+'%';$('throttle-mini').textContent=pct+'%';$('throttle-mini-bar').style.width=pct+'%';
}
function updateLabReadouts(){
  $('lab-speed').textContent=velocity.length().toFixed(3)+' u/s';
  $('lab-accel').textContent=lastAccel.toFixed(3)+' u/s²';
  $('lab-dv').textContent=deltaV.toFixed(3)+' u/s';
  $('lab-capture').textContent=lastCapture.toFixed(4);
}
function setPropulsionPanel(open){
  $('propulsion-panel').hidden=!open;
  $('propulsion-toggle').setAttribute('aria-expanded',String(open));
}
$('propulsion-toggle').addEventListener('click',()=>setPropulsionPanel($('propulsion-panel').hidden));
$('propulsion-close').addEventListener('click',()=>setPropulsionPanel(false));
$('kill-velocity').addEventListener('click',()=>{velocity.set(0,0,0);lastAccel=0;postReceipt('velocity-zero',{modeled_speed:0});updateLabReadouts()});
$('throttle').addEventListener('input',e=>updateThrottle(e.target.value));
$('throttle').addEventListener('change',()=>postReceipt('throttle',{throttle}));
document.querySelectorAll('.prop-mode').forEach(b=>b.addEventListener('click',()=>setPropulsionMode(b.dataset.propMode)));
document.querySelectorAll('[data-lab-focus]').forEach(b=>b.addEventListener('click',()=>setFocus(b.dataset.labFocus)));

document.querySelectorAll('[data-thrust]').forEach(b=>{
  const k=b.dataset.thrust;
  const release=()=>{keys.delete(k);b.classList.remove('active')};
  b.addEventListener('pointerdown',e=>{e.preventDefault();keys.add(k);b.classList.add('active');b.setPointerCapture?.(e.pointerId);perturbState(.012)});
  b.addEventListener('pointerup',release);b.addEventListener('pointercancel',release);b.addEventListener('lostpointercapture',release);
});
$('pulse-thrust').addEventListener('click',()=>{
  if(propulsionMode==='coast'||throttle<=0)return;
  const forward=new THREE.Vector3(0,0,-1).applyQuaternion(craft.quaternion).normalize(),dv=.72*throttle*propulsionGain();
  velocity.addScaledVector(forward,dv);deltaV+=dv;perturbState(.02*throttle);postReceipt('pulse-thrust',{impulse_display_units:dv});
});
updateThrottle(35);setPropulsionMode('coherence');updateLabReadouts();

function pilotStep(dt){
  const legacyInput=new THREE.Vector3(
    (keys.has('d')||keys.has('arrowright')?1:0)-(keys.has('a')||keys.has('arrowleft')?1:0),
    (keys.has('q')?1:0)-(keys.has('e')?1:0),
    (keys.has('s')||keys.has('arrowdown')?1:0)-(keys.has('w')||keys.has('arrowup')?1:0)
  );
  const cmd=cityFlightCommand;
  const input=cmd?.engaged?new THREE.Vector3(cmd.roll,-cmd.yaw,-cmd.pitch):legacyInput;
  const effectiveThrottle=cmd?.engaged?cmd.throttle:throttle;
  const magnitude=Math.min(1,input.length());
  let accel=0;
  if(magnitude>0&&propulsionMode!=='coast'&&effectiveThrottle>0){
    input.normalize();accel=1.45*effectiveThrottle*propulsionGain()*magnitude;velocity.addScaledVector(input,accel*dt);deltaV+=accel*dt;
    const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,-1),input);craft.quaternion.slerp(q,1-Math.pow(.025,dt*60));
    perturbState(.0018*effectiveThrottle);
  }
  lastAccel=accel;
  const drag=propulsionMode==='inertial' ? .9992 : propulsionMode==='coherence' ? .9965 : .9997;
  velocity.multiplyScalar(Math.pow(drag,dt*60));
  craftOffset.addScaledVector(velocity,dt*16);craftOffset.clampLength(2.5,28);
  if(feed&&focus!=='free')craft.position.lerp(cometGroup.position.clone().add(craftOffset),1-Math.pow(.003,dt));else craft.position.addScaledVector(velocity,dt*14);
  const plumeTarget=accel>0?Math.min(.78,.16+effectiveThrottle*.62):0;enginePlume.material.opacity+= (plumeTarget-enginePlume.material.opacity)*Math.min(1,dt*12);enginePlume.scale.set(1,.7+effectiveThrottle*1.8,1);
  fieldShell.material.opacity=propulsionMode==='coherence' ? .12+.3*lastCapture : .08;fieldShell.rotation.z+=dt*(.25+throttle*1.8);
  updateLabReadouts();
}
async function remoteWitness(){try{const r=await fetch(MATRIX_ENDPOINT,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({statevector:rho,source:'Syntax Jacob',circuit:{mode:focus,scalar_lock:scalarLock,propulsion_mode:propulsionMode,throttle}})}),j=await r.json();if(!j.ok)throw new Error(j.error||'witness rejected');$('cube').textContent='CUBE WITNESS · E47 '+(j.witness.witness.e47_weight*100).toFixed(2)+'%';$('cube').style.color='var(--mint)'}catch{$('cube').textContent='CUBE WITNESS · OFFLINE';$('cube').style.color='var(--hot)'}}
function updateCoherence(){const w=witnessLocal(rho);lastCapture=w.capture;$('capture').textContent=w.capture.toFixed(6);$('capture-bar').style.width=Math.min(100,w.capture*100)+'%';$('residual').textContent=w.residual.toExponential(2);updateLabReadouts()}

let prev=performance.now();function animate(now){const dt=Math.min(.05,(now-prev)/1000);prev=now;requestAnimationFrame(animate);controls.update();earth.rotation.y+=dt*.07;nucleus.rotation.y+=dt*.15;nucleus.rotation.x+=dt*.037;sunGlow.scale.setScalar(1+.025*Math.sin(now*.002));pilotStep(dt);if(scalarLock&&now-lastContract>90){rho=contract(rho);lastContract=now;updateCoherence()}if(now-lastWitness>3500){lastWitness=now;remoteWitness()}if(focus==='comet'&&feed)controls.target.lerp(cometGroup.position,.035);else if(focus==='earth'&&feed)controls.target.lerp(earthGroup.position,.035);else if(focus==='system')controls.target.lerp(new THREE.Vector3(),.035);composer.render()}
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight,false);composer.setSize(innerWidth,innerHeight)});
(async()=>{try{const g=await import(GRAPHICS_MODULE),cap=await g.detectCityGraphicsCapabilities(),profile=g.getCityGraphicsProfile?.('SYNTAX JACOB');$('gpu').textContent='GPU · '+String(cap.backend||'webgl').toUpperCase()+' · '+String(cap.tier||'')+(profile?' · PROFILE':'');if(cap.dpr)renderer.setPixelRatio(Math.min(cap.dpr,2))}catch{$('gpu').textContent='GPU · WEBGL'}})();

updateCoherence();setFocus('comet',false);refreshData();requestAnimationFrame(animate);setTimeout(()=>$('loading').classList.add('done'),1300);setInterval(refreshData,5*60*1000);
