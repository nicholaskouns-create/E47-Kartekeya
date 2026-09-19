import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';
import {clone as cloneSkeleton} from 'three/addons/utils/SkeletonUtils.js';

// SKYRMION-LICENSED-AIRCRAFT-ASSETS-2.0
// External assets are admitted only with an explicit model-level license/provenance record.
// An asset may replace a named fleet slot only when exactFor matches that slot AND runtimeUrl is authorized.

export const LICENSED_AIRCRAFT_ASSETS=Object.freeze({
  "f15-polyducky":Object.freeze({
    id:"f15-polyducky",label:"McDonnell Douglas F-15 Eagle",role:"fighter-reference",exactFor:"F-15",
    runtimeUrl:"https://cdn.jsdelivr.net/gh/srcejon/sdrangel-3d-models@main/f15.glb",
    source:"https://github.com/srcejon/sdrangel-3d-models/blob/main/f15.glb",
    author:"PolyDucky",original:"https://skfb.ly/6QWGp",license:"CC BY 4.0",
    licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"Redistributed by srcejon/sdrangel-3d-models; its LICENSE explicitly attributes f15.glb to PolyDucky under CC BY 4.0.",
    targetLength:19.4,status:"runtime-ready"
  }),
  "nasa-global-hawk":Object.freeze({
    id:"nasa-global-hawk",label:"NASA Global Hawk",role:"nasa-reference-airframe",exactFor:null,
    runtimeUrl:"https://assets.science.nasa.gov/content/dam/science/cds/3d/resources/model/global-hawk/Global%20Hawk.glb",
    source:"https://science.nasa.gov/3d-resources/global-hawk/",
    author:"NASA/Michael D. Carbajal",license:"NASA Media Usage Guidelines",
    licenseUrl:"https://www.nasa.gov/nasa-brand-center/images-and-media/",
    provenance:"Official NASA Science 3D Resource. NASA states that polygon data and texture maps used in 3D models generally are not subject to U.S. copyright; NASA should be acknowledged and endorsement must not be implied.",
    targetLength:14.5,status:"runtime-ready"
  }),
  "amvlab-a320":Object.freeze({
    id:"amvlab-a320",label:"Airbus A320",role:"airliner-reference",exactFor:"A320",
    runtimeUrl:"https://cdn.jsdelivr.net/gh/amvlab/aircraft-models@main/models/A320.glb",
    source:"https://github.com/amvlab/aircraft-models",author:"amvlab aircraft-models contributors",
    license:"CC BY 4.0",licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"amvlab/aircraft-models states that models and images are CC BY 4.0.",targetLength:37.6,status:"runtime-ready"
  }),
  "amvlab-b737-nologo":Object.freeze({
    id:"amvlab-b737-nologo",label:"B737 logo-free",role:"airliner-reference",exactFor:"B737",
    runtimeUrl:"https://cdn.jsdelivr.net/gh/amvlab/aircraft-models@main/models/B737_nologo.glb",
    source:"https://github.com/amvlab/aircraft-models",author:"amvlab aircraft-models contributors",
    license:"CC BY 4.0",licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"Logo-free model from amvlab/aircraft-models, licensed CC BY 4.0.",targetLength:39.5,status:"runtime-ready"
  }),
  "amvlab-evtol":Object.freeze({
    id:"amvlab-evtol",label:"amvlab eVTOL",role:"evtol-reference",exactFor:null,
    runtimeUrl:"https://cdn.jsdelivr.net/gh/amvlab/aircraft-models@main/models/EVTOL.glb",
    source:"https://github.com/amvlab/aircraft-models",author:"amvlab aircraft-models contributors",
    license:"CC BY 4.0",licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"amvlab/aircraft-models states that models and images are CC BY 4.0.",targetLength:12,status:"runtime-ready"
  }),
  "amvlab-drone":Object.freeze({
    id:"amvlab-drone",label:"amvlab Drone",role:"drone-reference",exactFor:null,
    runtimeUrl:"https://cdn.jsdelivr.net/gh/amvlab/aircraft-models@main/models/drone.glb",
    source:"https://github.com/amvlab/aircraft-models",author:"amvlab aircraft-models contributors",
    license:"CC BY 4.0",licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"amvlab/aircraft-models states that models and images are CC BY 4.0.",targetLength:4,status:"runtime-ready"
  }),
  "f16-cdesrocher":Object.freeze({
    id:"f16-cdesrocher",label:"F-16 Fighting Falcon",role:"exact-candidate",exactFor:"F-16",
    runtimeUrl:null,source:"https://sketchfab.com/3d-models/f-16-fighting-falcon-031debe8efad46dd9ba362604707ebb1",
    author:"cdesrocher",license:"CC BY",licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"Sketchfab model page identifies the downloadable model as Creative Commons Attribution. Download remains provider-controlled; SKYRMION does not bypass it.",
    targetLength:15.0,status:"license-verified-download-not-automated"
  }),
  "sr71-manilov":Object.freeze({
    id:"sr71-manilov",label:"Lockheed SR-71 Blackbird",role:"exact-candidate",exactFor:"SR-71",
    runtimeUrl:null,source:"https://sketchfab.com/3d-models/sr71-908985d8ec544638bcd661bc315597ad",
    author:"manilov.ap",license:"CC BY",licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"Sketchfab model page identifies the downloadable model as Creative Commons Attribution. Download remains provider-controlled; SKYRMION does not bypass it.",
    targetLength:32.7,status:"license-verified-download-not-automated"
  }),
  "x15-cmoreau":Object.freeze({
    id:"x15-cmoreau",label:"North American X-15",role:"exact-candidate",exactFor:"X-15",
    runtimeUrl:null,source:"https://sketchfab.com/3d-models/north-american-x-15-plane-bf491206ba844282949734b48b938c53",
    author:"cmoreau",license:"CC BY",licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"Sketchfab model page identifies the downloadable model as Creative Commons Attribution. Download remains provider-controlled; SKYRMION does not bypass it.",
    targetLength:15.2,status:"license-verified-download-not-automated"
  })
});

