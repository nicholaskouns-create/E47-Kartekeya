import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js";

const EPHEMERIS="https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/syntax-jacob-ephemeris";
const WITNESS="https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter";
const GRAPHICS="https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-graphics-accelerator?format=module";
const EARTH_DAY="https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57730/land_ocean_ice_2048.jpg";
const EARTH_CLOUDS="https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57747/cloud_combined_2048.jpg";

const $=id=>document.getElementById(id);
const canvas=$("scene");
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:"high-performance"});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setSize(innerWidth,innerHeight,false);
renderer.outputColorSpace=THREE.SRGBColorSpace;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.08;
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;

const scene=new THREE.Scene();
scene.background=new THREE.Color(0x020407);
scene.fog=new THREE.FogExp2(0x020407,0.018);

const camera=new THREE.PerspectiveCamera(46,innerWidth/innerHeight,.01,1000);
const orbit={theta:-.45,phi:1.06,radius:18};
const target=new THREE.Vector3(0,0,0);
const desiredTarget=new THREE.Vector3(0,0,0);

scene.add(new THREE.HemisphereLight(0x56798a,0x070706,.42));
const sun=new THREE.DirectionalLight(0xfff1d6,6.3);
sun.position.set(-18,10,12); sun.castShadow=true; scene.add(sun);
const rim=new THREE.PointLight(0x76dce7,18,36,2); rim.position.set(7,4,-9); scene.add(rim);

function seeded(seed=1){
  let s=seed>>>0;
  return ()=>{s^=s<<13;s^=s>>>17;s^=s<<5;return((s>>>0)%1000000)/1000000};
}
const rnd=seeded(470125);

function makeStars(){
  const n=6200,p=new Float32Array(n*3),c=new Float32Array(n*3);
  for(let i=0;i<n;i++){
    const r=80+Math.pow(rnd(),.45)*380, t=rnd()*Math.PI*2, u=Math.acos(2*rnd()-1);
    p[i*3]=r*Math.sin(u)*Math.cos(t);p[i*3+1]=r*Math.cos(u);p[i*3+2]=r*Math.sin(u)*Math.sin(t);
    const b=.55+rnd()*.45;c[i*3]=b*.84;c[i*3+1]=b*.91;c[i*3+2]=b;
  }
  const g=new THREE.BufferGeometry();g.setAttribute("position",new THREE.BufferAttribute(p,3));g.setAttribute("color",new THREE.BufferAttribute(c,3));
  const m=new THREE.PointsMaterial({size:.085,vertexColors:true,transparent:true,opacity:.88,sizeAttenuation:true});
  scene.add(new THREE.Points(g,m));
}
makeStars();

function makeEarth(){
  const group=new THREE.Group();group.position.set(-5.7,-.65,-1.8);
  const geo=new THREE.SphereGeometry(1.72,128,96);
  const mat=new THREE.MeshPhysicalMaterial({color:0x345c7a,roughness:.72,metalness:0,clearcoat:.08,clearcoatRoughness:.62});
  const earth=new THREE.Mesh(geo,mat);earth.castShadow=true;earth.receiveShadow=true;group.add(earth);
  const night=new THREE.PointLight(0x6fcfe6,2.2,8,2);night.position.set(-2.5,1.2,2.4);group.add(night);

  const atmGeo=new THREE.SphereGeometry(1.82,96,64);
  const atmMat=new THREE.ShaderMaterial({
    side:THREE.BackSide,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,
    uniforms:{glowColor:{value:new THREE.Color(0x70cde9)},power:{value:4.2},intensity:{value:.62}},
    vertexShader:`
      varying vec3 vNormal; varying vec3 vWorld;
      void main(){vNormal=normalize(normalMatrix*normal);vec4 w=modelMatrix*vec4(position,1.0);vWorld=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}
    `,
    fragmentShader:`
      varying vec3 vNormal; varying vec3 vWorld;
      uniform vec3 glowColor;uniform float power;uniform float intensity;
      void main(){vec3 viewDir=normalize(cameraPosition-vWorld);float fres=pow(1.0-max(dot(vNormal,viewDir),0.0),power);gl_FragColor=vec4(glowColor,fres*intensity);}
    `
  });
  group.add(new THREE.Mesh(atmGeo,atmMat));

  const cloudMat=new THREE.MeshLambertMaterial({color:0xffffff,transparent:true,opacity:.25,depthWrite:false,alphaTest:.02});
  const clouds=new THREE.Mesh(new THREE.SphereGeometry(1.746,96,64),cloudMat);group.add(clouds);

  const loader=new THREE.TextureLoader();
  loader.setCrossOrigin("anonymous");
  loader.load(EARTH_DAY,t=>{t.colorSpace=THREE.SRGBColorSpace;t.anisotropy=Math.min(16,renderer.capabilities.getMaxAnisotropy());mat.map=t;mat.needsUpdate=true;},undefined,()=>{});
  loader.load(EARTH_CLOUDS,t=>{t.colorSpace=THREE.SRGBColorSpace;cloudMat.map=t;cloudMat.alphaMap=t;cloudMat.needsUpdate=true;},undefined,()=>{});

  scene.add(group);
  return {group,earth,clouds};
}
const earthObj=makeEarth();

