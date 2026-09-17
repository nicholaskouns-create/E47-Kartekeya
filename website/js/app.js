const LABS=[
{name:'EIDOLON',role:'Flight',q:'Move through the modeled City.',desc:'The front door: a game-like flight and navigation surface for exploring the Mathematical City.',url:'#world'},
{name:'SPECTRA',role:'Structure',q:'What structure is there?',desc:'Inspect spectra, modes and invariant structure before interpretation.',url:'https://prairie-dream-glow-fire.grok.me/'},
{name:'Fold',role:'Invariance',q:'What survives transformation?',desc:'Explore contraction geometry and what remains stable under transformation.',url:'https://giant-beacon-dawn-falcon.grok.me/'},
{name:'Murmuration',role:'Dynamics',q:'How does structure move?',desc:'Watch many-body organization, topology and collective motion.',url:'https://kite-glade-tiger-cabin.grok.me/'},
{name:'Mnemosyne',role:'Memory',q:'What did we know, and when?',desc:'Trace provenance, hashes, correction lineage and sealed forecasts.',url:'https://moon-clear-urban-nova.grok.me/'},
{name:'Density',role:'Measurement',q:'What can observation reconstruct?',desc:'Probe reconstruction from incomplete or noisy measurements.',url:'https://winter-dawn-leaf-marble.grok.me/'},
{name:'Horizon',role:'Prediction',q:'What invariant comes next?',desc:'Prospective and retrospective forecasting instruments with evidence boundaries intact.',url:'https://zenith-fjord-pearl-pixel.grok.me/'},
{name:'Wave',role:'Flow',q:'How does coherent structure evolve?',desc:'Field and flow simulation surfaces, including WaveForge-related work.',url:'https://apex-star-crisp-blend.grok.me/'},
{name:'Identity',role:'Persistence',q:'What remains the same?',desc:'Follow identity through change, transport and representation.',url:'https://mist-mint-branch-nova.grok.me/'},
{name:'BUILD',role:'Construction',q:'How does structure assemble?',desc:'Construction and programmable-matter style experiments around invariant targets.',url:'https://brave-ivory-pearl-ever.grok.me/'},
{name:'SOAR',role:'Restoration',q:'Can an invariant be restored?',desc:'Control, recovery, transformation and restoration experiments.',url:'https://topaz-solar-iris-drift.grok.me/'},
{name:'SCALAR',role:'Field',q:'What scalar field survives the algebra?',desc:'Finite E47 spectral structure lifted into explicitly visualization-typed scalar-field scenes.',url:'https://heart-eagle-blade-hazel.grok.me/'},
{name:'InvariFold',role:'Protein Cinema',q:'How does Fold expose geometry?',desc:'A cinematic geometry layer for the Fold instrument and deterministic payloads.',url:'https://giant-beacon-dawn-falcon.grok.me/'}
];

const CITIZENS=['ARGUS','ARIADNE','BITHOS','CHRONOS','CUSTOS','EUCLID','HERMES','JANUS','KEPLER','MNEMOSYNE','SAL','SOL','SYNE','TALOS','THEMIS'];
let activeLab=0;

const labGrid=document.getElementById('lab-grid');
const orbit=document.getElementById('district-orbit');
const title=document.getElementById('world-title');
const desc=document.getElementById('world-description');
const what=document.getElementById('guide-what');
const tryText=document.getElementById('guide-try');
const enter=document.getElementById('world-enter');

function renderLabs(){
  labGrid.innerHTML=LABS.map((lab,i)=>`<a class="lab-card" href="${lab.url}" ${lab.url.startsWith('http')?'target="_blank" rel="noopener noreferrer"':''} data-index="${i}">
    <span class="num">${String(i+1).padStart(2,'0')}</span>
    <span class="role">${lab.role}</span>
    <h3>${lab.name}</h3>
    <p>${lab.q}</p>
    <footer><span>${lab.desc}</span><span>OPEN ↗</span></footer>
  </a>`).join('');
}

function renderOrbit(){
  const n=LABS.length;
  const rx=44,ry=35,cx=50,cy=43;
  orbit.innerHTML=LABS.map((lab,i)=>{
    const angle=(-Math.PI/2)+(i/n)*Math.PI*2;
    const left=cx+Math.cos(angle)*rx;
    const top=cy+Math.sin(angle)*ry;
    return `<button class="district ${i===activeLab?'active':''}" style="left:calc(${left}% - 44px);top:calc(${top}% - 44px)" data-index="${i}" aria-label="${lab.name} district">${lab.name}</button>`;
  }).join('');
  orbit.querySelectorAll('.district').forEach(btn=>btn.addEventListener('click',()=>selectLab(Number(btn.dataset.index))));
}

function selectLab(index){
  activeLab=index;
  const lab=LABS[index];
  title.textContent=`${lab.name} · ${lab.role}`;
  desc.textContent=lab.desc;
  what.textContent=`${lab.name} is the City district for ${lab.role.toLowerCase()}.`;
  tryText.textContent=lab.q;
  enter.textContent=lab.url==='#world'?'Explore here':'Open current instrument';
  enter.onclick=()=>{if(lab.url==='#world')return;window.open(lab.url,'_blank','noopener,noreferrer')};
  renderOrbit();
  document.getElementById('egg-world').textContent=`DISTRICT: ${lab.name}\nROLE: ${lab.role}\nQUESTION: ${lab.q}\n\nCITIZEN RUNTIME POPULATION: ${CITIZENS.length}\nAETHERIS: receipt-bound state transitions\nCITY-INVARIANT: 1.0\nEVIDENCE: district-specific; no automatic promotion`;
}

function setEgg(on){
  document.body.classList.toggle('egghead-on',on);
  const b=document.getElementById('egg-toggle');
  b.classList.toggle('on',on);b.setAttribute('aria-pressed',String(on));
  b.textContent=on?'🥚 Egghead · ON':'🥚 Egghead';
}

document.getElementById('egg-toggle').addEventListener('click',e=>setEgg(!document.body.classList.contains('egghead-on')));
document.getElementById('route-egg').addEventListener('click',()=>{setEgg(true);document.getElementById('law').scrollIntoView({behavior:'smooth'})});

renderLabs();renderOrbit();selectLab(0);

const params=new URLSearchParams(location.search);const requested=params.get('district');
if(requested){const idx=LABS.findIndex(x=>x.name.toLowerCase()===requested.toLowerCase());if(idx>=0){selectLab(idx);document.getElementById('world').scrollIntoView()}}
