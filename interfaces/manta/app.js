import * as THREE from '../../vendor/three.module.js';
import {MantaABRuntime,DT,MISSION_DURATION_S} from './manta-model.js';

const $=s=>document.querySelector(s);
const canvas=$('#stage');
const runtime=new MantaABRuntime();

let renderer,scene,camera,manta,baselineGhost,terrain,city,clouds,trailL,trailR;
let running=true,speedFactor=1,last=performance.now(),acc=0,viewMode=0,showBaseline=false;
let drag=false,px=0,py=0,orbitYaw=.7,orbitPitch=.28,orbitDistance=42;
let lastMorphKey='',worldOffsetZ=0;

const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;

function boot(){
  try{
    renderer=new THREE.WebGLRenderer({canvas,antialias:true,powerPreference:'high-performance',alpha:false});
    renderer.setPixelRatio(Math.min(devicePixelRatio||1,matchMedia('(max-width:760px)').matches?1.5:2));
    renderer.setSize(innerWidth,innerHeight,false);
    renderer.outputColorSpace=THREE.SRGBColorSpace;
    renderer.toneMapping=THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure=1.22;
    renderer.shadowMap.enabled=true;
    renderer.shadowMap.type=THREE.PCFSoftShadowMap;

    scene=new THREE.Scene();
    scene.background=new THREE.Color(0xbfe8fb);
    scene.fog=new THREE.Fog(0xd8edf3,220,1350);

    camera=new THREE.PerspectiveCamera(52,innerWidth/innerHeight,.1,5000);
    camera.position.set(-28,14,22);

    scene.add(new THREE.HemisphereLight(0xeaf8ff,0x9b805d,3.2));
    const sun=new THREE.DirectionalLight(0xfff4d8,5.8);
    sun.position.set(-180,260,130);sun.castShadow=true;
    sun.shadow.mapSize.set(2048,2048);sun.shadow.camera.left=-120;sun.shadow.camera.right=120;sun.shadow.camera.top=120;sun.shadow.camera.bottom=-120;
    scene.add(sun);

    makeSky();
    terrain=makeTerrain();
    city=makeCity();
    clouds=makeCloudLayer();

    manta=makeManta(false);
    baselineGhost=makeManta(true);
    baselineGhost.visible=false;
    scene.add(manta,baselineGhost);

    trailL=makeTrail(0x34dff0);trailR=makeTrail(0x34dff0);
    scene.add(trailL.line,trailR.line);

    installInput();
    $('#fallback').hidden=true;
    $('#status').textContent='FLYING';
    renderSnapshot(runtime.snapshot(),true);
    requestAnimationFrame(frame);
  }catch(error){
    console.error(error);
    $('#fallback').hidden=true;
    $('#fault').hidden=false;
    $('#fault').textContent='MANTA renderer fault: '+String(error?.message||error);
    $('#status').textContent='FAULT';
  }
}

function makeSky(){
  const geo=new THREE.SphereGeometry(2200,32,20);
  const mat=new THREE.ShaderMaterial({
    side:THREE.BackSide,depthWrite:false,
    uniforms:{
      zenith:{value:new THREE.Color(0x67bce8)},
      horizon:{value:new THREE.Color(0xe8f7fb)},
      low:{value:new THREE.Color(0xf1d6aa)}
    },
    vertexShader:'varying vec3 vP; void main(){vP=(modelMatrix*vec4(position,1.0)).xyz; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}',
    fragmentShader:'varying vec3 vP; uniform vec3 zenith; uniform vec3 horizon; uniform vec3 low; void main(){float h=normalize(vP).y*.5+.5; vec3 c=mix(low,horizon,smoothstep(.16,.50,h)); c=mix(c,zenith,smoothstep(.52,.96,h)); gl_FragColor=vec4(c,1.0);}'
  });
  scene.add(new THREE.Mesh(geo,mat));
  const disc=new THREE.Mesh(new THREE.SphereGeometry(15,20,20),new THREE.MeshBasicMaterial({color:0xfff7d2}));
  disc.position.set(-430,390,-900);scene.add(disc);
}

