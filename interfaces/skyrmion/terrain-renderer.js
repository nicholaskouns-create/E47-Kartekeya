// SKYRMION-TERRAIN-1.0
// Lightweight satellite-terrain presentation using WGS84 slippy-map tiles.
// Rendering/navigation only. It never mutates solver/evidence state.
const TILE=256;
const RAD=Math.PI/180;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));

function lngLatToWorld(lon,lat,z){
  const n=2**z;
  const x=(lon+180)/360*n;
  const s=Math.sin(clamp(lat,-85.05112878,85.05112878)*RAD);
  const y=(.5-Math.log((1+s)/(1-s))/(4*Math.PI))*n;
  return {x,y,z,n};
}
function tileUrl(x,y,z){
  const n=2**z;
  const xx=((x%n)+n)%n;
  const yy=clamp(y,0,n-1);
  return `https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/${z}/${yy}/${xx}`;
}

export function installSkyrmionTerrain({
  root=document.body,
  lat=36.1699,
  lon=-115.1398,
  altitude_m=1100,
  heading=0,
  enabled=true
}={}){
  const stage=document.createElement('div');
  stage.className='terrain-stage';
  stage.innerHTML=`
    <div class="terrain-sky"></div>
    <div class="terrain-haze"></div>
    <div class="terrain-camera">
      <div class="terrain-plane"><div class="terrain-grid"></div></div>
    </div>
    <div class="terrain-vignette"></div>
    <div class="terrain-attribution">Imagery © Esri, Maxar, Earthstar Geographics and contributors</div>`;
  root.prepend(stage);
  const grid=stage.querySelector('.terrain-grid');
  const plane=stage.querySelector('.terrain-plane');
  const camera=stage.querySelector('.terrain-camera');
  let state={lat,lon,altitude_m,heading,enabled,zoom:14,centerX:null,centerY:null};
  let cells=[];
  const radius=2;
  for(let dy=-radius;dy<=radius;dy++){
    for(let dx=-radius;dx<=radius;dx++){
      const img=document.createElement('img');
      img.decoding='async';img.loading='eager';img.referrerPolicy='no-referrer';
      img.dataset.dx=dx;img.dataset.dy=dy;
      img.style.left=((dx+radius)*TILE)+'px';
      img.style.top=((dy+radius)*TILE)+'px';
      grid.appendChild(img);cells.push(img);
    }
  }
  const size=(radius*2+1)*TILE;
  grid.style.width=size+'px';grid.style.height=size+'px';

  function chooseZoom(alt){
    if(alt<1200)return 15;
    if(alt<3200)return 14;
    if(alt<8500)return 13;
    if(alt<18000)return 12;
    return 11;
  }
  function refreshTiles(force=false){
    state.zoom=chooseZoom(state.altitude_m);
    const w=lngLatToWorld(state.lon,state.lat,state.zoom);
    const cx=Math.floor(w.x),cy=Math.floor(w.y);
    if(force||cx!==state.centerX||cy!==state.centerY){
      state.centerX=cx;state.centerY=cy;
      for(const img of cells){
        const dx=+img.dataset.dx,dy=+img.dataset.dy;
        img.src=tileUrl(cx+dx,cy+dy,state.zoom);
      }
    }
    const fracX=w.x-cx,fracY=w.y-cy;
    const offsetX=(.5-fracX)*TILE;
    const offsetY=(.5-fracY)*TILE;
    grid.style.transform=`translate3d(${offsetX}px,${offsetY}px,0)`;
  }
  function render(){
    stage.hidden=!state.enabled;
    if(!state.enabled)return;
    refreshTiles(false);
    const alt=clamp(state.altitude_m,100,25000);
    const scale=clamp(1.18-(Math.log10(alt)-2)*.18,.72,1.32);
    const pitch=clamp(70-(alt/25000)*12,56,72);
    plane.style.transform=`translate3d(-50%,-49%,0) rotateX(${pitch}deg) rotateZ(${-state.heading*180/Math.PI}deg) scale(${scale})`;
    camera.style.perspective=(620+alt*.035)+'px';
    stage.style.setProperty('--terrain-alt',String(alt));
  }
  function update(next={}){
    Object.assign(state,next);
    render();
  }
  refreshTiles(true);render();
  return {stage,state,update,refresh:()=>refreshTiles(true),destroy:()=>stage.remove()};
}

export const SKYRMION_TERRAIN={
  schema:'SKYRMION-TERRAIN-1.0',
  source:'Esri World Imagery raster tiles',
  crs:'EPSG:3857 display / WGS84 navigation',
  invariant:'imagery and perspective are rendering only; simulator state remains authoritative'
};
