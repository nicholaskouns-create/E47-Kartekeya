import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js';
import {MantaABRuntime,DT,MISSION_DURATION_S,REFERENCE} from './manta-model.js';

const $=s=>document.querySelector(s);
const runtime=new MantaABRuntime();
const canvas=$('#stage');
const renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance',alpha:false});
renderer.setPixelRatio(Math.min(2,devicePixelRatio||1));renderer.setSize(innerWidth,innerHeight);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.12;renderer.outputColorSpace=THREE.SRGBColorSpace;
const scene=new THREE.Scene();scene.background=new THREE.Color(0x020406);scene.fog=new THREE.FogExp2(0x020406,.0019);
const camera=new THREE.PerspectiveCamera(48,innerWidth/innerHeight,.1,4000);camera.position.set(34,16,42);
scene.add(new THREE.HemisphereLight(0x9fdcff,0x090607,1.65));const key=new THREE.DirectionalLight(0xffffff,5.5);key.position.set(20,35,18);key.castShadow=true;scene.add(key);const cyan=new THREE.PointLight(0x38e8ff,65,90,2);cyan.position.set(-12,3,-4);scene.add(cyan);
const floor=new THREE.Mesh(new THREE.PlaneGeometry(2400,2400,80,80),new THREE.MeshStandardMaterial({color:0x05090c,roughness:.92,metalness:.12,wireframe:true,transparent:true,opacity:.16}));floor.rotation.x=-Math.PI/2;floor.position.y=-7;scene.add(floor);
for(let i=0;i<700;i++){const g=new THREE.SphereGeometry(.025,4,4),m=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.25+Math.random()*.5});const p=new THREE.Mesh(g,m);p.position.set((Math.random()-.5)*700,20+Math.random()*240,(Math.random()-.5)*700);scene.add(p)}

function wingShape(morph,ghost=false){
  const span=11*(1+.42*morph.span),sweep=5.7+5.5*morph.sweep,tip=span/2;
  const shape=new THREE.Shape();shape.moveTo(3.6,0);shape.lineTo(1.1,1.8);shape.lineTo(-sweep,tip);shape.lineTo(-sweep-1.9,tip*.78);shape.lineTo(-2.2,1.05);shape.lineTo(-4.2,0);shape.lineTo(-2.2,-1.05);shape.lineTo(-sweep-1.9,-tip*.78);shape.lineTo(-sweep,-tip);shape.lineTo(1.1,-1.8);shape.closePath();
  const geo=new THREE.ExtrudeGeometry(shape,{depth:.35+1.2*(morph.thickness+.1),bevelEnabled:true,bevelSize:.15,bevelThickness:.12,bevelSegments:2});geo.rotateX(Math.PI/2);geo.rotateZ(-Math.PI/2);geo.translate(0,0,-.2);
  geo.computeVertexNormals();
  const mat=new THREE.MeshPhysicalMaterial({color:ghost?0x4e7682:0x0c1116,metalness:.88,roughness:.24,clearcoat:1,clearcoatRoughness:.14,transparent:ghost,opacity:ghost?.22:1,wireframe:ghost});
  return new THREE.Mesh(geo,mat);
}
function buildCraft(ghost=false){
  const root=new THREE.Group();root.userData.ghost=ghost;
  const body=new THREE.Mesh(new THREE.CapsuleGeometry(1.15,8.3,10,22),new THREE.MeshPhysicalMaterial({color:ghost?0x5e8790:0x111820,metalness:.9,roughness:.2,clearcoat:1,transparent:ghost,opacity:ghost?.16:1,wireframe:ghost}));body.rotation.z=Math.PI/2;body.scale.set(1,.72,.82);body.castShadow=!ghost;root.add(body);
  const nose=new THREE.Mesh(new THREE.ConeGeometry(1.15,3.6,24),body.material);nose.rotation.z=-Math.PI/2;nose.position.x=5.5;root.add(nose);
  const canopy=new THREE.Mesh(new THREE.SphereGeometry(1,24,14,0,Math.PI*2,0,Math.PI/2),new THREE.MeshPhysicalMaterial({color:0x18394a,metalness:.2,roughness:.08,transmission:.55,transparent:true,opacity:ghost?.12:.72}));canopy.scale.set(1.9,.62,.72);canopy.position.set(1.2,.65,0);root.add(canopy);
  const glow=new THREE.Mesh(new THREE.TorusGeometry(1.05,.08,10,42),new THREE.MeshBasicMaterial({color:ghost?0x7aaeb7:0x29e8ff,transparent:true,opacity:ghost?.18:.82}));glow.rotation.y=Math.PI/2;glow.position.x=-5;root.add(glow);
  root.userData.wing=wingShape({span:0,sweep:0,camber:0,twist:0,thickness:0,stiffness:.62},ghost);root.add(root.userData.wing);return root;
}
const manta=buildCraft(false),baseline=buildCraft(true);scene.add(manta,baseline);
baseline.position.z=-10;
function updateWing(root,morph){const old=root.userData.wing;root.remove(old);old.geometry.dispose();old.material.dispose();const next=wingShape(morph,root.userData.ghost);root.userData.wing=next;root.add(next);}

const pathMatM=new THREE.LineBasicMaterial({color:0x35ecff,transparent:true,opacity:.9});const pathMatB=new THREE.LineBasicMaterial({color:0x8b9ca0,transparent:true,opacity:.55});let lineM=null,lineB=null;
function pathLine(points,material,old){if(old){scene.remove(old);old.geometry.dispose()}const pts=points.map(p=>new THREE.Vector3(p.x*.012,p.y*.012,-p.z*.012));const geo=new THREE.BufferGeometry().setFromPoints(pts.length?pts:[new THREE.Vector3()]);const line=new THREE.Line(geo,material);scene.add(line);return line;}

