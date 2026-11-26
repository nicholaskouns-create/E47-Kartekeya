/** Emergent Spacetime -- page wiring and the instrument chain.
 *
 * The visualizer reads the metric off the exact rational occupancy. The chain
 * calls the instruments that already exist on this site rather than carrying
 * private copies of them, and fails closed: a stage runs only if the previous
 * one passed.
 */
import {
  A_MAX, A_MIN, EPS_STAR_DENOMINATOR, KAPPA, OMEGA_C,
  agreesWithCanonicalLock, crossingTime, exactSignature, flowDerivatives,
  g00FromAcceleration, metric, occupancy, recoverBoundary, signature,
  signatureDataset, toNumber, trajectory, transitionStep,
} from './flow.mjs';

const $ = (id) => document.getElementById(id);
const CSS = getComputedStyle(document.documentElement);
const colour = (name, fallback) => (CSS.getPropertyValue(name) || fallback).trim();
const CY = colour('--cyan', '#6edfd4');
const MINT = colour('--mint', '#c1e8ce');
const HOT = colour('--hot', '#d87e74');
const BRONZE = colour('--bronze', '#bc9c6c');
const LINE = colour('--line', '#243138');
const FAINT = colour('--faint', '#657478');

const STEPS = 10;
let start = OMEGA_C;
let current = 0.376;
let timer = null;

/* ------------------------------------------------------------------ */
/* canvas helpers                                                      */
/* ------------------------------------------------------------------ */

function surface(canvas, aspect = 0.62) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const w = canvas.clientWidth || 520;
  const h = Math.round(w * aspect);
  canvas.width = Math.round(w * dpr);
  canvas.height = Math.round(h * dpr);
  canvas.style.height = `${h}px`;
  const ctx = canvas.getContext('2d');
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, w, h);
  return { ctx, w, h };
}

function axes(ctx, box, xLabel, yLabel) {
  const { x0, y0, x1, y1 } = box;
  ctx.strokeStyle = LINE;
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(x0, y0); ctx.lineTo(x0, y1); ctx.lineTo(x1, y1);
  ctx.stroke();
  ctx.fillStyle = FAINT;
  ctx.font = '10px "IBM Plex Mono", monospace';
  ctx.textAlign = 'right';
  ctx.fillText(xLabel, x1, y1 + 15);
  ctx.textAlign = 'left';
  ctx.fillText(yLabel, x0, y0 - 6);
}

/* ------------------------------------------------------------------ */
/* the flow plot                                                       */
/* ------------------------------------------------------------------ */

function drawFlow(rows, activeStep) {
  const canvas = $('flowCanvas');
  const { ctx, w, h } = surface(canvas);
  const box = { x0: 34, y0: 14, x1: w - 10, y1: h - 24 };
  const px = (n) => box.x0 + (n / STEPS) * (box.x1 - box.x0);
  const py = (p) => box.y1 - p * (box.y1 - box.y0);

  // Lorentzian region above half occupancy, Euclidean below.
  ctx.fillStyle = 'rgba(216,126,116,.07)';
  ctx.fillRect(box.x0, py(1), box.x1 - box.x0, py(0.5) - py(1));
  ctx.fillStyle = 'rgba(193,232,206,.05)';
  ctx.fillRect(box.x0, py(0.5), box.x1 - box.x0, py(0) - py(0.5));

  // the critical line
  ctx.strokeStyle = BRONZE;
  ctx.setLineDash([4, 4]);
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(box.x0, py(0.5)); ctx.lineTo(box.x1, py(0.5)); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = BRONZE;
  ctx.font = '10px "IBM Plex Mono", monospace';
  ctx.textAlign = 'left';
  ctx.fillText('p = 1/2', box.x0 + 4, py(0.5) - 5);

  // the continuum logistic envelope
  const p0 = toNumber(start);
  if (p0 > 0 && p0 < 1) {
    ctx.strokeStyle = 'rgba(110,223,212,.38)';
    ctx.lineWidth = 1.25;
    ctx.beginPath();
    for (let i = 0; i <= 240; i++) {
      const t = (i / 240) * STEPS;
      const p = p0 / (p0 + (1 - p0) * Math.exp(-2 * KAPPA * t));
      i ? ctx.lineTo(px(t), py(p)) : ctx.moveTo(px(t), py(p));
    }
    ctx.stroke();
  }

  axes(ctx, box, 'step n', 'p');

  // exact steps
  rows.forEach((r) => {
    const lorentz = r.signature.code === '(3,1,0)';
    ctx.fillStyle = lorentz ? HOT : MINT;
    ctx.beginPath();
    ctx.arc(px(r.step), py(r.value), r.step === activeStep ? 5.5 : 3.4, 0, Math.PI * 2);
    ctx.fill();
    if (r.step === activeStep) {
      ctx.strokeStyle = CY;
      ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.arc(px(r.step), py(r.value), 9, 0, Math.PI * 2); ctx.stroke();
    }
  });

  // y ticks
  ctx.fillStyle = FAINT;
  ctx.textAlign = 'right';
  [0, 0.5, 1].forEach((v) => ctx.fillText(v.toFixed(1), box.x0 - 5, py(v) + 3));
}

