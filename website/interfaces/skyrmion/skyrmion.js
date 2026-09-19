import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {EffectComposer} from 'three/addons/postprocessing/EffectComposer.js';
import {RenderPass} from 'three/addons/postprocessing/RenderPass.js';
import {UnrealBloomPass} from 'three/addons/postprocessing/UnrealBloomPass.js';
import {installCityCinemaCodec} from '../flight/city-cinema-codec.js';

const MATRIX='https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter';
const GRAPHICS='https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-graphics-accelerator?format=module';
const EPHEM='https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/syntax-jacob-ephemeris';
const EPS=1/99144, OMEGA=47/125;
const aircraft=[
 {id:'f16',name:'F-16',class:'real',domain:'atmosphere',drive:'turbofan',accel:1.5,max:8.0,turn:1.45},
 {id:'sr71',name:'SR-71',class:'real',domain:'atmosphere',drive:'turboramjet',accel:1.1,max:11.0,turn:.72},
 {id:'x15',name:'X-15',class:'real',domain:'edge-space',drive:'rocket',accel:2.0,max:15.0,turn:.9},
 {id:'eidolon',name:'EIDOLON',class:'experimental',domain:'scalar',drive:'scalar-coherence',accel:2.4,max:18.0,turn:1.8},
 {id:'manta',name:'MANTA',class:'experimental',domain:'programmable-matter',drive:'spectral-morph',accel:2.0,max:16.0,turn:2.05},
 {id:'jacob',name:'SYNTAX JACOB',class:'latent',domain:'interstellar',drive:'coherence/inertial',accel:1.8,max:20.0,turn:1.25}
];
let active=0,domainIndex=0,lastWitness=0,lastCapture=OMEGA,ephem=null;
const domains=['atmosphere','orbital','interstellar'];
const canvas=document.getElementById('scene'),renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight,false);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;
const scene=new THREE.Scene(),camera=new THREE.PerspectiveCamera(62,innerWidth/innerHeight,.05,5000);camera.position.set(0,4,11);
const controls=new OrbitControls(camera,canvas);controls.enableDamping=true;controls.enablePan=false;controls.target.set(0,1,-18);
const composer=new EffectComposer(renderer);composer.addPass(new RenderPass(scene,camera));composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth,innerHeight),.42,.7,.85));
installCityCinemaCodec({renderer,composer,canvas});
scene.add(new THREE.HemisphereLight(0xbfefff,0x081015,2.5));const sun=new THREE.DirectionalLight(0xffffff,4);sun.position.set(8,18,4);scene.add(sun);
const world=new THREE.Group();scene.add(world);
const earth=new THREE.Mesh(new THREE.SphereGeometry(250,96,64),new THREE.MeshStandardMaterial({color:0x183f3b,roughness:.9,metalness:.05}));
earth.position.y=-247;world.add(earth);
const grid=new THREE.GridHelper(800,100,0x1a5555,0x0b2024);grid.position.y=.02;world.add(grid);
const stars=new THREE.Points(new THREE.BufferGeometry(),new THREE.PointsMaterial({color:0xbfefff,size:.42,sizeAttenuation:true}));
const starPos=new Float32Array(4500*3);for(let i=0;i<4500;i++){const r=800+Math.random()*2400,a=Math.random()*Math.PI*2,z=(Math.random()-.5)*1200;starPos[i*3]=Math.cos(a)*r;starPos[i*3+1]=z;starPos[i*3+2]=Math.sin(a)*r;}stars.geometry.setAttribute('position',new THREE.BufferAttribute(starPos,3));scene.add(stars);

function craftMesh(type){
 const g=new THREE.Group();
 const hull=new THREE.Mesh(new THREE.ConeGeometry(type.class==='real'?.46:.58,3.3, type.id==='manta'?5:24),new THREE.MeshStandardMaterial({color:type.class==='real'?0xb9c4c6:type.class==='experimental'?0x98e8d3:0xb0b2ff,metalness:.78,roughness:.28}));
 hull.rotation.x=-Math.PI/2;g.add(hull);
 const wing=new THREE.Mesh(new THREE.BoxGeometry(type.id==='manta'?5.3:3.4,.08,1.05),hull.material);wing.position.z=.3;g.add(wing);
 const glow=new THREE.Mesh(new THREE.TorusGeometry(.56,.035,8,64),new THREE.MeshBasicMaterial({color:0x71ffe8,transparent:true,opacity:type.class==='real'?.12:.55}));glow.rotation.x=Math.PI/2;glow.position.z=1.6;g.add(glow);g.userData.glow=glow;return g;
}
let craft=craftMesh(aircraft[0]);craft.position.set(0,3,-12);scene.add(craft),vel=new THREE.Vector3();
const keys=new Set();addEventListener('keydown',e=>{keys.add(e.key.toLowerCase());if(/^[1-6]$/.test(e.key))select(+e.key-1);if(e.key.toLowerCase()==='f')setDomain((domainIndex+1)%domains.length)});addEventListener('keyup',e=>keys.delete(e.key.toLowerCase()));