function makeTerrain(){
  const size=2200,seg=96,geo=new THREE.PlaneGeometry(size,size,seg,seg);
  geo.rotateX(-Math.PI/2);
  const p=geo.attributes.position;
  for(let i=0;i<p.count;i++){
    const x=p.getX(i),z=p.getZ(i);
    const ridge=18*Math.sin(x*.012)+14*Math.sin(z*.009)+7*Math.sin((x+z)*.021);
    const basin=-26*Math.exp(-(x*x+z*z)/380000);
    p.setY(i,-34+ridge+basin);
  }
  p.needsUpdate=true;geo.computeVertexNormals();
  const mat=new THREE.MeshStandardMaterial({color:0xc5a678,roughness:.97,metalness:0});
  const mesh=new THREE.Mesh(geo,mat);mesh.receiveShadow=true;scene.add(mesh);
  const runway=new THREE.Mesh(new THREE.PlaneGeometry(38,760),new THREE.MeshStandardMaterial({color:0x656e71,roughness:.9}));
  runway.rotation.x=-Math.PI/2;runway.position.set(0,-20,-250);scene.add(runway);
  for(let z=-600;z<130;z+=38){
    const mark=new THREE.Mesh(new THREE.PlaneGeometry(1.3,16),new THREE.MeshBasicMaterial({color:0xf7f4df}));
    mark.rotation.x=-Math.PI/2;mark.position.set(0,-19.95,z);scene.add(mark);
  }
  return mesh;
}

function makeCity(){
  const group=new THREE.Group(),geo=new THREE.BoxGeometry(1,1,1);
  const mat=new THREE.MeshStandardMaterial({color:0xa6a5a0,roughness:.9,metalness:.05});
  const count=150,inst=new THREE.InstancedMesh(geo,mat,count),o=new THREE.Object3D();
  for(let i=0;i<count;i++){
    const side=i%2?1:-1,x=side*(120+Math.random()*420),z=-520+Math.random()*900;
    const w=12+Math.random()*35,d=12+Math.random()*30,h=8+Math.pow(Math.random(),2)*85;
    o.position.set(x,-28+h/2,z);o.scale.set(w,h,d);o.rotation.y=Math.round(Math.random()*4)*Math.PI/2;o.updateMatrix();inst.setMatrixAt(i,o.matrix);
  }
  inst.castShadow=true;inst.receiveShadow=true;group.add(inst);scene.add(group);return group;
}

function makeCloudLayer(){
  const group=new THREE.Group();
  const texCanvas=document.createElement('canvas');texCanvas.width=texCanvas.height=256;
  const ctx=texCanvas.getContext('2d'),g=ctx.createRadialGradient(128,128,12,128,128,120);
  g.addColorStop(0,'rgba(255,255,255,.88)');g.addColorStop(.48,'rgba(255,255,255,.44)');g.addColorStop(1,'rgba(255,255,255,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,256,256);
  const tex=new THREE.CanvasTexture(texCanvas);
  for(let i=0;i<28;i++){
    const s=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,opacity:.23,depthWrite:false,color:0xffffff}));
    s.position.set((Math.random()-.5)*1300,90+Math.random()*180,(Math.random()-.5)*1400-220);
    const w=120+Math.random()*260;s.scale.set(w,w*.26,1);group.add(s);
  }
  scene.add(group);return group;
}

function pbr(color,extra={}){
  return new THREE.MeshPhysicalMaterial({
    color,metalness:.72,roughness:.18,clearcoat:1,clearcoatRoughness:.07,
    ...extra
  });
}

function planform(points,mat,depth=.28){
  const s=new THREE.Shape();s.moveTo(points[0][0],points[0][1]);
  for(let i=1;i<points.length;i++)s.lineTo(points[i][0],points[i][1]);s.closePath();
  const g=new THREE.ExtrudeGeometry(s,{depth,bevelEnabled:true,bevelSize:.10,bevelThickness:.08,bevelSegments:2});
  g.rotateX(Math.PI/2);
  return new THREE.Mesh(g,mat);
}