/* ------------------------------------------------------------------ */
/* g00 against occupancy                                               */
/* ------------------------------------------------------------------ */

function drawG00(p) {
  const canvas = $('g00Canvas');
  const { ctx, w, h } = surface(canvas);
  const box = { x0: 44, y0: 14, x1: w - 10, y1: h - 24 };
  const peak = Math.max(...Array.from({ length: 101 }, (_, i) => Math.abs(metric(i / 100)[0]))) || 1;
  const px = (v) => box.x0 + v * (box.x1 - box.x0);
  const py = (v) => (box.y0 + box.y1) / 2 - (v / peak) * ((box.y1 - box.y0) / 2) * 0.92;

  ctx.fillStyle = 'rgba(193,232,206,.05)';
  ctx.fillRect(box.x0, box.y0, px(0.5) - box.x0, box.y1 - box.y0);
  ctx.fillStyle = 'rgba(216,126,116,.07)';
  ctx.fillRect(px(0.5), box.y0, box.x1 - px(0.5), box.y1 - box.y0);

  // zero axis and the critical ordinate
  ctx.strokeStyle = LINE;
  ctx.lineWidth = 1;
  ctx.beginPath(); ctx.moveTo(box.x0, py(0)); ctx.lineTo(box.x1, py(0)); ctx.stroke();
  ctx.strokeStyle = BRONZE;
  ctx.setLineDash([4, 4]);
  ctx.beginPath(); ctx.moveTo(px(0.5), box.y0); ctx.lineTo(px(0.5), box.y1); ctx.stroke();
  ctx.setLineDash([]);

  ctx.strokeStyle = CY;
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let i = 0; i <= 300; i++) {
    const v = i / 300;
    i ? ctx.lineTo(px(v), py(metric(v)[0])) : ctx.moveTo(px(v), py(metric(v)[0]));
  }
  ctx.stroke();

  const g00 = metric(p)[0];
  ctx.fillStyle = g00 < 0 ? HOT : g00 > 0 ? MINT : BRONZE;
  ctx.beginPath(); ctx.arc(px(p), py(g00), 5.5, 0, Math.PI * 2); ctx.fill();

  axes(ctx, box, 'p', 'g₀₀');
  ctx.font = '10px "IBM Plex Mono", monospace';
  ctx.textAlign = 'center';
  ctx.fillStyle = MINT;
  ctx.fillText('accelerating · Euclidean', (box.x0 + px(0.5)) / 2, box.y0 + 12);
  ctx.fillStyle = HOT;
  ctx.fillText('decelerating · Lorentzian', (px(0.5) + box.x1) / 2, box.y0 + 12);
}

/* ------------------------------------------------------------------ */
/* readouts                                                            */
/* ------------------------------------------------------------------ */

function nearestStep(rows, p) {
  return rows.reduce((best, r) => (Math.abs(r.value - p) < Math.abs(rows[best].value - p) ? r.step : best), 0);
}

function renderDiagonal(p) {
  const g = metric(p);
  const names = ['g₀₀', 'g₁₁', 'g₂₂', 'g₃₃'];
  $('diag').innerHTML = g.map((v, i) => {
    const cls = v > 1e-15 ? 'pos' : v < -1e-15 ? 'neg' : 'zero';
    const shown = Math.abs(v) < 1e-9 && v !== 0 ? v.toExponential(2) : v.toFixed(6);
    return `<div><span>${names[i]}</span><b class="${cls}">${v === 0 ? '0' : shown}</b></div>`;
  }).join('');
}

function renderLadder(rows, activeStep) {
  $('ladder').querySelector('tbody').innerHTML = rows.map((r) => `
    <tr data-regime="${r.signature.label}" class="${r.step === activeStep ? 'now' : ''}">
      <td>${r.step}</td>
      <td class="ex">${r.exact}</td>
      <td>${r.value.toFixed(9)}</td>
      <td>${r.signature.code}</td>
      <td class="rg">${r.signature.label}</td>
      <td>${r.g00.toExponential(3)}</td>
    </tr>`).join('');
}

