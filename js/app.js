const LABS = [
  {name:'SPECTRA', role:'Structure', desc:'Spectra, modes, and invariant structure.', url:'interfaces/visualizers/?lab=spectra'},
  {name:'Fold', role:'Invariance', desc:'Contraction geometry and stable structure.', url:'interfaces/visualizers/?lab=fold'},
  {name:'Murmuration', role:'Dynamics', desc:'Many-body organization and topology.', url:'interfaces/visualizers/?lab=murmuration'},
  {name:'Mnemosyne', role:'Memory', desc:'Provenance, hashes, corrections, and forecasts.', url:'interfaces/visualizers/?lab=mnemosyne'},
  {name:'Density', role:'Measurement', desc:'Reconstruction from incomplete observations.', url:'interfaces/visualizers/?lab=density'},
  {name:'Horizon', role:'Prediction', desc:'Forecasting instruments with evidence boundaries.', url:'interfaces/visualizers/?lab=horizon'},
  {name:'Wave', role:'Flow', desc:'Field and flow simulation surfaces.', url:'interfaces/visualizers/?lab=wave'},
  {name:'InvariFold', role:'Geometry', desc:'Cinematic geometry for Fold payloads.', url:'interfaces/visualizers/?lab=invarifold'}
];

const grid = document.getElementById('lab-grid');

if (grid) {
  grid.innerHTML = LABS.map(lab => `
    <a class="lab-card" href="${lab.url}">
      <span class="role">${lab.role}</span>
      <h3>${lab.name}</h3>
      <p>${lab.desc}</p>
      <span class="open">OPEN ↗</span>
    </a>
  `).join('');
}