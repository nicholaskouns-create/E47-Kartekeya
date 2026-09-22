(() => {
  'use strict';

  const BASE = 'https://nicholaskouns-create.github.io/E47-Kartekeya';
  const GH = 'https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main';

  const INSTRUMENTS = [
    { n: '01', name: 'MANTA', sector: 'flight', blurb: 'Morphing aircraft and fixed-baseline simulation.', open: '/interfaces/manta/', source: '/website/interfaces/manta' },
    { n: '02', name: 'MANTA Daylight', sector: 'flight', blurb: 'Companion daylight flight view.', open: '/interfaces/manta-daylight/', source: '/website/interfaces/manta-daylight' },
    { n: '03', name: 'SKYRMION', sector: 'flight', blurb: 'WGS84 flight simulator with conventional and experimental models.', open: '/interfaces/skyrmion/', source: '/website/interfaces/skyrmion' },
    { n: '04', name: 'Syntax Jacob', sector: 'flight', blurb: '3I/ATLAS trajectory and propulsion lab.', open: '/interfaces/syntax-jacob/', source: '/website/interfaces/syntax-jacob' },
    { n: '05', name: 'UFO Propulsion', sector: 'flight', blurb: 'Native propulsion simulation interface.', open: '/interfaces/flight/ufo-propulsion/', source: '/website/interfaces/flight/ufo-propulsion' },
    { n: '06', name: 'Propulsion Atlas', sector: 'flight', blurb: 'Directory of propulsion apps and locations.', open: '/interfaces/propulsion/', source: '/website/interfaces/propulsion' },
    { n: '07', name: 'CITY CORE', sector: 'spectral', blurb: 'Instrument navigation and EIDOLON entry.', open: '/interfaces/kouns-core/?module=eidolon#flight', source: '/website/interfaces/kouns-core' },
    { n: '08', name: 'THE MATRIX', sector: 'spectral', blurb: 'Quantum circuit, statevector, and matrix-product-state tools.', open: '/interfaces/matrix/', source: '/website/interfaces/matrix' },
    { n: '09', name: 'CITY 125', sector: 'spectral', blurb: '125-state visual debugger.', open: '/interfaces/city-125/', source: '/website/interfaces/city-125' },
    { n: '10', name: 'Q5', sector: 'spectral', blurb: '5×5×5 packing ledger. Executable cube/torus neighbors. Live slice/topology panel.', open: '/interfaces/q5/', source: '/q5' },
    { n: '11', name: 'THE CUBE', sector: 'spectral', blurb: 'Modular Cube platform interface.', open: '/interfaces/cube-platform/', source: '/website/interfaces/cube-platform' },
    { n: '12', name: 'Visualizers', sector: 'spectral', blurb: 'Portal for independent research visualizers.', open: '/interfaces/visualizers/', source: '/website/interfaces/visualizers' },
    { n: '13', name: 'WebGL Lab', sector: 'spectral', blurb: 'Browser graphics instrument.', open: '/interfaces/webgl/', source: '/website/interfaces/webgl' },
    { n: '14', name: 'EIDOLON', sector: 'shell', blurb: 'EIDOLON flight shell.', open: '/interfaces/flight/eidolon/', source: '/website/interfaces/flight/eidolon' },
    { n: '15', name: 'EIDOLON Flight Lab', sector: 'shell', blurb: 'Companion shell embedding the EIDOLON route.', open: '/interfaces/eidolon-flight-lab/', source: '/website/interfaces/eidolon-flight-lab' },
    { n: '16', name: 'Eidolon Harmonic', sector: 'shell', blurb: 'Harmonic flight shell.', open: '/interfaces/flight/eidolon-harmonic/', source: '/website/interfaces/flight/eidolon-harmonic' },
    { n: '17', name: 'HOVER Assembly', sector: 'shell', blurb: 'Assembly interface shell.', open: '/interfaces/flight/hover-assembly/', source: '/website/interfaces/flight/hover-assembly' },
    { n: '18', name: 'HOVER Cockpit', sector: 'shell', blurb: 'Cockpit interface shell.', open: '/interfaces/flight/hover-cockpit/', source: '/website/interfaces/flight/hover-cockpit' },
    { n: '19', name: 'MAV', sector: 'shell', blurb: 'MAV console shell.', open: '/interfaces/flight/mav/', source: '/website/interfaces/flight/mav' },
    { n: '20', name: 'External Agents', sector: 'worker', blurb: 'Five-worker integration and status interface.', open: '/interfaces/external-agents/', source: '/website/interfaces/external-agents' },
    { n: '21', name: 'E47 Python core', sector: 'code', blurb: 'Finite kernel implementation. ker((C−6I)(C−30I)).', open: 'https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/src/e47', source: '/src/e47', external: true },
    { n: '22', name: 'AETHERIS', sector: 'code', blurb: 'State transitions and receipt machinery.', open: 'https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/src/aetheris', source: '/src/aetheris', external: true },
    { n: '23', name: 'MANTA Python model', sector: 'code', blurb: 'Programmable-matter model behind the flight lab.', open: 'https://github.com/nicholaskouns-create/E47-Kartekeya/tree/main/src/manta', source: '/src/manta', external: true },
    { n: '24', name: 'Component manifest', sector: 'code', blurb: 'lab-manifest.json — independent instruments, evidence classes, contracts.', open: 'https://github.com/nicholaskouns-create/E47-Kartekeya/blob/main/lab-manifest.json', source: '/lab-manifest.json', external: true }
  ];

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
    el.innerHTML = `
      <span class="n">${item.n}</span>
      <h2>${item.name}</h2>
      <div class="meta">
        <span class="pill sector">${item.sector}</span>
        <span class="pill">${item.source.replace(/^\//, '')}</span>
      </div>
      <p>${item.blurb}</p>
      <div class="links">
        <a class="open" href="${href(item)}">${item.external ? 'OPEN SOURCE' : 'OPEN'}</a>
        <a href="${GH + item.source}">SOURCE</a>
      </div>`;
    return el;
  }

  INSTRUMENTS.forEach(item => grid.appendChild(card(item)));
  const cards = Array.from(grid.querySelectorAll('.card'));

  function apply() {
    const tokens = norm(search.value.trim()).split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const c of cards) {
      const match = (sector === 'all' || c.dataset.sector === sector) &&
        tokens.every(t => c.dataset.search.includes(t));
      c.hidden = !match;
      if (match) visible += 1;
    }
    count.textContent = `${visible} of ${cards.length} instruments`;
    empty.hidden = visible !== 0;
    grid.hidden = visible === 0;
    chips.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.sector === sector)));
  }

  search.addEventListener('input', apply);
  search.addEventListener('keydown', e => {
    if (e.key === 'Escape') { search.value = ''; apply(); }
  });
  chips.forEach(b => b.addEventListener('click', () => { sector = b.dataset.sector; apply(); }));
  document.addEventListener('keydown', e => {
    if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.altKey && !e.target.closest('input,textarea,select')) {
      e.preventDefault();
      search.focus();
    }
  });
  apply();
})();