function makeComet(){
  const group=new THREE.Group();group.position.set(5.8,.25,-1.0);
  const geo=new THREE.IcosahedronGeometry(1.18,6);
  const pos=geo.attributes.position;
  for(let i=0;i<pos.count;i++){
    const x=pos.getX(i),y=pos.getY(i),z=pos.getZ(i);
    const n=new THREE.Vector3(x,y,z).normalize();
    const d=1+.12*Math.sin(n.x*11+n.y*4)+.08*Math.sin(n.z*17-n.x*3)+.05*Math.cos((n.x+n.z)*27);
    pos.setXYZ(i,x*d*1.14,y*d*.92,z*d*.86);
  }
  geo.computeVertexNormals();
  const nucleus=new THREE.Mesh(geo,new THREE.MeshStandardMaterial({color:0x544f48,roughness:.94,metalness:.02,bumpScale:.08}));
  nucleus.castShadow=true;group.add(nucleus);

  const comaN=5200,cp=new Float32Array(comaN*3),cc=new Float32Array(comaN*3);
  for(let i=0;i<comaN;i++){
    const rr=Math.pow(rnd(),2.7)*3.2+.35,t=rnd()*Math.PI*2,u=Math.acos(2*rnd()-1);
    cp[i*3]=rr*Math.sin(u)*Math.cos(t);cp[i*3+1]=rr*Math.cos(u);cp[i*3+2]=rr*Math.sin(u)*Math.sin(t);
    const k=1-Math.min(rr/3.6,1);cc[i*3]=.55+.42*k;cc[i*3+1]=.72+.25*k;cc[i*3+2]=.82+.18*k;
  }
  const cg=new THREE.BufferGeometry();cg.setAttribute("position",new THREE.BufferAttribute(cp,3));cg.setAttribute("color",new THREE.BufferAttribute(cc,3));
  const coma=new THREE.Points(cg,new THREE.PointsMaterial({size:.055,vertexColors:true,transparent:true,opacity:.33,depthWrite:false,blending:THREE.AdditiveBlending}));
  group.add(coma);

  const tailN=10500,tp=new Float32Array(tailN*3),tc=new Float32Array(tailN*3);
  for(let i=0;i<tailN;i++){
    const q=rnd(),len=Math.pow(q,.65)*24,width=.18+q*1.7,ang=rnd()*Math.PI*2,rad=Math.pow(rnd(),1.7)*width;
    tp[i*3]=1.1+len;tp[i*3+1]=Math.sin(ang)*rad+(q*q*.8);tp[i*3+2]=Math.cos(ang)*rad;
    const fade=1-q;tc[i*3]=.42+.45*fade;tc[i*3+1]=.68+.26*fade;tc[i*3+2]=.84+.14*fade;
  }
  const tg=new THREE.BufferGeometry();tg.setAttribute("position",new THREE.BufferAttribute(tp,3));tg.setAttribute("color",new THREE.BufferAttribute(tc,3));
  const tail=new THREE.Points(tg,new THREE.PointsMaterial({size:.045,vertexColors:true,transparent:true,opacity:.24,depthWrite:false,blending:THREE.AdditiveBlending}));
  group.add(tail);

  const halo=new THREE.Mesh(new THREE.SphereGeometry(1.85,48,32),new THREE.MeshBasicMaterial({color:0x87d7e2,transparent:true,opacity:.035,depthWrite:false,blending:THREE.AdditiveBlending}));
  group.add(halo);
  scene.add(group);
  return {group,nucleus,coma,tail};
}
const cometObj=makeComet();

