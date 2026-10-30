// CITY-CINEMA-CODEC-1.0
// Shared visual-resolution governor for propulsion labs. Rendering only: never mutates solver state.
export function installCityCinemaCodec({renderer=null,composer=null,canvas=null}={}){
  const c=canvas||renderer?.domElement||document.querySelector('canvas');
  const state={tier:'cinema',dpr:1,fps:0,scale:1,backend:renderer?'webgl':'canvas2d'};
  const maxDpr=matchMedia('(max-width: 800px)').matches?1.75:2.5;
  state.dpr=Math.min(devicePixelRatio||1,maxDpr);
  if(renderer){
    renderer.setPixelRatio(state.dpr);
    renderer.outputColorSpace=renderer.outputColorSpace;
    if('toneMappingExposure' in renderer) renderer.toneMappingExposure=1.08;
    state.backend=renderer.capabilities?.isWebGL2?'webgl2':'webgl';
  }
  if(c){c.style.imageRendering='auto';c.dataset.cityCinema='1';}
  let frames=0,last=performance.now();
  function tick(now){
    frames++;
    if(now-last>=1000){state.fps=Math.round(frames*1000/(now-last));frames=0;last=now;
      const next=state.fps<42?Math.max(.72,state.scale-.08):state.fps>57?Math.min(1,state.scale+.04):state.scale;
      if(next!==state.scale){
        state.scale=next;
        if(renderer)renderer.setPixelRatio(state.dpr*state.scale);
        if(c)c.dataset.cityRenderScale=state.scale.toFixed(2);
        window.dispatchEvent(new CustomEvent('city:render-scale',{detail:{...state}}));
      }
    }
    requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
  window.CITY_CINEMA_CODEC={schema:'CITY-CINEMA-CODEC-1.0',state,
    invariant:'visual resolution governor only; solver timestep, evidence class and scientific state unchanged'};
  return window.CITY_CINEMA_CODEC;
}
