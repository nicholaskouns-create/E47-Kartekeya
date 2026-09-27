(() => {
  "use strict";
  const routes = [
    {name:"PIP Explains E47–MANTA",kind:"LEARN",filter:["learn","run"],ev:["E0","E1","E2"],desc:"Kid-friendly interactive bridge from the exact 125→47 spectral core to the separately typed MANTA simulation layer.",url:"../pip-manta/",substrate:"GITHUB PAGES"},
    {name:"E47 in Two Pages",kind:"LEARN",filter:["learn"],ev:["E0","E1"],desc:"K², why dim V₂=5, recursive selection, and the claim boundary in one compact reader bridge.",url:"../../notes/e47-recursive-system/",substrate:"GITHUB PAGES"},
    {name:"125×125 Spectral Matrix Proof",kind:"VERIFY",filter:["verify","learn"],ev:["E0","E1"],desc:"Human-readable proof surface for the finite carrier, selector, projector, spectrum, and machine-checked closure.",url:"../e47-spectral-matrix-proof/",substrate:"GITHUB PAGES"},
    {name:"THE MATRIX",kind:"RUN",filter:["run","verify"],ev:["E1","E2"],desc:"Parity-validated quantum simulator connecting the finite E47 machinery to explicit quantum simulation workflows.",url:"../matrix/",substrate:"GITHUB PAGES"},
    {name:"Q5 Lattice",kind:"RUN",filter:["run","browse"],ev:["E1"],desc:"Executable 5×5×5 address topology for the 125-word packing ledger. Same carrier size, separate typed object.",url:"../q5/",substrate:"GITHUB PAGES"},
    {name:"NEXUS",kind:"BROWSE",filter:["run","browse"],ev:["E1","E2"],desc:"Composition surface for pulse, operad, packet cinema, and watchtower views across City instruments.",url:"../nexus/",substrate:"GITHUB PAGES"},
    {name:"MANTA",kind:"RUN",filter:["run"],ev:["E2"],desc:"Programmable-matter spectral-morph flight simulation. Geometry, gain, force, torque, and trajectory remain simulation.",url:"../manta/",substrate:"GITHUB PAGES"},
    {name:"SKYRMION Runtime 2",kind:"RUN",filter:["run"],ev:["E1","E2"],desc:"Multi-domain flight laboratory separating conventional vehicle models from explicit experimental simulation adapters.",url:"../skyrmion/",substrate:"GITHUB PAGES"},
    {name:"Syntax Jacob",kind:"RUN",filter:["run"],ev:["E1","E2"],desc:"3I/ATLAS scalar-navigation laboratory with live ephemeris context and modeled E47 coherence.",url:"../syntax-jacob/",substrate:"GITHUB PAGES"},
    {name:"Coherence Runtime",kind:"BUILD",filter:["build","run"],ev:["E1"],desc:"Executable CIRP/QEGT/Ubuntu/Murmuration runtime contract and implementation surface.",url:"../coherence-runtime/",substrate:"GITHUB PAGES"},
    {name:"Formalism Atlas",kind:"BROWSE",filter:["browse","verify"],ev:["E0","E1"],desc:"Current registry of formalisms, symbols, proofs, certificates, boundaries, and source routes.",url:"../formalism-atlas/",substrate:"GITHUB PAGES"},
    {name:"Route Packets",kind:"BROWSE",filter:["browse","build"],ev:["E1"],desc:"Cross-platform object projection showing how one research object appears across GitHub, Notion, Drive, Supabase, and AIMS.",url:"../route-packets/",substrate:"GITHUB PAGES"},
    {name:"CITY LIVE",kind:"RUN",filter:["run","browse"],ev:["E1","E2"],desc:"Workshop collection of independently addressable public instruments and experimental surfaces.",url:"../city-live/",substrate:"GITHUB PAGES"},
    {name:"CITY CORE",kind:"RUN",filter:["run","browse"],ev:["E1","E2"],desc:"Integrated research console and flight doorway with instrument loading, telemetry, and shared City navigation.",url:"../kouns-core/?module=eidolon#flight",substrate:"GITHUB PAGES"},
    {name:"SEE · Citadel",kind:"VERIFY",filter:["verify","browse"],ev:["E1"],desc:"Inspection point for receipts, registries, residuals, provenance, and machine-evidence metadata.",url:"https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/see/",substrate:"SUPABASE"},
    {name:"Certificates",kind:"VERIFY",filter:["verify","build"],ev:["E1"],desc:"Repository certificate corpus and reproducibility records for machine-verified results.",url:"https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/certificates",substrate:"GITHUB"},
    {name:"AIMS Root Directory",kind:"LEARN",filter:["learn","browse"],ev:[],desc:"Public explanatory publication surface and narrative index for the E47 research program.",url:"https://www.aims.healthcare/journal/e47-by-nicholas-kouns-root-directory",substrate:"AIMS"},
    {name:"Mathematical City · Notion",kind:"BROWSE",filter:["browse","learn"],ev:[],desc:"Living knowledge graph with linked pages, provenance, context, and research lineage.",url:"https://mathematicalcity.notion.site/?pvs=74",substrate:"NOTION"},
    {name:"Repository",kind:"BUILD",filter:["build"],ev:["E0","E1","E2"],desc:"Canonical executable research repository: code, tests, contracts, certificates, history, and Pages.",url:"https://github.com/nicholaskouns-create/E47-Kartekeya",substrate:"GITHUB"}
  ];
  const grid=document.getElementById("route-grid"),q=document.getElementById("q"),buttons=[...document.querySelectorAll("[data-filter]")],count=document.getElementById("count"),empty=document.getElementById("empty");
  let active="all";
  const norm=s=>s.normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
  function card(r){
    const ext=/^https?:/.test(r.url);
    return '<a class="route" href="'+r.url+'"'+(ext?' target="_blank" rel="noopener noreferrer"':'')+' data-search="'+norm([r.name,r.kind,r.desc,r.substrate,...r.filter,...r.ev].join(" "))+'"><div class="route-top"><span class="kind">'+r.kind+'</span><span class="evidence">'+r.ev.map(e=>'<i data-e="'+e+'">'+e+'</i>').join("")+'</span></div><h3>'+r.name+'</h3><p>'+r.desc+'</p><footer><span>'+r.substrate+'</span><b>↗</b></footer></a>';
  }
  function render(){
    const tokens=norm(q.value.trim()).split(/\s+/).filter(Boolean);
    const visible=routes.filter(r=>(active==="all"||r.filter.includes(active))&&tokens.every(t=>norm([r.name,r.kind,r.desc,r.substrate,...r.filter,...r.ev].join(" ")).includes(t)));
    grid.innerHTML=visible.map(card).join("");
    count.textContent=visible.length+" route"+(visible.length===1?"":"s");
    empty.hidden=visible.length!==0;
    grid.hidden=visible.length===0;
    buttons.forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.filter===active)));
  }
  q.addEventListener("input",render);
  q.addEventListener("keydown",e=>{if(e.key==="Escape"){q.value="";render()}});
  buttons.forEach(b=>b.addEventListener("click",()=>{active=b.dataset.filter;render()}));
  document.addEventListener("keydown",e=>{if(e.key==="/"&&!e.metaKey&&!e.ctrlKey&&!e.altKey&&!e.target.closest("input,textarea,[contenteditable]")){e.preventDefault();q.focus()}});
  render();
})();