function makeManta(ghost=false){
  const root=new THREE.Group();
  const silver=ghost
    ?new THREE.MeshBasicMaterial({color:0xf09a4a,wireframe:true,transparent:true,opacity:.45})
    :pbr(0xd2dde2);
  const dark=ghost?silver:pbr(0x5f737d,{roughness:.24});
  const glass=ghost?silver:new THREE.MeshPhysicalMaterial({color:0x65b7d5,roughness:.04,metalness:.05,transparent:true,opacity:.72,transmission:.18,clearcoat:1});

  const center=planform([[6.2,0],[2.8,2.3],[-1.2,2.6],[-5.7,1.4],[-7.4,0],[-5.7,-1.4],[-1.2,-2.6],[2.8,-2.3]],silver,.42);
  center.rotation.z=-Math.PI/2;center.castShadow=!ghost;root.add(center);

  const body=new THREE.Mesh(new THREE.CapsuleGeometry(1.15,9.2,12,24),dark);
  body.rotation.z=Math.PI/2;body.scale.set(1,.72,.86);body.castShadow=!ghost;root.add(body);
  const nose=new THREE.Mesh(new THREE.ConeGeometry(1.18,3.8,24),dark);nose.rotation.z=-Math.PI/2;nose.position.x=6.15;root.add(nose);
  const canopy=new THREE.Mesh(new THREE.SphereGeometry(1,28,16,0,Math.PI*2,0,Math.PI/2),glass);
  canopy.scale.set(2.1,.70,.82);canopy.position.set(1.7,.72,0);root.add(canopy);

  const wingMat=silver;
  const leftPivot=new THREE.Group(),rightPivot=new THREE.Group();
  const wingShape=[[1.1,.15],[-.5,1.7],[-7.7,6.6],[-8.8,5.4],[-5.1,1.2],[-2.5,.1]];
  const wingL=planform(wingShape,wingMat,.34);wingL.rotation.z=-Math.PI/2;wingL.position.set(-1.3,0,0);leftPivot.add(wingL);
  const mirror=wingShape.map(([x,y])=>[x,-y]);
  const wingR=planform(mirror,wingMat,.34);wingR.rotation.z=-Math.PI/2;wingR.position.set(-1.3,0,0);rightPivot.add(wingR);
  root.add(leftPivot,rightPivot);

  const controlMat=ghost?silver:pbr(0x83959c,{roughness:.26});
  const elevL=planform([[-2.2,.2],[-5.5,1.0],[-6.6,2.1],[-3.0,1.1]],controlMat,.18);elevL.rotation.z=-Math.PI/2;elevL.position.set(-1.4,.04,0);root.add(elevL);
  const elevR=elevL.clone();elevR.scale.z=-1;root.add(elevR);

  const engineMat=ghost?silver:pbr(0x3b4c55,{metalness:.9,roughness:.22});
  const engineGlowMat=new THREE.MeshBasicMaterial({color:ghost?0xf09a4a:0x4de8ff,transparent:true,opacity:ghost?.35:.95});
  const engines=[];
  for(const z of [-2.5,2.5]){
    const nac=new THREE.Mesh(new THREE.CylinderGeometry(.66,.82,3.4,24),engineMat);nac.rotation.z=Math.PI/2;nac.position.set(-4.7,-.18,z);root.add(nac);
    const ring=new THREE.Mesh(new THREE.TorusGeometry(.68,.10,10,28),engineGlowMat);ring.rotation.y=Math.PI/2;ring.position.set(-6.45,-.18,z);root.add(ring);
    const flame=new THREE.Mesh(new THREE.ConeGeometry(.48,3.0,18,1,true),engineGlowMat);flame.rotation.z=Math.PI/2;flame.position.set(-7.85,-.18,z);root.add(flame);engines.push(flame);
  }

  const edgeMat=new THREE.MeshBasicMaterial({color:ghost?0xf09a4a:0x66efff,transparent:true,opacity:ghost?.35:.80});
  for(const z of [-5.8,5.8]){
    const strip=new THREE.Mesh(new THREE.BoxGeometry(5.8,.035,.045),edgeMat);strip.position.set(-1.6,.20,z);strip.rotation.y=z<0?.46:-.46;root.add(strip);
  }

  root.userData={leftPivot,rightPivot,elevL,elevR,engines,ghost};
  root.scale.setScalar(1.18);
  return root;
}

