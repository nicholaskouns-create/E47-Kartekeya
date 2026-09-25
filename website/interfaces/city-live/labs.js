const LABS=[
["KARTEKEYA","Canonical engine · K · P47 · K²","⬡","https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/kartekeya","external"],
["SPECTRA","Eigenstructure of the same run","〰","https://prairie-dream-glow-fire.grok.me/","external"],
["FOLD","Tracks what survives transformation","◎","https://giant-beacon-dawn-falcon.grok.me/","external"],
["MURMURATION","State evolution into collective motion","✦","https://kite-glade-tiger-cabin.grok.me/","external"],
["EIDOLON","Enter the evolving field as observer","◢","../flight/eidolon/","same"],
["MANIFOLD","Locked spectral surfaces · Eidolon replay","▣","../manifold/","same"],
["NEXUS","Pulse bus · operad · cinema · lock","◎","../nexus/","same"],
["MANTA","State-coupled geometry surface","⌁","../manta/","same"],
["DENSITY","Observer-limited measurement","⌗","https://winter-dawn-leaf-marble.grok.me/","external"],
["DENSITY TOMOGRAPHY","Query · reconstruct · withhold · compare","⌗","../density-sensitivity/","same"],
["MNEMOSYNE","Sealed predictions and recall","◉","https://moon-clear-urban-nova.grok.me/","external"],
["HORIZON","Prospective next-state forecast","⟲","https://zenith-fjord-pearl-pixel.grok.me/","external"],
["SYNTAX JACOB","ATLAS 3I copilot · live JPL data","☄","../syntax-jacob/","same"],
["WAVEFORGE","Sonify the mathematics","≋","https://garden-moss-cabin-forest.grok.me/","external"],
["SEE / CITADEL","Coordination · evidence · provenance","♜","https://orbit-coral-delta-fjord.grok.me/","external"]
];
const labs=document.getElementById("labs"),packet=document.getElementById("packet");
if(labs){
  LABS.forEach(([n,d,icon,u,mode])=>{
    const a=document.createElement("a");
    a.className="lab"; a.href=u;
    if(mode==="external"){a.target="_blank";a.rel="noopener noreferrer"}
    a.innerHTML='<div class="icon">'+icon+'</div><div><b>'+n+'</b><p>'+d+'</p><span class="open">'+(mode==="same"?"OPEN LAB →":"LAUNCH HOSTED ↗")+'</span></div>';
    labs.appendChild(a);
  });
}
let raf=0,start=0,runId="idle",running=false;
function tick(ts){
  if(!running)return;
  if(!start)start=ts;
  const t=(ts-start)/1000,p=Math.min(1,t/7);
  const live={run_id:runId,t:+t.toFixed(3),state:p<1?"evolving":"settled",carrier:125,e47:47,complement:Math.max(0,Math.round(78*(1-p))),omega_c:.376,progress:+p.toFixed(4)};
  if(packet)packet.textContent=JSON.stringify(live);
  window.CITY_LIVE_PUBLISH?.(live);
  if(p<1)raf=requestAnimationFrame(tick); else running=false;
}
function begin(){cancelAnimationFrame(raf);start=0;runId="CITY-LIVE-"+Date.now().toString(36).toUpperCase();running=true;raf=requestAnimationFrame(tick)}
const run=document.getElementById("run"),replay=document.getElementById("replay"),reset=document.getElementById("reset");
if(run)run.onclick=begin;
if(replay)replay.onclick=begin;
if(reset)reset.onclick=()=>{running=false;cancelAnimationFrame(raf);start=0;runId="idle";if(packet)packet.textContent='{"run_id":"idle","state":"ready","carrier":125,"e47":47,"complement":78}'};
