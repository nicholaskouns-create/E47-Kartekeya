import * as THREE from 'three';

const R=6378137;
const TILE_SIZE=256;
const PATCH_RADIUS=1;
const GRID=96;
const DEFAULT_ZOOM=12;
const DEG=Math.PI/180;
const CRAFT_NAMES=['F-16','SR-71','X-15','EIDOLON','MANTA','SYNTAX JACOB'];
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const wrap=(v,n)=>((v%n)+n)%n;

function lonLatToTile(lon,lat,z){
  const n=2**z,safeLat=clamp(lat,-85.05112878,85.05112878);
  const x=((lon+180)/360)*n,s=Math.sin(safeLat*DEG);
  return {x,y:(.5-Math.log((1+s)/(1-s))/(4*Math.PI))*n,n};
}
function tileToLonLat(x,y,z){
  const n=2**z;
  return {lon:(x/n)*360-180,lat:Math.atan(Math.sinh(Math.PI*(1-2*y/n)))/DEG};
}
function localMeters(origin,lat,lon){
  const lat0=origin.lat*DEG;
  return {x:(lon-origin.lon)*DEG*R*Math.cos(lat0),z:-(lat-origin.lat)*DEG*R};
}
function distanceMeters(a,b){const m=localMeters(a,b.lat,b.lon);return Math.hypot(m.x,m.z)}
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
  const side=PATCH_RADIUS*2+1,canvas=document.createElement('canvas');
  canvas.width=canvas.height=side*TILE_SIZE;
  const ctx=canvas.getContext('2d',{willReadFrequently:true}),jobs=[];
  for(let dy=-PATCH_RADIUS;dy<=PATCH_RADIUS;dy++)for(let dx=-PATCH_RADIUS;dx<=PATCH_RADIUS;dx++){
    jobs.push(fetchBitmap(urlFor(z,cx+dx,cy+dy)).then(bitmap=>({bitmap,dx,dy})));
  }
  for(const {bitmap,dx,dy} of await Promise.all(jobs)){
    ctx.drawImage(bitmap,(dx+PATCH_RADIUS)*TILE_SIZE,(dy+PATCH_RADIUS)*TILE_SIZE,TILE_SIZE,TILE_SIZE);
    bitmap.close?.();
  }
  return canvas;
}
function decodeTerrainRGB(r,g,b){return -10000+(r*256*256+g*256+b)*.1}
function sampleHeightField(canvas,samples=GRID+1){
  const ctx=canvas.getContext('2d',{willReadFrequently:true}),image=ctx.getImageData(0,0,canvas.width,canvas.height);
  const heights=new Float32Array(samples*samples);let min=Infinity,max=-Infinity;
  for(let j=0;j<samples;j++){
    const sy=Math.round(j/(samples-1)*(canvas.height-1));
    for(let i=0;i<samples;i++){
      const sx=Math.round(i/(samples-1)*(canvas.width-1)),k=(sy*canvas.width+sx)*4;
      const h=decodeTerrainRGB(image.data[k],image.data[k+1],image.data[k+2]);
      heights[j*samples+i]=h;min=Math.min(min,h);max=Math.max(max,h);
    }
  }
  return {heights,samples,min,max};
}
function flatHeightField(){return {heights:new Float32Array((GRID+1)*(GRID+1)),samples:GRID+1,min:0,max:0}}
function fallbackTexture(){
  const c=document.createElement('canvas');c.width=c.height=768;
  const ctx=c.getContext('2d'),g=ctx.createLinearGradient(0,0,768,768);
  g.addColorStop(0,'#243438');g.addColorStop(.5,'#4b554f');g.addColorStop(1,'#1a2428');
  ctx.fillStyle=g;ctx.fillRect(0,0,768,768);
  for(let i=0;i<60;i++){ctx.strokeStyle='rgba(160,190,180,.08)';ctx.beginPath();ctx.moveTo(0,i*17);ctx.lineTo(768,i*13);ctx.stroke()}
  return c;
}
function cloudTexture(){
  const c=document.createElement('canvas');c.width=c.height=256;const ctx=c.getContext('2d');
  const g=ctx.createRadialGradient(128,128,8,128,128,118);
  g.addColorStop(0,'rgba(255,255,255,.72)');g.addColorStop(.4,'rgba(255,247,234,.4)');g.addColorStop(1,'rgba(255,255,255,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,256,256);
  const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;return tex;
}
function seeded(seed){let x=(seed|0)||1;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return((x>>>0)%1000000)/1000000}}
function seedFor(lat,lon){return((Math.round((lat+90)*10000)*73856093)^(Math.round((lon+180)*10000)*19349663))>>>0}