function updateMorph(root,m){
  const u=root.userData;
  const spanScale=1+1.20*m.span;
  u.leftPivot.scale.z=spanScale;u.rightPivot.scale.z=spanScale;
  u.leftPivot.rotation.y=-.62*m.sweep;u.rightPivot.rotation.y=.62*m.sweep;
  u.leftPivot.rotation.x=.55*m.twist;u.rightPivot.rotation.x=-.55*m.twist;
  u.leftPivot.position.y=.55*m.camber;u.rightPivot.position.y=.55*m.camber;
  u.elevL.rotation.x=-1.1*m.camber-.8*m.twist;u.elevR.rotation.x=-1.1*m.camber+.8*m.twist;
  root.scale.y=1+.7*m.thickness;
}

function makeTrail(color){
  const max=140,positions=new Float32Array(max*3),geo=new THREE.BufferGeometry();
  geo.setAttribute('position',new THREE.BufferAttribute(positions,3));
  const line=new THREE.Line(geo,new THREE.LineBasicMaterial({color,transparent:true,opacity:.38}));
  const history=[];
  return {line,history,positions,max};
}

function updateTrail(trail,pos){
  trail.history.unshift(pos.clone());if(trail.history.length>trail.max)trail.history.length=trail.max;
  for(let i=0;i<trail.max;i++){
    const p=trail.history[i]||trail.history[trail.history.length-1]||pos,j=i*3;
    trail.positions[j]=p.x;trail.positions[j+1]=p.y;trail.positions[j+2]=p.z;
  }
  trail.line.geometry.attributes.position.needsUpdate=true;
}

function q3(q){return new THREE.Quaternion(q[1],q[2],q[3],q[0])}

function craftPosition(frame){
  const p=frame.path.length?frame.path[frame.path.length-1]:{x:0,y:0,z:0};
  return new THREE.Vector3(p.x*.013,24+p.y*.010,-p.z*.013);
}

function renderSnapshot(s,force=false){
  const m=s.morph,b=s.baseline;
  const mp=craftPosition(m),bp=craftPosition(b);
  manta.position.lerp(mp,force?1:.32);manta.quaternion.slerp(q3(m.quaternion),force?1:.18);
  baselineGhost.position.lerp(bp,force?1:.25);baselineGhost.quaternion.slerp(q3(b.quaternion),force?1:.16);

  updateMorph(manta,m.morph);updateMorph(baselineGhost,{span:0,sweep:0,camber:0,twist:0,thickness:0,stiffness:.62});
  baselineGhost.visible=showBaseline;

  const left=manta.localToWorld(new THREE.Vector3(-4,0,-5.4));
  const right=manta.localToWorld(new THREE.Vector3(-4,0,5.4));
  if(runtime.frame%3===0){updateTrail(trailL,left);updateTrail(trailR,right)}

  const morphMagnitude=Math.min(1,Math.abs(m.morph.span)*2.4+Math.abs(m.morph.sweep)*1.7+Math.abs(m.morph.camber)*2.0+Math.abs(m.morph.twist)*1.8+Math.abs(m.morph.thickness)*2.0);
  $('#morphMeter').style.setProperty('--morph',Math.round(12+88*morphMagnitude)+'%');
  $('#morphText').textContent=morphMagnitude<.05?'NEUTRAL':m.phase;
  $('#status').textContent=s.done?'MISSION COMPLETE':running?'FLYING':'PAUSED';
  $('#clock').textContent=s.t.toFixed(1)+' s';
  $('#phase').textContent=m.phase;
  $('#speed').textContent=m.speed.toFixed(0)+' m/s';
  $('#altitude').textContent=Math.round(m.altitudeM).toLocaleString()+' m';
  $('#speedDelta').textContent='Δ '+(s.delta.speed>=0?'+':'')+s.delta.speed.toFixed(0);
  $('#altDelta').textContent='Δ '+(s.delta.altitude>=0?'+':'')+Math.round(s.delta.altitude)+' m';
  $('#cl').textContent=m.CL.toFixed(3);$('#cd').textContent=m.CD.toFixed(3);$('#cm').textContent=m.Cm.toFixed(3);
  $('#mass').textContent=Math.round(m.massKg).toLocaleString()+' kg';
  $('#energy').textContent=(m.morphEnergyJ/3.6e6).toFixed(3)+' kWh';
  $('#qbar').textContent=(m.peakQ/1000).toFixed(1)+' kPa';
}