const cache=new Map();
const loader=new GLTFLoader();

const CONTROL_PATTERNS=Object.freeze({
  aileronL:[/aileron.*l(eft)?/i,/left.*aileron/i,/aileron_l/i,/l_aileron/i,/ail_l/i],
  aileronR:[/aileron.*r(ight)?/i,/right.*aileron/i,/aileron_r/i,/r_aileron/i,/ail_r/i],
  elevator:[/^elevator$/i,/elevator[^lr]/i,/stabilator/i,/horizontal.*tail/i,/elevon/i],
  elevatorL:[/elevator.*l(eft)?/i,/left.*elevator/i,/stabilator.*l/i],
  elevatorR:[/elevator.*r(ight)?/i,/right.*elevator/i,/stabilator.*r/i],
  rudder:[/rudder/i,/vertical.*tail.*control/i],
  flapL:[/flap.*l(eft)?/i,/left.*flap/i,/flap_l/i],
  flapR:[/flap.*r(ight)?/i,/right.*flap/i,/flap_r/i],
  spoilerL:[/spoiler.*l(eft)?/i,/left.*spoiler/i],
  spoilerR:[/spoiler.*r(ight)?/i,/right.*spoiler/i],
  gear:[/landing.*gear/i,/gear/i,/wheel/i],
  noseGear:[/nose.*gear/i,/front.*gear/i],
  mainGear:[/main.*gear/i],
  canopy:[/canopy/i,/cockpit.*glass/i,/windscreen/i,/windshield/i],
  nozzle:[/nozzle/i,/exhaust/i,/afterburner/i]
});

const nodeMatches=(name,patterns)=>patterns.some(r=>r.test(name||""));

function collectNamedNodes(scene){
  const nodes=[];
  scene.traverse(o=>nodes.push({name:o.name||"",type:o.type,object:o}));
  return nodes;
}

function bindNodes(scene){
  const nodes=collectNamedNodes(scene),bindings={};
  for(const [key,patterns] of Object.entries(CONTROL_PATTERNS)){
    bindings[key]=nodes.filter(n=>nodeMatches(n.name,patterns)).map(n=>n.object);
  }
  return {bindings,nodes:nodes.map(n=>({name:n.name,type:n.type}))};
}

function cloneAndTuneMaterials(scene){
  scene.traverse(o=>{
    if(!o.isMesh)return;
    o.castShadow=true;o.receiveShadow=true;
    const original=Array.isArray(o.material)?o.material:[o.material];
    const tuned=original.map(src=>{
      if(!src)return src;
      const m=src.clone(),name=(o.name+" "+(m.name||"")).toLowerCase();
      if(/canopy|glass|windscreen|windshield/.test(name)){
        m.transparent=true;m.opacity=Math.min(m.opacity??1,.58);m.depthWrite=false;
        if("roughness" in m)m.roughness=Math.min(m.roughness??.25,.14);
        if("metalness" in m)m.metalness=Math.min(m.metalness??0,.10);
        if("transmission" in m)m.transmission=Math.max(m.transmission??0,.12);
      }else{
        if("roughness" in m)m.roughness=THREE.MathUtils.clamp(m.roughness??.42,.14,.84);
        if("metalness" in m)m.metalness=THREE.MathUtils.clamp(m.metalness??.35,0,.90);
      }
      m.needsUpdate=true;return m;
    });
    o.material=Array.isArray(o.material)?tuned:tuned[0];
  });
}

