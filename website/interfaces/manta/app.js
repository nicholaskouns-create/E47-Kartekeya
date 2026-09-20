import * as THREE from '../../vendor/three.module.js';
import {MantaABRuntime,DT,MISSION_DURATION_S,REFERENCE} from './manta-model.js';

const $=s=>document.querySelector(s);
const runtime=new MantaABRuntime();
const canvas=$('#stage');

const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance'});
renderer.setPixelRatio(Math.min(2,devicePixelRatio||1));
renderer.setSize(innerWidth,innerHeight);
renderer.shadowMap.enabled=true;
renderer.shadowMap.type=THREE.PCFSoftShadowMap;
renderer.toneMapping=THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure=1.28;
renderer.outputColorSpace=THREE.SRGBColorSpace;

const scene=new THREE.Scene();
scene.background=new THREE.Color(0x8fc7e6);
scene.fog=new THREE.Fog(0xa9d6eb,180,900);

const camera=new THREE.PerspectiveCamera(52,innerWidth/innerHeight,.1,5000);
camera.position.set(-34,15,26);

scene.add(new THREE.HemisphereLight(0xeaf8ff,0x80684e,3.4));
const sun=new THREE.DirectionalLight(0xfff3d6,6.2);
sun.position.set(-90,150,70);
sun.castShadow=true;
sun.shadow.mapSize.set(2048,2048);
sun.shadow.camera.left=-160;sun.shadow.camera.right=160;sun.shadow.camera.top=160;sun.shadow.camera.bottom=-160;
scene.add(sun);

const ground=new THREE.Mesh(
  new THREE.PlaneGeometry(5000,5000,1,1),
  new THREE.MeshStandardMaterial({color:0x947a59,roughness:1,metalness:0})
);
ground.rotation.x=-Math.PI/2;
ground.position.y=-14;
ground.receiveShadow=true;
scene.add(ground);

const grid=new THREE.GridHelper(1600,80,0xd7c29d,0x9f8968);
grid.position.y=-13.92;
grid.material.transparent=true;
grid.material.opacity=.24;
scene.add(grid);

const runway=new THREE.Mesh(
  new THREE.PlaneGeometry(48,900),
  new THREE.MeshStandardMaterial({color:0x33383b,roughness:.92})
);
runway.rotation.x=-Math.PI/2;
runway.position.set(0,-13.86,-170);
scene.add(runway);
for(let z=-590;z<260;z+=38){
  const stripe=new THREE.Mesh(new THREE.PlaneGeometry(1.2,18),new THREE.MeshBasicMaterial({color:0xf4f1df}));
  stripe.rotation.x=-Math.PI/2;stripe.position.set(0,-13.82,z);scene.add(stripe);
}

const mountainMat=new THREE.MeshStandardMaterial({color:0x765f4e,roughness:1});
for(let i=0;i<32;i++){
  const h=38+Math.random()*85,r=28+Math.random()*60;
  const m=new THREE.Mesh(new THREE.ConeGeometry(r,h,5),mountainMat);
  const side=i%2?1:-1;
  m.position.set(side*(160+Math.random()*520),-14+h/2,-180-Math.random()*900);
  m.rotation.y=Math.random()*Math.PI;
  m.receiveShadow=true;scene.add(m);
}

const sunDisc=new THREE.Mesh(new THREE.SphereGeometry(11,24,24),new THREE.MeshBasicMaterial({color:0xfff3c7}));
sunDisc.position.set(-240,210,-780);scene.add(sunDisc);

