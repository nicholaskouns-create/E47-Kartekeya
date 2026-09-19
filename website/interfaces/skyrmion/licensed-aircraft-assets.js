import * as THREE from 'three';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

export const LICENSED_AIRCRAFT_ASSETS={
  "f15-polyducky":{
    id:"f15-polyducky",
    label:"McDonnell Douglas F-15 Eagle",
    role:"fighter-reference",
    exactFor:"F-15",
    runtimeUrl:"https://cdn.jsdelivr.net/gh/srcejon/sdrangel-3d-models@main/f15.glb",
    source:"https://github.com/srcejon/sdrangel-3d-models/blob/main/f15.glb",
    author:"PolyDucky",
    original:"https://skfb.ly/6QWGp",
    license:"CC BY 4.0",
    licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"Redistributed by srcejon/sdrangel-3d-models; its LICENSE explicitly attributes f15.glb to PolyDucky under CC BY 4.0.",
    targetLength:19.4,
    forward:"auto"
  },
  "amvlab-a320":{
    id:"amvlab-a320",
    label:"Airbus A320",
    role:"airliner-reference",
    exactFor:"A320",
    runtimeUrl:"https://cdn.jsdelivr.net/gh/amvlab/aircraft-models@main/models/A320.glb",
    source:"https://github.com/amvlab/aircraft-models",
    author:"amvlab aircraft-models contributors",
    license:"CC BY 4.0",
    licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"amvlab/aircraft-models states that models and images are CC BY 4.0.",
    targetLength:37.6,
    forward:"auto"
  },
  "amvlab-evtol":{
    id:"amvlab-evtol",
    label:"amvlab eVTOL",
    role:"evtol-reference",
    exactFor:null,
    runtimeUrl:"https://cdn.jsdelivr.net/gh/amvlab/aircraft-models@main/models/EVTOL.glb",
    source:"https://github.com/amvlab/aircraft-models",
    author:"amvlab aircraft-models contributors",
    license:"CC BY 4.0",
    licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"amvlab/aircraft-models states that models and images are CC BY 4.0.",
    targetLength:12,
    forward:"auto"
  },
  "amvlab-drone":{
    id:"amvlab-drone",
    label:"amvlab Drone",
    role:"drone-reference",
    exactFor:null,
    runtimeUrl:"https://cdn.jsdelivr.net/gh/amvlab/aircraft-models@main/models/drone.glb",
    source:"https://github.com/amvlab/aircraft-models",
    author:"amvlab aircraft-models contributors",
    license:"CC BY 4.0",
    licenseUrl:"https://creativecommons.org/licenses/by/4.0/",
    provenance:"amvlab/aircraft-models states that models and images are CC BY 4.0.",
    targetLength:4,
    forward:"auto"
  }
};

const cache=new Map();
const loader=new GLTFLoader();

const CONTROL_PATTERNS={
  aileronL:[/aileron.*l(eft)?/i,/left.*aileron/i,/aileron_l/i,/l_aileron/i],
  aileronR:[/aileron.*r(ight)?/i,/right.*aileron/i,/aileron_r/i,/r_aileron/i],
  elevator:[/elevator/i,/stabilator/i,/horizontal.*tail/i],
  rudder:[/rudder/i,/vertical.*tail/i],
  gear:[/landing.*gear/i,/gear/i,/wheel/i],
  canopy:[/canopy/i,/cockpit.*glass/i,/windscreen/i,/windshield/i],
  nozzle:[/nozzle/i,/exhaust/i,/afterburner/i]
};