function makeSky(scene){
  const fog=new THREE.FogExp2(0x896044,.00005);scene.fog=fog;
  scene.add(new THREE.HemisphereLight(0xffd1a5,0x162329,2.4));
  const sun=new THREE.DirectionalLight(0xffbf7a,4.2);sun.position.set(-2600,4200,1900);
  sun.castShadow=true;sun.shadow.mapSize.set(1024,1024);sun.shadow.camera.near=10;sun.shadow.camera.far=11000;
  sun.shadow.camera.left=-3500;sun.shadow.camera.right=3500;sun.shadow.camera.top=3500;sun.shadow.camera.bottom=-3500;sun.shadow.bias=-.0002;
  scene.add(sun);
  const sky=new THREE.Mesh(new THREE.SphereGeometry(18000,40,24),new THREE.ShaderMaterial({
    side:THREE.BackSide,depthWrite:false,
    uniforms:{top:{value:new THREE.Color(0x361306)},horizon:{value:new THREE.Color(0xc07843)},low:{value:new THREE.Color(0x33464b)}},
    vertexShader:`varying vec3 vPos;void main(){vec4 w=modelMatrix*vec4(position,1.);vPos=w.xyz;gl_Position=projectionMatrix*viewMatrix*w;}`,
    fragmentShader:`varying vec3 vPos;uniform vec3 top;uniform vec3 horizon;uniform vec3 low;void main(){float h=normalize(vPos).y*.5+.5;vec3 c=mix(low,horizon,smoothstep(.12,.48,h));c=mix(c,top,smoothstep(.52,1.,h));gl_FragColor=vec4(c,1.);}`
  }));
  scene.add(sky);return {sky,sun,fog};
}
function makeSpace(scene){
  const count=4200,pos=new Float32Array(count*3);
  for(let i=0;i<count;i++){
    const r=8000+Math.random()*10000,a=Math.random()*Math.PI*2,u=Math.random()*2-1,s=Math.sqrt(1-u*u);
    pos[i*3]=Math.cos(a)*s*r;pos[i*3+1]=u*r;pos[i*3+2]=Math.sin(a)*s*r;
  }
  const geo=new THREE.BufferGeometry();geo.setAttribute('position',new THREE.BufferAttribute(pos,3));
  const stars=new THREE.Points(geo,new THREE.PointsMaterial({color:0xddeeff,size:7,sizeAttenuation:true,transparent:true,opacity:.86,depthWrite:false}));
  const planet=new THREE.Mesh(new THREE.SphereGeometry(5800,64,40),new THREE.MeshStandardMaterial({color:0x16466d,roughness:1,metalness:0,emissive:0x061522,emissiveIntensity:.3}));
  planet.position.set(0,-5700,-5200);stars.visible=false;planet.visible=false;scene.add(stars,planet);return {stars,planet};
}
function makeClouds(span,seed){
  const rng=seeded(seed^0x4f1bbcdc),tex=cloudTexture(),group=new THREE.Group();
  for(let i=0;i<52;i++){
    const cloud=new THREE.Sprite(new THREE.SpriteMaterial({map:tex,transparent:true,opacity:.09+rng()*.15,depthWrite:false,color:0xfff3e6}));
    const w=500+rng()*1200;cloud.position.set((rng()-.5)*span*1.25,1200+rng()*1300,(rng()-.5)*span*1.25);
    cloud.scale.set(w,w*(.22+rng()*.18),1);group.add(cloud);
  }
  return group;
}
function makeBuildings(span,seed){
  const rng=seeded(seed^0x6a09e667),group=new THREE.Group();
  const geom=new THREE.BoxGeometry(1,1,1),mat=new THREE.MeshStandardMaterial({color:0x354145,roughness:.94,metalness:.03,emissive:0x101716,emissiveIntensity:.2});
  const count=330,mesh=new THREE.InstancedMesh(geom,mat,count),dummy=new THREE.Object3D();
  for(let i=0;i<count;i++){
    const w=16+rng()*50,d=18+rng()*60,h=10+Math.pow(rng(),2.4)*220,ring=Math.sqrt(rng())*span*.32,a=rng()*Math.PI*2;
    dummy.position.set(Math.cos(a)*ring,h*.5+3,Math.sin(a)*ring);dummy.rotation.y=Math.round(rng()*4)*Math.PI/2;dummy.scale.set(w,h,d);dummy.updateMatrix();mesh.setMatrixAt(i,dummy.matrix);
  }
  mesh.instanceMatrix.needsUpdate=true;mesh.castShadow=true;mesh.receiveShadow=true;group.add(mesh);return group;
}
function points(points,color,size){
  return new THREE.Points(new THREE.BufferGeometry().setFromPoints(points),new THREE.PointsMaterial({color,size,sizeAttenuation:true,transparent:true,opacity:.95,depthWrite:false}));
}
function makeLights(span,seed){
  const rng=seeded(seed^0xbb67ae85),group=new THREE.Group(),left=[],right=[],runwayLength=Math.min(3600,span*.48);
  for(let z=-runwayLength/2;z<=runwayLength/2;z+=55){left.push(new THREE.Vector3(-34,7,z));right.push(new THREE.Vector3(34,7,z))}
  group.add(points(left,0xc7edff,9),points(right,0xc7edff,9));
  for(let road=0;road<7;road++){
    const p=[],baseZ=(rng()-.5)*span*.55,phase=rng()*Math.PI*2;
    for(let i=0;i<110;i++){const u=i/109;p.push(new THREE.Vector3((u-.5)*span*.72,5.5,baseZ+Math.sin(u*5+phase)*(80+rng()*35)))}
    group.add(points(p,0xffbd68,5.5));
  }
  return group;
}