function normalizeScene(scene,targetLength){
  scene.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(scene),size=new THREE.Vector3(),center=new THREE.Vector3();
  box.getSize(size);box.getCenter(center);
  const planar=Math.max(size.x,size.z,1e-6),scale=(targetLength||16)/planar;
  scene.scale.multiplyScalar(scale);scene.position.sub(center.multiplyScalar(scale));scene.updateMatrixWorld(true);
  const normalizedBox=new THREE.Box3().setFromObject(scene),normalizedSize=new THREE.Vector3();
  normalizedBox.getSize(normalizedSize);
  return {sourceSize:[size.x,size.y,size.z],scale,normalizedSize:[normalizedSize.x,normalizedSize.y,normalizedSize.z]};
}

function orientForward(scene){
  scene.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(scene),size=new THREE.Vector3();box.getSize(size);
  const dominant=size.x>size.z?"x":"z";
  if(dominant==="x")scene.rotation.y=-Math.PI/2;
  scene.updateMatrixWorld(true);return dominant;
}

function collectModelStats(scene,animations=[]){
  let meshes=0,skinnedMeshes=0,bones=0,vertices=0,triangles=0,materials=0,textures=0;
  const seenMaterials=new Set(),seenTextures=new Set();
  scene.traverse(o=>{
    if(o.isBone)bones++;
    if(!o.isMesh)return;
    meshes++;if(o.isSkinnedMesh)skinnedMeshes++;
    const g=o.geometry,position=g?.attributes?.position;
    if(position)vertices+=position.count;
    triangles+=g?.index?Math.floor(g.index.count/3):position?Math.floor(position.count/3):0;
    const mats=Array.isArray(o.material)?o.material:[o.material];
    for(const m of mats){
      if(!m||seenMaterials.has(m.uuid))continue;seenMaterials.add(m.uuid);materials++;
      for(const value of Object.values(m)){
        if(value?.isTexture&&!seenTextures.has(value.uuid)){seenTextures.add(value.uuid);textures++}
      }
    }
  });
  return {meshes,skinnedMeshes,bones,vertices,triangles,materials,textures,animations:animations.length};
}

function captureBindPose(bindings){
  for(const nodes of Object.values(bindings)){
    for(const node of nodes||[]){
      if(!node?.rotation)continue;
      node.userData.skyrmionBindRotation=node.userData.skyrmionBindRotation||{x:node.rotation.x,y:node.rotation.y,z:node.rotation.z};
    }
  }
}

export function validateAssetRecord(meta){
  const errors=[];
  if(!meta?.id)errors.push("missing id");
  if(!meta?.label)errors.push("missing label");
  if(!meta?.source)errors.push("missing source");
  if(!meta?.license)errors.push("missing license");
  if(!meta?.author)errors.push("missing author");
  if(meta?.status==="runtime-ready"&&!meta?.runtimeUrl)errors.push("runtime-ready without runtimeUrl");
  if(meta?.exactFor&&meta?.role==="exact-candidate"&&meta?.runtimeUrl)errors.push("exact candidate unexpectedly has automated URL; review provider terms");
  return {ok:errors.length===0,errors};
}

export function attributionFor(assetId){
  const a=LICENSED_AIRCRAFT_ASSETS[assetId];
  return a?a.label+" · "+a.author+" · "+a.license:null;
}

export function exactCandidateFor(craftName){
  return Object.values(LICENSED_AIRCRAFT_ASSETS).find(a=>a.exactFor===craftName&&a.role==="exact-candidate")||null;
}

export function runtimeReadyAssets(){
  return Object.values(LICENSED_AIRCRAFT_ASSETS).filter(a=>a.status==="runtime-ready"&&a.runtimeUrl);
}

