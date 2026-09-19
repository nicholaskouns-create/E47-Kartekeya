import * as THREE from 'three';
let licensedAssetModulePromise=null;
const getLicensedAssetModule=()=>licensedAssetModulePromise||(licensedAssetModulePromise=import('./licensed-aircraft-assets.js'));

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

function makeEnvironmentTexture(){
  const c=document.createElement('canvas');c.width=1024;c.height=512;
  const ctx=c.getContext('2d'),g=ctx.createLinearGradient(0,0,0,c.height);
  g.addColorStop(0,'#152534');g.addColorStop(.28,'#5a6570');g.addColorStop(.47,'#d09565');g.addColorStop(.56,'#6c6558');g.addColorStop(1,'#111715');
  ctx.fillStyle=g;ctx.fillRect(0,0,c.width,c.height);
  const sun=ctx.createRadialGradient(210,225,2,210,225,95);
  sun.addColorStop(0,'rgba(255,245,210,1)');sun.addColorStop(.2,'rgba(255,189,112,.75)');sun.addColorStop(1,'rgba(255,150,75,0)');
  ctx.fillStyle=sun;ctx.fillRect(0,0,c.width,c.height);
  const tex=new THREE.CanvasTexture(c);tex.mapping=THREE.EquirectangularReflectionMapping;tex.colorSpace=THREE.SRGBColorSpace;return tex;
}
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
  return new THREE.MeshPhysicalMaterial({
    color,emissive,emissiveIntensity,metalness,roughness,transparent,opacity,side:THREE.DoubleSide,
    clearcoat:.42,clearcoatRoughness:.22,sheen:.08,sheenRoughness:.45
  });
}
function physicalGlass(color=0x7fc9da){
  return new THREE.MeshPhysicalMaterial({
    color,metalness:.05,roughness:.08,transparent:true,opacity:.48,transmission:.38,thickness:.22,
    clearcoat:1,clearcoatRoughness:.05,ior:1.46,side:THREE.DoubleSide,depthWrite:false
  });
}
function basic(color,opacity=1){
  return new THREE.MeshBasicMaterial({color,transparent:opacity<1,opacity,side:THREE.DoubleSide,depthWrite:opacity>=1,blending:opacity<1?THREE.AdditiveBlending:THREE.NormalBlending});
}
function shadowize(group){
  group.traverse(o=>{if(o.isMesh){o.castShadow=true;o.receiveShadow=true}});
  return group;
}
function extrudedPlanform(coords,mat,thickness=.16,y=0){
  const shape=new THREE.Shape();shape.moveTo(coords[0][0],coords[0][1]);
  for(let i=1;i<coords.length;i++)shape.lineTo(coords[i][0],coords[i][1]);
  shape.closePath();
  const geo=new THREE.ExtrudeGeometry(shape,{depth:thickness,bevelEnabled:true,bevelThickness:.035,bevelSize:.045,bevelSegments:2,curveSegments:1});
  geo.rotateX(Math.PI/2);
  const mesh=new THREE.Mesh(geo,mat);mesh.position.y=y-thickness*.5;return mesh;
}
function planform(coords,mat,y=0){return extrudedPlanform(coords,mat,.09,y)}
function fuselage(profile,mat,segments=32){
  const pts=profile.map(([z,r])=>new THREE.Vector2(r,z));
  const geo=new THREE.LatheGeometry(pts,segments);geo.rotateX(Math.PI/2);geo.computeVertexNormals();
  return new THREE.Mesh(geo,mat);
}
function canopy(scale,position,glass=physicalGlass()){
  const m=new THREE.Mesh(new THREE.SphereGeometry(1,32,18),glass);m.scale.set(...scale);m.position.set(...position);return m;
}
function verticalSurface(coords,mat,x=0){
  const shape=new THREE.Shape();shape.moveTo(coords[0][0],coords[0][1]);
  for(let i=1;i<coords.length;i++)shape.lineTo(coords[i][0],coords[i][1]);shape.closePath();
  const geo=new THREE.ExtrudeGeometry(shape,{depth:.11,bevelEnabled:true,bevelThickness:.025,bevelSize:.025,bevelSegments:1});
  geo.rotateY(Math.PI/2);
  const mesh=new THREE.Mesh(geo,mat);mesh.position.x=x;return mesh;
}
function pivotSurface(coords,mat,pivotX,pivotZ,y=.08,thickness=.11){
  const local=coords.map(([x,z])=>[x-pivotX,z-pivotZ]),pivot=new THREE.Group();
  pivot.position.set(pivotX,y,pivotZ);pivot.add(extrudedPlanform(local,mat,thickness,0));return pivot;
}
function engineFlame(radius,length,color=0x6eefff){
  const g=new THREE.Group();
  const outer=new THREE.Mesh(new THREE.ConeGeometry(radius,length,20,1,true),basic(color,.26));outer.rotation.x=Math.PI/2;outer.position.z=length*.48;
  const inner=new THREE.Mesh(new THREE.ConeGeometry(radius*.52,length*.7,16,1,true),basic(0xf2ffff,.55));inner.rotation.x=Math.PI/2;inner.position.z=length*.35;
  const ring=new THREE.Mesh(new THREE.TorusGeometry(radius*.86,.08,8,28),basic(color,.82));
  g.add(outer,inner,ring);g.userData={outer,inner,ring,baseLength:length};return g;
}
function trailAnchor(parent,x,y,z){const a=new THREE.Object3D();a.position.set(x,y,z);parent.add(a);return a}
function landingGear(skin,{mainX=2.2,mainZ=1.6,noseZ=-4.2,height=1.75}={}){
  const g=new THREE.Group(),strutMat=material(0x737c7e,{metalness:.78,roughness:.24}),rubber=material(0x15191a,{metalness:.05,roughness:.9});
  function leg(x,z,h=height,wheel=.34){
    const lg=new THREE.Group();
    const strut=new THREE.Mesh(new THREE.CylinderGeometry(.08,.10,h,10),strutMat);strut.position.y=-h*.5;lg.add(strut);
    const wh=new THREE.Mesh(new THREE.CylinderGeometry(wheel,wheel,.16,18),rubber);wh.rotation.z=Math.PI/2;wh.position.y=-h;lg.add(wh);
    lg.position.set(x,-.12,z);return lg;
  }
  g.add(leg(-mainX,mainZ),leg(mainX,mainZ),leg(0,noseZ,height*.78,.27));
  g.userData.deploy=0;g.scale.y=.001;g.visible=false;return g;
}
function navLight(color,intensity=2.2){
  const group=new THREE.Group();
  const lens=new THREE.Mesh(new THREE.SphereGeometry(.115,16,10),new THREE.MeshBasicMaterial({color,toneMapped:false}));
  const light=new THREE.PointLight(color,intensity,45,2);group.add(lens,light);return group;
}
function addNavigationLights(g,{span=8,tailZ=5,noseZ=-6}={}){
  const left=navLight(0xff2d2d,2.4),right=navLight(0x35ff8a,2.4),tail=navLight(0xffffff,1.7),beacon=navLight(0xff4433,1.3);
  left.position.set(-span*.48,.12,0);right.position.set(span*.48,.12,0);tail.position.set(0,.18,tailZ);beacon.position.set(0,.75,noseZ*.08);
  g.add(left,right,tail,beacon);g.userData.navLights={left,right,tail,beacon};return g.userData.navLights;
}
function addLandingLights(g,{x=1.3,z=-1.6}={}){
  const lights=[];
  for(const sx of [-1,1]){
    const lamp=new THREE.SpotLight(0xfff1d5,0,280,Math.PI/10,.55,1.5);
    lamp.position.set(sx*x,-.15,z);lamp.target.position.set(sx*x,-22,z-115);g.add(lamp,lamp.target);lights.push(lamp);
  }
  g.userData.landingLights=lights;return lights;
}
function addPanelMicrodetail(g){
  const lineMat=new THREE.LineBasicMaterial({color:0x9fb2b4,transparent:true,opacity:.10,depthWrite:false});
  const targets=[];
  g.traverse(o=>{
    if(!o.isMesh||o.material?.transparent||o.geometry?.type==='SphereGeometry'||o.geometry?.type==='TorusGeometry')return;
    if(!o.geometry?.attributes?.position||targets.length>=14)return;
    targets.push(o);
  });
  for(const target of targets){
    try{
      const edge=new THREE.LineSegments(new THREE.EdgesGeometry(target.geometry,38),lineMat);
      edge.renderOrder=2;target.add(edge);
    }catch{}
  }
}
function finalizeCraft(g,spec={}){
  Object.assign(g.userData,spec);
  g.userData.controls=g.userData.controls||{};
  g.userData.exhausts=g.userData.exhausts||[];
  g.userData.trailAnchors=g.userData.trailAnchors||[];
  g.userData.cameraDistance=g.userData.cameraDistance||36;
  g.userData.cameraHeight=g.userData.cameraHeight||12;
  g.userData.cameraLookAhead=g.userData.cameraLookAhead||62;
  if(!g.userData.navLights)addNavigationLights(g,{span:Math.max(6,spec.span||10),tailZ:spec.tailZ||5,noseZ:spec.noseZ||-6});
  if(!g.userData.landingLights)addLandingLights(g,{x:Math.max(.9,(spec.span||10)*.14),z:spec.landingZ||-1.5});
  addPanelMicrodetail(g);
  return shadowize(g);
}
function makeF16(){
  const g=new THREE.Group(),skin=material(0x7f8b8e,{metalness:.72,roughness:.27}),dark=material(0x30383a,{metalness:.58,roughness:.3});
  const body=fuselage([[-8.5,.05],[-7.8,.34],[-6.4,.62],[-3.8,.86],[.5,.92],[3.8,.70],[6.5,.44],[7.2,.08]],skin,36);g.add(body);
  g.add(extrudedPlanform([[-1.1,-3.5],[-5.9,-.3],[-5.2,1.65],[-1.0,1.3],[1.0,1.3],[5.2,1.65],[5.9,-.3],[1.1,-3.5]],skin,.19,.02));
  g.add(extrudedPlanform([[-.9,3.7],[-2.6,5.1],[-2.15,6.15],[0,5.55],[2.15,6.15],[2.6,5.1],[.9,3.7]],skin,.14,.09));
  g.add(verticalSurface([[3.0,0],[5.8,0],[5.1,3.15],[3.8,3.45]],skin,0));
  const canopyMesh=canopy([.72,.48,2.05],[0,.63,-3.4]);g.add(canopyMesh);
  const intake=new THREE.Mesh(new THREE.TorusGeometry(.54,.10,10,28),dark);intake.rotation.x=Math.PI/2;intake.position.set(0,-.2,-1.65);g.add(intake);
  const aL=pivotSurface([[-5.05,.7],[-2.6,.85],[-2.45,1.55],[-4.6,1.62]],skin,-2.55,1.1,.13);
  const aR=pivotSurface([[2.6,.85],[5.05,.7],[4.6,1.62],[2.45,1.55]],skin,2.55,1.1,.13);
  const elevator=pivotSurface([[-2.1,5.15],[-.3,5.0],[.3,5.0],[2.1,5.15],[1.95,5.85],[-1.95,5.85]],skin,0,5.15,.13);
  const rudderPivot=new THREE.Group();rudderPivot.position.set(0,0,5.0);const rudder=verticalSurface([[0,0],[1.1,0],[.55,2.8],[.05,3.0]],skin,0);rudder.position.z=-1.1;rudderPivot.add(rudder);
  g.add(aL,aR,elevator,rudderPivot);
  const gear=landingGear(skin,{mainX:2.0,mainZ:1.0,noseZ:-4.7,height:1.65});g.add(gear);
  const exhaust=engineFlame(.52,3.2,0x64dfff);exhaust.position.set(0,0,7.0);g.add(exhaust);
  const anchors=[trailAnchor(g,-3.8,.1,1.4),trailAnchor(g,3.8,.1,1.4)];
  return finalizeCraft(g,{label:'F-16',controls:{aileronL:aL,aileronR:aR,elevator,rudder:rudderPivot},gear,exhausts:[exhaust],trailAnchors:anchors,cameraDistance:31,cameraHeight:10,cameraLookAhead:52,span:9.96,tailZ:6.2,noseZ:-8.5});
}
function makeSR71(){
  const g=new THREE.Group(),skin=material(0x111719,{metalness:.82,roughness:.2}),dark=material(0x06090a,{metalness:.5,roughness:.35});
  const body=fuselage([[-13.8,.05],[-12.5,.28],[-9.5,.48],[-5,.58],[1,.55],[7,.40],[10,.08]],skin,36);g.add(body);
  g.add(extrudedPlanform([[-.8,-8],[-8.6,-1.5],[-7.7,4.4],[-3.1,8.2],[-1.0,8.2],[1.0,8.2],[3.1,8.2],[7.7,4.4],[8.6,-1.5],[.8,-8]],skin,.16,.01));
  const canopyMesh=canopy([.56,.28,2.35],[0,.42,-7.4],physicalGlass(0x7aa4ab));g.add(canopyMesh);
  const aL=pivotSurface([[-7.3,2.2],[-3.9,4.4],[-3.0,6.0],[-6.6,4.2]],skin,-3.65,4.15,.10);
  const aR=pivotSurface([[3.9,4.4],[7.3,2.2],[6.6,4.2],[3.0,6.0]],skin,3.65,4.15,.10);g.add(aL,aR);
  const exhausts=[],anchors=[];
  for(const x of [-3.15,3.15]){
    const nac=fuselage([[-5.4,.15],[-4.6,.56],[1,.72],[6.6,.66],[7.7,.22]],skin,24);nac.position.x=x;g.add(nac);
    const intake=new THREE.Mesh(new THREE.TorusGeometry(.7,.11,10,28),dark);intake.rotation.x=Math.PI/2;intake.position.set(x,0,-5.1);g.add(intake);
    const ex=engineFlame(.56,4.2,0x66e5ff);ex.position.set(x,0,7.65);g.add(ex);exhausts.push(ex);anchors.push(trailAnchor(g,x,0,7.4));
  }
  const rudderL=new THREE.Group(),rudderR=new THREE.Group();
  for(const [pivot,x] of [[rudderL,-2.45],[rudderR,2.45]]){
    pivot.position.set(x,0,5.7);const fin=verticalSurface([[0,0],[2.2,0],[1.5,2.3],[.3,2.75]],skin,0);fin.position.z=-2.2;pivot.add(fin);g.add(pivot);
  }
  const gear=landingGear(skin,{mainX:2.6,mainZ:3.4,noseZ:-8.0,height:1.85});g.add(gear);
  return finalizeCraft(g,{label:'SR-71',controls:{aileronL:aL,aileronR:aR,rudderL,rudderR},gear,exhausts,trailAnchors:anchors,cameraDistance:48,cameraHeight:15,cameraLookAhead:76,span:16.94,tailZ:9.8,noseZ:-13.8});
}
function makeX15(){
  const g=new THREE.Group(),skin=material(0x596469,{metalness:.72,roughness:.28}),dark=material(0x22292b,{metalness:.5,roughness:.4});
  g.add(fuselage([[-8.4,.04],[-7.5,.28],[-5.7,.56],[-1,.72],[4.1,.60],[6.2,.30],[6.8,.06]],skin,34));
  g.add(extrudedPlanform([[-.8,-2.7],[-4.4,.1],[-3.8,1.7],[-.9,1.25],[.9,1.25],[3.8,1.7],[4.4,.1],[.8,-2.7]],skin,.16,.02));
  g.add(extrudedPlanform([[-.7,4.1],[-2.25,5.2],[-1.9,6.15],[0,5.6],[1.9,6.15],[2.25,5.2],[.7,4.1]],skin,.13,.10));
  g.add(verticalSurface([[3.2,0],[5.7,0],[5.25,3.6],[4.1,3.9]],skin,0));
  const canopyMesh=canopy([.62,.35,1.7],[0,.5,-4.4],physicalGlass(0x89a6a7));g.add(canopyMesh);
  const aL=pivotSurface([[-3.7,.9],[-2.1,1.05],[-1.8,1.55],[-3.45,1.65]],skin,-2.05,1.2,.11);
  const aR=pivotSurface([[2.1,1.05],[3.7,.9],[3.45,1.65],[1.8,1.55]],skin,2.05,1.2,.11);
  const elevator=pivotSurface([[-1.9,5.05],[-.2,5.0],[.2,5.0],[1.9,5.05],[1.65,5.85],[-1.65,5.85]],skin,0,5.1,.11);
  g.add(aL,aR,elevator);
  const gear=landingGear(skin,{mainX:1.7,mainZ:1.8,noseZ:-4.9,height:1.55});g.add(gear);
  const exhaust=engineFlame(.69,4.4,0xff9d5c);exhaust.position.z=6.75;g.add(exhaust);
  const nozzle=new THREE.Mesh(new THREE.TorusGeometry(.68,.12,10,30),dark);nozzle.rotation.x=Math.PI/2;nozzle.position.z=6.65;g.add(nozzle);
  return finalizeCraft(g,{label:'X-15',controls:{aileronL:aL,aileronR:aR,elevator},gear,exhausts:[exhaust],trailAnchors:[trailAnchor(g,-2.1,.1,1.5),trailAnchor(g,2.1,.1,1.5)],cameraDistance:32,cameraHeight:10,cameraLookAhead:54,span:6.8,tailZ:6.1,noseZ:-8.4});
}
function makeEidolon(){
  const g=new THREE.Group(),shell=material(0x617b7c,{emissive:0x123b3a,emissiveIntensity:.48,metalness:.75,roughness:.17});
  const upper=new THREE.Mesh(new THREE.SphereGeometry(4.2,48,24),shell);upper.scale.set(1.8,.28,1.25);g.add(upper);
  const lower=new THREE.Mesh(new THREE.SphereGeometry(3.9,40,20),material(0x334f50,{metalness:.65,roughness:.22}));lower.scale.set(1.75,.20,1.2);lower.position.y=-.28;g.add(lower);
  const canopyMesh=canopy([1.7,.52,2.35],[0,.62,-1.05],physicalGlass(0x74d1d1));g.add(canopyMesh);
  const ring=new THREE.Mesh(new THREE.TorusGeometry(5.4,.16,12,96),basic(0x6fffe8,.68));ring.rotation.x=Math.PI/2;g.add(ring);
  const ring2=new THREE.Mesh(new THREE.TorusGeometry(4.25,.06,8,80),basic(0xc1fff4,.48));ring2.rotation.x=Math.PI/2;ring2.rotation.z=.4;g.add(ring2);
  const left=pivotSurface([[-7.0,-1.0],[-4.4,-.5],[-4.0,2.0],[-6.4,1.2]],shell,-4.2,.2,.02),right=pivotSurface([[4.4,-.5],[7.0,-1.0],[6.4,1.2],[4.0,2.0]],shell,4.2,.2,.02);g.add(left,right);
  const gear=landingGear(shell,{mainX:2.8,mainZ:1.4,noseZ:-2.6,height:1.45});g.add(gear);
  const exhaust=engineFlame(1.15,3.5,0x64ffe4);exhaust.position.z=4.0;g.add(exhaust);
  const anchors=[trailAnchor(g,-3.8,0,3.1),trailAnchor(g,3.8,0,3.1)];
  return finalizeCraft(g,{label:'EIDOLON',controls:{aileronL:left,aileronR:right},gear,exhausts:[exhaust],trailAnchors:anchors,cameraDistance:34,cameraHeight:11,cameraLookAhead:58,span:14.0,tailZ:4.2,noseZ:-5.2,animateVisual:dt=>{ring.rotation.z+=dt*.5;ring2.rotation.z-=dt*.82}});
}
function makeManta(){
  const g=new THREE.Group(),baseMat=material(0x447d78,{emissive:0x123d38,emissiveIntensity:.58,metalness:.48,roughness:.24,transparent:true,opacity:.66});
  const shell=extrudedPlanform([[0,-8.2],[4.4,-4.6],[8.3,-.4],[6.2,3.4],[2.6,5.9],[0,4.7],[-2.6,5.9],[-6.2,3.4],[-8.3,-.4],[-4.4,-4.6]],baseMat,.23,0);g.add(shell);
  const canopyMesh=canopy([1.25,.42,2.05],[0,.52,-2.2],physicalGlass(0x79d7cc));g.add(canopyMesh);
  const wingL=pivotSurface([[-8.0,-.3],[-5.0,1.2],[-4.2,3.6],[-6.4,3.0]],baseMat,-4.5,1.1,.08);
  const wingR=pivotSurface([[5.0,1.2],[8.0,-.3],[6.4,3.0],[4.2,3.6]],baseMat,4.5,1.1,.08);g.add(wingL,wingR);
  const pointPositions=new Float32Array(125*3),pointGeo=new THREE.BufferGeometry();pointGeo.setAttribute('position',new THREE.BufferAttribute(pointPositions,3));
  const pts=new THREE.Points(pointGeo,new THREE.PointsMaterial({color:0xbaffee,size:.48,sizeAttenuation:true,transparent:true,opacity:.95,depthWrite:false}));g.add(pts);
  const edges=[];for(let a=0;a<5;a++)for(let b=0;b<5;b++)for(let c=0;c<5;c++){const i=a*25+b*5+c;if(a<4)edges.push([i,i+25]);if(b<4)edges.push([i,i+5]);if(c<4)edges.push([i,i+1])}
  const linePositions=new Float32Array(edges.length*2*3),lineGeo=new THREE.BufferGeometry();lineGeo.setAttribute('position',new THREE.BufferAttribute(linePositions,3));
  const lines=new THREE.LineSegments(lineGeo,new THREE.LineBasicMaterial({color:0x72e9d9,transparent:true,opacity:.42,depthWrite:false}));g.add(lines);
  const gear=landingGear(baseMat,{mainX:2.5,mainZ:1.2,noseZ:-2.9,height:1.35});g.add(gear);
  const exL=engineFlame(.72,3.2,0x63ffe4),exR=engineFlame(.72,3.2,0x63ffe4);exL.position.set(-2.5,0,4.6);exR.position.set(2.5,0,4.6);g.add(exL,exR);
  Object.assign(g.userData,{label:'MANTA',shell,pointPositions,pointGeo,linePositions,lineGeo,edges,hasFrame:false});
  return finalizeCraft(g,{controls:{aileronL:wingL,aileronR:wingR},gear,exhausts:[exL,exR],trailAnchors:[trailAnchor(g,-2.5,0,4.5),trailAnchor(g,2.5,0,4.5)],cameraDistance:35,cameraHeight:11,cameraLookAhead:60,span:16.0,tailZ:5.0,noseZ:-8.2});
}
function makeSyntaxJacob(){
  const g=new THREE.Group(),shell=material(0x73749a,{emissive:0x2c245d,emissiveIntensity:.68,metalness:.68,roughness:.19});
  const body=fuselage([[-8.8,.03],[-7.2,.42],[-4.8,1.45],[-1.5,2.1],[2.2,1.65],[5.2,.72],[6.4,.08]],shell,8);body.scale.y=.65;g.add(body);
  g.add(extrudedPlanform([[0,-7.6],[-5.2,-2.1],[-6.8,1.6],[-3.2,3.9],[-1.2,5.0],[1.2,5.0],[3.2,3.9],[6.8,1.6],[5.2,-2.1]],shell,.22,0));
  const canopyMesh=canopy([1.3,.5,2.1],[0,.64,-3.6],physicalGlass(0x9e92df));g.add(canopyMesh);
  const r1=new THREE.Mesh(new THREE.TorusGeometry(5.6,.11,8,88),basic(0xb6a8ff,.78));r1.rotation.x=Math.PI/2;r1.position.z=.4;g.add(r1);
  const r2=new THREE.Mesh(new THREE.TorusGeometry(4.0,.07,8,72),basic(0x86fff0,.58));r2.rotation.x=Math.PI/2;r2.rotation.z=Math.PI/4;r2.position.z=.4;g.add(r2);
  const left=pivotSurface([[-6.5,.4],[-4.0,1.5],[-3.0,3.4],[-5.4,2.7]],shell,-3.8,1.4,.08),right=pivotSurface([[4.0,1.5],[6.5,.4],[5.4,2.7],[3.0,3.4]],shell,3.8,1.4,.08);g.add(left,right);
  const gear=landingGear(shell,{mainX:2.5,mainZ:1.7,noseZ:-4.5,height:1.45});g.add(gear);
  const exhaust=engineFlame(.95,4.0,0x9b8cff);exhaust.position.z=6.3;g.add(exhaust);
  return finalizeCraft(g,{label:'SYNTAX JACOB',controls:{aileronL:left,aileronR:right},gear,exhausts:[exhaust],trailAnchors:[trailAnchor(g,-2.7,0,4.5),trailAnchor(g,2.7,0,4.5)],cameraDistance:38,cameraHeight:12,cameraLookAhead:65,span:13.6,tailZ:6.2,noseZ:-8.8,animateVisual:dt=>{r1.rotation.z+=dt*.34;r2.rotation.z-=dt*.7}});
}
function makeFleet(){
  const models=[makeF16(),makeSR71(),makeX15(),makeEidolon(),makeManta(),makeSyntaxJacob()];
  models.forEach((m,i)=>{m.visible=i===0;m.name=CRAFT_NAMES[i]});return models;
}
function updateMantaModel(model,state){
  const geo=state?.geometry;if(!model||!Array.isArray(geo)||geo.length<375)return;
  const d=model.userData,scale=3.65;
  for(let i=0;i<125;i++){const j=i*3;d.pointPositions[j]=geo[j]*scale;d.pointPositions[j+1]=geo[j+1]*scale*2.1;d.pointPositions[j+2]=geo[j+2]*scale}
  d.pointGeo.attributes.position.needsUpdate=true;let k=0;
  for(const [a,b] of d.edges){
    const ia=a*3,ib=b*3;
    d.linePositions[k++]=d.pointPositions[ia];d.linePositions[k++]=d.pointPositions[ia+1];d.linePositions[k++]=d.pointPositions[ia+2];
    d.linePositions[k++]=d.pointPositions[ib];d.linePositions[k++]=d.pointPositions[ib+1];d.linePositions[k++]=d.pointPositions[ib+2];
  }
  d.lineGeo.attributes.position.needsUpdate=true;d.hasFrame=true;d.shell.material.opacity=.32;
}
function controlList(value){return !value?[]:Array.isArray(value)?value:[value]}
function driveControl(value,axis,target,rate,dt){
  for(const node of controlList(value)){
    if(!node?.rotation)continue;
    const bind=node.userData?.skyrmionBindRotation?.[axis]??0;
    const desired=bind+target;
    node.rotation[axis]+=(desired-node.rotation[axis])*Math.min(1,dt*rate);
  }
}
function updateCraftSystems(model,flight,dt,groundElevation=0){
  if(!model)return;
  const u=model.userData,c=u.controls||{},roll=clamp(Number(flight.roll||0),-.9,.9),pitch=clamp(Number(flight.pitch||0),-.55,.55),speed=Math.max(0,Number(flight.speed||0));
  driveControl(c.aileronL,'x',roll*.48,9,dt);
  driveControl(c.aileronR,'x',-roll*.48,9,dt);
  driveControl(c.elevator,'x',-pitch*.55,9,dt);
  driveControl(c.elevatorL,'x',-pitch*.55+roll*.16,9,dt);
  driveControl(c.elevatorR,'x',-pitch*.55-roll*.16,9,dt);
  const rudderTarget=roll*.16;
  for(const r of [c.rudder,c.rudderL,c.rudderR])driveControl(r,'y',rudderTarget,7,dt);
  const clearance=Number(flight.altitude_m||0)-Number(groundElevation||0),gearTarget=(Number(flight.domain||0)===0&&clearance<650&&speed<240)?1:0;
  const flapTarget=Number.isFinite(flight.flaps)?clamp(Number(flight.flaps),0,1):gearTarget*.42;
  driveControl(c.flapL,'x',flapTarget*.52,5,dt);
  driveControl(c.flapR,'x',flapTarget*.52,5,dt);
  driveControl(c.spoilerL,'x',Math.max(0,roll)*.34,7,dt);
  driveControl(c.spoilerR,'x',Math.max(0,-roll)*.34,7,dt);
  if(u.gear){
    u.gear.userData.deploy+=(gearTarget-u.gear.userData.deploy)*Math.min(1,dt*3.5);
    const d=u.gear.userData.deploy;u.gear.visible=d>.015;u.gear.scale.y=Math.max(.001,d);
  }
  for(const node of u.gearNodes||[])node.visible=gearTarget>.5;
  const thrust=clamp(.18+speed/420,.18,1.18);
  for(const ex of u.exhausts||[]){
    const pulse=.92+Math.sin(performance.now()*.025)*.08;
    ex.scale.set(1,1,thrust*pulse);ex.visible=speed>15;
    const outer=ex.userData.outer,inner=ex.userData.inner;
    if(outer)outer.material.opacity=.12+.2*clamp(thrust,0,1);
    if(inner)inner.material.opacity=.28+.35*clamp(thrust,0,1);
  }
  const lowAndSlow=Number(flight.domain||0)===0&&clearance<850&&speed<180;
  for(const lamp of u.landingLights||[])lamp.intensity+=( (lowAndSlow?22:0)-lamp.intensity)*Math.min(1,dt*6);
  if(u.navLights?.beacon)u.navLights.beacon.visible=(Math.floor(performance.now()/420)%2)===0;
  u.animationMixer?.update?.(dt);
  u.animateVisual?.(dt,flight);
}
function makeTrailSystem(scene){
  const MAX=150,geometry=new THREE.BufferGeometry(),positions=new Float32Array(MAX*2*3),colors=new Float32Array(MAX*2*3);
  geometry.setAttribute('position',new THREE.BufferAttribute(positions,3));geometry.setAttribute('color',new THREE.BufferAttribute(colors,3));
  const pointsMesh=new THREE.Points(geometry,new THREE.PointsMaterial({size:4.2,sizeAttenuation:true,transparent:true,opacity:.34,depthWrite:false,vertexColors:true,blending:THREE.AdditiveBlending}));
  scene.add(pointsMesh);
  let history=[[],[]],accum=0;
  function clear(){history=[[],[]];positions.fill(0);colors.fill(0);geometry.attributes.position.needsUpdate=true;geometry.attributes.color.needsUpdate=true}
  function update(model,flight,dt){
    accum+=dt;if(!model||accum<.055)return;accum=0;
    const anchors=model.userData.trailAnchors||[],speed=Number(flight.speed||0),alt=Number(flight.altitude_m||0),domain=Number(flight.domain||0);
    const emit=domain===0&&speed>120&&alt>1800;
    if(!emit){if(history[0].length||history[1].length){for(const h of history)if(h.length)h.pop();render()}return}
    for(let lane=0;lane<2;lane++){
      const a=anchors[lane]||anchors[0];if(!a)continue;
      const p=new THREE.Vector3();a.getWorldPosition(p);history[lane].unshift(p);if(history[lane].length>MAX)history[lane].length=MAX;
    }
    render();
  }
  function render(){
    for(let lane=0;lane<2;lane++){
      for(let i=0;i<MAX;i++){
        const idx=(lane*MAX+i)*3,p=history[lane][i];
        if(p){positions[idx]=p.x;positions[idx+1]=p.y;positions[idx+2]=p.z;const fade=1-i/MAX;colors[idx]=.55+.45*fade;colors[idx+1]=.72+.28*fade;colors[idx+2]=.82+.18*fade}
        else{positions[idx]=positions[idx+1]=positions[idx+2]=0;colors[idx]=colors[idx+1]=colors[idx+2]=0}
      }
    }
    geometry.attributes.position.needsUpdate=true;geometry.attributes.color.needsUpdate=true;
  }
  return {mesh:pointsMesh,update,clear};
}
function prepareLicensedRig(scene,meta,inspection,animations=[]){
  const rig=new THREE.Group();
  rig.add(scene);
  const box=new THREE.Box3().setFromObject(scene),size=new THREE.Vector3(),center=new THREE.Vector3();
  box.getSize(size);box.getCenter(center);
  const length=Math.max(size.x,size.z,6),width=Math.min(Math.max(size.x,size.z),length);
  const bindings=inspection?.bindings||{};
  const exhaust=engineFlame(Math.max(.35,width*.035),Math.max(2.4,length*.18),0x74e8ff);
  exhaust.position.set(0,0,length*.48);rig.add(exhaust);
  const left=trailAnchor(rig,-Math.max(1,width*.32),0,length*.20),right=trailAnchor(rig,Math.max(1,width*.32),0,length*.20);
  const controls={
    aileronL:bindings.aileronL||[],aileronR:bindings.aileronR||[],
    elevator:bindings.elevator||[],elevatorL:bindings.elevatorL||[],elevatorR:bindings.elevatorR||[],
    rudder:bindings.rudder||[],flapL:bindings.flapL||[],flapR:bindings.flapR||[],
    spoilerL:bindings.spoilerL||[],spoilerR:bindings.spoilerR||[]
  };
  const animationMixer=animations.length?new THREE.AnimationMixer(scene):null;
  if(animationMixer)for(const clip of animations)animationMixer.clipAction(clip).play();
  rig.userData={
    label:meta.label,licensed:true,licensedAssetId:meta.id,
    licensedBindings:bindings,controls,exhausts:[exhaust],trailAnchors:[left,right],
    cameraDistance:Math.max(75,length*5.2),cameraHeight:Math.max(24,length*1.4),cameraLookAhead:Math.max(130,length*7),
    gearNodes:bindings.gear||[],canopyNodes:bindings.canopy||[],sourceScene:scene,animationMixer,
    licenseAttribution:meta.label+' · '+meta.author+' · '+meta.license
  };
  return shadowize(rig);
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
  const scene=new THREE.Scene(),environmentTexture=makeEnvironmentTexture();scene.environment=environmentTexture;
  const atmos=makeSky(scene),space=makeSpace(scene),camera=new THREE.PerspectiveCamera(47,innerWidth/innerHeight,.25,30000);
  const craftRoot=new THREE.Group(),fleet=makeFleet();fleet.forEach(m=>craftRoot.add(m));scene.add(craftRoot);
  const trailSystem=makeTrailSystem(scene),shadowTarget=new THREE.Object3D();scene.add(shadowTarget);atmos.sun.target=shadowTarget;
  const flight={lat,lon,altitude_m,heading,pitch,roll,speed,active,domain:0,enabled:true};
  const chase={distance:36,height:12,lookAhead:62,damping:.105,bankMix:.38};
  const worldUp=new THREE.Vector3(0,1,0),forward=new THREE.Vector3(),right=new THREE.Vector3(),craftUp=new THREE.Vector3(),cameraUp=new THREE.Vector3();
  const desiredCamera=new THREE.Vector3(),desiredTarget=new THREE.Vector3(),smoothTarget=new THREE.Vector3(),basis=new THREE.Matrix4(),baseQ=new THREE.Quaternion(),rollQ=new THREE.Quaternion(),localRollAxis=new THREE.Vector3(0,0,-1);
  let patch=null,patchLoading=false,generation=0,destroyed=false,activeIndex=clamp(Number(active)||0,0,5),mantaState=null;
  const licensedAssetState={loaded:{},replacements:{},errors:{},audit:null,registry:null};
  async function licensedAPI(){
    const api=await getLicensedAssetModule();
    licensedAssetState.registry=api.LICENSED_AIRCRAFT_ASSETS;
    return api;
  }
  const quality={renderScale:1,dpr:Math.min(devicePixelRatio||1,maxDpr),shadowSize:1024,lastTelemetry:0};
  function applyQualityScale(next){
    const scale=clamp(Number(next??window.CITY_CINEMA_CODEC?.state?.scale??1),.5,1);
    quality.renderScale=scale;quality.dpr=Math.max(.65,Math.min((devicePixelRatio||1)*scale,maxDpr));
    renderer.setPixelRatio(quality.dpr);renderer.setSize(innerWidth,innerHeight,false);
    const shadowSize=scale<.64?512:scale<.9?1024:matchMedia('(max-width:800px)').matches?1024:2048;
    if(shadowSize!==quality.shadowSize){
      quality.shadowSize=shadowSize;atmos.sun.shadow.mapSize.set(shadowSize,shadowSize);
      atmos.sun.shadow.map?.dispose?.();atmos.sun.shadow.map=null;
    }
  }

  async function loadLicensedReference(assetId){
    if(licensedAssetState.loaded[assetId])return licensedAssetState.loaded[assetId];
    try{
      const {loadLicensedAircraft}=await licensedAPI();
      const loaded=await loadLicensedAircraft(assetId,{clone:true});
      const rig=prepareLicensedRig(loaded.scene,loaded.meta,loaded.inspection,loaded.gltf?.animations||[]);
      rig.visible=false;
      licensedAssetState.loaded[assetId]={...loaded,rig};
      return licensedAssetState.loaded[assetId];
    }catch(error){
      licensedAssetState.errors[assetId]=String(error?.message||error);
      throw error;
    }
  }
  async function replaceCraftWithLicensedAsset(slotIndex,assetId){
    const slot=clamp(Number(slotIndex)||0,0,fleet.length-1),craftName=CRAFT_NAMES[slot];
    const {canReplaceCraft,loadLicensedAircraft}=await licensedAPI();
    if(!canReplaceCraft(assetId,craftName))throw new Error(`Identity gate: ${assetId} is not licensed/registered as exact ${craftName}`);
    const loaded=await loadLicensedAircraft(assetId,{clone:true});
    const old=fleet[slot],rig=prepareLicensedRig(loaded.scene,loaded.meta,loaded.inspection,loaded.gltf?.animations||[]);
    rig.visible=slot===activeIndex;
    craftRoot.remove(old);craftRoot.add(rig);fleet[slot]=rig;
    licensedAssetState.replacements[craftName]=assetId;
    if(slot===activeIndex)trailSystem.clear();
    dispatchEvent(new CustomEvent('skyrmion:asset-replacement',{detail:{craftName,assetId,license:loaded.meta.license,author:loaded.meta.author}}));
    return {craftName,assetId,license:loaded.meta.license,author:loaded.meta.author};
  }
  async function runLicensedAssetAudit(){
    const {auditLicensedAssets}=await licensedAPI();
    const report=await auditLicensedAssets();
    licensedAssetState.audit=report;
    dispatchEvent(new CustomEvent('skyrmion:asset-audit',{detail:report}));
    return report;
  }
  function setActiveCraft(i){
    const next=clamp(Number(i)||0,0,fleet.length-1);if(next===activeIndex&&fleet[next].visible)return;
    activeIndex=next;fleet.forEach((m,j)=>m.visible=j===activeIndex);trailSystem?.clear?.();
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
      patch={center,span,world,terrain,buildings,clouds,lights,texture,min:field.min,max:field.max,centerElevation,
        heights:field.heights,samples:field.samples};trailSystem?.clear?.();
      updateDomainVisibility();
      dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:imgResult.status==='fulfilled'&&demResult.status==='fulfilled'?'LIVE':'DEGRADED',center,span,elevation_min_m:field.min,elevation_max_m:field.max}}));
    }catch(error){
      dispatchEvent(new CustomEvent('skyrmion:terrain-status',{detail:{status:'FALLBACK',error:String(error?.message||error)}}));
    }finally{if(gen===generation)patchLoading=false}
  }
  function samplePatchHeight(x,z){
    if(!patch?.heights||!patch?.samples||!patch?.span)return patch?.centerElevation||0;
    const n=patch.samples;
    const u=clamp(x/patch.span+.5,0,1)*(n-1);
    const v=clamp(.5-z/patch.span,0,1)*(n-1);
    const x0=Math.floor(u),x1=Math.min(n-1,x0+1),z0=Math.floor(v),z1=Math.min(n-1,z0+1);
    const tx=u-x0,tz=v-z0,h=patch.heights;
    const h00=h[z0*n+x0],h10=h[z0*n+x1],h01=h[z1*n+x0],h11=h[z1*n+x1];
    return (h00*(1-tx)+h10*tx)*(1-tz)+(h01*(1-tx)+h11*tx)*tz;
  }
  function updateDomainVisibility(){
    const d=Number(flight.domain||0),atmospheric=d===0;
    if(patch?.world)patch.world.visible=atmospheric;
    atmos.sky.visible=atmospheric;atmos.sun.visible=atmospheric;scene.fog=atmospheric?atmos.fog:null;
    space.stars.visible=!atmospheric;space.planet.visible=d===1;trailSystem.mesh.visible=atmospheric;
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
    const current=fleet[activeIndex],speedFactor=clamp(Number(flight.speed||0)/450,0,1),k=1-Math.pow(1-chase.damping,dt*60);
    craftUp.set(0,1,0).applyQuaternion(craftRoot.quaternion).normalize();
    cameraUp.copy(worldUp).lerp(craftUp,chase.bankMix).normalize();
    const baseDistance=current?.userData?.cameraDistance||chase.distance,baseHeight=current?.userData?.cameraHeight||chase.height,baseLook=current?.userData?.cameraLookAhead||chase.lookAhead;
    desiredCamera.copy(craftRoot.position).addScaledVector(forward,-(baseDistance+speedFactor*55)).addScaledVector(cameraUp,baseHeight+Math.max(0,Number(flight.pitch||0))*28);
    desiredTarget.copy(craftRoot.position).addScaledVector(forward,baseLook+speedFactor*85);
    camera.position.lerp(desiredCamera,k);smoothTarget.lerp(desiredTarget,k*1.15);camera.up.lerp(cameraUp,k*.85).normalize();camera.lookAt(smoothTarget);
    camera.fov+=(47+speedFactor*4-camera.fov)*k*.4;camera.updateProjectionMatrix();
  }
  let last=performance.now();
  function frame(now){
    if(destroyed)return;requestAnimationFrame(frame);
    const dt=Math.min(.033,Math.max(.001,(now-last)/1000));last=now;updateCamera(dt);
    const current=fleet[activeIndex],ground=samplePatchHeight(craftRoot.position.x,craftRoot.position.z);
    const clearance=Math.max(0,Number(flight.altitude_m||0)-ground),atmospheric=Number(flight.domain||0)===0;
    updateCraftSystems(current,flight,dt,ground);
    trailSystem.update(current,flight,dt);
    renderer.shadowMap.enabled=atmospheric&&clearance<6500&&quality.renderScale>.54;
    if(scene.fog)scene.fog.density=.000025+.000045*clamp(1-clearance/9000,0,1);
    shadowTarget.position.copy(craftRoot.position);
    atmos.sun.position.copy(craftRoot.position).add(new THREE.Vector3(-2200,3400,1700));
    atmos.sun.target.updateMatrixWorld();
    if(patch?.clouds)patch.clouds.rotation.y+=dt*.0018;
    renderer.render(scene,camera);
    if(now-quality.lastTelemetry>1000){
      quality.lastTelemetry=now;
      const info=renderer.info.render;
      dispatchEvent(new CustomEvent('skyrmion:render-stats',{detail:{
        schema:'SKYRMION-RENDER-STATS-1.0',calls:info.calls,triangles:info.triangles,points:info.points,lines:info.lines,
        dpr:quality.dpr,renderScale:quality.renderScale,shadowMap:renderer.shadowMap.enabled,shadowSize:quality.shadowSize,
        clearance_m:clearance,active:CRAFT_NAMES[activeIndex],licensedAssetId:current?.userData?.licensedAssetId||null
      }}));
    }
  }
  addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();applyQualityScale(quality.renderScale)});
  addEventListener('city:render-scale',e=>applyQualityScale(e.detail?.scale??window.CITY_CINEMA_CODEC?.state?.scale??1));
  await buildPatch(lat,lon,true);setActiveCraft(activeIndex);if(mantaState)updateMantaFrame(mantaState);updateFlightState(flight);updateCraftPose();
  applyQualityScale(window.CITY_CINEMA_CODEC?.state?.scale??1);
  const lab=new URLSearchParams(location.search).get('assetlab');
  if(lab==='audit')runLicensedAssetAudit().catch(()=>{});
  else if(lab)getLicensedAssetModule().then(api=>{
    if(!api.LICENSED_AIRCRAFT_ASSETS[lab])return;
    return loadLicensedReference(lab).then(v=>dispatchEvent(new CustomEvent('skyrmion:asset-reference-ready',{detail:{id:lab,meta:v.meta,stats:v.stats,inspection:{nodes:v.inspection.nodes.length,bindings:Object.fromEntries(Object.entries(v.inspection.bindings).map(([k,x])=>[k,x.length]))}}})));
  }).catch(()=>{});
  requestAnimationFrame(frame);
  return {
    schema:'SKYRMION-TERRAIN-3D-6.0',ready:true,renderer,scene,camera,craftRoot,fleet,
    get activeCraft(){return fleet[activeIndex]},get patch(){return patch},
    updateFlightState,updateMantaFrame,teleport,setActiveCraft,
    licensedAssetState,quality,getLicensedAssets:async()=>Object.keys((await licensedAPI()).LICENSED_AIRCRAFT_ASSETS),loadLicensedReference,replaceCraftWithLicensedAsset,runLicensedAssetAudit,samplePatchHeight,
    destroy(){destroyed=true;generation++;if(patch?.world)dispose(patch.world);fleet.forEach(dispose);environmentTexture.dispose?.();renderer.dispose();canvas.remove()}
  };
}