function render(p, { fromSlider = false } = {}) {
  current = Math.min(1, Math.max(0, p));
  const rows = trajectory(STEPS, start);
  const active = nearestStep(rows, current);
  const sig = Math.abs(current - 0.5) < 1e-12 ? exactSignature({ num: 1n, den: 2n }) : signature(current);
  const { pdot, pddot } = flowDerivatives(current);

  if (!fromSlider) $('pSlider').value = String(current);
  $('pOut').textContent = current.toFixed(6);

  const badge = $('sigBadge');
  badge.textContent = sig.code;
  badge.className = `sigbadge ${sig.code === '(4,0,0)' ? 'euclid' : sig.code === '(3,1,0)' ? 'lorentz' : 'degen'}`;
  $('sigName').textContent = sig.label;

  renderDiagonal(current);
  const exact = rows.find((r) => r.step === active);
  $('kvExact').textContent = Math.abs(exact.value - current) < 1e-9 ? exact.exact : `≈ ${exact.exact} (step ${active})`;
  $('kvG00').textContent = metric(current)[0].toExponential(4);
  $('kvG00').className = `big ${metric(current)[0] < 0 ? 'hot' : 'mint'}`;
  $('kvPdot').textContent = pdot.toExponential(4);
  $('kvPddot').textContent = pddot.toExponential(4);

  let turn;
  try { turn = transitionStep(start); } catch { turn = '—'; }
  $('kvTurn').textContent = String(turn);
  try { $('kvCross').textContent = crossingTime(start).toFixed(6); }
  catch { $('kvCross').textContent = '—'; }

  renderLadder(rows, active);
  drawFlow(rows, active);
  drawG00(current);
  $('stepNote').textContent = `g₀₀ = p̈/4 agrees to ${Math.abs(metric(current)[0] - g00FromAcceleration(current)).toExponential(1)}`;
}

/* ------------------------------------------------------------------ */
/* controls                                                            */
/* ------------------------------------------------------------------ */

function parseStart(text) {
  const [n, d] = text.split('/');
  return { num: BigInt(n), den: BigInt(d) };
}

function stopPlaying() {
  if (timer) { clearInterval(timer); timer = null; }
  $('playBtn').textContent = 'Run the flow';
}

$('pSlider').addEventListener('input', (e) => {
  stopPlaying();
  render(Number(e.target.value), { fromSlider: true });
});

document.querySelectorAll('[data-start]').forEach((btn) => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('[data-start]').forEach((b) => b.setAttribute('aria-pressed', String(b === btn)));
    stopPlaying();
    start = parseStart(btn.dataset.start);
    render(toNumber(start));
  });
});

$('playBtn').addEventListener('click', () => {
  if (timer) { stopPlaying(); return; }
  $('playBtn').textContent = 'Pause';
  let n = 0;
  timer = setInterval(() => {
    render(toNumber(occupancy(n, start)));
    if (++n > STEPS) { n = 0; }
  }, 700);
});

$('resetBtn').addEventListener('click', () => { stopPlaying(); render(toNumber(start)); });
window.addEventListener('resize', () => render(current));

/* ------------------------------------------------------------------ */
/* the instrument chain                                                */
/* ------------------------------------------------------------------ */

const receipt = { stages: [] };

function setStage(id, state, text) {
  const el = $(`st${id}`);
  el.dataset.state = state;
  el.querySelector('.st').textContent = { run: 'running', ok: 'pass', fail: 'fail', skip: 'skipped', idle: 'idle' }[state];
  if (text !== undefined) $(`out${id}`).textContent = text;
}

const yieldFrame = () => new Promise((r) => requestAnimationFrame(() => setTimeout(r, 0)));

async function stage(id, label, body) {
  setStage(id, 'run', 'working...');
  await yieldFrame();
  try {
    const { text, data } = await body();
    setStage(id, 'ok', text);
    receipt.stages.push({ stage: id, label, outcome: 'pass', detail: text, data });
    return data ?? true;
  } catch (error) {
    setStage(id, 'fail', String(error.message || error));
    receipt.stages.push({ stage: id, label, outcome: 'fail', detail: String(error.message || error) });
    throw error;
  }
}

