#!/usr/bin/env python3
"""Q5 host — one pass.

Validate the frozen 125-word ledger, emit the GitHub Pages cube from
codec + cells.jsonl + onsite three.js, and serve it.

    python q5/host.py           # validate + emit into website/
    python q5/host.py serve     # emit, then host website/ on :8000
    python q5/host.py check     # validator only

No new operator. The cube is the packing map. Certificates are rows later.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import codec  # noqa: E402
import validator  # noqa: E402

GITHUB_RAW = "https://raw.githubusercontent.com/nicholaskouns-create/E47-Kartekeya/main/q5"
PAGES_CUBE = "https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/"
NOTION_HUB = "https://www.notion.so/3e246094fd308151966ae74dedb2976a"
THREE_ONSITE = "../../vendor/three.module.js"
THREE_CDN = "https://cdn.jsdelivr.net/npm/three@0.180.0/build/three.module.js"


def repo_root(start: Path | None = None) -> Path:
    cur = (start or HERE).resolve()
    for p in [cur, *cur.parents]:
        if (p / "website" / "index.html").is_file() and (p / "q5").is_dir():
            return p
    return HERE.parent


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover" />
  <meta name="theme-color" content="#090b0d" />
  <title>Q5 · 125-word ledger</title>
  <meta name="description" content="Interactive 5×5×5 Q5 packing map with cube/torus adjacency. π(x,y,z)=25x+5y+z." />
  <link rel="canonical" href="https://nicholaskouns-create.github.io/E47-Kartekeya/interfaces/q5/" />
  <script type="importmap">{"imports":{"three":"../../vendor/three.module.js"}}</script>
  <style>
    :root{--bg:#090b0d;--panel:rgba(10,14,13,.88);--fg:#e7eee9;--muted:#8a9790;--line:#24302b;--live:#6edfd4;--lock:#c1e8ce}
    *{box-sizing:border-box}
    html,body{margin:0;height:100%;background:var(--bg);color:var(--fg);font:14px/1.4 "IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;overflow:hidden}
    canvas{display:block;width:100%;height:100%}
    .word{position:absolute;top:16px;left:16px;font:500 36px/1 "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.12em;color:var(--live);text-shadow:0 0 24px rgba(110,223,212,.18)}
    .state{position:absolute;top:62px;left:16px;display:grid;gap:3px;max-width:min(720px,72vw);padding:9px 11px;border:1px solid var(--line);border-radius:10px;background:var(--panel);backdrop-filter:blur(12px);font:500 11px/1.4 "IBM Plex Mono",ui-monospace,monospace;color:var(--muted)}
    .state .live{color:var(--live)} .state .lock{color:var(--lock)}
    .links{position:absolute;top:16px;right:16px;display:flex;gap:8px;flex-wrap:wrap;justify-content:flex-end;max-width:48%}
    a.quiet{color:var(--muted);font:12px "IBM Plex Mono",ui-monospace,monospace;text-decoration:none}
    .controls{position:absolute;left:50%;bottom:max(12px,env(safe-area-inset-bottom));transform:translateX(-50%);display:grid;gap:6px;width:min(1040px,calc(100vw - 20px))}
    .bar{display:flex;gap:6px;align-items:center;overflow-x:auto;padding:7px;border:1px solid var(--line);border-radius:12px;background:var(--panel);backdrop-filter:blur(12px);scrollbar-width:none}
    .bar::-webkit-scrollbar{display:none}
    button,a.chip,span.chip{min-height:42px;border:1px solid var(--line);background:#111614;color:var(--fg);border-radius:9px;padding:8px 11px;font:500 11px "IBM Plex Mono",ui-monospace,monospace;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;white-space:nowrap;cursor:pointer}
    button.on,a.chip.on{border-color:var(--live);color:var(--live)}
    button:disabled{opacity:.32;cursor:not-allowed}
    span.chip{cursor:default;color:var(--muted)}
    .step{min-width:72px}
    @media(max-width:700px){
      .word{font-size:30px}
      .state{top:56px;max-width:calc(100vw - 32px);font-size:10px}
      .links{top:18px}.links a:not(:first-child){display:none}
      .controls{bottom:max(8px,env(safe-area-inset-bottom));width:calc(100vw - 12px);gap:4px}
      .bar{padding:5px;gap:5px}
      button,a.chip,span.chip{min-height:40px;padding:7px 9px;font-size:10px}
      .step{min-width:66px}
    }
  </style>
</head>
<body>
  <canvas id="stage"></canvas>
  <div class="word" id="word">---</div>
  <div class="state" aria-live="polite">
    <span id="indexReadout">i = ---</span>
    <span id="coordReadout">xyz = ---</span>
    <span id="magReadout">m = ---</span>
    <span id="topologyReadout" class="live">topology = cube</span>
    <span id="neighborReadout" class="lock">neighbors = ---</span>
  </div>
  <div class="links">
    <a class="quiet" href="../../index.html">CITY</a>
    <a class="quiet" href="https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/q5/cells.jsonl">cells.jsonl</a>
    <a class="quiet" href="https://www.notion.so/3e246094fd308151966ae74dedb2976a">Notion ledger</a>
  </div>
  <div class="controls">
    <div class="bar">
      <button type="button" id="walk" class="on">Pause</button>
      <button type="button" id="peel">Peel</button>
      <button type="button" id="topology">Topology · cube</button>
      <button type="button" class="step" data-axis="x" data-dir="-1">−X</button>
      <button type="button" class="step" data-axis="x" data-dir="1">+X</button>
      <button type="button" class="step" data-axis="y" data-dir="-1">−Y</button>
      <button type="button" class="step" data-axis="y" data-dir="1">+Y</button>
      <button type="button" class="step" data-axis="z" data-dir="-1">−Z</button>
      <button type="button" class="step" data-axis="z" data-dir="1">+Z</button>
    </div>
    <div class="bar">
      <button type="button" id="sliceAxis">Slice · all</button>
      <button type="button" id="slicePrev" disabled>− slice</button>
      <span class="chip" id="sliceValue">all</span>
      <button type="button" id="sliceNext" disabled>+ slice</button>
      <a class="chip" id="github" href="https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/q5/cells.jsonl">GitHub</a>
      <a class="chip" id="notion" href="https://www.notion.so/3e246094fd308151966ae74dedb2976a">Notion</a>
    </div>
  </div>
  <script type="module" src="./lattice.js"></script>
</body>
</html>
"""

