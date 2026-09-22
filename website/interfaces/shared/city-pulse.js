export const CITY_PULSE_SCHEMA="CITY-PULSE/1.0";
const CHANNEL="mathematical-city-pulse";
const STORAGE_KEY="CITY_PULSE_LAST";
function valid(p){return p&&p.schema===CITY_PULSE_SCHEMA&&typeof p.run_id==="string"&&Number.isFinite(p.t)&&p.carrier===125&&p.e47===47}
export function installCityPulse({surface="CITY",onPulse=null}={}){
 let bc=null,last=null;
 const receive=p=>{if(!valid(p))return;last=p;window.CITY_PULSE_STATE=p;document.dispatchEvent(new CustomEvent("city:pulse",{detail:p}));onPulse?.(p)};
 try{if("BroadcastChannel"in window){bc=new BroadcastChannel(CHANNEL);bc.onmessage=e=>receive(e.data)}}catch{}
 addEventListener("storage",e=>{if(e.key!==STORAGE_KEY||!e.newValue)return;try{receive(JSON.parse(e.newValue))}catch{}});
 addEventListener("message",e=>{if(e.data?.type==="CITY_PULSE")receive(e.data.packet)});
 function publish(packet){const p={schema:CITY_PULSE_SCHEMA,source:surface,wall_time:new Date().toISOString(),...packet};if(!valid(p))throw new Error("CITY_PULSE contract violation");last=p;receive(p);try{bc?.postMessage(p)}catch{};try{localStorage.setItem(STORAGE_KEY,JSON.stringify(p))}catch{};try{if(window.parent!==window)window.parent.postMessage({type:"CITY_PULSE",packet:p},"*")}catch{};return p}
 function close(){try{bc?.close()}catch{}}
 const api={schema:CITY_PULSE_SCHEMA,surface,publish,receive,get state(){return last},close};window.CITY_PULSE=api;return api
}