function material(color,{emissive=0x000000,emissiveIntensity=0,metalness=.58,roughness=.34,transparent=false,opacity=1}={}){
  return new THREE.MeshStandardMaterial({color,emissive,emissiveIntensity,metalness,roughness,transparent,opacity,side:THREE.DoubleSide});
}
function basic(color,opacity=1){return new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,side:THREE.DoubleSide,depthWrite:opacity>=1})}
function shadowize(group){
  group.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});return group;
}
function planform(coords,mat,y=0){
  const shape=new THREE.Shape();shape.moveTo(coords[0][0],coords[0][1]);
  for(let i=1;i<coords.length;i++)shape.lineTo(coords[i][0],coords[i][1]);
  shape.closePath();
  const mesh=new THREE.Mesh(new THREE.ShapeGeometry(shape),mat);mesh.rotation.x=Math.PI/2;mesh.position.y=y;return mesh;
}
function capsule(radius,length,mat){
  const m=new THREE.Mesh(new THREE.CapsuleGeometry(radius,length,6,16),mat);m.rotation.x=Math.PI/2;return m;
}
function engineGlow(z,color=0x66fff0,radius=.8){
  const ring=new THREE.Mesh(new THREE.TorusGeometry(radius,.14,8,32),basic(color,.85));ring.position.z=z;return ring;
}
function makeF16(){
  const g=new THREE.Group(),skin=material(0x7d898c,{metalness:.72,roughness:.28});
  g.add(planform([[0,-8.2],[1.6,-3.1],[5.8,.8],[5.1,2.4],[1.2,1.8],[1.4,6.2],[-1.4,6.2],[-1.2,1.8],[-5.1,2.4],[-5.8,.8],[-1.6,-3.1]],skin,.05));
  const body=capsule(.72,10.5,skin);body.position.z=-.2;g.add(body);
  const tail=planform([[0,1.8],[0,6.4],[0,6.4]],skin);tail.visible=false;
  const fin=new THREE.Mesh(new THREE.BoxGeometry(.12,2.8,3.0),skin);fin.position.set(0,1.4,3.5);fin.rotation.x=-.25;g.add(fin);
  g.add(engineGlow(6.1,0x68d9ff,.58));g.scale.setScalar(1.15);g.userData.label='F-16';return shadowize(g);
}
function makeSR71(){
  const g=new THREE.Group(),skin=material(0x111719,{metalness:.8,roughness:.22});
  g.add(planform([[0,-13],[2,-7],[8,-1],[7.5,4],[3,8],[1.7,10],[-1.7,10],[-3,8],[-7.5,4],[-8,-1],[-2,-7]],skin,.03));
  const body=capsule(.62,17,skin);body.position.z=-1.3;g.add(body);
  for(const x of [-3.1,3.1]){const n=capsule(.66,10.5,skin);n.position.set(x,-.12,1.4);g.add(n);const glow=engineGlow(7.0,0x5fdcff,.52);glow.position.set(x,0,7);g.add(glow)}
  g.userData.label='SR-71';return shadowize(g);
}
function makeX15(){
  const g=new THREE.Group(),skin=material(0x596469,{metalness:.7,roughness:.3});
  g.add(planform([[0,-7.8],[1,-3],[4,.2],[3.5,1.6],[1,1.2],[1.2,6],[-1.2,6],[-1,1.2],[-3.5,1.6],[-4,.2],[-1,-3]],skin,.04));
  const body=capsule(.66,10.8,skin);body.position.z=-.8;g.add(body);
  const fin=new THREE.Mesh(new THREE.BoxGeometry(.1,3.5,2.4),skin);fin.position.set(0,1.7,3.8);fin.rotation.x=-.2;g.add(fin);
  g.add(engineGlow(6,0xff985f,.68));g.userData.label='X-15';return shadowize(g);
}
function makeEidolon(){
  const g=new THREE.Group(),shell=material(0x6b7d7f,{emissive:0x123b3a,emissiveIntensity:.55,metalness:.72,roughness:.2});
  const core=new THREE.Mesh(new THREE.SphereGeometry(3.5,32,18),shell);core.scale.set(1.8,.38,1);g.add(core);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(4.8,.18,12,72),basic(0x6fffe8,.72));ring.rotation.x=Math.PI/2;g.add(ring);
  const ring2=new THREE.Mesh(new THREE.TorusGeometry(3.8,.07,8,64),basic(0xb8fff2,.55));ring2.rotation.x=Math.PI/2;ring2.rotation.z=.35;g.add(ring2);
  g.userData.animate=dt=>{ring.rotation.z+=dt*.55;ring2.rotation.z-=dt*.9};g.userData.label='EIDOLON';return shadowize(g);
}
function makeManta(){
  const g=new THREE.Group(),baseMat=material(0x447d78,{emissive:0x123d38,emissiveIntensity:.65,metalness:.46,roughness:.28,transparent:true,opacity:.72});
  const shell=planform([[0,-8],[4.5,-4],[8,0],[5.8,3.2],[2.2,5.5],[0,4.4],[-2.2,5.5],[-5.8,3.2],[-8,0],[-4.5,-4]],baseMat,0);g.add(shell);
  const pointPositions=new Float32Array(125*3),pointGeo=new THREE.BufferGeometry();pointGeo.setAttribute('position',new THREE.BufferAttribute(pointPositions,3));
  const pts=new THREE.Points(pointGeo,new THREE.PointsMaterial({color:0xbaffee,size:.48,sizeAttenuation:true,transparent:true,opacity:.95,depthWrite:false}));g.add(pts);
  const edges=[];for(let a=0;a<5;a++)for(let b=0;b<5;b++)for(let c=0;c<5;c++){const i=a*25+b*5+c;if(a<4)edges.push([i,i+25]);if(b<4)edges.push([i,i+5]);if(c<4)edges.push([i,i+1])}
  const linePositions=new Float32Array(edges.length*2*3),lineGeo=new THREE.BufferGeometry();lineGeo.setAttribute('position',new THREE.BufferAttribute(linePositions,3));
  const lines=new THREE.LineSegments(lineGeo,new THREE.LineBasicMaterial({color:0x72e9d9,transparent:true,opacity:.42,depthWrite:false}));g.add(lines);
  g.userData={label:'MANTA',shell,pointPositions,pointGeo,linePositions,lineGeo,edges,hasFrame:false};
  return shadowize(g);
}
function makeSyntaxJacob(){
  const g=new THREE.Group(),shell=material(0x7778a2,{emissive:0x2c245d,emissiveIntensity:.75,metalness:.65,roughness:.22});
  const body=new THREE.Mesh(new THREE.OctahedronGeometry(4.2,1),shell);body.scale.set(.75,.45,1.65);body.rotation.x=.18;g.add(body);
  const spine=capsule(.38,10.5,shell);spine.position.z=-1;g.add(spine);
  const r1=new THREE.Mesh(new THREE.TorusGeometry(5.2,.11,8,72),basic(0xb6a8ff,.8));r1.rotation.x=Math.PI/2;g.add(r1);
  const r2=new THREE.Mesh(new THREE.TorusGeometry(3.7,.08,8,64),basic(0x86fff0,.62));r2.rotation.x=Math.PI/2;r2.rotation.z=Math.PI/4;g.add(r2);
  g.userData.animate=dt=>{r1.rotation.z+=dt*.38;r2.rotation.z-=dt*.72};g.userData.label='SYNTAX JACOB';return shadowize(g);
}
function makeFleet(){
  const models=[makeF16(),makeSR71(),makeX15(),makeEidolon(),makeManta(),makeSyntaxJacob()];
  models.forEach((m,i)=>{m.visible=i===0;m.name=CRAFT_NAMES[i]});return models;
}
function updateMantaModel(model,state){
  const geo=state?.geometry;if(!model||!Array.isArray(geo)||geo.length<375)return;
  const d=model.userData,scale=3.65;
  for(let i=0;i<125;i++){
    const j=i*3;d.pointPositions[j]=geo[j]*scale;d.pointPositions[j+1]=geo[j+1]*scale*2.1;d.pointPositions[j+2]=geo[j+2]*scale;
  }
  d.pointGeo.attributes.position.needsUpdate=true;
  let k=0;
  for(const [a,b] of d.edges){
    const ia=a*3,ib=b*3;
    d.linePositions[k++]=d.pointPositions[ia];d.linePositions[k++]=d.pointPositions[ia+1];d.linePositions[k++]=d.pointPositions[ia+2];
    d.linePositions[k++]=d.pointPositions[ib];d.linePositions[k++]=d.pointPositions[ib+1];d.linePositions[k++]=d.pointPositions[ib+2];
  }
  d.lineGeo.attributes.position.needsUpdate=true;d.hasFrame=true;d.shell.material.opacity=.35;
}
function dispose(root){
  root?.traverse?.(o=>{o.geometry?.dispose?.();if(Array.isArray(o.material))o.material.forEach(m=>m.dispose?.());else o.material?.dispose?.()});
}