const camPos=new THREE.Vector3(),camTarget=new THREE.Vector3();
function updateCamera(dt){
  if(!manta)return;
  const q=manta.quaternion,forward=new THREE.Vector3(1,0,0).applyQuaternion(q).normalize();
  const up=new THREE.Vector3(0,1,0).applyQuaternion(q).normalize();
  const right=new THREE.Vector3(0,0,1).applyQuaternion(q).normalize();
  let desired=new THREE.Vector3(),target=manta.position.clone().addScaledVector(forward,18);

  if(viewMode===0){
    desired.copy(manta.position).addScaledVector(forward,-31).addScaledVector(up,9.5).addScaledVector(right,10);
  }else if(viewMode===1){
    desired.copy(manta.position).addScaledVector(right,-28).addScaledVector(up,7).addScaledVector(forward,-2);
    target.copy(manta.position).addScaledVector(forward,10);
  }else{
    desired.set(
      manta.position.x+Math.cos(orbitYaw)*Math.cos(orbitPitch)*orbitDistance,
      manta.position.y+Math.sin(orbitPitch)*orbitDistance,
      manta.position.z+Math.sin(orbitYaw)*Math.cos(orbitPitch)*orbitDistance
    );
    target.copy(manta.position);
  }
  camPos.lerp(desired,1-Math.exp(-5.8*dt));camTarget.lerp(target,1-Math.exp(-7.5*dt));
  camera.position.copy(camPos);camera.up.lerp(new THREE.Vector3(0,1,0),.15).normalize();camera.lookAt(camTarget);
  const targetFov=viewMode===0?50:viewMode===1?47:52;camera.fov=lerp(camera.fov,targetFov,1-Math.exp(-4*dt));camera.updateProjectionMatrix();
}

function moveWorld(){
  const z=manta?.position?.z||0;
  const target=Math.floor(z/500)*500;
  if(target!==worldOffsetZ){worldOffsetZ=target;city.position.z=target;clouds.position.z=target;terrain.position.z=target}
  clouds.position.x+=.006;
}

function installInput(){
  canvas.addEventListener('pointerdown',e=>{drag=true;px=e.clientX;py=e.clientY;if(viewMode!==2){viewMode=2;$('#view').textContent='ORBIT'}canvas.setPointerCapture(e.pointerId)});
  canvas.addEventListener('pointermove',e=>{if(!drag)return;orbitYaw-=(e.clientX-px)*.006;orbitPitch=clamp(orbitPitch+(e.clientY-py)*.004,-.05,1.05);px=e.clientX;py=e.clientY});
  canvas.addEventListener('pointerup',()=>drag=false);
  canvas.addEventListener('wheel',e=>{orbitDistance=clamp(orbitDistance+e.deltaY*.025,24,88)},{passive:true});

  $('#run').onclick=()=>{if(runtime.done)reset();running=true};
  $('#pause').onclick=()=>{running=false;renderSnapshot(runtime.snapshot())};
  $('#reset').onclick=reset;
  $('#view').onclick=e=>{viewMode=(viewMode+1)%3;e.currentTarget.textContent=['CHASE','WING','ORBIT'][viewMode]};
  $('#baseline').onclick=e=>{showBaseline=!showBaseline;e.currentTarget.classList.toggle('active',showBaseline);baselineGhost.visible=showBaseline};
  $('#data').onclick=()=>document.body.classList.toggle('show-data');
  $('#closeData').onclick=()=>document.body.classList.remove('show-data');
  addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight,false)});
}

function reset(){
  runtime.reset();acc=0;running=true;last=performance.now();trailL.history.length=0;trailR.history.length=0;renderSnapshot(runtime.snapshot(),true);
}

function frame(now){
  const dt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;
  if(running&&!runtime.done){
    acc+=dt*speedFactor;
    let n=0;
    while(acc>=DT&&n<40){
      const s=runtime.step();acc-=DT;n++;
      renderSnapshot(s);
    }
    if(runtime.done)running=false;
  }
  updateCamera(dt);moveWorld();
  renderer.render(scene,camera);
  requestAnimationFrame(frame);
}

boot();