function wingShape(morph,ghost=false){
  // Visual exaggeration only. The dynamics still use the exact modeled morph values.
  const span=12.4*(1+1.25*morph.span);
  const sweep=5.5+11.5*morph.sweep;
  const tip=Math.max(3.6,span/2);
  const rootCamber=1.45+3.2*morph.camber;
  const tipTwist=1.0+2.7*morph.twist;
  const shape=new THREE.Shape();
  shape.moveTo(4.2,0);
  shape.lineTo(1.3,rootCamber);
  shape.lineTo(-sweep,tip);
  shape.lineTo(-sweep-2.2,tip*.78+tipTwist);
  shape.lineTo(-2.2,1.1);
  shape.lineTo(-4.5,0);
  shape.lineTo(-2.2,-1.1);
  shape.lineTo(-sweep-2.2,-tip*.78-tipTwist);
  shape.lineTo(-sweep,-tip);
  shape.lineTo(1.3,-rootCamber);
  shape.closePath();

  const geo=new THREE.ExtrudeGeometry(shape,{
    depth:.48+2.2*(morph.thickness+.1),
    bevelEnabled:true,bevelSize:.20,bevelThickness:.16,bevelSegments:3
  });
  geo.rotateX(Math.PI/2);
  geo.rotateZ(-Math.PI/2);
  geo.translate(0,0,-.25);
  geo.computeVertexNormals();

  const mat=ghost
    ? new THREE.MeshPhysicalMaterial({color:0xffb85c,emissive:0x5c2600,emissiveIntensity:.42,metalness:.25,roughness:.28,transparent:true,opacity:.34,wireframe:true})
    : new THREE.MeshPhysicalMaterial({color:0x8ea8b7,metalness:.78,roughness:.18,clearcoat:1,clearcoatRoughness:.08,envMapIntensity:1.4});
  const mesh=new THREE.Mesh(geo,mat);
  mesh.castShadow=!ghost;
  return mesh;
}

function buildCraft(ghost=false){
  const root=new THREE.Group();root.userData.ghost=ghost;
  const bodyMat=ghost
    ? new THREE.MeshPhysicalMaterial({color:0xffb85c,emissive:0x713700,emissiveIntensity:.35,transparent:true,opacity:.28,wireframe:true})
    : new THREE.MeshPhysicalMaterial({color:0x50616d,metalness:.82,roughness:.15,clearcoat:1,clearcoatRoughness:.08});

  const body=new THREE.Mesh(new THREE.CapsuleGeometry(1.35,9.4,14,28),bodyMat);
  body.rotation.z=Math.PI/2;
  body.scale.set(1,.72,.88);
  body.castShadow=!ghost;
  root.add(body);

  const nose=new THREE.Mesh(new THREE.ConeGeometry(1.35,4.5,28),bodyMat);
  nose.rotation.z=-Math.PI/2;
  nose.position.x=6.7;
  root.add(nose);

  const canopy=new THREE.Mesh(
    new THREE.SphereGeometry(1,30,18,0,Math.PI*2,0,Math.PI/2),
    new THREE.MeshPhysicalMaterial({color:0x55a7d4,metalness:.05,roughness:.06,transmission:.50,transparent:true,opacity:ghost?.14:.74})
  );
  canopy.scale.set(2.05,.68,.82);
  canopy.position.set(1.5,.78,0);
  root.add(canopy);

  const engineGlow=new THREE.Mesh(
    new THREE.TorusGeometry(1.18,.11,12,48),
    new THREE.MeshBasicMaterial({color:ghost?0xffb85c:0x42f1ff,transparent:true,opacity:ghost?.30:1})
  );
  engineGlow.rotation.y=Math.PI/2;
  engineGlow.position.x=-5.7;
  root.add(engineGlow);

  root.userData.wing=wingShape({span:0,sweep:0,camber:0,twist:0,thickness:0,stiffness:.62},ghost);
  root.add(root.userData.wing);
  return root;
}

const manta=buildCraft(false);
const baseline=buildCraft(true);
scene.add(manta,baseline);

function updateWing(root,morph){
  const old=root.userData.wing;
  root.remove(old);
  old.geometry.dispose();
  old.material.dispose();
  const next=wingShape(morph,root.userData.ghost);
  root.userData.wing=next;
  root.add(next);
}

const pathMatM=new THREE.LineBasicMaterial({color:0x00e8ff,transparent:true,opacity:.95});
const pathMatB=new THREE.LineBasicMaterial({color:0xffb85c,transparent:true,opacity:.72});
let lineM=null,lineB=null;