function makeCraft(){
  const g=new THREE.Group();g.position.set(1.2,.9,3.2);
  const hull=new THREE.Mesh(new THREE.CapsuleGeometry(.28,1.5,10,28),new THREE.MeshPhysicalMaterial({color:0xbcc9c8,metalness:.72,roughness:.2,clearcoat:.9,clearcoatRoughness:.12}));
  hull.rotation.z=Math.PI/2;g.add(hull);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(.72,.07,18,96),new THREE.MeshStandardMaterial({color:0x77dbe1,emissive:0x245c62,emissiveIntensity:1.5,metalness:.45,roughness:.23}));
  ring.rotation.y=Math.PI/2;g.add(ring);
  const finMat=new THREE.MeshStandardMaterial({color:0x8a9698,metalness:.5,roughness:.3});
  for(const y of [-.38,.38]){
    const fin=new THREE.Mesh(new THREE.ConeGeometry(.24,.85,4),finMat);fin.position.set(-.45,y,0);fin.rotation.z=-Math.PI/2;fin.scale.z=.35;g.add(fin);
  }
  const core=new THREE.PointLight(0x71d7df,7,6,2);core.position.set(-.7,0,0);g.add(core);
  const shells=[];
  for(let i=0;i<5;i++){
    const s=new THREE.Mesh(new THREE.TorusGeometry(1+i*.18,.012,8,96),new THREE.MeshBasicMaterial({color:i%2?0xc6a26d:0x71d7df,transparent:true,opacity:.18-i*.022,depthWrite:false,blending:THREE.AdditiveBlending}));
    s.rotation.set(Math.PI/2,i*.37,0);g.add(s);shells.push(s);
  }
  scene.add(g);return {group:g,shells};
}
const craft=makeCraft();

const relArrow=new THREE.ArrowHelper(new THREE.Vector3(1,0,0),earthObj.group.position,7,0x71d7df,.35,.16);
relArrow.line.material.transparent=true;relArrow.line.material.opacity=.28;relArrow.cone.material.transparent=true;relArrow.cone.material.opacity=.5;scene.add(relArrow);

const tangentMat=new THREE.LineBasicMaterial({color:0xc6a26d,transparent:true,opacity:.34});
const tangentGeo=new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(-8,0,0),new THREE.Vector3(8,0,0)]);
const tangentLine=new THREE.Line(tangentGeo,tangentMat);cometObj.group.add(tangentLine);

const casimir=[0,2,6,12,20,30,42],mult=[1,9,25,28,27,22,13],C=[];
casimir.forEach((v,i)=>{for(let j=0;j<mult[i];j++)C.push(v)});
const K2=C.map(c=>{const k=(c-6)*(c-30);return k*k});
const EPS=1/99144;
let eState=new Float64Array(125),capture=.376,copilot=true,throttle=.62,seed=470125;

function reseedState(){
  const r=seeded(seed++);
  for(let i=0;i<125;i++)eState[i]=(r()-.5)*2;
  normalizeState();updateCapture();
}
function normalizeState(){
  let s=0;for(const x of eState)s+=x*x;s=Math.sqrt(s)||1;for(let i=0;i<125;i++)eState[i]/=s;
}
function updateCapture(){
  let k=0,n=0;for(let i=0;i<125;i++){const z=eState[i]*eState[i];n+=z;if(C[i]===6||C[i]===30)k+=z}
  capture=k/(n||1);
  $("capture").textContent=capture.toFixed(3);
  $("coherenceRing").style.setProperty("--capture-angle",(Math.max(0,Math.min(1,capture))*360).toFixed(2)+"deg");
  craft.shells.forEach((s,i)=>{s.material.opacity=.04+.19*capture*(1-i*.11);s.scale.setScalar(.78+.3*capture+.025*i)});
}
function contract(steps=1){
  for(let n=0;n<steps;n++){for(let i=0;i<125;i++)eState[i]*=(1-EPS*K2[i]);normalizeState();}
  updateCapture();
}
reseedState();

function postReceipt(kind,detail={}){
  const receipt={
    type:"aetheris.receipt",
    module:"SYNTAX JACOB",
    status:"RECEIVED",
    evidence_class:"E2",
    timestamp:new Date().toISOString(),
    state_transition:{step:detail.step??null,capture,omega_c:47/125,copilot,throttle},
    certificate:{status:"PASS",evidence_class:"E2"},
    output_packet:{state_transition:{capture,omega_c:47/125,copilot,throttle}},
    kind_detail:kind,
    ...detail
  };
  try{window.parent?.postMessage(receipt,"*")}catch{}
}

