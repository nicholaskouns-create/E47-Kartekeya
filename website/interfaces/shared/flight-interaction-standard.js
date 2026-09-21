export const CITY_FLIGHT_INTERACTION = Object.freeze({
  schema:'CITY-FLIGHT-INTERACTION/2.4',
  version:'2.4.0',
  controls:Object.freeze({
    bank:'A/D or ArrowLeft/ArrowRight',
    pitch:'W/S or ArrowUp/ArrowDown',
    rudder:'Q/E',
    boost:'Shift',
    idle:'Control',
    camera:'C',
    fleet:'1-7'
  })
});

const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const approach=(v,t,maxDelta)=>v<t?Math.min(t,v+maxDelta):Math.max(t,v-maxDelta);
const CONTROL_KEYS=new Set(['a','d','w','s','q','e','arrowleft','arrowright','arrowup','arrowdown','shift','control']);

function installHud(surface,cameraModes){
  if(document.getElementById('city-flight-standard'))return document.getElementById('city-flight-standard');
  if(!document.getElementById('city-flight-standard-style')){
    const style=document.createElement('style');style.id='city-flight-standard-style';style.textContent=`
#city-flight-standard{position:fixed;inset:0;z-index:35;pointer-events:none;font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#eef9f6}
#city-flight-standard .cfs-top{position:absolute;top:max(10px,env(safe-area-inset-top));left:50%;transform:translateX(-50%);display:flex;gap:7px;align-items:center}
#city-flight-standard .cfs-chip,#city-flight-standard .cfs-help{background:rgba(5,10,12,.66);border:1px solid rgba(156,235,220,.20);backdrop-filter:blur(16px) saturate(135%);-webkit-backdrop-filter:blur(16px) saturate(135%);box-shadow:0 12px 38px rgba(0,0,0,.22);border-radius:999px;font:800 9px ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:.055em}
#city-flight-standard .cfs-chip{padding:8px 11px}.cfs-live{color:#9cebdc}
#city-flight-standard .cfs-reticle{position:absolute;left:50%;top:50%;width:34px;height:34px;transform:translate(-50%,-50%);opacity:.34}
#city-flight-standard .cfs-reticle:before,#city-flight-standard .cfs-reticle:after{content:"";position:absolute;background:#dffaf3}.cfs-reticle:before{left:16px;top:0;width:1px;height:34px}.cfs-reticle:after{left:0;top:16px;width:34px;height:1px}
#city-flight-standard .cfs-help{position:absolute;left:50%;bottom:max(12px,env(safe-area-inset-bottom));transform:translateX(-50%);padding:9px 13px;white-space:nowrap;color:rgba(232,250,246,.78)}
#city-flight-standard .cfs-stick{position:absolute;right:max(18px,env(safe-area-inset-right));bottom:max(58px,calc(env(safe-area-inset-bottom) + 48px));width:96px;height:96px;border-radius:50%;border:1px solid rgba(156,235,220,.24);background:radial-gradient(circle,rgba(156,235,220,.08),rgba(5,10,12,.42));pointer-events:auto;touch-action:none;backdrop-filter:blur(10px)}
#city-flight-standard .cfs-knob{position:absolute;left:50%;top:50%;width:34px;height:34px;border-radius:50%;transform:translate(-50%,-50%);border:1px solid rgba(220,255,248,.48);background:rgba(156,235,220,.16);box-shadow:0 0 24px rgba(117,239,215,.12)}
@media(max-width:760px){#city-flight-standard .cfs-top{top:auto;bottom:58px}.cfs-help{font-size:7px!important;max-width:94vw;overflow:hidden;text-overflow:ellipsis}.cfs-chip:first-child{display:none}}
`;document.head.appendChild(style);
  }
  const hud=document.createElement('div');hud.id='city-flight-standard';
  hud.innerHTML=`<div class="cfs-top"><span class="cfs-chip cfs-live">${surface} · RT2.4</span><span class="cfs-chip" data-cfs-state>R 0.00 · P 0.00 · Y 0.00 · T 0%</span><span class="cfs-chip" data-cfs-camera>${cameraModes[0]}</span></div><div class="cfs-reticle"></div><div class="cfs-stick" data-cfs-stick><div class="cfs-knob" data-cfs-knob></div></div><div class="cfs-help">A/D BANK · W/S PITCH · Q/E RUDDER · SHIFT THRUST · C CAMERA · 1–7 FLEET</div>`;
  document.body.appendChild(hud);return hud;
}