export async function loadLicensedAircraft(assetId,{clone=false,timeoutMs=15000}={}){
  const meta=LICENSED_AIRCRAFT_ASSETS[assetId];
  if(!meta)throw new Error("Unknown licensed aircraft asset: "+assetId);
  const valid=validateAssetRecord(meta);
  if(!valid.ok)throw new Error("Invalid asset record "+assetId+": "+valid.errors.join(", "));
  if(!meta.runtimeUrl)throw new Error("Asset is provenance-registered but not runtime-downloadable: "+assetId);

  if(!cache.has(assetId)){
    cache.set(assetId,new Promise((resolve,reject)=>{
      let settled=false;
      const timer=setTimeout(()=>{if(!settled){settled=true;cache.delete(assetId);reject(new Error("GLB load timeout: "+assetId))}},timeoutMs);
      dispatchEvent(new CustomEvent("skyrmion:asset-load",{detail:{id:assetId,status:"loading",meta}}));
      loader.load(meta.runtimeUrl,gltf=>{
        if(settled)return;settled=true;clearTimeout(timer);
        const scene=gltf.scene||gltf.scenes?.[0];
        if(!scene){cache.delete(assetId);reject(new Error("GLB contains no scene: "+assetId));return}
        cloneAndTuneMaterials(scene);
        const sourceForward=orientForward(scene),normalization=normalizeScene(scene,meta.targetLength),inspection=bindNodes(scene);
        captureBindPose(inspection.bindings);
        const stats=collectModelStats(scene,gltf.animations||[]);
        scene.userData.licensedAsset={
          id:assetId,label:meta.label,role:meta.role,exactFor:meta.exactFor,author:meta.author,license:meta.license,
          licenseUrl:meta.licenseUrl,source:meta.source,sourceForward,normalization,stats,
          namedNodes:inspection.nodes.map(n=>n.name).filter(Boolean)
        };
        scene.userData.licensedBindings=inspection.bindings;
        dispatchEvent(new CustomEvent("skyrmion:asset-load",{detail:{id:assetId,status:"ready",meta,stats}}));
        resolve({scene,gltf,meta,inspection,stats});
      },xhr=>{
        if(!xhr?.total)return;
        dispatchEvent(new CustomEvent("skyrmion:asset-load",{detail:{id:assetId,status:"progress",progress:xhr.loaded/xhr.total,meta}}));
      },error=>{
        if(settled)return;settled=true;clearTimeout(timer);cache.delete(assetId);
        dispatchEvent(new CustomEvent("skyrmion:asset-load",{detail:{id:assetId,status:"error",error:String(error?.message||error),meta}}));
        reject(error);
      });
    }));
  }

  const loaded=await cache.get(assetId);
  if(!clone)return loaded;
  const scene=cloneSkeleton(loaded.scene);
  cloneAndTuneMaterials(scene);
  const inspection=bindNodes(scene);captureBindPose(inspection.bindings);
  scene.userData={...loaded.scene.userData,licensedBindings:inspection.bindings};
  return {...loaded,scene,inspection,stats:collectModelStats(scene,loaded.gltf.animations||[])};
}

export function canReplaceCraft(assetId,craftName){
  const meta=LICENSED_AIRCRAFT_ASSETS[assetId];
  return Boolean(meta?.runtimeUrl&&meta?.exactFor&&meta.exactFor===craftName);
}

export function releaseLicensedAsset(assetId){
  const existed=cache.has(assetId);cache.delete(assetId);return existed;
}

export async function auditLicensedAssets({timeoutMs=12000,includeCandidates=true}={}){
  const report={schema:"SKYRMION-LICENSED-ASSET-AUDIT-2.0",generatedAt:new Date().toISOString(),assets:{}};
  for(const [id,meta] of Object.entries(LICENSED_AIRCRAFT_ASSETS)){
    const validation=validateAssetRecord(meta);
    if(!meta.runtimeUrl){
      if(includeCandidates)report.assets[id]={ok:validation.ok,loadable:false,status:meta.status,license:meta.license,exactFor:meta.exactFor,validation};
      continue;
    }
    const start=performance.now();
    try{
      const result=await loadLicensedAircraft(id,{timeoutMs});
      report.assets[id]={ok:true,loadable:true,ms:Math.round(performance.now()-start),stats:result.stats,
        bindings:Object.fromEntries(Object.entries(result.inspection.bindings).map(([k,v])=>[k,v.length])),
        license:result.meta.license,exactFor:result.meta.exactFor,validation};
    }catch(error){
      report.assets[id]={ok:false,loadable:true,ms:Math.round(performance.now()-start),error:String(error?.message||error),
        license:meta.license,exactFor:meta.exactFor,validation};
    }
  }
  return report;
}