let running=false,speedFactor=1,last=performance.now(),acc=0,lastWingUpdate=0,drag=false,px=0,py=0,yaw=.66,pitch=.23,dist=54;
function cameraOrbit(){camera.position.set(Math.cos(yaw)*Math.cos(pitch)*dist,Math.sin(pitch)*dist,Math.sin(yaw)*Math.cos(pitch)*dist);camera.lookAt(0,0,0)}cameraOrbit();
canvas.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture(e.pointerId)});canvas.addEventListener('pointermove',e=>{if(!drag)return;yaw-=(e.clientX-px)*.006;pitch=THREE.MathUtils.clamp(pitch+(e.clientY-py)*.004,-.1,1.05);px=e.clientX;py=e.clientY;cameraOrbit()});canvas.addEventListener('pointerup',()=>drag=false);canvas.addEventListener('wheel',e=>{dist=THREE.MathUtils.clamp(dist+e.deltaY*.03,24,110);cameraOrbit()},{passive:true});

function quatToThree(q){return new THREE.Quaternion(q[1],q[2],q[3],q[0])}
function fmt(v,d=2){return Number.isFinite(v)?v.toFixed(d):'—'}
function renderHud(s){
  $('#clock').textContent=`${fmt(s.t,1)} / ${MISSION_DURATION_S}s`;$('#phase').textContent=s.morph.phase;
  const m=s.morph,b=s.baseline;
  $('#cl').textContent=fmt(m.CL,3);$('#cd').textContent=fmt(m.CD,3);$('#cm').textContent=fmt(m.Cm,3);
  $('#mass').textContent=`${fmt(m.massKg,1)} kg`;$('#mdot').textContent=`${fmt(m.mdot,3)} kg/s`;
  $('#inertia').textContent=m.inertia.map(x=>Math.round(x).toLocaleString()).join(' / ');
  $('#energy').textContent=`${fmt(m.morphEnergyJ/3.6e6,3)} kWh`;$('#bounds').textContent=String(m.boundHits);
  $('#speedM').textContent=`${fmt(m.speed,1)} m/s`;$('#speedB').textContent=`${fmt(b.speed,1)} m/s`;$('#deltaSpeed').textContent=`${s.delta.speed>=0?'+':''}${fmt(s.delta.speed,1)}`;
  $('#altM').textContent=`${fmt(m.altitudeM,0)} m`;$('#altB').textContent=`${fmt(b.altitudeM,0)} m`;$('#deltaAlt').textContent=`${s.delta.altitude>=0?'+':''}${fmt(s.delta.altitude,0)}`;
  $('#fuelM').textContent=`${fmt(REFERENCE.fuelKg-m.fuelKg,1)} kg`;$('#fuelB').textContent=`${fmt(REFERENCE.fuelKg-b.fuelKg,1)} kg`;
  $('#peakAlpha').textContent=`${fmt(m.peakAlpha*180/Math.PI,1)}°`;$('#peakQ').textContent=`${fmt(m.peakQ/1000,1)} kPa`;
  const morph=m.morph;for(const k of ['span','sweep','camber','twist','thickness','stiffness']){$(`#v-${k}`).textContent=fmt(morph[k],2);$(`#b-${k}`).style.width=`${Math.max(0,Math.min(100,(morph[k]+.2)/1.2*100))}%`;}
  $('#status').textContent=s.done?'MISSION COMPLETE':running?'A/B RUNNING':'PAUSED';
  $('#status').classList.toggle('live',running&&!s.done);
}
function applyScene(s){
  const m=s.morph,b=s.baseline;manta.quaternion.copy(quatToThree(m.quaternion));baseline.quaternion.copy(quatToThree(b.quaternion));baseline.position.set((b.distanceM-m.distanceM)*.004,0,-10);
  if(s.t-lastWingUpdate>.12){updateWing(manta,m.morph);lastWingUpdate=s.t;}
  if(runtime.frame%24===0){lineM=pathLine(m.path,pathMatM,lineM);lineB=pathLine(b.path,pathMatB,lineB)}
}
function tick(now){const elapsed=Math.min(.05,(now-last)/1000);last=now;if(running&&!runtime.done){acc+=elapsed*speedFactor;let n=0;while(acc>=DT&&n<40){const s=runtime.step();acc-=DT;n++;applyScene(s);renderHud(s)}if(runtime.done)running=false}renderer.render(scene,camera);requestAnimationFrame(tick)}requestAnimationFrame(tick);
function reset(){running=false;runtime.reset();acc=0;lastWingUpdate=0;if(lineM){scene.remove(lineM);lineM.geometry.dispose();lineM=null}if(lineB){scene.remove(lineB);lineB.geometry.dispose();lineB=null}updateWing(manta,runtime.snapshot().morph.morph);renderHud(runtime.snapshot());}
$('#run').onclick=()=>{if(runtime.done)reset();running=true};$('#pause').onclick=()=>running=false;$('#reset').onclick=reset;$('#fast').onclick=()=>{speedFactor=speedFactor===1?4:speedFactor===4?12:1;$('#fast').textContent=`${speedFactor}×`};
$('#export').onclick=()=>{const blob=new Blob([JSON.stringify(runtime.exportReceipt(),null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='MANTA-AB-6DOF-receipt.json';a.click();URL.revokeObjectURL(a.href)};
$('#finish').onclick=()=>{running=false;runtime.runToEnd();const s=runtime.snapshot();applyScene(s);renderHud(s)};
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight)});reset();
