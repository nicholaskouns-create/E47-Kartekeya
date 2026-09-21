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

// Legacy curated-grid contract remains machine-testable, while the Atlas itself
// publishes the expanded 12-lab morphism sequence directly in HTML.
const legacyGrid = document.getElementById('lab-grid');
if (legacyGrid) {
  legacyGrid.innerHTML = LABS.map(lab => `
    <a class="lab-card" href="${lab.url}">
      <span class="role">${lab.role}</span>
      <h3>${lab.name}</h3>
      <p>${lab.desc}</p>
      <span class="open">OPEN ↗</span>
    </a>
  `).join('');
}

if (typeof document.querySelector === 'function' && typeof document.querySelectorAll === 'function') {
  (() => {
    const qs = (s) => document.querySelector(s);
    const qsa = (s) => Array.from(document.querySelectorAll(s));

    const filter = qs('#catalog-filter');
    if (filter) {
      const rows = qsa('[data-catalog] a');
      filter.addEventListener('input', () => {
        const q = filter.value.trim().toLowerCase();
        rows.forEach((row) => {
          row.hidden = Boolean(q) && !row.textContent.toLowerCase().includes(q);
        });
      });
    }

    const navLinks = qsa('.topbar nav a[href^="#"]');
    const sections = qsa('.atlas-page[id], main > section[id]');
    if ('IntersectionObserver' in window && navLinks.length) {
      const byHash = new Map(navLinks.map(a => [a.getAttribute('href'), a]));
      const observer = new IntersectionObserver((entries) => {
        const visible = entries
          .filter(e => e.isIntersecting)
          .sort((a,b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (!visible) return;
        navLinks.forEach(a => a.classList.remove('active'));
        const link = byHash.get('#' + visible.target.id);
        if (link) link.classList.add('active');
      }, {rootMargin:'-35% 0px -55% 0px', threshold:[0,.1,.5]});
      sections.forEach(s => observer.observe(s));
    }

    const kernelCanvas = qs('#kernel-chart');
    const leakCanvas = qs('#leak-chart');
    if (!kernelCanvas || !leakCanvas) return;

    const play = qs('#lock-play');
    const reset = qs('#lock-reset');
    const tRead = qs('#lock-t');
    const weightRead = qs('#lock-weight');
    const leakRead = qs('#lock-leak');

    const P0 = 47 / 125;
    const C0 = 1 - P0;
    const Q = 15 / 17;
    const TMAX = 150;
    const RECORDED_LOCK = 55;
    let t = 0;
    let timer = null;

    function boundAt(step) {
      const r = Math.pow(Q, 2 * step);
      const denom = P0 + C0 * r;
      return {
        weightFloor: P0 / denom,
        leakCeil: (C0 * r) / denom
      };
    }

    function fitCanvas(canvas) {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = Math.max(320, Math.round(rect.width * dpr));
      const h = Math.max(220, Math.round(rect.height * dpr));
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
      return {ctx:canvas.getContext('2d'), w, h, dpr};
    }

    function css(name) {
      return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
    }

    function basePlot(canvas, titleRight) {
      const {ctx,w,h,dpr} = fitCanvas(canvas);
      ctx.clearRect(0,0,w,h);
      const pad = {l:44*dpr,r:18*dpr,t:18*dpr,b:34*dpr};
      const pw = w-pad.l-pad.r, ph = h-pad.t-pad.b;
      ctx.strokeStyle = '#1f2a2f';
      ctx.lineWidth = dpr;
      ctx.font = `${8*dpr}px IBM Plex Mono, monospace`;
      ctx.fillStyle = '#657478';
      ctx.textAlign = 'center';
      [0,30,60,90,120,150].forEach(v => {
        const x = pad.l + pw*(v/TMAX);
        ctx.beginPath();ctx.moveTo(x,pad.t);ctx.lineTo(x,pad.t+ph);ctx.stroke();
        ctx.fillText(String(v),x,h-12*dpr);
      });
      ctx.textAlign='left';
      ctx.fillText(titleRight,pad.l,12*dpr);
      return {ctx,w,h,dpr,pad,pw,ph};
    }

    function drawKernel() {
      const p = basePlot(kernelCanvas,'Tr(P_E47 ρ) lower envelope');
      const {ctx,dpr,pad,pw,ph} = p;
      [0,.25,.5,.75,1].forEach(v => {
        const y=pad.t+ph*(1-v);
        ctx.strokeStyle='#1f2a2f';ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+pw,y);ctx.stroke();
        ctx.fillStyle='#657478';ctx.textAlign='right';ctx.fillText(v.toFixed(2),pad.l-7*dpr,y+3*dpr);
      });
      ctx.strokeStyle=css('--mint') || '#c1e8ce';
      ctx.lineWidth=2*dpr;
      ctx.beginPath();
      for(let s=0;s<=TMAX;s++){
        const b=boundAt(s);
        const x=pad.l+pw*(s/TMAX);
        const y=pad.t+ph*(1-b.weightFloor);
        if(s===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
      }
      ctx.stroke();

      const markerX=pad.l+pw*(RECORDED_LOCK/TMAX);
      ctx.strokeStyle=css('--bronze') || '#bc9c6c';
      ctx.setLineDash([5*dpr,5*dpr]);
      ctx.beginPath();ctx.moveTo(markerX,pad.t);ctx.lineTo(markerX,pad.t+ph);ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle=css('--bronze') || '#bc9c6c';ctx.textAlign='left';ctx.fillText('recorded lock t=55',markerX+5*dpr,pad.t+12*dpr);

      const b=boundAt(t);
      const x=pad.l+pw*(t/TMAX),y=pad.t+ph*(1-b.weightFloor);
      ctx.fillStyle=css('--cyan') || '#6edfd4';
      ctx.beginPath();ctx.arc(x,y,4*dpr,0,Math.PI*2);ctx.fill();
    }

    function drawLeak() {
      const p = basePlot(leakCanvas,'log10 leakage upper envelope');
      const {ctx,dpr,pad,pw,ph} = p;
      const minLog=-16,maxLog=0;
      [0,-4,-8,-12,-16].forEach(v => {
        const y=pad.t+ph*((maxLog-v)/(maxLog-minLog));
        ctx.strokeStyle='#1f2a2f';ctx.beginPath();ctx.moveTo(pad.l,y);ctx.lineTo(pad.l+pw,y);ctx.stroke();
        ctx.fillStyle='#657478';ctx.textAlign='right';ctx.fillText(v===0?'1':'1e'+v,pad.l-7*dpr,y+3*dpr);
      });

      ctx.strokeStyle=css('--cyan') || '#6edfd4';
      ctx.lineWidth=2*dpr;
      ctx.beginPath();
      for(let s=0;s<=TMAX;s++){
        const b=boundAt(s);
        const lv=Math.max(minLog,Math.log10(Math.max(b.leakCeil,1e-18)));
        const x=pad.l+pw*(s/TMAX);
        const y=pad.t+ph*((maxLog-lv)/(maxLog-minLog));
        if(s===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
      }
      ctx.stroke();

      const markerX=pad.l+pw*(RECORDED_LOCK/TMAX);
      ctx.strokeStyle=css('--bronze') || '#bc9c6c';
      ctx.setLineDash([5*dpr,5*dpr]);
      ctx.beginPath();ctx.moveTo(markerX,pad.t);ctx.lineTo(markerX,pad.t+ph);ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle=css('--bronze') || '#bc9c6c';ctx.textAlign='left';ctx.fillText('seed-42 lock marker',markerX+5*dpr,pad.t+12*dpr);

      const b=boundAt(t);
      const lv=Math.max(minLog,Math.log10(Math.max(b.leakCeil,1e-18)));
      const x=pad.l+pw*(t/TMAX);
      const y=pad.t+ph*((maxLog-lv)/(maxLog-minLog));
      ctx.fillStyle=css('--mint') || '#c1e8ce';
      ctx.beginPath();ctx.arc(x,y,4*dpr,0,Math.PI*2);ctx.fill();
    }

    function formatSci(x) {
      if (!Number.isFinite(x) || x === 0) return '0';
      if (x >= 1e-3) return x.toFixed(6);
      return x.toExponential(1).replace('e+','e');
    }

    function render() {
      const b=boundAt(t);
      if (tRead) tRead.textContent=`${t} / ${TMAX}`;
      if (weightRead) weightRead.textContent=b.weightFloor.toFixed(6);
      if (leakRead) leakRead.textContent=formatSci(b.leakCeil);
      drawKernel();drawLeak();
    }

    function stop() {
      if (timer) clearInterval(timer);
      timer=null;
      if (play) play.textContent=t>=TMAX?'Replay plate':'Play plate';
    }

    function start() {
      stop();
      if (t>=TMAX) t=0;
      if (play) play.textContent='Pause';
      timer=setInterval(() => {
        t=Math.min(TMAX,t+1);
        render();
        if(t>=TMAX) stop();
      },28);
    }

    if (play) play.addEventListener('click', () => {
      if (timer) stop(); else start();
    });
    if (reset) reset.addEventListener('click', () => {
      stop();t=0;render();
    });
    window.addEventListener('resize', render, {passive:true});
    render();
  })();
}