async function emitWitness(){
  $("witnessStatus").textContent="EMITTING";
  try{
    const statevector=[...eState].map(x=>[x,0]);
    const r=await fetch(WITNESS,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({statevector,circuit:{instrument:"Syntax Jacob",operator:"Gamma=I-epsilon*K^2",epsilon:EPS}})});
    const j=await r.json();
    if(!r.ok||!j.ok)throw new Error(j.error||("HTTP "+r.status));
    const w=j.witness;
    $("witnessStatus").textContent="E47 "+(100*w.witness.e47_weight).toFixed(2)+"%";
    postReceipt("matrix-cube-witness",{digest:w.object?.state_hash,witness:w});
  }catch(e){
    $("witnessStatus").textContent="UNAVAILABLE";
    console.warn("Syntax Jacob witness",e);
  }
}

let live=null;
async function refreshEphemeris(){
  $("livePill").className="pill pending";$("livePill").textContent="JPL SYNC";
  try{
    const r=await fetch(EPHEMERIS,{cache:"no-store"});const j=await r.json();
    if(!r.ok||!j.ok)throw new Error(j.error||("HTTP "+r.status));
    live=j;
    $("earthRange").textContent=j.relative.earth_to_comet_au.toFixed(3);
    $("sunRange").textContent=j.comet.heliocentric_distance_au.toFixed(3);
    $("cometSpeed").textContent=j.comet.speed_km_s.toFixed(1);
    $("relativeSpeed").textContent=j.relative.relative_speed_km_s.toFixed(1);
    $("solution").textContent=String(j.sbdb.orbit?.orbit_id??"—");
    $("observations").textContent=String(j.sbdb.orbit?.n_obs_used??"—");
    $("epoch").textContent=String(j.sbdb.orbit?.epoch??"—");
    $("updated").textContent=new Date(j.generated_at).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit",second:"2-digit"});
    $("livePill").className="pill live";$("livePill").textContent="LIVE · JPL";
    const v=new THREE.Vector3(...j.relative.earth_to_comet_vector_au);
    if(v.lengthSq()>0){
      v.normalize();
      const dir=new THREE.Vector3(v.x,v.z,-v.y).normalize();
      relArrow.position.copy(earthObj.group.position);relArrow.setDirection(dir);relArrow.setLength(7,.35,.16);
    }
    const vel=new THREE.Vector3(...j.comet.velocity_au_per_day);
    if(vel.lengthSq()>0){
      vel.normalize();const d=new THREE.Vector3(vel.x,vel.z,-vel.y).normalize();
      tangentLine.geometry.setFromPoints([d.clone().multiplyScalar(-7),d.clone().multiplyScalar(7)]);
    }
  }catch(e){
    $("livePill").className="pill error";$("livePill").textContent="JPL OFFLINE";
    console.warn("Syntax Jacob ephemeris",e);
  }
}

async function detectGraphics(){
  try{
    const m=await import(GRAPHICS);
    const c=await m.detectCityGraphicsCapabilities();
    const p=m.getCityGraphicsProfile?.("SYNTAX JACOB");
    $("graphicsStatus").textContent=((c.tier||c.backend||"READY")+(p?" · PROFILE":"")).toUpperCase();
  }catch{
    $("graphicsStatus").textContent=(navigator.gpu?"WEBGPU":"WEBGL");
  }
}

const keys=new Set();let heading=0,verticalVel=0,surge=0;
addEventListener("keydown",e=>{if(["INPUT","TEXTAREA"].includes(document.activeElement?.tagName))return;keys.add(e.key.toLowerCase())});
addEventListener("keyup",e=>keys.delete(e.key.toLowerCase()));

function updateFlight(dt,t){
  if(keys.has("a"))heading+=dt*1.2;if(keys.has("d"))heading-=dt*1.2;
  if(keys.has("w"))surge+=dt*1.8;if(keys.has("s"))surge-=dt*1.8;
  if(keys.has("q"))verticalVel+=dt*.9;if(keys.has("e"))verticalVel-=dt*.9;
  surge*=Math.pow(.18,dt);verticalVel*=Math.pow(.12,dt);
  const forward=new THREE.Vector3(Math.cos(heading),0,Math.sin(heading));
  craft.group.position.addScaledVector(forward,surge*dt*(1+throttle*1.4));
  craft.group.position.y+=verticalVel*dt;

  if(copilot){
    const assist=.18+.82*capture;
    const a=t*.00022;
    const desired=cometObj.group.position.clone().add(new THREE.Vector3(Math.cos(a)*4.5,1.3+Math.sin(a*.72)*1.1,Math.sin(a)*4.5));
    craft.group.position.lerp(desired,Math.min(1,dt*(.15+assist*.72)));
    const look=cometObj.group.position.clone().sub(craft.group.position).normalize();
    heading=Math.atan2(look.z,look.x);
  }
  craft.group.rotation.y=-heading;
  craft.group.rotation.z=Math.sin(t*.0015)*.06*(1-capture);
  const pulse=1+.05*Math.sin(t*.004*(1+throttle));
  craft.shells.forEach((s,i)=>{s.rotation.z+=dt*(.18+i*.055);s.scale.multiplyScalar(pulse>1?1.00004:.99996)});
}