LATTICE_JS = r"""import * as THREE from 'three';
import {RADIX,DIM,CELLS as TOPO_CELLS,pi,neighbors,stepAxis,sliceCells} from './topology.mjs';

const RAW = 'https://raw.githubusercontent.com/nicholaskouns-create/E47-Kartekeya/main/q5/cells.jsonl';
const HUB = 'https://www.notion.so/3e246094fd308151966ae74dedb2976a';

function hex(role){
  return role==='corner'?'#d7e7de':role==='edge'?'#b7cfc2':role==='face'?'#8eaa9b':'#3e4a44';
}
function tex(cell){
  const c=document.createElement('canvas');
  c.width=128;c.height=128;
  const g=c.getContext('2d');
  g.fillStyle=hex(cell.role);g.fillRect(0,0,128,128);
  g.strokeStyle=(cell.i===47||cell.i===78)?'#eef2ee':'rgba(9,11,10,.18)';
  g.lineWidth=(cell.i===47||cell.i===78)?8:2;
  g.strokeRect(4,4,120,120);
  g.fillStyle=cell.role==='core'?'#c5ddd0':'#090b0a';
  g.font='600 42px ui-monospace,monospace';
  g.textAlign='center';g.textBaseline='middle';
  g.fillText(cell.word,64,58);
  g.font='500 16px ui-monospace,monospace';
  g.fillStyle=cell.role==='core'?'#9db8a8':'rgba(9,11,10,.45)';
  g.fillText(String(cell.i),64,92);
  const t=new THREE.CanvasTexture(c);
  t.colorSpace=THREE.SRGBColorSpace;
  return t;
}
async function loadJSONL(url){
  const res=await fetch(url);
  if(!res.ok)throw new Error(url);
  return (await res.text()).trim().split('\n').map((line)=>JSON.parse(line));
}
async function loadCells(){
  try{return await loadJSONL('./cells.jsonl');}
  catch{return await loadJSONL(RAW);}
}
async function loadSlots(){
  try{
    const res=await fetch('./slots.json');
    if(!res.ok)return {};
    return await res.json();
  }catch{return {};}
}
function assertLedger(rows){
  if(rows.length!==DIM)throw new Error('ledger must be 125 words');
  for(const row of rows){
    const cell=TOPO_CELLS[row.i];
    if(!cell||cell.x!==row.x||cell.y!==row.y||cell.z!==row.z||cell.word!==row.word){
      throw new Error('ledger/topology mismatch at i='+String(row.i));
    }
  }
}

const canvas=document.getElementById('stage');
const wordEl=document.getElementById('word');
const indexReadout=document.getElementById('indexReadout');
const coordReadout=document.getElementById('coordReadout');
const magReadout=document.getElementById('magReadout');
const topologyReadout=document.getElementById('topologyReadout');
const neighborReadout=document.getElementById('neighborReadout');
const walkBtn=document.getElementById('walk');
const peelBtn=document.getElementById('peel');
const topologyBtn=document.getElementById('topology');
const sliceAxisBtn=document.getElementById('sliceAxis');
const slicePrevBtn=document.getElementById('slicePrev');
const sliceNextBtn=document.getElementById('sliceNext');
const sliceValueEl=document.getElementById('sliceValue');
const stepButtons=[...document.querySelectorAll('[data-axis][data-dir]')];
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
key.position.set(4,7,5);scene.add(key);
const fill=new THREE.DirectionalLight(0x6edfd4,0.22);
fill.position.set(-5,-2,-3);scene.add(fill);

let cells=[],meshes=[],selected=62,playing=true,peeled=false,rx=0.38,ry=0.72;
let slots={};
let topology=new URL(location.href).searchParams.get('topology')==='torus'?'torus':'cube';
let sliceAxis='all',sliceValue=2;
const GAP=0.18,SIZE=0.86;

function home(cell,explode){
  const s=1+GAP+explode*0.72;
  return new THREE.Vector3((cell.x-2)*s,(cell.y-2)*s,(cell.z-2)*(s+explode*0.9));
}
function syncUrl(){
  if(!cells.length)return;
  const u=new URL(location.href);
  if(topology==='torus')u.searchParams.set('topology','torus');
  else u.searchParams.delete('topology');
  u.hash=cells[selected].word;
  history.replaceState(null,'',u);
}
function activeNeighbors(cell){
  return neighbors(cell,topology);
}
function bind(cell){
  const ns=activeNeighbors(cell);
  wordEl.textContent=cell.word;
  indexReadout.textContent='i = '+String(cell.i);
  coordReadout.textContent='xyz = '+cell.x+','+cell.y+','+cell.z;
  magReadout.textContent='m = '+cell.m.join(',');
  topologyReadout.textContent='topology = '+topology+' · degree '+String(ns.length);
  neighborReadout.textContent='neighbors = '+ns.map((n)=>(n.dir<0?'−':'+')+n.axis+' '+cells[n.i].word).join(' · ');
  topologyBtn.textContent='Topology · '+topology;
  topologyBtn.classList.toggle('on',topology==='torus');
  sliceAxisBtn.textContent='Slice · '+sliceAxis;
  sliceValueEl.textContent=sliceAxis==='all'?'all':sliceAxis+' = '+String(sliceValue);
  slicePrevBtn.disabled=sliceAxis==='all';
  sliceNextBtn.disabled=sliceAxis==='all';
  gh.href='https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/q5/cells.jsonl#L'+String(cell.i+1);
  no.href=slots[cell.word]||HUB;
  no.textContent='Notion '+cell.word;
  for(const button of stepButtons){
    const axis=button.dataset.axis;
    const dir=Number(button.dataset.dir);
    const next=stepAxis(cell,axis,dir,topology==='torus');
    const blocked=next===cell.i&&topology==='cube';
    button.disabled=blocked;
    button.textContent=(dir<0?'−':'+')+axis.toUpperCase()+' · '+(blocked?'edge':cells[next].word);
  }
  syncUrl();
}
function layout(){
  const explode=peeled?1:0;
  const cell=cells[selected];
  const neighborSet=new Set(activeNeighbors(cell).map((n)=>n.i));
  const visible=sliceAxis==='all'?null:new Set(sliceCells(sliceAxis,sliceValue).map((c)=>c.i));
  for(const current of cells){
    const m=meshes[current.i];
    m.position.copy(home(current,explode));
    m.visible=!visible||visible.has(current.i);
    const hot=current.i===selected;
    const near=neighborSet.has(current.i);
    m.scale.setScalar(hot?1.16:near?1.06:1);
    m.material.emissive.setHex(hot?0x315a55:near?0x102d2a:0x000000);
    m.material.emissiveIntensity=hot?0.75:near?0.42:0;
  }
  bind(cell);
}
function resize(){
  const w=innerWidth,h=innerHeight;
  renderer.setSize(w,h,false);
  camera.aspect=w/h;camera.updateProjectionMatrix();
}
function stopWalk(){
  playing=false;
  walkBtn.textContent='Walk';
  walkBtn.classList.remove('on');
}
function selectIndex(i){
  selected=((i%DIM)+DIM)%DIM;
  if(sliceAxis!=='all')sliceValue=cells[selected][sliceAxis];
  stopWalk();
  layout();
}
function move(axis,dir){
  const cell=cells[selected];
  const next=stepAxis(cell,axis,dir,topology==='torus');
  if(next===selected&&topology==='cube')return;
  selected=next;
  if(sliceAxis===axis)sliceValue=cells[selected][axis];
  stopWalk();
  layout();
}
function cycleSlice(){
  const order=['all','x','y','z'];
  sliceAxis=order[(order.indexOf(sliceAxis)+1)%order.length];
  if(sliceAxis!=='all')sliceValue=cells[selected][sliceAxis];
  layout();
}
function changeSlice(delta){
  if(sliceAxis==='all')return;
  sliceValue=(sliceValue+delta+RADIX)%RADIX;
  const c=cells[selected];
  const x=sliceAxis==='x'?sliceValue:c.x;
  const y=sliceAxis==='y'?sliceValue:c.y;
  const z=sliceAxis==='z'?sliceValue:c.z;
  selected=pi(x,y,z);
  stopWalk();
  layout();
}
function nextWalkIndex(){
  if(sliceAxis==='all')return (selected+1)%DIM;
  const visible=sliceCells(sliceAxis,sliceValue);
  const at=visible.findIndex((c)=>c.i===selected);
  return visible[(at+1+visible.length)%visible.length].i;
}

const ray=new THREE.Raycaster();
const ptr=new THREE.Vector2();
function pick(ev){
  const r=canvas.getBoundingClientRect();
  ptr.x=((ev.clientX-r.left)/r.width)*2-1;
  ptr.y=-((ev.clientY-r.top)/r.height)*2+1;
  ray.setFromCamera(ptr,camera);
  const hit=ray.intersectObjects(meshes.filter((m)=>m.visible),false)[0];
  if(!hit)return;
  selectIndex(hit.object.userData.i);
}

let drag=false,px=0,py=0;
canvas.addEventListener('pointerdown',(e)=>{drag=true;px=e.clientX;py=e.clientY;canvas.setPointerCapture(e.pointerId);});
canvas.addEventListener('pointerup',(e)=>{
  const moved=Math.hypot(e.clientX-px,e.clientY-py);
  drag=false;
  if(moved<6)pick(e);
});
canvas.addEventListener('pointermove',(e)=>{
  if(!drag)return;
  ry+=(e.clientX-px)*0.005;
  rx+=(e.clientY-py)*0.005;
  rx=Math.max(-1.2,Math.min(1.2,rx));
  px=e.clientX;py=e.clientY;
});
canvas.addEventListener('wheel',(e)=>{
  e.preventDefault();
  const z=camera.position.length()*(e.deltaY>0?1.06:0.94);
  camera.position.setLength(Math.max(6,Math.min(18,z)));
},{passive:false});

walkBtn.onclick=()=>{
  playing=!playing;
  walkBtn.textContent=playing?'Pause':'Walk';
  walkBtn.classList.toggle('on',playing);
};
peelBtn.onclick=()=>{peeled=!peeled;peelBtn.classList.toggle('on',peeled);layout();};
topologyBtn.onclick=()=>{topology=topology==='cube'?'torus':'cube';layout();};
sliceAxisBtn.onclick=cycleSlice;
slicePrevBtn.onclick=()=>changeSlice(-1);
sliceNextBtn.onclick=()=>changeSlice(1);
for(const button of stepButtons){
  button.onclick=()=>move(button.dataset.axis,Number(button.dataset.dir));
}
window.addEventListener('keydown',(e)=>{
  if(e.key==='t'||e.key==='T'){topology=topology==='cube'?'torus':'cube';layout();}
  if(e.key==='x')move('x',1);
  if(e.key==='X')move('x',-1);
  if(e.key==='y')move('y',1);
  if(e.key==='Y')move('y',-1);
  if(e.key==='z')move('z',1);
  if(e.key==='Z')move('z',-1);
});

let acc=0;
function tick(t){
  const now=t*0.001;
  if(!tick.t)tick.t=now;
  const dt=now-tick.t;tick.t=now;
  if(playing){
    acc+=dt;
    if(acc>0.9){
      acc=0;
      selected=nextWalkIndex();
      layout();
    }
  }
  group.rotation.set(rx,ry,0);
  const pulse=playing?1.14+0.06*Math.sin(now*5):1.16;
  if(meshes[selected]&&meshes[selected].visible)meshes[selected].scale.setScalar(pulse);
  renderer.render(scene,camera);
  requestAnimationFrame(tick);
}

const [rows,slotMap]=await Promise.all([loadCells(),loadSlots()]);
assertLedger(rows);
slots=slotMap;
cells=TOPO_CELLS.map((c)=>({...c,m:[...c.m]}));
const requestedWord=location.hash.slice(1);
const requested=cells.find((c)=>c.word===requestedWord);
if(requested)selected=requested.i;
const geo=new THREE.BoxGeometry(SIZE,SIZE,SIZE);
for(const cell of cells){
  const mat=new THREE.MeshLambertMaterial({map:tex(cell),emissive:0x000000});
  const mesh=new THREE.Mesh(geo,mat);
  mesh.userData.i=cell.i;
  group.add(mesh);
  meshes[cell.i]=mesh;
}
layout();
resize();
addEventListener('resize',resize);
requestAnimationFrame(tick);
"""


