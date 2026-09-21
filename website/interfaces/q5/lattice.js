import * as THREE from 'three';

const RAW = 'https://raw.githubusercontent.com/nicholaskouns-create/E47-Kartekeya/main/q5/cells.jsonl';
const HUB = 'https://www.notion.so/3e246094fd308151966ae74dedb2976a';

function roleOf(x,y,z){
  const on = (c) => c===0 || c===4;
  const n = Number(on(x))+Number(on(y))+Number(on(z));
  return n===3?'corner':n===2?'edge':n===1?'face':'core';
}
function hex(role){
  return role==='corner'?'#d7e7de':role==='edge'?'#b7cfc2':role==='face'?'#8eaa9b':'#3e4a44';
}
function tex(cell){
  const c = document.createElement('canvas');
  c.width=128; c.height=128;
  const g=c.getContext('2d');
  const bg=hex(cell.role);
  g.fillStyle=bg; g.fillRect(0,0,128,128);
  g.strokeStyle=(cell.i===47||cell.i===78)?'#eef2ee':'rgba(9,11,10,.18)';
  g.lineWidth=(cell.i===47||cell.i===78)?8:2;
  g.strokeRect(4,4,120,120);
  g.fillStyle=cell.role==='core'?'#c5ddd0':'#090b0a';
  g.font="600 42px ui-monospace,monospace";
  g.textAlign='center'; g.textBaseline='middle';
  g.fillText(cell.word,64,58);
  g.font="500 16px ui-monospace,monospace";
  g.fillStyle=cell.role==='core'?'#9db8a8':'rgba(9,11,10,.45)';
  g.fillText(String(cell.i),64,92);
  const t=new THREE.CanvasTexture(c);
  t.colorSpace=THREE.SRGBColorSpace;
  return t;
}
async function loadJSONL(url){
  const res=await fetch(url);
  if(!res.ok) throw new Error(url);
  return (await res.text()).trim().split('\n').map((line)=>JSON.parse(line));
}
async function loadCells(){
  try{ return await loadJSONL('./cells.jsonl'); }
  catch{ return await loadJSONL(RAW); }
}
async function loadSlots(){
  try{
    const res=await fetch('./slots.json');
    if(!res.ok) return {};
    return await res.json();
  }catch{ return {}; }
}

const canvas=document.getElementById('stage');
const wordEl=document.getElementById('word');
const walkBtn=document.getElementById('walk');
const peelBtn=document.getElementById('peel');
const gh=document.getElementById('github');
const no=document.getElementById('notion');

const renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:false});
renderer.setPixelRatio(Math.min(devicePixelRatio,2));
renderer.setClearColor(0x090b0d,1);
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(38,1,0.1,80);
camera.position.set(7.4,6.2,8.6);
const group=new THREE.Group();
scene.add(group);
scene.add(new THREE.AmbientLight(0xb7c4bc,0.55));
const key=new THREE.DirectionalLight(0xe7eee9,1.05);
key.position.set(4,7,5); scene.add(key);
const fill=new THREE.DirectionalLight(0x6edfd4,0.22);
fill.position.set(-5,-2,-3); scene.add(fill);

let cells=[], meshes=[], selected=62, playing=true, peeled=false, rx=0.38, ry=0.72;
let slots={};
const GAP=0.18, SIZE=0.86;

function home(cell, explode){
  const s=1+GAP+explode*0.72;
  return new THREE.Vector3((cell.x-2)*s,(cell.y-2)*s,(cell.z-2)*(s+explode*0.9));
}
function bind(cell){
  wordEl.textContent=cell.word;
  gh.href=`https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/q5/cells.jsonl#L${cell.i+1}`;
  no.href=slots[cell.word]||HUB;
  no.textContent=`Notion ${cell.word}`;
}
function layout(){
  const explode=peeled?1:0;
  for(const cell of cells){
    const m=meshes[cell.i];
    const p=home(cell,explode);
    m.position.copy(p);
    const hot=cell.i===selected;
    m.scale.setScalar(hot?1.16:1);
  }
  bind(cells[selected]);
}
function resize(){
  const w=innerWidth,h=innerHeight;
  renderer.setSize(w,h,false);
  camera.aspect=w/h; camera.updateProjectionMatrix();
}

const ray=new THREE.Raycaster();
const ptr=new THREE.Vector2();
function pick(ev){
  const r=canvas.getBoundingClientRect();
  ptr.x=((ev.clientX-r.left)/r.width)*2-1;
  ptr.y=-((ev.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(meshes,false)[0];
  if(!hit) return;
  selected=hit.object.userData.i;
  playing=false; walkBtn.textContent='Walk';
  layout();
}

let drag=false,px=0,py=0;
canvas.addEventListener('pointerdown',(e)=>{drag=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener('pointerup',(e)=>{
  const moved=Math.hypot(e.clientX-px,e.clientY-py);
  drag=false;
  if(moved<6) pick(e);
});
canvas.addEventListener('pointermove',(e)=>{
  if(!drag) return;
  ry+=(e.clientX-px)*0.005;
  rx+=(e.clientY-py)*0.005;
  rx=Math.max(-1.2,Math.min(1.2,rx));
  px=e.clientX; py=e.clientY;
});
canvas.addEventListener('wheel',(e)=>{
  e.preventDefault();
  const z=camera.position.length()*(e.deltaY>0?1.06:0.94);
  camera.position.setLength(Math.max(6,Math.min(18,z)));
},{passive:false});

walkBtn.onclick=()=>{playing=!playing; walkBtn.textContent=playing?'Pause':'Walk'; walkBtn.classList.toggle('on',playing);};
peelBtn.onclick=()=>{peeled=!peeled; peelBtn.classList.toggle('on',peeled); layout();};

let acc=0;
function tick(t){
  const now=t*0.001;
  if(!tick.t) tick.t=now;
  const dt=now-tick.t; tick.t=now;
  if(playing){
    acc+=dt;
    if(acc>0.9){ acc=0; selected=(selected+1)%125; layout(); }
  }
  group.rotation.set(rx,ry,0);
  const pulse=playing?1.14+0.06*Math.sin(now*5):1.16;
  if(meshes[selected]) meshes[selected].scale.setScalar(pulse);
  renderer.render(scene,camera);
  requestAnimationFrame(tick);
}

const [rows, slotMap]=await Promise.all([loadCells(), loadSlots()]);
slots=slotMap;
if(rows.length!==125) throw new Error('ledger must be 125 words');
cells=rows.map((row)=>({
  ...row,
  role:roleOf(row.x,row.y,row.z),
  m:[row.x-2,row.y-2,row.z-2],
}));
const geo=new THREE.BoxGeometry(SIZE,SIZE,SIZE);
for(const cell of cells){
  const mat=new THREE.MeshLambertMaterial({map:tex(cell)});
  const mesh=new THREE.Mesh(geo,mat);
  mesh.userData.i=cell.i;
  group.add(mesh);
  meshes[cell.i]=mesh;
}
layout();
resize();
addEventListener('resize',resize);
walkBtn.classList.add('on');
requestAnimationFrame(tick);