export async function createSkyrmionTerrain3D({host=document.body,lat=36.1699,lon=-115.1398,altitude_m=3658,heading=0,pitch=0,roll=0,speed=216,active=0,zoom=DEFAULT_ZOOM}={}){
  const canvas=document.createElement('canvas');canvas.id='terrain3d';canvas.setAttribute('aria-hidden','true');
  Object.assign(canvas.style,{position:'fixed',inset:'0',width:'100%',height:'100%',zIndex:'0',pointerEvents:'none'});
  host.prepend(canvas);
  const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false,powerPreference:'high-performance'});
  const maxDpr=matchMedia('(max-width:800px)').matches?1.45:2;
  renderer.setPixelRatio(Math.min(devicePixelRatio||1,maxDpr));renderer.setSize(innerWidth,innerHeight,false);renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.ACESFilmicToneMapping;renderer.toneMappingExposure=1.08;renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;renderer.setClearColor(0x010207,1);
  const scene=new THREE.Scene(),atmos=makeSky(scene),space=makeSpace(scene),camera=new THREE.PerspectiveCamera(61,innerWidth/innerHeight,1,30000);
  const craftRoot=new THREE.Group(),fleet=makeFleet();fleet.forEach(m=>craftRoot.add(m));scene.add(craftRoot);
  const flight={lat,lon,altitude_m,heading,pitch,roll,speed,active,domain:0,enabled:true};
  const chase={distance:185,height:52,lookAhead:235,damping:.09,bankMix:.38};
  const worldUp=new THREE.Vector3(0,1,0),forward=new THREE.Vector3(),right=new THREE.Vector3(),craftUp=new THREE.Vector3(),cameraUp=new THREE.Vector3();
  const desiredCamera=new THREE.Vector3(),desiredTarget=new THREE.Vector3(),smoothTarget=new THREE.Vector3(),basis=new THREE.Matrix4(),baseQ=new THREE.Quaternion(),rollQ=new THREE.Quaternion(),localRollAxis=new THREE.Vector3(0,0,-1);
  let patch=null,patchLoading=false,generation=0,destroyed=false,activeIndex=clamp(Number(active)||0,0,5),mantaState=null;

  function setActiveCraft(i){
    const next=clamp(Number(i)||0,0,fleet.length-1);if(next===activeIndex&&fleet[next].visible)return;
    activeIndex=next;fleet.forEach((m,j)=>m.visible=j===activeIndex);
    dispatchEvent(new CustomEvent('skyrmion:craft-3d',{detail:{active:activeIndex,name:CRAFT_NAMES[activeIndex]}}));
  }
  async function buildPatch(centerLat,centerLon,force=false){
    if(patchLoading&&!force)return;patchLoading=true;const gen=++generation;
    dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:'LOADING'}}));
    try{
      const tile=lonLatToTile(centerLon,centerLat,zoom),cx=Math.floor(tile.x),cy=Math.floor(tile.y),center=tileToLonLat(cx+.5,cy+.5,zoom);
      const west=tileToLonLat(cx-PATCH_RADIUS,cy+.5,zoom),east=tileToLonLat(cx+PATCH_RADIUS+1,cy+.5,zoom);
      const span=Math.abs(localMeters(center,center.lat,east.lon).x-localMeters(center,center.lat,west.lon).x);
      const [imgResult,demResult]=await Promise.allSettled([stitchTiles(imageryUrl,zoom,cx,cy),stitchTiles(demUrl,zoom,cx,cy)]);
      if(gen!==generation||destroyed)return;
      const imagery=imgResult.status==='fulfilled'?imgResult.value:fallbackTexture();let field=flatHeightField();
      if(demResult.status==='fulfilled'){try{field=sampleHeightField(demResult.value)}catch{}}
      const geometry=new THREE.PlaneGeometry(span,span,GRID,GRID);geometry.rotateX(-Math.PI/2);const pos=geometry.attributes.position;
      for(let j=0;j<=GRID;j++)for(let i=0;i<=GRID;i++){const vi=j*(GRID+1)+i;pos.setY(vi,field.heights[vi])}
      pos.needsUpdate=true;geometry.computeVertexNormals();
      const texture=new THREE.CanvasTexture(imagery);texture.colorSpace=THREE.SRGBColorSpace;texture.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());
      const terrain=new THREE.Mesh(geometry,new THREE.MeshStandardMaterial({map:texture,roughness:.98,metalness:0}));terrain.receiveShadow=true;
      const seed=seedFor(center.lat,center.lon),world=new THREE.Group(),buildings=makeBuildings(span,seed),clouds=makeClouds(span,seed),lights=makeLights(span,seed);
      const centerElevation=field.heights[Math.floor(field.heights.length/2)]||0;buildings.position.y=centerElevation;lights.position.y=centerElevation;
      world.add(terrain,buildings,clouds,lights);scene.add(world);
      if(patch?.world){scene.remove(patch.world);dispose(patch.world);patch.texture?.dispose?.()}
      patch={center,span,world,terrain,buildings,clouds,lights,texture,min:field.min,max:field.max,centerElevation};
      updateDomainVisibility();
      dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:imgResult.status==='fulfilled'&&demResult.status==='fulfilled'?'LIVE':'DEGRADED',center,span,elevation_min_m:field.min,elevation_max_m:field.max}}));
    }catch(error){
      dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:'FALLBACK',error:String(error?.message||error)}}));
    }finally{if(gen===generation)patchLoading=false}
  }
  function updateDomainVisibility(){
    const d=Number(flight.domain||0),atmospheric=d===0;
    if(patch?.world)patch.world.visible=atmospheric;
    atmos.sky.visible=atmospheric;atmos.sun.visible=atmospheric;scene.fog=atmospheric?atmos.fog:null;
    space.stars.visible=!atmospheric;space.planet.visible=d===1;
  }
  function updateFlightState(next={}){
    Object.assign(flight,next);setActiveCraft(flight.active);updateDomainVisibility();
    if(!patch||distanceMeters(patch.center,flight)>patch.span*.28)buildPatch(flight.lat,flight.lon).catch(()=>{});
  }
  function updateMantaFrame(state){mantaState=state;updateMantaModel(fleet[4],state)}
  function teleport(next={}){Object.assign(flight,next);setActiveCraft(flight.active);buildPatch(flight.lat,flight.lon,true).catch(()=>{})}
  function updateCraftPose(){
    if(!patch)return;
    const local=localMeters(patch.center,flight.lat,flight.lon),h=Number(flight.heading||0),p=Number(flight.pitch||0),r=Number(flight.roll||0),cp=Math.cos(p),sp=Math.sin(p);
    craftRoot.position.set(local.x,Math.max(5,Number(flight.altitude_m||0)),local.z);
    forward.set(Math.sin(h)*cp,sp,-Math.cos(h)*cp).normalize();
    right.crossVectors(forward,worldUp).normalize();if(right.lengthSq()<.01)right.set(1,0,0);
    craftUp.crossVectors(right,forward).normalize();
    basis.makeBasis(right,craftUp,forward.clone().negate());baseQ.setFromRotationMatrix(basis);rollQ.setFromAxisAngle(localRollAxis,r);
    craftRoot.quaternion.copy(baseQ).multiply(rollQ);
  }
  function updateCamera(dt){
    if(!patch)return;updateCraftPose();
    const speedFactor=clamp(Number(flight.speed||0)/450,0,1),k=1-Math.pow(1-chase.damping,dt*60);
    craftUp.set(0,1,0).applyQuaternion(craftRoot.quaternion).normalize();
    cameraUp.copy(worldUp).lerp(craftUp,chase.bankMix).normalize();
    desiredCamera.copy(craftRoot.position).addScaledVector(forward,-(chase.distance+speedFactor*85)).addScaledVector(cameraUp,chase.height+Math.max(0,Number(flight.pitch||0))*34);
    desiredTarget.copy(craftRoot.position).addScaledVector(forward,chase.lookAhead+speedFactor*105);
    camera.position.lerp(desiredCamera,k);smoothTarget.lerp(desiredTarget,k*1.15);camera.up.lerp(cameraUp,k*.85).normalize();camera.lookAt(smoothTarget);
    camera.fov+=(61+speedFactor*5-camera.fov)*k*.4;camera.updateProjectionMatrix();
  }
  let last=performance.now();
  function frame(now){
    if(destroyed)return;requestAnimationFrame(frame);
    const dt=Math.min(.033,Math.max(.001,(now-last)/1000));last=now;updateCamera(dt);
    const current=fleet[activeIndex];current?.userData?.animate?.(dt);
    if(patch?.clouds)patch.clouds.rotation.y+=dt*.0018;
    renderer.render(scene,camera);
  }
  addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight,false);renderer.setPixelRatio(Math.min(devicePixelRatio||1,maxDpr))});
  await buildPatch(lat,lon,true);setActiveCraft(activeIndex);if(mantaState)updateMantaFrame(mantaState);updateFlightState(flight);updateCraftPose();requestAnimationFrame(frame);
  return {
    schema:'SKYRMION-TERRAIN-3D-2.0',ready:true,renderer,scene,camera,craftRoot,fleet,
    get activeCraft(){return fleet[activeIndex]},get patch(){return patch},
    updateFlightState,updateMantaFrame,teleport,setActiveCraft,
    destroy(){destroyed=true;generation++;if(patch?.world)dispose(patch.world);fleet.forEach(dispose);renderer.dispose();canvas.remove()}
  };
}