let pointer=null;
canvas.addEventListener("pointerdown",e=>{pointer={x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId)});
canvas.addEventListener("pointermove",e=>{
  if(!pointer)return;
  const dx=e.clientX-pointer.x,dy=e.clientY-pointer.y;pointer={x:e.clientX,y:e.clientY};
  orbit.theta-=dx*.0048;orbit.phi=Math.max(.18,Math.min(Math.PI-.18,orbit.phi+dy*.0048));
});
canvas.addEventListener("pointerup",()=>pointer=null);
canvas.addEventListener("pointercancel",()=>pointer=null);
canvas.addEventListener("wheel",e=>{orbit.radius=Math.max(6,Math.min(42,orbit.radius*Math.exp(e.deltaY*.001)))},{passive:true});

function focusObject(obj,radius=13){desiredTarget.copy(obj.position);orbit.radius=radius}
$("focusComet").onclick=()=>focusObject(cometObj.group,11);
$("focusEarth").onclick=()=>focusObject(earthObj.group,10);
$("focusCraft").onclick=()=>focusObject(craft.group,8);
$("copilotToggle").onclick=()=>{
  copilot=!copilot;$("copilotToggle").classList.toggle("on",copilot);$("copilotToggle").setAttribute("aria-pressed",String(copilot));
  $("copilotToggle").textContent=copilot?"COPILOT ON":"MANUAL";$("flightMode").textContent=copilot?"COHERENCE ASSIST":"MANUAL VECTOR";
  postReceipt("copilot-mode");
};
$("lockCoherence").onclick=()=>{contract(12);postReceipt("coherence-lock",{step:12});};
$("emitWitness").onclick=emitWitness;
$("reseed").onclick=()=>{reseedState();postReceipt("reseed")};
$("throttle").addEventListener("input",e=>{throttle=Number(e.target.value);$("throttleOut").textContent=throttle.toFixed(2)});
$("fullscreen").onclick=async()=>{try{if(!document.fullscreenElement)await document.documentElement.requestFullscreen();else await document.exitFullscreen()}catch{}};

function labelAt(id,obj,offsetY=0){
  const p=obj.position.clone();p.y+=offsetY;p.project(camera);
  const x=(p.x*.5+.5)*innerWidth,y=(-p.y*.5+.5)*innerHeight;
  const el=$(id);el.style.left=x+"px";el.style.top=y+"px";el.style.display=(p.z>-1&&p.z<1)?"block":"none";
}
function updateCamera(){
  target.lerp(desiredTarget,.06);
  const sp=Math.sin(orbit.phi),cp=Math.cos(orbit.phi);
  camera.position.set(target.x+orbit.radius*sp*Math.cos(orbit.theta),target.y+orbit.radius*cp,target.z+orbit.radius*sp*Math.sin(orbit.theta));
  camera.lookAt(target);
}
addEventListener("resize",()=>{
  camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
  renderer.setPixelRatio(Math.min(devicePixelRatio,2));renderer.setSize(innerWidth,innerHeight,false);
});

let last=performance.now(),frame=0;
function animate(now){
  requestAnimationFrame(animate);
  const dt=Math.min(.05,(now-last)/1000);last=now;frame++;
  earthObj.earth.rotation.y+=dt*.045;earthObj.clouds.rotation.y+=dt*.051;
  cometObj.nucleus.rotation.y+=dt*.16;cometObj.nucleus.rotation.x+=dt*.032;
  cometObj.coma.rotation.x+=dt*.014;cometObj.tail.rotation.x=Math.sin(now*.00007)*.06;
  if(copilot&&capture<.9995&&frame%4===0)contract(1);
  updateFlight(dt,now);updateCamera();
  if(frame%2===0){labelAt("earthLabel",earthObj.group,2.25);labelAt("cometLabel",cometObj.group,2.1);labelAt("craftLabel",craft.group,.9)}
  renderer.render(scene,camera);
}
updateCamera();requestAnimationFrame(animate);

Promise.allSettled([refreshEphemeris(),detectGraphics()]).finally(()=>{
  setTimeout(()=>$("loading").classList.add("hide"),450);
});
setInterval(refreshEphemeris,180000);