const PATH_SCALE=.028;
const ALT_SCALE=.020;
function pathPoint(p,offsetZ=0){
  return new THREE.Vector3(p.x*PATH_SCALE,p.y*ALT_SCALE-2,-p.z*PATH_SCALE+offsetZ);
}
function pathLine(points,material,old,offsetZ=0){
  if(old){scene.remove(old);old.geometry.dispose()}
  const pts=points.map(p=>pathPoint(p,offsetZ));
  const geo=new THREE.BufferGeometry().setFromPoints(pts.length?pts:[new THREE.Vector3()]);
  const line=new THREE.Line(geo,material);
  scene.add(line);
  return line;
}

let running=true;
let speedFactor=1;
let last=performance.now(),acc=0,lastWingUpdate=-1;
let cameraMode='CHASE';
let dragging=false,px=0,py=0,yaw=.72,pitch=.25,dist=58;
const camTarget=new THREE.Vector3();

function quatToThree(q){return new THREE.Quaternion(q[1],q[2],q[3],q[0])}
function fmt(v,d=2){return Number.isFinite(v)?v.toFixed(d):'—'}

function setCraftWorld(root,frame,lateral=0){
  const p=frame.path.length?frame.path[frame.path.length-1]:{x:0,y:0,z:0};
  root.position.copy(pathPoint(p,lateral));
  root.quaternion.copy(quatToThree(frame.quaternion));
}

function updateCamera(){
  if(cameraMode==='CHASE'&&!dragging){
    const localOffset=new THREE.Vector3(-34,14,22).applyQuaternion(manta.quaternion);
    const desired=manta.position.clone().add(localOffset);
    camera.position.lerp(desired,.075);
    camTarget.lerp(manta.position.clone().add(new THREE.Vector3(6,0,0).applyQuaternion(manta.quaternion)),.10);
    camera.lookAt(camTarget);
  }else{
    const center=manta.position;
    camera.position.set(
      center.x+Math.cos(yaw)*Math.cos(pitch)*dist,
      center.y+Math.sin(pitch)*dist,
      center.z+Math.sin(yaw)*Math.cos(pitch)*dist
    );
    camera.lookAt(center);
  }
}

canvas.addEventListener('pointerdown',e=>{
  dragging=true;cameraMode='ORBIT';px=e.clientX;py=e.clientY;canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointermove',e=>{
  if(!dragging)return;
  yaw-=(e.clientX-px)*.006;
  pitch=THREE.MathUtils.clamp(pitch+(e.clientY-py)*.004,-.1,1.05);
  px=e.clientX;py=e.clientY;
});
canvas.addEventListener('pointerup',()=>dragging=false);
canvas.addEventListener('wheel',e=>{
  cameraMode='ORBIT';
  dist=THREE.MathUtils.clamp(dist+e.deltaY*.03,26,120);
},{passive:true});