export function installFlightInteractionStandard({
  surface='FLIGHT',
  baseThrottle=.72,
  cameraModes=['CHASE','WING','ORBIT'],
  rampUp=1.85,
  rampReturn=2.75,
  mountHud=true,
  onControls=()=>{},
  onCamera=()=>{},
  onFleet=()=>{}
}={}){
  const keys=new Set();
  const state={roll:0,pitch:0,yaw:0,throttle:clamp(Number(baseThrottle)||0,0,1),boost:false,idle:false,engaged:false,cameraIndex:0,vehicleIndex:null};
  const pointer={roll:0,pitch:0,active:false};
  const hud=mountHud?installHud(surface,cameraModes):null;
  const touchStick=hud?.querySelector('[data-cfs-stick]'),touchKnob=hud?.querySelector('[data-cfs-knob]');
  let touchDrag=false,destroyed=false,last=performance.now();
  const setTouch=(x,y)=>{
    if(!touchStick)return;
    const r=touchStick.getBoundingClientRect(),dx=clamp((x-r.left-r.width/2)/(r.width*.36),-1,1),dy=clamp((y-r.top-r.height/2)/(r.height*.36),-1,1);
    pointer.roll=dx;pointer.pitch=-dy;pointer.active=true;state.engaged=true;
    if(touchKnob)touchKnob.style.transform=`translate(calc(-50% + ${dx*27}px),calc(-50% + ${dy*27}px))`;
  };
  touchStick?.addEventListener('pointerdown',e=>{touchDrag=true;touchStick.setPointerCapture?.(e.pointerId);setTouch(e.clientX,e.clientY)});
  touchStick?.addEventListener('pointermove',e=>{if(touchDrag)setTouch(e.clientX,e.clientY)});
  for(const ev of ['pointerup','pointercancel','lostpointercapture'])touchStick?.addEventListener(ev,()=>{touchDrag=false;pointer.roll=pointer.pitch=0;pointer.active=false;if(touchKnob)touchKnob.style.transform='translate(-50%,-50%)'});

  const publish=(dt)=>{
    const detail={schema:CITY_FLIGHT_INTERACTION.schema,version:CITY_FLIGHT_INTERACTION.version,surface,dt,...state,camera:cameraModes[state.cameraIndex]};
    window.CITY_FLIGHT_COMMAND=detail;
    onControls(detail,dt);
    dispatchEvent(new CustomEvent('city:flight-control',{detail}));
    hud?.querySelector('[data-cfs-state]')?.replaceChildren(document.createTextNode(`R ${state.roll.toFixed(2)} · P ${state.pitch.toFixed(2)} · Y ${state.yaw.toFixed(2)} · T ${Math.round(state.throttle*100)}%`));
  };

  const down=e=>{
    if(['INPUT','TEXTAREA','SELECT'].includes(e.target?.tagName)||e.defaultPrevented)return;
    const k=e.key.toLowerCase();
    if(CONTROL_KEYS.has(k)){keys.add(k);state.engaged=true;}
    if(k==='c'&&!e.repeat){
      state.cameraIndex=(state.cameraIndex+1)%cameraModes.length;
      const mode=cameraModes[state.cameraIndex];
      hud?.querySelector('[data-cfs-camera]')?.replaceChildren(document.createTextNode(mode));
      onCamera(mode,state.cameraIndex);
      dispatchEvent(new CustomEvent('city:flight-camera',{detail:{schema:CITY_FLIGHT_INTERACTION.schema,surface,mode,index:state.cameraIndex}}));
    }
    if(!e.repeat&&/^[1-7]$/.test(k)){
      state.vehicleIndex=Number(k)-1;
      onFleet(state.vehicleIndex);
      dispatchEvent(new CustomEvent('city:flight-fleet',{detail:{schema:CITY_FLIGHT_INTERACTION.schema,surface,index:state.vehicleIndex}}));
    }
  };
  const up=e=>keys.delete(e.key.toLowerCase());
  const blur=()=>{keys.clear();pointer.roll=pointer.pitch=0;pointer.active=false;state.roll=state.pitch=state.yaw=0;};
  addEventListener('keydown',down);addEventListener('keyup',up);addEventListener('blur',blur);

  function frame(now){
    if(destroyed)return;
    const dt=Math.min(.05,Math.max(.001,(now-last)/1000));last=now;
    const rollTarget=clamp(pointer.roll+(((keys.has('d')||keys.has('arrowright'))?1:0)-((keys.has('a')||keys.has('arrowleft'))?1:0)), -1,1);
    const pitchTarget=clamp(pointer.pitch+(((keys.has('w')||keys.has('arrowup'))?1:0)-((keys.has('s')||keys.has('arrowdown'))?1:0)), -1,1);
    const yawTarget=((keys.has('e')?1:0)-(keys.has('q')?1:0));
    const rate=(v,t)=>Math.abs(t)>Math.abs(v)?rampUp:rampReturn;
    state.roll=approach(state.roll,rollTarget,rate(state.roll,rollTarget)*dt);
    state.pitch=approach(state.pitch,pitchTarget,rate(state.pitch,pitchTarget)*dt);
    state.yaw=approach(state.yaw,yawTarget,rate(state.yaw,yawTarget)*dt);
    state.boost=keys.has('shift');state.idle=keys.has('control');
    state.throttle=state.boost?1:(state.idle?.05:clamp(Number(typeof baseThrottle==='function'?baseThrottle():baseThrottle)||0,0,1));
    publish(dt);requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  dispatchEvent(new CustomEvent('city:flight-standard-ready',{detail:{schema:CITY_FLIGHT_INTERACTION.schema,version:CITY_FLIGHT_INTERACTION.version,surface}}));
  return {
    schema:CITY_FLIGHT_INTERACTION.schema,state,
    setPointerAxes(roll=0,pitch=0){pointer.roll=clamp(Number(roll)||0,-1,1);pointer.pitch=clamp(Number(pitch)||0,-1,1);pointer.active=Boolean(pointer.roll||pointer.pitch);if(pointer.active)state.engaged=true;},
    reset(){keys.clear();pointer.roll=pointer.pitch=0;pointer.active=false;Object.assign(state,{roll:0,pitch:0,yaw:0,boost:false,idle:false,engaged:false});},
    destroy(){destroyed=true;removeEventListener('keydown',down);removeEventListener('keyup',up);removeEventListener('blur',blur);hud?.remove();}
  };
}