def emit(root: Path, slots_path: Path | None = None) -> Path:
    cells_src = HERE / "cells.jsonl"
    if not cells_src.is_file():
        raise SystemExit(f"missing {cells_src}")
    rows = validator.load_cells(cells_src)
    validator.check_cells(rows)
    validator.check_residuals()

    dest = root / "website" / "interfaces" / "q5"
    dest.mkdir(parents=True, exist_ok=True)
    data = root / "website" / "data"
    data.mkdir(parents=True, exist_ok=True)

    shutil.copyfile(cells_src, dest / "cells.jsonl")
    shutil.copyfile(HERE / "topology.mjs", dest / "topology.mjs")
    shutil.copyfile(cells_src, data / "q5-cells.jsonl")

    slots_src = slots_path
    if slots_src is None:
        for cand in (
            HERE / "slots.json",
            root / "website" / "interfaces" / "q5" / "slots.json",
        ):
            if cand.is_file():
                slots_src = cand
                break
    if slots_src and slots_src.is_file():
        shutil.copyfile(slots_src, dest / "slots.json")

    three = THREE_ONSITE if (root / "website" / "vendor" / "three.module.js").is_file() else THREE_CDN
    html = (
        INDEX_HTML.replace("__THREE__", three)
        .replace("__NOTION__", NOTION_HUB)
    )
    (dest / "index.html").write_text(html, encoding="utf-8")
    (dest / "lattice.js").write_text(LATTICE_JS, encoding="utf-8")
    print(f"emitted {dest}")
    print(f"pages   {PAGES_CUBE}")
    return dest


def serve(root: Path, host: str, port: int) -> None:
    site = root / "website"
    if not (site / "index.html").is_file():
        raise SystemExit(f"website/index.html missing under {root}")

    class Handler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(site), **kwargs)

    httpd = ThreadingHTTPServer((host, port), Handler)
    print(f"hosting {site} at http://{host}:{port}/")
    print(f"cube    http://{host}:{port}/interfaces/q5/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("stop")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("cmd", nargs="?", default="emit", choices=("emit", "serve", "check"))
    p.add_argument("--root", type=Path, default=None)
    p.add_argument("--slots", type=Path, default=None)
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=8000)
    args = p.parse_args(argv)
    root = args.root.resolve() if args.root else repo_root()

    if args.cmd == "check":
        validator.main()
        return 0
    emit(root, args.slots)
    if args.cmd == "serve":
        serve(root, args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
