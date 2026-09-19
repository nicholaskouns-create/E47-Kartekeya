import * as THREE from 'three';

const R=6378137;
const TILE_SIZE=256;
const PATCH_RADIUS=1;
const GRID=96;
const DEFAULT_ZOOM=12;
const DEG=Math.PI/180;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const wrap=(v,n)=>((v%n)+n)%n;

function lonLatToTile(lon,lat,z){
  const n=2**z;
  const safeLat=clamp(lat,-85.05112878,85.05112878);
  const x=((lon+180)/360)*n;
  const s=Math.sin(safeLat*DEG);
  const y=(.5-Math.log((1+s)/(1-s))/(4*Math.PI))*n;
  return {x,y,n};
}
function tileToLonLat(x,y,z){
  const n=2**z;
  const lon=(x/n)*360-180;
  const lat=Math.atan(Math.sinh(Math.PI*(1-2*y/n)))/DEG;
  return {lon,lat};
}
function localMeters(origin,lat,lon){
  const lat0=origin.lat*DEG;
  return {
    x:(lon-origin.lon)*DEG*R*Math.cos(lat0),
    z:-(lat-origin.lat)*DEG*R
  };
}
function distanceMeters(a,b){
  const m=localMeters(a,b.lat,b.lon);
  return Math.hypot(m.x,m.z);
}
function imageryUrl(z,x,y){
  const n=2**z;
  return `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${z}/${clamp(y,0,n-1)}/${wrap(x,n)}`;
}
function demUrl(z,x,y){
  const n=2**z;
  return `https://demotiles.maplibre.org/terrain-tiles/${z}/${wrap(x,n)}/${clamp(y,0,n-1)}.png`;
}
async function fetchBitmap(url){
  const response=await fetch(url,{mode:'cors',cache:'force-cache'});
  if(!response.ok)throw new Error(`tile ${response.status}: ${url}`);
  return createImageBitmap(await response.blob());
}
async function stitchTiles(urlFor,z,cx,cy){
  const side=PATCH_RADIUS*2+1;
  const canvas=document.createElement('canvas');
  canvas.width=canvas.height=side*TILE_SIZE;
  const ctx=canvas.getContext('2d',{willReadFrequently:true});
  const jobs=[];
  for(let dy=-PATCH_RADIUS;dy<=PATCH_RADIUS;dy++){
    for(let dx=-PATCH_RADIUS;dx<=PATCH_RADIUS;dx++){
      jobs.push(fetchBitmap(urlFor(z,cx+dx,cy+dy)).then(bitmap=>({bitmap,dx,dy})));
    }
  }
  const tiles=await Promise.all(jobs);
  for(const {bitmap,dx,dy} of tiles){
    ctx.drawImage(bitmap,(dx+PATCH_RADIUS)*TILE_SIZE,(dy+PATCH_RADIUS)*TILE_SIZE,TILE_SIZE,TILE_SIZE);
    bitmap.close?.();
  }
  return canvas;
}
function decodeTerrainRGB(r,g,b){return -10000+(r*256*256+g*256+b)*.1}
function sampleHeightField(canvas,samples=GRID+1){
  const ctx=canvas.getContext('2d',{willReadFrequently:true});
  const image=ctx.getImageData(0,0,canvas.width,canvas.height);
  const heights=new Float32Array(samples*samples);
  let min=Infinity,max=-Infinity;
  for(let j=0;j<samples;j++){
    const sy=Math.round(j/(samples-1)*(canvas.height-1));
    for(let i=0;i<samples;i++){
      const sx=Math.round(i/(samples-1)*(canvas.width-1));
      const k=(sy*canvas.width+sx)*4;
      const h=decodeTerrainRGB(image.data[k],image.data[k+1],image.data[k+2]);
      heights[j*samples+i]=h;min=Math.min(min,h);max=Math.max(max,h);
    }
  }
  return {heights,samples,min,max};
}
function flatHeightField(){
  return {heights:new Float32Array((GRID+1)*(GRID+1)),samples:GRID+1,min:0,max:0};
}
function fallbackTexture(){
  const c=document.createElement('canvas');c.width=c.height=768;
  const ctx=c.getContext('2d'),g=ctx.createLinearGradient(0,0,768,768);
  g.addColorStop(0,'#243438');g.addColorStop(.5,'#4b554f');g.addColorStop(1,'#1a2428');
  ctx.fillStyle=g;ctx.fillRect(0,0,768,768);
  for(let i=0;i<60;i++){ctx.strokeStyle='rgba(160,190,180,.08)';ctx.beginPath();ctx.moveTo(0,i*17);ctx.lineTo(768,i*13);ctx.stroke()}
  return c;
}
function cloudTexture(){
  const c=document.createElement('canvas');c.width=c.height=256;
  const ctx=c.getContext('2d');
  const g=ctx.createRadialGradient(128,128,8,128,128,118);
  g.addColorStop(0,'rgba(255,255,255,.72)');g.addColorStop(.4,'rgba(255,247,234,.4)');g.addColorStop(1,'rgba(255,255,255,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,256,256);
  const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;return tex;
}
function seeded(seed){let x=(seed|0)||1;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return((x>>>0)%1000000)/1000000}}
function seedFor(lat,lon){return((Math.round((lat+90)*10000)*73856093)^(Math.round((lon+180)*10000)*19349663))>>>0}
function makeSky(scene){
  scene.fog=new THREE.FogExp2(0x896044,.00005);
  scene.add(new THREE.HemisphereLight(0xffd1a5,0x162329,2.4));
  const sun=new THREE.DirectionalLight(0xffbf7a,4.2);sun.position.set(-2600,4200,1900);scene.add(sun);
  const sky=new THREE.Mesh(new THREE.SphereGeometry(18000,40,24),new THREE.ShaderMaterial({
    side:THREE.BackSide,depthWrite:false,
    uniforms:{top:{value:new THREE.Color(0x361306)},horizon:{value:new THREE.Color(0xc07843)},low:{value:new THREE.Color(0x33464b)}},
    vertexShader:`varying vec3 vPos;void main(){vec4 w=modelMatrix*vec4(position,1.);vPos=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader:`varying vec3 vPos;uniform vec3 top;uniform vec3 horizon;uniform vec3 low;void main(){float h=normalize(vPos).y*.5+.5;vec3 c=mix(low,horizon,smoothstep(.12,.48,h));c=mix(c,top,smoothstep(.52,1.,h));gl_FragColor=vec4(c,1.);}`
  }));
  scene.add(sky);
}
function makeClouds(span,seed){
  const rng=seeded(seed^0x4f1bbcdc),tex=cloudTexture(),group=new THREE.Group();
  for(let i=0;i<52;i++){
    const cloud=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,opacity:.09+rng()*.15,depthWrite:false,color:0xfff3e6}));
    const w=500+rng()*1200;
    cloud.position.set((rng()-.5)*span*1.25,1200+rng()*1300,(rng()-.5)*span*1.25);
    cloud.scale.set(w,w*(.22+rng()*.18),1);group.add(cloud);
  }
  return group;
}
function makeBuildings(span,seed){
  const rng=seeded(seed^0x6a09e667),group=new THREE.Group();
  const geom=new THREE.BoxGeometry(1,1,1),mat=new THREE.MeshStandardMaterial({color:0x354145,roughness:.94,metalness:.03,emissive:0x101716,emissiveIntensity:.2});
  const count=330,mesh=new THREE.InstancedMesh(geom,mat,count),dummy=new THREE.Object3D();
  for(let i=0;i<count;i++){
    const w=16+rng()*50,d=18+rng()*60,h=10+Math.pow(rng(),2.4)*220;
    const ring=Math.sqrt(rng())*span*.32,a=rng()*Math.PI*2;
    dummy.position.set(Math.cos(a)*ring,h*.5+3,Math.sin(a)*ring);
    dummy.rotation.y=Math.round(rng()*4)*Math.PI/2;dummy.scale.set(w,h,d);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);
  }
  mesh.instanceMatrix.needsUpdate=true;group.add(mesh);return group;
}
function points(points,color,size){
  return new THREE.Points(new THREE.BufferGeometry().setFromPoints(points),new THREE.PointsMaterial({color,size,sizeAttenuation:true,transparent:true,opacity:.95,depthWrite:false}));
}
function makeLights(span,seed){
  const rng=seeded(seed^0xbb67ae85),group=new THREE.Group(),left=[],right=[];
  const runwayLength=Math.min(3600,span*.48);
  for(let z=-runwayLength/2;z<=runwayLength/2;z+=55){left.push(new THREE.Vector3(-34,7,z));right.push(new THREE.Vector3(34,7,z))}
  group.add(points(left,0xc7edff,9),points(right,0xc7edff,9));
  for(let road=0;road<7;road++){
    const p=[],baseZ=(rng()-.5)*span*.55,phase=rng()*Math.PI*2;
    for(let i=0;i<110;i++){const u=i/109;p.push(new THREE.Vector3((u-.5)*span*.72,5.5,baseZ+Math.sin(u*5+phase)*(80+rng()*35)))}
    group.add(points(p,0xffbd68,5.5));
  }
  return group;
}
function dispose(root){
  root?.traverse?.(o=>{o.geometry?.dispose?.();if(Array.isArray(o.material))o.material.forEach(m=>m.dispose?.());else o.material?.dispose?.()});
}
export async function createSkyrmionTerrain3D({host=document.body,lat=36.1699,lon=-115.1398,altitude_m=3658,heading=0,pitch=0,roll=0,speed=216,zoom=DEFAULT_ZOOM}={}){
  const canvas=document.createElement('canvas');canvas.id='terrain3d';canvas.setAttribute('aria-hidden','true');
  Object.assign(canvas.style,{position:'fixed',inset:'0',width:'100%',height:'100%',zIndex:'0',pointerEvents:'none',transition:'opacity .35s ease'});host.prepend(canvas);
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,2));renderer.setSize(innerWidth,innerHeight,false);renderer.outputColorSpace=THREE.SRGBColorSpace;renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;
  const scene=new THREE.Scene();makeSky(scene);
  const camera=new THREE.PerspectiveCamera(61,innerWidth/innerHeight,1,30000);
  const flight={lat,lon,altitude_m,heading,pitch,roll,speed,domain:0,enabled:true};
  const chase={distance:185,height:56,lookAhead:240,damping:.085,bankMix:.34};
  const up=new THREE.Vector3(0,1,0),forward=new THREE.Vector3(),right=new THREE.Vector3(),desiredCamera=new THREE.Vector3(),desiredTarget=new THREE.Vector3(),smoothTarget=new THREE.Vector3(),desiredUp=new THREE.Vector3(),rollQ=new THREE.Quaternion();
  let patch=null,patchLoading=false,generation=0,destroyed=false;

  async function buildPatch(centerLat,centerLon,force=false){
    if(patchLoading&&!force)return;patchLoading=true;const gen=++generation;
    dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:'LOADING'}}));
    try{
      const tile=lonLatToTile(centerLon,centerLat,zoom),cx=Math.floor(tile.x),cy=Math.floor(tile.y);
      const center=tileToLonLat(cx+.5,cy+.5,zoom);
      const west=tileToLonLat(cx-PATCH_RADIUS,cy+.5,zoom),east=tileToLonLat(cx+PATCH_RADIUS+1,cy+.5,zoom);
      const span=Math.abs(localMeters(center,center.lat,east.lon).x-localMeters(center,center.lat,west.lon).x);
      const [imgResult,demResult]=await Promise.allSettled([stitchTiles(imageryUrl,zoom,cx,cy),stitchTiles(demUrl,zoom,cx,cy)]);
      if(gen!==generation||destroyed)return;
      const imagery=imgResult.status==='fulfilled'?imgResult.value:fallbackTexture();
      let field=flatHeightField();
      if(demResult.status==='fulfilled'){try{field=sampleHeightField(demResult.value)}catch{}}
      const geometry=new THREE.PlaneGeometry(span,span,GRID,GRID);geometry.rotateX(-Math.PI/2);
      const pos=geometry.attributes.position;
      for(let j=0;j<=GRID;j++)for(let i=0;i<=GRID;i++){const vi=j*(GRID+1)+i;pos.setY(vi,field.heights[vi])}
      pos.needsUpdate=true;geometry.computeVertexNormals();
      const texture=new THREE.CanvasTexture(imagery);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
      const terrain=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({map:texture,roughness:.98,metalness:0}));
      const seed=seedFor(center.lat,center.lon),world=new THREE.Group(),buildings=makeBuildings(span,seed),clouds=makeClouds(span,seed),lights=makeLights(span,seed);
      world.add(terrain,buildings,clouds,lights);scene.add(world);
      if(patch?.world){scene.remove(patch.world);dispose(patch.world);patch.texture?.dispose?.()}
      patch={center,span,world,terrain,buildings,clouds,lights,texture,min:field.min,max:field.max};
      dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:imgResult.status==='fulfilled'&&demResult.status==='fulfilled'?'LIVE':'DEGRADED',center,span,elevation_min_m:field.min,elevation_max_m:field.max}}));
    }catch(error){
      dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:'FALLBACK',error:String(error?.message||error)}}));
    }finally{if(gen===generation)patchLoading=false}
  }
  function updateFlightState(next={}){
    Object.assign(flight,next);
    const atmospheric=flight.enabled!==false&&Number(flight.domain||0)===0;canvas.style.opacity=atmospheric?'1':'0';
    if(!patch||distanceMeters(patch.center,flight)>patch.span*.28)buildPatch(flight.lat,flight.lon).catch(()=>{});
  }
  function teleport(next={}){Object.assign(flight,next);buildPatch(flight.lat,flight.lon,true).catch(()=>{})}
  function updateCamera(dt){
    if(!patch)return;
    const local=localMeters(patch.center,flight.lat,flight.lon);
    const craftPos=new THREE.Vector3(local.x,Math.max(5,Number(flight.altitude_m||0)),local.z);
    const h=Number(flight.heading||0),p=Number(flight.pitch||0),r=Number(flight.roll||0),cp=Math.cos(p),sp=Math.sin(p);
    forward.set(Math.sin(h)*cp,sp,-Math.cos(h)*cp).normalize();
    right.crossVectors(forward,up).normalize();if(right.lengthSq()<.01)right.set(1,0,0);
    const speedFactor=clamp(Number(flight.speed||0)/450,0,1);
    desiredCamera.copy(craftPos).addScaledVector(forward,-(chase.distance+speedFactor*85)).addScaledVector(up,chase.height+Math.max(0,p)*38);
    desiredTarget.copy(craftPos).addScaledVector(forward,chase.lookAhead+speedFactor*100);
    const k=1-Math.pow(1-chase.damping,dt*60);
    camera.position.lerp(desiredCamera,k);smoothTarget.lerp(desiredTarget,k*1.15);
    desiredUp.copy(up);rollQ.setFromAxisAngle(forward,-r*chase.bankMix);desiredUp.applyQuaternion(rollQ).normalize();camera.up.lerp(desiredUp,k*.9).normalize();
    camera.lookAt(smoothTarget);camera.fov+=(61+speedFactor*5-camera.fov)*k*.4;camera.updateProjectionMatrix();
  }
  let last=performance.now();
  function frame(now){
    if(destroyed)return;requestAnimationFrame(frame);
    const dt=Math.min(.033,Math.max(.001,(now-last)/1000));last=now;updateCamera(dt);
    if(patch?.clouds)patch.clouds.rotation.y+=dt*.0018;
    renderer.render(scene,camera);
  }
  addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight,false);renderer.setPixelRatio(Math.min(devicePixelRatio||1,2))});
  await buildPatch(lat,lon,true);updateFlightState(flight);requestAnimationFrame(frame);
  return {schema:'SKYRMION-TERRAIN-3D-1.0',renderer,scene,camera,get patch(){return patch},updateFlightState,teleport,destroy(){destroyed=true;generation++;if(patch?.world)dispose(patch.world);renderer.dispose();canvas.remove()}};
}
