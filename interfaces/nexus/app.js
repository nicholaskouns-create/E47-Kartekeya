    const HOST = "https://nicholaskouns-create.github.io/E47-Kartekeya";
    const DOORS = [
      ["CITY LIVE", HOST + "/interfaces/city-live/"],
      ["MANIFOLD", HOST + "/interfaces/manifold/"],
      ["EIDOLON", HOST + "/interfaces/flight/eidolon/"],
      ["Q5", HOST + "/interfaces/q5/"],
      ["Kartekeya", "https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/kartekeya"],
      ["SEE", "https://gpkjvihkyectnenvnbng.supabase.co/functions/v1/city-app-host/see/"]
    ];
    const OCTET_PATH = ["SPECTRA","Fold","Density","Murmuration","Horizon","Mnemosyne","Wave","Identity","REVEAL"];
    const PENDING = new Set(["BUILD","SOAR"]);
    const COPROCESSOR = new Set(["SCALAR","EIDOLON","InvariFold","Cube"]);
    const LAW = new Set(["Constitution","Citadel","Control Plane","Monorail","Sol","Path"]);
    const MACHINES = [
      { roman:"I", name:"Prospective", question:"What invariant is about to exist?",
        product:["SPECTRA","Fold","Murmuration","Density","Horizon","Mnemosyne"],
        evidence:"E2", note:"forecast vs sealed prior" },
      { roman:"II", name:"Persistence", question:"What remains after perturbation?",
        product:["Wave","Identity","REVEAL","SCORE"],
        evidence:"E2", note:"Wave only after Mnemosyne seal" },
      { roman:"III", name:"Construction", question:"How does structure assemble around an invariant?",
        product:["SPECTRA","BUILD","SCALAR","Cube"],
        evidence:"E2", note:"adapter pending on BUILD" },
      { roman:"IV", name:"Restoration", question:"Can a degraded sector be restored without leaving itself?",
        product:["SOAR","SEE","Mnemosyne","Identity"],
        evidence:"E2", note:"adapter pending on SOAR" },
      { roman:"V", name:"Protein Cinema", question:"Can a sequence be contracted onto a spectral basin?",
        product:["Fold","InvariFold","Γ"],
        evidence:"E2", note:"cinema bound · not AF3 parity" },
      { roman:"VI", name:"Field", question:"What geometry does the kernel induce, flown as simulation?",
        product:["SCALAR","Eidolon","SOAR"],
        evidence:"E2", note:"no physical promotion" },
      { roman:"VII", name:"Civic Kernel", question:"How does a claim become a citizen?",
        product:["Constitution","Citadel","Control Plane","Monorail","Sol","Path"],
        evidence:"law", note:"operating law · not a packet morphism" },
      { roman:"—", name:"Packing Address", question:"Where does a word sit on the 125-cell ledger?",
        product:["Q5"],
        evidence:"E0 packing", note:"π(x,y,z)=25x+5y+z · not ker K" },
      { roman:"VIII", name:"Proof Forge", question:"What is certified?",
        product:["SEE","lock cards"],
        evidence:"E0/E1 labels only", note:"inspection functor, not a stage" },
      { roman:"IX", name:"City OS", question:"What composition can no single lab be?",
        product:["Kartekeya","Octet bus","SEE","Civic Kernel","I–VIII"],
        evidence:"ceiling", note:"reader of products · not a second kernel" }
    ];
    const VIEWS = [
      ["nexus","NEXUS"],["cinema","Cinema"],["operad","Operad"],
      ["pulse","Pulse"],["watchtower","Watchtower"],["lock","Lock card"]
    ];
    const FALLBACK = {
      lock: { line: "[LOCK] PASS  dimH=125  dimE47=47  rankK=78  Omega_c=47/125  Delta=11664  kappa=16  rho=15/17  TrP47=47", passed:true, dim_H:125, dim_E47:47, rank_K:78, omega_frac:"47/125", Delta:11664, kappa:16 },
      spectral: { J:[0,1,2,3,4,5,6], dim:[1,9,25,28,27,22,13], lambda:[0,2,6,12,20,30,42], mu2:[32400,12544,0,11664,19600,0,186624], P47:[0,0,1,0,0,1,0] },
      domains: [{name:"RAND/Policy",theta:0},{name:"Defense",theta:45},{name:"MITRE",theta:90},{name:"Space",theta:135},{name:"Health",theta:180},{name:"AI",theta:225},{name:"Resilience",theta:270},{name:"Public Safety",theta:315}],
      eidolon: { mode:"translate", L:0.952, omega:0.442, m_eff:36.1, phase:"BURN", budget:0.89, stability:0.81, n:[0,0.001,0.506,0.047,0,0.446,0], t:36, series_n:1081 },
      tomo: { rel_l2:0.917, mass_ratio:2.635, mse:0.0043, gated:true }
    };
    const $ = (id) => document.getElementById(id);
    let STATE = FALLBACK;
    let PULSE = null;
    let OCTET = { path: OCTET_PATH.slice(), schema:"MC-OCTET-PACKET-1.0", pulses:[] };
    let TOWER = { line: FALLBACK.lock.line, passed:true, engines:{SpectralEngine:{present:true},EidolonEngine:{present:true},TomographicVisualizer:{present:true}}, routes:[] };
    let SERIES = { t:[0,12,24,36], L:[0.467,0.92,0.95,0.952], omega_t:[0.35,0.43,0.44,0.442], x:[0,40,160,400], y:[0,30,120,310], dt:1/30 };
    let frame = 0, timer = null;
    function viewOf() {
      const q = new URLSearchParams(location.search).get("view");
      const h = (location.hash||"").replace("#/","").replace("#","");
      const v = (q || h || "nexus").toLowerCase();
      return VIEWS.some(([k]) => k===v) ? v : "nexus";
    }
    function mark(name) {
      if (PENDING.has(name)) return `<span class="sq" title="pending adapter">□ ${name}</span>`;
      if (COPROCESSOR.has(name) || name === "Eidolon" || name === "Γ") return `<span class="co">${name}</span>`;
      if (LAW.has(name)) return `<span class="law">${name}</span>`;
      return `<span class="on">${name}</span>`;
    }
    function productLine(list) { return list.map(mark).join('<span class="op"> ⊗ </span>'); }
    function octetPath() { return (OCTET.path && OCTET.path.length ? OCTET.path : OCTET_PATH); }
    function legalStage(L, frac) {
      const path = octetPath();
      const wave = Math.max(0, path.indexOf("Wave"));
      let i = Math.round(frac * (path.length - 1));
      if (L < 0.376 && i >= wave) i = wave - 1;
      return { path, i: Math.max(0, Math.min(path.length - 1, i)), sealed: L >= 0.376 };
    }
    function stageTape(active, sealed) {
      const path = octetPath();
      return `<div class="stages">${path.map((s,i) => {
        const blocked = !sealed && i >= path.indexOf("Wave");
        const cls = blocked ? "blocked" : (i === active ? "on" : (i < active ? "done" : ""));
        return `<span class="stage ${cls}">${s}</span>`;
      }).join('<span class="arrow">→</span>')}</div>`;
    }
    function spark(canvas, ys, color) {
      if (!canvas || !ys || ys.length < 2) return;
      const ctx = canvas.getContext("2d");
      const w = canvas.width = canvas.clientWidth * 2;
      const h = canvas.height = canvas.clientHeight * 2;
      ctx.clearRect(0,0,w,h);
      const min = Math.min(...ys), max = Math.max(...ys);
      const span = Math.max(max-min, 1e-6);
      ctx.beginPath();
      ys.forEach((y,i) => {
        const x = i/(ys.length-1)*(w-8)+4;
        const yy = h-6-((y-min)/span)*(h-12);
        i ? ctx.lineTo(x,yy) : ctx.moveTo(x,yy);
      });
      ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.stroke();
      if (min <= 0.376 && 0.376 <= max) {
        const y = h-6-((0.376-min)/span)*(h-12);
        ctx.strokeStyle = "#F43F5E"; ctx.setLineDash([6,6]);
        ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(w,y); ctx.stroke(); ctx.setLineDash([]);
      }
    }
    function pathCanvas(canvas, x, y) {
      if (!canvas || !x) return;
      const ctx = canvas.getContext("2d");
      const w = canvas.width = canvas.clientWidth * 2;
      const h = canvas.height = canvas.clientHeight * 2;
      ctx.fillStyle = "#0B1220"; ctx.fillRect(0,0,w,h);
      const xmin = Math.min(...x,-1), xmax = Math.max(...x,1);
      const ymin = Math.min(...y,-1), ymax = Math.max(...y,1);
      ctx.beginPath();
      x.forEach((xv,i) => {
        const px = 8+(xv-xmin)/Math.max(xmax-xmin,1e-6)*(w-16);
        const py = h-8-(y[i]-ymin)/Math.max(ymax-ymin,1e-6)*(h-16);
        i ? ctx.lineTo(px,py) : ctx.moveTo(px,py);
      });
      ctx.strokeStyle = "#39f3ef"; ctx.lineWidth = 3; ctx.stroke();
    }
    function metrics() {
      const L = STATE.lock;
      return `<div class="card span-3"><div class="k">dim H</div><div class="v">${L.dim_H}</div></div><div class="card span-3"><div class="k">dim E47</div><div class="v mint">${L.dim_E47}</div></div><div class="card span-3"><div class="k">rank K</div><div class="v">${L.rank_K}</div></div><div class="card span-3"><div class="k">Ω_c</div><div class="v ghost">${L.omega_frac}</div></div>`;
    }
    function sectorBars(vals) {
      const p47 = STATE.spectral.P47;
      const v = vals || STATE.spectral.dim.map(d => d/125);
      return `<div class="bars">${v.map((x,i)=>`<div class="bar"><span>J=${i}</span><i><b class="${p47[i]?'ker':''}" style="width:${Math.min(100,x*100).toFixed(1)}%"></b></i><span>${Number(x).toFixed(3)}</span></div>`).join("")}</div>`;
    }
    function doors() {
      return `<div class="doors">${DOORS.map(([n,u])=>`<a href="${u}" target="_blank" rel="noopener">${n} ↗</a>`).join("")}</div>`;
    }
    function sectorTable() {
      const s = STATE.spectral;
      return `<table><thead><tr><th>J</th><th>dim</th><th>λ</th><th>μ²</th><th>sector</th></tr></thead><tbody>${s.J.map((J,i)=>`<tr class="${s.P47[i]?'ker':''}"><td>${J}</td><td>${s.dim[i]}</td><td>${s.lambda[i]}</td><td>${s.mu2[i]}</td><td>${s.P47[i]?'KER E47':'perp'}</td></tr>`).join("")}</tbody></table>`;
    }
    function nexusView() {
      const e = STATE.eidolon, t = STATE.tomo;
      return `<div class="grid">${metrics()}<div class="card span-4"><div class="k">Left · EidolonEngine</div><div class="v mint">${Number(e.L).toFixed(3)}</div><p class="k">L · Ω ${Number(e.omega).toFixed(3)} · ${e.phase} · engine owns ODE</p><canvas id="cL"></canvas><canvas id="cXY"></canvas></div><div class="card span-4"><div class="phone"><div class="k">Center · Density / tomo</div><h2 style="letter-spacing:.12em">P47 GATE</h2><div class="v mint">${t.gated ? "ON" : "OPEN SLOT"}</div><p class="k">rel L2 ${Number(t.rel_l2).toFixed(3)} · mass ratio ${Number(t.mass_ratio).toFixed(3)}</p>${sectorBars(e.n)}</div></div><div class="card span-4"><div class="k">Right · City console</div><h2 style="margin:6px 0 0;letter-spacing:.12em">125 → 47</h2>${sectorTable()}${STATE.domains.map(d=>`<div class="dom"><b>${d.name}</b><span>${d.theta}°</span></div>`).join("")}</div><div class="card span-12"><div class="k">Bottom · CITY_PULSE readout of MC-OCTET-PACKET-1.0</div><div class="tape" id="tape"></div><div style="height:10px"></div>${doors()}</div></div>`;
    }
    function cinemaView() {
      return `<div class="grid"><div class="card span-12"><div class="k">Packet cinema · Octet-legal stage order</div><p>One t. Four traces. Stage cursor may not enter Wave until L ≥ Ω_c (Mnemosyne seal). Not a unified PDE.</p><div id="stageTape"></div><div class="replay"><div class="row"><span>shared clock · executable path only</span><span id="replayRead">t=0</span></div><input id="replay" type="range" min="0" max="1" value="1" step="1" /><div class="modes"><button type="button" id="replayPlay">play</button><button type="button" id="replayPause">pause</button><button type="button" id="replayReset">reset</button></div></div></div><div class="card span-3"><div class="k">Eidolon L</div><div class="v mint" id="cinL">—</div></div><div class="card span-3"><div class="k">Ω</div><div class="v" id="cinO">—</div></div><div class="card span-3"><div class="k">complement</div><div class="v ghost" id="cinC">—</div></div><div class="card span-3"><div class="k">Octet stage</div><div class="v" id="cinS" style="font-size:18px">—</div></div><div class="card span-6"><div class="k">L(t) vs Ω_c</div><canvas id="cL"></canvas></div><div class="card span-6"><div class="k">Trajectory</div><canvas id="cXY"></canvas></div></div>`;
    }
    function operadView() {
      const cards = MACHINES.map(m => {
        const holes = m.product.filter(p => PENDING.has(p));
        const open = holes.length || m.name === "Civic Kernel";
        return `<div class="card span-6 ${open?'open':''}"><div class="k">${m.roman} · ${m.evidence}</div><h3 style="margin:8px 0 6px;letter-spacing:.08em">${m.name}</h3><div class="product">${productLine(m.product)}</div><p style="margin:10px 0 6px">${m.question}</p><p class="k">${m.note}${holes.length ? " · □ pending adapter" : ""}</p></div>`;
      }).join("");
      return `<div class="grid"><div class="card span-12"><div class="k">Operad console · labs are morphisms · machines are products</div><p>Full City product on every card. □ is a missing adapter, not a live child. Civic Kernel is law. Q5 is address. Evidence is a ceiling.</p><p class="k">MC-OCTET-PACKET-1.0 · ${octetPath().join(" → ")}</p></div>${cards}</div>`;
    }
    function pulseView() {
      const p = PULSE || {};
      const parent = OCTET.schema || "MC-OCTET-PACKET-1.0";
      return `<div class="grid"><div class="card span-12"><div class="k">CITY_PULSE / 1.0 · readout seal</div><p>Reads <b>${parent}</b>. Does not replace the append-only chain. Horizon reads the seal. Wave does not invent a second hash lineage.</p></div><div class="card span-3"><div class="k">run</div><div class="v" style="font-size:16px">${p.run_id||"—"}</div></div><div class="card span-3"><div class="k">L</div><div class="v mint">${p.L!=null?Number(p.L).toFixed(3):"—"}</div></div><div class="card span-3"><div class="k">source</div><div class="v" style="font-size:18px">${p.source_app||"—"}</div></div><div class="card span-3"><div class="k">class</div><div class="v ghost">${p.evidence_class||"E2"}</div></div><div class="card span-6"><div class="k">parent chain</div><p class="seal">${parent}</p></div><div class="card span-6"><div class="k">readout SHA-256</div><p class="seal">${p.seal||"—"}</p></div><div class="card span-12"><div class="k">octet receipts · same t · not a new conductor</div><table><thead><tr><th>stage</th><th>class</th><th>seal</th></tr></thead><tbody>${(OCTET.pulses||[]).filter(r => octetPath().includes(r.source_app) || r.source_app==="REVEAL").map(r=>`<tr><td>${r.source_app}</td><td>${r.evidence_class}</td><td class="seal">${(r.seal||"").slice(0,16)}…</td></tr>`).join("")}</tbody></table></div><div class="card span-12 tape">${JSON.stringify({schema:"CITY_PULSE/1.0", reads:parent, replaces_chain:false, pulse:p},null,2)}</div></div>`;
    }
    function towerView() {
      const eng = TOWER.engines || {};
      return `<div class="grid"><div class="card span-12"><div class="k">Fidelity watchtower</div><p class="v mint" style="font-size:18px">${TOWER.line||STATE.lock.line}</p><p>FAIL stops the render. Routes are availability. Composition does not upgrade evidence class.</p></div>${Object.entries(eng).map(([n,e])=>`<div class="card span-4"><div class="k">${n}</div><div class="v mint">${e.present?'PRESENT':'OPEN'}</div><p class="k">${e.role||""}</p></div>`).join("")}<div class="card span-12">${doors()}</div></div>`;
    }
    function lockView() {
      const L = STATE.lock;
      return `<div class="card span-12" style="border-color:#39f3ef"><div style="display:flex;justify-content:space-between;align-items:baseline"><h2 style="margin:0;letter-spacing:.14em">NEXUS</h2><div class="v mint">PASS</div></div><p class="k">LOCK CARD · MATHEMATICAL CITY · E47 / KKP-R</p><div class="grid" style="margin-top:12px">${metrics()}<div class="card span-3"><div class="k">Δ</div><div class="v">${L.Delta}</div></div><div class="card span-3"><div class="k">κ</div><div class="v">${L.kappa}</div></div><div class="card span-3"><div class="k">ρ</div><div class="v ghost">15/17</div></div><div class="card span-3"><div class="k">Tr P47</div><div class="v mint">47</div></div></div><p class="k" style="margin-top:16px">Import, do not re-derive. Labs are morphisms. Machines are products. Seals are commits.</p></div>`;
    }
    function applyFrame(i) {
      const n = SERIES.t.length; if (!n) return;
      frame = Math.max(0, Math.min(n-1, i));
      const L = SERIES.L[frame], om = SERIES.omega_t[frame], t = SERIES.t[frame];
      const comp = Math.max(0, Math.round(78*(1-L)));
      const frac = n<=1 ? 1 : frame/(n-1);
      const st = legalStage(L, frac);
      const sl = $("replay"), rd = $("replayRead");
      if (sl) sl.value = String(frame);
      if (rd) rd.textContent = `t=${Number(t).toFixed(2)} s  L=${Number(L).toFixed(3)}  ${frame+1}/${n}  ${st.sealed?"SEALED":"pre-seal"}`;
      const set = (id,v) => { const el=$(id); if(el) el.textContent=v; };
      set("cinL", Number(L).toFixed(3));
      set("cinO", Number(om).toFixed(3));
      set("cinC", String(comp));
      set("cinS", st.path[st.i]);
      const tape = $("stageTape");
      if (tape) tape.innerHTML = stageTape(st.i, st.sealed);
      spark($("cL"), SERIES.L.slice(0, frame+1), "#3DFF9A");
      pathCanvas($("cXY"), (SERIES.x||[]).slice(0, frame+1), (SERIES.y||[]).slice(0, frame+1));
    }
    function wireReplay() {
      const sl = $("replay"); if (!sl) return;
      sl.max = String(Math.max(0, SERIES.t.length-1));
      sl.oninput = () => { stop(); applyFrame(Number(sl.value)); };
      const play=$("replayPlay"), pause=$("replayPause"), reset=$("replayReset");
      if (play) play.onclick = () => { stop(); if (frame>=SERIES.t.length-1) frame=0; timer = setInterval(() => { applyFrame(frame+1); if (frame>=SERIES.t.length-1) stop(); }, 33); };
      if (pause) pause.onclick = stop;
      if (reset) reset.onclick = () => { stop(); applyFrame(0); };
      applyFrame(frame || SERIES.t.length-1);
    }
    function stop() { if (timer) clearInterval(timer); timer=null; }
    function paint() {
      const view = viewOf();
      $("lockStrip").textContent = (TOWER.line || STATE.lock.line);
      $("nav").innerHTML = VIEWS.map(([k,lab]) => `<a class="${k===view?'active':''}" href="?view=${k}#/${k}">${lab}</a>`).join("") + `<a href="lock.html">Lock HTML</a><a href="embed.html">Embed</a>`;
      const render = { nexus:nexusView, cinema:cinemaView, operad:operadView, pulse:pulseView, watchtower:towerView, lock:lockView };
      $("app").innerHTML = render[view]();
      const tape = $("tape");
      if (tape) tape.textContent = JSON.stringify({ schema:"CITY_PULSE/1.0", reads:"MC-OCTET-PACKET-1.0", replaces_chain:false, L:STATE.eidolon.L, omega:STATE.eidolon.omega, complement: Math.max(0, Math.round(78*(1-STATE.eidolon.L))), seal: PULSE && PULSE.seal, path: octetPath().join(" → ") });
      spark($("cL"), SERIES.L, "#3DFF9A");
      pathCanvas($("cXY"), SERIES.x, SERIES.y);
      if (view === "cinema" || view === "nexus") wireReplay();
    }
    async function boot() {
      const load = async (path, assign) => {
        try { const r = await fetch(path, {cache:"no-store"}); if (r.ok) assign(await r.json()); } catch(_){}
      };
      await load("data/state.json", d => { STATE = Object.assign(FALLBACK, d); });
      await load("data/pulse.json", d => { PULSE = d; });
      await load("data/octet.json", d => { OCTET = Object.assign(OCTET, d); });
      await load("data/watchtower.json", d => { TOWER = d; });
      await load("data/series.json", d => { SERIES = d; });
      if (!SERIES.t || SERIES.t.length < 8) await load("../manifold/data/series.json", d => { SERIES = d; });
      frame = Math.max(0, SERIES.t.length-1);
      paint();
      addEventListener("hashchange", paint);
    }
    boot();