function nodeMatches(name,patterns){return patterns.some(r=>r.test(name||""))}
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
function tuneMaterials(scene){
  scene.traverse(o=>{
    if(!o.isMesh)return;
    o.castShadow=true;o.receiveShadow=true;
    const mats=Array.isArray(o.material)?o.material:[o.material];
    for(const m of mats){
      if(!m)continue;
      const name=(o.name+" "+(m.name||"")).toLowerCase();
      if(/canopy|glass|windscreen|windshield/.test(name)){
        m.transparent=true;m.opacity=Math.min(m.opacity??1,.58);m.depthWrite=false;
        if("roughness" in m)m.roughness=Math.min(m.roughness??.25,.16);
        if("metalness" in m)m.metalness=Math.min(m.metalness??0,.12);
      }else{
        if("roughness" in m)m.roughness=THREE.MathUtils.clamp(m.roughness??.42,.16,.82);
        if("metalness" in m)m.metalness=THREE.MathUtils.clamp(m.metalness??.35,0,.88);
      }
      m.needsUpdate=true;
    }
  });
}
function normalizeScene(scene,targetLength){
  scene.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(scene),size=new THREE.Vector3(),center=new THREE.Vector3();
  box.getSize(size);box.getCenter(center);
  const longest=Math.max(size.x,size.y,size.z,1e-6);
  const scale=(targetLength||16)/longest;
  scene.scale.multiplyScalar(scale);
  scene.position.sub(center.multiplyScalar(scale));
  scene.updateMatrixWorld(true);
  const normalizedBox=new THREE.Box3().setFromObject(scene),normalizedSize=new THREE.Vector3();
  normalizedBox.getSize(normalizedSize);
  return {sourceSize:[size.x,size.y,size.z],scale,normalizedSize:[normalizedSize.x,normalizedSize.y,normalizedSize.z]};
}
function orientForward(scene){
  scene.updateMatrixWorld(true);
  const box=new THREE.Box3().setFromObject(scene),size=new THREE.Vector3();box.getSize(size);
  const dominant=size.x>size.z?"x":"z";
  if(dominant==="x")scene.rotation.y=-Math.PI/2;
  scene.updateMatrixWorld(true);
  return dominant;
}

export function attributionFor(assetId){
  const a=LICENSED_AIRCRAFT_ASSETS[assetId];
  if(!a)return null;
  return `${a.label} · ${a.author} · ${a.license}`;
}

export async function loadLicensedAircraft(assetId,{clone=false}={}){
  const meta=LICENSED_AIRCRAFT_ASSETS[assetId];
  if(!meta)throw new Error("Unknown licensed aircraft asset: "+assetId);
  if(!cache.has(assetId)){
    cache.set(assetId,new Promise((resolve,reject)=>{
      loader.load(meta.runtimeUrl,gltf=>{
        const scene=gltf.scene||gltf.scenes?.[0];
        if(!scene){reject(new Error("GLB contains no scene: "+assetId));return}
        tuneMaterials(scene);
        const sourceForward=orientForward(scene);
        const normalization=normalizeScene(scene,meta.targetLength);
        const inspection=bindNodes(scene);
        scene.userData.licensedAsset={
          id:assetId,label:meta.label,role:meta.role,exactFor:meta.exactFor,
          author:meta.author,license:meta.license,licenseUrl:meta.licenseUrl,
          source:meta.source,sourceForward,normalization,
          namedNodes:inspection.nodes.map(n=>n.name).filter(Boolean)
        };
        scene.userData.licensedBindings=inspection.bindings;
        resolve({scene,gltf,meta,inspection});
      },undefined,reject);
    }));
  }
  const loaded=await cache.get(assetId);
  if(!clone)return loaded;
  const scene=loaded.scene.clone(true);
  tuneMaterials(scene);
  const inspection=bindNodes(scene);
  scene.userData={...loaded.scene.userData,licensedBindings:inspection.bindings};
  return {...loaded,scene,inspection};
}

export function canReplaceCraft(assetId,craftName){
  const meta=LICENSED_AIRCRAFT_ASSETS[assetId];
  return Boolean(meta?.exactFor&&meta.exactFor===craftName);
}

export async function auditLicensedAssets({timeoutMs=9000}={}){
  const report={schema:"SKYRMION-LICENSED-ASSET-AUDIT-1.0",assets:{}};
  for(const id of Object.keys(LICENSED_AIRCRAFT_ASSETS)){
    const start=performance.now();
    try{
      const result=await Promise.race([
        loadLicensedAircraft(id),
        new Promise((_,reject)=>setTimeout(()=>reject(new Error("timeout")),timeoutMs))
      ]);
      report.assets[id]={
        ok:true,ms:Math.round(performance.now()-start),
        nodes:result.inspection.nodes.length,
        bindings:Object.fromEntries(Object.entries(result.inspection.bindings).map(([k,v])=>[k,v.length])),
        license:result.meta.license,exactFor:result.meta.exactFor
      };
    }catch(error){
      report.assets[id]={ok:false,ms:Math.round(performance.now()-start),error:String(error?.message||error)};
    }
  }
  return report;
}