const vroot=document.getElementById('vehicles');aircraft.forEach((a,i)=>{const b=document.createElement('button');b.innerHTML=a.name+' <span class="'+a.class+'">●</span>';b.onclick=()=>select(i);b.dataset.i=i;vroot.appendChild(b)});
function select(i){active=i;scene.remove(craft);craft=craftMesh(aircraft[i]);craft.position.set(0,3,-12);scene.add(craft);vel.set(0,0,0);updateButtons();postReceipt('aircraft-select',{aircraft:aircraft[i].id})}
function updateButtons(){[...vroot.children].forEach((b,i)=>b.classList.toggle('active',i===active));document.getElementById('status').textContent=aircraft[active].name+' · '+aircraft[active].drive+' · '+aircraft[active].class.toUpperCase()}
updateButtons();
function setDomain(i){domainIndex=i;const d=domains[i];document.getElementById('domain').textContent=(d==='atmosphere'?'EARTH · ATMOSPHERE':d==='orbital'?'EARTH · ORBIT':'INTERSTELLAR').toUpperCase();grid.visible=d==='atmosphere';earth.visible=d!=='interstellar';scene.fog=d==='atmosphere'?new THREE.FogExp2(0x071318,.0018):null;postReceipt('domain-change',{domain:d})}
setDomain(0);

function buildState(){const a=aircraft[active];return Array.from({length:125},(_,i)=>[Math.sin(i*.618+active+vel.length()*.03)+.04*Math.cos(i*.13),Math.cos(i*.37+domainIndex)*.3])}
async function witness(){try{const r=await fetch(MATRIX,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({statevector:buildState(),source:'SKYRMION',circuit:{aircraft:aircraft[active].id,domain:domains[domainIndex],drive:aircraft[active].drive,speed:vel.length()}})}),j=await r.json();const w=j?.witness?.witness?.e47_weight;if(Number.isFinite(w)){lastCapture=w;document.getElementById('e47').textContent='E47 · '+(w*100).toFixed(1)+'%'}}catch{document.getElementById('e47').textContent='E47 · LOCAL'}}
function postReceipt(kind,detail={}){const a=aircraft[active],receipt={type:'aetheris.receipt',module:'SKYRMION',status:'RECEIVED',evidence_class:a.class==='real'?'E2':'E2',timestamp:new Date().toISOString(),state_transition:{kind,aircraft:a.id,aircraft_class:a.class,domain:domains[domainIndex],drive:a.drive,speed:vel.length(),e47_capture:lastCapture,omega_c:OMEGA,...detail},provenance:{interface:'website/interfaces/skyrmion',matrix_endpoint:'matrix-cube-adapter'},boundary:a.class==='real'?'simulation of conventional flight dynamics':'experimental/latent propulsion is simulation-only'}};try{localStorage.setItem('city:aetheris:last-receipt',JSON.stringify(receipt));window.parent?.postMessage(receipt,'*')}catch{}}

const mini=document.getElementById('minimap'),mctx=mini.getContext('2d');
function drawMini(){mctx.clearRect(0,0,mini.width,mini.height);mctx.strokeStyle='#78ead4';mctx.globalAlpha=.35;for(let x=0;x<mini.width;x+=32){mctx.beginPath();mctx.moveTo(x,0);mctx.lineTo(x,mini.height);mctx.stroke()}for(let y=0;y<mini.height;y+=23){mctx.beginPath();mctx.moveTo(0,y);mctx.lineTo(mini.width,y);mctx.stroke()}mctx.globalAlpha=1;mctx.fillStyle='#bfffee';mctx.beginPath();mctx.arc(mini.width/2,mini.height/2,5,0,Math.PI*2);mctx.fill();}

let prev=performance.now();
function frame(now){requestAnimationFrame(frame);const dt=Math.min(.033,(now-prev)/1000);prev=now;const a=aircraft[active],input=new THREE.Vector3((keys.has('d')?1:0)-(keys.has('a')?1:0),(keys.has('q')?1:0)-(keys.has('e')?1:0),(keys.has('s')?1:0)-(keys.has('w')?1:0));if(input.lengthSq()){input.normalize();let gain=a.accel;if(a.class!=='real')gain*=.65+1.35*Math.max(0,Math.min(1,lastCapture));vel.addScaledVector(input,gain*dt);if(vel.length()>a.max)vel.setLength(a.max);const q=new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0,0,-1),input);craft.quaternion.slerp(q,Math.min(1,a.turn*dt*3))}vel.multiplyScalar(Math.pow(a.class==='real'?.994:.997,dt*60));craft.position.addScaledVector(vel,dt*8);craft.position.x*=.999;craft.position.y=Math.max(1,craft.position.y);camera.position.lerp(craft.position.clone().add(new THREE.Vector3(0,3.4,10)),1-Math.pow(.002,dt));controls.target.lerp(craft.position.clone().add(new THREE.Vector3(0,0,-8)),1-Math.pow(.005,dt));if(craft.userData.glow)craft.userData.glow.rotation.z+=dt*(.2+vel.length()*.15);controls.update();earth.rotation.y+=dt*.006;drawMini();if(now-lastWitness>3000){lastWitness=now;witness()}composer.render()}
requestAnimationFrame(frame);
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight,false);composer.setSize(innerWidth,innerHeight)});
(async()=>{try{const g=await import(GRAPHICS),cap=await g.detectCityGraphicsCapabilities();document.getElementById('gpu').textContent='GPU · '+String(cap.backend||'WEBGL').toUpperCase();if(cap.dpr)renderer.setPixelRatio(Math.min(cap.dpr,2))}catch{document.getElementById('gpu').textContent='GPU · WEBGL'}})();
fetch(EPHEM,{cache:'no-store'}).then(r=>r.json()).then(j=>{ephem=j;document.getElementById('bus').textContent='CITY BUS · EPHEMERIS LIVE'}).catch(()=>{});
postReceipt('launch',{epsilon:EPS});
