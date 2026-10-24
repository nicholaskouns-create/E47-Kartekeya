import{instantiateMatrixCityAdapter}from'../../js/matrix-city125-aetheris.js';

const cityAdapter=instantiateMatrixCityAdapter();
const $=id=>document.getElementById(id);
const log=s=>$('log').textContent+=s+'\n';
let last=null;
let prismPending=false;
const worker=new Worker('./mps-worker.js');

function config(){
  return {
    n:+$('n').value,
    layers:+$('layers').value,
    phi:+$('phi').value,
    chi:+$('chi').value,
    entangler:$('entangler').value,
    noise:$('noise').value,
    g1:+$('g1').value,
    gphi:+$('gphi').value,
    seed:+$('seed').value,
    validate:+$('n').value<=10
  };
}

function drawCircuit(c){
  let gates=[];
  for(let k=0;k<c.layers;k++){
    gates.push('<span class="gate">H⊗'+c.n+'</span>','<span class="gate">Rφ⊗'+c.n+'</span>','<span class="gate">CNOT '+c.entangler+'</span>');
    if(c.noise!=='none')gates.push('<span class="gate warn">𝒩(T1,Tφ)</span>');
  }
  $('circuit').innerHTML=gates.join('');
}

function renderPrism(w){
  const bands=w.spectral_bands||[];
  if(!bands.length){
    $('prismBands').innerHTML='<div class="muted">No spectral-band witness returned.</div>';
    $('prismdetail').textContent='Run E47 PRISM TEST or 125-LIFT → E47.';
    return;
  }
  $('prismBands').innerHTML=bands.map(b=>{
    const pct=100*b.weight;
    return '<div class="spectral-band '+(b.selected?'selected':'')+'">'
      +'<div class="band-head"><b>λ '+b.lambda+'</b><span>'+b.multiplicity+'D</span></div>'
      +'<div class="band-track"><i style="width:'+Math.max(.5,Math.min(100,pct))+'%"></i></div>'
      +'<div class="band-value">'+pct.toFixed(4)+'%</div>'
      +(b.selected?'<div class="band-tag">E47</div>':'')
      +'</div>';
  }).join('');
  const e47=100*w.e47_weight;
  const rank=100*(47/125);
  const delta=e47-rank;
  $('prismdetail').textContent='Σ bands '+w.spectral_weight_sum.toFixed(12)
    +' · E47 λ=6⊕30 '+e47.toFixed(6)+'%'
    +' · rank fraction '+rank.toFixed(6)+'%'
    +' · Δ '+(delta>=0?'+':'')+delta.toFixed(6)+' percentage points'
    +' · projector/band residual '+w.e47_band_parity_residual.toExponential(3);
}

worker.onmessage=e=>{
  const x=e.data;
  if(!x.ok){log('ERROR '+x.error);prismPending=false;return;}
  last=x;
  $('norm').textContent=x.norm.toFixed(7);
  $('bond').textContent=x.maxBond;
  $('discard').textContent=x.discard.toExponential(2);
  $('events').textContent=x.noise?.events??0;
  $('bars').innerHTML=x.lastS.map(s=>'<div class="bar" style="height:'+Math.max(2,100*s/(x.lastS[0]||1))+'%"></div>').join('');
  log(new Date().toISOString()+' · '+x.engine+' · '+x.backend+' · χ='+x.maxBond+' · noise='+x.noise.model+' events='+x.noise.events+(x.validation?' · dense Δ='+x.validation.relative_l2.toExponential(3):''));
  if(prismPending){
    prismPending=false;
    lift();
  }
};

function run(){
  const c=config();
  drawCircuit(c);
  worker.postMessage(c);
}

function feature125(){
  if(!last?.statevector)throw Error('Run ≤16 qubits to materialize amplitudes for the 125 feature lift.');
  const v=last.statevector,N=v.length,out=[];
  for(let i=0;i<125;i++){
    const j=Math.floor(i*(N-1)/124),z=v[j];
    out.push([z[0],z[1]]);
  }
  const n=Math.sqrt(out.reduce((s,z)=>s+z[0]*z[0]+z[1]*z[1],0))||1;
  return out.map(z=>[z[0]/n,z[1]/n]);
}

async function lift(){
  try{
    const statevector=feature125(),c=config();
    const circuit={
      schema:'MATRIX-CIRCUIT-3.0',
      engine:'two-site-mps-worker',
      ...c,
      lift:{
        name:'sampled-amplitude-feature-lift-125-v3',
        source_dimension:2**c.n,
        target_dimension:125,
        claim:'explicit normalized feature map; not Hilbert-space isomorphism'
      }
    };
    const r=await fetch('https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/matrix-cube-adapter',{
      method:'POST',
      headers:{'content-type':'application/json'},
      body:JSON.stringify({statevector,circuit})
    });
    const x=await r.json();
    if(!x.ok)throw Error(x.error);
    const w=x.witness.witness;
    $('e47').textContent=(100*w.e47_weight).toFixed(3)+'% E47';
    $('e47detail').textContent='complement '+(100*w.complement_weight).toFixed(3)+'% · K² '+w.k2_energy.toExponential(3)+' · typed 125 feature vector';
    renderPrism(w);
    const city=await cityAdapter.ingest({statevector,circuit,e47Witness:w});
    window.parent.postMessage({type:'CITY_MATRIX_STATE',statevector,circuit,city_packet:city.packet,aetheris_receipt:city.receipt},'*');
    log('125-LIFT · E47 witness '+x.witness.object.state_hash.slice(0,16)+' · spectral Σ '+w.spectral_weight_sum.toFixed(12)+' · CITY '+city.city.carrier+' · receipt '+city.receipt.status);
  }catch(e){
    $('e47').textContent='LIFT ERROR';
    $('e47detail').textContent=e.message;
    $('prismdetail').textContent='PRISM ERROR · '+e.message;
  }
}

function prismTest(){
  $('n').value=8;
  $('layers').value=24;
  $('chi').value=16;
  $('phi').value=.7;
  $('entangler').value='brickwork';
  $('noise').value='none';
  $('g1').value=0;
  $('gphi').value=0;
  $('seed').value=47125;
  prismPending=true;
  $('prismdetail').textContent='Running certified 8q · 24 layer · χ16 · φ0.7 beam through the E47 prism…';
  log('E47 PRISM TEST · certified MATRIX configuration');
  run();
}

$('run').onclick=run;
$('lift').onclick=lift;
$('prismtest').onclick=prismTest;
run();