function renderHud(s){
  $('#clock').textContent=`${fmt(s.t,1)} / ${MISSION_DURATION_S}s`;
  $('#phase').textContent=s.morph.phase;
  const m=s.morph,b=s.baseline;
  $('#cl').textContent=fmt(m.CL,3);$('#cd').textContent=fmt(m.CD,3);$('#cm').textContent=fmt(m.Cm,3);
  $('#mass').textContent=`${fmt(m.massKg,1)} kg`;$('#mdot').textContent=`${fmt(m.mdot,3)} kg/s`;
  $('#inertia').textContent=m.inertia.map(x=>Math.round(x).toLocaleString()).join(' / ');
  $('#energy').textContent=`${fmt(m.morphEnergyJ/3.6e6,3)} kWh`;$('#bounds').textContent=String(m.boundHits);
  $('#speedM').textContent=`${fmt(m.speed,1)} m/s`;$('#speedB').textContent=`${fmt(b.speed,1)} m/s`;$('#deltaSpeed').textContent=`${s.delta.speed>=0?'+':''}${fmt(s.delta.speed,1)}`;
  $('#altM').textContent=`${fmt(m.altitudeM,0)} m`;$('#altB').textContent=`${fmt(b.altitudeM,0)} m`;$('#deltaAlt').textContent=`${s.delta.altitude>=0?'+':''}${fmt(s.delta.altitude,0)}`;
  $('#fuelM').textContent=`${fmt(REFERENCE.fuelKg-m.fuelKg,1)} kg`;$('#fuelB').textContent=`${fmt(REFERENCE.fuelKg-b.fuelKg,1)} kg`;
  $('#peakAlpha').textContent=`${fmt(m.peakAlpha*180/Math.PI,1)}°`;$('#peakQ').textContent=`${fmt(m.peakQ/1000,1)} kPa`;
  for(const k of ['span','sweep','camber','twist','thickness','stiffness']){
    const val=m.morph[k];
    $(`#v-${k}`).textContent=fmt(val,2);
    $(`#b-${k}`).style.width=`${Math.max(0,Math.min(100,(val+.2)/1.2*100))}%`;
  }
  $('#status').textContent=s.done?'MISSION COMPLETE':running?'FLYING':'PAUSED';
  $('#status').classList.toggle('live',running&&!s.done);
}

function applyScene(s){
  const m=s.morph,b=s.baseline;
  setCraftWorld(manta,m,0);
  setCraftWorld(baseline,b,-9);

  if(s.t-lastWingUpdate>.08){
    updateWing(manta,m.morph);
    lastWingUpdate=s.t;
  }
  if(runtime.frame%18===0){
    lineM=pathLine(m.path,pathMatM,lineM,0);
    lineB=pathLine(b.path,pathMatB,lineB,-9);
  }
}

function tick(now){
  const elapsed=Math.min(.05,(now-last)/1000);last=now;
  if(running&&!runtime.done){
    acc+=elapsed*speedFactor;
    let n=0;
    while(acc>=DT&&n<60){
      const s=runtime.step();
      acc-=DT;n++;
      applyScene(s);renderHud(s);
    }
    if(runtime.done)running=false;
  }
  updateCamera();
  renderer.render(scene,camera);
  requestAnimationFrame(tick);
}
requestAnimationFrame(tick);

function reset(autoStart=true){
  runtime.reset();acc=0;lastWingUpdate=-1;
  if(lineM){scene.remove(lineM);lineM.geometry.dispose();lineM=null}
  if(lineB){scene.remove(lineB);lineB.geometry.dispose();lineB=null}
  const s=runtime.snapshot();
  updateWing(manta,s.morph.morph);
  setCraftWorld(manta,s.morph,0);setCraftWorld(baseline,s.baseline,-9);
  renderHud(s);
  running=autoStart;
  cameraMode='CHASE';
  camTarget.copy(manta.position);
}
$('#run').onclick=()=>{if(runtime.done)reset(false);running=true};
$('#pause').onclick=()=>running=false;
$('#reset').onclick=()=>reset(true);
$('#fast').onclick=()=>{
  speedFactor=speedFactor===1?4:speedFactor===4?12:1;
  $('#fast').textContent=`${speedFactor}×`;
};
$('#finish').onclick=()=>{
  running=false;
  runtime.runToEnd();
  const s=runtime.snapshot();
  applyScene(s);renderHud(s);cameraMode='ORBIT';
};
$('#export').onclick=()=>{
  const blob=new Blob([JSON.stringify(runtime.exportReceipt(),null,2)],{type:'application/json'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);a.download='MANTA-AB-6DOF-receipt.json';a.click();
  URL.revokeObjectURL(a.href);
};
const camBtn=$('#cameraToggle');
if(camBtn)camBtn.onclick=()=>{
  cameraMode=cameraMode==='CHASE'?'ORBIT':'CHASE';
  camBtn.textContent=cameraMode;
};

addEventListener('resize',()=>{
  camera.aspect=innerWidth/innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth,innerHeight);
});

reset(true);
