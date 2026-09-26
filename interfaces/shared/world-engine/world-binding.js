// CITY-WORLD-BINDING-1.0
// Cross-surface persistence/broadcast adapter for CITY-WORLD-ENGINE-1.0.
// Keeps one WGS84 world anchor while instruments/craft change.

import {WORLD_ENGINE_VERSION,createWorldState,generateWorldCell} from './world-engine.js';

export const WORLD_BINDING_VERSION='CITY-WORLD-BINDING-1.0';
export const WORLD_STORAGE_KEY='city.world.state.v1';
export const WORLD_CHANNEL='city-world-engine-v1';

const finite=(v,d=0)=>Number.isFinite(Number(v))?Number(v):d;

export function normalizeWorldState(input={}){
  const state=createWorldState({
    lat:finite(input.lat,36.1699),
    lon:finite(input.lon,-115.1398),
    altitude_m:finite(input.altitudeM??input.altitude_m,610),
    heading:finite(input.heading,0),
    pitch:finite(input.pitch,0),
    roll:finite(input.roll,0),
    speed:finite(input.speedMps??input.speed,0),
    domain:finite(input.domain,0)
  });
  return {
    ...state,
    worldCellId:input.worldCellId||null,
    updatedAt:finite(input.updatedAt,Date.now())
  };
}

export function readWorldState(fallback=null){
  try{
    const raw=globalThis.localStorage?.getItem(WORLD_STORAGE_KEY);
    if(raw)return normalizeWorldState(JSON.parse(raw));
  }catch{}
  return fallback?normalizeWorldState(fallback):null;
}

export function writeWorldState(input={}){
  const state=normalizeWorldState({...input,updatedAt:Date.now()});
  try{globalThis.localStorage?.setItem(WORLD_STORAGE_KEY,JSON.stringify(state))}catch{}
  return state;
}

export function installWorldBinding({
  surface='CITY',
  initial=null,
  postTarget=null,
  onState=null,
  generateCell=false,
  cellSpanM=12000,
  cellSamples=33
}={}){
  let state=readWorldState(initial)||normalizeWorldState(initial||{});
  let cell=generateCell?generateWorldCell({lat:state.lat,lon:state.lon,span:cellSpanM,samples:cellSamples}):null;
  let handling=false,destroyed=false;
  const channel=typeof BroadcastChannel==='function'?new BroadcastChannel(WORLD_CHANNEL):null;

  function payload(next=state,source=surface){
    return {...normalizeWorldState(next),schema:'CITY-WORLD-STATE-1.0',version:WORLD_ENGINE_VERSION,binding:WORLD_BINDING_VERSION,source};
  }
  function publishTo(target=postTarget){
    if(!target)return;
    const win=target?.contentWindow||target;
    try{win?.postMessage?.({type:'CITY:WORLD',...payload()},'*')}catch{}
  }
  function commit(next,{broadcast=true,dispatch=true,source=surface}={}){
    if(destroyed)return state;
    state=writeWorldState({...state,...next});
    if(generateCell)cell=generateWorldCell({lat:state.lat,lon:state.lon,span:cellSpanM,samples:cellSamples});
    const detail={...payload(state,source),worldCellId:cell?.id||state.worldCellId||null};
    try{onState?.(detail,cell)}catch{}
    publishTo(postTarget);
    if(broadcast)try{channel?.postMessage(detail)}catch{}
    if(dispatch&&typeof globalThis.dispatchEvent==='function'&&typeof globalThis.CustomEvent==='function'){
      handling=true;
      try{globalThis.dispatchEvent(new CustomEvent('city:world-state',{detail}))}finally{handling=false}
    }
    return state;
  }
  function onWorldEvent(event){
    if(handling||!event?.detail)return;
    commit(event.detail,{broadcast:true,dispatch:false,source:event.detail.source||surface});
  }
  function onMessage(event){
    const d=event?.data;
    if(d?.type!=='CITY:WORLD'&&d?.schema!=='CITY-WORLD-STATE-1.0')return;
    commit(d,{broadcast:true,dispatch:true,source:d.source||'postMessage'});
  }
  if(typeof globalThis.addEventListener==='function'){
    globalThis.addEventListener('city:world-state',onWorldEvent);
    globalThis.addEventListener('message',onMessage);
  }
  if(channel)channel.onmessage=e=>commit(e.data,{broadcast:false,dispatch:true,source:e.data?.source||'broadcast'});
  commit(state,{broadcast:false,dispatch:false,source:surface});

  return {
    schema:WORLD_BINDING_VERSION,
    version:WORLD_BINDING_VERSION,
    surface,
    get state(){return {...state}},
    get cell(){return cell},
    update(next){return commit(next,{broadcast:true,dispatch:true,source:surface})},
    publish(){return commit(state,{broadcast:true,dispatch:true,source:surface})},
    publishTo,
    destroy(){
      destroyed=true;
      try{channel?.close()}catch{}
      try{globalThis.removeEventListener?.('city:world-state',onWorldEvent)}catch{}
      try{globalThis.removeEventListener?.('message',onMessage)}catch{}
    }
  };
}
