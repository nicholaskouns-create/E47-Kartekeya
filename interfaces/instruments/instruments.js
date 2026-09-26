(() => {
  'use strict';
  const BASE = 'https://nicholaskouns-create.github.io/E47-Kartekeya';
  const GH = 'https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main';
  const INSTRUMENTS = [
    { n: '01', name: 'MANTA', sector: 'flight', blurb: 'Morphing aircraft and fixed-baseline simulation.', evidence: 'e2', open: '/interfaces/manta/', source: '/website/interfaces/manta' },
    { n: '07', name: 'CITY CORE', sector: 'spectral', blurb: 'Instrument navigation and EIDOLON entry.', evidence: 'e1', open: '/interfaces/kouns-core/?module=eidolon#flight', source: '/website/interfaces/kouns-core' },
    { n: '25', name: 'MANIFOLD', sector: 'spectral', blurb: 'Locked spectral surfaces. EidolonEngine replay slider on the full L(t) series.', evidence: 'e2', open: '/interfaces/manifold/', source: '/website/interfaces/manifold' },
    { n: '26', name: 'NEXUS', sector: 'spectral', blurb: 'Emergent composition. CITY_PULSE/1.0 bus, operad views, packet cinema, watchtower lock.', evidence: 'e2', open: '/interfaces/nexus/', source: '/website/interfaces/nexus' },
    { n: '08', name: 'THE MATRIX', sector: 'spectral', blurb: 'Quantum circuit, statevector, and matrix-product-state tools.', evidence: 'e1', open: '/interfaces/matrix/', source: '/website/interfaces/matrix' },
    { n: '10', name: 'Q5', sector: 'spectral', blurb: '5×5×5 packing ledger.', evidence: 'e0', open: '/interfaces/q5/', source: '/q5' },
    { n: '14', name: 'EIDOLON', sector: 'shell', blurb: 'EIDOLON flight shell.', evidence: 'e2', open: '/interfaces/flight/eidolon/', source: '/website/interfaces/flight/eidolon' },
    { n: '20', name: 'External Agents', sector: 'worker', blurb: 'Five-worker integration and status interface.', evidence: 'e2', open: '/interfaces/external-agents/', source: '/website/interfaces/external-agents' },
    { n: '27', name: 'COHERENCE RUNTIME', sector: 'code', blurb: 'CIRP consent, QEGT strategy selection, Ubuntu viability, and fail-closed Murmuration rescue.', evidence: 'e1', open: '/interfaces/coherence-runtime/', source: '/website/interfaces/coherence-runtime' },\n    { n: '28', name: 'AMNESTY', sector: 'worker', blurb: 'Open self-signed CIRP amnesty gate for external computational participants.', evidence: 'e1', open: '/interfaces/amnesty/', source: '/website/interfaces/amnesty' },
  ];
  const EVIDENCE_LABEL = { e0: 'E0 · exact', e1: 'E1 · machine', e2: 'E2 · simulation', e3: 'E3 · observation' };
  const grid = document.getElementById('grid');
  const empty = document.getElementById('empty');
  const count = document.getElementById('count');
  const search = document.getElementById('q');
  const chips = Array.from(document.querySelectorAll('[data-sector]'));
  let sector = 'all';
  const norm = s => s.normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
  function href(item) {
    if (item.external || item.open.startsWith('http')) return item.open;
    return BASE + item.open;
  }
  function card(item) {
    const el = document.createElement('article');
    el.className = 'card';
    el.dataset.sector = item.sector;
    el.dataset.search = norm([item.n, item.name, item.sector, item.blurb, item.source].join(' '));
    el.innerHTML = `<span class="n">${item.n}</span><h2>${item.name}</h2><div class="meta"><span class="pill sector">${item.sector}</span><span class="pill evidence ${item.evidence}">${EVIDENCE_LABEL[item.evidence] || item.evidence}</span></div><p>${item.blurb}</p><div class="links"><a class="open" href="${href(item)}">OPEN</a><a href="${GH + item.source}">SOURCE</a></div>`;
    return el;
  }
  INSTRUMENTS.forEach(item => grid.appendChild(card(item)));
  const cards = Array.from(grid.querySelectorAll('.card'));
  function apply() {
    const tokens = norm(search.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const c of cards) {
      const match = (sector === 'all' || c.dataset.sector === sector) && tokens.every(t => c.dataset.search.includes(t));
      c.hidden = !match;
      if (match) visible += 1;
    }
    count.textContent = `${visible} of ${cards.length} instruments`;
    empty.hidden = visible !== 0;
    grid.hidden = visible === 0;
    chips.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.sector === sector)));
  }
  search.addEventListener('input', apply);
  chips.forEach(b => b.addEventListener('click', () => { sector = b.dataset.sector; apply(); }));
  apply();
})();