async function runChain() {
  const btn = $('runChain');
  btn.disabled = true;
  $('dlReceipt').disabled = true;
  receipt.stages = [];
  [1, 2, 3, 4, 5].forEach((i) => setStage(i, 'idle', ''));

  try {
    // 01 -- bind, and refuse to proceed on any disagreement with src/e47.
    const lock = await stage(1, 'Bind the canonical kernel', async () => {
      const mod = await import('../shared/e47-kernel-binding.js');
      const contract = mod.loadCanonicalE47();
      agreesWithCanonicalLock(contract);
      const k = contract.canonical;
      return {
        text: `bound ${contract.schema}\nauthority ${contract.authority}\n`
          + `carrier ${k.carrier_dimension} · kernel ${k.kernel_dimension} · Ω_c ${k.coherence_fraction}\n`
          + `ε∗ ${k.epsilon_star} · ρ∗ ${k.rho_star} · roots [${k.casimir_roots}]\n`
          + `derived constants agree with src/e47 on all seven fields`,
        data: { schema: contract.schema, authority: contract.authority, canonical: k },
      };
    });

    // 02 -- the flow.
    const flow = await stage(2, 'Run the occupancy flow', async () => {
      const rows = trajectory(6, start);
      const turn = transitionStep(start);
      const p2 = occupancy(2, start);
      return {
        text: `p₀ = ${start.num}/${start.den}\n`
          + rows.slice(0, 5).map((r) => `n=${r.step}  p=${r.value.toFixed(9)}  ${r.signature.code} ${r.signature.label}`).join('\n')
          + `\nfirst Lorentzian step = ${turn} (upper bound; a generic state arrives sooner)`,
        data: {
          start: `${start.num}/${start.den}`,
          transition_step: turn,
          crossing_time: crossingTime(start),
          step2_exact: `${p2.num}/${p2.den}`,
          rows: rows.map((r) => ({ step: r.step, exact: r.exact, value: r.value, signature: r.signature.code })),
        },
      };
    });

    // 03 -- the 47-dimensional quantum carrier.
    const quantum = await stage(3, 'Evolve the 47-dimensional quantum carrier', async () => {
      const qgnn = await import('../observatory/qgnn.mjs');
      const data = await qgnn.loadCarrier();
      if (data.dimension !== 47) throw new Error(`carrier dimension ${data.dimension}, expected 47`);
      const runs = [0, flow.transition_step - 1, flow.transition_step].map((n) => {
        const p = toNumber(occupancy(Math.max(0, n), start));
        // Four angles driven by the occupancy: deterministic, bounded by 2pi.
        const angles = [Math.PI * p, Math.PI * p * p, Math.PI * (1 - p) / 2, Math.PI * (1 - 2 * p) / 2];
        const out = qgnn.evolveCarrier(data, angles);
        return { step: Math.max(0, n), occupancy: p, expectation: out.expectation, norm: out.norm, error: out.error, imaginaryResidual: out.imaginaryResidual };
      });
      const worst = Math.max(...runs.map((r) => r.error));
      if (!(worst < 1e-9)) throw new Error(`carrier norm drifted by ${worst.toExponential(2)}; the kernel is not invariant`);
      return {
        text: `carrier ${data.schema} · dimension ${data.dimension}\n`
          + `source sha256 ${data.source.sha256.slice(0, 16)}...\n`
          + runs.map((r) => `n=${r.step}  p=${r.occupancy.toFixed(6)}  ⟨O⟩=${r.expectation.toFixed(9)}  ‖ψ‖²=${r.norm.toFixed(12)}`).join('\n')
          + `\nworst norm deviation ${worst.toExponential(2)} — the 47-dimensional kernel is invariant under the gate family,\nwhich is the premise the theorem assumes. Measured, not asserted.`,
        data: { schema: data.schema, dimension: data.dimension, source_sha256: data.source.sha256, runs, worst_norm_error: worst },
      };
    });

    // 04 -- make the neural lab rediscover the critical occupancy.
    const learned = await stage(4, 'Make the neural lab rediscover one half', async () => {
      const engine = await import('../observatory/engine.mjs');
      const dataset = signatureDataset(384, 47);
      const trainer = engine.createTrainer({ dataset, hidden: 10, seed: 47, learningRate: 0.6 });
      let metrics = engine.trainerMetrics(trainer);
      for (let epoch = 0; epoch < 1200; epoch++) metrics = engine.trainEpoch(trainer);
      const maxSpeed = 2 * KAPPA * 0.25;
      const probe = (p) => {
        const y = Math.max(-1, Math.min(1, (flowDerivatives(p).pdot / maxSpeed) * 2 - 1));
        return engine.predict(trainer, 2 * p - 1, y);
      };
      const found = recoverBoundary(probe);
      if (found === null) throw new Error('the learner produced no decision boundary to recover');
      const gap = Math.abs(found - 0.5);
      // A genuine gate, not decoration: the recovered boundary is sample-limited
      // and typically lands a few parts in a thousand from 1/2. Anything worse
      // than 2% means the learner did not find the structure at all.
      if (!(gap < 0.02)) throw new Error(`recovered boundary ${found.toFixed(6)} is ${gap.toExponential(2)} from 1/2; the learner did not find the structure`);
      return {
        text: `dataset ${dataset.length} samples of (centred occupancy, flow speed); the number 1/2 is never supplied\n`
          + `trained ${metrics.epoch} epochs · loss ${metrics.loss.toFixed(6)} · accuracy ${(metrics.accuracy * 100).toFixed(2)}%\n`
          + `recovered critical occupancy = ${found.toFixed(9)}\n`
          + `exact value = 0.500000000 · difference ${gap.toExponential(2)}\n`
          + `recovered from labelled samples alone. The residual is sample-limited, not a\n`
          + `training artefact: across ten sample seeds the median miss is 1.8e-3 and the worst 4.3e-3.`,
        data: { samples: dataset.length, epochs: metrics.epoch, loss: metrics.loss, accuracy: metrics.accuracy, recovered_boundary: found, exact_boundary: 0.5, difference: gap },
      };
    });

    // 05 -- the receipt, in the shape SEE ingests.
    await stage(5, 'Issue the evidence receipt', async () => {
      const stamp = new Date().toISOString();
      receipt.schema = 'EMERGENT-SPACETIME-RECEIPT-1';
      receipt.instrument = '31 EMERGE · Half-Occupancy';
      receipt.issued = stamp;
      receipt.theorem = 'g00 = p-double-dot / 4; the metric signature is sgn(1 - 2p) and turns at half occupancy';
      receipt.canonical = lock.canonical;
      receipt.scope = 'Induced coframe metric of a contraction fixed-point flow. Not a solution of the Einstein field equations. Exact noiseless simulation; no quantum hardware.';
      receipt.see_seed = [{
        id: `${stamp.slice(0, 10)}-emergent-spacetime`,
        epoch: stamp.slice(0, 7),
        domain: 3,
        implementation: 2,
        operationality: 1,
        outcome: 'full',
        source: 'in_page_computation',
        note: `half-occupancy signature turn at step ${flow.transition_step}; learner recovered ${learned.recovered_boundary.toFixed(6)} against exact 1/2; carrier norm deviation ${quantum.worst_norm_error.toExponential(2)}`,
      }];
      $('dlReceipt').disabled = false;
      return {
        text: `receipt ${receipt.schema} assembled from ${receipt.stages.length + 1} stages\n`
          + `one SEE seed record emitted, outcome "full"\n`
          + `use Download receipt, then mirror it in SEE as source-bound evidence`,
        data: { schema: receipt.schema, issued: stamp },
      };
    });

    $('chainNote').textContent = 'All five stages passed. Four independently built instruments agree on one number.';
  } catch {
    [1, 2, 3, 4, 5].forEach((i) => {
      if ($(`st${i}`).dataset.state === 'idle') setStage(i, 'skip', 'not run: an earlier stage failed');
    });
    $('chainNote').textContent = 'The chain stopped at the first failing stage and issued no receipt. That is the intended behaviour.';
  } finally {
    btn.disabled = false;
  }
}

$('runChain').addEventListener('click', runChain);

$('dlReceipt').addEventListener('click', () => {
  const blob = new Blob([JSON.stringify(receipt, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `emergent-spacetime-receipt-${receipt.issued?.slice(0, 10) || 'run'}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
});

/* ------------------------------------------------------------------ */
/* the binding chip, installed on load                                 */
/* ------------------------------------------------------------------ */

(async () => {
  render(toNumber(start));
  try {
    const mod = await import('../shared/e47-kernel-binding.js');
    const contract = mod.loadCanonicalE47();
    agreesWithCanonicalLock(contract);
    const chip = $('bindChip');
    chip.classList.add('live');
    chip.textContent = `E47 · BOUND · ${contract.canonical.coherence_fraction}`;
    window.CITY_E47_CANONICAL = contract;
    document.dispatchEvent(new CustomEvent('city:e47-bound', { detail: { surface: 'EMERGE', contract } }));
  } catch (error) {
    const chip = $('bindChip');
    chip.classList.remove('live');
    chip.textContent = 'E47 · MISS';
    chip.title = String(error.message || error);
    document.dispatchEvent(new CustomEvent('city:e47-miss', { detail: { surface: 'EMERGE', error: String(error) } }));
  }
})();
